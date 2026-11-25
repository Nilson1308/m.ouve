<template>
  <div
    class="min-h-screen flex flex-col bg-stone-100 text-slate-950"
    :class="{ 'bg-emerald-600 text-white': sucesso }"
  >
    <div
      v-if="carregando"
      class="min-h-screen flex flex-col items-center justify-center gap-4 px-6"
    >
      <div
        class="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"
        aria-hidden="true"
      />
      <p class="text-lg font-semibold text-slate-800">Carregando ordem de serviço…</p>
    </div>

    <div
      v-else-if="estadoErro"
      class="min-h-screen flex flex-col items-center justify-center px-6 text-center safe-top safe-bottom"
    >
      <header class="absolute top-0 left-0 right-0 px-4 py-4 border-b border-stone-300 bg-white">
        <img :src="BRAND.logos.light" :alt="BRAND.name" class="h-9 w-auto mx-auto" />
      </header>
      <div class="max-w-md mt-16">
        <p class="text-5xl mb-4" aria-hidden="true">{{ estadoErro === 'expirado' ? '⏱️' : '🔗' }}</p>
        <h1 class="text-2xl font-bold text-slate-900 mb-3">
          {{ estadoErro === 'expirado' ? 'Link indisponível' : 'Link não encontrado' }}
        </h1>
        <p class="text-base text-slate-700 leading-relaxed">{{ mensagemEstadoErro }}</p>
      </div>
    </div>

    <div
      v-else-if="sucesso"
      class="flex-1 flex flex-col items-center justify-center text-center px-6"
    >
      <CheckCircleIcon class="w-24 h-24 text-white mb-6" />
      <h1 class="text-2xl font-bold leading-snug mb-3">Evidências enviadas com sucesso!</h1>
      <p class="text-lg text-emerald-50">Você já pode fechar esta tela.</p>
    </div>

    <template v-else-if="contexto">
      <header class="px-4 py-4 border-b-2 border-stone-300 bg-white shadow-sm safe-top sticky top-0 z-20">
        <div class="max-w-lg mx-auto flex items-center justify-between gap-3">
          <img :src="BRAND.logos.light" :alt="BRAND.name" class="h-9 w-auto" />
          <span class="text-xs font-bold uppercase tracking-wide text-amber-800 bg-amber-100 px-2 py-1 rounded">
            Campo
          </span>
        </div>
      </header>

      <main class="flex-1 max-w-lg mx-auto w-full px-4 py-5 pb-32 space-y-5">
        <section class="rounded-2xl border-2 border-slate-800 bg-white shadow-md p-4 space-y-4">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Protocolo</p>
            <h1 class="text-2xl font-black text-slate-950 leading-tight">
              {{ contexto.numero_protocolo }}
            </h1>
          </div>
          <dl class="grid grid-cols-1 gap-3 text-sm">
            <div>
              <dt class="text-xs font-bold uppercase text-slate-500">Serviço</dt>
              <dd class="font-semibold text-slate-900">{{ contexto.servico_nome || '—' }}</dd>
            </div>
            <div>
              <dt class="text-xs font-bold uppercase text-slate-500">Secretaria</dt>
              <dd class="font-semibold text-slate-900">{{ contexto.unidade_nome || '—' }}</dd>
            </div>
            <div v-if="contexto.prazo_sla">
              <dt class="text-xs font-bold uppercase text-slate-500">Prazo SLA</dt>
              <dd class="font-bold text-red-800">{{ formatarDataHora(contexto.prazo_sla) }}</dd>
            </div>
          </dl>
        </section>

        <section class="rounded-2xl border-2 border-slate-300 bg-white p-4 space-y-3">
          <h2 class="text-lg font-bold text-slate-950 flex items-center gap-2">
            <MapPinIcon class="w-6 h-6 text-red-600" />
            Local da ocorrência
          </h2>
          <div v-if="contexto.equipamento" class="rounded-xl bg-slate-100 border border-slate-300 p-3 text-sm">
            <p class="font-bold text-slate-900">{{ contexto.equipamento.nome }}</p>
            <p class="text-slate-700">{{ labelTipoEquipamento(contexto.equipamento.tipo) }}</p>
            <p v-if="contexto.equipamento.bairro" class="text-slate-600">{{ contexto.equipamento.bairro }}</p>
          </div>
          <p class="text-base font-medium text-slate-900 leading-snug">{{ enderecoExibicao }}</p>
          <div class="flex flex-col sm:flex-row gap-2">
            <a
              v-if="linksNavegacao.maps"
              :href="linksNavegacao.maps"
              target="_blank"
              rel="noopener noreferrer"
              class="flex-1 min-h-[44px] inline-flex items-center justify-center gap-2 rounded-xl font-bold text-sm bg-blue-600 text-white active:bg-blue-800 touch-manipulation"
            >
              Abrir no Google Maps
            </a>
            <a
              v-if="linksNavegacao.waze"
              :href="linksNavegacao.waze"
              target="_blank"
              rel="noopener noreferrer"
              class="flex-1 min-h-[44px] inline-flex items-center justify-center gap-2 rounded-xl font-bold text-sm bg-cyan-600 text-white active:bg-cyan-800 touch-manipulation"
            >
              Abrir no Waze
            </a>
          </div>
        </section>

        <section class="rounded-2xl border-2 border-slate-300 bg-white p-4 space-y-3">
          <h2 class="text-lg font-bold text-slate-950">O que fazer</h2>
          <div>
            <p class="text-xs font-bold uppercase text-slate-500 mb-1">Descrição da solicitação</p>
            <p class="text-sm text-slate-900 whitespace-pre-line leading-relaxed">
              {{ contexto.descricao_solicitacao || '—' }}
            </p>
          </div>
          <div
            v-if="contexto.instrucoes_despacho"
            class="rounded-xl border-2 border-amber-500 bg-amber-50 p-3"
          >
            <p class="text-xs font-black uppercase text-amber-900 mb-1">Instruções do despacho</p>
            <p class="text-sm font-medium text-amber-950 whitespace-pre-line leading-relaxed">
              {{ contexto.instrucoes_despacho }}
            </p>
          </div>
          <div
            v-if="contexto.motivo_reabertura"
            class="rounded-xl border-2 border-violet-500 bg-violet-50 p-3"
          >
            <p class="text-xs font-black uppercase text-violet-900 mb-1">Retrabalho — motivo da reabertura</p>
            <p class="text-sm text-violet-950 whitespace-pre-line">{{ contexto.motivo_reabertura }}</p>
            <div v-if="contexto.reabertura_anexos?.length" class="grid grid-cols-3 gap-2 mt-3">
              <button
                v-for="(item, idx) in contexto.reabertura_anexos"
                :key="item.id || idx"
                type="button"
                class="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-400 min-h-[44px]"
                @click="abrirLightbox(contexto.reabertura_anexos, idx)"
              >
                <img :src="item.url" :alt="item.nome" class="w-full h-full object-cover" loading="lazy" />
              </button>
            </div>
          </div>
        </section>

        <section
          v-if="contexto.anexos_iniciais?.length"
          class="rounded-2xl border-2 border-slate-300 bg-white p-4"
        >
          <h2 class="text-lg font-bold text-slate-950 mb-3">Fotos de referência (abertura)</h2>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="(item, idx) in contexto.anexos_iniciais"
              :key="item.id || idx"
              type="button"
              class="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-400 min-h-[44px]"
              @click="abrirLightbox(contexto.anexos_iniciais, idx)"
            >
              <img :src="item.url" :alt="item.nome" class="w-full h-full object-cover" loading="lazy" />
            </button>
          </div>
        </section>

        <section
          v-if="contexto.diligencias?.length"
          class="rounded-2xl border-2 border-indigo-500 bg-indigo-50/80 p-4 space-y-4"
        >
          <h2 class="text-lg font-black text-indigo-950">Complementações / Diligências do Cidadão</h2>
          <article
            v-for="d in contexto.diligencias"
            :key="d.id"
            class="rounded-xl bg-white border border-indigo-200 p-3 space-y-2"
          >
            <p class="text-xs font-bold uppercase text-indigo-700">{{ d.status }}</p>
            <p class="text-sm font-semibold text-slate-900">
              <span class="text-slate-500 font-normal">Pergunta:</span> {{ d.pergunta }}
            </p>
            <p v-if="d.resposta_cidadao" class="text-sm text-slate-800">
              <span class="font-semibold">Resposta:</span> {{ d.resposta_cidadao }}
            </p>
            <div v-if="d.anexos?.length" class="grid grid-cols-3 gap-2">
              <button
                v-for="(anexo, idx) in d.anexos"
                :key="anexo.id || idx"
                type="button"
                class="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-400 min-h-[44px]"
                @click="abrirLightbox(d.anexos, idx)"
              >
                <img :src="anexo.url" :alt="anexo.nome" class="w-full h-full object-cover" loading="lazy" />
              </button>
            </div>
          </article>
        </section>

        <section
          v-if="contexto.evidencias_campo_enviadas?.length"
          class="rounded-2xl border-2 border-emerald-400 bg-emerald-50 p-4"
        >
          <h2 class="text-lg font-bold text-emerald-950 mb-2">Já enviado por este link</h2>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="(item, idx) in contexto.evidencias_campo_enviadas"
              :key="item.id || idx"
              type="button"
              class="relative aspect-square rounded-lg overflow-hidden border-2 border-slate-400 min-h-[44px]"
              @click="abrirLightbox(contexto.evidencias_campo_enviadas, idx)"
            >
              <img :src="item.url" :alt="item.nome" class="w-full h-full object-cover" loading="lazy" />
            </button>
          </div>
        </section>

        <section class="rounded-2xl border-2 border-dashed border-slate-400 bg-slate-50 p-4">
          <h2 class="text-xl font-bold text-slate-950 mb-1">Enviar novas evidências</h2>
          <p class="text-sm text-slate-600 mb-4">Fotografe o serviço executado e descreva o que foi feito.</p>

          <p
            v-if="erroEnvio"
            class="mb-4 p-3 rounded-xl bg-red-100 border-2 border-red-500 text-sm text-red-900"
          >
            {{ erroEnvio }}
          </p>

          <label
            class="flex flex-col items-center justify-center gap-3 min-h-[120px] border-2 border-dashed border-slate-500 rounded-2xl bg-white active:bg-stone-100 cursor-pointer mb-4 touch-manipulation"
          >
            <span class="text-4xl" aria-hidden="true">📷</span>
            <span class="text-base font-bold text-center px-4 text-slate-900">Tirar / escolher fotos</span>
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

          <section v-if="fotos.length" class="mb-4">
            <p class="text-sm font-bold text-slate-800 mb-2">Pré-visualização ({{ fotos.length }})</p>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="(item, idx) in fotos"
                :key="item.id"
                type="button"
                class="relative aspect-square rounded-xl overflow-hidden border-2 border-slate-600 min-h-[44px]"
                @click="abrirVisualizadorLocal(idx)"
              >
                <img :src="item.previewUrl" :alt="item.file.name" class="w-full h-full object-cover" />
                <span
                  class="absolute top-1 right-1 w-8 h-8 rounded-full bg-black/75 text-white text-lg flex items-center justify-center"
                  @click.stop="removerFoto(idx)"
                >
                  ×
                </span>
              </button>
            </div>
          </section>

          <section class="mb-2">
            <div class="flex items-center justify-between gap-2 mb-2">
              <label class="text-sm font-bold text-slate-800">Descrição do serviço</label>
              <button
                v-if="ditadoSuportado"
                type="button"
                class="min-h-[44px] px-4 rounded-xl font-bold text-sm flex items-center gap-2 touch-manipulation"
                :class="
                  ditadoOuvindo
                    ? 'bg-red-600 text-white'
                    : 'bg-slate-200 text-slate-900 border-2 border-slate-500'
                "
                @click="alternarDitado"
              >
                <MicrophoneIcon class="w-5 h-5" />
                {{ ditadoOuvindo ? 'Parar' : 'Ditar' }}
              </button>
            </div>
            <textarea
              v-model="descricao"
              rows="4"
              class="w-full rounded-xl border-2 border-slate-500 bg-white text-slate-900 text-base px-4 py-3 focus:border-amber-500 focus:ring-0"
              placeholder="Descreva o que foi executado…"
            />
          </section>
        </section>
      </main>

      <footer class="fixed bottom-0 left-0 right-0 p-4 bg-white/95 border-t-2 border-slate-300 safe-bottom z-20">
        <div class="max-w-lg mx-auto">
          <button
            type="button"
            class="w-full min-h-[56px] text-lg font-black rounded-2xl bg-amber-400 text-slate-950 border-2 border-slate-900 shadow-lg active:scale-[0.98] disabled:opacity-50 touch-manipulation"
            :disabled="enviando || !podeEnviar"
            @click="enviar"
          >
            {{ enviando ? 'Enviando…' : 'Enviar evidências' }}
          </button>
        </div>
      </footer>
    </template>

    <Teleport to="body">
      <div
        v-if="lightboxAberto"
        class="fixed inset-0 z-[100] bg-black/95 flex flex-col"
        role="dialog"
        aria-modal="true"
        @click.self="fecharLightbox"
      >
        <p class="sr-only">{{ lightboxTitulo }}</p>
        <div class="flex items-center justify-between p-4 text-white safe-top">
          <span class="text-sm font-medium">{{ lightboxIndice + 1 }} / {{ lightboxLista.length }}</span>
          <button type="button" class="text-3xl font-bold px-3 min-h-[44px]" @click="fecharLightbox">×</button>
        </div>
        <div class="flex-1 flex items-center justify-center px-4 pb-8">
          <img
            :src="lightboxLista[lightboxIndice]?.url"
            :alt="lightboxLista[lightboxIndice]?.nome || 'Imagem'"
            class="max-w-full max-h-full object-contain"
          />
        </div>
        <div v-if="lightboxLista.length > 1" class="flex justify-center gap-4 pb-8 safe-bottom">
          <button
            type="button"
            class="min-h-[44px] px-6 py-3 rounded-xl bg-white/20 font-semibold text-white"
            @click="lightboxAnterior"
          >
            Anterior
          </button>
          <button
            type="button"
            class="min-h-[44px] px-6 py-3 rounded-xl bg-amber-400 text-slate-900 font-bold"
            @click="lightboxProxima"
          >
            Próxima
          </button>
        </div>
      </div>

      <div
        v-if="visualizadorAberto"
        class="fixed inset-0 z-[100] bg-black/95 flex flex-col"
        @click.self="fecharVisualizador"
      >
        <div class="flex-1 flex items-center justify-center px-4">
          <img
            :src="fotos[visualizadorIndice]?.previewUrl"
            alt="Pré-visualização"
            class="max-w-full max-h-full object-contain"
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { CheckCircleIcon, MicrophoneIcon, MapPinIcon } from '@heroicons/vue/24/solid'
import axios from 'axios'
import { BRAND } from '@/constants/brand'
import { getApiErrorMessage } from '@/utils/apiError'
import { useSpeechDictation } from '@/composables/useSpeechDictation'
import { labelTipoEquipamento } from '@/constants/equipamentosPublicos'

