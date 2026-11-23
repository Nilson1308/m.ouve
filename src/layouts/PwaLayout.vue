<template>
  <div class="min-h-screen" :class="{ 'pb-20': showBottomNav }">
    <a href="#conteudo-principal" class="skip-link">Pular para o conteúdo principal</a>
    <!-- Header PWA com Glassmorphism (oculto em sub-telas com cabeçalho próprio) -->
    <header
      v-if="showShellHeader"
      class="sticky top-0 z-20 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft"
    >
      <div class="px-6 py-4 safe-area-inset">
        <div class="flex items-center justify-between mb-3">
          <!-- Logo -->
          <router-link to="/app/dashboard" class="flex items-center gap-3">
            <img
              v-if="themeStore.currentTheme === 'light'"
              :src="BRAND.logos.light"
              :alt="BRAND.name"
              class="h-10 w-auto object-contain"
            />
            <img
              v-else
              :src="BRAND.logos.dark"
              :alt="BRAND.name"
              class="h-10 w-auto object-contain"
            />
          </router-link>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <NotificacoesCidadaoBell class="hidden md:block" />
            <PwaA11yMenu />
            <ThemeToggle surface="light" />
            <button
              type="button"
              @click="handleLogout"
              class="btn-icon group"
              aria-label="Sair da conta"
            >
              <ArrowRightOnRectangleIcon class="w-5 h-5 text-gray-600 dark:text-gray-300 high-contrast:text-yellow-300 group-hover:text-red-600 dark:group-hover:text-red-400" aria-hidden="true" />
            </button>
          </div>
        </div>
        
        <!-- User Greeting -->
        <div class="flex items-center gap-3">
          <router-link
            to="/app/perfil"
            class="w-10 h-10 rounded-full shrink-0 overflow-hidden bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-sm font-bold ring-2 ring-white/50 dark:ring-gray-800 shadow-soft"
            aria-label="Ir para meu perfil"
          >
            <img
              v-if="avatarUrl"
              :src="avatarUrl"
              alt=""
              class="w-full h-full object-cover"
            />
            <span v-else aria-hidden="true">{{ iniciaisUsuario }}</span>
          </router-link>
          <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold min-w-0">
            Olá, <span class="font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300">{{ authStore.userName }}</span>
          </p>
        </div>
      </div>
    </header>

    <!-- Área de conteúdo (landmark principal nas sub-rotas) -->
    <div
      :id="showShellHeader ? 'conteudo-principal' : undefined"
      :tabindex="showShellHeader ? -1 : undefined"
      class="animate-fade-in motion-reduce:animate-none"
    >
      <router-view />
    </div>

    <!-- Bottom Navigation (PWA) -->
    <nav
      v-if="showBottomNav"
      aria-label="Navegação principal do aplicativo"
      class="fixed bottom-0 left-0 right-0 z-30 bg-white dark:bg-gray-900 high-contrast:bg-black border-t border-gray-200 dark:border-gray-800 high-contrast:border-yellow-300 shadow-float dark:shadow-float-dark safe-area-inset-bottom"
    >
      <div class="flex items-center justify-around py-2">
        <!-- Home -->
        <router-link 
          to="/app/dashboard" 
          class="nav-item"
          :class="{ 'nav-item-active': $route.path.includes('/dashboard') }"
        >
          <HomeIcon class="w-6 h-6" aria-hidden="true" />
          <span class="text-xs mt-1">Início</span>
        </router-link>

        <!-- Nova Solicitação -->
        <router-link 
          to="/app/nova-solicitacao" 
          class="nav-item"
          :class="{ 'nav-item-active': $route.path.includes('/nova-solicitacao') || $route.path.includes('/chat') }"
        >
          <PlusCircleIcon class="w-6 h-6" aria-hidden="true" />
          <span class="text-xs mt-1">Nova</span>
        </router-link>

        <!-- Notificações -->
        <router-link
          to="/app/notificacoes"
          class="nav-item relative"
          :class="{ 'nav-item-active': $route.path.includes('/notificacoes') }"
          :aria-label="notificacoesNavAriaLabel"
        >
          <span class="relative inline-flex" aria-hidden="true">
            <BellIcon class="w-6 h-6" />
            <span
              v-if="notificacoesStore.temNaoLidas"
              class="absolute -top-1.5 -right-2 min-w-[1.125rem] h-[1.125rem] px-0.5 rounded-full bg-red-500 text-white text-[10px] font-bold leading-none flex items-center justify-center"
            >
              {{ badgeCount }}
            </span>
          </span>
          <span class="text-xs mt-1" aria-hidden="true">Avisos</span>
        </router-link>

        <!-- Perfil -->
        <router-link 
          to="/app/perfil" 
          class="nav-item"
          :class="{ 'nav-item-active': $route.path.includes('/perfil') || $route.path.includes('/ajuda') }"
        >
          <UserCircleIcon class="w-6 h-6" aria-hidden="true" />
          <span class="text-xs mt-1">Perfil</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { BRAND } from '@/constants/brand'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import PwaA11yMenu from '@/components/pwa/PwaA11yMenu.vue'
import NotificacoesCidadaoBell from '@/components/pwa/NotificacoesCidadaoBell.vue'
import { useNotificacoesCidadaoStore } from '@/stores/notificacoesCidadao'
import {
  HomeIcon,
  PlusCircleIcon,
  UserCircleIcon,
  BellIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const avatarUrl = computed(() => authStore.user?.avatar || '')

const iniciaisUsuario = computed(() => {
  const n = (authStore.userName || '?').trim()
  const p = n.split(/\s+/)
  if (p.length >= 2) return (p[0][0] + p[p.length - 1][0]).toUpperCase()
  return n.slice(0, 2).toUpperCase()
})

const notificacoesStore = useNotificacoesCidadaoStore()

const showShellHeader = computed(() => !route.meta.pwaHideShellHeader)
const showBottomNav = computed(() => !route.meta.pwaHideBottomNav)

const badgeCount = computed(() => {
  const n = notificacoesStore.naoLidas
  return n > 99 ? '99+' : String(n)
})

const notificacoesNavAriaLabel = computed(() => {
  const base = 'Notificações'
  if (!notificacoesStore.temNaoLidas) return base
  const q = notificacoesStore.naoLidas
  return `${base}, ${q} não lida${q === 1 ? '' : 's'}`
})

let pollInterval = null

function atualizarNotificacoes() {
  if (!authStore.isAuthenticated || authStore.isBackoffice) return
  notificacoesStore.carregar({ silencioso: true, limit: 15 }).catch(() => null)
}

function onWindowFocus() {
  atualizarNotificacoes()
}

onMounted(() => {
  atualizarNotificacoes()
  pollInterval = window.setInterval(atualizarNotificacoes, 2 * 60 * 1000)
  window.addEventListener('focus', onWindowFocus)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  window.removeEventListener('focus', onWindowFocus)
})

async function handleLogout() {
  notificacoesStore.reset()
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-item {
  @apply flex flex-col items-center justify-center;
  @apply px-4 py-2 min-h-[44px] rounded-button;
  @apply text-gray-600 dark:text-gray-400 high-contrast:text-white;
  @apply transition-all duration-200 motion-reduce:transition-none;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800 high-contrast:hover:bg-yellow-300/20;
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2;
}

.nav-item-active {
  @apply text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300;
  @apply font-semibold;
  @apply bg-primary-50 dark:bg-primary-900/20 high-contrast:bg-yellow-300/20;
}
</style>
