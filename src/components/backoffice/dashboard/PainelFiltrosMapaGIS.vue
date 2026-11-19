<template>
  <div
    class="painel-filtros flex flex-col max-h-[min(85vh,calc(100vh-6rem))] overflow-hidden bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 rounded-xl shadow-2xl"
    :class="{ 'animate-pulse-slow': loading }"
  >
    <!-- Header (fixo) -->
    <div class="flex-shrink-0 flex items-center justify-between px-5 pt-5 pb-3 border-b border-gray-200/60 dark:border-gray-700/60">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center flex-shrink-0">
          <AdjustmentsHorizontalIcon class="w-5 h-5 text-white" />
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-bold text-gray-900 dark:text-white truncate">
            Filtros Estratégicos
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
            Refine a visualização territorial
          </p>
        </div>
      </div>

      <button
        v-if="minimizavel"
        @click="$emit('toggle-minimizado')"
        class="lg:hidden btn-icon flex-shrink-0"
      >
        <component :is="minimizado ? ChevronDownIcon : ChevronUpIcon" class="w-5 h-5" />
      </button>
    </div>

    <!-- Corpo rolável -->
    <div
      v-show="!minimizado"
      class="filtros-scroll flex-1 min-h-0 overflow-y-auto overscroll-contain px-5 py-4 space-y-4"
    >
      <!-- Período — grid compacto -->
      <section>
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Período</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <label class="block">
            <span class="text-[11px] text-gray-500 dark:text-gray-400">Data inicial</span>
            <input
              v-model="filtrosLocais.dataInicial"
              type="date"
              class="mt-0.5 w-full px-2.5 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm"
              :disabled="loading"
            />
          </label>
          <label class="block">
            <span class="text-[11px] text-gray-500 dark:text-gray-400">Data final</span>
            <input
              v-model="filtrosLocais.dataFinal"
              type="date"
              class="mt-0.5 w-full px-2.5 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm"
              :disabled="loading"
            />
          </label>
        </div>
      </section>

      <!-- Bairro -->
      <section>
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Bairro</p>
        <div class="space-y-2">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              v-model="buscaBairro"
              type="search"
              autocomplete="off"
              placeholder="Buscar bairro..."
              class="w-full pl-8 pr-2.5 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white/90 dark:bg-gray-900/90 text-sm"
              :disabled="loading || loadingBairros"
            />
          </div>
          <select
            v-model="filtrosLocais.bairro"
            class="w-full px-2.5 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm"
            :disabled="loading || loadingBairros"
          >
            <option :value="null">Todos os Bairros</option>
            <option v-for="nome in bairrosFiltrados" :key="nome" :value="nome">
              {{ nome }}
            </option>
          </select>
          <p v-if="loadingBairros" class="text-[11px] text-gray-500 animate-pulse">Carregando bairros...</p>
          <p
            v-else-if="!listaBairros.length"
            class="text-[11px] text-gray-500 dark:text-gray-400"
          >
            Nenhum bairro identificado nos protocolos com geo. Confira o endereço ou o JSON do protocolo.
          </p>
        </div>
      </section>

      <!-- Status compacto -->
      <section>
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Status</p>
        <div class="space-y-1">
          <label
            v-for="opcao in opcoesStatus"
            :key="opcao.value"
            class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/40 cursor-pointer text-sm"
            :class="{ 'bg-primary-50 dark:bg-primary-900/20': filtrosLocais.status.includes(opcao.value) }"
          >
            <input
              type="checkbox"
              :value="opcao.value"
              v-model="filtrosLocais.status"
              class="w-3.5 h-3.5 rounded border-gray-300"
              :disabled="loading"
            />
            <span class="flex-1 text-gray-900 dark:text-white">{{ opcao.label }}</span>
            <span class="w-2 h-2 rounded-full flex-shrink-0" :class="opcao.corClasse" />
          </label>
        </div>
      </section>

      <section v-if="exibirFiltroServico">
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">Serviço</p>
        <select
          v-model="filtrosLocais.servico"
          class="w-full px-2.5 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm"
          :disabled="loading"
        >
          <option :value="null">Todos os serviços</option>
          <option v-for="servico in servicosDisponiveis" :key="servico.id" :value="servico.id">
            {{ servico.nome }}
          </option>
        </select>
      </section>

      <div
        v-if="totalFiltrosAtivos > 0"
        class="bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20 border border-primary-200/80 dark:border-primary-800 rounded-lg p-2.5"
      >
        <p class="text-[11px] font-semibold text-primary-700 dark:text-primary-400 mb-1">
          {{ totalFiltrosAtivos }} filtro(s) ativo(s)
        </p>
        <div class="flex flex-wrap gap-1 text-[11px] text-gray-600 dark:text-gray-300">
          <span v-if="filtrosLocais.bairro">📍 {{ filtrosLocais.bairro }}</span>
          <span v-if="filtrosLocais.status.length">{{ filtrosLocais.status.length }} status</span>
        </div>
      </div>
    </div>

    <!-- Ações fixas no rodapé -->
    <div
      v-show="!minimizado"
      class="flex-shrink-0 flex gap-2 px-5 py-4 border-t border-gray-200/60 dark:border-gray-700/60 bg-white/90 dark:bg-gray-800/90"
    >
      <button
        type="button"
        @click="aplicarFiltros"
        :disabled="loading"
        class="flex-1 btn-primary flex items-center justify-center gap-2 py-2 text-sm"
      >
        <MagnifyingGlassIcon class="w-4 h-4" />
        {{ loading ? 'Aplicando...' : 'Aplicar' }}
      </button>
      <button
        type="button"
        @click="$emit('atualizar')"
        :disabled="loading"
        class="btn-secondary p-2.5 flex-shrink-0"
        title="Atualizar mapa com os filtros atuais"
        aria-label="Atualizar mapa"
      >
        <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': loading }" />
      </button>
      <button
        v-if="totalFiltrosAtivos > 0"
        type="button"
        @click="limparFiltros"
        :disabled="loading"
        class="btn-secondary p-2"
        title="Limpar filtros"
        aria-label="Limpar filtros"
      >
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import {
  AdjustmentsHorizontalIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  filtros: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  minimizavel: { type: Boolean, default: true },
  minimizado: { type: Boolean, default: false },
  exibirFiltroServico: { type: Boolean, default: false },
  servicosDisponiveis: { type: Array, default: () => [] },
  bairrosDisponiveis: { type: Array, default: () => [] },
  loadingBairros: { type: Boolean, default: false }
})

