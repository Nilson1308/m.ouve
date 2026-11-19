<template>
  <div class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
    <div ref="mapaContainer" class="w-full" :style="{ height }" />
    <p v-if="!temMapa" class="text-sm text-gray-500 dark:text-gray-400 text-center py-8 px-4">
      Sem coordenadas para exibir o mapa consolidado.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
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

const MOGI = { lat: -23.522, lng: -46.1883 }

const props = defineProps({
  centroide: { type: Object, default: () => ({}) },
  filhos: { type: Array, default: () => [] },
  height: { default: '18rem' }
})

const mapaContainer = ref(null)
const mapa = ref(null)
const marcadores = ref([])

const temMapa = computed(() => {
  const c = props.centroide
  if (c?.latitude != null && c?.longitude != null) return true
  return (props.filhos || []).some(
    (f) => f.localizacao?.latitude != null && f.localizacao?.longitude != null
  )
})

function latLngCentro() {
  const c = props.centroide || {}
  if (c.latitude != null && c.longitude != null) {
    return [Number(c.latitude), Number(c.longitude)]
  }
  const pts = (props.filhos || [])
    .map((f) => f.localizacao)
    .filter((loc) => loc?.latitude != null && loc?.longitude != null)
  if (!pts.length) return [MOGI.lat, MOGI.lng]
  const lat = pts.reduce((s, p) => s + Number(p.latitude), 0) / pts.length
  const lng = pts.reduce((s, p) => s + Number(p.longitude), 0) / pts.length
  return [lat, lng]
}

function limparMarcadores() {
  for (const m of marcadores.value) {
    mapa.value?.removeLayer(m)
  }
  marcadores.value = []
}

function desenhar() {
  if (!mapa.value) return
  limparMarcadores()

  const centro = latLngCentro()
  const pinCentro = L.circleMarker(centro, {
    radius: 12,
    color: '#ea580c',
    fillColor: '#f97316',
    fillOpacity: 0.9,
    weight: 3
  })
    .bindPopup('<strong>Centro do incidente</strong>')
    .addTo(mapa.value)
  marcadores.value.push(pinCentro)

  for (const filho of props.filhos || []) {
    const loc = filho.localizacao || {}
    if (loc.latitude == null || loc.longitude == null) continue
    const m = L.marker([Number(loc.latitude), Number(loc.longitude)])
      .bindPopup(`<strong>${filho.codigo}</strong><br/>${filho.cidadao?.nome || ''}`)
      .addTo(mapa.value)
    marcadores.value.push(m)
  }

  const bounds = marcadores.value.map((m) => m.getLatLng())
  if (bounds.length > 1) {
    mapa.value.fitBounds(L.latLngBounds(bounds), { padding: [28, 28], maxZoom: 17 })
  } else {
    mapa.value.setView(centro, 16)
  }
}

function initMapa() {
  if (!mapaContainer.value || mapa.value) return
  const centro = latLngCentro()
  mapa.value = L.map(mapaContainer.value, { scrollWheelZoom: false, zoomControl: true }).setView(
    centro,
    15
  )
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(mapa.value)
  desenhar()
}

onMounted(() => {
  if (temMapa.value) {
    initMapa()
  }
})

watch(
  () => [props.centroide, props.filhos],
  () => {
    if (!temMapa.value) return
    if (!mapa.value) {
      initMapa()
      return
    }
    desenhar()
  },
  { deep: true }
)

onUnmounted(() => {
  limparMarcadores()
  mapa.value?.remove()
  mapa.value = null
})
</script>