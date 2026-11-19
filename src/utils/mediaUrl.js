/**
 * Normaliza URLs de mídia para HTTPS quando a página está em HTTPS
 * (corrige respostas antigas com http:// do backend atrás do proxy).
 */
export function ensureHttpsMediaUrl(url) {
  if (!url || typeof url !== 'string') return url

  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    if (url.startsWith('http://')) {
      try {
        const parsed = new URL(url)
        if (parsed.host === window.location.host) {
          return `https://${parsed.host}${parsed.pathname}${parsed.search}${parsed.hash}`
        }
      } catch {
        return url
      }
    }
  }

  return url
}

/** Resolve caminhos relativos (/media/...) e força HTTPS no mesmo host. */
export function resolveMediaUrl(url) {
  if (!url || typeof url !== 'string') return url || ''

  let resolved = url.trim()
  if (resolved.startsWith('/')) {
    let base = ''
    if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) {
      base = import.meta.env.VITE_API_BASE_URL.replace(/\/api\/v1\/?$/, '')
    } else if (typeof window !== 'undefined') {
      base = window.location.origin
    }
    resolved = base ? `${base}${resolved}` : resolved
  }

  return ensureHttpsMediaUrl(resolved)
}
