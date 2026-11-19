<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <div class="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl">
                <ShieldCheckIcon class="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                  Triagem e Bloqueios
                </h1>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Atuações da Inteligência Artificial · Escudo Político
                </p>
              </div>
            </div>
            <p class="text-gray-600 dark:text-gray-400 ml-16">
              Atendimentos barrados automaticamente por quebra de regras de elegibilidade
            </p>
          </div>

          <!-- Botão de atualização -->
          <button
            @click="carregarDados"
            :disabled="carregando"
            class="btn-primary flex items-center gap-2"
            :class="{ 'opacity-50 cursor-not-allowed': carregando }"
          >
            <ArrowPathIcon 
              class="w-5 h-5" 
              :class="{ 'animate-spin': carregando }"
            />
            <span class="hidden sm:inline">Atualizar</span>
          </button>
        </div>

        <!-- Última atualização -->
        <p v-if="ultimaAtualizacao" class="text-xs text-gray-500 dark:text-gray-500 mt-3 ml-16 flex items-center gap-1.5">
          <ClockIcon class="w-4 h-4" />
          Última atualização: {{ formatarDataHora(ultimaAtualizacao) }}
        </p>
      </div>

      <!-- Filtros -->
      <div class="mb-8 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Data Inicial -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Inicial
            </label>
            <input
              v-model="filtros.dataInicial"
              type="date"
              class="input-primary w-full"
            />
          </div>

          <!-- Data Final -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Final
            </label>
            <input
              v-model="filtros.dataFinal"
              type="date"
              class="input-primary w-full"
            />
          </div>

          <!-- Unidade -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Secretaria
            </label>
            <select v-model="filtros.unidadeId" class="input-primary w-full">
              <option :value="null">Todas</option>
              <option v-for="unidade in unidadesAtivas" :key="unidade.id" :value="unidade.id">
                {{ unidade.sigla || unidade.nome }}
              </option>
            </select>
          </div>

          <!-- Botões -->
          <div class="flex items-end gap-2">
            <button
              @click="aplicarFiltros"
              :disabled="carregando"
              class="btn-primary flex-1"
            >
              Aplicar
            </button>
            <button
              @click="limparFiltros"
              :disabled="carregando"
              class="btn-secondary"
            >
              Limpar
            </button>
          </div>
        </div>
      </div>

      <!-- KPI Principal: Escudo Político -->
      <div class="mb-8">
        <template v-if="carregando">
          <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 animate-pulse">
            <div class="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </template>
        <template v-else-if="dados">
          <!-- Card de KPI Destaque -->
          <div class="relative overflow-hidden bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl shadow-lg p-1">
            <div class="bg-white dark:bg-gray-800 rounded-xl p-8">
              <div class="flex items-center justify-between">
                <!-- Ícone e Título -->
                <div class="flex items-start gap-6">
                  <div class="p-4 bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40 rounded-2xl">
                    <ShieldCheckIcon class="w-16 h-16 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <h2 class="text-lg font-semibold text-gray-600 dark:text-gray-400 mb-1 flex items-center gap-2">
                      <span>Atendimentos Barrados pela IA</span>
                      <ContextualHelpIcon
                        texto="Sessões de chat encerradas pela IA por inelegibilidade (fora do escopo ou regra do serviço) — reduz fila humana."
                        label="Ajuda: atendimentos barrados pela IA"
                      />
                    </h2>
                    <p class="text-6xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                      {{ formatarNumero(dados.total_sessoes_inelegiveis) }}
                    </p>
                    <p class="text-sm text-gray-500 dark:text-gray-500 mt-2 flex items-center gap-2">
                      <SparklesIcon class="w-4 h-4" />
                      <span class="font-semibold">Economia direta de triagem humana</span>
                    </p>
                  </div>
                </div>

                <!-- Badge de Impacto -->
                <div class="hidden lg:block text-right">
                  <div class="inline-flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-full border-2 border-green-500 dark:border-green-700">
                    <CheckCircleIcon class="w-5 h-5 text-green-600 dark:text-green-400" />
                    <span class="text-sm font-semibold text-green-700 dark:text-green-300">
                      ROI Positivo
                    </span>
                  </div>
                  <p class="text-xs text-gray-500 dark:text-gray-500 mt-2">
                    Tempo economizado pela IA
                  </p>
                </div>
              </div>

              <!-- Descrição do Impacto -->
              <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  <span class="font-semibold text-gray-900 dark:text-white">Escudo Político:</span>
                  A IA bloqueou automaticamente {{ formatarNumero(dados.total_sessoes_inelegiveis) }} tentativas de atendimento que não atendiam aos critérios de elegibilidade, economizando tempo de triagem manual e garantindo que apenas demandas válidas cheguem aos atendentes.
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Grid de Gráficos/Listas -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Ranking por Serviço -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
              <WrenchScrewdriverIcon class="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Gargalos por Serviço
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Serviços com mais bloqueios
              </p>
            </div>
          </div>

          <!-- Loading -->
          <template v-if="carregando">
            <div class="space-y-4">
              <div v-for="i in 5" :key="i" class="animate-pulse">
                <div class="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            </div>
          </template>

          <!-- Empty State -->
          <template v-else-if="!dados || !dados.ranking_por_servico.length">
            <div class="text-center py-12">
              <InformationCircleIcon class="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
              <p class="text-gray-600 dark:text-gray-400 text-sm">
                Nenhum bloqueio registrado neste período
              </p>
            </div>
          </template>

          <!-- Lista de Serviços -->
          <template v-else>
            <div class="space-y-3">
              <div
                v-for="(item, index) in dados.ranking_por_servico.slice(0, 10)"
                :key="item.servico_id"
                class="group"
              >
                <div class="flex items-center justify-between mb-1.5">
                  <div class="flex items-center gap-3 flex-1 min-w-0">
                    <!-- Posição -->
                    <div
                      class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg text-sm font-bold"
                      :class="
                        index === 0
                          ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
                          : index === 1
                            ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                            : index === 2
                              ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                      "
                    >
                      {{ index + 1 }}
                    </div>
                    <!-- Nome do Serviço -->
                    <span class="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {{ item.servico_nome }}
                    </span>
                  </div>
                  <!-- Total -->
                  <span class="text-sm font-bold text-gray-900 dark:text-white ml-3">
                    {{ formatarNumero(item.total) }}
                  </span>
                </div>
                <!-- Barra de Progresso -->
                <div class="relative h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    class="absolute inset-y-0 left-0 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-500"
                    :style="{ width: `${calcularPercentual(item.total, maxServico)}%` }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Mostrar mais (se houver) -->
            <div v-if="dados.ranking_por_servico.length > 10" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button class="text-sm text-primary-600 dark:text-primary-400 hover:underline">
                Ver todos os {{ dados.ranking_por_servico.length }} serviços →
              </button>
            </div>
          </template>
        </div>

        <!-- Ranking por Motivo -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <ExclamationTriangleIcon class="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Top Motivos de Bloqueio
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Principais regras violadas
              </p>
            </div>
          </div>

          <!-- Loading -->
          <template v-if="carregando">
            <div class="space-y-4">
              <div v-for="i in 5" :key="i" class="animate-pulse">
                <div class="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            </div>
          </template>

          <!-- Empty State -->
          <template v-else-if="!dados || !dados.ranking_por_motivo.length">
            <div class="text-center py-12">
              <InformationCircleIcon class="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
              <p class="text-gray-600 dark:text-gray-400 text-sm">
                Nenhum motivo de bloqueio registrado
              </p>
            </div>
          </template>

          <!-- Lista de Motivos -->
          <template v-else>
            <div class="space-y-4">
              <div
                v-for="(item, index) in dados.ranking_por_motivo.slice(0, 8)"
                :key="index"
                class="group"
              >
                <!-- Header com posição e total -->
                <div class="flex items-start justify-between mb-2">
                  <div class="flex items-start gap-3 flex-1 min-w-0">
                    <!-- Posição -->
                    <div
                      class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg text-sm font-bold mt-0.5"
                      :class="
                        index === 0
                          ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                          : index === 1
                            ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                      "
                    >
                      {{ index + 1 }}
                    </div>
                    <!-- Motivo -->
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 dark:text-white leading-snug">
                        {{ formatarMotivo(item.motivo) }}
                      </p>
                    </div>
                  </div>
                  <!-- Total -->
                  <span class="text-sm font-bold text-gray-900 dark:text-white ml-3 flex-shrink-0">
                    {{ formatarNumero(item.total) }}
                  </span>
                </div>
                <!-- Barra de Progresso -->
                <div class="relative h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden ml-10">
                  <div
                    class="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
                    :class="
                      index === 0
                        ? 'bg-gradient-to-r from-red-500 to-red-600'
                        : index === 1
                          ? 'bg-gradient-to-r from-orange-500 to-orange-600'
                          : 'bg-gradient-to-r from-gray-400 to-gray-500'
                    "
                    :style="{ width: `${calcularPercentual(item.total, maxMotivo)}%` }"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Mostrar mais (se houver) -->
            <div v-if="dados.ranking_por_motivo.length > 8" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button class="text-sm text-primary-600 dark:text-primary-400 hover:underline">
                Ver todos os {{ dados.ranking_por_motivo.length }} motivos →
              </button>
            </div>
          </template>
        </div>
      </div>

      <!-- Empty State Global -->
      <div
        v-if="!carregando && dados && dados.total_sessoes_inelegiveis === 0"
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center"
      >
        <div class="max-w-md mx-auto">
          <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
            <ShieldCheckIcon class="w-12 h-12 text-gray-400 dark:text-gray-500" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            A IA ainda não registrou bloqueios
          </h3>
          <p class="text-gray-600 dark:text-gray-400">
            Nenhum atendimento foi barrado por quebra de regras de elegibilidade neste período. Ajuste os filtros ou aguarde novas interações.
          </p>
        </div>
      </div>

      <!-- Alerta de erro -->
      <div
        v-if="!carregando && erro"
        class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6"
      >
        <div class="flex items-start gap-3">
          <ExclamationCircleIcon class="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 class="text-sm font-semibold text-red-900 dark:text-red-200 mb-1">
              Erro ao carregar dados
            </h3>
            <p class="text-sm text-red-700 dark:text-red-300">
              {{ erro }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useDashboardStore } from '@/stores/dashboard'
