<template>
  <div
    v-if="totalSugestoes > 0"
    class="relative overflow-hidden rounded-xl border-2 border-primary-300/50 dark:border-primary-600/40 shadow-sm"
  >
    <div
      class="absolute inset-0 bg-gradient-to-r from-primary-500/8 via-purple-500/10 to-pink-500/8 dark:from-primary-500/15 dark:via-purple-500/10"
      aria-hidden="true"
    />
    <div class="relative flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-start gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 text-white shadow-md"
        >
          <SparklesIcon class="h-5 w-5" />
        </div>
        <div>
          <p class="text-sm font-bold text-gray-900 dark:text-white">
            IA identificou {{ totalSugestoes }}
            {{ totalSugestoes === 1 ? 'agrupamento' : 'agrupamentos' }}
            · {{ totalProtocolos }} protocolo(s)
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
            Cards com ✨ estão nas sugestões. Use o mapa para aprovar ou anexar em lote.
          </p>
        </div>
      </div>
      <button
        type="button"
        class="shrink-0 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold text-white bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 shadow-md"
        @click="$emit('abrir-mapa-ia')"
      >
        <MapIcon class="h-4 w-4" />
        Abrir Mapa &amp; IA
      </button>
    </div>
  </div>
</template>

<script setup>
import { SparklesIcon, MapIcon } from '@heroicons/vue/24/outline'

defineProps({
  totalSugestoes: { type: Number, default: 0 },
  totalProtocolos: { type: Number, default: 0 }
})

defineEmits(['abrir-mapa-ia'])
</script>