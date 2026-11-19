<template>
  <div class="location-map-root rounded-card overflow-hidden border border-gray-200 dark:border-gray-600 high-contrast:border-yellow-300">
    <div
      ref="containerRef"
      class="w-full"
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
  zoom: { type: Number, default: 17 },
  height: { type: String, default: '12rem' }
})

const emit = defineEmits(['update:latitude', 'update:longitude', 'move'])

const containerRef = ref(null)
let map = null
let marker = null

function initMap() {
  if (!containerRef.value || props.latitude == null || props.longitude == null) return
  if (map) {
    map.remove()
    map = null
    marker = null
  }

  map = L.map(containerRef.value, {
    scrollWheelZoom: true,
    touchZoom: true
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map)

  marker = L.marker([props.latitude, props.longitude], {
    draggable: props.draggable
  }).addTo(map)

  map.setView([props.latitude, props.longitude], props.zoom)

  if (props.draggable) {
    marker.on('dragend', () => {
      const { lat, lng } = marker.getLatLng()
      emit('update:latitude', lat)
      emit('update:longitude', lng)
      emit('move', { latitude: lat, longitude: lng })
    })
  }
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

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(
  () => [props.latitude, props.longitude],
  ([lat, lng]) => {
    if (lat != null && lng != null) {
      if (!map) {
        nextTick(() => initMap())
      } else {
        syncMarker(lat, lng)
      }
    }
  }
)
</script>

<style scoped>
.location-map-root :deep(.leaflet-control-attribution) {
  font-size: 10px;
}
</style>
