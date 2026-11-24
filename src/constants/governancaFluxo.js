/** Rótulos de governança (catálogo e protocolo). */

export function badgeGovernancaServico(servico) {
  if (!servico) return null
  const fluxo = servico.fluxo_tramitacao || 'direto_secretaria'
  if (fluxo === 'ouvidoria_encaminha') {
    return {
      label: 'Ouvidoria',
      title: 'Triagem e despacho na Mesa; homologação obrigatória na saída.',
      class:
        'bg-amber-100 text-amber-900 dark:bg-amber-950/50 dark:text-amber-200 ring-1 ring-amber-200/80 dark:ring-amber-700/50'
    }
  }
  if (servico.exigir_validacao_ouvidoria) {
    return {
      label: 'Direto · Homologado',
      title: 'OS automática na secretaria; resposta passa pela Ouvidoria antes do cidadão.',
      class:
        'bg-violet-100 text-violet-900 dark:bg-violet-950/50 dark:text-violet-200 ring-1 ring-violet-200/80 dark:ring-violet-700/50'
    }
  }
  return {
    label: 'Direto · Autônomo',
    title: 'OS automática na secretaria; resposta final enviada direto ao cidadão.',
    class:
      'bg-teal-100 text-teal-900 dark:bg-teal-950/50 dark:text-teal-200 ring-1 ring-teal-200/80 dark:ring-teal-700/50'
  }
}

export function indicadorFluxoDiretoProtocolo(protocolo) {
  const fluxo =
    protocolo?.fluxoTramitacao ||
    protocolo?.servicoFluxoTramitacao ||
    protocolo?.servico?.fluxo_tramitacao
  if (fluxo !== 'direto_secretaria') return null
  return {
    label: 'Fluxo direto',
    title: 'Protocolo despachado automaticamente à secretaria executora na abertura.'
  }
}