import { useAdminStore } from '@/stores/admin'
import {
  ShieldCheckIcon,
  ArrowPathIcon,
  ClockIcon,
  WrenchScrewdriverIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import ContextualHelpIcon from '@/components/shared/ContextualHelpIcon.vue'

const dashboardStore = useDashboardStore()
const adminStore = useAdminStore()

const { inelegibilidade: dados, loadingInelegibilidade: carregando, erro } = storeToRefs(dashboardStore)
const { unidadesAtivas } = storeToRefs(adminStore)

const filtros = ref({
  dataInicial: null,
  dataFinal: null,
  unidadeId: null,
  servicoId: null
})

const ultimaAtualizacao = ref(null)

// Computed
const maxServico = computed(() => {
  if (!dados.value?.ranking_por_servico?.length) return 0
  return Math.max(...dados.value.ranking_por_servico.map(s => s.total))
})

const maxMotivo = computed(() => {
  if (!dados.value?.ranking_por_motivo?.length) return 0
  return Math.max(...dados.value.ranking_por_motivo.map(m => m.total))
})

// Funções de formatação
function formatarNumero(valor) {
  if (valor == null) return '—'
  return new Intl.NumberFormat('pt-BR').format(valor)
}

function formatarDataHora(data) {
  if (!data) return ''
  try {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(data))
  } catch {
    return data
  }
}

