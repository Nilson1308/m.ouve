<template>
  <div class="px-6 py-8 space-y-8">
      <!-- Stats Cards Modernos -->
      <div class="grid grid-cols-2 gap-4">
        <!-- Total Protocolos -->
        <div class="card bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/10 border-primary-200 dark:border-primary-800 hover:scale-105 transition-transform duration-300">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-primary-700 dark:text-primary-300 high-contrast:text-yellow-300 high-contrast:font-bold mb-1">
                Total
              </p>
              <p class="text-3xl font-bold text-primary-900 dark:text-primary-100 high-contrast:text-white">
                {{ protocolosStore.protocolos.length }}
              </p>
            </div>
            <div class="w-14 h-14 rounded-avatar bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-button">
              <DocumentTextIcon class="w-7 h-7 text-white" />
            </div>
          </div>
        </div>

        <!-- Ativos -->
        <div class="card bg-gradient-to-br from-teal-50 to-teal-100 dark:from-teal-900/20 dark:to-teal-800/10 border-teal-200 dark:border-teal-800 hover:scale-105 transition-transform duration-300">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-teal-700 dark:text-teal-300 high-contrast:text-yellow-300 high-contrast:font-bold mb-1">
                Ativos
              </p>
              <p class="text-3xl font-bold text-teal-900 dark:text-teal-100 high-contrast:text-white">
                {{ protocolosAtivos }}
              </p>
            </div>
            <div class="w-14 h-14 rounded-avatar bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center shadow-button">
              <ClockIcon class="w-7 h-7 text-white" />
            </div>
          </div>
        </div>
      </div>

      <!-- Meus Protocolos -->
      <section>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Meus Protocolos
          </h2>
          <button
            type="button"
            @click="filtroPainelAberto = !filtroPainelAberto"
            class="btn-ghost text-sm relative"
            :aria-expanded="filtroPainelAberto"
          >
            <FunnelIcon class="w-4 h-4" />
            Filtros
            <span
              v-if="temFiltrosAtivos"
              class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-primary-600 high-contrast:bg-yellow-300 animate-pulse"
              aria-hidden="true"
            />
          </button>
        </div>

        <!-- Filtros Inteligentes -->
        <transition name="slide-down">
          <div v-if="filtroPainelAberto" class="card mb-4 p-5 border border-gray-100 dark:border-gray-700 high-contrast:border-yellow-300">
            <ProtocolosFiltros
              v-model="filtros"
              :total-resultados="protocolosExibidos.length"
              @aplicar="aplicarFiltros"
            />
          </div>
        </transition>

        <!-- Loading State -->
        <div v-if="protocolosStore.loading" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="protocolosExibidos.length === 0 && protocolosStore.protocolos.length > 0"
          class="card text-center py-10 animate-scale-in"
        >
          <FunnelIcon class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Nenhum protocolo com estes filtros
          </h3>
          <button type="button" class="btn-secondary text-sm mt-2" @click="limparFiltros">
            Limpar filtros
          </button>
        </div>

        <div v-else-if="protocolosStore.protocolos.length === 0" class="card text-center py-12 animate-scale-in">
          <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 flex items-center justify-center">
            <InboxIcon class="w-10 h-10 text-gray-400 dark:text-gray-500" />
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-2">
            Nenhum protocolo ainda
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mb-6">
            Crie sua primeira solicitação para começar
          </p>
          <button @click="router.push('/app/nova-solicitacao')" class="btn-primary">
            <PlusIcon class="w-5 h-5" />
            Nova Solicitação
          </button>
        </div>

        <!-- Lista de Protocolos -->
        <div v-else class="space-y-4 animate-slide-up">
          <div
            v-for="protocolo in protocolosExibidos"
            :key="protocolo.id"
            @click="router.push({ name: 'pwa-detalhes-protocolo', params: { id: protocolo.id } })"
            class="protocol-card group"
            :class="getProtocolBorderClass(protocolo)"
          >
            <!-- Header do Card -->
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2 flex-wrap">
                  <span class="text-xs font-mono font-semibold text-gray-500 dark:text-gray-400 high-contrast:text-gray-400">
                    {{ protocolo.id }}
                  </span>
                  <StatusBadge :status="protocolo.status" :tipo="protocolo.tipo" />
                  <span
                    v-if="protocolo.aguardandoCidadao || protocolo.aguardando_cidadao || protocolo.status === 'aguardando_cidadao'"
                    class="inline-flex items-center min-h-[28px] px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500 text-amber-950 dark:bg-amber-400 dark:text-amber-950 high-contrast:bg-yellow-300 high-contrast:text-black ring-2 ring-amber-600/30"
                  >
                    Aguardando sua resposta
                  </span>
                </div>
                <h3 class="font-bold text-gray-900 dark:text-white high-contrast:text-white text-lg group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                  {{ protocolo.categoria }}
                </h3>
              </div>
              
              <!-- Ícone do Tipo -->
              <div class="w-12 h-12 rounded-avatar flex items-center justify-center shadow-soft" :class="getTipoIconClass(protocolo.tipo)">
                <BuildingOffice2Icon v-if="protocolo.tipo === 'zeladoria'" class="w-6 h-6 text-white" />
                <ChatBubbleLeftRightIcon v-else class="w-6 h-6 text-white" />
              </div>
            </div>

            <!-- Descrição -->
            <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mb-4 line-clamp-2">
              {{ protocolo.descricao }}
            </p>

            <!-- Footer -->
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2 text-gray-500 dark:text-gray-500">
                <ClockIcon class="w-4 h-4" />
                <span class="high-contrast:text-white high-contrast:font-bold">{{ formatarData(protocolo.dataCriacao) }}</span>
              </div>
              
              <div class="flex items-center gap-3 text-gray-400 dark:text-gray-500">
                <div v-if="protocolo.localizacao" class="flex items-center gap-1 high-contrast:text-yellow-300">
                  <MapPinIcon class="w-4 h-4" />
                </div>
                <div v-if="protocolo.anexos && protocolo.anexos.length > 0" class="flex items-center gap-1 high-contrast:text-yellow-300">
                  <PaperClipIcon class="w-4 h-4" />
                  <span class="high-contrast:font-bold">{{ protocolo.anexos.length }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    <!-- Ação principal — nova solicitação -->
    <div class="fixed left-0 right-0 bottom-24 z-30 pointer-events-none px-4 pb-6 safe-area-inset-bottom flex justify-end">
      <button
        type="button"
        @click="router.push('/app/nova-solicitacao')"
        class="pointer-events-auto flex items-center gap-2.5 pl-4 pr-5 py-3.5 rounded-full bg-gradient-to-r from-success-500 to-success-600 hover:from-success-600 hover:to-success-700 shadow-float hover:shadow-glow-green text-white transition-all duration-300 hover:scale-[1.02] active:scale-95 group border-2 border-white/20 dark:border-white/10"
        aria-label="Abrir nova solicitação de ouvidoria ou zeladoria"
      >
        <span class="flex h-10 w-10 items-center justify-center rounded-full bg-white/20 group-hover:bg-white/25">
          <PlusIcon class="w-6 h-6 group-hover:rotate-90 transition-transform duration-300" />
        </span>
        <span class="flex flex-col items-start leading-tight pr-1">
          <span class="text-sm sm:text-base font-bold">Nova solicitação</span>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BRAND } from '@/constants/brand'
