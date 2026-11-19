<template>
  <div class="h-full flex flex-col bg-white dark:bg-gray-800">
    <!-- Header do Mapa -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">
          Visão Geográfica de Protocolos
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ protocolosVisiveis.length }} protocolo(s) no mapa
        </p>
      </div>

      <!-- Ferramentas -->
      <div class="flex items-center gap-3">
        <!-- Toggle Modo Seleção -->
        <button
          @click="modoSelecao = !modoSelecao"
          :class="[
            'px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2',
            modoSelecao
              ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/50'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          ]"
        >
          <CursorArrowRaysIcon class="w-5 h-5" />
          Seleção em Lote
          <span v-if="modoSelecao && protocolosSelecionados.length > 0" class="px-2 py-0.5 bg-white/20 rounded-full text-xs font-bold">
            {{ protocolosSelecionados.length }}
          </span>
        </button>

        <!-- Botão Limpar Seleção -->
        <button
          v-if="protocolosSelecionados.length > 0"
          @click="limparSelecao"
          class="px-4 py-2 bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/50 text-red-700 dark:text-red-300 rounded-lg font-medium text-sm transition-colors"
        >
          Limpar Seleção
        </button>

        <!-- Botão Resetar Visualização -->
        <button
          @click="resetarMapa"
          class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title="Resetar visualização"
        >
          <ArrowsPointingOutIcon class="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>
    </div>

    <!-- Área do Mapa -->
    <div class="flex-1 relative">
      <!-- Mapa Leaflet -->
      <div ref="mapaContainer" class="w-full h-full"></div>

      <!-- Overlay quando em modo seleção -->
      <div
        v-if="modoSelecao"
        class="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-primary-600 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-3 animate-bounce"
      >
        <CursorArrowRaysIcon class="w-5 h-5" />
        <span class="font-semibold">
          Clique nos pinos para selecionar múltiplos protocolos
        </span>
      </div>

      <!-- Botão Flutuante de Agrupamento -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-10"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-10"
      >
        <div
          v-if="protocolosSelecionados.length >= 2"
          class="absolute bottom-8 left-1/2 -translate-x-1/2 z-[1000]"
        >
          <button
            @click="abrirModalCriarSuperOS"
            class="group relative px-8 py-4 bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 hover:from-primary-700 hover:via-purple-700 hover:to-pink-700 text-white rounded-2xl font-bold text-lg shadow-2xl transition-all transform hover:scale-105"
          >
            <!-- Brilho animado -->
            <div class="absolute inset-0 bg-gradient-to-r from-primary-400 via-purple-400 to-pink-400 rounded-2xl opacity-0 group-hover:opacity-30 blur-xl transition-opacity"></div>
            
            <div class="relative flex items-center gap-3">
              <SparklesIcon class="w-6 h-6" />
              <span>
                Agrupar {{ protocolosSelecionados.length }} selecionados em Super OS
              </span>
              <ArrowRightIcon class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </div>
          </button>
        </div>
      </Transition>

      <!-- Legenda -->
      <div class="absolute bottom-4 right-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 border border-gray-200 dark:border-gray-700">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          Legenda
        </h3>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-red-500 rounded-full"></div>
            <span class="text-xs text-gray-700 dark:text-gray-300">Urgente</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-orange-500 rounded-full"></div>
            <span class="text-xs text-gray-700 dark:text-gray-300">Alta</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span class="text-xs text-gray-700 dark:text-gray-300">Normal</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 bg-purple-500 rounded-full ring-4 ring-purple-200"></div>
            <span class="text-xs text-gray-700 dark:text-gray-300">Selecionado</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Criar Super OS -->
    <ModalCriarSuperOS
      v-if="modalCriarAberto"
      :protocolos="protocolosSelecionados"
      @fechar="modalCriarAberto = false"
      @confirmar="criarSuperOSManual"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useSuperOSStore } from '@/stores/super_os'