const route = useRoute()
const token = route.params.token

const contexto = ref(null)
const carregando = ref(true)
const estadoErro = ref(null)
const mensagemEstadoErro = ref('')

const fotos = ref([])
const descricao = ref('')
const enviando = ref(false)
const sucesso = ref(false)
const erroEnvio = ref(null)
const inputArquivos = ref(null)

const visualizadorAberto = ref(false)
const visualizadorIndice = ref(0)

const lightboxAberto = ref(false)
const lightboxLista = ref([])
const lightboxIndice = ref(0)
const lightboxTitulo = 'Galeria de imagens'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

let idSequencial = 0

const podeEnviar = computed(
  () => fotos.value.length > 0 || descricao.value.trim().length > 0
)

const enderecoExibicao = computed(() => {
  if (!contexto.value) return 'Endereço não informado'
  const partes = [contexto.value.endereco_texto, contexto.value.bairro].filter(Boolean)
  return partes.length ? partes.join(' · ') : 'Endereço não informado'
})

const linksNavegacao = computed(() => {
  const ctx = contexto.value
  if (!ctx) return { maps: '', waze: '' }
  const lat = ctx.latitude ?? ctx.equipamento?.latitude
  const lng = ctx.longitude ?? ctx.equipamento?.longitude
  if (lat != null && lng != null && Number.isFinite(Number(lat)) && Number.isFinite(Number(lng))) {
    const q = `${lat},${lng}`
    return {
      maps: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`,
      waze: `https://waze.com/ul?ll=${lat},${lng}&navigate=yes`
    }
  }
  const end = enderecoExibicao.value
  if (end && end !== 'Endereço não informado') {
    return {
      maps: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(end)}`,
      waze: `https://waze.com/ul?q=${encodeURIComponent(end)}&navigate=yes`
    }
  }
  return { maps: '', waze: '' }
})

