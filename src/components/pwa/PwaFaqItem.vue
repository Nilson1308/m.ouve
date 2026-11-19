<template>
  <div class="card p-0 overflow-hidden border border-gray-200/80 dark:border-gray-700">
    <h3 class="sr-only">{{ pergunta }}</h3>
    <button
      :id="buttonId"
      type="button"
      class="w-full flex items-center justify-between gap-3 px-4 py-4 min-h-[44px] text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 high-contrast:hover:bg-yellow-300/10 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary-500"
      :aria-expanded="aberto"
      :aria-controls="panelId"
      @click="toggle"
      @keydown="onKeydown"
    >
      <span class="text-sm font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300 pr-2">
        {{ pergunta }}
      </span>
      <ChevronDownIcon
        class="w-5 h-5 text-gray-400 shrink-0 transition-transform duration-200 motion-reduce:transition-none"
        :class="{ 'rotate-180': aberto }"
        aria-hidden="true"
      />
    </button>
    <Transition name="faq-expand">
      <div
        v-show="aberto"
        :id="panelId"
        role="region"
        :aria-labelledby="buttonId"
        class="px-4 pb-4 border-t border-gray-100 dark:border-gray-700"
      >
        <p class="text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white leading-relaxed pt-3">
          {{ resposta }}
        </p>
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  pergunta: { type: String, required: true },
  resposta: { type: String, required: true },
  idBase: { type: String, required: true },
  inicialAberto: { type: Boolean, default: false }
})

const aberto = ref(props.inicialAberto)
const buttonId = `faq-btn-${props.idBase}`
const panelId = `faq-panel-${props.idBase}`

function toggle() {
  aberto.value = !aberto.value
}

function onKeydown(event) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    toggle()
  }
}
</script>

<style scoped>
.faq-expand-enter-active,
.faq-expand-leave-active {
  transition: opacity 0.2s ease, max-height 0.25s ease;
  max-height: 480px;
  overflow: hidden;
}
.faq-expand-enter-from,
.faq-expand-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>