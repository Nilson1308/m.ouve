/** Normaliza categoria aninhada (API) ou string legada. */
export function nomeCategoriaServico(servico) {
  if (!servico) return 'Outros'
  const cat = servico.categoria
  if (typeof cat === 'string') return cat
  return cat?.nome || 'Outros'
}

export function slugCategoriaServico(servico) {
  const cat = servico?.categoria
  if (cat && typeof cat === 'object' && cat.slug) return cat.slug
  if (typeof cat === 'string') {
    return cat.toLowerCase().replace(/\s+/g, '_')
  }
  return nomeCategoriaServico(servico).toLowerCase().replace(/\s+/g, '_')
}

export function ordemCategoriaServico(servico) {
  const cat = servico?.categoria
  if (cat && typeof cat === 'object' && cat.ordem != null) return cat.ordem
  return 999
}

export function iconeCategoriaServico(servico) {
  const cat = servico?.categoria
  if (cat && typeof cat === 'object' && cat.icone) return cat.icone
  return null
}
