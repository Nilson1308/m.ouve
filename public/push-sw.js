/* eslint-disable no-restricted-globals */
/**
 * Listeners de Web Push (importados pelo Workbox / service worker gerado).
 */

function resolverUrlNotificacao(payload) {
  const data = payload && typeof payload === 'object' ? payload.data : null
  if (data && typeof data.url === 'string' && data.url.length > 0) {
    if (data.url.startsWith('http')) return data.url
    if (data.url.startsWith('/')) return `${self.location.origin}${data.url}`
    return `${self.location.origin}/${data.url}`
  }
  if (data && data.protocolo_codigo) {
    return `${self.location.origin}/app/protocolo/${encodeURIComponent(data.protocolo_codigo)}`
  }
  return `${self.location.origin}/app/dashboard`
}

self.addEventListener('push', (event) => {
  let payload = { title: 'M.Ouve', body: '' }
  try {
    if (event.data) {
      payload = event.data.json()
    }
  } catch {
  }

  const titulo = payload.title || (payload.data && payload.data.titulo) || 'M.Ouve'
  const corpo = payload.body || (payload.data && payload.data.mensagem) || ''
  const url = resolverUrlNotificacao(payload)
  const tag = (payload.data && payload.data.notificacao_id) || 'ouve-notificacao'

  event.waitUntil(
    self.registration.showNotification(titulo, {
      body: corpo,
      icon: '/pwa-192x192.png',
      badge: '/pwa-192x192.png',
      tag: String(tag),
      data: { url },
      renotify: true
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const destino = (event.notification.data && event.notification.data.url) || `${self.location.origin}/app/dashboard`

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (!client.url.startsWith(self.location.origin) || !('focus' in client)) {
          continue
        }
        if (typeof client.navigate === 'function') {
          return client.focus().then(() => client.navigate(destino))
        }
        return client.focus()
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(destino)
      }
      return undefined
    })
  )
})