function formatarDataHora(iso) {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(
      new Date(iso)
    )
  } catch {
    return iso
  }
}

async function carregarContexto() {
  carregando.value = true
  estadoErro.value = null
  try {
    const { data } = await axios.get(`${baseURL}/publico/evidencias/${token}`, {
      timeout: 60000,
      headers: { Accept: 'application/json' }
    })
    contexto.value = data
  } catch (e) {
    const status = e?.response?.status
    if (status === 404) {
      estadoErro.value = 'invalido'
      mensagemEstadoErro.value =
        'Este link não existe ou já foi substituído. Peça à secretaria um novo link mágico.'
    } else if (status === 410) {
      estadoErro.value = 'expirado'
      mensagemEstadoErro.value = getApiErrorMessage(
        e,
        'Este link expirou ou a ordem de serviço já foi concluída/formalizada.'
      )
    } else {
      estadoErro.value = 'invalido'
      mensagemEstadoErro.value = getApiErrorMessage(
        e,
        'Não foi possível carregar esta ordem de serviço. Verifique a conexão e tente de novo.'
      )
    }
  } finally {
    carregando.value = false
  }
}

function acrescentarTextoDitado(texto) {
  const atual = descricao.value.trim()
  descricao.value = atual ? `${atual} ${texto}` : texto
}

