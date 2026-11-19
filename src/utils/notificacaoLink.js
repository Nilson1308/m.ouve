/** Resolve link_acao da API para rota interna do SPA. */
export function rotaInternaNotificacao(link) {
  if (!link) return null
  try {
    const base = typeof window !== 'undefined' ? window.location.origin : ''
    const url = link.startsWith('http') ? new URL(link) : new URL(link, base)
    if (typeof window !== 'undefined' && url.origin === window.location.origin) {
      return url.pathname + url.search + url.hash
    }
  } catch {
  }
  if (link.startsWith('/')) return link
  return null
}

export function formatarQuandoNotificacao(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  const diff = Date.now() - d.getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return 'Agora'
  if (min < 60) return `Há ${min} min`
  const h = Math.floor(min / 60)
  if (h < 24) return `Há ${h}h`
  const dias = Math.floor(h / 24)
  if (dias < 7) return `Há ${dias}d`
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
