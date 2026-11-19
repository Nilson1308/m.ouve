<template>
  <div ref="rootRef" class="relative z-[200]">
    <button
      type="button"
      @click.stop="toggleMenu"
      :class="buttonClass"
      :aria-label="`Tema atual: ${themeStore.getThemeLabel()}`"
      :aria-expanded="showMenu"
      aria-haspopup="listbox"
    >
      <component :is="currentIcon" :class="iconClass" aria-hidden="true" />
    </button>

    <transition name="dropdown">
      <div
        v-if="showMenu"
        role="listbox"
        :class="[
          'absolute right-0 mt-2 w-64 rounded-card py-2 z-[250]',
          'bg-white dark:bg-gray-800',
          'border border-gray-200 dark:border-gray-700',
          'shadow-float dark:shadow-float-dark',
          'high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300 high-contrast:shadow-none'
        ]"
        @click.stop
      >
        <p class="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 high-contrast:text-yellow-300">
          Aparência
        </p>
        <button
          v-for="theme in themes"
          :key="theme.value"
          type="button"
          role="option"
          :aria-selected="themeStore.currentTheme === theme.value"
          @click="selectTheme(theme.value)"
          :class="[
            'w-full px-4 py-3 text-left flex items-center gap-3 transition-colors',
            'hover:bg-gray-50 dark:hover:bg-gray-700/80',
            'high-contrast:hover:bg-yellow-300 high-contrast:hover:text-black',
            {
              'bg-primary-50 dark:bg-primary-900/30': themeStore.currentTheme === theme.value,
              'high-contrast:bg-yellow-300 high-contrast:text-black':
                themeStore.currentTheme === theme.value && themeStore.currentTheme === 'high-contrast'
            }
          ]"
        >
          <component
            :is="theme.icon"
            :class="[
              'w-5 h-5 shrink-0',
              themeStore.currentTheme === theme.value
                ? 'text-primary-600 dark:text-primary-400 high-contrast:text-black'
                : 'text-gray-600 dark:text-gray-400 high-contrast:text-yellow-300'
            ]"
          />
          <div class="flex-1 min-w-0">
            <div
              :class="[
                'font-medium text-gray-900 dark:text-gray-100',
                'high-contrast:text-white high-contrast:font-bold',
                {
                  'high-contrast:text-black':
                    themeStore.currentTheme === theme.value && themeStore.currentTheme === 'high-contrast'
                }
              ]"
            >
              {{ theme.label }}
            </div>
            <div
              :class="[
                'text-xs text-gray-500 dark:text-gray-400 truncate',
                'high-contrast:text-gray-300',
                {
                  'high-contrast:text-gray-800':
                    themeStore.currentTheme === theme.value && themeStore.currentTheme === 'high-contrast'
                }
              ]"
            >
              {{ theme.description }}
            </div>
          </div>
          <CheckIcon
            v-if="themeStore.currentTheme === theme.value"
            class="w-5 h-5 shrink-0 text-primary-600 dark:text-primary-400 high-contrast:text-black"
          />
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import {
  SunIcon,
  MoonIcon,
  EyeIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  /** Fundo claro (header interno) ou escuro (login) */
  surface: {
    type: String,
    default: 'light',
    validator: (v) => ['light', 'dark'].includes(v)
  }
})

const themeStore = useThemeStore()
const showMenu = ref(false)
const rootRef = ref(null)

const themes = [
  {
    value: 'light',
    label: 'Tema Claro',
    description: 'Padrão para uso diurno',
    icon: SunIcon
  },
  {
    value: 'dark',
    label: 'Tema Escuro',
    description: 'Reduz o brilho da tela',
    icon: MoonIcon
  },
  {
    value: 'high-contrast',
    label: 'Alto Contraste',
    description: 'Acessibilidade WCAG AAA',
    icon: EyeIcon
  }
]

const currentIcon = computed(() => {
  const theme = themes.find(t => t.value === themeStore.currentTheme)
  return theme ? theme.icon : SunIcon
})

const buttonClass = computed(() => {
  if (props.surface === 'dark') {
    return [
      'inline-flex items-center justify-center w-10 h-10 rounded-button',
      'bg-white/10 hover:bg-white/20 border border-white/30',
      'high-contrast:bg-black high-contrast:border-2 high-contrast:border-yellow-300',
      'high-contrast:hover:bg-yellow-300/20',
      'transition-colors focus:outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/50 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent motion-reduce:transition-none'
    ]
  }
  return 'btn-icon'
})

const iconClass = computed(() => {
  if (props.surface === 'dark') {
    return 'w-6 h-6 text-white high-contrast:text-yellow-300'
  }
  return 'w-5 h-5 text-gray-700 dark:text-gray-200 high-contrast:text-yellow-300'
})

function toggleMenu() {
  showMenu.value = !showMenu.value
}

function selectTheme(theme) {
  themeStore.setTheme(theme)
  showMenu.value = false
}

function handleClickOutside(event) {
  if (rootRef.value && !rootRef.value.contains(event.target) && showMenu.value) {
    showMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}
</style>
