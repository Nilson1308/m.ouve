<template>
  <div class="min-h-full bg-gray-50 dark:bg-gray-950">
    <div
      v-if="erro"
      class="mx-4 sm:mx-6 lg:mx-8 mt-4 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm text-red-800 dark:text-red-200"
    >
      {{ erro }}
      <button type="button" class="ml-3 underline font-medium" @click="adminStore.limparErro()">
        Fechar
      </button>
    </div>

    <div class="flex flex-col lg:flex-row gap-0 lg:gap-0 min-h-[calc(100vh-4rem)]">
      <aside
        class="lg:w-72 shrink-0 border-b lg:border-b-0 lg:border-r border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/60 backdrop-blur-md p-4 lg:p-6"
      >
        <h2 class="text-lg font-bold text-slate-900 dark:text-white mb-1">Administração</h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mb-6">
          Governança, catálogo e monitoramento
        </p>
        <nav class="space-y-1">
          <button
            v-for="sec in secoesVisiveis"
            :key="sec.id"
            type="button"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left text-sm font-medium transition-colors"
            :class="
              secaoAtiva === sec.id
                ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
            "
            @click="selecionarSecao(sec.id)"
          >
            <component :is="sec.icon" class="w-5 h-5 shrink-0" />
            <span class="flex-1 truncate">{{ sec.nome }}</span>
            <span
              v-if="sec.badge"
              class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700"
            >
              {{ sec.badge }}
            </span>
          </button>
        </nav>
      </aside>

      <main class="flex-1 min-w-0 px-4 sm:px-6 lg:px-8 py-6 lg:py-8 overflow-x-auto">
        <Transition name="fade" mode="out-in">
          <GestaoUnidades v-if="secaoAtiva === 'unidades'" />
          <GestaoUsuarios v-else-if="secaoAtiva === 'usuarios'" />
          <GestaoPerfis v-else-if="secaoAtiva === 'perfis'" />
          <GestaoCatalogo v-else-if="secaoAtiva === 'servicos'" />
          <GestaoEquipamentos v-else-if="secaoAtiva === 'equipamentos'" />
          <GestaoSaudeInfra v-else-if="secaoAtiva === 'monitoramento'" />
          <p v-else class="text-center py-16 text-slate-500 dark:text-slate-400 text-sm">
            Selecione uma seção ao lado.
          </p>
        </Transition>
      </main>
    </div>

    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="toastAberto"
          class="fixed bottom-6 right-6 z-[200] max-w-sm px-4 py-3 rounded-xl shadow-lg border text-sm font-medium flex items-start gap-2"
          :class="
            toastErro
              ? 'bg-red-50 border-red-200 text-red-900 dark:bg-red-950 dark:border-red-800 dark:text-red-100'
              : 'bg-white border-gray-200 text-gray-900 dark:bg-gray-800 dark:border-gray-600 dark:text-white'
          "
          role="status"
        >
          <CheckCircleIcon v-if="!toastErro" class="w-5 h-5 text-green-600 shrink-0" />
          <ExclamationCircleIcon v-else class="w-5 h-5 text-red-600 shrink-0" />
          <span>{{ toastMensagem }}</span>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  BuildingOfficeIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  WrenchScrewdriverIcon,
  SignalIcon,
  BuildingStorefrontIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import GestaoUnidades from '@/components/backoffice/admin/GestaoUnidades.vue'
import GestaoUsuarios from '@/components/backoffice/admin/GestaoUsuarios.vue'
import GestaoPerfis from '@/components/backoffice/admin/GestaoPerfis.vue'
import GestaoCatalogo from '@/components/backoffice/catalogo/GestaoCatalogo.vue'
import GestaoSaudeInfra from '@/components/backoffice/admin/GestaoSaudeInfra.vue'
import GestaoEquipamentos from '@/components/backoffice/admin/GestaoEquipamentos.vue'
import { useAdminStore } from '@/stores/admin'
import { useCatalogoStore } from '@/stores/catalogo'
import { useAdminToast } from '@/composables/useAdminToast'
import { useRbac } from '@/composables/useRbac'

const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()
const catalogoStore = useCatalogoStore()
const { totalUnidades, totalUsuarios, totalPerfis, totalEquipamentos, erro } = storeToRefs(adminStore)
const { totalServicos } = storeToRefs(catalogoStore)
const { toastAberto, toastMensagem, toastErro } = useAdminToast()
const { can, isSuperAdmin } = useRbac()

const SECOES_VALIDAS = ['unidades', 'usuarios', 'perfis', 'servicos', 'equipamentos', 'monitoramento']
const secaoAtiva = ref('unidades')

const secoes = computed(() => [
  {
    id: 'unidades',
    nome: 'Unidades Administrativas',
    icon: BuildingOfficeIcon,
    badge: totalUnidades.value > 0 ? totalUnidades.value : null,
    visible: () => can('configuracoes.ler') || isSuperAdmin.value
  },
  {
    id: 'usuarios',
    nome: 'Usuários e Acessos',
    icon: UserGroupIcon,
    badge: totalUsuarios.value > 0 ? totalUsuarios.value : null,
    visible: () => can('gestao_usuarios.ler') || isSuperAdmin.value
  },
  {
    id: 'perfis',
    nome: 'Perfis e Permissões',
    icon: ShieldCheckIcon,
    badge: totalPerfis.value > 0 ? totalPerfis.value : null,
    visible: () => isSuperAdmin.value
  },
  {
    id: 'servicos',
    nome: 'Catálogo de Serviços',
    icon: WrenchScrewdriverIcon,
    badge: totalServicos.value > 0 ? totalServicos.value : null,
    visible: () => can('configuracoes.ler') || isSuperAdmin.value
  },
  {
    id: 'equipamentos',
    nome: 'Equipamentos Públicos',
    icon: BuildingStorefrontIcon,
    badge: totalEquipamentos.value > 0 ? totalEquipamentos.value : null,
    visible: () => can('configuracoes.ler') || isSuperAdmin.value
  },
  {
    id: 'monitoramento',
    nome: 'Monitoramento NOC',
    icon: SignalIcon,
    badge: null,
    visible: () => isSuperAdmin.value
  }
])

const secoesVisiveis = computed(() => secoes.value.filter((s) => s.visible()))

function sincronizarSecaoComRota() {
  const aba = route.query.aba || route.query.secao
  if (typeof aba === 'string' && SECOES_VALIDAS.includes(aba)) {
    const sec = secoes.value.find((s) => s.id === aba)
    if (sec && sec.visible()) {
      secaoAtiva.value = aba
      return
    }
  }
  const first = secoesVisiveis.value[0]
  if (first) secaoAtiva.value = first.id
}

function selecionarSecao(id) {
  secaoAtiva.value = id
  router.replace({ name: 'backoffice-configuracoes', query: { ...route.query, aba: id } })
}

watch(
  () => [route.query.aba, route.query.secao, secoesVisiveis.value.length],
  () => sincronizarSecaoComRota()
)

onMounted(() => {
  sincronizarSecaoComRota()
  adminStore.carregarUnidades().catch(() => {})
  adminStore.carregarUsuarios().catch(() => {})
  adminStore.carregarPerfisAcesso().catch(() => {})
  catalogoStore.carregarServicosCatalogo().catch(() => {})
  adminStore.carregarEquipamentos({}, { silencioso: true }).catch(() => {})
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>