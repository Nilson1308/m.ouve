import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

function mapOrdemServicoAssinatura(os) {
  if (!os || typeof os !== 'object') return null
  return {
    id: os.id,
    protocoloId: os.protocolo_id || '',
    servico: os.servico || '',
    endereco: os.endereco || '',
    unidadeNome: os.unidade_nome || '',
    unidadeSigla: os.unidade_sigla || '',
    instrucaoOuvidoria: os.instrucao_ouvidoria || os.descricao || '',
    despachoTecnicoOs: (os.despacho_tecnico || '').trim(),
    observacoesExecucao: os.observacoes_execucao || '',
    observacoesExtras: (os.observacoes_extras || '').trim(),
    evidencias: Array.isArray(os.evidencias) ? os.evidencias : [],
    cidadao: os.cidadao || { nome: '—' },
    prioridade: os.prioridade || 'media',
    statusApi: os.status_api || os.status || '',
    prazoInterno: os.prazo_interno || null
  }
}

function mapSolicitacao(raw) {
  const os = raw.ordem_servico || {}
  const osMap = mapOrdemServicoAssinatura(os)
  return {
    id: raw.id,
    ordemServicoId: raw.ordem_servico_id || os.id,
    solicitanteId: raw.solicitante_id,
    assinanteDestinoId: raw.assinante_destino_id,
    despachoTecnico: raw.despacho_tecnico || '',
    status: raw.status,
    hashAssinatura: raw.hash_assinatura || '',
    assinadaEm: raw.assinada_em,
    criadoEm: raw.criado_em,
    protocoloCodigo: osMap?.protocoloId || raw.protocolo_codigo || '',
    solicitanteNome: raw.solicitante_nome || '',
    assinanteDestinoNome: raw.assinante_destino_nome || '',
    unidadeNome: osMap?.unidadeNome || raw.unidade_nome || '',
    unidadeSigla: osMap?.unidadeSigla || '',
    motivoRejeicao: raw.motivo_rejeicao || '',
    ordemServico: osMap
  }
}

export const useAssinaturasStore = defineStore('assinaturas', () => {
  const pendentes = ref([])
  const assinantes = ref([])
  const loadingPendentes = ref(false)
  const loadingAssinantes = ref(false)
  const processando = ref(false)
  const erro = ref(null)

  const totalPendentes = computed(() => pendentes.value.length)

  async function carregarPendentes() {
    loadingPendentes.value = true
    erro.value = null
    try {
      const { data } = await api.get('/backoffice/assinaturas/pendentes')
      pendentes.value = (data.results || []).map(mapSolicitacao)
      return pendentes.value
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível carregar assinaturas pendentes.')
      pendentes.value = []
      throw e
    } finally {
      loadingPendentes.value = false
    }
  }

  async function carregarAssinantes() {
    loadingAssinantes.value = true
    try {
      const { data } = await api.get('/backoffice/assinaturas/assinantes')
      assinantes.value = (data.results || []).map((u) => ({
        id: u.id,
        nome: u.nome || u.email || 'Servidor',
        email: u.email || ''
      }))
      return assinantes.value
    } catch (e) {
      assinantes.value = []
      throw e
    } finally {
      loadingAssinantes.value = false
    }
  }

  async function solicitar({ ordemServicoId, assinanteDestinoId, despachoTecnico }) {
    processando.value = true
    erro.value = null
    try {
      const body = {
        ordem_servico_id: ordemServicoId,
        despacho_tecnico: despachoTecnico
      }
      if (assinanteDestinoId) {
        body.assinante_destino_id = assinanteDestinoId
      }
      const { data } = await api.post('/backoffice/assinaturas/solicitar', body)
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível solicitar assinatura.')
      throw e
    } finally {
      processando.value = false
    }
  }

  async function assinar(solicitacaoId, senhaAssinatura) {
    processando.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        `/backoffice/assinaturas/${solicitacaoId}/assinar`,
        { senha_assinatura: senhaAssinatura }
      )
      pendentes.value = pendentes.value.filter((p) => p.id !== solicitacaoId)
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível assinar o despacho.')
      throw e
    } finally {
      processando.value = false
    }
  }

  function limpar() {
    pendentes.value = []
    assinantes.value = []
    erro.value = null
    loadingPendentes.value = false
    processando.value = false
  }

  async function rejeitar(solicitacaoId, motivo) {
    processando.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        `/backoffice/assinaturas/${solicitacaoId}/rejeitar`,
        { motivo_rejeicao: motivo }
      )
      pendentes.value = pendentes.value.filter((p) => p.id !== solicitacaoId)
      return data
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível rejeitar a solicitação.')
      throw e
    } finally {
      processando.value = false
    }
  }

  return {
    pendentes,
    assinantes,
    loadingPendentes,
    loadingAssinantes,
    processando,
    erro,
    totalPendentes,
    carregarPendentes,
    carregarAssinantes,
    solicitar,
    assinar,
    rejeitar,
    limpar
  }
})