/** Mapeamento API v4.17 — Agente IA proativo (Radar). */

const ESCOPO_LABEL = {
  controladoria: 'Controladoria',
  ouvidoria: 'Ouvidoria',
  unidade: 'Secretaria'
}

export function labelEscopoBriefing(escopoTipo, unidadeNome = '') {
  if (escopoTipo === 'unidade' && unidadeNome) return unidadeNome
  return ESCOPO_LABEL[escopoTipo] || escopoTipo || 'Operacional'
}

export function labelModoGeracao(modo) {
  return modo === 'llm' ? 'Síntese IA' : 'Análise municipal'
}

export function normalizarBriefing(data) {
  if (!data || typeof data !== 'object') return null
  const conteudo = data.conteudo || {}
  return {
    briefingId: data.briefing_id,
    escopoTipo: data.escopo_tipo,
    unidadeId: data.unidade_id,
    dataReferencia: data.data_referencia,
    modoGeracao: data.modo_geracao,
    modeloLlm: data.modelo_llm,
    resumoExecutivo: conteudo.resumo_executivo || '',
    resumoExecutivoEmail: data.resumo_executivo_email || conteudo.resumo_executivo_email || '',
    insights: Array.isArray(conteudo.insights) ? conteudo.insights : [],
    minhasAvaliacoes: data.minhas_avaliacoes && typeof data.minhas_avaliacoes === 'object'
      ? { ...data.minhas_avaliacoes }
      : {},
    tokensMesAtual: data.tokens_mes_atual,
    orcamentoTokensMensal: data.orcamento_tokens_mensal,
    percentualConsumo: data.percentual_consumo
  }
}

export function normalizarConfigAgente(data) {
  if (!data) return null
  return {
    agente_ativo: Boolean(data.agente_ativo),
    briefing_proativo_ativo: Boolean(data.briefing_proativo_ativo),
    briefing_hora_geracao: Number(data.briefing_hora_geracao ?? 7),
    incluir_resumo_no_digest_email: Boolean(data.incluir_resumo_no_digest_email),
    copiloto_chat_ativo: Boolean(data.copiloto_chat_ativo),
    limite_perguntas_dia_por_usuario: Number(data.limite_perguntas_dia_por_usuario ?? 30),
    orcamento_tokens_mensal: Number(data.orcamento_tokens_mensal ?? 0),
    anomalia_percentual_minimo: Number(data.anomalia_percentual_minimo ?? 50),
    anomalia_volume_minimo: Number(data.anomalia_volume_minimo ?? 3),
    dias_parado_triagem_alerta: Number(data.dias_parado_triagem_alerta ?? 2),
    atualizado_em: data.atualizado_em
  }
}

export function categoriaInsightClasses(categoria) {
  switch (categoria) {
    case 'acao_imediata':
      return {
        border: 'border-l-amber-500 dark:border-l-amber-400',
        bg: 'bg-amber-50/80 dark:bg-amber-950/25',
        icon: 'text-amber-600 dark:text-amber-400',
        pill: 'bg-amber-100 text-amber-900 dark:bg-amber-900/50 dark:text-amber-100'
      }
    case 'sugestao_conducao':
      return {
        border: 'border-l-emerald-500 dark:border-l-emerald-400',
        bg: 'bg-emerald-50/80 dark:bg-emerald-950/25',
        icon: 'text-emerald-600 dark:text-emerald-400',
        pill: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-900/50 dark:text-emerald-100'
      }
    default:
      return {
        border: 'border-l-indigo-500 dark:border-l-indigo-400',
        bg: 'bg-indigo-50/80 dark:bg-indigo-950/25',
        icon: 'text-indigo-600 dark:text-indigo-400',
        pill: 'bg-indigo-100 text-indigo-900 dark:bg-indigo-900/50 dark:text-indigo-100'
      }
  }
}