/** Conversão SLA — API sempre em horas (sla_horas). */

export function horasParaExibicao(horas) {
  const h = Math.max(0, Math.floor(Number(horas) || 0))
  if (!h) return { unidade: 'horas', valor: 1 }
  if (h >= 24 && h % 24 === 0) {
    return { unidade: 'dias', valor: h / 24 }
  }
  return { unidade: 'horas', valor: h }
}

export function valorUnidadeParaHoras(valor, unidade) {
  const v = Math.max(0, Number(valor) || 0)
  if (unidade === 'dias') return Math.round(v * 24 * 100) / 100
  return Math.round(v)
}

export function limitesSla(unidade) {
  if (unidade === 'dias') {
    return { min: 0.25, max: 365, step: 0.25 }
  }
  return { min: 1, max: 8760, step: 1 }
}

export function formatarSlaDuracao(horas) {
  const h = Number(horas) || 0
  if (!h) return ''
  const dias = Math.floor(h / 24)
  const rest = h % 24
  if (!dias) return `${h} hora${h > 1 ? 's' : ''}`
  if (!rest) return `${dias} dia${dias > 1 ? 's' : ''} (${h}h)`
  return `${dias}d ${rest}h (${h} horas)`
}