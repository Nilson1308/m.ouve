/** Normaliza payloads de ``/backoffice/equipamentos``. */

function parseCoord(val) {
  if (val === null || val === undefined || val === '') return null
  const n = Number(val)
  return Number.isFinite(n) ? n : null
}

export function mapEquipamentoAdmin(api) {
  if (!api) return null
  const apelidos = Array.isArray(api.apelidos) ? api.apelidos : []
  return {
    id: String(api.id),
    nome: api.nome || '',
    tipo: api.tipo || 'outro',
    unidadeResponsavelId: api.unidade_responsavel
      ? String(api.unidade_responsavel)
      : api.unidade_responsavel_id
        ? String(api.unidade_responsavel_id)
        : '',
    unidadeResponsavelNome: api.unidade_responsavel_nome || '',
    apelidos,
    endereco: api.endereco || '',
    bairro: api.bairro || '',
    latitude: parseCoord(api.latitude),
    longitude: parseCoord(api.longitude),
    georreferenciado: Boolean(api.georreferenciado),
    ativo: api.ativo !== false,
    criadoEm: api.criado_em || null,
    atualizadoEm: api.atualizado_em || null
  }
}

export function payloadEquipamentoAdmin(form) {
  const apelidos = (form.apelidos || []).map((a) => String(a).trim()).filter(Boolean)
  const body = {
    nome: String(form.nome || '').trim(),
    tipo: form.tipo,
    unidade_responsavel: form.unidadeResponsavelId || form.unidade_responsavel,
    apelidos,
    endereco: String(form.endereco || '').trim(),
    bairro: String(form.bairro || '').trim(),
    ativo: form.ativo !== false
  }
  if (!body.unidade_responsavel) {
    delete body.unidade_responsavel
  }

  if (form.limparGeorreferencia) {
    body.latitude = null
    body.longitude = null
  } else {
    const lat = parseCoord(form.latitude)
    const lng = parseCoord(form.longitude)
    if (lat != null && lng != null) {
      body.latitude = lat
      body.longitude = lng
    }
  }
  return body
}

export function mapEquipamentoProtocolo(api) {
  if (!api) return null
  return {
    id: String(api.id),
    nome: api.nome || '',
    tipo: api.tipo || '',
    bairro: api.bairro || ''
  }
}