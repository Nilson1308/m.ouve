/**
 * Mapeia GET /backoffice/dashboard/eficiencia (contrato v3.5+) → view do dashboard.
 */

function mapDemandaMapaItem(d) {
  if (!d) return null
  const lat = Number(d.latitude)
  const lng = Number(d.longitude)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null

  const sla = d.sla || {}
  return {
    id: d.id,
    codigo: d.codigo,
    numero: d.codigo,
    status: d.status,
    descricaoResumo: d.descricao_resumo || '',
    endereco: d.endereco || '',
    bairro: d.bairro || '',
    latitude: lat,
    longitude: lng,
    lat,
    lng,
    intensidade: 1,
    dataCriacao: d.data_criacao || null,
    cidadao: {
      nome: d.cidadao?.nome || 'Cidadão'
    },
    servico: {
      id: d.servico?.id || null,
      nome: d.servico?.nome || ''
    },
    sla: {
      slaHoras: sla.sla_horas ?? null,
      vencido: Boolean(sla.vencido),
      horasRestantes: sla.horas_restantes ?? null,
      prazoEm: sla.prazo_em || null
    }
  }
}

/**
 * Mapeia GET /backoffice/dashboard/mapa-calor → camada Leaflet.heat + marcadores.
 */
export function mapMapaCalorApi(api) {
  if (!api) return { coordenadas: [], demandas: [], total: 0, retornados: 0 }

  const demandas = (Array.isArray(api.demandas) ? api.demandas : [])
    .map(mapDemandaMapaItem)
    .filter(Boolean)

  let coordenadas = []
  if (demandas.length > 0) {
    coordenadas = demandas.map((d) => ({
      id: d.id,
      latitude: d.latitude,
      longitude: d.longitude,
      lat: d.lat,
      lng: d.lng,
      intensidade: 1
    }))
  } else {
    const ponderados = api.pontos_ponderados
    if (Array.isArray(ponderados) && ponderados.length > 0) {
      coordenadas = ponderados
        .filter((p) => Array.isArray(p) && p.length >= 2)
        .map(([lat, lng, peso]) => ({
          latitude: Number(lat),
          longitude: Number(lng),
          lat: Number(lat),
          lng: Number(lng),
          intensidade: Number(peso) || 1
        }))
    } else if (Array.isArray(api.pontos)) {
      coordenadas = api.pontos
        .filter((p) => Array.isArray(p) && p.length >= 2)
        .map(([lat, lng]) => ({
          latitude: Number(lat),
          longitude: Number(lng),
          lat: Number(lat),
          lng: Number(lng),
          intensidade: 1
        }))
    }
  }

  return {
    coordenadas,
    demandas,
    total: Number(api.total) || coordenadas.length,
    retornados: Number(api.retornados) || coordenadas.length,
    truncado: Boolean(api.truncado),
    filtros_aplicados: api.filtros_aplicados || {},
    gerado_em: api.gerado_em || null
  }
}

export function mapDashboardEficiencia(api) {
  if (!api) return null

  const ranking = (api.ranking_sla_unidades || []).map((u) => {
    const total = Number(u.total_protocolos) || 0
    const pctVencidos = Number(u.pct_vencidos) || 0
    const vencido = Math.round((total * pctVencidos) / 100)
    const no_prazo = Math.max(0, total - vencido)

    return {
      id: u.unidade_id,
      nome: u.nome || '',
      sigla: u.sigla || '',
      tma_horas: u.tma_horas ?? null,
      total,
      no_prazo,
      vencido,
      pct_vencidos: pctVencidos,
      pct_no_prazo: Number(u.pct_no_prazo) || 0,
      sem_vinculo_catalogo: Boolean(u.sem_vinculo_catalogo)
    }
  })

  const resumo = api.resumo_sla_mesa
  const temResumoMesa = resumo && typeof resumo === 'object'

  let totalProtocolos = 0
  let totalVencido = 0
  let totalNoPrazo = 0
  let taxaSla = 0

  if (temResumoMesa) {
    totalProtocolos = Number(resumo.total_itens) || Number(api.totais?.itens_mesa) || 0
    totalVencido = Number(resumo.vencidos) || 0
    const noPrazoRaw = Number(resumo.no_prazo)
    totalNoPrazo = Number.isFinite(noPrazoRaw)
      ? noPrazoRaw
      : Math.max(0, totalProtocolos - totalVencido)
    const taxaRaw = Number(resumo.taxa_cumprimento)
    taxaSla = Number.isFinite(taxaRaw)
      ? taxaRaw
      : totalProtocolos > 0
        ? (totalNoPrazo / totalProtocolos) * 100
        : 0
  } else {
    // API antiga (sem resumo_sla_mesa): usa só o que o ranking cobre — não inventar “no prazo”
    totalProtocolos = Number(api.totais?.protocolos) || ranking.reduce((s, u) => s + u.total, 0) || 0
    totalVencido = ranking.reduce((s, u) => s + u.vencido, 0)
    totalNoPrazo = ranking.reduce((s, u) => s + u.no_prazo, 0)
    taxaSla =
      totalProtocolos > 0 && totalNoPrazo + totalVencido > 0
        ? (totalNoPrazo / (totalNoPrazo + totalVencido)) * 100
        : 0
  }

  return {
    escopo: api.escopo,
    unidade_id: api.unidade_id,
    gerado_em: api.gerado_em,
    tma_global_horas: api.tma_geral?.horas ?? null,
    tma_variacao: null,
    taxa_sla_cumprido: taxaSla,
    sla_variacao: null,
    total_protocolos: totalProtocolos,
    total_no_prazo: totalNoPrazo,
    total_vencido: totalVencido,
    total_protocolos_cadastro: Number(api.totais?.protocolos) || 0,
    meta_tma_dias: 5,
    ranking_unidades: ranking,
    funil_status: api.funil_status || [],
    protocolos_concluidos_tma: api.tma_geral?.protocolos_concluidos ?? 0
  }
}

