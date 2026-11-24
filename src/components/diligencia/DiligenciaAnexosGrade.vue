<template>
  <div v-if="lista.length" class="mt-3 space-y-2">
    <p class="text-xs font-semibold text-gray-600 dark:text-gray-400">
      {{ labelQuantidade }}
    </p>
    <div v-if="imagens.length" class="grid grid-cols-3 sm:grid-cols-4 gap-2">
      <button
        v-for="(anexo, idx) in imagens"
        :key="anexo.id"
        type="button"
        class="group relative aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        :aria-label="`Ampliar ${nomeAnexoExibicao(anexo, `imagem ${idx + 1}`)}`"
        @click="abrirLightbox(anexo)"
      >
        <img
          :src="anexo.url"
          :alt="nomeAnexoExibicao(anexo)"
          class="w-full h-full object-cover transition group-hover:opacity-90"
          loading="lazy"
        />
      </button>
    </div>
    <ul v-if="documentos.length" class="flex flex-col gap-2">
      <li
        v-for="doc in documentos"
        :key="doc.id"
        class="flex items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/60 px-3 py-2 text-sm"
      >
        <DocumentIcon class="w-5 h-5 shrink-0 text-gray-500 dark:text-gray-400" aria-hidden="true" />
        <span class="flex-1 min-w-0 truncate text-gray-800 dark:text-gray-200" :title="nomeAnexoExibicao(doc)">
          {{ nomeAnexoExibicao(doc) }}
        </span>
        <a
          :href="doc.url"
          target="_blank"
          rel="noopener noreferrer"
          class="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:underline shrink-0"
        >
          Abrir
        </a>
        <a
          :href="doc.url"
          download
          class="text-xs font-medium text-gray-600 dark:text-gray-400 hover:underline shrink-0"
        >
          Baixar
        </a>
      </li>
    </ul>
  </div>

  <ModalVisualizacaoFoto
    v-if="fotoLightbox"
    :foto="fotoLightbox"
    :todas="fotosLightbox"
    @fechar="fotoLightbox = null"
    @anterior="navegarLightbox(-1)"
    @proxima="navegarLightbox(1)"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import { DocumentIcon } from '@heroicons/vue/24/outline'
import ModalVisualizacaoFoto from '@/components/backoffice/setorial/ModalVisualizacaoFoto.vue'
import {
  ehImagemAnexo,
  mapAnexoDiligencia,
  nomeAnexoExibicao
} from '@/utils/diligenciaHelpers'

const props = defineProps({
  anexos: { type: Array, default: () => [] }
})

const fotoLightbox = ref(null)

const lista = computed(() => {
  if (!props.anexos?.length) return []
  return props.anexos.map(mapAnexoDiligencia).filter((a) => a?.url)
})

const imagens = computed(() => lista.value.filter((a) => a.url && ehImagemAnexo(a)))
const documentos = computed(() =>
  lista.value.filter((a) => a.url && !ehImagemAnexo(a))
)

const labelQuantidade = computed(() => {
  const n = lista.value.filter((a) => a.url).length || lista.value.length
  return n === 1 ? '1 anexo na resposta' : `${n} anexos na resposta`
})

const fotosLightbox = computed(() =>
  imagens.value.map((a) => ({
    id: a.id,
    url: a.url,
    legenda: nomeAnexoExibicao(a),
    enviado_em: a.criado_em || new Date().toISOString(),
    enviado_por: 'Cidadão'
  }))
)

function abrirLightbox(anexo) {
  fotoLightbox.value = {
    id: anexo.id,
    url: anexo.url,
    legenda: nomeAnexoExibicao(anexo),
    enviado_em: anexo.criado_em || new Date().toISOString(),
    enviado_por: 'Cidadão'
  }
}

function navegarLightbox(delta) {
  const todas = fotosLightbox.value
  if (!fotoLightbox.value || todas.length < 2) return
  const idx = todas.findIndex((f) => f.id === fotoLightbox.value.id)
  const next = (idx + delta + todas.length) % todas.length
  fotoLightbox.value = { ...todas[next] }
}
</script>