<template>
  <div class="relative w-full h-full">
    <!-- Container do Mapa -->
    <div 
      ref="mapaContainer" 
      class="w-full h-full rounded-lg overflow-hidden"
      role="application"
      aria-label="Mapa de calor de ocorrências territoriais"
    />

    <!-- Badge Contador (canto superior direito) -->
    <div 
      v-if="!loading && coordenadas.length > 0"
      class="absolute top-4 right-4 z-[1000] bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg px-4 py-2.5"
    >
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-gradient-to-r from-green-400 via-yellow-400 to-red-500 animate-pulse"></div>
        <div>
          <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">
            Ocorrências
          </p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">
            {{ coordenadas.length.toLocaleString('pt-BR') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div 
      v-if="loading"
      class="absolute inset-0 z-[1001] bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm flex items-center justify-center rounded-lg"
    >
      <div class="text-center">
        <div class="inline-block w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-3"></div>
        <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
          Carregando mapa...
        </p>
      </div>
    </div>

    <!-- Estado Vazio -->
    <div 
      v-if="!loading && coordenadas.length === 0"
      class="absolute inset-0 z-[999] flex items-center justify-center pointer-events-none"
    >
      <div class="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-xl p-8 text-center max-w-md shadow-xl">
        <MapIcon class="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Nenhuma Ocorrência Encontrada
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Não há dados para exibir com os filtros selecionados. Ajuste os parâmetros e tente novamente.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { HeatLayer } from 'leaflet.heat'
import { MapIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  coordenadas: {
    type: Array,
    default: () => []
    // Formato esperado: [{ latitude, longitude, intensidade }]
  },
  demandas: {
    type: Array,
    default: () => []
  },
  demandaSelecionadaId: {
    type: String,
    default: null
  },
  exibirMarcadores: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  centro: {
    type: Object,
    default: () => ({ lat: -23.5222, lng: -46.1883 }) // Mogi das Cruzes
  },
  zoom: {
    type: Number,
    default: 13
  }
})

const emit = defineEmits(['selecionar-demanda', 'limpar-selecao'])

const mapaContainer = ref(null)
let mapa = null
let camadaCalor = null
let camadaMarcadores = null
const marcadoresPorId = new Map()

// ==================== INICIALIZAÇÃO ====================

function initMapa() {
  if (!mapaContainer.value) return
  
  // Remover mapa anterior se existir
  if (mapa) {
    mapa.remove()
    mapa = null
    camadaCalor = null
    camadaMarcadores = null
    marcadoresPorId.clear()
  }
  
  // Criar novo mapa
  mapa = L.map(mapaContainer.value, {
    center: [props.centro.lat, props.centro.lng],
    zoom: props.zoom,
    scrollWheelZoom: true,
    touchZoom: true,
    zoomControl: true
  })
  
  // Adicionar tile layer (OpenStreetMap)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mapa)

  mapa.on('click', () => {
    emit('limpar-selecao')
  })
  
  // Desenhar heatmap inicial
  desenharCamadas()
}

function criarIconeDemanda(selecionado) {
  const classe = selecionado ? 'demanda-marcador demanda-marcador--ativo' : 'demanda-marcador'
  const html = `<div class="${classe}" aria-hidden="true"><span class="demanda-marcador__halo"></span><span class="demanda-marcador__nucleo"></span></div>`
  return L.divIcon({
    className: 'demanda-marcador-host',
    html,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  })
}

function desenharMarcadores() {
  if (!mapa) return

  if (camadaMarcadores) {
    mapa.removeLayer(camadaMarcadores)
    camadaMarcadores = null
    marcadoresPorId.clear()
  }

  if (!props.exibirMarcadores || !props.demandas?.length) return

  camadaMarcadores = L.layerGroup().addTo(mapa)

  props.demandas.forEach((demanda) => {
    const lat = Number(demanda.latitude)
    const lng = Number(demanda.longitude)
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return

    const selecionado = props.demandaSelecionadaId === demanda.id
    const marcador = L.marker([lat, lng], {
      icon: criarIconeDemanda(selecionado),
      riseOnHover: true,
      zIndexOffset: selecionado ? 1200 : 500
    })

    marcador.on('click', (ev) => {
      L.DomEvent.stopPropagation(ev)
      emit('selecionar-demanda', demanda)
    })

    marcador.addTo(camadaMarcadores)
    marcadoresPorId.set(demanda.id, marcador)
  })
}

function atualizarEstiloMarcadores() {
  if (!props.demandas?.length) return
  props.demandas.forEach((demanda) => {
    const marcador = marcadoresPorId.get(demanda.id)
    if (!marcador) return
    const selecionado = props.demandaSelecionadaId === demanda.id
    marcador.setIcon(criarIconeDemanda(selecionado))
    marcador.setZIndexOffset(selecionado ? 1200 : 500)
  })

  if (props.demandaSelecionadaId) {
    const ativo = props.demandas.find((d) => d.id === props.demandaSelecionadaId)
    if (ativo && mapa) {
      mapa.panTo([ativo.latitude, ativo.longitude], {
        animate: true,
        duration: 0.35
      })
    }
  }
}

function desenharCamadas() {
  desenharHeatmap()
  desenharMarcadores()
}

// ==================== HEATMAP ====================

function desenharHeatmap() {
  if (!mapa) return
  
  // Remover camada anterior
  if (camadaCalor) {
    mapa.removeLayer(camadaCalor)
    camadaCalor = null
  }
  
  // Verificar se há coordenadas
  if (!props.coordenadas || props.coordenadas.length === 0) {
    return
  }
  
  // Preparar dados no formato [lat, lng, intensidade]
  const pontos = props.coordenadas
    .filter(coord => coord.latitude != null && coord.longitude != null)
    .map(coord => {
      const lat = Number(coord.latitude)
      const lng = Number(coord.longitude)
      const intensidade = coord.intensidade || 1
      return [lat, lng, intensidade]
    })
  
  if (pontos.length === 0) return
  
  // Criar camada de heatmap
  camadaCalor = new HeatLayer(pontos, {
    radius: 25,
    blur: 15,
    maxZoom: 17,
    max: 1.0,
    gradient: {
      0.0: '#00ff00',
      0.2: '#80ff00',
      0.4: '#ffff00',
      0.6: '#ffaa00',
      0.8: '#ff5500',
      1.0: '#ff0000'
    }
  })
  camadaCalor.addTo(mapa)
  
  // Ajustar bounds do mapa para incluir todos os pontos
  ajustarBounds(pontos)
}

function ajustarBounds(pontos) {
  if (!mapa || pontos.length === 0) return
  
  // Criar bounds com todos os pontos
  const latLngs = pontos.map(p => [p[0], p[1]])
  const bounds = L.latLngBounds(latLngs)
  
  // Ajustar mapa para mostrar todos os pontos
  if (pontos.length === 1) {
    // Se for apenas um ponto, centralizar nele
    mapa.setView([pontos[0][0], pontos[0][1]], 15)
  } else {
    // Se forem múltiplos pontos, ajustar bounds com padding
    mapa.fitBounds(bounds, {
      padding: [50, 50],
      maxZoom: 15
    })
  }
}

// ==================== WATCHERS ====================

watch(
  () => [props.coordenadas, props.demandas, props.exibirMarcadores],
  () => {
    nextTick(() => {
      desenharCamadas()
    })
  },
  { deep: true }
)

watch(
  () => props.demandaSelecionadaId,
  () => {
    nextTick(() => atualizarEstiloMarcadores())
  }
)

watch(
  () => props.loading,
  (novoValor) => {
    if (!novoValor && mapa) {
      // Quando terminar de carregar, redesenhar
      nextTick(() => {
        mapa.invalidateSize()
        desenharCamadas()
      })
    }
  }
)

// ==================== LIFECYCLE ====================

onMounted(() => {
  nextTick(() => {
    initMapa()
  })
})

onBeforeUnmount(() => {
  if (camadaCalor) {
    mapa?.removeLayer(camadaCalor)
    camadaCalor = null
  }
  if (camadaMarcadores) {
    mapa?.removeLayer(camadaMarcadores)
    camadaMarcadores = null
  }
  marcadoresPorId.clear()
  if (mapa) {
    mapa.remove()
    mapa = null
  }
})

// ==================== EXPOSED METHODS ====================

defineExpose({
  invalidateSize: () => mapa?.invalidateSize(),
  fitBounds: () => {
    if (props.coordenadas.length > 0) {
      const pontos = props.coordenadas.map(c => [c.latitude, c.longitude])
      ajustarBounds(pontos)
    }
  }
})
</script>

<style scoped>
/* Ajustes do Leaflet para melhor integração */
:deep(.leaflet-control-attribution) {
  font-size: 10px;
  background-color: rgba(255, 255, 255, 0.8);
}

:deep(.leaflet-control-zoom) {
  border: 1px solid rgb(209 213 219) !important;
  border-radius: 0.5rem;
  overflow: hidden;
}

:deep(.leaflet-control-zoom a) {
  background-color: white;
  color: rgb(75 85 99);
  border-bottom: 1px solid rgb(229 231 235);
  width: 34px;
  height: 34px;
  line-height: 34px;
  font-size: 20px;
}

:deep(.leaflet-control-zoom a:hover) {
  background-color: rgb(243 244 246);
  color: rgb(55 65 81);
}

/* Dark mode */
.dark :deep(.leaflet-control-attribution) {
  background-color: rgba(31, 41, 55, 0.8);
  color: rgb(209 213 219);
}

.dark :deep(.leaflet-control-zoom) {
  border-color: rgb(55 65 81) !important;
}

.dark :deep(.leaflet-control-zoom a) {
  background-color: rgb(31 41 55);
  color: rgb(209 213 219);
  border-bottom-color: rgb(55 65 81);
}

.dark :deep(.leaflet-control-zoom a:hover) {
  background-color: rgb(55 65 81);
  color: rgb(243 244 246);
}

:deep(.demanda-marcador-host) {
  background: transparent;
  border: none;
}

:deep(.demanda-marcador) {
  position: relative;
  width: 28px;
  height: 28px;
  cursor: pointer;
}

:deep(.demanda-marcador__halo) {
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: rgb(99 102 241 / 0.25);
  transform: scale(0.85);
  transition: transform 0.2s ease, background 0.2s ease;
}

:deep(.demanda-marcador__nucleo) {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  margin: -6px 0 0 -6px;
  border-radius: 9999px;
  background: linear-gradient(135deg, rgb(99 102 241), rgb(147 51 234));
  border: 2px solid white;
  box-shadow: 0 2px 8px rgb(99 102 241 / 0.45);
}

:deep(.demanda-marcador--ativo .demanda-marcador__halo) {
  transform: scale(1.35);
  background: rgb(234 88 12 / 0.28);
}

:deep(.demanda-marcador--ativo .demanda-marcador__nucleo) {
  width: 14px;
  height: 14px;
  margin: -7px 0 0 -7px;
  background: linear-gradient(135deg, rgb(249 115 22), rgb(239 68 68));
  box-shadow: 0 0 0 4px rgb(249 115 22 / 0.25);
}
</style>
