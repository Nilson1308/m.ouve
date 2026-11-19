<template>
  <div ref="rootRef" class="relative">
    <button
      type="button"
      class="btn-icon relative"
      title="Notificações internas"
      aria-label="Notificações internas"
      :aria-expanded="aberto"
      @click="togglePainel"
    >
      <BellIcon class="w-5 h-5 text-gray-600 dark:text-gray-300" />
      <span
        v-if="store.temNaoLidas"
        class="absolute -top-0.5 -right-0.5 min-w-[1.125rem] h-[1.125rem] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center"
      >
        {{ badgeCount }}
      </span>
    </button>

    <Transition name="fade-scale">
      <div
        v-if="aberto"
        class="absolute right-0 mt-2 w-[min(100vw-2rem,22rem)] rounded-card border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-float z-[60]"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white">Notificações</h3>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="text-xs text-primary-600 dark:text-primary-400 hover:underline disabled:opacity-50"
              :disabled="!store.temNaoLidas || store.loading"
              @click="marcarTodas"
            >
              Marcar todas
            </button>
            <button
              type="button"
              class="btn-icon p-1"
              title="Atualizar"
              :disabled="store.loading"
              @click="atualizar"
            >
              <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': store.loading }" />
            </button>
          </div>
        </div>

        <div v-if="store.loading && !store.items.length" class="p-6 text-center text-sm text-gray-500">
          Carregando…
        </div>

        <ul v-else-if="store.items.length" class="max-h-80 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-700">
          <li
            v-for="item in store.items"
            :key="item.id"
            class="px-4 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
            :class="{ 'bg-primary-50/50 dark:bg-primary-900/10': !item.lida }"
            @click="abrirNotificacao(item)"
          >
            <div class="flex items-start gap-2">
              <span
                class="mt-1.5 w-2 h-2 rounded-full shrink-0"
                :class="item.lida ? 'bg-transparent' : 'bg-primary-500'"
                aria-hidden="true"
              />
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {{ item.titulo }}
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mt-0.5">
                  {{ item.mensagem }}
                </p>
                <p class="text-[10px] text-gray-400 mt-1">
                  {{ formatarQuando(item.dataCriacao) }}
                </p>
              </div>
            </div>
          </li>
        </ul>

        <p v-else class="p-6 text-sm text-center text-gray-500 dark:text-gray-400">
          Nenhuma notificação no momento.
        </p>

        <div class="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/80">
          <RouterLink
            to="/backoffice/notificacoes"
            class="block w-full text-center text-sm font-semibold text-primary-600 dark:text-primary-400 hover:underline py-1"
            @click="aberto = false"
          >
            Ver todas as notificações
          </RouterLink>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { BellIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import { formatarQuandoNotificacao, rotaInternaNotificacao } from '@/utils/notificacaoLink'

const store = useNotificacoesInternasStore()
const router = useRouter()
const aberto = ref(false)
const rootRef = ref(null)

const badgeCount = computed(() => {
  const n = store.naoLidas
  return n > 99 ? '99+' : String(n)
})

function togglePainel() {
  aberto.value = !aberto.value
  if (aberto.value) {
    atualizar()
  }
}

async function atualizar() {
  try {
    await store.carregar({ silencioso: aberto.value && store.items.length > 0 })
  } catch {
    /* silencioso no header */
  }
}

async function marcarTodas() {
  await store.marcarTodasLidasVisiveis()
}

async function abrirNotificacao(item) {
  if (!item.lida) {
    try {
      await store.marcarLida(item.id)
    } catch {
      /* segue navegação */
    }
  }
  aberto.value = false
  const rota = rotaInternaNotificacao(item.linkAcao)
  if (rota) {
    router.push(rota)
  } else if (item.linkAcao) {
    window.location.href = item.linkAcao
  }
}

function formatarQuando(iso) {
  return formatarQuandoNotificacao(iso)
}

function onClickFora(ev) {
  if (!aberto.value || !rootRef.value) return
  if (!rootRef.value.contains(ev.target)) {
    aberto.value = false
  }
}

onMounted(() => {
  store.carregar({ silencioso: true }).catch(() => null)
  document.addEventListener('click', onClickFora)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickFora)
})
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
</style>
