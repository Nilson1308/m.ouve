<template>
  <div class="space-y-2">
    <!-- Grid de Miniaturas -->
    <div class="grid gap-2" :class="gridClass">
      <div
        v-for="(foto, index) in fotos"
        :key="index"
        class="relative group rounded-card overflow-hidden bg-gray-100 dark:bg-gray-700 aspect-square cursor-pointer hover:opacity-90 transition-opacity"
        @click="$emit('visualizar', index)"
      >
        <img
          :src="urlSegura(foto.url)"
          :alt="foto.nome || `Foto ${index + 1}`"
          class="w-full h-full object-cover"
        />
        
        <!-- Overlay com Info -->
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
          <div class="absolute bottom-2 left-2 right-2">
            <p class="text-xs font-semibold text-white truncate">
              {{ foto.nome || `foto_${index + 1}.jpg` }}
            </p>
            <p v-if="foto.tamanho" class="text-xs text-gray-300">
              {{ formatarTamanho(foto.tamanho) }}
            </p>
          </div>
        </div>

        <!-- Botão Remover (se editável) -->
        <button
          v-if="editavel"
          @click.stop="$emit('remover', index)"
          class="absolute top-1 right-1 p-1.5 bg-red-500 hover:bg-red-600 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <XMarkIcon class="w-4 h-4 text-white" />
        </button>

        <!-- Badge de Contador (se mais de 4 fotos) -->
        <div
          v-if="index === 3 && fotos.length > 4"
          class="absolute inset-0 bg-black/70 flex items-center justify-center"
        >
          <span class="text-2xl font-bold text-white">
            +{{ fotos.length - 4 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Contador -->
    <div v-if="mostrarContador" class="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
      <span class="flex items-center gap-1">
        <PhotoIcon class="w-4 h-4" />
        {{ fotos.length }} {{ fotos.length === 1 ? 'foto' : 'fotos' }}
      </span>
      <span v-if="tamanhoTotal">
        {{ formatarTamanho(tamanhoTotal) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { XMarkIcon, PhotoIcon } from '@heroicons/vue/24/outline'
import { ensureHttpsMediaUrl } from '@/utils/mediaUrl'

function urlSegura(url) {
  return ensureHttpsMediaUrl(url)
}

const props = defineProps({
  fotos: {
    type: Array,
    required: true,
    // Array de objetos: { url, nome?, tamanho? }
  },
  editavel: {
    type: Boolean,
    default: false
  },
  mostrarContador: {
    type: Boolean,
    default: true
  },
  maxExibicao: {
    type: Number,
    default: 4
  }
})

defineEmits(['visualizar', 'remover'])

// Define grid baseado no número de fotos
const gridClass = computed(() => {
  const count = Math.min(props.fotos.length, props.maxExibicao)
  if (count === 1) return 'grid-cols-1'
  if (count === 2) return 'grid-cols-2'
  return 'grid-cols-2'
})

// Tamanho total dos arquivos
const tamanhoTotal = computed(() => {
  return props.fotos.reduce((total, foto) => total + (foto.tamanho || 0), 0)
})

// Formata tamanho de arquivo
function formatarTamanho(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>
