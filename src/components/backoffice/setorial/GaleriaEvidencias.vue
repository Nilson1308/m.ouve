<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h4 class="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
        <PhotoIcon class="w-5 h-5 text-gray-500" />
        Galeria de Evidências
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
          ({{ evidencias.length }} {{ evidencias.length === 1 ? 'foto' : 'fotos' }})
        </span>
      </h4>

      <button
        v-if="evidencias.length > 0"
        type="button"
        class="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
        @click="visualizarTodas"
      >
        Ver todas →
      </button>
    </div>

    <div
      v-if="evidencias.length === 0"
      class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-card p-8 text-center bg-gray-50 dark:bg-gray-700/30"
    >
      <div class="flex flex-col items-center gap-3">
        <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded-full">
          <PhotoIcon class="w-10 h-10 text-gray-400" />
        </div>
        <div>
          <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-1">
            Aguardando envio das evidências de campo
          </h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Use o link mágico <strong>ou</strong> envie fotos manualmente abaixo (persistidas no servidor).
          </p>
        </div>

        <div v-if="!somenteLeitura" class="mt-4">
          <label
            class="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            :class="{ 'pointer-events-none opacity-60': enviando }"
          >
            <ArrowUpTrayIcon class="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ enviando ? 'Enviando…' : 'Fazer upload manual' }}
            </span>
            <input
              type="file"
              accept="image/*"
              multiple
              class="hidden"
              :disabled="enviando"
              @change="onInputChange"
            />
          </label>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
            JPG, PNG ou HEIC — gravados na ordem de serviço
          </p>
        </div>
      </div>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div v-for="evidencia in evidencias" :key="evidencia.id" class="relative group">
        <div
          class="aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 cursor-pointer"
          @click="visualizar(evidencia)"
        >
          <img
            :src="evidencia.url"
            :alt="evidencia.legenda"
            class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
          <div class="absolute inset-0 bg-black/0 group-hover:bg-black/60 transition-colors flex items-center justify-center">
            <MagnifyingGlassPlusIcon class="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
        <div class="mt-2">
          <p class="text-xs font-medium text-gray-900 dark:text-white truncate">
            {{ evidencia.legenda }}
          </p>
          <span class="text-xs text-gray-500 dark:text-gray-400">
            {{ formatarData(evidencia.enviado_em) }}
          </span>
        </div>
      </div>

      <label
        v-if="!somenteLeitura"
        class="aspect-square rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-500 bg-gray-50 dark:bg-gray-700/30 cursor-pointer flex flex-col items-center justify-center gap-2 transition-colors group"
        :class="{ 'pointer-events-none opacity-60': enviando }"
      >
        <ArrowUpTrayIcon
          class="w-8 h-8 text-gray-400 group-hover:text-primary-500 transition-colors"
          :class="{ 'animate-pulse': enviando }"
        />
        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
          {{ enviando ? 'Enviando…' : 'Adicionar' }}
        </span>
        <input type="file" accept="image/*" multiple class="hidden" :disabled="enviando" @change="onInputChange" />
      </label>
    </div>

    <p v-if="erroUpload" class="text-sm text-red-600 dark:text-red-400 mt-2">{{ erroUpload }}</p>

    <ModalVisualizacaoFoto
      v-if="fotoAtual"
      :foto="fotoAtual"
      :todas="evidencias"
      @fechar="fotoAtual = null"
      @proxima="proximaFoto"
      @anterior="fotoAnterior"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  PhotoIcon,
  ArrowUpTrayIcon,
  MagnifyingGlassPlusIcon
} from '@heroicons/vue/24/outline'
import ModalVisualizacaoFoto from './ModalVisualizacaoFoto.vue'

const props = defineProps({
  evidencias: { type: Array, required: true },
  enviando: { type: Boolean, default: false },
  somenteLeitura: { type: Boolean, default: false }
})

const emit = defineEmits(['enviar-arquivos'])

const fotoAtual = ref(null)
const erroUpload = ref('')

function onFiles(files) {
  erroUpload.value = ''
  const lista = Array.from(files || [])
  if (!lista.length) return
  const invalidos = lista.filter((f) => !f.type.startsWith('image/'))
  if (invalidos.length) {
    erroUpload.value = 'Envie apenas imagens (JPG, PNG, etc.).'
    return
  }
  emit('enviar-arquivos', lista)
}

function onInputChange(event) {
  onFiles(event.target.files)
  event.target.value = ''
}

function visualizar(evidencia) {
  fotoAtual.value = evidencia
}

function visualizarTodas() {
  if (props.evidencias.length > 0) fotoAtual.value = props.evidencias[0]
}

function proximaFoto() {
  const index = props.evidencias.findIndex((e) => e.id === fotoAtual.value.id)
  fotoAtual.value =
    index < props.evidencias.length - 1
      ? props.evidencias[index + 1]
      : props.evidencias[0]
}

function fotoAnterior() {
  const index = props.evidencias.findIndex((e) => e.id === fotoAtual.value.id)
  fotoAtual.value =
    index > 0 ? props.evidencias[index - 1] : props.evidencias[props.evidencias.length - 1]
}

function formatarData(data) {
  if (!data) return '—'
  const d = new Date(data)
  const dia = d.getDate().toString().padStart(2, '0')
  const mes = (d.getMonth() + 1).toString().padStart(2, '0')
  const hora = d.getHours().toString().padStart(2, '0')
  const min = d.getMinutes().toString().padStart(2, '0')
  return `${dia}/${mes} ${hora}:${min}`
}
</script>