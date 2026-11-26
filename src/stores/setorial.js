import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { serializarQueryParams } from '@/utils/apiQuery'
import { mapOrdemSetorial, mapOrdensSetorialLista } from '@/utils/setorialMappers'
import { OPCOES_URGENCIA_FILTRO } from '@/utils/urgenciaHelpers'

export const useSetorialStore = defineStore('setorial', () => {
  const ordens = ref([])
  const loading = ref(false)
  const loadingOpcoesFiltros = ref(false)
  const opcoesFiltrosSetorial = ref({
    bairros: [],
    servicos: [],
    status: [],
    urgencias: []
  })
  const filtros = ref({
    busca: '',
    servicoIds: [],
    bairros: [],
    statusLista: [],
    urgenciaLista: [],
    apenasReabertos: false,
    apenasSugestaoUrgenciaIa: false
  })
  const gerandoLink = ref(false)
  const formalizando = ref(false)
  const erro = ref(null)
  const kpis = computed(() => {
    const todas = ordens.value
    const hoje = new Date().toDateString()
    return {
      pendentes: todas.filter(
        (o) => o.status === 'nova' || o.status === 'aguardando_campo'
      ).length,
      atrasadas: todas.filter((o) => o.sla_status === 'vencido').length,
      aguardandoCampo: todas.filter((o) => o.status === 'aguardando_campo').length,
      concluidasHoje: todas.filter(
        (o) =>
          o.status === 'concluida' &&
          o.concluida_em &&
          new Date(o.concluida_em).toDateString() === hoje
      ).length
    }
  })

  const unidade = computed(() => {
    const primeira = ordens.value[0]
    if (!primeira) {
      return { nome: 'Painel Setorial', codigo: '—', id: null }
    }
    return {
      id: null,
      nome: primeira.unidade_nome || 'Unidade Administrativa',
      codigo: primeira.unidade_sigla || 'SETORIAL'
    }
  })

  function atualizarOrdemNoState(ordemApi) {
    const mapped = mapOrdemSetorial(ordemApi)
    const idx = ordens.value.findIndex((o) => o.id === mapped.id)
    if (idx >= 0) {
      ordens.value[idx] = mapped
    } else {
      ordens.value.unshift(mapped)
    }
    return mapped
  }

  function buildQueryParams() {
    const p = {}
    if (filtros.value.busca?.trim()) {
      p.busca = filtros.value.busca.trim()
    }
    if (filtros.value.servicoIds?.length) {
      p.servico_id = [...filtros.value.servicoIds]
    }
    if (filtros.value.bairros?.length) {
      p.bairro = [...filtros.value.bairros]
    }
    if (filtros.value.statusLista?.length) {
      p.status_ui = [...filtros.value.statusLista]
    }
    if (filtros.value.urgenciaLista?.length) {
      p.urgencia = [...filtros.value.urgenciaLista]
    }
    if (filtros.value.apenasReabertos) {
      p.apenas_reabertos = 'true'
    }
    if (filtros.value.apenasSugestaoUrgenciaIa) {
      p.apenas_sugestao_urgencia_ia = 'true'
    }
    return p
  }

  const totalFiltrosAvancados = computed(() => {
    const f = filtros.value
    return (
      (f.servicoIds?.length || 0) +
      (f.bairros?.length || 0) +
      (f.statusLista?.length || 0) +
      (f.urgenciaLista?.length || 0) +
      (f.apenasReabertos ? 1 : 0) +
      (f.apenasSugestaoUrgenciaIa ? 1 : 0)
    )
  })

  function aplicarFiltrosAvancados(payload) {
    filtros.value.servicoIds = payload.servicoIds || []
    filtros.value.bairros = payload.bairros || []
    filtros.value.statusLista = payload.statusLista || []
    filtros.value.urgenciaLista = payload.urgenciaLista || []
    filtros.value.apenasReabertos = Boolean(payload.apenasReabertos)
    filtros.value.apenasSugestaoUrgenciaIa = Boolean(payload.apenasSugestaoUrgenciaIa)
  }

  function setFiltroBusca(val) {
    filtros.value.busca = val
  }

  function limparFiltros() {
    filtros.value = {
      busca: '',
      servicoIds: [],
      bairros: [],
      statusLista: [],
      urgenciaLista: [],
      apenasReabertos: false,
      apenasSugestaoUrgenciaIa: false
    }
  }

  async function carregarOpcoesFiltrosSetorial() {
    loadingOpcoesFiltros.value = true
    try {
      const { data } = await api.get('/backoffice/setorial/filtros')
      opcoesFiltrosSetorial.value = {
        bairros: data.bairros || [],
        servicos: data.servicos || [],
        status: data.status || [],
        urgencias:
          data.urgencias?.length > 0 ? data.urgencias : [...OPCOES_URGENCIA_FILTRO]
      }
      return opcoesFiltrosSetorial.value
    } catch (e) {
      opcoesFiltrosSetorial.value = {
        bairros: [],
        servicos: [],
        status: [],
        urgencias: [...OPCOES_URGENCIA_FILTRO]
      }
      throw e
    } finally {
      loadingOpcoesFiltros.value = false
    }
  }

  async function carregarOrdens() {
    loading.value = true
    erro.value = null
    try {
      const qs = serializarQueryParams(buildQueryParams())
      const url = qs
        ? `/backoffice/setorial/ordens?${qs}`
        : '/backoffice/setorial/ordens'
      const { data } = await api.get(url)
      ordens.value = mapOrdensSetorialLista(data)
      return ordens.value
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível carregar as ordens de serviço da unidade.'
      )
      ordens.value = []
      throw e
    } finally {
      loading.value = false
    }
  }

  const enviandoEvidencias = ref(false)

  async function enviarEvidencias(osId, files) {
    if (!files?.length) return null
    enviandoEvidencias.value = true
    erro.value = null
    try {
      const formData = new FormData()
      for (const file of files) {
        formData.append('anexos', file)
        formData.append('tipo_evidencia', 'depois')
      }
      const { data } = await api.post(`/backoffice/ordens/${osId}/evidencias`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (data.ordem_servico) {
        return atualizarOrdemNoState(data.ordem_servico)
      }
      return null
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível enviar as evidências.')
      throw e
    } finally {
      enviandoEvidencias.value = false
    }
  }

  async function gerarLinkMagico(osId) {
    gerandoLink.value = true
    erro.value = null
    try {
      const { data } = await api.post(`/backoffice/ordens/${osId}/gerar-link`)
      const ordem = data.ordem_servico
        ? atualizarOrdemNoState(data.ordem_servico)
        : null
      const magicLink = data.magic_link || (ordem && ordem.magic_link)
      return { magic_link: magicLink, url: data.url, ordem_servico: ordem }
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível gerar o link mágico.')
      throw e
    } finally {
      gerandoLink.value = false
    }
  }

  async function formalizarOrdem(osId, payload) {
    formalizando.value = true
    erro.value = null
    try {
      const body = {
        despacho_tecnico: payload.despacho_tecnico || payload.despacho,
        observacoes_extras:
          payload.observacoes_extras || payload.observacoes || '',
        senha_assinatura: payload.senha_assinatura || payload.senha
      }
      const { data } = await api.post(`/backoffice/ordens/${osId}/formalizar`, body)
      if (data.ordem_servico) {
        atualizarOrdemNoState(data.ordem_servico)
      }
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(
        e,
        'Não foi possível formalizar a ordem de serviço.'
      )
      throw e
    } finally {
      formalizando.value = false
    }
  }

  function ordemPorId(id) {
    return ordens.value.find((o) => o.id === id) || null
  }

  const carregandoDetalhe = ref(false)

  async function carregarOrdemDetalhe(ordemId) {
    if (!ordemId) return null
    carregandoDetalhe.value = true
    try {
      const { data } = await api.get(`/backoffice/setorial/ordens/${ordemId}`)
      return atualizarOrdemNoState(data)
    } finally {
      carregandoDetalhe.value = false
    }
  }

  return {
    ordens,
    loading,
    gerandoLink,
    formalizando,
    enviandoEvidencias,
    erro,
    kpis,
    unidade,
    filtros,
    opcoesFiltrosSetorial,
    loadingOpcoesFiltros,
    totalFiltrosAvancados,
    carregarOrdens,
    carregarOpcoesFiltrosSetorial,
    aplicarFiltrosAvancados,
    setFiltroBusca,
    limparFiltros,
    buildQueryParams,
    enviarEvidencias,
    gerarLinkMagico,
    formalizarOrdem,
    ordemPorId,
    atualizarOrdemNoState,
    carregarOrdemDetalhe,
    carregandoDetalhe
  }
})
