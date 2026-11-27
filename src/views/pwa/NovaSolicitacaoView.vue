<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 high-contrast:from-black high-contrast:to-black">
    <!-- Header -->
    <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft safe-area-inset-top">
      <div class="px-6 py-4 safe-area-inset flex items-center gap-4">
        <button type="button" @click="voltar" class="btn-icon" aria-label="Voltar">
          <ChevronLeftIcon class="w-6 h-6" aria-hidden="true" />
        </button>
        <div class="flex-1 min-w-0">
          <h1 class="text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Nova Solicitação
          </h1>
          <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
            Escolha a categoria do atendimento
          </p>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <PwaA11yMenu />
          <ThemeToggle surface="light" />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main id="conteudo-principal" tabindex="-1" class="px-6 py-8 pb-24 animate-fade-in motion-reduce:animate-none">
      <!-- Loading State -->
      <div
        v-if="catalogoStore.loading"
        class="flex flex-col items-center justify-center py-20"
        role="status"
        aria-live="polite"
      >
        <div class="animate-spin motion-reduce:animate-none rounded-full h-16 w-16 border-4 border-primary-500 border-t-transparent mb-4" aria-hidden="true"></div>
        <p class="text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
          Carregando categorias...
        </p>
      </div>

      <!-- Error State -->
      <div v-else-if="catalogoStore.error" class="card text-center py-12 animate-scale-in">
        <ExclamationCircleIcon class="w-16 h-16 mx-auto text-red-500 mb-4" aria-hidden="true" />
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-2">
          Erro ao Carregar Categorias
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mb-6">
          {{ catalogoStore.error }}
        </p>
        <button type="button" @click="catalogoStore.carregarCatalogo()" class="btn-primary">
          <ArrowPathIcon class="w-5 h-5" aria-hidden="true" />
          Tentar Novamente
        </button>
      </div>

      <!-- Info Card (modo com assistente IA) -->
      <div
        v-if="exibirDestaqueIa"
        class="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/10 high-contrast:bg-transparent border-blue-200 dark:border-blue-800 high-contrast:border-yellow-300 mb-6 animate-slide-up"
      >
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 rounded-full flex items-center justify-center shadow-button">
            <SparklesIcon class="w-6 h-6 text-white high-contrast:text-black" aria-hidden="true" />
          </div>
          <div class="flex-1">
            <h2 class="font-bold text-blue-900 dark:text-blue-100 high-contrast:text-yellow-300 mb-1">
              Atendimento com IA Conversacional
            </h2>
            <p class="text-sm text-blue-800 dark:text-blue-200 high-contrast:text-white high-contrast:font-bold">
              Nossa assistente virtual vai conversar com você para entender e registrar sua solicitação de forma natural e rápida.
            </p>
          </div>
        </div>
      </div>

      <!-- Grid de Categorias -->
      <h2 v-if="!catalogoStore.loading && !catalogoStore.error && categorias.length" class="sr-only">
        Categorias de atendimento
      </h2>
      <div v-if="!catalogoStore.loading && !catalogoStore.error" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          v-for="categoria in categorias"
          :key="categoria.nome"
          type="button"
          @click="abrirCategoria(categoria)"
          class="group card card-interactive text-left p-6 min-h-[44px] hover:scale-105 active:scale-95 motion-reduce:hover:scale-100 motion-reduce:active:scale-100 transition-all animate-scale-in motion-reduce:animate-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 high-contrast:focus-visible:outline-yellow-300"
          :aria-label="rotuloAriaCategoria(categoria)"
        >
          <!-- Ícone da Categoria -->
          <div class="flex items-start gap-4 mb-4">
            <div
              class="flex-shrink-0 w-16 h-16 rounded-avatar flex items-center justify-center shadow-button transition-transform group-hover:scale-110"
              :class="categoria.iconClass"
            >
              <component :is="categoria.icon" class="w-8 h-8 text-white" aria-hidden="true" />
            </div>

            <div class="flex-1 min-w-0">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {{ categoria.nome }}
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mb-3 line-clamp-2">
                {{ categoria.descricao }}
              </p>

              <!-- Stats -->
              <div class="flex items-center gap-3 text-xs">
                <span class="inline-flex items-center gap-1 text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
                  <TagIcon class="w-4 h-4" aria-hidden="true" />
                  {{ categoria.quantidadeVisivel }} {{ categoria.quantidadeVisivel === 1 ? 'serviço' : 'serviços' }}
                </span>
                <span
                  v-if="categoria.rotuloModo"
                  class="inline-flex items-center gap-1 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 font-semibold"
                >
                  <component :is="categoria.iconeModo" class="w-4 h-4" aria-hidden="true" />
                  {{ categoria.rotuloModo }}
                </span>
              </div>
            </div>
          </div>

          <!-- Seta -->
          <div class="flex items-center justify-end">
            <div class="flex items-center gap-2 text-sm font-semibold text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300">
              <span>{{ categoria.cta }}</span>
              <ChevronRightIcon class="w-5 h-5 group-hover:translate-x-1 transition-transform motion-reduce:transition-none" aria-hidden="true" />
            </div>
          </div>
        </button>
      </div>

      <!-- Empty State -->
      <div v-if="!catalogoStore.loading && !catalogoStore.error && categorias.length === 0" class="card text-center py-12 animate-scale-in">
        <InboxIcon class="w-20 h-20 mx-auto text-gray-400 mb-4" aria-hidden="true" />
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-2">
          Nenhuma categoria disponível
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
          As categorias de atendimento estão temporariamente indisponíveis.
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogoStore } from '@/stores/catalogo'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import PwaA11yMenu from '@/components/pwa/PwaA11yMenu.vue'
import { componenteIconeCategoria, classeGradienteIconeCategoria } from '@/utils/catalogoIcones'
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  InboxIcon,
  SparklesIcon,
  TagIcon,
  ChatBubbleLeftEllipsisIcon,
  ListBulletIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const catalogoStore = useCatalogoStore()

