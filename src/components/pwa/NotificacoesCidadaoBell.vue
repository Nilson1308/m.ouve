<template>
  <div ref="rootRef" class="relative">
    <button
      type="button"
      class="btn-icon relative min-h-[44px] min-w-[44px]"
      :aria-expanded="aberto"
      aria-haspopup="dialog"
      :aria-label="ariaLabelSino"
      @click="togglePainel"
    >
      <BellIcon
        class="w-5 h-5 text-gray-600 dark:text-gray-300 high-contrast:text-yellow-300"
        aria-hidden="true"
      />
      <span
        v-if="store.temNaoLidas"
        class="absolute top-0.5 right-0.5 min-w-[1.125rem] h-[1.125rem] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center"
        aria-hidden="true"
      >
        {{ badgeCount }}
      </span>
    </button>

    <Transition name="fade-scale">
      <div
        v-if="aberto"
        id="painel-notificacoes-cidadao"
        role="dialog"
        aria-modal="false"
        aria-labelledby="titulo-painel-notificacoes"
        class="absolute right-0 mt-2 w-[min(100vw-2rem,22rem)] rounded-card border border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300 bg-white dark:bg-gray-900 high-contrast:bg-black shadow-float z-[60]"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h2 id="titulo-painel-notificacoes" class="text-sm font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Notificações
          </h2>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="text-xs text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 hover:underline disabled:opacity-50 min-h-[44px] px-1"
              :disabled="store.loading"
              @click="atualizar"
            >
              Atualizar
            </button>
            <button
              type="button"
              class="btn-icon p-1 min-h-[44px] min-w-[44px]"
              aria-label="Fechar painel de notificações"
              @click="fechar"
            >
              <XMarkIcon class="w-5 h-5" aria-hidden="true" />
            </button>
          </div>
        </div>

        <p v-if="store.loading && !store.items.length" class="p-6 text-center text-sm text-gray-500" role="status">
          Carregando…
        </p>

        <ul
          v-else-if="store.items.length"
          class="max-h-80 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-700"
        >
          <li v-for="item in previewItems" :key="item.id">
            <button
              type="button"
              class="w-full text-left px-4 py-3 min-h-[44px] hover:bg-gray-50 dark:hover:bg-gray-800 high-contrast:hover:bg-yellow-300/10 transition-colors motion-reduce:transition-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary-500"
              :class="{ 'bg-primary-50/50 dark:bg-primary-900/10': !item.lida }"
              @click="abrirNotificacao(item)"
            >
              <div class="flex items-start gap-2">
                <span
                  class="mt-1.5 w-2 h-2 rounded-full shrink-0"
                  :class="item.lida ? 'bg-transparent' : 'bg-primary-500 high-contrast:bg-yellow-300'"
                  aria-hidden="true"
                />
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900 dark:text-white high-contrast:text-white truncate">
                    {{ item.titulo }}
                  </p>
                  <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-gray-200 line-clamp-2 mt-0.5">
                    {{ item.mensagem }}
                  </p>
                  <p class="text-[10px] text-gray-400 high-contrast:text-gray-300 mt-1">
                    {{ formatarQuando(item.dataCriacao) }}
                  </p>
                </div>
              </div>
            </button>
          </li>
        </ul>

        <p v-else class="p-6 text-sm text-center text-gray-500 dark:text-gray-400">
          Nenhuma notificação no momento.
        </p>

        <div class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/80">
          <RouterLink
            to="/app/notificacoes"
            class="block w-full text-center text-sm font-semibold text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 hover:underline py-2 min-h-[44px]"
            @click="fechar"
          >
            Ver todas as notificações
          </RouterLink>
        </div>
      </div>
    </Transition>

    <div class="sr-only" aria-live="polite" aria-atomic="true">{{ anuncioLive }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useNotificacoesCidadaoStore } from '@/stores/notificacoesCidadao'
import { formatarQuandoNotificacao } from '@/utils/notificacaoLink'

const store = useNotificacoesCidadaoStore()
const router = useRouter()
const aberto = ref(false)
const rootRef = ref(null)
const anuncioLive = ref('')

const badgeCount = computed(() => {
  const n = store.naoLidas
  return n > 99 ? '99+' : String(n)
})

const ariaLabelSino = computed(() => {
  const base = 'Abrir notificações'
  if (!store.temNaoLidas) return base
  return `${base}, ${store.naoLidas} não lida${store.naoLidas === 1 ? '' : 's'}`
})

const previewItems = computed(() => store.items.slice(0, 8))

function formatarQuando(iso) {
  return formatarQuandoNotificacao(iso) || ''
}

function fechar() {
  aberto.value = false
}

async function togglePainel() {
  aberto.value = !aberto.value
  if (aberto.value) {
    await store.carregar({ silencioso: false, limit: 15 })
  }
}

async function atualizar() {
  await store.carregar({ silencioso: false, limit: 15 })
}

async function abrirNotificacao(item) {
  if (!item.lida) {
    try {
      await store.marcarLida(item.id)
      anuncioLive.value = 'Notificação marcada como lida'
    } catch {
      anuncioLive.value = 'Não foi possível marcar como lida'
    }
  }
  fechar()
  const ref = item.protocoloCodigo || item.protocoloId
  if (ref) {
    router.push({ name: 'pwa-detalhes-protocolo', params: { id: String(ref) } })
  } else {
    router.push({ name: 'pwa-notificacoes' })
  }
}

function onClickFora(event) {
  if (!aberto.value) return
  if (rootRef.value && !rootRef.value.contains(event.target)) {
    fechar()
  }
}

function onEscape(event) {
  if (event.key === 'Escape' && aberto.value) {
    event.preventDefault()
    fechar()
  }
}

onMounted(() => {
  document.addEventListener('click', onClickFora)
  document.addEventListener('keydown', onEscape)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickFora)
  document.removeEventListener('keydown', onEscape)
})
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.96) translateY(-4px);
}
@media (prefers-reduced-motion: reduce) {
  .fade-scale-enter-active,
  .fade-scale-leave-active {
    transition: none;
  }
}
</style>