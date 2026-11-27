<template>
  <button
    type="button"
    class="inline-flex items-center justify-center min-h-[44px] px-4 py-2 rounded-full text-sm font-medium border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-750 high-contrast:border-yellow-300 high-contrast:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:opacity-50"
    :disabled="desabilitado"
    @click="$emit('pular')"
  >
    Pular esta etapa
  </button>
</template>

<script setup>
defineProps({
  desabilitado: { type: Boolean, default: false }
})
defineEmits(['pular'])
</script>