/** Helpers scatter-gather (nós = ordens de serviço por secretaria). */

const FECHADOS = new Set(['concluida', 'concluido'])
const CANCELADOS = new Set(['cancelada', 'cancelado'])

export function statusOrdemNo(ordem) {
  if (!ordem) return ''
  return (
    ordem.status_api ||
    ordem.statusApi ||
    ordem.status ||
    ''
  ).toLowerCase()
}

export function nomeSecretariaNo(ordem) {
  return (
    ordem.unidade?.sigla ||
    ordem.unidade_sigla ||
    ordem.unidade_obj?.sigla ||
    ordem.unidade?.nome ||
    ordem.unidade_obj?.nome ||
    (typeof ordem.unidade === 'string' ? ordem.unidade : null) ||
    ordem.nome_equipe ||
    'Secretaria'
  )
}

export function noFechado(ordem) {
  return FECHADOS.has(statusOrdemNo(ordem))
}

export function noAberto(ordem) {
  const s = statusOrdemNo(ordem)
  return s && !FECHADOS.has(s) && !CANCELADOS.has(s)
}

export function resumoNos(ordens = []) {
  const lista = Array.isArray(ordens) ? ordens : []
  const ativas = lista.filter((o) => !CANCELADOS.has(statusOrdemNo(o)))
  const total = ativas.length
  const fechados = ativas.filter((o) => noFechado(o)).length
  return {
    total,
    fechados,
    abertos: Math.max(0, total - fechados),
    percentual: total ? Math.round((fechados / total) * 100) : 0
  }
}

export function emojiStatusNo(ordem) {
  if (noFechado(ordem)) return '🟢'
  if (CANCELADOS.has(statusOrdemNo(ordem))) return '⚫'
  return '🟡'
}

export function legendaStatusNo(ordem) {
  if (noFechado(ordem)) return 'Nó fechado'
  if (CANCELADOS.has(statusOrdemNo(ordem))) return 'Cancelado'
  return 'Nó aberto'
}

/** Nós ainda em tramitação (para Kanban / cards). */
export function nosAbertos(ordens = []) {
  return (Array.isArray(ordens) ? ordens : []).filter((o) => noAberto(o))
}

/** Gather completo — pronto para validação da Ouvidoria. */
export function protocoloAguardandoValidacao(protocolo) {
  if (!protocolo) return false
  if (protocolo.status === 'aguardando_revisao') return true
  if (protocolo.status !== 'em_andamento') return false
  const { total, abertos } = resumoNos(protocolo.ordens_servico)
  return total > 0 && abertos === 0
}

export function protocoloAguardandoCidadao(protocolo) {
  return protocolo?.status === 'aguardando_cidadao'
}

/** Scatter ativo — pelo menos um nó aberto (ou em andamento sem OS legadas). */
export function protocoloEmTramitacao(protocolo) {
  if (!protocolo || protocolo.status !== 'em_andamento') return false
  if (protocoloAguardandoValidacao(protocolo)) return false
  const { total, abertos } = resumoNos(protocolo.ordens_servico)
  if (total === 0) return true
  return abertos > 0
}