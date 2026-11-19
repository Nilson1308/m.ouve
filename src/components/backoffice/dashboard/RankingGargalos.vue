<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <ExclamationTriangleIcon class="w-5 h-5 text-amber-500" />
            Gargalos por Secretaria
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Unidades com maior volume de SLA vencido
          </p>
        </div>
        <div class="text-right">
          <p class="text-xs text-gray-500 dark:text-gray-500">Ordenado por criticidade</p>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="p-6 space-y-4">
      <div v-for="i in 5" :key="i" class="animate-pulse">
        <div class="flex items-center justify-between mb-2">
          <div class="h-4 w-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
          <div class="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
        <div class="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </div>

    <!-- Lista de secretarias -->
    <div v-else-if="unidades.length > 0" class="divide-y divide-gray-200 dark:divide-gray-700">
      <div 
        v-for="(unidade, index) in unidades" 
        :key="unidade.id"
        class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <!-- Cabeçalho da unidade -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-start gap-3 flex-1">
            <!-- Ranking badge -->
            <div 
              class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm"
              :class="getRankingBadgeClass(index)"
            >
              {{ index + 1 }}
            </div>

            <!-- Nome e sigla -->
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-gray-900 dark:text-white text-sm">
                {{ unidade.nome }}
              </h4>
              <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                {{ unidade.sigla }}
              </p>
            </div>
          </div>

          <!-- TMA da unidade -->
          <div class="text-right flex-shrink-0 ml-4">
            <p class="text-xs text-gray-500 dark:text-gray-500">TMA</p>
            <p class="text-lg font-bold text-gray-900 dark:text-white">
              {{ formatarTMA(unidade.tma_horas) }}
            </p>
          </div>
        </div>

        <!-- Barra de progresso dupla -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center gap-4">
              <span class="flex items-center gap-1 text-green-600 dark:text-green-400">
                <span class="w-2 h-2 rounded-full bg-green-500"></span>
                No prazo: <strong>{{ unidade.no_prazo }}</strong>
              </span>
              <span class="flex items-center gap-1 text-red-600 dark:text-red-400">
                <span class="w-2 h-2 rounded-full bg-red-500"></span>
                Vencido: <strong>{{ unidade.vencido }}</strong>
              </span>
            </div>
            <span class="text-gray-600 dark:text-gray-400">
              Total: {{ unidade.total }}
            </span>
          </div>

          <!-- Progress bar -->
          <div class="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden flex">
            <!-- Parte verde (no prazo) -->
            <div 
              class="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
              :style="{ width: `${calcularPercentual(unidade.no_prazo, unidade.total)}%` }"
            ></div>
            <!-- Parte vermelha (vencido) -->
            <div 
              class="h-full bg-gradient-to-r from-red-500 to-red-600 transition-all duration-500"
              :style="{ width: `${calcularPercentual(unidade.vencido, unidade.total)}%` }"
            ></div>
          </div>

          <!-- Percentuais -->
          <div class="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>{{ calcularPercentual(unidade.no_prazo, unidade.total).toFixed(1) }}% cumprindo SLA</span>
            <span 
              v-if="unidade.vencido > 0"
              class="font-semibold text-red-600 dark:text-red-400"
            >
              {{ calcularPercentual(unidade.vencido, unidade.total).toFixed(1) }}% em atraso
            </span>
          </div>
        </div>

        <!-- Badge de alerta crítico -->
        <div 
          v-if="calcularPercentual(unidade.vencido, unidade.total) > 50"
          class="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-semibold"
        >
          <ExclamationTriangleIcon class="w-3.5 h-3.5" />
          Situação Crítica
        </div>

        <p
          v-if="unidade.sem_vinculo_catalogo"
          class="mt-3 text-xs text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2"
        >
          Nenhum serviço destes cartões tem secretaria no catálogo nem OS com unidade.
          O gargalo existe operacionalmente, mas a governança precisa vincular responsáveis.
        </p>
      </div>
    </div>

    <!-- Estado vazio -->
    <div v-else class="p-12 text-center">
      <CheckCircleIcon
        v-if="!totalVencido"
        class="w-16 h-16 text-green-500 mx-auto mb-4"
      />
      <ExclamationTriangleIcon
        v-else
        class="w-16 h-16 text-amber-500 mx-auto mb-4"
      />
      <p class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ totalVencido ? 'Atrasos sem decomposição por secretaria' : 'Nenhum Gargalo Identificado' }}
      </p>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-2 max-w-md mx-auto">
        {{
          totalVencido
            ? `${totalVencido} item(ns) com SLA vencido na Mesa, mas nenhuma secretaria pôde ser atribuída. Revise o catálogo de serviços e ordens de serviço.`
            : 'Todas as unidades monitoradas estão cumprindo os prazos estabelecidos.'
        }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { 
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

defineProps({
  unidades: {
    type: Array,
    required: true
  },
  totalVencido: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

function getRankingBadgeClass(index) {
  if (index === 0) {
    return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
  }
  if (index === 1) {
    return 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
  }
  if (index === 2) {
    return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400'
  }
  return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400'
}

function calcularPercentual(valor, total) {
  if (!total || total === 0) return 0
  return (valor / total) * 100
}

function formatarTMA(horas) {
  if (horas === null || horas === undefined) return 'N/A'
  
  const dias = Math.floor(horas / 24)
  const horasRestantes = Math.floor(horas % 24)
  
  if (dias > 0) {
    return horasRestantes > 0 ? `${dias}d ${horasRestantes}h` : `${dias}d`
  }
  
  return `${horasRestantes}h`
}
</script>
