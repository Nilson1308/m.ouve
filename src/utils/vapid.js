/**
 * Converte chave VAPID (base64 URL-safe) para Uint8Array do Push API.
 */
export function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  const output = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i += 1) {
    output[i] = raw.charCodeAt(i)
  }
  return output
}

export function resolverVapidPublicKey() {
  const fromEnv = (import.meta.env.VITE_VAPID_PUBLIC_KEY || '').trim()
  return fromEnv || null
}