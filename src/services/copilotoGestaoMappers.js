/** Mapeamento contrato v4.18 — Copiloto Gestor */

const TOOL_LABELS = {
  obter_resumo_eficiencia: 'Eficiência',
  listar_gargalos_sla_e_cobrancas: 'SLA & Cobranças',
  listar_anomalias_equipamentos_bairros: 'Território e equipamentos',
  obter_qualidade_e_retrabalho: 'Qualidade e retrabalho',
  resumir_fila_operacional: 'Fila operacional',
  obter_resumo_inelegibilidade: 'Inelegibilidade'
}

export function labelFerramentaCopiloto(nome) {
  return TOOL_LABELS[nome] || nome
}

export function normalizarConfigCopiloto(data) {
  if (!data || typeof data !== 'object') return null
  return {
    copilotoDisponivel: Boolean(data.copiloto_disponivel),
    motivoIndisponivel: data.motivo_indisponivel || null,
    perspectiva: data.perspectiva || 'controladoria',
    unidadeNome: data.unidade_nome || null,
    perguntasHoje: Number(data.perguntas_hoje ?? 0),
    limiteDiario: Number(data.limite_diario ?? 30),
    budgetEsgotado: Boolean(data.budget_esgotado),
    sugestoesIniciais: Array.isArray(data.sugestoes_iniciais) ? [...data.sugestoes_iniciais] : []
  }
}

export function normalizarSessaoResumo(raw) {
  return {
    id: raw.id,
    titulo: raw.titulo || 'Conversa',
    perspectiva: raw.perspectiva,
    unidadeId: raw.unidade_id || null,
    contextoRotaInicial: raw.contexto_rota_inicial || '',
    criadoEm: raw.criado_em,
    atualizadoEm: raw.atualizado_em
  }
}

export function normalizarMensagemCopiloto(raw) {
  return {
    id: raw.id,
    papel: raw.papel,
    conteudo: raw.conteudo || '',
    statusProcessamento: raw.status_processamento || 'concluida',
    ferramentasUsadas: Array.isArray(raw.ferramentas_usadas) ? raw.ferramentas_usadas : [],
    referencias: Array.isArray(raw.referencias) ? raw.referencias : [],
    modoGeracao: raw.modo_geracao || '',
    modeloLlm: raw.modelo_llm || '',
    tokensEntrada: Number(raw.tokens_entrada ?? 0),
    tokensSaida: Number(raw.tokens_saida ?? 0),
    erroDetalhe: raw.erro_detalhe || '',
    criadoEm: raw.criado_em
  }
}

export function normalizarSessaoDetalhe(data) {
  return {
    sessaoId: data.sessao_id,
    titulo: data.titulo,
    perspectiva: data.perspectiva,
    unidadeId: data.unidade_id || null,
    contextoRotaInicial: data.contexto_rota_inicial || '',
    criadoEm: data.criado_em,
    atualizadoEm: data.atualizado_em,
    iaProcessando: Boolean(data.ia_processando),
    mensagens: (data.mensagens || []).map(normalizarMensagemCopiloto)
  }
}

export function normalizarPerguntarResposta(data) {
  return {
    sessaoId: data.sessao_id,
    mensagemAssistenteId: data.mensagem_assistente_id,
    status: data.status,
    perguntasHoje: Number(data.perguntas_hoje ?? 0),
    limiteDiario: Number(data.limite_diario ?? 30)
  }
}