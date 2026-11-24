export function labelNivelAlertaSla(nivel) {
  const map = {
    preventivo_80: 'Preventivo',
    vencido: 'Vencido',
    escalonado_controladoria: 'Escalonado'
  }
  if (!nivel) return '—'
  return map[nivel] || nivel
}

export function classeNivelAlertaSla(nivel) {
  const map = {
    preventivo_80:
      'bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200 border-amber-200 dark:border-amber-700',
    vencido:
      'bg-orange-100 text-orange-900 dark:bg-orange-900/40 dark:text-orange-200 border-orange-200 dark:border-orange-700',
    escalonado_controladoria:
      'bg-red-100 text-red-900 dark:bg-red-900/40 dark:text-red-200 border-red-200 dark:border-red-700'
  }
  return (
    map[nivel] ||
    'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-600'
  )
}

export function labelTipoEnvioSla(tipo) {
  const map = {
    digest_unidade: 'Digest Unidade',
    digest_controladoria: 'Controladoria',
    disparo_manual: 'Manual'
  }
  return map[tipo] || tipo || '—'
}

export function labelStatusEnvioSla(status) {
  const map = {
    enviado: 'Enviado',
    erro: 'Erro',
    sem_pendencias: 'Sem pendências'
  }
  return map[status] || status || '—'
}