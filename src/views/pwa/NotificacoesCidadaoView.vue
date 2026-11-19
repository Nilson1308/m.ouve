<template>
  <div class="min-h-screen pb-20">
    <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 border-b border-gray-200/50 dark:border-gray-800/50 safe-area-inset">
      <div class="px-4 sm:px-6 py-3 flex items-center gap-2">
        <button type="button" class="btn-icon shrink-0 min-h-[44px] min-w-[44px]" aria-label="Voltar" @click="voltar">
          <ChevronLeftIcon class="w-5 h-5" aria-hidden="true" />
        </button>
        <h1 class="text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
          Notificações
        </h1>
      </div>
    </header>

    <main id="conteudo-principal" tabindex="-1" class="px-4 sm:px-6 py-6 max-w-2xl mx-auto space-y-5">
      <PwaWebPushNudge
        heading-suffix="central"
        @ativado="onPushAtivado"
        @erro="onPushErro"
      />

      <div v-if="store.loading && !store.items.length" class="py-12 text-center text-sm text-gray-500" role="status">
        Carregando notificações…
      </div>

      <ul v-else-if="store.items.length" class="space-y-3" role="list">
        <li
          v-for="item in store.items"
          :key="item.id"
          role="listitem"
          class="card p-0 overflow-hidden"
        >
          <button
            type="button"
            class="w-full text-left p-4 min-h-[44px] hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors motion-reduce:transition-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            :class="{ 'border-l-4 border-primary-500 high-contrast:border-yellow-300': !item.lida }"
            @click="abrirItem(item)"
          >
            <p class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
              {{ item.titulo }}
            </p>
            <p class="text-sm text-gray-700 dark:text-gray-300 mt-1 leading-relaxed">
              {{ item.mensagem }}
            </p>
            <time
              :datetime="item.dataCriacao || undefined"
              class="text-xs text-gray-500 dark:text-gray-400 mt-2 block"
            >
              {{ formatarQuando(item.dataCriacao) }}
            </time>
          </button>
        </li>
      </ul>

      <div v-else class="card text-center py-12">
        <BellIcon class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" aria-hidden="true" />
        <p class="text-sm text-gray-600 dark:text-gray-400">Você não tem notificações ainda.</p>
      </div>

      <p class="sr-only" aria-live="polite" aria-atomic="true">{{ anuncioLive }}</p>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronLeftIcon, BellIcon } from '@heroicons/vue/24/outline'
import { useNotificacoesCidadaoStore } from '@/stores/notificacoesCidadao'
import { formatarQuandoNotificacao } from '@/utils/notificacaoLink'
import PwaWebPushNudge from '@/components/pwa/PwaWebPushNudge.vue'

const router = useRouter()
const store = useNotificacoesCidadaoStore()
const anuncioLive = ref('')

function onPushAtivado() {
  anuncioLive.value = 'Notificações push ativadas neste dispositivo.'
}

function onPushErro(msg) {
  anuncioLive.value = msg || 'Não foi possível ativar as notificações.'
}

function formatarQuando(iso) {
  return formatarQuandoNotificacao(iso) || ''
}

function voltar() {
  router.push({ name: 'pwa-dashboard' })
}

async function abrirItem(item) {
  if (!item.lida) {
    try {
      await store.marcarLida(item.id)
      anuncioLive.value = 'Notificação marcada como lida'
    } catch {
      anuncioLive.value = 'Erro ao marcar notificação'
    }
  }
  const ref = item.protocoloCodigo || item.protocoloId
  if (ref) {
    router.push({ name: 'pwa-detalhes-protocolo', params: { id: String(ref) } })
  }
}

onMounted(async () => {
  await store.carregar({ limit: 50 })
})
</script>