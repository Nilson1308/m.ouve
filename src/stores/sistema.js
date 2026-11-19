import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

/** Estado offline quando a API falha (5xx, rede, etc.). */
export function snapshotSaudeOffline(mensagem = null) {
  return {
    chat_operacional: false,
    redis: {
      status: 'OFFLINE',
      ok: false,
      detalhe: mensagem || 'Não foi possível consultar o servidor'
    },
    celery: {
      status: 'OFFLINE',
      ok: false,
      workers_vivos: 0,
      workers: [],
      filas_detectadas: [],
      fila_padrao: null,
      detalhe: mensagem || 'Não foi possível consultar o servidor'
    },
    verificado_em: new Date().toISOString(),
    _erro_http: true
  }
}

export const useSistemaStore = defineStore('sistema', () => {
  const saudeInfra = ref(null)
  const loadingSaude = ref(false)
  const atualizandoSaude = ref(false)
  const erroSaude = ref(null)

  async function carregarSaudeInfra(opcoes = {}) {
    const { silencioso = false } = opcoes
    if (silencioso) {
      atualizandoSaude.value = true
    } else {
      loadingSaude.value = true
    }
    erroSaude.value = null

    try {
      const { data } = await api.get('/backoffice/admin/saude-infra')
      saudeInfra.value = { ...data, _erro_http: false }
      return saudeInfra.value
    } catch (err) {
      const msg = getApiErrorMessage(err, 'Falha ao consultar saúde da infraestrutura')
      erroSaude.value = msg
      saudeInfra.value = snapshotSaudeOffline(msg)
      throw err
    } finally {
      loadingSaude.value = false
      atualizandoSaude.value = false
    }
  }

  return {
    saudeInfra,
    loadingSaude,
    atualizandoSaude,
    erroSaude,
    carregarSaudeInfra
  }
})