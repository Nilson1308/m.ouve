import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { ensureHttpsMediaUrl } from '@/utils/mediaUrl'

const POLL_INTERVAL_MS = 2000
const POLL_MAX_ATTEMPTS = 90

export const useChatStore = defineStore('chat', () => {
  const sessaoAtual = ref(null)
  const mensagens = ref([])
  const loading = ref(false)
  const error = ref(null)
  const isTyping = ref(false)
  const protocoloPendente = ref(null)

  let pollingIntervalId = null
  let pollingAttempts = 0
  let pollingSessaoId = null
  let pollingResolve = null
  let pollingReject = null

  function mapearMensagemApi(mensagem) {
    const fotosApi = (mensagem.fotos || []).map((f) => ({
      ...f,
      url: ensureHttpsMediaUrl(f.url)
    }))
    return {
      id: mensagem.id,
      tipo: mensagem.autor,
      conteudo: mensagem.conteudo_texto,
      localizacao: mensagem.localizacao,
      tipoAcao: mensagem.tipo_acao,
      escolhaConfig: mensagem.payload_ui || null,
      fotos: fotosApi.length ? fotosApi : undefined,
      timestamp: formatarTimestamp(mensagem.criado_em),
      criadoEm: mensagem.criado_em
    }
  }

  function sincronizarProtocoloDaResposta(data) {
    if (data?.protocolo) {
      protocoloPendente.value = data.protocolo
      return
    }
    const pid = data?.sessao?.protocolo_final_id
    if (pid && !protocoloPendente.value?.id) {
      protocoloPendente.value = { id: pid, codigo: protocoloPendente.value?.codigo || '' }
    }
  }

  function aplicarMensagensDaApi(listaApi) {
    const fotosPorId = new Map(
      mensagens.value
        .filter((m) => m.fotos?.length)
        .map((m) => [m.id, m.fotos])
    )
    const proximas = (listaApi || []).map((m) => {
      const msg = mapearMensagemApi(m)
      if (!msg.fotos?.length && fotosPorId.has(msg.id)) {
        msg.fotos = fotosPorId.get(msg.id)
      }
      return msg
    })
    mensagens.value = proximas
  }

  function encontrarUltimaMensagemIa(listaApi) {
    const lista = listaApi || []
    for (let i = lista.length - 1; i >= 0; i--) {
      if (lista[i].autor === 'ia') return lista[i]
    }
    return null
  }

  function pararPolling({ limparCallbacks = true, desligarTyping = false } = {}) {
    if (pollingIntervalId !== null) {
      clearInterval(pollingIntervalId)
      pollingIntervalId = null
    }
    pollingAttempts = 0
    pollingSessaoId = null
    if (limparCallbacks) {
      pollingResolve = null
      pollingReject = null
    }
    if (desligarTyping) {
      isTyping.value = false
    }
  }

  async function executarTickPolling() {
    if (!pollingSessaoId) return

    pollingAttempts += 1
    if (pollingAttempts > POLL_MAX_ATTEMPTS) {
      const err = new Error('Tempo esgotado aguardando resposta da IA.')
      pararPolling()
      isTyping.value = false
      pollingReject?.(err)
      return
    }

    try {
      const data = await chatService.listarMensagens(pollingSessaoId)
      sessaoAtual.value = data.sessao
      sincronizarProtocoloDaResposta(data)

      if (data.ia_processando) {
        aplicarMensagensDaApi(data.mensagens || [])
      }

      if (!data.ia_processando) {
        pararPolling(false)
        aplicarMensagensDaApi(data.mensagens || [])
        sincronizarProtocoloDaResposta(data)
        isTyping.value = false

        const respostaApi = encontrarUltimaMensagemIa(data.mensagens)
        const mensagemResposta = respostaApi ? mapearMensagemApi(respostaApi) : null

        pollingResolve?.({
          mensagemResposta,
          protocolo: data.protocolo || null,
          sessao: data.sessao
        })
        pollingResolve = null
        pollingReject = null
      }
    } catch (err) {
      pararPolling()
      isTyping.value = false
      pollingReject?.(err)
    }
  }

  /**
   * Polling via setInterval (2s) até ia_processando === false.
   * Retorna Promise com a última resposta da IA quando o turno termina.
   */
  function iniciarPolling(sessaoId) {
    pararPolling()

    pollingSessaoId = sessaoId
    pollingAttempts = 0

    return new Promise((resolve, reject) => {
      pollingResolve = resolve
      pollingReject = reject
      pollingIntervalId = setInterval(() => {
        void executarTickPolling()
      }, POLL_INTERVAL_MS)
      void executarTickPolling()
    })
  }

  async function iniciarSessao(categoria) {
    loading.value = true
    error.value = null
    mensagens.value = []
    pararPolling()

    try {
      const data = await chatService.iniciarSessao(categoria)
      sessaoAtual.value = data.sessao
      if (data.mensagem) {
        adicionarMensagemLocal(data.mensagem)
      }
      return { success: true, sessao: data.sessao, mensagem: data.mensagem }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Falha ao iniciar conversa com o assistente')
      adicionarMensagemErro(error.value)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function enviarMensagem(payload) {
    if (!sessaoAtual.value?.id) {
      error.value = 'Sessão não inicializada'
      return { success: false, error: error.value }
    }

    error.value = null

    try {
      const data = await chatService.interagir(sessaoAtual.value.id, payload)

      if (data.sessao) {
        sessaoAtual.value = data.sessao
      }

      if (data.mensagem_cidadao) {
        adicionarMensagemLocal(data.mensagem_cidadao, payload.arquivos)
      }

      isTyping.value = true
      const poll = await iniciarPolling(sessaoAtual.value.id)
      sessaoAtual.value = poll.sessao || sessaoAtual.value

      return {
        success: true,
        status: data.status || 'processando',
        taskId: data.task_id,
        mensagemCidadao: data.mensagem_cidadao,
        mensagemResposta: poll.mensagemResposta,
        protocolo: poll.protocolo || null
      }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Falha ao enviar mensagem')
      adicionarMensagemErro(error.value)
      return { success: false, error: error.value }
    } finally {
      if (!pollingIntervalId) {
        isTyping.value = false
      }
    }
  }

  function adicionarMensagemLocal(mensagem, arquivos = null) {
    const msg = {
      id: mensagem.id,
      tipo: mensagem.autor,
      conteudo: mensagem.conteudo_texto,
      localizacao: mensagem.localizacao,
      tipoAcao: mensagem.tipo_acao,
      escolhaConfig: mensagem.payload_ui || null,
      timestamp: formatarTimestamp(mensagem.criado_em),
      criadoEm: mensagem.criado_em
    }

    if (arquivos && arquivos.length > 0) {
      msg.fotos = arquivos.map((file) => ({
        url: URL.createObjectURL(file),
        nome: file.name,
        tamanho: file.size
      }))
    }

    mensagens.value.push(msg)
  }

  function adicionarMensagemErro(textoErro) {
    mensagens.value.push({
      id: `erro-${Date.now()}`,
      tipo: 'sistema',
      conteudo: textoErro,
      timestamp: formatarTimestamp(new Date().toISOString()),
      isError: true
    })
  }

  function formatarTimestamp(isoString) {
    const data = new Date(isoString)
    return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  function resetar() {
    pararPolling()
    sessaoAtual.value = null
    mensagens.value = []
    loading.value = false
    error.value = null
    isTyping.value = false
    protocoloPendente.value = null
  }

  return {
    sessaoAtual,
    mensagens,
    loading,
    error,
    isTyping,
    /** @deprecated use isTyping — mantido para compatibilidade */
    iaDigitando: isTyping,
    protocoloPendente,
    iniciarSessao,
    enviarMensagem,
    iniciarPolling,
    pararPolling,
    adicionarMensagemLocal,
    adicionarMensagemErro,
    resetar
  }
})
