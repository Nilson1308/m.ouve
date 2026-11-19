import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { protocolosService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { mapListaProtocolosResponse, mapProtocoloFromApi } from '@/utils/protocoloMapper'

export const useProtocolosStore = defineStore('protocolos', () => {
  const protocolos = ref([])
  const loading = ref(false)
  const error = ref(null)

  const protocolosAtivos = computed(() =>
    protocolos.value.filter((p) => p.status !== 'resolvido' && p.status !== 'rejeitado')
  )

  const protocolosResolvidos = computed(() =>
    protocolos.value.filter((p) => p.status === 'resolvido')
  )

  const totalProtocolos = computed(() => protocolos.value.length)

  const getStatusLabel = (status) => {
    const labels = {
      em_analise: 'Em Análise',
      em_andamento: 'Equipe em Deslocamento',
      resolvido: 'Resolvido',
      rejeitado: 'Não Procedente'
    }
    return labels[status] || status
  }

  const getStatusBadgeClass = (status) => {
    const classes = {
      em_analise: 'badge-pending',
      em_andamento: 'badge-in-progress',
      resolvido: 'badge-resolved',
      rejeitado: 'badge-rejected'
    }
    return classes[status] || 'badge-pending'
  }

  function buildCreatePayload(dados) {
    const loc = dados.localizacao || {}
    const latitude = dados.latitude ?? loc.latitude
    const longitude = dados.longitude ?? loc.longitude
    const endereco = dados.endereco ?? loc.endereco ?? ''

    const payload = {
      servico_id: dados.servico_id,
      dados_dinamicos: dados.dados_dinamicos || {},
      descricao: dados.descricao
    }

    if (latitude != null && longitude != null) {
      payload.endereco = endereco
      payload.latitude = latitude
      payload.longitude = longitude
    } else if (endereco) {
      payload.endereco = endereco
    }

    if (dados.fotos?.length) {
      payload.fotos = dados.fotos
    }
    if (dados.audio) {
      payload.audio = dados.audio
    }

    return payload
  }

  async function carregarProtocolos(filters = {}) {
    loading.value = true
    error.value = null

    try {
      const response = await protocolosService.list(filters)
      protocolos.value = mapListaProtocolosResponse(response)
      return { success: true }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao carregar protocolos')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function criarSolicitacao(dados) {
    loading.value = true
    error.value = null

    try {
      const payload = buildCreatePayload(dados)
      const created = await protocolosService.create(payload)
      const protocolo = mapProtocoloFromApi(created)
      protocolos.value.unshift(protocolo)
      return { success: true, protocolo }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao criar solicitação')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function buscarProtocolo(id) {
    loading.value = true
    error.value = null

    try {
      const response = await protocolosService.get(id)
      const protocolo = mapProtocoloFromApi(response)

      const index = protocolos.value.findIndex((p) => p.id === id)
      if (index >= 0) {
        protocolos.value[index] = protocolo
      }

      return { success: true, protocolo }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Protocolo não encontrado')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  /**
   * Criar solicitação dinâmica baseada em catálogo de serviços
   * @param {Object} payload - { servico_id, dados_dinamicos, endereco_texto, localizacao, anexos }
   */
  async function criarSolicitacaoDinamica(payload) {
    loading.value = true
    error.value = null

    try {
      // Monta o payload no formato esperado pela API
      const dados = {
        servico_id: payload.servico_id,
        dados_dinamicos: payload.dados_dinamicos || {},
        descricao: '', // Descrição pode vir dos dados_dinamicos
        endereco: payload.endereco_texto || '',
        latitude: payload.localizacao?.latitude,
        longitude: payload.localizacao?.longitude,
        fotos: payload.anexos || []
      }

      // Extrai descrição principal dos dados dinâmicos se existir
      if (dados.dados_dinamicos.descricao_detalhada) {
        dados.descricao = dados.dados_dinamicos.descricao_detalhada
      } else if (dados.dados_dinamicos.informacao_solicitada) {
        dados.descricao = dados.dados_dinamicos.informacao_solicitada
      } else if (dados.dados_dinamicos.observacoes) {
        dados.descricao = dados.dados_dinamicos.observacoes
      } else if (dados.dados_dinamicos.descricao_problema) {
        dados.descricao = dados.dados_dinamicos.descricao_problema
      } else {
        // Fallback: concatena valores dos campos
        dados.descricao = Object.values(dados.dados_dinamicos)
          .filter(v => typeof v === 'string' && v.length > 0)
          .join('; ') || 'Solicitação via formulário dinâmico'
      }

      // Usa a função existente para criar
      return await criarSolicitacao(dados)
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao criar solicitação')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  return {
    protocolos,
    loading,
    error,
    protocolosAtivos,
    protocolosResolvidos,
    totalProtocolos,
    getStatusLabel,
    getStatusBadgeClass,
    carregarProtocolos,
    criarSolicitacao,
    criarSolicitacaoDinamica,
    buscarProtocolo
  }
})