import { useAuthStore } from '@/stores/auth'
import { useProtocolosStore } from '@/stores/protocolos'
import { useThemeStore } from '@/stores/theme'
import { useDialog } from '@/composables/useDialog'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import ProtocolosFiltros from '@/components/pwa/dashboard/ProtocolosFiltros.vue'
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ClockIcon,
  FunnelIcon,
  InboxIcon,
  PlusIcon,
  BuildingOffice2Icon,
  MapPinIcon,
  PaperClipIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const protocolosStore = useProtocolosStore()
const { confirm } = useDialog()

const filtroPainelAberto = ref(false)
const filtros = ref({
  busca: '',
  status: '',
  categoria: '',
  dataInicio: '',
  dataFim: ''
})

const STATUS_ENCERRADOS = new Set(['resolvido', 'rejeitado', 'concluido', 'nao_procedente', 'arquivado'])

const temFiltrosAtivos = computed(() => {
  return filtros.value.busca ||
         filtros.value.status ||
         filtros.value.categoria ||
         filtros.value.dataInicio ||
         filtros.value.dataFim
})

const protocolosExibidos = computed(() => {
  let lista = protocolosStore.protocolos

  // Filtro de busca
  if (filtros.value.busca) {
    const busca = filtros.value.busca.toLowerCase()
    lista = lista.filter(p => 
      p.codigo?.toLowerCase().includes(busca) ||
      p.descricao?.toLowerCase().includes(busca) ||
      p.endereco?.toLowerCase().includes(busca) ||
      p.tipo?.toLowerCase().includes(busca)
    )
  }

  // Filtro de status
  if (filtros.value.status) {
    lista = lista.filter(p => p.status?.toUpperCase() === filtros.value.status)
  }

  // Filtro de categoria
  if (filtros.value.categoria) {
    const categoria = filtros.value.categoria.toLowerCase()
    if (categoria === 'ouvidoria') {
      lista = lista.filter(p => p.tipo === 'ouvidoria')
    } else if (categoria === 'zeladoria urbana') {
      lista = lista.filter(p => p.tipo === 'zeladoria')
    }
  }

  // Filtro de período
  if (filtros.value.dataInicio) {
    const dataInicio = new Date(filtros.value.dataInicio)
    lista = lista.filter(p => new Date(p.dataCriacao) >= dataInicio)
  }

  if (filtros.value.dataFim) {
    const dataFim = new Date(filtros.value.dataFim)
    dataFim.setHours(23, 59, 59, 999) // Fim do dia
    lista = lista.filter(p => new Date(p.dataCriacao) <= dataFim)
  }

  return lista
})

