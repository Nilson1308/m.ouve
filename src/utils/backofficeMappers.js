/** Normaliza payloads da API /backoffice/* para o UI da Mesa de Trabalho. */

function iniciais(texto) {
  if (!texto) return '?'
  return texto
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0])
    .join('')
    .toUpperCase()
}

function buildTags(api) {
  const tags = []
  const dados = api.dados_dinamicos || {}
  if (dados.categoria_problema) tags.push(dados.categoria_problema)
  if (dados.tema) tags.push(dados.tema)
  if (api.urgencia && api.urgencia !== 'media') tags.push(api.urgencia)
  if (api.sla?.vencido) tags.push('atrasado')
  return tags.length ? tags : ['protocolo']
}

/**
 * @param {object} api — item de GET /backoffice/protocolos
 */
export function mapProtocoloBackoffice(api) {
  const ordens = api.ordens_servico || []
  const nomesUnidades = ordens
    .map((o) => o.unidade?.nome || o.nome_equipe)
    .filter(Boolean)

  const responsavel =
    nomesUnidades.length > 0
      ? {
          nome: nomesUnidades.join(', '),
          avatar: null,
          iniciais: iniciais(nomesUnidades[0])
        }
      : null

  const servicoNome =
    typeof api.servico === 'string' ? api.servico : api.servico?.nome || 'Serviço'

  const categoria =
    api.servico?.categoria_slug ||
    api.dados_dinamicos?.categoria_problema ||
    api.dados_dinamicos?.tema ||
    'geral'

  return {
    id: api.id,
    codigo: api.codigo,
    numero: api.codigo,
    servico: servicoNome,
    categoria,
    endereco: api.endereco || '',
    bairro: api.dados_dinamicos?.bairro || '',
    cidadao: api.cidadao || { nome: '—', telefone: '' },
    status: api.status,
    urgencia: api.urgencia || 'media',
    sla: {
      prazo: api.sla?.prazo_em ?? null,
      vencido: Boolean(api.sla?.vencido),
      horasRestantes: Number(api.sla?.horas_restantes ?? 0),
      slaHoras: api.sla?.sla_horas ?? api.servico?.sla_horas
    },
    criadoEm: api.data_criacao,
    responsavel,
    departamento: nomesUnidades[0] || null,
    ordens_servico: ordens,
    tags: buildTags(api),
    temAnexos: Boolean(api.tem_anexos),
    temLocalizacao: Boolean(api.tem_localizacao),
    localizacao: api.localizacao || null,
    dadosDinamicos: api.dados_dinamicos || {},
    superOsId: api.super_os_id || null,
    superOsCodigo: api.super_os_codigo || null,
    descricao: api.descricao || ''
  }
}

export function mapUnidadeBackoffice(api) {
  return {
    id: api.id,
    nome: api.nome,
    sigla: api.sigla || '',
    ativa: api.ativo !== false && api.ativa !== false
  }
}

function humanizeCampo(chave) {
  return String(chave)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

/** Valores exibidos na tabela — sem JSON/colas de array. */
export function formatValorColetado(valor) {
  if (valor == null || valor === '') return '—'

  if (Array.isArray(valor)) {
    return valor
      .map((item) => formatValorColetado(item))
      .filter((t) => t && t !== '—')
      .join(', ')
  }

  if (typeof valor === 'object') {
    return Object.values(valor)
      .map((item) => formatValorColetado(item))
      .filter((t) => t && t !== '—')
      .join(', ')
  }

  if (typeof valor === 'boolean') return valor ? 'Sim' : 'Não'

  if (typeof valor === 'string') {
    const texto = valor.trim()
    if (
      (texto.startsWith('[') && texto.endsWith(']')) ||
      (texto.startsWith('{') && texto.endsWith('}'))
    ) {
      try {
        return formatValorColetado(JSON.parse(texto))
      } catch {
        return texto.replace(/^\[|\]$/g, '').replace(/"/g, '').trim() || '—'
      }
    }
    return texto
  }

  return String(valor)
}

function mapDadosColetadosUI(dados) {
  if (!dados || typeof dados !== 'object') return {}
  const out = {}
  for (const [chave, valor] of Object.entries(dados)) {
    if (String(chave).startsWith('_')) continue
    const rotulo = humanizeCampo(chave)
    out[rotulo] = formatValorColetado(valor)
  }
  return out
}

export function mapOrdemServicoDetalhe(ordem, urgenciaProtocolo) {
  const statusUi =
    ordem.status === 'concluida'
      ? 'concluido'
      : ordem.status === 'cancelada'
        ? 'cancelado'
        : ordem.status

  return {
    id: ordem.id,
    unidade: ordem.unidade?.nome || ordem.nome_equipe || '—',
    unidade_sigla: ordem.unidade?.sigla || '',
    unidade_obj: ordem.unidade || null,
    responsavel: ordem.nome_equipe || ordem.unidade?.nome || '—',
    status: statusUi,
    statusApi: ordem.status,
    prioridade: urgenciaProtocolo || 'media',
    instrucao: ordem.instrucao || ordem.descricao || '',
    despacho_tecnico: (ordem.despacho_tecnico || '').trim(),
    observacoes_extras: (ordem.observacoes_extras || '').trim(),
    prazo: ordem.prazo_em || null,
    iniciado_em: ordem.criado_em || null,
    concluido_em: ordem.concluido_em || null,
    observacoes_execucao: ordem.observacoes_execucao || '',
    fotos_execucao: ordem.fotos_execucao || [],
    materiais_utilizados: ordem.materiais_utilizados || []
  }
}

/**
 * GET /backoffice/protocolos/:id — visão 360º
 * @param {object} api
 */
export function mapProtocoloDetalheBackoffice(api) {
  const base = mapProtocoloBackoffice(api)
  const loc = api.localizacao || {}
  const enderecoLinha = (loc.endereco || api.endereco || '').trim()

  return {
    ...base,
    tipo: 'zeladoria',
    atualizadoEm: api.data_atualizacao || base.criadoEm,
    dados_coletados: mapDadosColetadosUI(api.dados_coletados),
    historico_chat: api.historico_chat || [],
    historico_protocolo: api.historico_protocolo || [],
    localizacao: {
      endereco: enderecoLinha,
      numero: loc.numero || '',
      complemento: loc.complemento || '',
      bairro: loc.bairro || api.dados_dinamicos?.bairro || base.bairro || '',
      cidade: loc.cidade || '',
      estado: loc.estado || '',
      cep: loc.cep || '',
      latitude: loc.latitude ?? null,
      longitude: loc.longitude ?? null,
      pontos_referencia: loc.pontos_referencia || ''
    },
    ordens_servico: (api.ordens_servico || []).map((o) =>
      mapOrdemServicoDetalhe(o, base.urgencia)
    ),
    resposta_cidadao: api.resposta_cidadao || '',
    observacoes_internas: api.observacoes_internas || ''
  }
}
