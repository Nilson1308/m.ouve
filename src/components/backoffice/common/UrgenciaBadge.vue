<template>
  <span
    class="inline-flex items-center gap-1 font-semibold rounded-badge border transition-colors"
    :class="[sizeClass, nivelClass, sugestaoIaPendente ? 'ring-2 ring-violet-400/60 dark:ring-violet-500/50' : '']"
    :title="tituloAcessivel"
  >
    <ArrowTrendingUpIcon v-if="nivel === 'alta'" class="shrink-0" :class="iconClass" aria-hidden="true" />
    <ExclamationTriangleIcon
      v-else-if="nivel === 'critica'"
      class="shrink-0"
      :class="iconClass"
      aria-hidden="true"
    />
    <span>{{ label }}</span>
    <span
      v-if="sugestaoIaPendente"
      class="ml-0.5 text-[10px] font-bold uppercase tracking-wide text-violet-700 dark:text-violet-200"
    >
      IA
    </span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowTrendingUpIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/solid'
import { labelUrgencia, normalizarUrgencia } from '@/utils/urgenciaHelpers'

const props = defineProps({
  nivel: { type: String, default: 'normal' },
  sugestaoIaPendente: { type: Boolean, default: false },
  size: { type: String, default: 'sm' }
})

const nivel = computed(() => normalizarUrgencia(props.nivel))

const label = computed(() => labelUrgencia(nivel.value))

const sizeClass = computed(() =>
  props.size === 'lg' ? 'text-sm px-3 py-1.5' : 'text-xs px-2 py-0.5'
)

const iconClass = computed(() => (props.size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'))

const nivelClass = computed(() => {
  const map = {
    baixa:
      'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-600',
    normal:
      'bg-sky-100 text-sky-800 border-sky-200 dark:bg-sky-950/50 dark:text-sky-200 dark:border-sky-800',
    alta:
      'bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950/50 dark:text-amber-100 dark:border-amber-700',
    critica:
      'bg-rose-100 text-rose-950 border-rose-300 dark:bg-rose-950/70 dark:text-rose-50 dark:border-rose-600 shadow-sm shadow-rose-500/10'
  }
  return map[nivel.value] || map.normal
})

const tituloAcessivel = computed(() => {
  let t = `Urgência ${label.value}`
  if (props.sugestaoIaPendente) t += ' — sugestão da IA pendente'
  return t
})
</script>