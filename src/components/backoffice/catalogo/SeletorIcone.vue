<template>
  <div class="space-y-3">
    <div
      class="flex items-center gap-4 p-4 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/60"
    >
      <div
        class="flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center shadow-button transition-transform duration-300"
        :class="previewGradiente"
      >
        <component :is="previewComponente" class="w-8 h-8 text-white" aria-hidden="true" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          Prévia no PWA
        </p>
        <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
          {{ previewRotulo }}
        </p>
        <p v-if="modelValue" class="text-[11px] text-gray-500 dark:text-gray-400 font-mono mt-0.5 truncate">
          {{ modelValue }}
        </p>
        <p v-else class="text-xs text-amber-700 dark:text-amber-300 mt-1">
          Selecione um ícone na grade abaixo
        </p>
      </div>
    </div>

    <div
      class="grid grid-cols-4 sm:grid-cols-6 gap-2 max-h-[220px] overflow-y-auto p-1 rounded-lg border border-gray-100 dark:border-gray-700"
      role="listbox"
      aria-label="Ícones disponíveis"
    >
      <button
        v-for="item in ICONES_CATEGORIA_CATALOGO"
        :key="item.id"
        type="button"
        role="option"
        :aria-selected="item.id === valorInterno"
        :title="item.label"
        class="group relative flex flex-col items-center justify-center gap-1 p-2.5 rounded-xl border-2 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        :class="botaoClasse(item.id)"
        @click="selecionar(item.id)"
      >
        <span
          class="w-10 h-10 rounded-lg flex items-center justify-center transition-transform duration-200 group-hover:scale-105"
          :class="[`bg-gradient-to-br ${item.gradient}`, item.id === valorInterno ? 'ring-2 ring-white/90 ring-offset-2 ring-offset-primary-500' : '']"
        >
          <component :is="componentePorIdCatalogo(item.id)" class="w-5 h-5 text-white" />
        </span>
        <span class="text-[9px] leading-tight text-center text-gray-600 dark:text-gray-400 line-clamp-2 w-full">
          {{ item.label }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ICONES_CATEGORIA_CATALOGO,
  componenteIconeCategoria,
  componentePorIdCatalogo,
  classeGradienteIconeCategoria,
  rotuloIconeCategoria,
  normalizarIdIconeCategoria
} from '@/utils/catalogoIcones'

const props = defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const valorInterno = computed(() => normalizarIdIconeCategoria(props.modelValue))

const previewComponente = computed(() => componenteIconeCategoria(valorInterno.value || props.modelValue))
const previewGradiente = computed(() => classeGradienteIconeCategoria(valorInterno.value || props.modelValue))
const previewRotulo = computed(() => rotuloIconeCategoria(valorInterno.value || props.modelValue))

function botaoClasse(id) {
  const ativo = id === valorInterno.value
  return ativo
    ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/40 shadow-sm scale-[1.02]'
    : 'border-transparent bg-white dark:bg-gray-800 hover:border-primary-300 hover:bg-primary-50/50 dark:hover:bg-primary-950/20'
}

function selecionar(id) {
  emit('update:modelValue', id)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>