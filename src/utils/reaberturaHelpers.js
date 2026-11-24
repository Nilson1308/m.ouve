/** Sprint 4 — reabertura / contestação (v4.15). */

import { mapAnexoDiligencia } from '@/utils/diligenciaHelpers'

const MOTIVO_BLOQUEIO = {
  desabilitado: 'A contestação não está disponível para este serviço.',
  nao_concluido: 'A solicitação ainda não foi concluída.',
  janela_expirada: 'O prazo para contestar já encerrou.',
  limite_atingido: 'O limite de reaberturas deste protocolo foi atingido.',
  encerrado_definitivamente: 'A janela de contestação foi encerrada definitivamente.'
}

export function textoMotivoBloqueioReabertura(codigo) {
  if (!codigo) return ''
  return MOTIVO_BLOQUEIO[codigo] || ''
}

export function mapReaberturaFromApi(api) {
  if (!api || typeof api !== 'object') return null
  const anexos = (Array.isArray(api.anexos) ? api.anexos : [])
    .map(mapAnexoDiligencia)
    .filter(Boolean)
  return {
    id: String(api.id),
    motivo: api.motivo || '',
    anexos_ids: Array.isArray(api.anexos_ids) ? api.anexos_ids.map(String) : [],
    anexos,
    nota_csat_origem:
      api.nota_csat_origem != null && api.nota_csat_origem !== ''
        ? Number(api.nota_csat_origem)
        : null,
    notaCsatOrigem:
      api.nota_csat_origem != null && api.nota_csat_origem !== ''
        ? Number(api.nota_csat_origem)
        : null,
    prazo_sla_anterior: api.prazo_sla_anterior ?? null,
    novo_prazo_sla: api.novo_prazo_sla ?? null,
    ordem_servico_id: api.ordem_servico_id ?? null,
    criado_em: api.criado_em ?? null,
    criadoEm: api.criado_em ?? null
  }
}

export function mapCamposReaberturaProtocolo(protocolo) {
  if (!protocolo) return {}
  const reaberturas = Array.isArray(protocolo.reaberturas)
    ? protocolo.reaberturas.map(mapReaberturaFromApi).filter(Boolean)
    : []
  return {
    pode_reabrir: Boolean(protocolo.pode_reabrir),
    podeReabrir: Boolean(protocolo.pode_reabrir ?? protocolo.podeReabrir),
    motivo_bloqueio_reabertura: protocolo.motivo_bloqueio_reabertura ?? null,
    motivoBloqueioReabertura: protocolo.motivo_bloqueio_reabertura ?? protocolo.motivoBloqueioReabertura ?? null,
    reabertura_ate: protocolo.reabertura_ate ?? null,
    reaberturaAte: protocolo.reabertura_ate ?? protocolo.reaberturaAte ?? null,
    qtd_reaberturas: Number(protocolo.qtd_reaberturas ?? 0),
    qtdReaberturas: Number(protocolo.qtd_reaberturas ?? protocolo.qtdReaberturas ?? 0),
    max_reaberturas_permitidas: Number(protocolo.max_reaberturas_permitidas ?? 1),
    maxReaberturasPermitidas: Number(
      protocolo.max_reaberturas_permitidas ?? protocolo.maxReaberturasPermitidas ?? 1
    ),
    sugerir_reabertura_csat: Boolean(protocolo.sugerir_reabertura_csat),
    sugerirReaberturaCsat: Boolean(
      protocolo.sugerir_reabertura_csat ?? protocolo.sugerirReaberturaCsat
    ),
    reaberto: Boolean(protocolo.reaberto ?? Number(protocolo.qtd_reaberturas ?? 0) > 0),
    ultima_reabertura_em: protocolo.ultima_reabertura_em ?? null,
    ultimaReaberturaEm: protocolo.ultima_reabertura_em ?? protocolo.ultimaReaberturaEm ?? null,
    reaberturas
  }
}

export function formatarTaxaRetrabalho(valor) {
  const n = Number(valor)
  if (!Number.isFinite(n)) return '—'
  return `${n.toFixed(1).replace('.', ',')}%`
}