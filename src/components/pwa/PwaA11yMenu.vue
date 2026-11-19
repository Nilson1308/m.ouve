<template>
  <div ref="rootRef" class="relative z-[200]">
    <button
      ref="triggerRef"
      type="button"
      class="btn-icon min-w-[44px] min-h-[44px]"
      :aria-label="menuAberto ? 'Fechar opções de acessibilidade' : 'Abrir opções de acessibilidade'"
      :aria-expanded="menuAberto"
      aria-haspopup="dialog"
      @click.stop="alternarMenu"
    >
      <AdjustmentsHorizontalIcon class="w-5 h-5" aria-hidden="true" />
    </button>

    <Teleport to="body">
      <transition name="dropdown">
        <div
          v-if="menuAberto"
          class="fixed inset-0 z-[480] bg-black/30 dark:bg-black/50 high-contrast:bg-black/70 motion-reduce:transition-none"
          aria-hidden="true"
          @click="fecharMenu"
        />
      </transition>
      <transition name="dropdown">
        <div
          v-if="menuAberto"
          ref="panelRef"
          class="fixed z-[500] left-3 right-3 sm:left-auto sm:right-4 sm:w-72 max-w-[calc(100vw-1.5rem)] rounded-card py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-float dark:shadow-float-dark high-contrast:bg-black high-contrast:border-yellow-300 safe-area-inset motion-reduce:transition-none"
          :style="estiloPainel"
          role="dialog"
          aria-modal="true"
          aria-label="Configurações de acessibilidade"
          @click.stop
        >
          <p class="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 high-contrast:text-yellow-300">
            Acessibilidade (eMAG)
          </p>

          <fieldset class="px-2 pb-2 border-0 m-0">
            <legend class="px-2 text-sm font-semibold text-gray-800 dark:text-gray-200 high-contrast:text-white">
              Tamanho do texto
            </legend>
            <div class="flex flex-col gap-1 mt-1 px-2" role="radiogroup" aria-label="Tamanho do texto">
              <button
                v-for="opt in escalas"
                :key="opt.value"
                type="button"
                role="radio"
                :aria-checked="a11yStore.textScale === opt.value"
                class="w-full px-4 py-2.5 min-h-[44px] text-left rounded-button text-sm transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/80 high-contrast:hover:bg-yellow-300/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 motion-reduce:transition-none"
                :class="
                  a11yStore.textScale === opt.value
                    ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200 font-semibold'
                    : 'text-gray-700 dark:text-gray-300'
                "
                @click="selecionarEscala(opt.value)"
              >
                {{ opt.label }}
              </button>
            </div>
          </fieldset>

          <div class="border-t border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300/50 mx-3 my-2" />

          <div class="px-2 pb-1">
            <button
              type="button"
              class="w-full px-4 py-2.5 min-h-[44px] text-left rounded-button text-sm flex items-center justify-between gap-2 hover:bg-gray-50 dark:hover:bg-gray-700/80 high-contrast:hover:bg-yellow-300/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 motion-reduce:transition-none"
              :aria-pressed="a11yStore.highContrastOn"
              @click="a11yStore.toggleHighContrast()"
            >
              <span class="font-medium text-gray-900 dark:text-white high-contrast:text-yellow-300">
                Alto contraste
              </span>
              <span
                class="text-xs px-2 py-0.5 rounded-badge shrink-0"
                :class="
                  a11yStore.highContrastOn
                    ? 'bg-yellow-300 text-black font-bold'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                "
              >
                {{ a11yStore.highContrastOn ? 'Ativo' : 'Off' }}
              </span>
            </button>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { AdjustmentsHorizontalIcon } from '@heroicons/vue/24/outline'
import { useA11yStore } from '@/stores/a11y'

const a11yStore = useA11yStore()
const menuAberto = ref(false)
const rootRef = ref(null)
const triggerRef = ref(null)
const panelRef = ref(null)
const estiloPainel = ref({ top: '4.5rem' })

const escalas = [
  { value: 'normal', label: 'Normal' },
  { value: 'large', label: 'Grande' },
  { value: 'xlarge', label: 'Extra grande' }
]

function atualizarPosicaoPainel() {
  const el = triggerRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const gap = 8
  const top = Math.round(rect.bottom + gap)
  estiloPainel.value = { top: `${top}px` }
}

function alternarMenu() {
  const abrir = !menuAberto.value
  menuAberto.value = abrir
  if (abrir) {
    nextTick(() => {
      atualizarPosicaoPainel()
    })
  }
}

function fecharMenu() {
  menuAberto.value = false
  nextTick(() => triggerRef.value?.focus())
}

function selecionarEscala(value) {
  a11yStore.setTextScale(value)
}

function handleClickOutside(event) {
  if (!menuAberto.value) return
  if (rootRef.value?.contains(event.target)) return
  if (panelRef.value?.contains(event.target)) return
  fecharMenu()
}

function onEscape(event) {
  if (event.key === 'Escape' && menuAberto.value) {
    event.preventDefault()
    fecharMenu()
  }
}

function onResize() {
  if (menuAberto.value) atualizarPosicaoPainel()
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', onEscape)
  window.addEventListener('resize', onResize)
  window.addEventListener('scroll', onResize, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', onEscape)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('scroll', onResize, true)
})
</script>