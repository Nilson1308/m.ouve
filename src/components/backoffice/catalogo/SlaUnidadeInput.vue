<template>
  <div>
    <label v-if="label" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
      {{ label }}
    </label>
  <div class="flex flex-col sm:flex-row gap-2 sm:items-stretch">
    <input
      v-model.number="valorLocal"
      type="number"
      class="input flex-1 min-w-0"
      :min="limites.min"
      :max="limites.max"
      :step="limites.step"
      :disabled="disabled"
      @keydown.enter.prevent
    />
    <select
      v-model="unidade"
      class="input w-full sm:w-36 shrink-0"
      :disabled="disabled"
      aria-label="Unidade do SLA"
    >
      <option value="horas">Horas</option>
      <option value="dias">Dias</option>
    </select>
  </div>
    <p v-if="textoAuxiliar" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
      {{ textoAuxiliar }}
    </p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import {
  formatarSlaDuracao,
  horasParaExibicao,
  limitesSla,
  valorUnidadeParaHoras
} from '@/utils/slaUnidade'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 72
  },
  label: {
    type: String,
    default: 'SLA *'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const unidade = ref('horas')
const valorLocal = ref(72)
let sincronizando = false

const limites = computed(() => limitesSla(unidade.value))

const horasAtuais = computed(() => valorUnidadeParaHoras(valorLocal.value, unidade.value))

const textoAuxiliar = computed(() => {
  const h = horasAtuais.value
  if (h <= 0) return ''
  if (unidade.value === 'dias') {
    return `Equivale a ${h} hora${h > 1 ? 's' : ''} — ${formatarSlaDuracao(h)}`
  }
  return formatarSlaDuracao(h)
})

function aplicarHoras(horas) {
  sincronizando = true
  const exib = horasParaExibicao(horas)
  unidade.value = exib.unidade
  valorLocal.value = exib.valor
  sincronizando = false
}

watch(
  () => props.modelValue,
  (h) => {
    const convertido = valorUnidadeParaHoras(valorLocal.value, unidade.value)
    if (convertido === h) return
    aplicarHoras(h)
  },
  { immediate: true }
)

watch([unidade, valorLocal], () => {
  if (sincronizando) return
  const h = horasAtuais.value
  if (h < 1) return
  if (h !== props.modelValue) {
    emit('update:modelValue', h)
  }
})

watch(unidade, (nova, antiga) => {
  if (sincronizando || nova === antiga) return
  sincronizando = true
  const h = Number(props.modelValue) || horasAtuais.value
  if (nova === 'dias') {
    valorLocal.value = Math.round((h / 24) * 100) / 100
  } else {
    valorLocal.value = Math.round(h) || 24
  }
  sincronizando = false
})
</script>