import {
  CursorArrowRaysIcon,
  ArrowsPointingOutIcon,
  SparklesIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'
import ModalCriarSuperOS from './ModalCriarSuperOS.vue'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps({
  protocolos: {
    type: Array,
    default: () => []
  },
  sugestaoDestacada: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['protocolo-selecionado', 'super-os-criada', 'super-os-erro'])

// Store
const superOSStore = useSuperOSStore()

// Estado
const mapaContainer = ref(null)
const mapa = ref(null)
const marcadores = ref({})
const modoSelecao = ref(false)
const protocolosSelecionados = ref([])
const modalCriarAberto = ref(false)

// Computeds
const protocolosVisiveis = computed(() => props.protocolos || [])

// Lifecycle
onMounted(() => {
  inicializarMapa()
})

onBeforeUnmount(() => {
  if (mapa.value) {
    mapa.value.remove()
  }
})

// Watchers
watch(() => protocolosVisiveis.value, () => {
  atualizarMarcadores()
}, { deep: true })

watch(() => props.sugestaoDestacada, (sugestao) => {
  if (sugestao) {
    destacarSugestao(sugestao)
  }
})

// Funções
function inicializarMapa() {
  if (!mapaContainer.value) return

  mapa.value = L.map(mapaContainer.value, {
    center: [-23.522, -46.1883],
    zoom: 13,
    zoomControl: true
  })

  // Adicionar tiles do OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(mapa.value)

  // Adicionar marcadores iniciais
  atualizarMarcadores()
}

function atualizarMarcadores() {
  if (!mapa.value) return

  // Limpar marcadores existentes
  Object.values(marcadores.value).forEach(marker => {
    mapa.value.removeLayer(marker)
  })
  marcadores.value = {}

  // Adicionar novos marcadores
  protocolosVisiveis.value.forEach(protocolo => {
    adicionarMarcador(protocolo)
  })

  // Ajustar bounds se houver protocolos
  if (protocolosVisiveis.value.length > 0) {
    const bounds = protocolosVisiveis.value.map(p => [p.coordenadas.lat, p.coordenadas.lng])
    mapa.value.fitBounds(bounds, { padding: [50, 50] })
  }
}

function adicionarMarcador(protocolo) {
  if (!mapa.value || !protocolo.coordenadas) return

  const isSelecionado = protocolosSelecionados.value.some(p => p.id === protocolo.id)
  
  // Cor baseada na urgência
  let cor = '#3B82F6' // azul (normal)
  if (protocolo.urgencia === 'urgente') cor = '#EF4444' // vermelho
  else if (protocolo.urgencia === 'alta') cor = '#F97316' // laranja

  // Ícone customizado
  const icon = L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="relative">
        ${isSelecionado ? '<div class="absolute inset-0 bg-purple-500 rounded-full animate-ping opacity-75"></div>' : ''}
        <div class="relative w-8 h-8 rounded-full shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform cursor-pointer ${isSelecionado ? 'ring-4 ring-purple-300' : ''}" style="background-color: ${cor}">
          <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32]
  })

  const marker = L.marker(
    [protocolo.coordenadas.lat, protocolo.coordenadas.lng],
    { icon }
  ).addTo(mapa.value)

  // Popup com informações
  const popupContent = `
    <div class="p-2">
      <div class="font-bold text-sm mb-1">${protocolo.codigo}</div>
      <div class="text-xs text-gray-600 mb-1">${protocolo.servico}</div>
      <div class="text-xs text-gray-500">${protocolo.endereco}</div>
    </div>
  `
  marker.bindPopup(popupContent)

  // Evento de click
  marker.on('click', () => {
    if (modoSelecao.value) {
      toggleSelecao(protocolo)
    } else {
      emit('protocolo-selecionado', protocolo)
    }
  })

  marcadores.value[protocolo.id] = marker
}

function toggleSelecao(protocolo) {
  const index = protocolosSelecionados.value.findIndex(p => p.id === protocolo.id)
  
  if (index !== -1) {
    protocolosSelecionados.value.splice(index, 1)
  } else {
    protocolosSelecionados.value.push(protocolo)
  }

  // Atualizar visualização do marcador
  atualizarMarcadores()
}

function limparSelecao() {
  protocolosSelecionados.value = []
  atualizarMarcadores()
}

function resetarMapa() {
  if (!mapa.value) return
  
  mapa.value.setView([-23.522, -46.1883], 13)
  limparSelecao()
}

function destacarSugestao(sugestao) {
  if (!mapa.value) return

  // Centralizar no centro geográfico da sugestão
  mapa.value.setView(
    [sugestao.centro_geografico.lat, sugestao.centro_geografico.lng],
    14,
    { animate: true, duration: 0.5 }
  )

  // Desenhar círculo representando o raio
  const circulo = L.circle(
    [sugestao.centro_geografico.lat, sugestao.centro_geografico.lng],
    {
      color: '#8B5CF6',
      fillColor: '#8B5CF6',
      fillOpacity: 0.1,
      radius: sugestao.raio_km * 1000 // converter km para metros
    }
  ).addTo(mapa.value)

  // Remover círculo após 3 segundos
  setTimeout(() => {
    mapa.value.removeLayer(circulo)
  }, 3000)

  // Destacar protocolos da sugestão
  sugestao.protocolos.forEach(protocolo => {
    const marker = marcadores.value[protocolo.id]
    if (marker) {
      marker.openPopup()
    }
  })
}

function abrirModalCriarSuperOS() {
  modalCriarAberto.value = true
}

async function criarSuperOSManual(dados) {
  const qtd = protocolosSelecionados.value.length
  try {
    const resultado = await superOSStore.criarSuperOSMapa({
      titulo_resumo: dados.titulo,
      protocolos_ids: protocolosSelecionados.value.map((p) => p.id)
    })

    modalCriarAberto.value = false
    limparSelecao()

    emit('super-os-criada', {
      titulo: dados.titulo,
      quantidade: qtd,
      super_os: resultado.super_os,
      codigo: resultado.super_os?.codigo
    })
  } catch (error) {
    emit('super-os-erro', getApiErrorMessage(error, 'Erro ao criar Super OS.'))
  }
}
</script>

<style>
/* Estilos para marcadores Leaflet */
.custom-marker {
  background: transparent;
  border: none;
}

.leaflet-popup-content-wrapper {
  border-radius: 8px;
}

.leaflet-popup-content {
  margin: 0;
}
</style>