function formatarMotivo(motivo) {
  if (!motivo) return 'Sem motivo especificado'
  // Formatar o motivo para ficar mais legível
  // Ex: "Qual a idade · regra interpretacao" → "Qual a idade · Regra de interpretação"
  return motivo
    .split('·')
    .map(part => part.trim())
    .map((part, index) => {
      if (index === 0) return part
      // Capitalizar primeira letra de cada palavra da regra
      return part.charAt(0).toUpperCase() + part.slice(1)
    })
    .join(' · ')
}

function calcularPercentual(valor, max) {
  if (!max || max === 0) return 0
  return Math.round((valor / max) * 100)
}

// Funções de ação
async function carregarDados() {
  try {
    await dashboardStore.carregarInelegibilidade(filtros.value)
    ultimaAtualizacao.value = new Date().toISOString()
  } catch (err) {
    console.error('Erro ao carregar dados de inelegibilidade:', err)
  }
}

async function aplicarFiltros() {
  await carregarDados()
}

function limparFiltros() {
  filtros.value = {
    dataInicial: null,
    dataFinal: null,
    unidadeId: null,
    servicoId: null
  }
  carregarDados()
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    adminStore.carregarUnidades({ silencioso: true }),
    carregarDados()
  ])
})
</script>

<style scoped>
.btn-primary {
  @apply px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors;
}

.input-primary {
  @apply px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500;
}
</style>
