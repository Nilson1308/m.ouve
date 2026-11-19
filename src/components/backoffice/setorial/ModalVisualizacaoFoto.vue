<template>
  <!-- Backdrop -->
  <div
    class="fixed inset-0 bg-black/90 backdrop-blur-sm z-[60] flex items-center justify-center p-4"
    @click="$emit('fechar')"
  >
    <!-- Container -->
    <div
      class="relative max-w-6xl w-full"
      @click.stop
    >
      <!-- Header -->
      <div class="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-gradient-to-b from-black/60 to-transparent">
        <div class="text-white">
          <p class="text-sm font-medium">
            {{ currentIndex + 1 }} / {{ todas.length }}
          </p>
          <p class="text-lg font-bold">
            {{ foto.legenda }}
          </p>
        </div>

        <button
          @click="$emit('fechar')"
          class="p-2 bg-black/50 hover:bg-black/70 rounded-lg transition-colors"
        >
          <XMarkIcon class="w-6 h-6 text-white" />
        </button>
      </div>

      <!-- Imagem -->
      <div class="relative aspect-video bg-black rounded-lg overflow-hidden">
        <img
          :src="foto.url"
          :alt="foto.legenda"
          class="w-full h-full object-contain"
        />

        <!-- Navegação -->
        <button
          v-if="todas.length > 1"
          @click="$emit('anterior')"
          class="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-black/50 hover:bg-black/70 rounded-full transition-colors"
        >
          <ChevronLeftIcon class="w-6 h-6 text-white" />
        </button>

        <button
          v-if="todas.length > 1"
          @click="$emit('proxima')"
          class="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-black/50 hover:bg-black/70 rounded-full transition-colors"
        >
          <ChevronRightIcon class="w-6 h-6 text-white" />
        </button>
      </div>

      <!-- Info Footer -->
      <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/60 to-transparent">
        <div class="flex items-center justify-between text-white text-sm">
          <div class="flex items-center gap-4">
            <span class="flex items-center gap-1.5">
              <CalendarIcon class="w-4 h-4" />
              {{ formatarData(foto.enviado_em) }}
            </span>
            <span class="flex items-center gap-1.5">
              <UserIcon class="w-4 h-4" />
              {{ foto.enviado_por }}
            </span>
            <span v-if="foto.metadata?.gps" class="flex items-center gap-1.5 text-green-400">
              <MapPinIcon class="w-4 h-4" />
              GPS: {{ foto.metadata.gps.lat.toFixed(4) }}, {{ foto.metadata.gps.lng.toFixed(4) }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="baixar"
              class="p-2 bg-black/50 hover:bg-black/70 rounded-lg transition-colors"
              title="Baixar imagem"
            >
              <ArrowDownTrayIcon class="w-5 h-5" />
            </button>
            <a
              :href="foto.url"
              target="_blank"
              class="p-2 bg-black/50 hover:bg-black/70 rounded-lg transition-colors"
              title="Abrir em nova aba"
            >
              <ArrowTopRightOnSquareIcon class="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarIcon,
  UserIcon,
  MapPinIcon,
  ArrowDownTrayIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  foto: {
    type: Object,
    required: true
  },
  todas: {
    type: Array,
    required: true
  }
})

defineEmits(['fechar', 'proxima', 'anterior'])

const currentIndex = computed(() => {
  return props.todas.findIndex(f => f.id === props.foto.id)
})

function formatarData(data) {
  const d = new Date(data)
  const dia = d.getDate().toString().padStart(2, '0')
  const mes = (d.getMonth() + 1).toString().padStart(2, '0')
  const ano = d.getFullYear()
  const hora = d.getHours().toString().padStart(2, '0')
  const min = d.getMinutes().toString().padStart(2, '0')
  return `${dia}/${mes}/${ano} às ${hora}:${min}`
}

async function baixar() {
  try {
    const response = await fetch(props.foto.url)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `evidencia-${props.foto.id}.jpg`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Erro ao baixar imagem:', error)
  }
}
</script>
