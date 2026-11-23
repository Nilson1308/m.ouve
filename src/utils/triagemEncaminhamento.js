/** Unidades e pré-preenchimento de despacho a partir de ``triagemSugerida``. */

export function unidadesTriagemSugeridas(triagem) {
  if (!triagem || typeof triagem !== 'object') return []
  const lista = triagem.unidades_sugeridas ?? triagem.unidadesSugeridas
  return Array.isArray(lista) ? lista : []
}

export function temTriagemEncaminhamento(protocolo) {
  return unidadesTriagemSugeridas(protocolo?.triagemSugerida).length > 0
}

export function resumoEncaminhamentoTexto(protocolo) {
  const unidades = unidadesTriagemSugeridas(protocolo?.triagemSugerida)
  if (!unidades.length) return ''
  const primeiro = (unidades[0].nome || 'Unidade').trim()
  if (unidades.length === 1) return primeiro
  return `${primeiro} +${unidades.length - 1}`
}

/**
 * @param {object} protocolo — item mapeado do backoffice
 * @param {object[]|undefined} unidades — subconjunto; padrão = todas da triagem
 * @returns {{ unidadeId: string, instrucao: string, prazo_horas: number }[]}
 */
export function buildPrefillOrdensFromTriagem(protocolo, unidades) {
  const lista = Array.isArray(unidades)
    ? unidades
    : unidadesTriagemSugeridas(protocolo?.triagemSugerida)
  if (!lista.length) return []

  const prazo = protocolo?.sla?.slaHoras || 48
  const jaDespachadas = new Set(
    (protocolo?.ordens_servico || [])
      .map((o) => String(o.unidade_id || o.unidade?.id || ''))
      .filter(Boolean)
  )

  return lista
    .filter((u) => u?.id && !jaDespachadas.has(String(u.id)))
    .map((u) => ({
      unidadeId: String(u.id),
      instrucao: `Encaminhamento sugerido: ${(u.motivo || u.nome || '').trim()}`,
      prazo_horas: prazo
    }))
}