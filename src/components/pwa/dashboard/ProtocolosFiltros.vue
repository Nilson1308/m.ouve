<template>
  <div class="space-y-4">
    <!-- Busca Inteligente -->
    <div class="relative">
      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
        Buscar Protocolo
      </label>
      <div class="relative">
        <input
          v-model="filtrosLocal.busca"
          type="text"
          placeholder="Código, descrição ou endereço..."
          class="input pl-10 pr-10"
          @input="emitirFiltros"
        />
        <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
        <button
          v-if="filtrosLocal.busca"
          @click="limparBusca"
          class="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <XMarkIcon class="w-4 h-4 text-gray-500" />
        </button>
      </div>
    </div>

    <!-- Grid de Filtros -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Status -->
      <div>
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
          Status
        </label>
        <select
          v-model="filtrosLocal.status"
          class="input"
          @change="emitirFiltros"
        >
          <option value="">Todos</option>
          <option value="ABERTO">Abertos</option>
          <option value="EM_ANDAMENTO">Em Andamento</option>
          <option value="RESOLVIDO">Resolvidos</option>
          <option value="FECHADO">Fechados</option>
        </select>
      </div>

      <!-- Categoria -->
      <div>
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
          Categoria
        </label>
        <select
          v-model="filtrosLocal.categoria"
          class="input"
          @change="emitirFiltros"
        >
          <option value="">Todas</option>
          <option value="Ouvidoria">Ouvidoria</option>
          <option value="Zeladoria Urbana">Zeladoria Urbana</option>
          <option value="Saúde">Saúde</option>
          <option value="Educação">Educação</option>
        </select>
      </div>
    </div>

    <!-- Período -->
    <div>
      <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
        Período
      </label>
      <div class="grid grid-cols-2 gap-2">
        <input
          v-model="filtrosLocal.dataInicio"
          type="date"
          class="input text-sm"
          @change="emitirFiltros"
        />
        <input
          v-model="filtrosLocal.dataFim"
          type="date"
          class="input text-sm"
          @change="emitirFiltros"
        />
      </div>
    </div>

    <!-- Chips de Filtros Ativos -->
    <div v-if="filtrosAtivos.length > 0" class="flex flex-wrap gap-2">
      <button
        v-for="chip in filtrosAtivos"
        :key="chip.key"
        @click="removerFiltro(chip.key)"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-100 dark:bg-primary-900/30 high-contrast:bg-transparent border border-primary-300 dark:border-primary-700 high-contrast:border-yellow-300 rounded-full text-xs font-semibold text-primary-700 dark:text-primary-300 high-contrast:text-yellow-300 hover:bg-primary-200 dark:hover:bg-primary-800/40 transition-colors"
      >
        {{ chip.label }}
        <XMarkIcon class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Ações -->
    <div class="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300">
      <button
        v-if="temFiltrosAtivos"
        @click="limparTodosFiltros"
        class="text-sm font-semibold text-gray-600 dark:text-gray-400 high-contrast:text-white hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
      >
        Limpar tudo
      </button>
      <div class="ml-auto text-xs text-gray-500 dark:text-gray-500 high-contrast:text-white high-contrast:font-bold">
        {{ totalResultados }} {{ totalResultados === 1 ? 'protocolo' : 'protocolos' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      busca: '',
      status: '',
      categoria: '',
      dataInicio: '',
      dataFim: ''
    })
  },
  totalResultados: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue', 'aplicar'])

const filtrosLocal = ref({ ...props.modelValue })

// Sincroniza com v-model do pai
watch(() => props.modelValue, (newVal) => {
  filtrosLocal.value = { ...newVal }
}, { deep: true })

// Chips de filtros ativos
const filtrosAtivos = computed(() => {
  const chips = []
  
  if (filtrosLocal.value.status) {
    chips.push({
      key: 'status',
      label: `Status: ${getLabelStatus(filtrosLocal.value.status)}`
    })
  }
  
  if (filtrosLocal.value.categoria) {
    chips.push({
      key: 'categoria',
      label: `Categoria: ${filtrosLocal.value.categoria}`
    })
  }
  
  if (filtrosLocal.value.dataInicio) {
    chips.push({
      key: 'dataInicio',
      label: `De: ${formatarData(filtrosLocal.value.dataInicio)}`
    })
  }
  
  if (filtrosLocal.value.dataFim) {
    chips.push({
      key: 'dataFim',
      label: `Até: ${formatarData(filtrosLocal.value.dataFim)}`
    })
  }
  
  return chips
})

const temFiltrosAtivos = computed(() => {
  return filtrosLocal.value.busca ||
         filtrosLocal.value.status ||
         filtrosLocal.value.categoria ||
         filtrosLocal.value.dataInicio ||
         filtrosLocal.value.dataFim
})

function emitirFiltros() {
  emit('update:modelValue', { ...filtrosLocal.value })
  emit('aplicar', { ...filtrosLocal.value })
}

function limparBusca() {
  filtrosLocal.value.busca = ''
  emitirFiltros()
}

function removerFiltro(key) {
  filtrosLocal.value[key] = ''
  emitirFiltros()
}

function limparTodosFiltros() {
  filtrosLocal.value = {
    busca: '',
    status: '',
    categoria: '',
    dataInicio: '',
    dataFim: ''
  }
  emitirFiltros()
}

function getLabelStatus(status) {
  const labels = {
    'ABERTO': 'Aberto',
    'EM_ANDAMENTO': 'Em Andamento',
    'RESOLVIDO': 'Resolvido',
    'FECHADO': 'Fechado'
  }
  return labels[status] || status
}

function formatarData(dataStr) {
  if (!dataStr) return ''
  const [ano, mes, dia] = dataStr.split('-')
  return `${dia}/${mes}/${ano}`
}
</script>