const emit = defineEmits(['aplicar', 'limpar', 'atualizar', 'toggle-minimizado'])

const dashboardStore = useDashboardStore()
const buscaBairro = ref('')

const filtrosLocais = ref({
  dataInicial: props.filtros.dataInicial || null,
  dataFinal: props.filtros.dataFinal || null,
  status: props.filtros.status || [],
  servico: props.filtros.servico || null,
  bairro: props.filtros.bairro || null
})

const listaBairros = computed(() => {
  if (props.bairrosDisponiveis?.length) return props.bairrosDisponiveis
  return dashboardStore.bairrosDisponiveis
})

const bairrosFiltrados = computed(() => {
  const termo = buscaBairro.value.trim().toLowerCase()
  if (!termo) return listaBairros.value
  return listaBairros.value.filter((nome) => String(nome).toLowerCase().includes(termo))
})

onMounted(() => {
  void dashboardStore.carregarBairrosDashboard()
})

const opcoesStatus = [
  { value: 'em_analise', label: 'Em análise', corClasse: 'bg-blue-500' },
  { value: 'em_andamento', label: 'Em andamento', corClasse: 'bg-yellow-500' },
  { value: 'aguardando_revisao', label: 'Aguardando validação', corClasse: 'bg-purple-500' },
  { value: 'resolvido', label: 'Resolvido', corClasse: 'bg-green-500' },
  { value: 'rejeitado', label: 'Rejeitado', corClasse: 'bg-gray-500' }
]

const totalFiltrosAtivos = computed(() => {
  let count = 0
  if (filtrosLocais.value.dataInicial) count++
  if (filtrosLocais.value.dataFinal) count++
  if (filtrosLocais.value.status.length > 0) count++
  if (filtrosLocais.value.servico) count++
  if (filtrosLocais.value.bairro) count++
  return count
})

function aplicarFiltros() {
  emit('aplicar', { ...filtrosLocais.value })
}

function limparFiltros() {
  filtrosLocais.value = {
    dataInicial: null,
    dataFinal: null,
    status: [],
    servico: null,
    bairro: null
  }
  buscaBairro.value = ''
  emit('limpar')
}

watch(
  () => props.filtros,
  (novosFiltros) => {
    filtrosLocais.value = {
      dataInicial: novosFiltros.dataInicial || null,
      dataFinal: novosFiltros.dataFinal || null,
      status: novosFiltros.status || [],
      servico: novosFiltros.servico || null,
      bairro: novosFiltros.bairro || null
    }
  },
  { deep: true }
)
</script>

<style scoped>
.painel-filtros {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.filtros-scroll {
  scrollbar-gutter: stable;
}

.filtros-scroll::-webkit-scrollbar {
  width: 6px;
}

.filtros-scroll::-webkit-scrollbar-thumb {
  background: rgb(156 163 175 / 0.5);
  border-radius: 999px;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.88; }
}

.animate-pulse-slow {
  animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>