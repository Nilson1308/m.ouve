/** Detecção leve de plataforma para UX do PWA (sem dependências). */

export function isIOS() {
  if (typeof navigator === 'undefined') return false
  const ua = navigator.userAgent || ''
  if (/iPad|iPhone|iPod/i.test(ua)) return true
  return navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1
}

/** PWA instalado (Tela de Início / display-mode standalone). */
export function isPwaStandalone() {
  if (typeof window === 'undefined') return false
  if (window.matchMedia?.('(display-mode: standalone)').matches) return true
  return Boolean(window.navigator.standalone)
}

/** Safari no iOS sem atalho na Tela de Início — Web Push não funciona até instalar. */
export function precisaInstrucaoIosAddToHome() {
  return isIOS() && !isPwaStandalone()
}