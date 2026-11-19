import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  THEME_STORAGE_KEY,
  THEME_VALUES,
  applyThemeToDocument,
  readSavedTheme
} from '@/utils/themeBootstrap'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(readSavedTheme())

  function applyTheme(theme) {
    if (!THEME_VALUES.includes(theme)) return
    applyThemeToDocument(theme)
    localStorage.setItem(THEME_STORAGE_KEY, theme)
    currentTheme.value = theme
  }

  // Alternar para o próximo tema
  function toggleTheme() {
    const currentIndex = THEME_VALUES.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % THEME_VALUES.length
    applyTheme(THEME_VALUES[nextIndex])
  }

  function setTheme(theme) {
    applyTheme(theme)
  }

  // Obter label do tema atual
  function getThemeLabel() {
    const labels = {
      'light': 'Claro',
      'dark': 'Escuro',
      'high-contrast': 'Alto Contraste'
    }
    return labels[currentTheme.value] || 'Claro'
  }

  // Obter ícone do tema atual
  function getThemeIcon() {
    const icons = {
      'light': 'sun',
      'dark': 'moon',
      'high-contrast': 'eye'
    }
    return icons[currentTheme.value] || 'sun'
  }

  return {
    currentTheme,
    applyTheme,
    toggleTheme,
    setTheme,
    getThemeLabel,
    getThemeIcon
  }
})
