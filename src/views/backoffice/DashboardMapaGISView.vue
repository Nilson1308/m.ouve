<template>
  <div class="h-[calc(100vh-4rem)] bg-gray-50 dark:bg-gray-900 relative overflow-hidden">
    <!-- Mapa (Fundo - ocupa toda a tela) -->
    <div class="absolute inset-0">
      <MapaCalorExecutivo
        ref="mapaRef"
        :coordenadas="coordenadasMapa"
        :demandas="demandasMapa"
        :demanda-selecionada-id="demandaSelecionada?.id ?? null"
        :exibir-marcadores="exibirMarcadoresDemanda"
        :loading="dashboardStore.loadingMapaCalor"
        :centro="centroMapa"
        :zoom="13"
        @selecionar-demanda="handleSelecionarDemanda"
        @limpar-selecao="demandaSelecionada = null"
      />
    </div>

    <!-- Painel de Filtros (Overlay - canto superior esquerdo no desktop, bottom drawer no mobile) -->
    <div class="absolute inset-x-0 bottom-0 lg:inset-y-0 lg:left-0 lg:bottom-auto z-[1000] pointer-events-none">
      <div class="pointer-events-auto p-4 lg:p-6 lg:max-w-md">
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="lg:translate-x-[-100%] translate-y-full opacity-0"
          enter-to-class="lg:translate-x-0 translate-y-0 opacity-100"
          leave-active-class="transition-all duration-300 ease-in"
          leave-from-class="lg:translate-x-0 translate-y-0 opacity-100"
          leave-to-class="lg:translate-x-[-100%] translate-y-full opacity-0"
        >
          <PainelFiltrosMapaGIS
            v-show="painelVisivel"
            :filtros="dashboardStore.filtrosMapaCalor"
            :loading="dashboardStore.loadingMapaCalor"
            :minimizavel="true"
            :minimizado="painelMinimizado"
            :exibir-filtro-servico="true"
            :servicos-disponiveis="catalogoStore.servicosAtivos"
            :bairros-disponiveis="dashboardStore.bairrosDisponiveis"
            :loading-bairros="dashboardStore.loadingBairros"
            @aplicar="handleAplicarFiltros"
            @limpar="handleLimparFiltros"
            @atualizar="atualizarMapa"
            @toggle-minimizado="painelMinimizado = !painelMinimizado"
          />
        </Transition>
      </div>
    </div>

    <!-- Botão Toggle Painel (Mobile/Desktop) -->
    <button
      @click="painelVisivel = !painelVisivel"
      class="absolute top-4 left-4 z-[1001] lg:hidden btn-primary shadow-2xl flex items-center gap-2"
    >
      <AdjustmentsHorizontalIcon class="w-5 h-5" />
      <span class="text-sm font-semibold">Filtros</span>
    </button>

    <!-- Header Info (Canto superior - Mobile/Desktop) -->
    <div class="absolute top-4 left-1/2 transform -translate-x-1/2 z-[999] pointer-events-none">
      <div class="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 rounded-full shadow-2xl px-6 py-3 pointer-events-auto">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
            <MapIcon class="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 class="text-sm font-bold text-gray-900 dark:text-white leading-tight">
              Visão Territorial
            </h1>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ dashboardStore.periodoFormatado }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Resumo da demanda (clique no mapa) -->
    <div
      class="absolute inset-x-4 bottom-4 lg:inset-x-auto lg:top-24 lg:right-6 lg:bottom-auto z-[1001] pointer-events-none flex justify-center lg:justify-end"
    >
      <div class="pointer-events-auto w-full max-w-md">
        <PainelResumoDemandaMapaGIS
          :demanda="demandaSelecionada"
          @fechar="demandaSelecionada = null"
          @abrir-visao-360="abrirVisao360"
        />
      </div>
    </div>

    <!-- Legenda do Heatmap (canto inferior direito — longe do painel de filtros) -->
    <div 
      v-if="coordenadasMapa.length > 0"
      class="absolute bottom-6 right-6 z-[999] bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 rounded-lg shadow-2xl p-4 w-[220px] max-w-[calc(100vw-2rem)]"
    >
      <h4 class="text-xs font-bold text-gray-900 dark:text-white mb-3">
        Densidade de Ocorrências
      </h4>
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded-full bg-gradient-to-r from-green-400 to-green-500"></div>
          <span class="text-xs text-gray-700 dark:text-gray-300">Baixa</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded-full bg-gradient-to-r from-yellow-400 to-yellow-500"></div>
          <span class="text-xs text-gray-700 dark:text-gray-300">Média</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded-full bg-gradient-to-r from-orange-400 to-orange-500"></div>
          <span class="text-xs text-gray-700 dark:text-gray-300">Alta</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded-full bg-gradient-to-r from-red-500 to-red-600"></div>
          <span class="text-xs text-gray-700 dark:text-gray-300">Crítica</span>
        </div>
      </div>
      <div v-if="demandasMapa.length" class="mt-4 pt-3 border-t border-gray-200/70 dark:border-gray-700/70">
        <label class="flex items-center justify-between gap-2 cursor-pointer">
          <span class="text-xs font-semibold text-gray-800 dark:text-gray-200">Pontos clicáveis</span>
          <input
            v-model="exibirMarcadoresDemanda"
            type="checkbox"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
        </label>
        <p class="mt-2 text-[11px] leading-snug text-gray-600 dark:text-gray-400">
          Toque no marcador para resumo e acesso à visão 360º.
        </p>
      </div>
    </div>

    <!-- Toast de Erro (se houver) -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="translate-y-[-100%] opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-[-100%] opacity-0"
    >
      <div 
        v-if="dashboardStore.erro"
        class="absolute top-20 left-1/2 transform -translate-x-1/2 z-[1002] max-w-md w-full mx-4"
      >
        <div class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4 shadow-xl">
          <div class="flex items-start gap-3">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
            <div class="flex-1">
              <h4 class="text-sm font-semibold text-red-900 dark:text-red-200 mb-1">
                Erro ao Carregar Dados
              </h4>
              <p class="text-sm text-red-700 dark:text-red-300">
                {{ dashboardStore.erro }}
              </p>
            </div>
            <button
              @click="dashboardStore.erro = null"
              class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useCatalogoStore } from '@/stores/catalogo'
