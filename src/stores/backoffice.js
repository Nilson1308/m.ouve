import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  mapOrdemServicoDetalhe,
  mapProtocoloBackoffice,
  mapProtocoloDetalheBackoffice,
  mapUnidadeBackoffice
} from '@/utils/backofficeMappers'
import { mapKanbanItem } from '@/utils/superOsMappers'
import { protocoloAguardandoValidacao } from '@/utils/scatterGather'

export const useBackofficeStore = defineStore('backoffice', () => {
  const protocolos = ref([])
  const unidades = ref([])
  const loading = ref(false)
  const loadingUnidades = ref(false)
  const despachando = ref(false)
  const protocoloAtual = ref(null)
  const loadingDetalhes = ref(false)
  const salvandoValidacao = ref(false)
  const salvandoDevolucao = ref(false)
  const erro = ref(null)

  const pagination = ref({
    current_page: 1,
    per_page: 60,
    total_items: 0,
    total_pages: 0
  })

  const opcoesFiltrosMesa = ref({
    bairros: [],
    servicos: [],
    status: [],
    urgencias: []
  })
  const loadingOpcoesFiltros = ref(false)

  const filtros = ref({
    busca: '',
    slaVencido: false,
    urgentes: false,
    unidadesIds: [],
    servicoIds: [],
    bairros: [],
    statusLista: [],
    urgenciaLista: [],
    equipamentoId: '',
    equipamentoRotulo: '',
    apenasCobrados: false,
    apenasReabertos: false,
    page: 1
  })

  function urgenciasParaApi() {
    const lista = [...(filtros.value.urgenciaLista || [])]
    if (filtros.value.urgentes) {
      for (const u of ['alta', 'critica']) {
        if (!lista.includes(u)) lista.push(u)
      }
    }
    return lista
  }

  function buildQueryParams() {
    const p = {
      page: filtros.value.page,
      per_page: pagination.value.per_page
    }
    if (filtros.value.busca?.trim()) {
      p.busca = filtros.value.busca.trim()
    }
    const urgencias = urgenciasParaApi()
    if (urgencias.length) {
      p.urgencia = urgencias
    }
    if (filtros.value.statusLista?.length) {
      p.status = [...filtros.value.statusLista]
    }
    if (filtros.value.unidadesIds?.length) {
      p.unidade_id = [...filtros.value.unidadesIds]
    }
    if (filtros.value.servicoIds?.length) {
      p.servico_id = [...filtros.value.servicoIds]
    }
    if (filtros.value.bairros?.length) {
      p.bairro = [...filtros.value.bairros]
    }
    if (filtros.value.slaVencido) {
      p.sla_vencido = 'true'
    }
    if (filtros.value.equipamentoId?.trim()) {
      p.equipamento_id = filtros.value.equipamentoId.trim()
    }
    if (filtros.value.apenasCobrados) {
      p.apenas_cobrados = 'true'
    }
    if (filtros.value.apenasReabertos) {
      p.apenas_reabertos = 'true'
    }
    return p
  }

  function serializarParamsMesa(flat) {
    const search = new URLSearchParams()
    for (const [key, val] of Object.entries(flat)) {
      if (val === undefined || val === null || val === '') continue
      if (Array.isArray(val)) {
        for (const item of val) {
          if (item !== undefined && item !== null && item !== '') {
            search.append(key, String(item))
          }
        }
      } else {
        search.append(key, String(val))
      }
    }
    return search.toString()
  }

  const protocolosExibidos = computed(() => protocolos.value)

  const totalFiltrosAvancados = computed(() => {
    const f = filtros.value
    return (
      (f.unidadesIds?.length || 0) +
      (f.servicoIds?.length || 0) +
      (f.bairros?.length || 0) +
      (f.statusLista?.length || 0) +
      (f.urgenciaLista?.length || 0) +
      (f.equipamentoId ? 1 : 0) +
      (f.apenasCobrados ? 1 : 0) +
      (f.apenasReabertos ? 1 : 0)
    )
  })

  const contadores = computed(() => {
    const base = protocolos.value
    const hoje = new Date().toDateString()
    return {
      total: pagination.value.total_items || base.length,
      emAndamento: base.filter((p) => p.status === 'em_andamento').length,
      aguardandoValidacao: base.filter((p) => protocoloAguardandoValidacao(p)).length,
      slaVencido: base.filter((p) => p.sla?.vencido).length,
      urgentes: base.filter((p) => ['alta', 'critica'].includes(p.urgencia)).length,
      concluidosHoje: base.filter((p) => {
        if (p.status !== 'resolvido') return false
        if (!p.criadoEm) return false
        return new Date(p.criadoEm).toDateString() === hoje
      }).length
    }
  })

  async function carregarProtocolos() {
    loading.value = true
    erro.value = null
    try {
      const qs = serializarParamsMesa(buildQueryParams())
      let data
      let fonteKanban = true
      try {
        ;({ data } = await api.get(`/backoffice/kanban?${qs}`))
      } catch (e) {
        if (e?.response?.status !== 404) throw e
        fonteKanban = false
        ;({ data } = await api.get(`/backoffice/protocolos?${qs}`))
      }
      const lista = data.data || []
      protocolos.value = fonteKanban
        ? lista.map(mapKanbanItem)
        : lista.map(mapProtocoloBackoffice)
      if (data.pagination) {
        pagination.value = { ...pagination.value, ...data.pagination }
      } else if (data.count != null) {
        pagination.value = {
          ...pagination.value,
          total_items: data.count,
          total_pages: Math.max(1, Math.ceil(data.count / pagination.value.per_page))
        }
      }
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível carregar o Kanban unificado da mesa.'
      )
      protocolos.value = []
      throw e
    } finally {
      loading.value = false
    }
  }

  async function carregarUnidades() {
    if (unidades.value.length > 0) return unidades.value
    loadingUnidades.value = true
    try {
      const { data } = await api.get('/backoffice/mesa/unidades')
      const lista = Array.isArray(data) ? data : data.data || []
      unidades.value = lista.map(mapUnidadeBackoffice)
      return unidades.value
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível carregar as unidades.')
      throw e
    } finally {
      loadingUnidades.value = false
    }
  }

  /**
   * @param {string} protocoloId UUID
   * @param {{ ordens: Array<{unidade_id, instrucao, prazo_horas}>, observacao_geral?: string }} payload
   */
  async function despacharProtocolo(protocoloId, payload) {
    despachando.value = true
    erro.value = null
    try {
      const body = {
        ordens: payload.ordens.map((o) => ({
          unidade_id: o.unidade_id,
          instrucao: o.instrucao.trim(),
          prazo_horas: Number(o.prazo_horas)
        })),
        observacao_geral: payload.observacao_geral?.trim() || ''
      }
      const { data } = await api.post(
        `/backoffice/protocolos/${protocoloId}/despachar`,
        body
      )
      if (data.protocolo) {
        const mapped = mapProtocoloBackoffice(data.protocolo)
        const idx = protocolos.value.findIndex((p) => p.id === protocoloId)
        if (idx >= 0) {
          protocolos.value[idx] = mapped
        }
      } else {
        await carregarProtocolos()
      }
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível despachar o protocolo. Verifique os dados e tente novamente.'
      )
      throw e
    } finally {
      despachando.value = false
    }
  }

  function setFiltro(key, value) {
    filtros.value[key] = value
    if (key !== 'page') {
      filtros.value.page = 1
    }
  }

  function toggleFiltroBoolean(key) {
    filtros.value[key] = !filtros.value[key]
    filtros.value.page = 1
  }

  function limparFiltros() {
    filtros.value = {
      busca: '',
      slaVencido: false,
      urgentes: false,
      unidadesIds: [],
      servicoIds: [],
      bairros: [],
      statusLista: [],
      urgenciaLista: [],
      equipamentoId: '',
      equipamentoRotulo: '',
      apenasCobrados: false,
      apenasReabertos: false,
      page: 1
    }
  }

  function aplicarFiltrosAvancados(payload) {
    filtros.value.unidadesIds = payload.unidadesIds || []
    filtros.value.servicoIds = payload.servicoIds || []
    filtros.value.bairros = payload.bairros || []
    filtros.value.statusLista = payload.statusLista || []
    filtros.value.urgenciaLista = payload.urgenciaLista || []
    filtros.value.equipamentoId = payload.equipamentoId || ''
    filtros.value.equipamentoRotulo = payload.equipamentoRotulo || ''
    filtros.value.apenasCobrados = Boolean(payload.apenasCobrados)
    filtros.value.apenasReabertos = Boolean(payload.apenasReabertos)
    filtros.value.page = 1
  }

  async function carregarOpcoesFiltrosMesa() {
    loadingOpcoesFiltros.value = true
    try {
      const { data } = await api.get('/backoffice/mesa/filtros')
      opcoesFiltrosMesa.value = {
        bairros: data.bairros || [],
        servicos: data.servicos || [],
        status: data.status || [],
        urgencias: data.urgencias || []
      }
      return opcoesFiltrosMesa.value
    } catch (e) {
      opcoesFiltrosMesa.value = {
        bairros: [],
        servicos: [],
        status: [],
        urgencias: []
      }
      throw e
    } finally {
      loadingOpcoesFiltros.value = false
    }
  }

  function limparProtocoloAtual() {
    protocoloAtual.value = null
  }

  async function carregarDetalhesProtocolo(id) {
    loadingDetalhes.value = true
    erro.value = null
    try {
      const { data } = await api.get(`/backoffice/protocolos/${id}`)
      protocoloAtual.value = mapProtocoloDetalheBackoffice(data)
      return protocoloAtual.value
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível carregar os detalhes do protocolo.'
      )
      protocoloAtual.value = null
      throw e
    } finally {
      loadingDetalhes.value = false
    }
  }

  /**
   * @param {string} protocoloId UUID
   * @param {{ resposta_cidadao: string, observacoes_internas?: string }} payload
   */
  async function validarProtocolo(protocoloId, payload) {
    salvandoValidacao.value = true
    erro.value = null
    try {
      const body = {
        resposta_cidadao: payload.resposta_cidadao?.trim(),
        observacoes_internas: payload.observacoes_internas?.trim() || ''
      }
      const { data } = await api.post(
        `/backoffice/protocolos/${protocoloId}/validar`,
        body
      )
      if (data.protocolo) {
        protocoloAtual.value = mapProtocoloDetalheBackoffice(data.protocolo)
      }
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível validar o protocolo. Verifique os dados e tente novamente.'
      )
      throw e
    } finally {
      salvandoValidacao.value = false
    }
  }

  /**
   * @param {string} ordemId UUID
   * @param {{ motivo: string, justificativa: string }} payload
   */
  async function devolverOrdemServico(ordemId, payload) {
    salvandoDevolucao.value = true
    erro.value = null
    try {
      const body = {
        motivo: payload.motivo?.trim(),
        justificativa: payload.justificativa?.trim()
      }
      const { data } = await api.post(`/backoffice/ordens/${ordemId}/devolver`, body)
      if (protocoloAtual.value?.id && data.ordem_servico) {
        const idx = protocoloAtual.value.ordens_servico.findIndex(
          (o) => o.id === ordemId
        )
        const mapped = mapOrdemServicoDetalhe(
          data.ordem_servico,
          protocoloAtual.value.urgencia
        )
        if (idx >= 0) {
          protocoloAtual.value.ordens_servico[idx] = mapped
        }
        if (data.protocolo_status) {
          protocoloAtual.value.status = data.protocolo_status
        }
      }
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível devolver a ordem de serviço.'
      )
      throw e
    } finally {
      salvandoDevolucao.value = false
    }
  }

  return {
    protocolos,
    protocolosExibidos,
    unidades,
    loading,
    loadingUnidades,
    despachando,
    protocoloAtual,
    loadingDetalhes,
    salvandoValidacao,
    salvandoDevolucao,
    erro,
    filtros,
    pagination,
    contadores,
    carregarProtocolos,
    carregarUnidades,
    despacharProtocolo,
    carregarDetalhesProtocolo,
    validarProtocolo,
    devolverOrdemServico,
    limparProtocoloAtual,
    setFiltro,
    toggleFiltroBoolean,
    limparFiltros,
    aplicarFiltrosAvancados,
    opcoesFiltrosMesa,
    loadingOpcoesFiltros,
    carregarOpcoesFiltrosMesa,
    totalFiltrosAvancados
  }
})
