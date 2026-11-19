import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

export function mapNotificacaoInterna(api) {
  return {
    id: api.id,
    titulo: api.titulo,
    mensagem: api.mensagem,
    lida: Boolean(api.lida),
    linkAcao: api.link_acao || '',
    dataCriacao: api.data_criacao
  }
}

export const useNotificacoesInternasStore = defineStore('notificacoesInternas', () => {
  const items = ref([])
  const naoLidas = ref(0)
  const loading = ref(false)
  const erro = ref(null)
  const ultimaAtualizacao = ref(null)

  const temNaoLidas = computed(() => naoLidas.value > 0)

  async function carregar(opts = {}) {
    const silencioso = Boolean(opts.silencioso)
    if (!silencioso) {
      loading.value = true
    }
    erro.value = null
    try {
      const params = { limit: opts.limit ?? 50 }
      if (opts.apenasNaoLidas) {
        params.nao_lidas = 'true'
      }
      const { data } = await api.get('/backoffice/notificacoes', { params })
      items.value = (data.results || []).map(mapNotificacaoInterna)
      naoLidas.value = Number(data.nao_lidas ?? items.value.filter((n) => !n.lida).length)
      ultimaAtualizacao.value = new Date().toISOString()
      return items.value
    } catch (e) {
      if (!silencioso) {
        erro.value = getApiErrorMessage(e, 'Não foi possível carregar notificações.')
      }
      throw e
    } finally {
      if (!silencioso) {
        loading.value = false
      }
    }
  }

  async function marcarLida(id) {
    const { data } = await api.post(`/backoffice/notificacoes/${id}/marcar-lida`)
    const idx = items.value.findIndex((n) => n.id === id)
    if (idx >= 0) {
      items.value[idx] = { ...items.value[idx], lida: true }
    }
    if (data?.notificacao) {
      const mapped = mapNotificacaoInterna(data.notificacao)
      if (idx >= 0) items.value[idx] = mapped
    }
    naoLidas.value = Math.max(0, items.value.filter((n) => !n.lida).length)
  }

  async function marcarTodasLidasVisiveis() {
    const pendentes = items.value.filter((n) => !n.lida)
    await Promise.all(pendentes.map((n) => marcarLida(n.id).catch(() => null)))
    await carregar({ silencioso: true })
  }

  return {
    items,
    naoLidas,
    loading,
    erro,
    temNaoLidas,
    ultimaAtualizacao,
    carregar,
    marcarLida,
    marcarTodasLidasVisiveis
  }
})
