/** Normaliza protocolos, Kanban unificado e dossiê Super OS. */

import {
  formatValorColetado,
  mapOrdemServicoDetalhe
} from '@/utils/backofficeMappers'

const MOGI_CENTER = { lat: -23.522, lng: -46.1883 }

function humanizeCampo(chave) {
  return String(chave)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

function mapDadosColetadosUI(dados) {
  if (!dados || typeof dados !== 'object') return {}
  const out = {}
  for (const [chave, valor] of Object.entries(dados)) {
    if (String(chave).startsWith('_')) continue
    out[humanizeCampo(chave)] = formatValorColetado(valor)
  }
  return out
}

function mapSlaKanban(sla = {}) {
  return {
    prazo: sla.prazo_em ?? null,
    vencido: Boolean(sla.vencido),
    horasRestantes: Number(sla.horas_restantes ?? 0),
    slaHoras: sla.sla_horas ?? null
  }
}

/**
 * Item de GET /backoffice/kanban (protocolo | super_os).
 */
export function mapKanbanItem(api) {
  const tipo = api.tipo === 'super_os' ? 'super_os' : 'protocolo'
  const sla = mapSlaKanban(api.sla)
  const base = {
    id: api.id,
    tipo,
    codigo: api.codigo,
    numero: api.codigo,
    titulo: api.titulo || api.codigo,
    status: api.status,
    urgencia: api.urgencia || 'media',
    sla,
    criadoEm: api.criado_em,
    endereco: api.endereco || '',
    servico: api.servico_nome || 'Serviço',
    categoria: 'geral',
    prazoHoras: api.prazo_horas,
    qtdFilhos: Number(api.qtd_filhos ?? 0),
    precisaIntegracaoAncora: Boolean(api.precisa_integracao_ancora),
    bairro: '',
    cidadao:
      tipo === 'super_os'
        ? { nome: `${api.qtd_filhos || 0} cidadãos`, telefone: '' }
        : {
            nome: api.cidadao?.nome || '—',
            telefone: api.cidadao?.telefone || ''
          },
    responsavel: null,
    departamento: null,
    ordens_servico: [],
    tags: tipo === 'super_os' ? ['super_os', 'incidente_massa'] : ['protocolo'],
    temAnexos: false,
    temLocalizacao: Boolean(api.endereco),
    localizacao: null,
    dadosDinamicos: {},
    superOsId: null,
    superOsCodigo: null,
    descricao: api.titulo || '',
    triagemSugerida:
      tipo === 'protocolo' && api.triagem_sugerida && Object.keys(api.triagem_sugerida).length
        ? api.triagem_sugerida
        : null
  }
  if (tipo === 'super_os') {
    base.numero = api.codigo
  }
  return base
}

/**
 * GET /backoffice/super-os/:id — dossiê
 */
export function mapSuperOSDetalhe(api) {
  const urgencia = api.urgencia || 'media'
  const filhos = (api.protocolos_filhos || []).map((f) => ({
    id: f.id,
    codigo: f.codigo,
    numero: f.codigo,
    status: f.status,
    descricao: f.descricao || '',
    endereco: f.endereco_texto || f.localizacao?.endereco || '',
    criadoEm: f.data_criacao,
    cidadao: f.cidadao || { nome: '—', telefone: '', email: '' },
    servico: f.servico?.nome || 'Serviço',
    dados_coletados: mapDadosColetadosUI(f.dados_coletados),
    historico_chat: f.historico_chat || [],
    historico_protocolo: f.historico_protocolo || [],
    sla: mapSlaKanban(f.sla),
    urgencia: f.urgencia || 'media',
    localizacao: {
      endereco: f.localizacao?.endereco || f.endereco_texto || '',
      latitude: f.localizacao?.latitude ?? null,
      longitude: f.localizacao?.longitude ?? null
    }
  }))

  const sla = mapSlaKanban(api.sla)
  const centro = api.centroide || {}
  const servico =
    filhos[0]?.servico || api.protocolos_filhos?.[0]?.servico?.nome || 'Incidente em massa'

  return {
    id: api.id,
    tipo: 'super_os',
    codigo: api.codigo,
    numero: api.codigo,
    titulo: api.titulo_resumo,
    tituloResumo: api.titulo_resumo,
    descricaoGeral: api.descricao_geral || '',
    status: api.status,
    urgencia,
    sla,
    criadoEm: api.criado_em,
    atualizadoEm: api.atualizado_em,
    quantidadeProtocolos: api.quantidade_protocolos ?? filhos.length,
    protocolosFilhos: filhos,
    centroide: {
      latitude: centro.latitude ?? api.latitude_centro,
      longitude: centro.longitude ?? api.longitude_centro
    },
    ordens_servico_ids: api.ordens_servico_ids || [],
    ordens_servico: (api.ordens_servico || []).map((o) =>
      mapOrdemServicoDetalhe(o, urgencia)
    ),
    servico: typeof servico === 'string' ? servico : servico?.nome || 'Serviço',
    categoria: 'geral',
    endereco: filhos[0]?.endereco || '',
    bairro: '',
    cidadao: { nome: `${filhos.length} cidadãos afetados`, telefone: '' },
    tags: ['super_os']
  }
}

/** Objeto compatível com ProtocoloOperacao / DespacharProtocolo. */
export function superOsComoProtocoloOperacao(superOs) {
  if (!superOs) return null
  return {
    id: superOs.id,
    numero: superOs.codigo,
    codigo: superOs.codigo,
    servico: superOs.servico,
    categoria: superOs.categoria,
    endereco: superOs.endereco,
    bairro: superOs.bairro,
    status: superOs.status,
    urgencia: superOs.urgencia,
    sla: superOs.sla,
    criadoEm: superOs.criadoEm,
    atualizadoEm: superOs.atualizadoEm,
    cidadao: superOs.cidadao,
    ordens_servico: superOs.ordens_servico || [],
    qtdFilhos: superOs.quantidadeProtocolos
  }
}

export function coordenadasDeProtocolo(p) {
  const loc = p.localizacao || {}
  let lat = loc.latitude ?? loc.lat
  let lng = loc.longitude ?? loc.lng

  const dados = p.dados_dinamicos || p.dadosDinamicos || {}
  if (lat == null) lat = dados.latitude ?? dados.lat
  if (lng == null) lng = dados.longitude ?? dados.lng

  if (lat == null || lng == null || Number.isNaN(Number(lat))) return null
  return { lat: Number(lat), lng: Number(lng) }
}

/**
 * @param {object} p — item mapeado da mesa (backofficeMappers)
 */
export function mapProtocoloParaMapa(p) {
  const coordenadas = coordenadasDeProtocolo(p)
  if (!coordenadas) return null
  return {
    id: p.id,
    codigo: p.codigo || p.numero,
    servico: p.servico || 'Serviço',
    endereco: p.endereco || p.bairro || '',
    coordenadas,
    urgencia: p.urgencia || 'normal',
    criado_em: p.criadoEm,
    foto_url: p.fotoUrl || null,
    status: p.status
  }
}

export function protocolosElegiveisMapa(protocolos) {
  return (protocolos || [])
    .filter(
      (p) =>
        p.tipo !== 'super_os' &&
        (p.status === 'em_analise' || p.status === 'em_andamento') &&
        !p.superOsId
    )
    .map(mapProtocoloParaMapa)
    .filter(Boolean)
}

function extrairRegiaoDoTitulo(titulo) {
  if (!titulo) return 'Região'
  const m = titulo.match(/próximos?\s+[àa]\s+(.+)$/i)
  return m ? m[1].trim() : 'Área mapeada'
}

function estimarEconomia(quantidade) {
  const q = Math.max(2, quantidade || 2)
  return {
    equipes: Math.max(1, q - 1),
    tempo_horas: q * 2,
    custo_reais: q * 480
  }
}

/**
 * @param {object} api — item de GET /backoffice/super-os/sugestoes
 * @param {Map<string, object>} protocolosIndex — protocolos da mesa por UUID
 */
export function mapSugestaoSuperOS(api, protocolosIndex = new Map()) {
  const ids = api.protocolo_ids || []
  const protocolos = ids
    .map((id) => {
      const p = protocolosIndex.get(id)
      if (p) return mapProtocoloParaMapa(p)
      if (!id) return null
      return {
        id,
        codigo: String(id).slice(0, 8).toUpperCase(),
        servico: api.servico_nome || 'Serviço',
        endereco: '—',
        coordenadas: {
          lat: api.latitude_centro ?? MOGI_CENTER.lat,
          lng: api.longitude_centro ?? MOGI_CENTER.lng
        },
        urgencia: 'normal',
        criado_em: null,
        foto_url: null
      }
    })
    .filter(Boolean)

  const qtd = api.quantidade || ids.length || protocolos.length
  const raioMetros = api.raio_metros ?? 300
  const tipoAcao = api.tipo_acao || 'criar'
  const superOsId = api.super_os_id || null
  const ancoraId = api.protocolo_ancora_id || null

  const sugestaoId =
    tipoAcao === 'anexar' && superOsId
      ? `anexar-${superOsId}-${ids.join(',')}`
      : tipoAcao === 'criar_retroativa' && ancoraId
        ? `retroativa-${ancoraId}-${ids.join(',')}`
        : `cluster-${api.servico_id}-${api.latitude_centro}-${api.longitude_centro}-${ids.join(',')}`

  return {
    id: sugestaoId,
    tipo_acao: tipoAcao,
    super_os_id: superOsId,
    super_os_codigo: api.super_os_codigo || null,
    super_os_titulo: api.super_os_titulo || null,
    protocolo_ancora_id: ancoraId,
    protocolo_ancora_codigo: api.protocolo_ancora_codigo || null,
    titulo_resumo: api.titulo,
    tipo_servico: api.servico_nome || 'Serviço',
    regiao: extrairRegiaoDoTitulo(api.titulo),
    confianca_ia: Math.min(0.98, 0.72 + qtd * 0.05),
    protocolo_ids: ids,
    protocolos,
    centro_geografico: {
      lat: api.latitude_centro ?? MOGI_CENTER.lat,
      lng: api.longitude_centro ?? MOGI_CENTER.lng
    },
    raio_km: raioMetros / 1000,
    raio_metros: raioMetros,
    economia_estimada: estimarEconomia(qtd),
    servico_id: api.servico_id,
    quantidade: qtd
  }
}