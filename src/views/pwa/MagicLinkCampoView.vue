<template>
  <div
    class="min-h-screen flex flex-col bg-slate-900 text-white"
    :class="{ 'bg-emerald-700': sucesso }"
  >
    <header
      v-if="!sucesso"
      class="px-4 py-5 border-b border-slate-700 bg-slate-900 safe-top"
    >
      <div class="max-w-lg mx-auto flex items-center justify-center">
        <img :src="BRAND.logos.dark" :alt="BRAND.name" class="h-10 w-auto" />
      </div>
    </header>

    <main class="flex-1 flex flex-col max-w-lg mx-auto w-full px-4 py-6 pb-28">
      <div
        v-if="sucesso"
        class="flex-1 flex flex-col items-center justify-center text-center px-6"
      >
        <CheckCircleIcon class="w-24 h-24 text-white mb-6" />
        <h1 class="text-2xl font-bold leading-snug mb-3">
          Evidências enviadas com sucesso!
        </h1>
        <p class="text-lg text-emerald-100">
          Você já pode fechar esta tela.
        </p>
      </div>

      <template v-else>
        <h1 class="text-2xl font-bold text-center mb-2">Envio de Evidências</h1>
        <p class="text-center text-slate-300 text-sm mb-6">
          Fotografe o serviço, descreva o que foi feito e envie para a secretaria.
        </p>

        <p
          v-if="erroEnvio"
          class="mb-4 p-4 rounded-xl bg-red-900/80 border border-red-500 text-sm"
        >
          {{ erroEnvio }}
        </p>

        <label
          class="flex flex-col items-center justify-center gap-3 min-h-[140px] border-2 border-dashed border-slate-500 rounded-2xl bg-slate-800/80 active:bg-slate-700 cursor-pointer mb-4 touch-manipulation"
        >
          <span class="text-4xl" aria-hidden="true">📷</span>
          <span class="text-base font-semibold text-center px-4">
            Tirar / escolher fotos
          </span>
          <input
            ref="inputArquivos"
            type="file"
            accept="image/*"
            capture="environment"
            multiple
            class="sr-only"
            @change="onArquivosSelecionados"
          />
        </label>

        <!-- Galeria / visualizador -->
        <section v-if="fotos.length" class="mb-6">
          <p class="text-sm font-semibold text-slate-200 mb-3">
            Pré-visualização ({{ fotos.length }})
          </p>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="(item, idx) in fotos"
              :key="item.id"
              type="button"
              class="relative aspect-square rounded-xl overflow-hidden border-2 border-slate-600 focus:ring-2 focus:ring-amber-400"
              @click="abrirVisualizador(idx)"
            >
              <img
                :src="item.previewUrl"
                :alt="item.file.name"
                class="w-full h-full object-cover"
              />
              <span
                class="absolute top-1 right-1 w-7 h-7 rounded-full bg-black/70 text-white text-lg leading-none flex items-center justify-center"
                @click.stop="removerFoto(idx)"
              >
                ×
              </span>
            </button>
          </div>
        </section>

        <!-- Descrição + ditado (voz → texto, gratuito no navegador) -->
        <section class="mb-6">
          <div class="flex items-center justify-between gap-2 mb-2">
            <label class="text-sm font-semibold text-slate-200">
              Descrição do serviço
            </label>
            <button
              v-if="ditadoSuportado"
              type="button"
              class="min-h-[44px] px-4 rounded-xl font-bold text-sm flex items-center gap-2 touch-manipulation"
              :class="
                ditadoOuvindo
                  ? 'bg-red-600 text-white'
                  : 'bg-slate-700 text-amber-300 border border-slate-500'
              "
              @click="alternarDitado"
            >
              <MicrophoneIcon class="w-5 h-5" />
              {{ ditadoOuvindo ? 'Parar ditado' : 'Falar descrição' }}
            </button>
          </div>

          <p
            v-if="ditadoOuvindo"
            class="mb-2 text-amber-300 text-sm font-medium animate-pulse"
          >
            Ouvindo… fale o relato em voz alta (o texto aparece abaixo).
          </p>
          <p v-else-if="ditadoParcial" class="mb-2 text-slate-400 text-sm italic">
            {{ ditadoParcial }}
          </p>
          <p v-if="ditadoErro" class="mb-2 text-red-400 text-sm">
            {{ ditadoErro }}
          </p>
          <p v-else-if="!ditadoSuportado" class="mb-2 text-slate-400 text-xs">
            Ditado por voz não disponível neste navegador. Digite o texto manualmente.
          </p>

          <textarea
            v-model="descricao"
            rows="5"
            class="w-full rounded-xl border-2 border-slate-600 bg-slate-800 text-white text-base px-4 py-3 placeholder-slate-500 focus:border-amber-400 focus:ring-0"
            placeholder="Digite ou use «Falar descrição» para ditar gratuitamente…"
          />
          <p class="mt-2 text-xs text-slate-500">
            O ditado usa o reconhecimento de voz do seu celular (grátis). Revise o texto antes de enviar.
          </p>
        </section>
      </template>
    </main>

    <footer
      v-if="!sucesso"
      class="fixed bottom-0 left-0 right-0 p-4 bg-slate-900/95 border-t border-slate-700 safe-bottom"
    >
      <div class="max-w-lg mx-auto">
        <button
          type="button"
          class="w-full min-h-[56px] text-lg font-bold rounded-2xl bg-amber-400 text-slate-900 shadow-lg active:scale-[0.98] disabled:opacity-50 touch-manipulation"
          :disabled="enviando || !podeEnviar"
          @click="enviar"
        >
          {{ enviando ? 'Enviando…' : 'Enviar Arquivos' }}
        </button>
      </div>
    </footer>

    <!-- Lightbox -->
    <Teleport to="body">
      <div
        v-if="visualizadorAberto"
        class="fixed inset-0 z-[100] bg-black/95 flex flex-col"
        @click.self="fecharVisualizador"
      >
        <div class="flex items-center justify-between p-4 text-white safe-top">
          <span class="text-sm font-medium">
            {{ visualizadorIndice + 1 }} / {{ fotos.length }}
          </span>
          <button
            type="button"
            class="text-2xl font-bold px-3 py-1"
            @click="fecharVisualizador"
          >
            ×
          </button>
        </div>
        <div class="flex-1 flex items-center justify-center px-4 pb-8">
          <img
            :src="fotos[visualizadorIndice]?.previewUrl"
            alt="Evidência"
            class="max-w-full max-h-full object-contain"
          />
        </div>
        <div
          v-if="fotos.length > 1"
          class="flex justify-center gap-6 pb-8 safe-bottom"
        >
          <button
            type="button"
            class="px-6 py-3 rounded-xl bg-white/20 font-semibold"
            @click="fotoAnterior"
          >
            Anterior
          </button>
          <button
            type="button"
            class="px-6 py-3 rounded-xl bg-amber-400 text-slate-900 font-semibold"
            @click="proximaFoto"
          >
            Próxima
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { CheckCircleIcon, MicrophoneIcon } from '@heroicons/vue/24/solid'
import axios from 'axios'
import { BRAND } from '@/constants/brand'
import { getApiErrorMessage } from '@/utils/apiError'
import { useSpeechDictation } from '@/composables/useSpeechDictation'

