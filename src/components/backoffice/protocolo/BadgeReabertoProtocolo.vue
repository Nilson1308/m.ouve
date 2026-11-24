<template>
  <span
    v-if="qtd > 0 || reaberto"
    class="inline-flex items-center gap-1 badge badge-sm bg-orange-100 text-orange-900 dark:bg-orange-950/60 dark:text-orange-100 border border-orange-300/70 dark:border-orange-700/60 font-semibold"
    :title="`Protocolo reaberto pelo cidadão${qtd > 1 ? ` (${qtd}x)` : ''}`"
  >
    <ArrowUturnLeftIcon class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
  {{ qtd > 1 ? `Reaberto (${qtd}x)` : 'Reaberto' }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowUturnLeftIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  qtdReaberturas: { type: Number, default: 0 },
  reaberto: { type: Boolean, default: false }
})

const qtd = computed(() => Number(props.qtdReaberturas) || 0)
const reaberto = computed(() => Boolean(props.reaberto) || qtd.value > 0)
</script>