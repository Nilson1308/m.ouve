export const THEME_STORAGE_KEY = 'ouvia_theme'
export const THEME_VALUES = ['light', 'dark', 'high-contrast']

export function readSavedTheme() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY)
    return THEME_VALUES.includes(saved) ? saved : 'light'
  } catch {
    return 'light'
  }
}

export function applyThemeToDocument(theme) {
  const html = document.documentElement
  for (const t of THEME_VALUES) {
    html.classList.remove(t)
  }
  if (THEME_VALUES.includes(theme)) {
    html.classList.add(theme)
  }
}

/** Chamada síncrona antes do mount do Vue — evita flash de tema claro no refresh. */
export function bootstrapTheme() {
  applyThemeToDocument(readSavedTheme())
}