const route = useRoute()
const token = route.params.token

const fotos = ref([])
const descricao = ref('')
const enviando = ref(false)
const sucesso = ref(false)
const erroEnvio = ref(null)
const inputArquivos = ref(null)

const visualizadorAberto = ref(false)
const visualizadorIndice = ref(0)

function acrescentarTextoDitado(texto) {
  const atual = descricao.value.trim()
  descricao.value = atual ? `${atual} ${texto}` : texto
}

const {
  suportado: ditadoSuportado,
  ouvindo: ditadoOuvindo,
  erro: ditadoErro,
  parcial: ditadoParcial,
  alternar: alternarDitado,
  parar: pararDitado
} = useSpeechDictation({ onFinalText: acrescentarTextoDitado, lang: 'pt-BR' })

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

let idSequencial = 0

const podeEnviar = computed(
  () => fotos.value.length > 0 || descricao.value.trim().length > 0
)

function onArquivosSelecionados(event) {
  const lista = Array.from(event.target.files || [])
  for (const file of lista) {
    fotos.value.push({
      id: ++idSequencial,
      file,
      previewUrl: URL.createObjectURL(file)
    })
  }
  if (inputArquivos.value) inputArquivos.value.value = ''
}

function removerFoto(indice) {
  const item = fotos.value[indice]
  if (item?.previewUrl) URL.revokeObjectURL(item.previewUrl)
  fotos.value.splice(indice, 1)
  if (visualizadorAberto.value && visualizadorIndice.value >= fotos.value.length) {
    visualizadorIndice.value = Math.max(0, fotos.value.length - 1)
    if (!fotos.value.length) fecharVisualizador()
  }
}

function abrirVisualizador(indice) {
  visualizadorIndice.value = indice
  visualizadorAberto.value = true
}

function fecharVisualizador() {
  visualizadorAberto.value = false
}

function fotoAnterior() {
  visualizadorIndice.value =
    (visualizadorIndice.value - 1 + fotos.value.length) % fotos.value.length
}

function proximaFoto() {
  visualizadorIndice.value = (visualizadorIndice.value + 1) % fotos.value.length
}

async function enviar() {
  pararDitado()
  if (!podeEnviar.value) return
  enviando.value = true
  erroEnvio.value = null
  try {
    const formData = new FormData()
    fotos.value.forEach((item) => {
      formData.append('anexos', item.file)
    })
    if (descricao.value.trim()) {
      formData.append('descricao', descricao.value.trim())
    }
    await axios.post(`${baseURL}/publico/evidencias/${token}`, formData, {
      timeout: 120000,
      headers: { Accept: 'application/json' }
    })
    sucesso.value = true
  } catch (e) {
    erroEnvio.value = getApiErrorMessage(
      e,
      'Não foi possível enviar. Verifique o link ou tente novamente.'
    )
  } finally {
    enviando.value = false
  }
}

onBeforeUnmount(() => {
  fotos.value.forEach((f) => {
    if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
  })
  pararDitado()
})
</script>

<style scoped>
.safe-top {
  padding-top: max(1.25rem, env(safe-area-inset-top));
}
.safe-bottom {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
</style>
