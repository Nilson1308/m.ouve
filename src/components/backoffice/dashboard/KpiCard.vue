<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow duration-200">
    <!-- Header com ícone -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center gap-3">
        <div 
          class="w-12 h-12 rounded-lg flex items-center justify-center"
          :class="iconBgClass"
        >
          <component :is="icon" class="w-6 h-6" :class="iconClass" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
            {{ titulo }}
          </p>
          <slot name="subtitulo">
            <p v-if="subtitulo" class="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
              {{ subtitulo }}
            </p>
          </slot>
        </div>
      </div>

      <!-- Trend indicator (opcional) -->
      <div 
        v-if="variacao !== null && variacao !== undefined"
        class="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold"
        :class="variacaoClass"
      >
        <component :is="variacaoIcon" class="w-3.5 h-3.5" />
        <span>{{ Math.abs(variacao) }}%</span>
      </div>
    </div>

    <!-- Valor principal -->
    <div class="mb-3">
      <p class="text-3xl font-bold text-gray-900 dark:text-white">
        <slot>{{ valor }}</slot>
      </p>
    </div>

    <!-- Contexto adicional -->
    <div v-if="contexto" class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
      <component v-if="contextoIcon" :is="contextoIcon" class="w-4 h-4" />
      <span>{{ contexto }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  MinusIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  titulo: {
    type: String,
    required: true
  },
  subtitulo: {
    type: String,
    default: null
  },
  valor: {
    type: [String, Number],
    default: null
  },
  icon: {
    type: Object,
    required: true
  },
  variacao: {
    type: Number,
    default: null // positivo = melhora, negativo = piora
  },
  variacaoInvertida: {
    type: Boolean,
    default: false // Se true, variação negativa é boa (ex: redução de TMA)
  },
  tipo: {
    type: String,
    default: 'neutral', // 'success', 'danger', 'warning', 'neutral', 'primary'
    validator: (v) => ['success', 'danger', 'warning', 'neutral', 'primary'].includes(v)
  },
  contexto: {
    type: String,
    default: null
  },
  contextoIcon: {
    type: Object,
    default: null
  }
})

// Classes do ícone principal baseadas no tipo
const iconBgClass = computed(() => {
  const classes = {
    success: 'bg-green-100 dark:bg-green-900/20',
    danger: 'bg-red-100 dark:bg-red-900/20',
    warning: 'bg-amber-100 dark:bg-amber-900/20',
    primary: 'bg-primary-100 dark:bg-primary-900/20',
    neutral: 'bg-gray-100 dark:bg-gray-700'
  }
  return classes[props.tipo]
})

const iconClass = computed(() => {
  const classes = {
    success: 'text-green-600 dark:text-green-400',
    danger: 'text-red-600 dark:text-red-400',
    warning: 'text-amber-600 dark:text-amber-400',
    primary: 'text-primary-600 dark:text-primary-400',
    neutral: 'text-gray-600 dark:text-gray-400'
  }
  return classes[props.tipo]
})

// Ícone e classes da variação
const ehMelhora = computed(() => {
  if (props.variacao === null || props.variacao === undefined) return null
  if (props.variacao === 0) return null
  
  const positivo = props.variacao > 0
  return props.variacaoInvertida ? !positivo : positivo
})

const variacaoIcon = computed(() => {
  if (ehMelhora.value === null) return MinusIcon
  return ehMelhora.value ? ArrowTrendingUpIcon : ArrowTrendingDownIcon
})

const variacaoClass = computed(() => {
  if (ehMelhora.value === null) {
    return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
  }
  return ehMelhora.value
    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
})
</script>
