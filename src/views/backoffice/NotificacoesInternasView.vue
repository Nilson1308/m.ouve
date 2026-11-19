<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <header class="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <BellAlertIcon class="w-8 h-8 text-primary-500" />
              Notificações internas
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Despachos, formalizações e alertas operacionais do backoffice
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium
                     bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200
                     border border-gray-300 dark:border-gray-600
                     hover:border-primary-500 hover:text-primary-500
                     transition-all duration-200 disabled:opacity-50"
              :disabled="store.loading"
              @click="recarregar"
            >
              <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': store.loading }" />
              Atualizar
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200
                     bg-primary-600 text-white shadow-button hover:bg-primary-700
                     disabled:opacity-50 disabled:pointer-events-none"
              :disabled="!store.temNaoLidas || store.loading"
              @click="marcarTodas"
            >
              <CheckIcon class="w-5 h-5" />
              Marcar todas como lidas
            </button>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2" role="tablist" aria-label="Filtrar notificações">
          <button
            v-for="tab in filtros"
            :key="tab.id"
            type="button"
            role="tab"
            :aria-selected="filtroAtivo === tab.id"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200"
            :class="
              filtroAtivo === tab.id
                ? 'bg-primary-600 text-white shadow-button'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 hover:border-primary-500 hover:text-primary-500'
            "
            @click="aplicarFiltro(tab.id)"
          >
            {{ tab.label }}
            <span
              v-if="tab.id === 'nao_lidas' && store.naoLidas > 0"
              class="badge bg-white text-danger-600"
            >
              {{ store.naoLidas }}
            </span>
          </button>
        </div>
      </div>
    </header>

    <main class="px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <!-- KPIs -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div class="card border-2 border-primary-200 dark:border-primary-800 shadow-card">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Não lidas</p>
          <p class="text-3xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ store.naoLidas }}
          </p>
        </div>
        <div class="card shadow-card">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Nesta lista</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ itensExibidos.length }}</p>
        </div>
        <div class="card shadow-card">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Última sync</p>
          <p class="text-sm font-semibold text-gray-800 dark:text-gray-200 mt-2">
            {{ ultimaSyncLabel }}
          </p>
        </div>
      </div>

      <div class="alert-info">
        <InformationCircleIcon class="w-5 h-5 shrink-0" />
        <p class="text-sm">
          Notificações são geradas ao <strong>despachar protocolos</strong> (scatter) e ao
          <strong>formalizar ordens de serviço</strong> (gather). Use os links para ir direto à ação.
        </p>
      </div>

      <p v-if="store.erro" class="text-sm text-red-600 dark:text-red-400">{{ store.erro }}</p>

      <!-- Loading -->
      <div v-if="store.loading && !store.items.length" class="card py-20 text-center">
        <div class="inline-block h-10 w-10 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-4">Carregando notificações…</p>
      </div>

      <!-- Empty -->
      <div v-else-if="!itensExibidos.length" class="card py-16 text-center">
        <InboxIcon class="w-14 h-14 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-lg font-semibold text-gray-800 dark:text-gray-200">
          {{ emptyTitle }}
        </p>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
          {{ emptySubtitle }}
        </p>
        <button
          v-if="filtroAtivo !== 'todas'"
          type="button"
          class="btn-secondary mt-6"
          @click="aplicarFiltro('todas')"
        >
          Ver todas
        </button>
      </div>

      <!-- Lista -->
      <ul v-else class="space-y-3">
        <li
          v-for="item in itensExibidos"
          :key="item.id"
          class="card transition-all duration-200 hover:shadow-card-hover border-l-4"
          :class="
            item.lida
              ? 'border-l-gray-200 dark:border-l-gray-600 opacity-90'
              : 'border-l-primary-500 bg-primary-50/30 dark:bg-primary-900/10'
          "
        >
          <div class="flex flex-col sm:flex-row sm:items-start gap-4">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
              :class="item.lida ? 'bg-gray-100 dark:bg-gray-700' : 'bg-primary-100 dark:bg-primary-900/50'"
            >
              <BellIcon
                class="w-5 h-5"
                :class="item.lida ? 'text-gray-500' : 'text-primary-600 dark:text-primary-400'"
              />
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1">
                <h2 class="text-base font-semibold text-gray-900 dark:text-white">
                  {{ item.titulo }}
                </h2>
                <span
                  v-if="!item.lida"
                  class="inline-flex px-2 py-0.5 rounded-badge text-xs font-semibold bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200"
                >
                  Nova
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap leading-relaxed">
                {{ item.mensagem }}
              </p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-2 flex items-center gap-1">
                <ClockIcon class="w-3.5 h-3.5" />
                {{ formatarQuando(item.dataCriacao) }}
              </p>
            </div>

            <div class="flex sm:flex-col gap-2 shrink-0">
              <button
                v-if="item.linkAcao"
                type="button"
                class="btn-primary text-sm py-2 px-3 flex items-center justify-center gap-1.5"
                @click="abrirAcao(item)"
              >
                <ArrowTopRightOnSquareIcon class="w-4 h-4" />
                Abrir
              </button>
              <button
                v-if="!item.lida"
                type="button"
                class="btn-secondary text-sm py-2 px-3"
                :disabled="marcandoId === item.id"
                @click="marcarUma(item)"
              >
                {{ marcandoId === item.id ? '…' : 'Marcar lida' }}
              </button>
            </div>
          </div>
        </li>
      </ul>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  BellAlertIcon,
  BellIcon,
  ArrowPathIcon,
  CheckIcon,
  InformationCircleIcon,
  InboxIcon,
  ClockIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import { formatarQuandoNotificacao, rotaInternaNotificacao } from '@/utils/notificacaoLink'