const protocolosAtivos = computed(() => {
  return protocolosStore.protocolos.filter((p) => !STATUS_ENCERRADOS.has(p.status)).length
})

function aplicarFiltros() {
  // Filtros já são aplicados automaticamente via computed
  console.log('Filtros aplicados:', filtros.value)
}

onMounted(() => {
  protocolosStore.carregarProtocolos()
})

async function handleLogout() {
  const confirmado = await confirm(
    'Você será desconectado do sistema. Deseja continuar?',
    'Confirmar Saída'
  )
  
  if (confirmado) {
    await authStore.logout()
    router.push('/login')
  }
}

function getProtocolBorderClass(protocolo) {
  const colors = {
    'triagem': 'before:bg-primary-500',
    'em_analise': 'before:bg-primary-500',
    'validacao': 'before:bg-purple-500',
    'em_andamento': 'before:bg-amber-500',
    'em_execucao': 'before:bg-teal-500',
    'resolvido': 'before:bg-green-500',
    'concluido': 'before:bg-green-500',
    'arquivado': 'before:bg-gray-400',
  }
  return colors[protocolo.status] || 'before:bg-gray-300'
}

function getTipoIconClass(tipo) {
  return tipo === 'zeladoria' 
    ? 'bg-gradient-to-br from-teal-500 to-teal-600'
    : 'bg-gradient-to-br from-primary-500 to-primary-600'
}

function formatarData(dataISO) {
  const data = new Date(dataISO)
  const agora = new Date()
  const diff = Math.floor((agora - data) / 1000)

  if (diff < 60) return 'Agora'
  if (diff < 3600) return `${Math.floor(diff / 60)}min atrás`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h atrás`
  if (diff < 172800) return 'Ontem'
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
