import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

function mapNotificacaoAuditoria(row) {
  if (!row) return null
  return {
    id: row.id,
    titulo: row.titulo,
    mensagem: row.mensagem,
    lida: Boolean(row.lida),
    data_criacao: row.data_criacao,
    usuario_destino_id: row.usuario_destino_id,
    usuario_destino_nome: row.usuario_destino_nome || '—',
    usuario_destino_email: row.usuario_destino_email || '',
    unidade_destino_id: row.unidade_destino_id,
    unidade_destino_nome: row.unidade_destino_nome || null
  }
}

export const useNotificacoesAdminStore = defineStore('notificacoesAdmin', () => {
  const configuracao = ref(null)
  const loadingConfig = ref(false)
  const salvandoGatilhos = ref(false)

  const auditoria = ref([])
  const auditoriaCount = ref(0)
  const auditoriaNext = ref(null)
  const auditoriaPrevious = ref(null)
  const loadingAuditoria = ref(false)
  const loadingBroadcast = ref(false)
  const erro = ref(null)

  async function carregarConfiguracao() {
    loadingConfig.value = true
    erro.value = null
    try {
      const { data } = await api.get('/backoffice/admin/configuracao-sistema')
      configuracao.value = data
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar configuração do sistema')
      throw err
    } finally {
      loadingConfig.value = false
    }
  }

  async function atualizarGatilhos(partial) {
    salvandoGatilhos.value = true
    erro.value = null
    try {
      const { data } = await api.patch('/backoffice/admin/configuracao-sistema', partial)
      configuracao.value = data
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao salvar gatilhos')
      throw err
    } finally {
      salvandoGatilhos.value = false
    }
  }

  async function dispararBroadcast(payload) {
    loadingBroadcast.value = true
    erro.value = null
    try {
      const body = {
        titulo: payload.titulo,
        mensagem: payload.mensagem,
        nivel_urgencia: payload.nivel_urgencia || 'normal'
      }
      if (payload.unidade_alvo_id) {
        body.unidade_alvo_id = payload.unidade_alvo_id
      }
      if (payload.link_acao?.trim()) {
        body.link_acao = payload.link_acao.trim()
      }
      const { data } = await api.post('/backoffice/admin/notificacoes/broadcast', body)
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao disparar aviso')
      throw err
    } finally {
      loadingBroadcast.value = false
    }
  }

  async function carregarAuditoria(opcoes = {}) {
    const { page = 1, page_size = 50, lida = null, busca = '' } = opcoes
    loadingAuditoria.value = true
    erro.value = null
    try {
      const params = { page, page_size }
      if (lida === true || lida === false) {
        params.lida = lida
      }
      if (busca?.trim()) {
        params.busca = busca.trim()
      }
      const { data } = await api.get('/backoffice/admin/notificacoes/auditoria', { params })
      const lista = (data.results || []).map(mapNotificacaoAuditoria)
      if (page > 1) {
        auditoria.value = [...auditoria.value, ...lista]
      } else {
        auditoria.value = lista
      }
      auditoriaCount.value = data.count ?? lista.length
      auditoriaNext.value = data.next
      auditoriaPrevious.value = data.previous
      return lista
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar auditoria')
      throw err
    } finally {
      loadingAuditoria.value = false
    }
  }

  function limparErro() {
    erro.value = null
  }

  return {
    configuracao,
    loadingConfig,
    salvandoGatilhos,
    auditoria,
    auditoriaCount,
    auditoriaNext,
    auditoriaPrevious,
    loadingAuditoria,
    loadingBroadcast,
    erro,
    carregarConfiguracao,
    atualizarGatilhos,
    dispararBroadcast,
    carregarAuditoria,
    limparErro
  }
})