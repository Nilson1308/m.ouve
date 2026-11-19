import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  mapDashboardEficiencia,
  mapDashboardQualidade,
  mapMapaCalorApi,
  mapDashboardInelegibilidade
} from '@/utils/dashboardMappers'

function filtrosMapaPadrao() {
  return {
    dataInicial: null,
    dataFinal: null,
    status: [],
    servico: null,
    bairro: null,
    categoriaId: null,
    unidadeResponsavelId: null
  }
}

function buildMapaCalorParams(filtros) {
  const params = {}
  if (filtros.dataInicial) params.data_inicio = filtros.dataInicial
  if (filtros.dataFinal) params.data_fim = filtros.dataFinal
  if (filtros.status?.length) params.status = filtros.status.join(',')
  if (filtros.servico) params.servico_id = filtros.servico
  if (filtros.categoriaId) params.categoria_id = filtros.categoriaId
  if (filtros.unidadeResponsavelId) {
    params.unidade_responsavel_id = filtros.unidadeResponsavelId
  }
  if (filtros.bairro) params.bairro = filtros.bairro
  params.incluir_demandas = 1
  return params
}

export const useDashboardStore = defineStore('dashboard', () => {
  const eficiencia = ref(null)
  const loadingEficiencia = ref(false)

  const qualidade = ref(null)
  const loadingQualidade = ref(false)

  const mapaCalor = ref(null)
  const loadingMapaCalor = ref(false)

  const inelegibilidade = ref(null)
  const loadingInelegibilidade = ref(false)

  const filtrosMapaCalor = ref(filtrosMapaPadrao())
  const bairrosDisponiveis = ref([])
  const loadingBairros = ref(false)
  const erro = ref(null)

  const totalOcorrencias = computed(() => {
    if (mapaCalor.value?.total != null) return mapaCalor.value.total
    return mapaCalor.value?.coordenadas?.length || 0
  })

  const periodoFormatado = computed(() => {
    const f = filtrosMapaCalor.value
    if (!f.dataInicial && !f.dataFinal) return 'Todos os períodos'

    const formatarData = (data) => {
      if (!data) return null
      const partes = String(data).split('-')
      if (partes.length === 3) {
        return `${partes[2]}/${partes[1]}/${partes[0]}`
      }
      return new Date(data).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    }

    const inicio = formatarData(f.dataInicial)
    const fim = formatarData(f.dataFinal)

    if (inicio && fim) return `${inicio} a ${fim}`
    if (inicio) return `A partir de ${inicio}`
    if (fim) return `Até ${fim}`
    return 'Todos os períodos'
  })

  async function carregarEficiencia(opcoes = {}) {
    const { silencioso = false } = opcoes

    if (!silencioso) loadingEficiencia.value = true
    erro.value = null

    try {
      const { data } = await api.get('/backoffice/dashboard/eficiencia')
      eficiencia.value = mapDashboardEficiencia(data)
      return eficiencia.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar dados de eficiência')
      console.error('Erro ao carregar eficiência:', err)
      throw err
    } finally {
      if (!silencioso) loadingEficiencia.value = false
    }
  }

  async function carregarQualidade(opcoes = {}) {
    const { silencioso = false, semLoading = silencioso, params = {} } = opcoes

    if (!semLoading) loadingQualidade.value = true

    try {
      const { data } = await api.get('/backoffice/dashboard/qualidade', { params })
      qualidade.value = mapDashboardQualidade(data)
      return qualidade.value
    } catch (err) {
      qualidade.value = mapDashboardQualidade(null)
      if (!silencioso) {
        erro.value = getApiErrorMessage(err, 'Erro ao carregar dados de qualidade')
      }
      console.error('Erro ao carregar qualidade:', err)
      throw err
    } finally {
      if (!semLoading) loadingQualidade.value = false
    }
  }

  async function carregarMapaCalor(filtros = null) {
    loadingMapaCalor.value = true
    erro.value = null

    try {
      const f = filtros || filtrosMapaCalor.value
      const params = buildMapaCalorParams(f)

      const { data } = await api.get('/backoffice/dashboard/mapa-calor', { params })
      mapaCalor.value = mapMapaCalorApi(data)
      return mapaCalor.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar mapa de calor')
      mapaCalor.value = { coordenadas: [], demandas: [], total: 0, retornados: 0 }
      console.error('Erro ao carregar mapa de calor:', err)
      throw err
    } finally {
      loadingMapaCalor.value = false
    }
  }

  async function aplicarFiltrosMapaCalor(novosFiltros) {
    filtrosMapaCalor.value = {
      ...filtrosMapaCalor.value,
      ...novosFiltros
    }
    await carregarMapaCalor()
  }

  async function limparFiltrosMapaCalor() {
    filtrosMapaCalor.value = filtrosMapaPadrao()
    await carregarMapaCalor()
  }

  async function carregarBairrosDashboard() {
    if (loadingBairros.value) return bairrosDisponiveis.value
    loadingBairros.value = true
    try {
      const { data } = await api.get('/backoffice/dashboard/bairros')
      bairrosDisponiveis.value = Array.isArray(data?.bairros) ? data.bairros : []
      return bairrosDisponiveis.value
    } catch (err) {
      console.error('Erro ao carregar bairros do dashboard:', err)
      bairrosDisponiveis.value = []
      return []
    } finally {
      loadingBairros.value = false
    }
  }

  async function carregarInelegibilidade(filtros = {}) {
    loadingInelegibilidade.value = true
    erro.value = null

    try {
      const params = {}
      if (filtros.dataInicial) params.data_inicio = filtros.dataInicial
      if (filtros.dataFinal) params.data_fim = filtros.dataFinal
      if (filtros.unidadeId) params.unidade_id = filtros.unidadeId
      if (filtros.servicoId) params.servico_id = filtros.servicoId

      const { data } = await api.get('/backoffice/dashboard/inelegibilidade', { params })
      inelegibilidade.value = mapDashboardInelegibilidade(data)
      return inelegibilidade.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar métricas de inelegibilidade')
      inelegibilidade.value = mapDashboardInelegibilidade(null)
      console.error('Erro ao carregar inelegibilidade:', err)
      throw err
    } finally {
      loadingInelegibilidade.value = false
    }
  }

  function $reset() {
    eficiencia.value = null
    qualidade.value = null
    mapaCalor.value = null
    inelegibilidade.value = null
    loadingEficiencia.value = false
    loadingQualidade.value = false
    loadingMapaCalor.value = false
    loadingInelegibilidade.value = false
    filtrosMapaCalor.value = filtrosMapaPadrao()
    bairrosDisponiveis.value = []
    loadingBairros.value = false
    erro.value = null
  }

  return {
    eficiencia,
    loadingEficiencia,
    qualidade,
    loadingQualidade,
    mapaCalor,
    loadingMapaCalor,
    inelegibilidade,
    loadingInelegibilidade,
    filtrosMapaCalor,
    bairrosDisponiveis,
    loadingBairros,
    erro,
    totalOcorrencias,
    periodoFormatado,
    carregarEficiencia,
    carregarQualidade,
    carregarMapaCalor,
    carregarInelegibilidade,
    carregarBairrosDashboard,
    aplicarFiltrosMapaCalor,
    limparFiltrosMapaCalor,
    $reset
  }
})