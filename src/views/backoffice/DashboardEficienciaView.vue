<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              Dashboard de Eficiência
            </h1>
            <p class="text-gray-600 dark:text-gray-400 mt-2">
              Visão executiva de desempenho operacional e cumprimento de SLA
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
        <p v-if="ultimaAtualizacao" class="text-xs text-gray-500 dark:text-gray-500 mt-3 flex items-center gap-1.5">
          <ClockIcon class="w-4 h-4" />
          Última atualização: {{ formatarDataHora(ultimaAtualizacao) }}
        </p>
      </div>

      <!-- Cards de KPI -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-6 mb-8">
        <!-- TMA Global -->
        <template v-if="carregando">
          <SkeletonKpi v-for="i in 5" :key="i" />
        </template>
        <template v-else-if="dados">
          <KpiCard
            titulo="TMA Global"
            subtitulo="Tempo Médio de Atendimento"
            ajuda="TMA: tempo médio desde a abertura do protocolo até a conclusão — quanto menor, mais ágil a operação."
            :valor="formatarTMA(dados.tma_global_horas)"
            :icon="ClockIcon"
            :variacao="dados.tma_variacao"
            :variacao-invertida="true"
            tipo="primary"
            :contexto="`Meta: ${dados.meta_tma_dias || 5} dias`"
            :contexto-icon="FlagIcon"
          />

          <KpiCard
            titulo="Taxa de SLA Cumprido"
            subtitulo="Protocolos no prazo"
            ajuda="Percentual de protocolos encerrados dentro do prazo (SLA) definido para o serviço."
            :icon="CheckBadgeIcon"
            :variacao="dados.sla_variacao"
            :tipo="
              (dados.taxa_sla_cumprido ?? 0) >= 80
                ? 'success'
                : (dados.taxa_sla_cumprido ?? 0) >= 60
                  ? 'warning'
                  : 'danger'
            "
          >
            <template #default>
              <span class="text-3xl font-bold">{{ formatarPercentual(dados.taxa_sla_cumprido) }}</span>
            </template>
            <template #subtitulo>
              <span>{{ dados.total_no_prazo }} de {{ dados.total_protocolos }} protocolos</span>
            </template>
          </KpiCard>

          <KpiCard
            titulo="Protocolos em Atraso"
            subtitulo="Acima do prazo SLA"
            ajuda="Demandas que ultrapassaram o prazo-regulamentar e exigem priorização na mesa."
            :valor="formatarNumero(dados.total_vencido)"
            :icon="ExclamationTriangleIcon"
            tipo="danger"
            :contexto="contextoPercentualVencidos"
          />

          <KpiCard
            titulo="Unidades com Gargalos"
            subtitulo="Secretarias problemáticas"
            ajuda="Quantidade de secretarias com desempenho abaixo do esperado no ranking de TMA/SLA."
            :valor="contarUnidadesCriticas"
            :icon="BuildingOffice2Icon"
            tipo="warning"
            :contexto="`${dados.ranking_unidades.length} unidades monitoradas`"
          />

          <KpiCard
            titulo="Taxa de Retrabalho"
            subtitulo="Contestação após conclusão"
            ajuda="Percentual de protocolos concluídos que voltaram à fila por contestação do cidadão."
            :icon="ArrowPathIcon"
            :tipo="tipoKpiRetrabalho"
          >
            <template #default>
              <span class="text-3xl font-bold">{{ textoTaxaRetrabalhoExec }}</span>
            </template>
            <template #subtitulo>
              <span>{{ textoTotalReabertosExec }}</span>
            </template>
          </KpiCard>
        </template>
      </div>

      <!-- Alerta de erro API -->
      <div
        v-if="!carregando && erro"
        class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 mb-8"
      >
        <div class="flex items-start gap-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
          <div>
            <h3 class="font-semibold text-red-900 dark:text-red-200">Falha ao carregar dashboard</h3>
            <p class="text-sm text-red-700 dark:text-red-300 mt-1">{{ erro }}</p>
          </div>
        </div>
      </div>

      <!-- Alerta quando não há dados -->
      <div 
        v-if="!carregando && !dados && !erro"
        class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6 mb-8"
      >
        <div class="flex items-start gap-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0" />
          <div>
            <h3 class="font-semibold text-amber-900 dark:text-amber-200">
              Dados Indisponíveis
            </h3>
            <p class="text-sm text-amber-700 dark:text-amber-300 mt-1">
              Não foi possível carregar os dados do dashboard. Tente novamente em alguns instantes.
            </p>
          </div>
        </div>
      </div>

      <!-- Grid: Gráficos + Ranking -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Distribuição de Status (placeholder futuro para gráfico) -->
        <div class="lg:col-span-1 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <ChartPieIcon class="w-5 h-5 text-primary-500" />
            Distribuição
          </h3>
          
          <div v-if="carregando" class="space-y-4 animate-pulse">
            <div class="h-40 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            <div class="space-y-2">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>

          <div v-else-if="dados" class="space-y-4">
            <!-- Placeholder visual simples -->
            <div class="relative">
              <div class="flex items-center justify-center h-40">
                <div class="text-center">
                  <p class="text-4xl font-bold text-gray-900 dark:text-white">
                    {{ dados.total_protocolos }}
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Total de Protocolos
                  </p>
                </div>
              </div>
            </div>

            <!-- Legenda -->
            <div class="space-y-2">
              <div class="flex items-center justify-between p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
                <span class="text-sm text-green-700 dark:text-green-400 flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-green-500"></span>
                  No Prazo
                </span>
                <span class="font-semibold text-green-700 dark:text-green-400">
                  {{ dados.total_no_prazo }}
                </span>
              </div>
              <div class="flex items-center justify-between p-2 rounded-lg bg-red-50 dark:bg-red-900/20">
                <span class="text-sm text-red-700 dark:text-red-400 flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-red-500"></span>
                  Vencido
                </span>
                <span class="font-semibold text-red-700 dark:text-red-400">
                  {{ dados.total_vencido }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Ranking de Gargalos -->
        <div class="lg:col-span-2">
          <RankingGargalos 
            :unidades="dados?.ranking_unidades || []"
            :total-vencido="dados?.total_vencido ?? 0"
            :loading="carregando"
          />
        </div>
      </div>

      <!-- Resumo Qualidade (protocolos resolvidos) -->
      <div
        v-if="!carregandoQualidade && dadosQualidade?.resumo"
        class="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-5 py-4">
          <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            SLA nos resolvidos
          </p>
          <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatarPercentual(dadosQualidade.resumo.taxa_sla_cumprido) }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {{ formatarNumero(dadosQualidade.resumo.total_resolvidos) }} concluídos
          </p>
        </div>
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-5 py-4">
          <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            Satisfação média
          </p>
          <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {{
              dadosQualidade.resumo.media_satisfacao != null
                ? `${dadosQualidade.resumo.media_satisfacao.toFixed(1)}/5`
                : '—'
            }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
            {{ formatarNumero(dadosQualidade.resumo.total_avaliacoes) }} avaliações no período
          </p>
        </div>
        <div class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-5 py-4">
          <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            Cidadãos satisfeitos
          </p>
          <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
            {{
              dadosQualidade.resumo.percentual_satisfeitos != null
                ? formatarPercentual(dadosQualidade.resumo.percentual_satisfeitos)
                : '—'
            }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
            Notas 4 ou 5 (CSAT)
          </p>
        </div>
        <div
          class="rounded-xl border px-5 py-4"
          :class="classeCardRetrabalhoQualidade"
        >
          <p class="text-xs font-semibold uppercase tracking-wide opacity-80">
            Taxa de retrabalho
          </p>
          <p class="mt-1 text-2xl font-bold">
            {{ dadosQualidade.resumo.taxa_retrabalho_formatada || '—' }}
          </p>
          <p class="text-xs mt-1 opacity-90">
            {{ formatarNumero(dadosQualidade.resumo.total_reabertos) }} protocolo(s) reaberto(s) entre
            {{ formatarNumero(dadosQualidade.resumo.total_resolvidos) }} concluídos
          </p>
        </div>
      </div>

      <div
        v-if="!carregandoQualidade && dadosQualidade?.matriz_servicos?.length"
        class="mt-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden"
      >
        <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-base font-semibold text-gray-900 dark:text-white">Retrabalho por serviço</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-900/60 text-xs uppercase text-gray-500">
              <tr>
                <th class="px-5 py-3 text-left">Serviço</th>
                <th class="px-5 py-3 text-right">Concluídos</th>
                <th class="px-5 py-3 text-right">Reabertos</th>
                <th class="px-5 py-3 text-right">Taxa</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="s in dadosQualidade.matriz_servicos" :key="s.servico_id || s.nome">
                <td class="px-5 py-3 font-medium text-gray-900 dark:text-white">{{ s.nome }}</td>
                <td class="px-5 py-3 text-right tabular-nums">{{ formatarNumero(s.total_resolvidos) }}</td>
                <td class="px-5 py-3 text-right tabular-nums">{{ formatarNumero(s.total_reabertos) }}</td>
                <td
                  class="px-5 py-3 text-right tabular-nums font-semibold"
                  :class="Number(s.taxa_retrabalho_percentual) > 10 ? 'text-amber-700 dark:text-amber-300' : ''"
                >
                  {{ formatarPercentual(s.taxa_retrabalho_percentual) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Matriz de Qualidade (SLA vs Satisfação) -->
      <div class="mt-6">
        <MatrizQualidade
          :unidades="dadosQualidade?.unidades || []"
          :loading="carregandoQualidade"
          :minimo-avaliacoes="minimoAvaliacoesMatriz"
        />
      </div>

      <!-- Insights automáticos (opcional) -->
      <div 
        v-if="!carregando && dados && insights.length > 0"
        class="mt-8 bg-gradient-to-br from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20 border border-primary-200 dark:border-primary-800 rounded-xl p-6"
      >
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <LightBulbIcon class="w-5 h-5 text-amber-500" />
          Insights Automáticos
        </h3>
        <ul class="space-y-2">
          <li 
            v-for="(insight, index) in insights" 
            :key="index"
            class="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
          >
            <span class="text-primary-500 font-bold">•</span>
            <span>{{ insight }}</span>
          </li>
        </ul>
      </div>
    </div>

    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="toastAberto"
          class="fixed bottom-6 right-6 z-[200] max-w-sm px-4 py-3 rounded-xl shadow-lg border text-sm font-medium flex items-start gap-2 bg-red-50 border-red-200 text-red-900 dark:bg-red-950 dark:border-red-800 dark:text-red-100"
          role="status"
        >
          <ExclamationTriangleIcon class="w-5 h-5 text-red-600 shrink-0" />
          <span>{{ toastMensagem }}</span>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { 
  ClockIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  BuildingOffice2Icon,
  ChartPieIcon,
  ArrowPathIcon,
  FlagIcon,
  LightBulbIcon
} from '@heroicons/vue/24/outline'
import KpiCard from '@/components/backoffice/dashboard/KpiCard.vue'
import SkeletonKpi from '@/components/backoffice/dashboard/SkeletonKpi.vue'
import RankingGargalos from '@/components/backoffice/dashboard/RankingGargalos.vue'
import MatrizQualidade from '@/components/backoffice/dashboard/MatrizQualidade.vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAdminToast } from '@/composables/useAdminToast'

const dashboardStore = useDashboardStore()
const { 
  eficiencia: dados, 
  loadingEficiencia: carregando,
  qualidade: dadosQualidade,
  loadingQualidade: carregandoQualidade,
  erro 
} = storeToRefs(dashboardStore)
const { toastAberto, toastMensagem, mostrarToast } = useAdminToast()

const ultimaAtualizacao = ref(null)

// Computed
const contarUnidadesCriticas = computed(() => {
  const lista = dados.value?.ranking_unidades || []
  return lista.filter((u) => {
    const total = u.total || 0
    const vencido = u.vencido || 0
    if (!total || !vencido) return false
    const percentualVencido = (u.pct_vencidos ?? (vencido / total) * 100) || 0
    return percentualVencido > 30 || vencido === total
  }).length
})

const contextoPercentualVencidos = computed(() => {
  const d = dados.value
  if (!d?.total_protocolos) return '—'
  const pct = ((Number(d.total_vencido) || 0) / d.total_protocolos) * 100
  return `${pct.toFixed(1)}% do total`
})

const textoTaxaRetrabalhoExec = computed(() => dados.value?.resumo_executivo?.taxa_retrabalho_formatada ?? '—')

const textoTotalReabertosExec = computed(() => {
  const n = Number(dados.value?.resumo_executivo?.total_reabertos)
  if (!Number.isFinite(n)) return '—'
  return `${n} protocolo(s) reaberto(s) no período`
})

const tipoKpiRetrabalho = computed(() => {
  const taxa = Number(dados.value?.resumo_executivo?.taxa_retrabalho_percentual)
  if (!Number.isFinite(taxa) || taxa <= 0) return 'primary'
  if (taxa > 10) return 'danger'
  if (taxa > 5) return 'warning'
  return 'success'
})

const classeCardRetrabalhoQualidade = computed(() => {
  const taxa = Number(dadosQualidade.value?.resumo?.taxa_retrabalho_percentual)
  if (Number.isFinite(taxa) && taxa > 10) {
    return 'border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950/30 text-amber-950 dark:text-amber-100'
  }
  return 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
})

const minimoAvaliacoesMatriz = computed(() => {
  const lista = dadosQualidade.value?.unidades || []
  const comMinimoPadrao = lista.filter((u) => (u.total_avaliacoes || 0) >= 5).length
  return comMinimoPadrao > 0 ? 5 : 1
})

const insights = computed(() => {
  if (!dados.value) return []
  
  const insights = []
  const d = dados.value
  
  // Insight 1: TMA global
  if (d.tma_global_horas > (d.meta_tma_dias || 5) * 24) {
    const dias = Math.floor(d.tma_global_horas / 24)
    insights.push(`TMA global de ${dias} dias está acima da meta. Considere revisar processos internos.`)
  }
  
  // Insight 2: Taxa SLA
  const taxa = Number(d.taxa_sla_cumprido)
  if (Number.isFinite(taxa) && taxa < 70) {
    insights.push(`Taxa de SLA em ${taxa.toFixed(1)}% indica necessidade urgente de intervenção.`)
  } else if (Number.isFinite(taxa) && taxa >= 90) {
    insights.push(`Excelente desempenho! ${taxa.toFixed(1)}% de cumprimento de SLA.`)
  }
  
  // Insight 3: Unidades críticas
  if (contarUnidadesCriticas.value > 0) {
    insights.push(`${contarUnidadesCriticas.value} secretaria(s) com mais de 30% dos protocolos em atraso.`)
  }

  const semCatalogo = (d.ranking_unidades || []).some((u) => u.sem_vinculo_catalogo && u.vencido > 0)
  if (semCatalogo) {
    insights.push(
      'Há atrasos sem secretaria identificada no catálogo. Vincule unidade responsável aos serviços em Configurações.'
    )
  }
  
  // Insight 4: Tendência
  if (d.tma_variacao && d.tma_variacao < -10) {
    insights.push(`TMA melhorou ${Math.abs(d.tma_variacao)}% em relação ao período anterior!`)
  }
  
  return insights
})

// Métodos
async function carregarDados() {
  const resultados = await Promise.allSettled([
    dashboardStore.carregarEficiencia(),
    dashboardStore.carregarQualidade({ silencioso: true })
  ])

  if (resultados[0].status === 'rejected') {
    mostrarToast(erro.value || 'Erro ao carregar dados do dashboard', true)
    return
  }
  if (resultados[1].status === 'rejected') {
    mostrarToast('Matriz de qualidade indisponível no momento.', true)
  }
  ultimaAtualizacao.value = new Date()
}

function formatarTMA(horas) {
  if (horas === null || horas === undefined) return 'N/A'
  
  const dias = Math.floor(horas / 24)
  const horasRestantes = Math.floor(horas % 24)
  
  if (dias > 0) {
    return horasRestantes > 0 ? `${dias}d ${horasRestantes}h` : `${dias} dias`
  }
  
  if (horasRestantes > 0) {
    return `${horasRestantes}h`
  }
  
  const minutos = Math.floor(horas * 60)
  return `${minutos}min`
}

function formatarDataHora(data) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(data)
}

function formatarNumero(n) {
  return (Number(n) || 0).toLocaleString('pt-BR')
}

function formatarPercentual(n) {
  if (n === null || n === undefined || !Number.isFinite(Number(n))) return '—'
  return `${Number(n).toFixed(1)}%`
}

// Lifecycle
onMounted(() => {
  carregarDados()
})
</script>
