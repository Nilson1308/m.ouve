/** Normaliza payloads de GET /backoffice/setorial/ordens */

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
    encerramento_direto_secretaria: Boolean(api.encerramento_direto_secretaria)
  }
}

export function mapOrdensSetorialLista(data) {
  const lista = Array.isArray(data) ? data : data.data || []
  return lista.map(mapOrdemSetorial)
}