const modoAbertura = computed(
  () => catalogoStore.configPwa?.modo_abertura_pwa || 'hibrido'
)
const exibirDestaqueIa = computed(
  () => modoAbertura.value === 'hibrido' || modoAbertura.value === 'chat_ia'
)

const categorias = computed(() => {
  const grupos = catalogoStore.servicosPorCategoria || []
  const modo = modoAbertura.value

  return grupos.map((grupo) => {
    const ref = grupo.slug || grupo.nome
    const cfg = catalogoStore.configCategoriaPorRef(ref)
    const qtdVisivel =
      cfg?.total_servicos_visiveis != null ? cfg.total_servicos_visiveis : grupo.servicos.length
  const catalogoGuiado = modo === 'catalogo_guiado'
    return {
      nome: grupo.nome,
      slug: cfg?.slug || grupo.slug || '',
      refChat: cfg?.slug || cfg?.nome || grupo.nome,
      servicoUnicoId: cfg?.servico_unico_id || null,
      quantidadeVisivel: qtdVisivel,
      descricao: (cfg?.descricao || grupo.descricao || '').trim() || 'Serviços públicos desta área',
      icon: componenteIconeCategoria(grupo.icone),
      iconClass: classeGradienteIconeCategoria(grupo.icone),
      rotuloModo: catalogoGuiado ? 'Lista de serviços' : 'Chat com IA',
      iconeModo: catalogoGuiado ? ListBulletIcon : ChatBubbleLeftEllipsisIcon,
      cta: catalogoGuiado ? 'Ver serviços' : 'Iniciar atendimento'
    }
  })
})

onMounted(async () => {
  await Promise.all([catalogoStore.carregarCatalogo(), catalogoStore.carregarConfigPwa()])
})

function rotuloAriaCategoria(categoria) {
  return `${categoria.cta} na categoria ${categoria.nome}. ${categoria.descricao}`
}

function irChat(categoria, servicoId = null) {
  const query = servicoId ? { servico_id: servicoId } : {}
  router.push({
    name: 'pwa-chat-solicitacao',
    params: { categoriaNome: categoria.refChat },
    query
  })
}

function abrirCategoria(categoria) {
  const modo = modoAbertura.value
  if (modo === 'chat_ia') {
    irChat(categoria)
    return
  }
  if (categoria.servicoUnicoId && categoria.quantidadeVisivel === 1) {
    irChat(categoria, categoria.servicoUnicoId)
    return
  }
  const slug = categoria.slug || categoria.refChat
  router.push({
    name: 'pwa-nova-solicitacao-categoria',
    params: { categoriaSlug: slug }
  })
}

function voltar() {
  router.push('/app/dashboard')
}

</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>