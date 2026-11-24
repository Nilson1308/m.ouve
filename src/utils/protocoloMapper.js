import { resolveMediaUrl } from '@/utils/mediaUrl'

function nomeArquivoAnexo(url) {
  try {
    const parts = url.split('/')
    return decodeURIComponent(parts[parts.length - 1] || 'Anexo')
  } catch {
    return 'Anexo'
  }
}

/**
 * Normaliza protocolo da API (snake_case) para o formato usado nas views.
 */
export function mapProtocoloFromApi(protocolo) {
  if (!protocolo) return null

  const anexos = (protocolo.anexos || [])
    .map((anexo) => {
      if (typeof anexo === 'string') {
        const url = resolveMediaUrl(anexo)
        return url ? { id: url, url, tipo: '', nome: nomeArquivoAnexo(url) } : null
      }
      if (anexo?.url) {
        const url = resolveMediaUrl(anexo.url)
        return {
          id: anexo.id ?? url,
          url,
          tipo: anexo.tipo || '',
          nome: nomeArquivoAnexo(url)
        }
      }
      return null
    })
    .filter(Boolean)

  let equipe = protocolo.equipe
  if (equipe && typeof equipe === 'object') {
    equipe = equipe.nome || equipe.id
  }

  const avaliacaoRaw = protocolo.avaliacao
  const avaliacao =
    avaliacaoRaw && typeof avaliacaoRaw === 'object'
      ? {
          nota: Number(avaliacaoRaw.nota) || 0,
          comentario: avaliacaoRaw.comentario || '',
          criadaEm: avaliacaoRaw.criada_em ?? avaliacaoRaw.criadaEm ?? null
        }
      : null

  const camposSolicitacao = Array.isArray(protocolo.campos_solicitacao)
    ? protocolo.campos_solicitacao.map((c) => ({
        chave: c.chave,
        rotulo: c.rotulo,
        valor: c.valor
      }))
    : protocolo.camposSolicitacao || []

  return {
    ...protocolo,
    campos_solicitacao: camposSolicitacao,
    camposSolicitacao,
    dataCriacao: protocolo.data_criacao ?? protocolo.dataCriacao,
    dataAtualizacao: protocolo.data_atualizacao ?? protocolo.dataAtualizacao,
    tipoManifestacao: protocolo.tipo_manifestacao ?? protocolo.tipoManifestacao,
    pode_avaliar: Boolean(protocolo.pode_avaliar),
    podeAvaliar: Boolean(protocolo.pode_avaliar ?? protocolo.podeAvaliar),
    pode_cobrar: Boolean(protocolo.pode_cobrar),
    podeCobrar: Boolean(protocolo.pode_cobrar ?? protocolo.podeCobrar),
    motivo_bloqueio_cobranca: protocolo.motivo_bloqueio_cobranca ?? null,
    motivoBloqueioCobranca: protocolo.motivo_bloqueio_cobranca ?? protocolo.motivoBloqueioCobranca ?? null,
    proxima_cobranca_em: protocolo.proxima_cobranca_em ?? null,
    proximaCobrancaEm: protocolo.proxima_cobranca_em ?? protocolo.proximaCobrancaEm ?? null,
    qtd_cobrancas_cidadao: Number(protocolo.qtd_cobrancas_cidadao ?? 0),
    qtdCobrancasCidadao: Number(protocolo.qtd_cobrancas_cidadao ?? protocolo.qtdCobrancasCidadao ?? 0),
    prazo_sla: protocolo.prazo_sla ?? null,
    prazoSla: protocolo.prazo_sla ?? protocolo.prazoSla ?? null,
    dias_atraso: Number(protocolo.dias_atraso ?? 0),
    diasAtraso: Number(protocolo.dias_atraso ?? protocolo.diasAtraso ?? 0),
    ultimo_alerta_sla_nivel: protocolo.ultimo_alerta_sla_nivel ?? '',
    ultimoAlertaSlaNivel: protocolo.ultimo_alerta_sla_nivel ?? protocolo.ultimoAlertaSlaNivel ?? '',
    avaliacao,
    equipe,
    anexos,
    historicoApi: protocolo.historico
  }
}

export function mapListaProtocolosResponse(response) {
  const lista = response?.data ?? response ?? []
  return lista.map(mapProtocoloFromApi)
}
