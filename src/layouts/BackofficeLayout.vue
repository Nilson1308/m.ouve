<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-950 flex">
    <aside
      :class="[
        'hidden lg:flex lg:flex-col fixed left-0 top-0 bottom-0 z-30 border-r border-slate-200/80 dark:border-slate-800/80',
        'bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl shadow-xl transition-[width] duration-300 ease-out',
        sidebarRecolhida ? 'w-[4.25rem]' : 'w-64'
      ]"
    >
      <div
        class="p-4 border-b border-slate-200/80 dark:border-slate-800/80 flex items-center justify-between gap-2"
      >
        <div class="flex items-center gap-2 min-w-0 flex-1">
          <img
            v-if="!sidebarRecolhida"
            :src="themeStore.currentTheme === 'light' ? BRAND.logos.light : BRAND.logos.dark"
            :alt="BRAND.name"
            class="h-8 w-auto object-contain"
          />
          <img
            v-else
            :src="BRAND.favicon"
            alt=""
            class="h-8 w-8 mx-auto object-contain"
          />
        </div>
        <button
          type="button"
          class="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 shrink-0"
          :title="sidebarRecolhida ? 'Expandir menu' : 'Recolher menu'"
          @click="alternarSidebar"
        >
          <ChevronDoubleLeftIcon
            class="w-5 h-5 transition-transform duration-300"
            :class="sidebarRecolhida ? 'rotate-180' : ''"
          />
        </button>
      </div>

      <nav class="flex-1 p-2 space-y-0.5 overflow-y-auto">
        <template v-for="(item, idx) in itensMenuVisiveis" :key="item.key || `d-${idx}`">
          <hr
            v-if="item.type === 'divider'"
            class="my-3 border-slate-200 dark:border-slate-700 mx-2"
          />
          <router-link
            v-else
            :to="item.to"
            :title="sidebarRecolhida ? item.label : undefined"
            class="sidebar-item group"
            :class="{
              'sidebar-item-active': rotaAtiva(item),
              'justify-center px-2': sidebarRecolhida
            }"
          >
            <component :is="item.icon" class="w-5 h-5 shrink-0" />
            <span v-if="!sidebarRecolhida" class="truncate flex-1">{{ item.label }}</span>
            <span
              v-if="!sidebarRecolhida && item.badge"
              class="min-w-[1.25rem] h-5 px-1.5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center"
            >
              {{ item.badge }}
            </span>
          </router-link>
        </template>
      </nav>

      <router-link
          to="/backoffice/perfil"
          class="m-2 p-3 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/80 dark:bg-slate-800/50 hover:bg-primary-50 dark:hover:bg-primary-950/30 transition-colors flex items-center gap-3"
          :class="sidebarRecolhida ? 'justify-center' : ''"
        >
          <div
            class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-cyan-600 text-white flex items-center justify-center font-bold text-sm shrink-0"
          >
            {{ iniciais }}
          </div>
          <div v-if="!sidebarRecolhida" class="min-w-0 flex-1">
            <p class="text-sm font-semibold text-slate-900 dark:text-white truncate">
              {{ authStore.userName }}
            </p>
            <p class="text-xs text-primary-600 dark:text-primary-400 font-medium">Editar perfil</p>
          </div>
          <ChevronRightIcon v-if="!sidebarRecolhida" class="w-4 h-4 text-slate-400 shrink-0" />
        </router-link>
    </aside>

    <div
      :class="[
        'flex-1 flex flex-col transition-[margin] duration-300 ease-out',
        sidebarRecolhida ? 'lg:ml-[4.25rem]' : 'lg:ml-64'
      ]"
    >
      <header
        class="sticky top-0 z-20 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 shadow-sm"
      >
        <div class="px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
          <button type="button" class="lg:hidden btn-icon" @click="menuMobileAberto = !menuMobileAberto">
            <Bars3Icon v-if="!menuMobileAberto" class="w-6 h-6" />
            <XMarkIcon v-else class="w-6 h-6" />
          </button>
          <h1 class="text-lg sm:text-xl font-semibold text-slate-900 dark:text-white truncate">
            {{ pageTitle }}
          </h1>
          <div class="flex items-center gap-2 shrink-0">
            <NotificacoesInternasBell />
            <ThemeToggle surface="light" />
            <button type="button" class="btn-icon group" title="Sair" @click="handleLogout">
              <ArrowRightOnRectangleIcon
                class="w-5 h-5 text-gray-600 dark:text-gray-300 group-hover:text-red-600"
              />
            </button>
          </div>
        </div>
      </header>

      <Transition name="slide">
        <nav
          v-if="menuMobileAberto"
          class="fixed inset-0 z-40 bg-white dark:bg-slate-950 p-6 lg:hidden overflow-y-auto"
        >
          <img
            :src="themeStore.currentTheme === 'light' ? BRAND.logos.light : BRAND.logos.dark"
            class="h-8 mb-6"
            alt=""
          />
          <ul class="space-y-1">
            <li v-for="(item, idx) in itensMenuVisiveis" :key="item.key || `m-${idx}`">
              <hr v-if="item.type === 'divider'" class="my-4 border-slate-200 dark:border-slate-700" />
              <router-link
                v-else
                :to="item.to"
                class="sidebar-item-mobile"
                @click="menuMobileAberto = false"
              >
                <component :is="item.icon" class="w-6 h-6" />
                <span class="flex-1">{{ item.label }}</span>
              </router-link>
            </li>
          </ul>
        </nav>
      </Transition>

      <main class="flex-1 animate-fade-in">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useRbac } from '@/composables/useRbac'
