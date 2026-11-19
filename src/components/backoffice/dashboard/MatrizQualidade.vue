<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <ChartBarSquareIcon class="w-5 h-5 text-primary-500" />
            Matriz de Qualidade
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Cruzamento de Velocidade (SLA) vs. Satisfação (Avaliações)
          </p>
        </div>
        <div class="text-right">
          <p class="text-xs text-gray-500 dark:text-gray-500">{{ unidadesVisiveis.length }} secretarias</p>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="p-12">
      <div class="flex flex-col items-center justify-center">
        <div class="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
        <p class="text-sm text-gray-600 dark:text-gray-400">Carregando dados de qualidade...</p>
      </div>
    </div>

    <!-- Gráfico -->
    <div v-else-if="unidadesVisiveis.length > 0" class="p-6">
      <div class="relative">
        <!-- Canvas para o gráfico -->
        <div
          ref="graficoContainer"
          class="w-full rounded-lg border border-gray-200 dark:border-gray-700 relative isolate"
          style="height: 500px;"
        >
          <!-- Fundo + grade (clipe só aqui) -->
          <div class="absolute inset-0 overflow-hidden rounded-lg bg-gray-50 dark:bg-gray-900 pointer-events-none">
          <svg class="absolute inset-0 w-full h-full" style="z-index: 1;">
            <!-- Linhas verticais -->
            <line 
              v-for="i in 5" 
              :key="`v-${i}`"
              :x1="`${i * 20}%`" 
              y1="0" 
              :x2="`${i * 20}%`" 
              y2="100%" 
              stroke="currentColor" 
              class="text-gray-300 dark:text-gray-700" 
              stroke-width="1" 
              stroke-dasharray="4,4"
            />
            <!-- Linhas horizontais -->
            <line 
              v-for="i in 5" 
              :key="`h-${i}`"
              x1="0" 
              :y1="`${i * 20}%`" 
              x2="100%" 
              :y2="`${i * 20}%`" 
              stroke="currentColor" 
              class="text-gray-300 dark:text-gray-700" 
              stroke-width="1" 
              stroke-dasharray="4,4"
            />
            
            <!-- Linha divisória central vertical (SLA 50%) -->
            <line 
              x1="50%" 
              y1="0" 
              x2="50%" 
              y2="100%" 
              stroke="currentColor" 
              class="text-gray-400 dark:text-gray-600" 
              stroke-width="2"
            />
            
            <!-- Linha divisória central horizontal (Satisfação 3.0) -->
            <line 
              x1="0" 
              :y1="`${yPosicao(3.0)}%`" 
              x2="100%" 
              :y2="`${yPosicao(3.0)}%`" 
              stroke="currentColor" 
              class="text-gray-400 dark:text-gray-600" 
              stroke-width="2"
            />
          </svg>
          </div>

          <!-- Quadrantes (labels de fundo) -->
          <div class="absolute inset-0 grid grid-cols-2 grid-rows-2 pointer-events-none overflow-hidden rounded-lg" style="z-index: 2;">
            <!-- Quadrante Superior Esquerdo: Baixo SLA, Alta Satisfação (Amarelo) -->
            <div class="flex items-center justify-center p-4">
              <span class="text-xs font-semibold text-amber-600 dark:text-amber-400 opacity-20 pointer-events-none">
                LENTOS, QUALIDADE ALTA
              </span>
            </div>
            
            <!-- Quadrante Superior Direito: Alto SLA, Alta Satisfação (Verde) -->
            <div class="flex items-center justify-center p-4">
              <span class="text-xs font-semibold text-green-600 dark:text-green-400 opacity-20 pointer-events-none">
                EXCELÊNCIA
              </span>
            </div>
            
            <!-- Quadrante Inferior Esquerdo: Baixo SLA, Baixa Satisfação (Vermelho) -->
            <div class="flex items-center justify-center p-4">
              <span class="text-xs font-semibold text-red-600 dark:text-red-400 opacity-20 pointer-events-none">
                CRÍTICO
              </span>
            </div>
            
            <!-- Quadrante Inferior Direito: Alto SLA, Baixa Satisfação (Laranja) -->
            <div class="flex items-center justify-center p-4">
              <span class="text-xs font-semibold text-orange-600 dark:text-orange-400 opacity-20 pointer-events-none">
                RÁPIDO, MAL AVALIADO
              </span>
            </div>
          </div>

          <!-- Pontos (secretarias) — camada com overflow visível -->
          <div class="absolute inset-0 overflow-visible" style="z-index: 10;">
            <div
              v-for="unidade in unidadesVisiveis"
              :key="unidade.id"
              class="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
              :style="{ 
                left: `${xPosicao(unidade.taxa_sla_cumprido)}%`, 
                top: `${yPosicao(unidade.media_satisfacao)}%` 
              }"
              @mouseenter="abrirTooltip(unidade, $event)"
              @mouseleave="fecharTooltip"
            >
              <!-- Ponto + sigla (sempre visível) -->
              <div
                class="flex flex-col items-center gap-0.5"
                :class="pontoHover?.id === unidade.id ? 'scale-110' : 'scale-100'"
              >
                <div
                  class="w-4 h-4 rounded-full transition-all duration-200 ring-2 ring-white dark:ring-gray-800"
                  :class="[
                    getCorPonto(unidade),
                    pontoHover?.id === unidade.id ? 'scale-125 ring-4' : ''
                  ]"
                />
                <span
                  class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-white/90 dark:bg-gray-900/90 text-gray-800 dark:text-gray-200 shadow-sm border border-gray-200/80 dark:border-gray-600/80 max-w-[72px] truncate"
                  :title="unidade.nome"
                >
                  {{ unidade.sigla || unidade.nome?.slice(0, 6) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tooltip flutuante (acima de sidebars e sem clip do gráfico) -->
        <Teleport to="body">
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="tooltipFlutuante"
              class="fixed z-[250] pointer-events-none w-[min(280px,calc(100vw-24px))]"
              :style="tooltipFlutuante.estilo"
              role="tooltip"
            >
              <div class="bg-gray-900 dark:bg-gray-800 text-white rounded-lg shadow-2xl p-3 border border-gray-700/50">
                <div class="text-sm font-semibold mb-1 leading-snug">{{ tooltipFlutuante.unidade.nome }}</div>
                <div class="text-xs space-y-0.5 text-gray-300">
                  <div>
                    SLA Cumprido:
                    <strong class="text-white">
                      {{ tooltipFlutuante.unidade.taxa_sla_cumprido.toFixed(1) }}%
                    </strong>
                  </div>
                  <div>
                    Satisfação:
                    <strong class="text-white">
                      {{
                        tooltipFlutuante.unidade.media_satisfacao != null
                          ? `${Number(tooltipFlutuante.unidade.media_satisfacao).toFixed(1)}/5.0`
                          : '—'
                      }}
                    </strong>
                  </div>
                  <div>
                    Avaliações:
                    <strong class="text-white">{{ tooltipFlutuante.unidade.total_avaliacoes }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </Teleport>

        <!-- Eixos -->
        <div class="mt-4 grid grid-cols-2 gap-4">
          <!-- Eixo X -->
          <div>
            <div class="flex items-center gap-2 mb-2">
              <div class="w-3 h-0.5 bg-gray-400 dark:bg-gray-600"></div>
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Eixo X: Taxa de SLA Cumprido</span>
            </div>
            <div class="flex justify-between text-xs text-gray-600 dark:text-gray-400">
              <span>0%</span>
              <span>25%</span>
              <span class="font-bold">50%</span>
              <span>75%</span>
              <span>100%</span>
            </div>
          </div>

          <!-- Eixo Y -->
          <div>
            <div class="flex items-center gap-2 mb-2">
              <div class="w-0.5 h-3 bg-gray-400 dark:bg-gray-600"></div>
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Eixo Y: Média de Satisfação</span>
            </div>
            <div class="flex justify-between text-xs text-gray-600 dark:text-gray-400">
              <span>1.0</span>
              <span>2.0</span>
              <span class="font-bold">3.0</span>
              <span>4.0</span>
              <span>5.0</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Legenda dos Quadrantes -->
      <div class="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="flex items-center gap-2 p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
          <span class="text-xs font-semibold text-green-700 dark:text-green-400">Excelência</span>
        </div>
        <div class="flex items-center gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
          <div class="w-3 h-3 rounded-full bg-amber-500"></div>
          <span class="text-xs font-semibold text-amber-700 dark:text-amber-400">Lentos, Qualidade Alta</span>
        </div>
        <div class="flex items-center gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <span class="text-xs font-semibold text-red-700 dark:text-red-400">Crítico</span>
        </div>
        <div class="flex items-center gap-2 p-3 rounded-lg bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800">
          <div class="w-3 h-3 rounded-full bg-orange-500"></div>
          <span class="text-xs font-semibold text-orange-700 dark:text-orange-400">Rápido, Mal Avaliado</span>
        </div>
      </div>

      <!-- Alerta de unidades ocultas -->
      <div 
        v-if="unidadesOcultas > 0"
        class="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
      >
        <div class="flex items-start gap-3">
          <InformationCircleIcon class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-sm font-semibold text-blue-900 dark:text-blue-200">
              Unidades Sem Avaliações Suficientes
            </p>
            <p class="text-sm text-blue-700 dark:text-blue-300 mt-1">
              {{ unidadesOcultas }} secretaria(s) foram ocultadas por não possuírem avaliações de cidadãos. 
              Incentive o uso do sistema de avaliação para melhorar a análise.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado vazio -->
    <div v-else class="p-12 text-center">
      <ChartBarSquareIcon class="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
      <p class="text-lg font-semibold text-gray-900 dark:text-white">
        Sem Dados de Qualidade
      </p>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">
        {{
          unidades.length
            ? `Nenhuma secretaria atinge o mínimo de ${minimoAvaliacoes} avaliação(ões) para plotar no gráfico.`
            : 'Nenhum protocolo resolvido com avaliação no escopo atual.'
        }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  ChartBarSquareIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  unidades: {
    type: Array,
    default: () => []
    // Formato esperado: [{ id, nome, sigla, taxa_sla_cumprido, media_satisfacao, total_avaliacoes }]
  },
  loading: {
    type: Boolean,
    default: false
  },
  minimoAvaliacoes: {
    type: Number,
    default: 5 // Mínimo de avaliações para aparecer no gráfico
  }
})

const pontoHover = ref(null)
const tooltipFlutuante = ref(null)
const graficoContainer = ref(null)

const TOOLTIP_LARGURA = 260
const TOOLTIP_MARGEM = 12

function abrirTooltip(unidade, evento) {
  pontoHover.value = unidade
  const alvo = evento?.currentTarget
  if (!alvo || typeof alvo.getBoundingClientRect !== 'function') return

  const rect = alvo.getBoundingClientRect()
  const centroX = rect.left + rect.width / 2
  const topoMarcador = rect.top
  const acima = topoMarcador > 120

  let left = centroX - TOOLTIP_LARGURA / 2
  const maxLeft = window.innerWidth - TOOLTIP_LARGURA - TOOLTIP_MARGEM
  left = Math.max(TOOLTIP_MARGEM, Math.min(left, maxLeft))

  const estilo = acima
    ? {
        left: `${left}px`,
        top: `${topoMarcador - 8}px`,
        transform: 'translateY(-100%)'
      }
    : {
        left: `${left}px`,
        top: `${rect.bottom + 8}px`,
        transform: 'translateY(0)'
      }

  tooltipFlutuante.value = { unidade, estilo }
}

function fecharTooltip() {
  pontoHover.value = null
  tooltipFlutuante.value = null
}

/** Margem interna para pontos nos eixos não ficarem cortados (overflow-hidden). */
const PLOT_INSET = 8

// Filtrar unidades com avaliações suficientes
const unidadesVisiveis = computed(() => {
  return props.unidades.filter(u => {
    return u.total_avaliacoes >= props.minimoAvaliacoes &&
           u.media_satisfacao != null &&
           u.taxa_sla_cumprido != null
  })
})

const unidadesOcultas = computed(() => {
  return props.unidades.length - unidadesVisiveis.value.length
})

function insetLinear(valor0a100) {
  const v = Math.max(0, Math.min(100, valor0a100))
  return PLOT_INSET + (v / 100) * (100 - 2 * PLOT_INSET)
}

// Calcular posição X (SLA: 0% a 100%)
function xPosicao(taxa_sla) {
  return insetLinear(Number(taxa_sla) || 0)
}

// Calcular posição Y (Satisfação: 1.0 a 5.0, invertido pois Y cresce pra baixo)
function yPosicao(satisfacao) {
  const sat = Math.max(1, Math.min(5, Number(satisfacao) || 1))
  const normalizado = (sat - 1.0) / 4.0
  const yBruto = 100 - normalizado * 100
  return insetLinear(yBruto)
}

// Determinar cor do ponto baseado no quadrante
function getCorPonto(unidade) {
  const sla = unidade.taxa_sla_cumprido
  const sat = unidade.media_satisfacao
  
  if (sla >= 50 && sat >= 3.0) {
    // Alto SLA, Alta Satisfação: EXCELÊNCIA (Verde)
    return 'bg-green-500 hover:bg-green-600'
  } else if (sla < 50 && sat >= 3.0) {
    // Baixo SLA, Alta Satisfação: LENTOS MAS QUALIDADE ALTA (Amarelo)
    return 'bg-amber-500 hover:bg-amber-600'
  } else if (sla < 50 && sat < 3.0) {
    // Baixo SLA, Baixa Satisfação: CRÍTICO (Vermelho)
    return 'bg-red-500 hover:bg-red-600'
  } else {
    // Alto SLA, Baixa Satisfação: RÁPIDO MAS MAL AVALIADO (Laranja)
    return 'bg-orange-500 hover:bg-orange-600'
  }
}
</script>
