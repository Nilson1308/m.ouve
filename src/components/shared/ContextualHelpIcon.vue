<template>
  <span class="relative inline-flex items-center shrink-0 group/help">
    <button
      type="button"
      class="inline-flex items-center justify-center w-5 h-5 rounded-full text-gray-400 dark:text-gray-500 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700/80 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      :aria-label="labelAcessivel"
      @click.prevent.stop
    >
      <InformationCircleIcon class="w-4 h-4" aria-hidden="true" />
    </button>
    <span
      role="tooltip"
      class="pointer-events-none absolute left-1/2 -translate-x-1/2 bottom-full mb-2 z-50 w-[min(18rem,calc(100vw-2rem))] px-3 py-2 text-xs leading-snug text-left text-gray-100 bg-gray-900 dark:bg-gray-950 border border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover/help:opacity-100 group-hover/help:visible group-focus-within/help:opacity-100 group-focus-within/help:visible transition-opacity duration-150"
    >
      {{ texto }}
    </span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { InformationCircleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  texto: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  }
})

const labelAcessivel = computed(() => props.label || `Ajuda: ${props.texto}`)
</script>