import { BRAND } from '@/constants/brand'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import NotificacoesInternasBell from '@/components/backoffice/NotificacoesInternasBell.vue'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import {
  ChartBarSquareIcon,
  MapIcon,
  ShieldCheckIcon,
  ClipboardDocumentListIcon,
  BuildingOffice2Icon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
  BellAlertIcon,
  DocumentTextIcon,
  BookOpenIcon,
  ChevronDoubleLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const SIDEBAR_LS_KEY = 'ouvia_backoffice_sidebar_collapsed'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const { can, isSuperAdmin } = useRbac()
const menuMobileAberto = ref(false)
const notificacoesStore = useNotificacoesInternasStore()
const sidebarRecolhida = ref(localStorage.getItem(SIDEBAR_LS_KEY) === '1')
let pollNotificacoes = null

const iniciais = computed(() => {
  const n = (authStore.userName || '?').trim()
  const p = n.split(/\s+/)
  if (p.length >= 2) return (p[0][0] + p[p.length - 1][0]).toUpperCase()
  return n.slice(0, 2).toUpperCase()
})

const menuDef = computed(() => [
  {
    key: 'mesa',
    to: '/backoffice/mesa-trabalho',
    icon: ClipboardDocumentListIcon,
    label: 'Mesa de Trabalho',
    perm: 'mesa_trabalho.ler'
  },
  {
    key: 'setorial',
    to: '/backoffice/setorial',
    icon: BuildingOffice2Icon,
    label: 'Painel Setorial',
    perm: 'painel_setorial.ler'
  },
  {
    key: 'executiva',
    to: '/backoffice/dashboard',
    icon: ChartBarSquareIcon,
    label: 'Visão Executiva',
    perm: 'mesa_trabalho.ler'
  },
  {
    key: 'territorial',
    to: '/backoffice/dashboard/mapa-gis',
    icon: MapIcon,
    label: 'Visão Territorial',
    perm: 'mapa_ia.ler'
  },
  {
    key: 'notificacoes',
    to: '/backoffice/notificacoes',
    icon: BellAlertIcon,
    label: 'Notificações',
    perm: 'mesa_trabalho.ler',
    badge:
      notificacoesStore.naoLidas > 0
        ? notificacoesStore.naoLidas > 99
          ? '99+'
          : String(notificacoesStore.naoLidas)
        : null
  },
  {
    key: 'manual',
    to: '/backoffice/manual',
    icon: BookOpenIcon,
    label: 'Manual do Sistema',
    sempreVisivel: true
  },
  { type: 'divider' },
  {
    key: 'inelegibilidade',
    to: '/backoffice/dashboard/inelegibilidade',
    icon: ShieldCheckIcon,
    label: 'Triagem e Bloqueios',
    perm: 'mesa_trabalho.ler'
  },
  {
    key: 'textos',
    to: '/backoffice/textos-padrao',
    icon: DocumentTextIcon,
    label: 'Textos Padrão',
    perm: 'textos_padrao.ler'
  },
  {
    key: 'config',
    to: '/backoffice/configuracoes',
    icon: Cog6ToothIcon,
    label: 'Configurações',
    perm: 'configuracoes.ler',
    allowSuperAdminOnly: false
  }
])

const itensMenuVisiveis = computed(() =>
  menuDef.value.filter((item) => {
    if (item.type === 'divider') return true
    if (item.sempreVisivel) return true
    if (item.key === 'config') {
      return can('configuracoes.ler') || isSuperAdmin.value
    }
    return can(item.perm)
  })
)

function rotaAtiva(item) {
  if (!item.to) return false
  if (item.to === '/backoffice/dashboard') {
    return route.path === item.to
  }
  return route.path.startsWith(item.to)
}

const pageTitle = computed(() => {
  if (route.meta?.pageTitle) return route.meta.pageTitle
  if (route.path.includes('/manual')) return 'Manual do Sistema'
  if (route.path.includes('/perfil')) return 'Meu perfil'
  if (route.path.includes('/acesso-negado')) return 'Acesso negado'
  return 'Backoffice'
})

function alternarSidebar() {
  sidebarRecolhida.value = !sidebarRecolhida.value
  localStorage.setItem(SIDEBAR_LS_KEY, sidebarRecolhida.value ? '1' : '0')
}

onMounted(() => {
  notificacoesStore.carregar({ silencioso: true }).catch(() => null)
  pollNotificacoes = window.setInterval(() => {
    notificacoesStore.carregar({ silencioso: true }).catch(() => null)
  }, 90_000)
})

onUnmounted(() => {
  if (pollNotificacoes) clearInterval(pollNotificacoes)
})

async function handleLogout() {
  await authStore.logout()
  router.push('/backoffice/login')
}
</script>

<style scoped>
.sidebar-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-xl;
  @apply text-slate-700 dark:text-slate-300;
  @apply hover:bg-slate-100 dark:hover:bg-slate-800/80;
  @apply transition-colors relative;
}

.sidebar-item-active {
  @apply bg-primary-50 dark:bg-primary-950/40;
  @apply text-primary-700 dark:text-primary-300;
  @apply font-semibold;
}

.sidebar-item-active::before {
  content: '';
  @apply absolute left-0 top-2 bottom-2 w-1 bg-primary-500 rounded-r-full;
}

.sidebar-item-mobile {
  @apply flex items-center gap-4 p-3 rounded-xl;
  @apply text-slate-700 dark:text-slate-300;
  @apply hover:bg-slate-100 dark:hover:bg-slate-800;
}

.sidebar-item-mobile.router-link-active {
  @apply bg-primary-100 dark:bg-primary-950/50;
  @apply text-primary-700 dark:text-primary-300 font-semibold;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>