const store = useNotificacoesInternasStore()
const { items, ultimaAtualizacao } = storeToRefs(store)
const router = useRouter()

const filtroAtivo = ref('todas')
const marcandoId = ref(null)
const cacheLocal = ref([])

const filtros = [
  { id: 'todas', label: 'Todas' },
  { id: 'nao_lidas', label: 'Não lidas' },
  { id: 'lidas', label: 'Lidas' }
]

const itensExibidos = computed(() => {
  const lista = filtroAtivo.value === 'nao_lidas' ? cacheLocal.value : items.value
  if (filtroAtivo.value === 'lidas') {
    return items.value.filter((n) => n.lida)
  }
  if (filtroAtivo.value === 'nao_lidas') {
    return lista.filter((n) => !n.lida)
  }
  return items.value
})

const emptyTitle = computed(() => {
  if (filtroAtivo.value === 'nao_lidas') return 'Tudo em dia'
  if (filtroAtivo.value === 'lidas') return 'Nenhuma notificação lida ainda'
  return 'Nenhuma notificação'
})

const emptySubtitle = computed(() => {
  if (filtroAtivo.value === 'nao_lidas') {
    return 'Você não tem alertas pendentes no momento.'
  }
  if (filtroAtivo.value === 'lidas') {
    return 'As notificações marcadas como lidas aparecerão aqui.'
  }
  return 'Quando houver despachos ou formalizações, os avisos serão listados aqui.'
})

const ultimaSyncLabel = computed(() => {
  if (!ultimaAtualizacao.value) return '—'
  return formatarQuandoNotificacao(ultimaAtualizacao.value)
})

function formatarQuando(iso) {
  return formatarQuandoNotificacao(iso)
}

async function recarregar() {
  await carregarComFiltroAtual()
}

async function carregarComFiltroAtual() {
  try {
    if (filtroAtivo.value === 'nao_lidas') {
      await store.carregar({ limit: 200, apenasNaoLidas: true })
      cacheLocal.value = [...items.value]
    } else {
      await store.carregar({ limit: 200 })
      cacheLocal.value = []
    }
  } catch {
    /* erro no store */
  }
}

async function aplicarFiltro(id) {
  filtroAtivo.value = id
  await carregarComFiltroAtual()
}

async function marcarUma(item) {
  marcandoId.value = item.id
  try {
    await store.marcarLida(item.id)
  } finally {
    marcandoId.value = null
  }
}

async function marcarTodas() {
  await store.marcarTodasLidasVisiveis()
  await carregarComFiltroAtual()
}

async function abrirAcao(item) {
  if (!item.lida) {
    try {
      await store.marcarLida(item.id)
    } catch {
      /* segue */
    }
  }
  const rota = rotaInternaNotificacao(item.linkAcao)
  if (rota) {
    router.push(rota)
  } else if (item.linkAcao) {
    window.location.href = item.linkAcao
  }
}

onMounted(() => {
  carregarComFiltroAtual()
})
</script>
