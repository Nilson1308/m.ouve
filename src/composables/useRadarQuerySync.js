/**
 * Aplica query params vindos do Radar (router.push) nos filtros da Mesa ou Setorial.
 */

function splitList(val) {
  if (!val) return []
  return String(val)
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean)
}

export function queryRadarTemFiltros(query = {}) {
  return Object.keys(query).some((k) => {
    const v = query[k]
    return v !== undefined && v !== null && String(v).trim() !== ''
  })
}

export function payloadFiltrosAvancadosFromQuery(query = {}) {
  const q = query || {}
  return {
    unidadesIds: splitList(q.unidade_id),
    servicoIds: splitList(q.servico_id),
    bairros: splitList(q.bairro),
    statusLista: splitList(q.status),
    urgenciaLista: splitList(q.urgencia),
    equipamentoId: (q.equipamento_id || '').toString().trim(),
    equipamentoRotulo: '',
    apenasCobrados: q.apenas_cobrados === 'true',
    apenasReabertos: q.apenas_reabertos === 'true',
    apenasSugestaoUrgenciaIa: q.apenas_sugestao_urgencia_ia === 'true',
    busca: q.busca ? String(q.busca).trim() : ''
  }
}

export function aplicarQueryRadarNaMesa(route, backofficeStore) {
  const q = route.query || {}
  if (!queryRadarTemFiltros(q)) return false
  const base = payloadFiltrosAvancadosFromQuery(q)
  backofficeStore.aplicarFiltrosAvancados({
    unidadesIds: base.unidadesIds,
    servicoIds: base.servicoIds,
    bairros: base.bairros,
    statusLista: base.statusLista,
    urgenciaLista: base.urgenciaLista,
    equipamentoId: base.equipamentoId,
    equipamentoRotulo: base.equipamentoRotulo,
    apenasCobrados: base.apenasCobrados,
    apenasReabertos: base.apenasReabertos,
    apenasSugestaoUrgenciaIa: base.apenasSugestaoUrgenciaIa
  })
  backofficeStore.setFiltro('busca', base.busca)
  backofficeStore.setFiltro('slaVencido', false)
  backofficeStore.setFiltro('critico', false)
  return true
}

export function aplicarQueryRadarNoSetorial(route, setorialStore) {
  const q = route.query || {}
  if (!queryRadarTemFiltros(q)) return false
  const base = payloadFiltrosAvancadosFromQuery(q)
  setorialStore.aplicarFiltrosAvancados({
    servicoIds: base.servicoIds,
    bairros: base.bairros,
    statusLista: base.statusLista,
    urgenciaLista: base.urgenciaLista,
    apenasReabertos: base.apenasReabertos,
    apenasSugestaoUrgenciaIa: base.apenasSugestaoUrgenciaIa
  })
  setorialStore.setFiltroBusca(base.busca)
  return true
}