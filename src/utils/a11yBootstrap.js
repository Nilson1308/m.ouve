/** Escala de texto do PWA (eMAG) — aplicada antes do mount do Vue. */

export const TEXT_SCALE_STORAGE_KEY = 'ouvia_text_scale'
export const TEXT_SCALE_VALUES = ['normal', 'large', 'xlarge']

const SCALE_CLASSES = ['text-scale-normal', 'text-scale-large', 'text-scale-xlarge']

export function readSavedTextScale() {
  try {
    const saved = localStorage.getItem(TEXT_SCALE_STORAGE_KEY)
    return TEXT_SCALE_VALUES.includes(saved) ? saved : 'normal'
  } catch {
    return 'normal'
  }
}

export function applyTextScaleToDocument(scale) {
  const html = document.documentElement
  SCALE_CLASSES.forEach((c) => html.classList.remove(c))
  const key = TEXT_SCALE_VALUES.includes(scale) ? scale : 'normal'
  html.classList.add(`text-scale-${key}`)
}

export function bootstrapA11y() {
  applyTextScaleToDocument(readSavedTextScale())
}