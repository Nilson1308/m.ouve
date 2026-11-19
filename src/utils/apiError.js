/**
 * Código de erro do contrato da API (`error.code`).
 */
export function getApiErrorCode(error) {
  return error?.response?.data?.error?.code || null
}

/**
 * Detalhes extras (`error.details`), ex. `acao_sugerida`.
 */
export function getApiErrorDetails(error) {
  return error?.response?.data?.error?.details || null
}

/**
 * Extrai mensagem legível do formato de erro da API Django.
 */
export function getApiErrorMessage(error, fallback = 'Ocorreu um erro. Tente novamente.') {
  if (error?.code === 'ECONNABORTED') {
    return 'O envio demorou demais. Verifique sua conexão ou use uma foto menor.'
  }

  const status = error?.response?.status
  if (status === 413) {
    return 'Arquivo muito grande. Tente uma foto com resolução menor.'
  }

  const data = error?.response?.data
  if (!data) return error?.message || fallback

  if (data.error?.message) {
    const details = data.error.details
    if (details && typeof details === 'object') {
      const firstKey = Object.keys(details)[0]
      const firstMsg = details[firstKey]
      if (Array.isArray(firstMsg) && firstMsg[0]) {
        return firstMsg[0]
      }
    }
    return data.error.message
  }

  if (typeof data.detail === 'string') return data.detail

  if (typeof data === 'object' && data !== null) {
    for (const msgs of Object.values(data)) {
      if (Array.isArray(msgs) && msgs[0]) return String(msgs[0])
      if (typeof msgs === 'string' && msgs.trim()) return msgs
    }
  }

  return fallback
}
