import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { copilotoGestaoService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { normalizarMensagemCopiloto } from '@/services/copilotoGestaoMappers'

const POLL_MS = 1800
const POLL_TIMEOUT_MS = 45_000

export const useCopilotoStore = defineStore('copiloto', () => {
  const aberto = ref(false)
  const configUsuario = ref(null)
  const configCarregando = ref(false)
  const sessoes = ref([])
  const sessaoAtualId = ref(null)
  const sessaoTitulo = ref('')
  const mensagens = ref([])
  const enviando = ref(false)
  const iaProcessando = ref(false)
  const erro = ref(null)
  const mostrarHistorico = ref(false)
  const historicoCarregando = ref(false)

  let pollTimer = null
  let pollInicio = 0

  const conversaVazia = computed(
    () => !mensagens.value.length && !sessaoAtualId.value && !iaProcessando.value
  )

  const cotaAtingida = computed(() => {
    const cfg = configUsuario.value
    if (!cfg) return false
    return cfg.perguntasHoje >= cfg.limiteDiario
  })

  const botaoVisivel = computed(() => configUsuario.value !== null)

  const copilotoHabilitado = computed(() => Boolean(configUsuario.value?.copilotoDisponivel))

  function pararPolling() {
    if (pollTimer != null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
    pollInicio = 0
  }

  function limparEstadoConversa() {
    pararPolling()
    sessaoAtualId.value = null
    sessaoTitulo.value = ''
    mensagens.value = []
    iaProcessando.value = false
    erro.value = null
  }

  async function carregarConfig(rota = '') {
    configCarregando.value = true
    try {
      const params = rota ? { rota } : {}
      configUsuario.value = await copilotoGestaoService.obterConfigUsuario(params)
      return configUsuario.value
    } catch (e) {
      configUsuario.value = null
      return null
    } finally {
      configCarregando.value = false
    }
  }

  async function carregarHistorico() {
    historicoCarregando.value = true
    erro.value = null
    try {
      sessoes.value = await copilotoGestaoService.listarSessoes()
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível carregar o histórico.')
    } finally {
      historicoCarregando.value = false
    }
  }

  async function aplicarDetalheSessao(detalhe) {
    sessaoAtualId.value = detalhe.sessaoId
    sessaoTitulo.value = detalhe.titulo
    mensagens.value = detalhe.mensagens
    iaProcessando.value = detalhe.iaProcessando
    return detalhe
  }

  async function abrirSessao(sessaoId) {
    erro.value = null
    mostrarHistorico.value = false
    try {
      const detalhe = await copilotoGestaoService.obterSessao(sessaoId)
      await aplicarDetalheSessao(detalhe)
      if (detalhe.iaProcessando) {
        iniciarPolling(sessaoId)
      }
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Sessão não encontrada.')
    }
  }

  async function excluirSessao(sessaoId) {
    await copilotoGestaoService.excluirSessao(sessaoId)
    sessoes.value = sessoes.value.filter((s) => s.id !== sessaoId)
    if (sessaoAtualId.value === sessaoId) {
      novaConversa()
    }
  }

  function novaConversa() {
    limparEstadoConversa()
    mostrarHistorico.value = false
  }

  async function abrirDrawer() {
    aberto.value = true
    if (!configUsuario.value) {
      await carregarConfig()
    }
  }

  function fecharDrawer() {
    aberto.value = false
    pararPolling()
  }

  function alternarDrawer() {
    if (aberto.value) fecharDrawer()
    else abrirDrawer()
  }

  function iniciarPolling(sessaoId) {
    pararPolling()
    pollInicio = Date.now()
    pollTimer = setInterval(() => pollSessao(sessaoId), POLL_MS)
    pollSessao(sessaoId)
  }

  async function pollSessao(sessaoId) {
    if (Date.now() - pollInicio > POLL_TIMEOUT_MS) {
      pararPolling()
      iaProcessando.value = false
      erro.value =
        'A resposta está demorando mais que o esperado. Tente atualizar a conversa em instantes.'
      return
    }
    try {
      const detalhe = await copilotoGestaoService.obterSessao(sessaoId)
      await aplicarDetalheSessao(detalhe)
      if (!detalhe.iaProcessando) {
        pararPolling()
        enviando.value = false
        await carregarConfig()
      }
    } catch {
      /* silencioso — tenta de novo */
    }
  }

  async function enviarPergunta(pergunta, contextoRota = '') {
    const texto = (pergunta || '').trim()
    if (texto.length < 3 || texto.length > 600) return
    if (!copilotoHabilitado.value) {
      erro.value = configUsuario.value?.motivoIndisponivel || 'Copiloto indisponível.'
      return
    }
    if (cotaAtingida.value) {
      erro.value = 'Limite diário de perguntas atingido.'
      return
    }

    enviando.value = true
    iaProcessando.value = true
    erro.value = null

    const msgUsuario = normalizarMensagemCopiloto({
      id: `local-u-${Date.now()}`,
      papel: 'usuario',
      conteudo: texto,
      status_processamento: 'concluida',
      ferramentas_usadas: [],
      referencias: [],
      modo_geracao: '',
      criado_em: new Date().toISOString()
    })
    const msgAssist = normalizarMensagemCopiloto({
      id: `local-a-${Date.now()}`,
      papel: 'assistente',
      conteudo: '',
      status_processamento: 'processando',
      ferramentas_usadas: [],
      referencias: [],
      modo_geracao: '',
      criado_em: new Date().toISOString()
    })
    mensagens.value = [...mensagens.value, msgUsuario, msgAssist]

    try {
      const body = {
        pergunta: texto,
        contexto_rota: contextoRota || undefined
      }
      if (sessaoAtualId.value) {
        body.sessao_id = sessaoAtualId.value
      }
      const resp = await copilotoGestaoService.perguntar(body)
      if (resp.httpStatus !== 202) {
        throw new Error('Resposta inesperada do servidor.')
      }
      sessaoAtualId.value = resp.sessaoId
      if (configUsuario.value) {
        configUsuario.value = {
          ...configUsuario.value,
          perguntasHoje: resp.perguntasHoje,
          limiteDiario: resp.limiteDiario
        }
      }
      const idx = mensagens.value.findIndex((m) => m.id === msgAssist.id)
      if (idx >= 0) {
        mensagens.value[idx] = { ...mensagens.value[idx], id: resp.mensagemAssistenteId }
      }
      iniciarPolling(resp.sessaoId)
    } catch (e) {
      enviando.value = false
      iaProcessando.value = false
      mensagens.value = mensagens.value.filter((m) => m.id !== msgAssist.id)
      const status = e?.response?.status
      if (status === 429) {
        const detail = e?.response?.data
        const hoje = detail?.perguntas_hoje
        const limite = detail?.limite_diario
        erro.value =
          typeof detail?.detail === 'string'
            ? detail.detail
            : `Limite diário atingido (${hoje ?? '?'}/${limite ?? '?'}).`
        if (configUsuario.value && typeof hoje === 'number') {
          configUsuario.value.perguntasHoje = hoje
        }
      } else if (status === 403) {
        erro.value = getApiErrorMessage(e, 'Copiloto desativado ou sem permissão.')
      } else {
        erro.value = getApiErrorMessage(e, 'Não foi possível enviar a pergunta.')
      }
    }
  }

  function aoDesmontar() {
    pararPolling()
  }

  return {
    aberto,
    configUsuario,
    configCarregando,
    sessoes,
    sessaoAtualId,
    sessaoTitulo,
    mensagens,
    enviando,
    iaProcessando,
    erro,
    mostrarHistorico,
    historicoCarregando,
    conversaVazia,
    cotaAtingida,
    botaoVisivel,
    copilotoHabilitado,
    carregarConfig,
    carregarHistorico,
    abrirSessao,
    excluirSessao,
    novaConversa,
    abrirDrawer,
    fecharDrawer,
    alternarDrawer,
    enviarPergunta,
    pararPolling,
    aoDesmontar
  }
})