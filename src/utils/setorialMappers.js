/** Normaliza payloads de GET /backoffice/setorial/ordens (API v4.14.2) */

import { mapDiligenciaFromApi } from '@/utils/diligenciaHelpers'
import { mapReaberturaFromApi } from '@/utils/reaberturaHelpers'

export function mapEvidenciaSetorial(api) {
  return {
    id: api.id,
    tipo: api.tipo || 'foto',
    url: api.url,
    legenda: api.legenda || api.tipo_evidencia || 'Evidência',
    enviado_em: api.enviado_em || api.criado_em,
    enviado_por: 'Equipe de Campo',
    metadata: null
  }
}

export function mapOrdemSetorial(api) {
  return {
    id: api.id,
    protocolo_id: api.protocolo_id,
    protocolo_uuid: api.protocolo_uuid,
    servico: api.servico,
    descricao: api.descricao,
    endereco: api.endereco || '',
    coordenadas: api.coordenadas,
    prioridade: api.prioridade || 'normal',
    status: api.status,
    status_api: api.status_api,
    sla_status: api.sla_status || 'normal',
    prazo_interno: api.prazo_interno,
    criado_em: api.criado_em,
    despachado_em: api.despachado_em,
    concluida_em: api.concluida_em,
    cidadao: api.cidadao || { nome: '—', cpf: '***.***.***-**' },
    instrucao_ouvidoria: api.instrucao_ouvidoria || '',
    despacho_tecnico: api.despacho_tecnico || '',
    observacoes_extras: api.observacoes_extras || '',
    observacoes_complementares: api.observacoes_extras || '',
    observacoes_execucao: api.observacoes_execucao || '',
    assinado_por: api.assinado_por || '',
    assinado_em: api.assinado_em,
    assinatura_digital_hash: api.assinatura_digital_hash || '',
    data_formalizacao: api.data_formalizacao || null,
    magic_link: api.magic_link || null,
    evidencias: (api.evidencias || []).map(mapEvidenciaSetorial),
    unidade_nome: api.unidade_nome,
    unidade_sigla: api.unidade_sigla,
    is_super_os: Boolean(api.is_super_os),
    qtd_chamados_vinculados: Number(api.qtd_chamados_vinculados ?? 1),
    super_os_codigo: api.super_os_codigo || null,
    protocolo_codigo: api.protocolo_codigo || null,
    exigir_validacao_ouvidoria: Boolean(api.exigir_validacao_ouvidoria),
    encerramento_direto_secretaria: Boolean(api.encerramento_direto_secretaria),
    aguardando_cidadao: Boolean(api.aguardando_cidadao),
    aguardandoCidadao: Boolean(api.aguardando_cidadao),
    sla_pausado: Boolean(api.sla_pausado),
    slaPausado: Boolean(api.sla_pausado),
    qtd_diligencias_respondidas: Number(api.qtd_diligencias_respondidas ?? 0),
    qtdDiligenciasRespondidas: Number(api.qtd_diligencias_respondidas ?? 0),
    ultima_diligencia_respondida_em: api.ultima_diligencia_respondida_em ?? null,
    ultimaDiligenciaRespondidaEm: api.ultima_diligencia_respondida_em ?? null,
    qtd_anexos_diligencias: Number(api.qtd_anexos_diligencias ?? 0),
    qtdAnexosDiligencias: Number(api.qtd_anexos_diligencias ?? 0),
    diligencia_ativa: api.diligencia_ativa ? mapDiligenciaFromApi(api.diligencia_ativa) : null,
    diligenciaAtiva: api.diligencia_ativa ? mapDiligenciaFromApi(api.diligencia_ativa) : null,
    diligencias: Array.isArray(api.diligencias)
      ? api.diligencias.map(mapDiligenciaFromApi).filter(Boolean)
      : [],
    pode_abrir_diligencia: Boolean(api.pode_abrir_diligencia),
    podeAbrirDiligencia: Boolean(api.pode_abrir_diligencia),
    motivo_bloqueio_diligencia: api.motivo_bloqueio_diligencia ?? null,
    motivoBloqueioDiligencia: api.motivo_bloqueio_diligencia ?? null,
    tempo_sla_pausado_segundos: Number(api.tempo_sla_pausado_segundos ?? 0),
    tempoSlaPausadoSegundos: Number(api.tempo_sla_pausado_segundos ?? 0),
    protocolo_qtd_reaberturas: Number(api.protocolo_qtd_reaberturas ?? 0),
    protocolo_reaberto: Boolean(api.protocolo_reaberto),
    protocolo_reaberturas: Array.isArray(api.protocolo_reaberturas)
      ? api.protocolo_reaberturas.map(mapReaberturaFromApi).filter(Boolean)
      : [],
    protocoloQtdReaberturas: Number(api.protocolo_qtd_reaberturas ?? 0),
    protocoloReaberto: Boolean(api.protocolo_reaberto)
  }
}

export function protocoloReaberturaFromOrdem(ordem) {
  if (!ordem) return null
  const reaberturas = Array.isArray(ordem.protocolo_reaberturas)
    ? ordem.protocolo_reaberturas
    : ordem.protocoloReaberturas || []
  return {
    id: ordem.protocolo_uuid || ordem.protocolo_id,
    qtdReaberturas: Number(ordem.protocoloQtdReaberturas ?? ordem.protocolo_qtd_reaberturas ?? 0),
    qtd_reaberturas: Number(ordem.protocoloQtdReaberturas ?? ordem.protocolo_qtd_reaberturas ?? 0),
    reaberto: Boolean(ordem.protocoloReaberto ?? ordem.protocolo_reaberto),
    reaberturas,
    status: 'resolvido'
  }
}

/** Payload UI para ProtocoloDiligenciaBackoffice a partir da OS setorial. */
export function protocoloDiligenciaFromOrdem(ordem) {
  if (!ordem) return null
  return {
    id: ordem.protocolo_uuid || ordem.protocolo_id,
    protocolo_uuid: ordem.protocolo_uuid,
    diligenciaAtiva: ordem.diligenciaAtiva ?? ordem.diligencia_ativa,
    diligencia_ativa: ordem.diligencia_ativa ?? ordem.diligenciaAtiva,
    diligencias: ordem.diligencias || [],
    podeAbrirDiligencia: Boolean(ordem.podeAbrirDiligencia ?? ordem.pode_abrir_diligencia),
    pode_abrir_diligencia: Boolean(ordem.pode_abrir_diligencia ?? ordem.podeAbrirDiligencia),
    motivoBloqueioDiligencia:
      ordem.motivoBloqueioDiligencia ?? ordem.motivo_bloqueio_diligencia ?? null,
    motivo_bloqueio_diligencia:
      ordem.motivo_bloqueio_diligencia ?? ordem.motivoBloqueioDiligencia ?? null,
    ordens_servico: [{ id: ordem.id }]
  }
}

export function mapOrdensSetorialLista(data) {
  const lista = Array.isArray(data) ? data : data.data || []
  return lista.map(mapOrdemSetorial)
}