const {
  suportado: ditadoSuportado,
  ouvindo: ditadoOuvindo,
  alternar: alternarDitado,
  parar: pararDitado
} = useSpeechDictation({ onFinalText: acrescentarTextoDitado, lang: 'pt-BR' })

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
}

function abrirVisualizadorLocal(indice) {
  visualizadorIndice.value = indice
  visualizadorAberto.value = true
}

function fecharVisualizador() {
  visualizadorAberto.value = false
}

function abrirLightbox(lista, indice = 0) {
  lightboxLista.value = (lista || []).filter((i) => i?.url)
  lightboxIndice.value = indice
  lightboxAberto.value = true
}

function fecharLightbox() {
  lightboxAberto.value = false
}

function lightboxAnterior() {
  const n = lightboxLista.value.length
  lightboxIndice.value = (lightboxIndice.value - 1 + n) % n
}

function lightboxProxima() {
  const n = lightboxLista.value.length
  lightboxIndice.value = (lightboxIndice.value + 1) % n
}

async function enviar() {
  pararDitado()
  if (!podeEnviar.value) return
  enviando.value = true
  erroEnvio.value = null
  try {
    const formData = new FormData()
    fotos.value.forEach((item) => formData.append('anexos', item.file))
    if (descricao.value.trim()) formData.append('descricao', descricao.value.trim())
    await axios.post(`${baseURL}/publico/evidencias/${token}`, formData, {
      timeout: 120000,
      headers: { Accept: 'application/json' }
    })
    fotos.value.forEach((f) => {
      if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
    })
    fotos.value = []
    descricao.value = ''
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

onMounted(() => {
  carregarContexto()
})

onBeforeUnmount(() => {
  fotos.value.forEach((f) => {
    if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
  })
  pararDitado()
})
</script>

<style scoped>
.safe-top {
  padding-top: max(1rem, env(safe-area-inset-top));
}
.safe-bottom {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
</style>