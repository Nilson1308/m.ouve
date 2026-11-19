import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  TEXT_SCALE_STORAGE_KEY,
  TEXT_SCALE_VALUES,
  applyTextScaleToDocument,
  readSavedTextScale
} from '@/utils/a11yBootstrap'
import { useThemeStore } from '@/stores/theme'

const THEME_BEFORE_HC_KEY = 'ouvia_theme_before_high_contrast'

export const useA11yStore = defineStore('a11y', () => {
  const textScale = ref(readSavedTextScale())
  const themeStore = useThemeStore()

  const highContrastOn = computed(() => themeStore.currentTheme === 'high-contrast')

  function setTextScale(scale) {
    if (!TEXT_SCALE_VALUES.includes(scale)) return
    textScale.value = scale
    localStorage.setItem(TEXT_SCALE_STORAGE_KEY, scale)
    applyTextScaleToDocument(scale)
  }

  function setHighContrast(enabled) {
    if (enabled) {
      const current = themeStore.currentTheme
      if (current !== 'high-contrast') {
        localStorage.setItem(THEME_BEFORE_HC_KEY, current)
      }
      themeStore.setTheme('high-contrast')
    } else {
      const restore =
        localStorage.getItem(THEME_BEFORE_HC_KEY) ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      const fallback = ['light', 'dark'].includes(restore) ? restore : 'light'
      themeStore.setTheme(fallback)
    }
  }

  function toggleHighContrast() {
    setHighContrast(!highContrastOn.value)
  }

  const textScaleLabel = computed(() => {
    const map = { normal: 'Normal', large: 'Grande', xlarge: 'Extra grande' }
    return map[textScale.value] || 'Normal'
  })

  return {
    textScale,
    highContrastOn,
    textScaleLabel,
    setTextScale,
    setHighContrast,
    toggleHighContrast
  }
})