/**
 * Mapeia GET /backoffice/dashboard/qualidade → MatrizQualidade.vue
 */
export function mapDashboardQualidade(api) {
  if (!api) {
    return {
      unidades: [],
      resumo: {
        total_resolvidos: 0,
        taxa_sla_cumprido: null,
        media_satisfacao: null,
        total_avaliacoes: 0,
        percentual_satisfeitos: null
      },
      escopo: null,
      unidade_id: null,
      gerado_em: null,
      filtros_aplicados: {}
    }
  }

  const unidades = (Array.isArray(api.matriz_unidades) ? api.matriz_unidades : []).map(
    (u) => ({
      id: u.unidade_id,
      unidade_id: u.unidade_id,
      nome: u.nome || '',
      sigla: u.sigla || '',
      taxa_sla_cumprido: Number(u.taxa_sla_cumprido) || 0,
      media_satisfacao:
        u.media_satisfacao != null && Number.isFinite(Number(u.media_satisfacao))
          ? Number(u.media_satisfacao)
          : null,
      total_avaliacoes: Number(u.total_avaliacoes) || 0,
      total_resolvidos: Number(u.total_resolvidos) || 0,
      resolvidos_no_prazo: Number(u.resolvidos_no_prazo) || 0,
      sem_vinculo_catalogo: Boolean(u.sem_vinculo_catalogo)
    })
  )

  const r = api.resumo_geral || {}
  return {
    escopo: api.escopo ?? null,
    unidade_id: api.unidade_id ?? null,
    gerado_em: api.gerado_em ?? null,
    filtros_aplicados: api.filtros_aplicados || {},
    unidades,
    resumo: {
      total_resolvidos: Number(r.total_resolvidos) || 0,
      taxa_sla_cumprido:
        r.taxa_sla_cumprido != null ? Number(r.taxa_sla_cumprido) : null,
      media_satisfacao:
        r.media_satisfacao != null ? Number(r.media_satisfacao) : null,
      total_avaliacoes: Number(r.total_avaliacoes) || 0,
      percentual_satisfeitos:
        r.percentual_satisfeitos != null && Number.isFinite(Number(r.percentual_satisfeitos))
          ? Number(r.percentual_satisfeitos)
          : null
    }
  }
}

/**
 * Mapeia GET /backoffice/dashboard/inelegibilidade → DashboardInelegibilidade.vue
 * Retorno: total_sessoes_inelegiveis, ranking_por_servico, ranking_por_motivo
 */
export function mapDashboardInelegibilidade(api) {
  if (!api) {
    return {
      total_sessoes_inelegiveis: 0,
      ranking_por_servico: [],
      ranking_por_motivo: [],
      escopo: null,
      gerado_em: null,
      filtros_aplicados: {}
    }
  }

  const rankingServico = (Array.isArray(api.ranking_por_servico) ? api.ranking_por_servico : []).map(
    (s) => ({
      servico_id: s.servico_id,
      servico_nome: s.servico_nome || 'Sem nome',
      total: Number(s.total) || 0
    })
  )

  const rankingMotivo = (Array.isArray(api.ranking_por_motivo) ? api.ranking_por_motivo : []).map(
    (m) => ({
      motivo: m.motivo || 'Sem motivo',
      total: Number(m.total) || 0
    })
  )

  return {
    total_sessoes_inelegiveis: Number(api.total_sessoes_inelegiveis) || 0,
    ranking_por_servico: rankingServico,
    ranking_por_motivo: rankingMotivo,
    escopo: api.escopo ?? null,
    gerado_em: api.gerado_em ?? null,
    filtros_aplicados: api.filtros_aplicados || {}
  }
}