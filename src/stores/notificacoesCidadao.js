import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { notificacoesCidadaoAppService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

export function mapNotificacaoCidadao(row) {
  if (!row) return null
  return {
    id: row.id,
    titulo: row.titulo || '',
    mensagem: row.mensagem || '',
    lida: Boolean(row.lida),
    dataCriacao: row.criada_em ?? row.dataCriacao ?? null,
    protocoloId: row.protocolo_id ?? row.protocoloId ?? null,
    protocoloCodigo: row.protocolo_codigo ?? row.protocoloCodigo ?? null
  }
}

export const useNotificacoesCidadaoStore = defineStore('notificacoesCidadao', () => {
  const items = ref([])
  const naoLidas = ref(0)
  const count = ref(0)
  const loading = ref(false)
  const error = ref(null)

  const temNaoLidas = computed(() => naoLidas.value > 0)

  async function carregar({ silencioso = false, limit = 30 } = {}) {
    if (!silencioso) loading.value = true
    error.value = null
    try {
      const data = await notificacoesCidadaoAppService.listar({ limit })
      items.value = (data.results || []).map(mapNotificacaoCidadao).filter(Boolean)
      count.value = Number(data.count) || items.value.length
      naoLidas.value = Number(data.nao_lidas) || 0
      return { success: true }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao carregar notificações')
      if (!silencioso) {
        console.error('[notificacoesCidadao]', err)
      }
      return { success: false, error: error.value }
    } finally {
      if (!silencioso) loading.value = false
    }
  }

  async function marcarLida(id) {
    const data = await notificacoesCidadaoAppService.marcarLida(id)
    const idx = items.value.findIndex((n) => n.id === id)
    if (idx >= 0) {
      const mapped = mapNotificacaoCidadao(data?.notificacao) || {
        ...items.value[idx],
        lida: true
      }
      items.value[idx] = mapped
    }
    if (naoLidas.value > 0) {
      naoLidas.value -= 1
    }
    return data
  }

  function reset() {
    items.value = []
    naoLidas.value = 0
    count.value = 0
    error.value = null
  }

  return {
    items,
    naoLidas,
    count,
    loading,
    error,
    temNaoLidas,
    carregar,
    marcarLida,
    reset
  }
})