import { useAdminToast } from '@/composables/useAdminToast'
import MapaCalorExecutivo from '@/components/backoffice/dashboard/MapaCalorExecutivo.vue'
import PainelFiltrosMapaGIS from '@/components/backoffice/dashboard/PainelFiltrosMapaGIS.vue'
import PainelResumoDemandaMapaGIS from '@/components/backoffice/dashboard/PainelResumoDemandaMapaGIS.vue'
import {
  MapIcon,
  AdjustmentsHorizontalIcon,
  ExclamationTriangleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const dashboardStore = useDashboardStore()
const catalogoStore = useCatalogoStore()
const { mostrarToast } = useAdminToast()
const mapaRef = ref(null)
const painelVisivel = ref(true)
const painelMinimizado = ref(false)
const demandaSelecionada = ref(null)
const exibirMarcadoresDemanda = ref(true)

// Centro padrão (Mogi das Cruzes)
const centroMapa = ref({
  lat: -23.5222,
  lng: -46.1883
})

// Coordenadas processadas para o mapa
const coordenadasMapa = computed(() => dashboardStore.mapaCalor?.coordenadas || [])
const demandasMapa = computed(() => dashboardStore.mapaCalor?.demandas || [])

function handleSelecionarDemanda(demanda) {
  demandaSelecionada.value = demanda
}

function abrirVisao360(demanda) {
  if (!demanda?.id) return
  router.push({
    name: 'backoffice-protocolo-detalhes',
    params: { id: demanda.id }
  })
}

// Métodos
async function carregarDados() {
  demandaSelecionada.value = null
  try {
    await dashboardStore.carregarMapaCalor()
    
    // Após carregar, ajustar mapa se necessário
    nextTick(() => {
      if (mapaRef.value) {
        mapaRef.value.invalidateSize()
        if (coordenadasMapa.value.length > 0) {
          mapaRef.value.fitBounds()
        }
      }
    })
  } catch {
    mostrarToast(dashboardStore.erro || 'Erro ao carregar mapa de calor', true)
  }
}

async function handleAplicarFiltros(filtros) {
  demandaSelecionada.value = null
  try {
    await dashboardStore.aplicarFiltrosMapaCalor(filtros)
  } catch {
    mostrarToast(dashboardStore.erro || 'Erro ao aplicar filtros no mapa', true)
  }
  
  // Fechar painel no mobile após aplicar
  if (window.innerWidth < 1024) {
    painelVisivel.value = false
  }
}

async function handleLimparFiltros() {
  demandaSelecionada.value = null
  try {
    await dashboardStore.limparFiltrosMapaCalor()
  } catch {
    mostrarToast(dashboardStore.erro || 'Erro ao limpar filtros do mapa', true)
  }
}

async function atualizarMapa() {
  await carregarDados()
}

// Lifecycle
onMounted(() => {
  void catalogoStore.carregarServicosCatalogo({ ativo: true }).catch(() => {})
  void carregarDados()

  painelVisivel.value = window.innerWidth >= 1024
})
</script>

<style scoped>
/* Animações suaves para transições */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Garantir que o mapa ocupe toda a altura disponível */
:deep(.leaflet-container) {
  height: 100%;
  width: 100%;
}

/* Glassmorphism para overlays */
.backdrop-blur-lg {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
</style>
