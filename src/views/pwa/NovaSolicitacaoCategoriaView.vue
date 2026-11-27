<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 high-contrast:from-black high-contrast:to-black">
    <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft safe-area-inset-top">
      <div class="px-6 py-4 safe-area-inset flex items-center gap-4">
        <button type="button" class="btn-icon min-h-[44px] min-w-[44px]" aria-label="Voltar para categorias" @click="voltarCategorias">
          <ChevronLeftIcon class="w-6 h-6" aria-hidden="true" />
        </button>
        <div class="flex-1 min-w-0">
          <h1 class="text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 truncate">
            {{ tituloCategoria }}
          </h1>
          <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
            Escolha como registrar seu atendimento
          </p>
        </div>
        <PwaA11yMenu />
        <ThemeToggle surface="light" />
      </div>
    </header>

    <main id="conteudo-principal" tabindex="-1" class="px-6 py-6 pb-24 space-y-6 animate-fade-in motion-reduce:animate-none">
      <div v-if="carregando" class="py-16 text-center" role="status" aria-live="polite">
        <div class="animate-spin motion-reduce:animate-none rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent mx-auto mb-3" aria-hidden="true" />
        <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">Carregando serviços...</p>
      </div>

      <template v-else>
        <section
          v-if="modoHibrido"
          class="card bg-gradient-to-br from-primary-500 to-primary-700 dark:from-primary-700 dark:to-primary-900 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 border-0 text-white high-contrast:text-white p-5"
          aria-labelledby="titulo-assistente-ia"
        >
          <h2 id="titulo-assistente-ia" class="text-base font-bold mb-2 high-contrast:text-yellow-300">
            Prefere apenas contar o problema?
          </h2>
          <p class="text-sm text-primary-50 high-contrast:text-white high-contrast:font-bold mb-4 leading-relaxed">
            O Assistente IA identifica o serviço certo para você conversando em linguagem natural.
          </p>
          <button
            type="button"
            class="w-full min-h-[44px] px-4 py-3 rounded-xl font-semibold bg-white text-primary-700 hover:bg-primary-50 active:bg-primary-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white high-contrast:bg-yellow-300 high-contrast:text-black high-contrast:hover:bg-yellow-200 high-contrast:focus-visible:outline-yellow-300 transition-colors"
            @click="abrirChatAssistente()"
          >
            Descrever com o Assistente IA
          </button>
        </section>

        <p
          v-if="modoHibrido"
          class="text-center text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 high-contrast:text-yellow-300"
          role="separator"
        >
          Ou escolha o serviço diretamente
        </p>

        <div class="space-y-3">
          <label for="busca-servicos-pwa" class="sr-only">Buscar serviço nesta categoria</label>
          <div class="relative">
            <MagnifyingGlassIcon class="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" aria-hidden="true" />
            <input
              id="busca-servicos-pwa"
              v-model="buscaInput"
              type="search"
              autocomplete="off"
              class="input w-full pl-10 pr-11 min-h-[44px]"
              placeholder="Buscar serviço..."
              @input="onBuscaInput"
            />
            <button
              v-if="buscaInput.trim()"
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 min-h-[36px] min-w-[36px] rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary-500"
              aria-label="Limpar busca"
              @click="limparBusca"
            >
              <XMarkIcon class="w-5 h-5 mx-auto" aria-hidden="true" />
            </button>
          </div>
          <p class="sr-only" aria-live="polite" aria-atomic="true">{{ anuncioBusca }}</p>
        </div>

        <ul v-if="servicosFiltrados.length" class="space-y-3" role="list">
          <li v-for="svc in servicosFiltrados" :key="svc.id">
            <button
              type="button"
              class="card card-interactive w-full text-left p-4 min-h-[44px] flex items-center gap-3 group focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 high-contrast:focus-visible:outline-yellow-300"
              :aria-label="`Abrir atendimento: ${svc.nome}`"
              @click="abrirServico(svc.id)"
            >
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300 truncate">
                  {{ svc.nome }}
                </p>
                <p v-if="svc.descricao_curta" class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white line-clamp-2 mt-0.5">
                  {{ svc.descricao_curta }}
                </p>
              </div>
              <ChevronRightIcon class="w-5 h-5 shrink-0 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 group-hover:translate-x-0.5 transition-transform motion-reduce:transition-none" aria-hidden="true" />
            </button>
          </li>
        </ul>

        <div v-else class="card text-center py-10 px-4">
          <p class="text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white high-contrast:font-bold mb-4">
            Nenhum serviço encontrado<span v-if="buscaDebounced"> para “{{ buscaDebounced }}”</span>.
          </p>
          <button
            v-if="modoHibrido"
            type="button"
            class="btn-primary min-h-[44px] w-full sm:w-auto"
            @click="abrirChatAssistente(buscaDebounced)"
          >
            Descrever para o Assistente IA
          </button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { catalogoService } from '@/services/api'
