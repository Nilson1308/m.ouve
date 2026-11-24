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
  limite_diligencias: 'Limite de diligências por protocolo atingido.'
}

export function labelStatusDiligencia(status) {
  return STATUS_DILIGENCIA[status] || status || '—'
}

export function textoMotivoBloqueioDiligencia(codigo) {
  if (!codigo) return ''
  return MOTIVO_BLOQUEIO_DILIGENCIA[codigo] || codigo
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