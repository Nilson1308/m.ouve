/** Labels e formatação — diligência / SLA pausado (v4.14). */

const STATUS_DILIGENCIA = {
  aguardando_cidadao: 'Aguardando cidadão',
  respondida: 'Respondida',
  expirada: 'Expirada',
  cancelada: 'Cancelada'
}

const MOTIVO_BLOQUEIO_DILIGENCIA = {
  desabilitado: 'Diligência desativada nas configurações do município.',
  protocolo_encerrado: 'Protocolo já encerrado.',
  diligencia_ativa: 'Já existe uma diligência aguardando resposta do cidadão.',
  limite_diligencias: 'Limite de diligências por protocolo atingido.',
  sem_permissao: 'Seu perfil não pode abrir diligências neste contexto.',
  sem_unidade: 'Vincule uma unidade administrativa para usar diligência.',
  ordem_outra_unidade: 'A ordem de serviço não pertence à sua secretaria.'
}

export function labelStatusDiligencia(status) {
  return STATUS_DILIGENCIA[status] || status || '—'
}

export function textoMotivoBloqueioDiligencia(codigo) {
  if (!codigo) return ''
  return MOTIVO_BLOQUEIO_DILIGENCIA[codigo] || codigo
}

/** Normaliza anexo de diligência (API v4.14.2). */
export function mapAnexoDiligencia(api) {
  if (!api || typeof api !== 'object') return null
  const mime = api.mime_type || api.tipo || 'application/octet-stream'
  const nome = api.nome_arquivo || api.nome || ''
  return {
    id: String(api.id),
    url: api.url || '',
    tipo: mime,
    mime_type: mime,
    nome_arquivo: nome,
    nome,
    criado_em: api.criado_em || null
  }
}

export function mapDiligenciaFromApi(api) {
  if (!api || typeof api !== 'object') return null
  const brutos = Array.isArray(api.anexos) ? api.anexos : []
  const anexos = brutos.map(mapAnexoDiligencia).filter(Boolean)
  return {
    ...api,
    id: String(api.id),
    anexos_ids: Array.isArray(api.anexos_ids) ? api.anexos_ids.map(String) : [],
    anexos
  }
}

export function ehImagemAnexo(anexo) {
  const mime = (anexo?.mime_type || anexo?.tipo || '').toLowerCase()
  if (mime.startsWith('image/')) return true
  const nome = anexo?.nome_arquivo || anexo?.nome || anexo?.url || ''
  return /\.(jpe?g|png|gif|webp|heic|bmp)$/i.test(nome)
}

export function nomeAnexoExibicao(anexo, fallback = 'Anexo') {
  return (
    anexo?.nome_arquivo ||
    anexo?.nome ||
    (anexo?.url ? anexo.url.split('/').pop() : '') ||
    fallback
  )
}

export function formatarPrazoHumano(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return String(iso)
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/** Converte segundos acumulados de pausa SLA em texto legível. */
export function formatarTempoPausadoSla(segundos) {
  const s = Math.max(0, Number(segundos) || 0)
  if (s < 60) return 'menos de 1 minuto'
  const min = Math.floor(s / 60)
  if (min < 60) return `${min} minuto(s)`
  const horas = Math.floor(min / 60)
  const restMin = min % 60
  if (horas < 24) {
    return restMin ? `${horas}h ${restMin}min` : `${horas} hora(s)`
  }
  const dias = Math.floor(horas / 24)
  const restH = horas % 24
  return restH ? `${dias} dia(s) e ${restH}h` : `${dias} dia(s)`
}

export const OPCOES_EXPIRACAO_DILIGENCIA = [
  {
    value: 'devolver_fila',
    label: 'Devolver para a fila do setor responsável (mantém protocolo aberto)'
  },
  {
    value: 'encerrar_sem_resposta',
    label: 'Encerrar protocolo automaticamente por falta de complementação'
  }
]