import { useCatalogoStore } from '@/stores/catalogo'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import PwaA11yMenu from '@/components/pwa/PwaA11yMenu.vue'
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const CHAT_RELATO_REDIRECT_KEY = 'ouve_chat_relato_redirect'

const route = useRoute()
const router = useRouter()
const catalogoStore = useCatalogoStore()

const categoriaSlug = computed(() => String(route.params.categoriaSlug || '').trim())
const modoAbertura = computed(
  () => catalogoStore.configPwa?.modo_abertura_pwa || 'hibrido'
)
const modoHibrido = computed(() => modoAbertura.value === 'hibrido')

const configCat = computed(() => catalogoStore.configCategoriaPorRef(categoriaSlug.value))
const tituloCategoria = computed(() => configCat.value?.nome || categoriaSlug.value.replace(/_/g, ' '))

const carregando = ref(true)
const servicos = ref([])
const buscaInput = ref('')
const buscaDebounced = ref('')
let debounceTimer = null

const servicosFiltrados = computed(() => servicos.value)

const anuncioBusca = computed(() => {
  if (carregando.value) return ''
  const n = servicosFiltrados.value.length
  if (buscaDebounced.value) {
    return `${n} serviço(s) encontrado(s) para ${buscaDebounced.value}`
  }
  return `${n} serviço(s) disponível(is)`
})

function onBuscaInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    buscaDebounced.value = buscaInput.value.trim()
    void carregarServicos()
  }, 250)
}

function limparBusca() {
  buscaInput.value = ''
  buscaDebounced.value = ''
  void carregarServicos()
}

async function carregarServicos() {
  carregando.value = true
  try {
    const data = await catalogoService.listPwaVisiveis({
      categoria: categoriaSlug.value,
      busca: buscaDebounced.value || undefined
    })
    servicos.value = Array.isArray(data?.servicos) ? data.servicos : []
  } catch (e) {
    console.error(e)
    servicos.value = []
  } finally {
    carregando.value = false
  }
}

function referenciaCategoriaChat() {
  return configCat.value?.slug || configCat.value?.nome || categoriaSlug.value
}

function abrirChatAssistente(textoInicial = '') {
  const ref = referenciaCategoriaChat()
  if (textoInicial?.trim()) {
    try {
      sessionStorage.setItem(
        CHAT_RELATO_REDIRECT_KEY,
        JSON.stringify({ categoria: ref, texto: textoInicial.trim() })
      )
    } catch {
      /* ignore */
    }
  }
  router.push({
    name: 'pwa-chat-solicitacao',
    params: { categoriaNome: ref }
  })
}

function abrirServico(servicoId) {
  router.push({
    name: 'pwa-chat-solicitacao',
    params: { categoriaNome: referenciaCategoriaChat() },
    query: { servico_id: servicoId }
  })
}

function voltarCategorias() {
  router.push({ name: 'pwa-nova-solicitacao' })
}

onMounted(async () => {
  if (!catalogoStore.configPwa) {
    await catalogoStore.carregarConfigPwa()
  }
  await carregarServicos()
})

onUnmounted(() => {
  clearTimeout(debounceTimer)
})

watch(categoriaSlug, () => {
  buscaInput.value = ''
  buscaDebounced.value = ''
  void carregarServicos()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>