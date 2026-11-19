import { notificacoesCidadaoAppService } from '@/services/api'
import { resolverVapidPublicKey, urlBase64ToUint8Array } from '@/utils/vapid'

export function pushSuportado() {
  return (
    typeof window !== 'undefined' &&
    'serviceWorker' in navigator &&
    'PushManager' in window &&
    'Notification' in window
  )
}

function subscriptionParaApi(subscription) {
  const json = subscription.toJSON()
  return {
    endpoint: json.endpoint,
    keys: {
      p256dh: json.keys?.p256dh,
      auth: json.keys?.auth
    }
  }
}

async function obterChaveVapid() {
  const envKey = resolverVapidPublicKey()
  if (envKey) return envKey
  const data = await notificacoesCidadaoAppService.obterVapidPublicKey()
  if (data?.configurado && data.vapid_public_key) {
    return data.vapid_public_key
  }
  throw new Error('Web Push não configurado no servidor.')
}

/**
 * Solicita permissão, inscreve no push e envia ao backend.
 */
export async function ativarWebPush() {
  if (!pushSuportado()) {
    throw new Error('Seu navegador não suporta notificações push.')
  }

  const permissao = await Notification.requestPermission()
  if (permissao !== 'granted') {
    throw new Error('Permissão de notificação negada ou não concedida.')
  }

  const vapidKey = await obterChaveVapid()
  const registration = await navigator.serviceWorker.ready
  let subscription = await registration.pushManager.getSubscription()

  const applicationServerKey = urlBase64ToUint8Array(vapidKey)

  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey
    })
  }

  const payload = subscriptionParaApi(subscription)
  await notificacoesCidadaoAppService.pushSubscribe(payload)
  return { ok: true, endpoint: payload.endpoint }
}

export async function pushJaInscrito() {
  if (!pushSuportado()) return false
  try {
    const registration = await navigator.serviceWorker.ready
    const sub = await registration.pushManager.getSubscription()
    return Boolean(sub)
  } catch {
    return false
  }
}