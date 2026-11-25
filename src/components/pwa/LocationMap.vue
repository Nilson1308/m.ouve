<template>
  <div class="location-map-root rounded-card overflow-hidden border border-gray-200 dark:border-gray-600 high-contrast:border-yellow-300">
    <div
      ref="containerRef"
      class="w-full h-64"
      :style="{ height }"
      role="application"
      :aria-label="draggable ? 'Mapa: arraste o pino para ajustar a localização' : 'Mapa da localização'"
    />
    <p v-if="draggable" class="text-xs text-center py-2 px-3 bg-gray-50 dark:bg-gray-900 text-gray-600 dark:text-gray-400">
      Arraste o pino vermelho para marcar o ponto exato do problema
    </p>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, ref, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow
})

const props = defineProps({
  latitude: { type: Number, default: null },
  longitude: { type: Number, default: null },
  draggable: { type: Boolean, default: false },
  pickOnClick: { type: Boolean, default: false },
  defaultLatitude: { type: Number, default: -23.5222 },
  defaultLongitude: { type: Number, default: -46.1883 },
  zoom: { type: Number, default: 17 },
  height: { type: String, default: '16rem' }
})

const emit = defineEmits(['update:latitude', 'update:longitude', 'move'])

const containerRef = ref(null)
let map = null
let marker = null
let resizeObserver = null

function coordenadasAtivas() {
  if (props.latitude != null && props.longitude != null) {
    return { lat: props.latitude, lng: props.longitude, temMarcador: true }
  }
  return {
    lat: props.defaultLatitude,
    lng: props.defaultLongitude,
    temMarcador: false
  }
}

function emitirPosicao(lat, lng) {
  emit('update:latitude', lat)
  emit('update:longitude', lng)
  emit('move', { latitude: lat, longitude: lng })
}

function ligarMarcador(lat, lng) {
  if (!map) return
  if (!marker) {
    marker = L.marker([lat, lng], { draggable: props.draggable || props.pickOnClick }).addTo(map)
    if (props.draggable || props.pickOnClick) {
      marker.on('dragend', () => {
        const pos = marker.getLatLng()
        emitirPosicao(pos.lat, pos.lng)
      })
    }
  } else {
    marker.setLatLng([lat, lng])
  }
}

function recentralizar() {
  if (!map) return
  const { lat, lng, temMarcador } = coordenadasAtivas()
  if (temMarcador) {
    map.setView([lat, lng], map.getZoom() || props.zoom)
  }
}

function agendarInvalidateSize() {
  if (!map) return
  map.invalidateSize({ pan: false })
  nextTick(() => {
    requestAnimationFrame(() => {
      map?.invalidateSize({ pan: false })
      setTimeout(() => map?.invalidateSize({ pan: false }), 150)
    })
  })
}

function initMap() {
  if (!containerRef.value) return
  if (map) {
    map.remove()
    map = null
    marker = null
  }

  const { lat, lng, temMarcador } = coordenadasAtivas()

  map = L.map(containerRef.value, {
    scrollWheelZoom: true,
    touchZoom: true
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map)

  map.setView([lat, lng], props.zoom)

  if (temMarcador) {
    ligarMarcador(lat, lng)
  }

  if (props.pickOnClick) {
    map.on('click', (ev) => {
      const { lat: cLat, lng: cLng } = ev.latlng
      ligarMarcador(cLat, cLng)
      if (marker && !marker.dragging?.enabled()) {
        marker.dragging.enable()
      }
      emitirPosicao(cLat, cLng)
    })
  }

  agendarInvalidateSize()
  observarResize()
}

function observarResize() {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (!containerRef.value || typeof ResizeObserver === 'undefined') return
  resizeObserver = new ResizeObserver(() => {
    map?.invalidateSize({ pan: false })
  })
  resizeObserver.observe(containerRef.value)
}

function syncMarker(lat, lng) {
  if (!map || lat == null || lng == null) return
  if (marker) {
    marker.setLatLng([lat, lng])
  }
  map.setView([lat, lng], map.getZoom())
}

onMounted(() => {
  nextTick(() => initMap())
})

defineExpose({
  invalidateSize: () => agendarInvalidateSize(),
  recentralizar
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (map) {
    map.remove()
    map = null
    marker = null
  }
})

watch(
  () => [props.latitude, props.longitude],
  ([lat, lng]) => {
    if (!map) {
      nextTick(() => initMap())
      return
    }
    if (lat != null && lng != null) {
      ligarMarcador(lat, lng)
      syncMarker(lat, lng)
    } else if (marker) {
      map.removeLayer(marker)
      marker = null
    }
  }
)
</script>

<style scoped>
.location-map-root :deep(.leaflet-control-attribution) {
  font-size: 10px;
}
.location-map-root :deep(.leaflet-container img) {
  max-width: none !important;
}
</style>