<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header Sticky -->
    <header class="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <ClipboardDocumentListIcon class="w-8 h-8 text-primary-500" />
              Mesa de Trabalho
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Gestão de Protocolos · Backoffice
            </p>
          </div>

          <div class="relative flex-1 max-w-md">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="filtros.busca"
              type="text"
              placeholder="Buscar por protocolo ou descrição..."
              class="block w-full pl-10 pr-3 py-2.5 border border-gray-300 dark:border-gray-600 rounded-input
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     placeholder-gray-500 dark:placeholder-gray-400
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     transition-all duration-200"
            />
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-2">
            <button
              @click="onToggleSlaVencido"
              :class="[
                'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                filtros.slaVencido
                  ? 'bg-danger-500 text-white shadow-button-hover'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 hover:border-danger-500 hover:text-danger-500'
              ]"
            >
              <ExclamationTriangleIcon class="w-5 h-5" />
              <span>SLA Vencido</span>
              <span v-if="contadores.slaVencido > 0" class="badge bg-white text-danger-600 ml-1">
                {{ contadores.slaVencido }}
              </span>
            </button>

            <button
              @click="onToggleUrgentes"
              :class="[
                'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                filtros.urgentes
                  ? 'bg-warning-500 text-white shadow-button-hover'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 hover:border-warning-500 hover:text-warning-500'
              ]"
            >
              <BoltIcon class="w-5 h-5" />
              <span>Urgentes</span>
              <span v-if="contadores.urgentes > 0" class="badge bg-white text-warning-600 ml-1">
                {{ contadores.urgentes }}
              </span>
            </button>

            <button
              type="button"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200
                     bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 
                     border border-gray-300 dark:border-gray-600
                     hover:border-primary-500 hover:text-primary-500"
              :class="totalFiltrosAvancados > 0 ? 'border-primary-500 text-primary-600 dark:text-primary-400 ring-1 ring-primary-500/30' : ''"
              @click="abrirFiltrosAvancados"
            >
              <FunnelIcon class="w-5 h-5" />
              <span>Mais filtros</span>
              <span
                v-if="totalFiltrosAvancados > 0"
                class="badge bg-primary-600 text-white min-w-[1.25rem] justify-center"
              >
                {{ totalFiltrosAvancados }}
              </span>
            </button>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <div class="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-button p-1">
              <button
                type="button"
                :class="[
                  'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                  abaMesa === 'protocolos'
                    ? 'bg-white dark:bg-gray-800 text-primary-600 shadow-soft'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                ]"
                @click="abaMesa = 'protocolos'"
              >
                <ClipboardDocumentListIcon class="w-5 h-5" />
                <span class="hidden sm:inline">Protocolos</span>
              </button>
              <button
                type="button"
                :class="[
                  'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                  abaMesa === 'assinaturas'
                    ? 'bg-white dark:bg-gray-800 text-primary-600 shadow-soft'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                ]"
                @click="irParaAssinaturas"
              >
                <PencilSquareIcon class="w-5 h-5" />
                <span class="hidden lg:inline">Aguardando minha assinatura</span>
                <span class="lg:hidden sm:inline hidden">Assinaturas</span>
                <span
                  v-if="assinaturasStore.totalPendentes > 0"
                  class="badge bg-danger-500 text-white ml-0.5"
                >
                  {{ assinaturasStore.totalPendentes }}
                </span>
              </button>
            </div>
            <div
              v-if="abaMesa === 'protocolos'"
              class="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-button p-1"
            >
            <button
              @click="modoVisualizacao = 'kanban'"
              :class="[
                'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                modoVisualizacao === 'kanban'
                  ? 'bg-white dark:bg-gray-800 text-primary-600 shadow-soft'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              ]"
            >
              <Squares2X2Icon class="w-5 h-5" />
              <span class="hidden sm:inline">Kanban</span>
            </button>
            <button
              @click="modoVisualizacao = 'lista'"
              :class="[
                'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                modoVisualizacao === 'lista'
                  ? 'bg-white dark:bg-gray-800 text-primary-600 shadow-soft'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              ]"
            >
              <Bars3Icon class="w-5 h-5" />
              <span class="hidden sm:inline">Lista</span>
            </button>
            <button
              @click="modoVisualizacao = 'mapa'"
              :class="[
                'inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all duration-200',
                modoVisualizacao === 'mapa'
                  ? 'bg-white dark:bg-gray-800 text-primary-600 shadow-soft'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              ]"
            >
              <MapIcon class="w-5 h-5" />
              <span class="hidden sm:inline">Mapa & IA</span>
            </button>
            </div>
          </div>
        </div>

        <div v-if="temFiltrosAtivos" class="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Filtros ativos:</span>
          <button
            v-for="filtro in filtrosAtivosArray"
            :key="filtro.key"
            @click="removerFiltro(filtro.key)"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-badge text-sm
                   bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300
                   hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors duration-200"
          >
            <span>{{ filtro.label }}</span>
            <XMarkIcon class="w-4 h-4" />
          </button>
          <button
            @click="limparFiltrosERecarregar"
            class="text-sm text-danger-600 hover:text-danger-700 font-medium ml-2"
          >
            Limpar todos
          </button>
        </div>
      </div>
    </header>

    <main class="px-4 sm:px-6 lg:px-8 py-6">
      <div v-if="erro" class="alert-danger mb-4 flex items-center justify-between gap-3">
        <span>{{ erro }}</span>
        <button type="button" class="btn-secondary text-sm" @click="recarregar">
          Tentar novamente
        </button>
      </div>

      <AssinaturasPendentesPanel
        v-if="abaMesa === 'assinaturas'"
        @toast="mostrarToast"
        @concluido="onAssinaturaConcluida"
      />

      <template v-else>
      <div
        v-if="contadores.aguardandoValidacao > 0"
        class="mb-4 rounded-lg border-2 border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/25 px-4 py-3 flex flex-wrap items-center justify-between gap-3"
        role="status"
      >
        <p class="text-sm text-purple-900 dark:text-purple-100">
          <strong class="font-semibold">{{ contadores.aguardandoValidacao }}</strong>
          {{
            contadores.aguardandoValidacao === 1
              ? ' protocolo pronto para validação da Ouvidoria'
              : ' protocolos prontos para validação da Ouvidoria'
          }}
          — gather completo (todos os nós encerrados).
        </p>
        <span class="text-xs text-purple-700 dark:text-purple-300">
          Coluna «Aguardando validação» no Kanban
        </span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
        <div class="card p-4 hover:shadow-card-hover transition-shadow duration-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Total</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ contadores.total }}</p>
            </div>
            <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-xl flex items-center justify-center">
              <ClipboardDocumentListIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
        </div>
        <div class="card p-4 hover:shadow-card-hover transition-shadow duration-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Em Andamento</p>
              <p class="text-2xl font-bold text-warning-600 dark:text-warning-400 mt-1">{{ contadores.emAndamento }}</p>
            </div>
            <div class="w-12 h-12 bg-warning-100 dark:bg-warning-900 rounded-xl flex items-center justify-center">
              <ClockIcon class="w-6 h-6 text-warning-600 dark:text-warning-400" />
            </div>
          </div>
        </div>
        <div
          class="card p-4 hover:shadow-card-hover transition-shadow duration-200"
          :class="contadores.aguardandoValidacao > 0 ? 'ring-2 ring-purple-400 dark:ring-purple-600' : ''"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Aguardando validação</p>
              <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">
                {{ contadores.aguardandoValidacao }}
              </p>
            </div>
            <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/50 rounded-xl flex items-center justify-center">
              <ShieldCheckIcon class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>
        <div class="card p-4 hover:shadow-card-hover transition-shadow duration-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">SLA Vencido</p>
              <p class="text-2xl font-bold text-danger-600 dark:text-danger-400 mt-1">{{ contadores.slaVencido }}</p>
            </div>
            <div class="w-12 h-12 bg-danger-100 dark:bg-danger-900 rounded-xl flex items-center justify-center">
              <ExclamationTriangleIcon class="w-6 h-6 text-danger-600 dark:text-danger-400" />
            </div>
          </div>
        </div>
        <div class="card p-4 hover:shadow-card-hover transition-shadow duration-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Concluídos Hoje</p>
              <p class="text-2xl font-bold text-success-600 dark:text-success-400 mt-1">{{ contadores.concluidosHoje }}</p>
            </div>
            <div class="w-12 h-12 bg-success-100 dark:bg-success-900 rounded-xl flex items-center justify-center">
              <CheckCircleIcon class="w-6 h-6 text-success-600 dark:text-success-400" />
            </div>
          </div>
        </div>
      </div>

      <ResumoIaMesa
        v-if="!loading && abaMesa === 'protocolos' && (modoVisualizacao === 'kanban' || modoVisualizacao === 'lista')"
        class="mb-4"
        :total-sugestoes="superOSStore.totalSugestoes"
        :total-protocolos="superOSStore.totalProtocolosAgrupáveis"
        @abrir-mapa-ia="abrirMapaIa()"
      />

      <div v-if="loading" class="card p-12 flex flex-col items-center justify-center gap-4 min-h-[420px]">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        <p class="text-gray-600 dark:text-gray-400 text-sm">Carregando protocolos...</p>
      </div>

      <div
        v-else-if="!protocolosExibidos.length && (modoVisualizacao === 'kanban' || modoVisualizacao === 'lista')"
        class="card flex flex-col items-center justify-center py-20 px-6 text-center min-h-[420px]"
        role="status"
      >
        <InboxIcon class="w-16 h-16 text-gray-300 dark:text-gray-600 opacity-80 mb-4" aria-hidden="true" />
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Sua mesa está limpa</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-2 max-w-md leading-relaxed">
          Não há protocolos neste recorte de filtros. Novas demandas despachadas para o seu setor aparecerão aqui automaticamente.
        </p>
      </div>

      <transition v-else name="fade" mode="out-in">
        <BoardKanban
          v-if="modoVisualizacao === 'kanban'"
          :protocolos="protocolosExibidos"
          @despachar="abrirDespacho"
          @integrar="integrarAncoraSuperOs"
          @detalhes="verDetalhes"
          @ver-cluster-ia="abrirMapaIa"
        />
        <TabelaProtocolos
          v-else-if="modoVisualizacao === 'lista'"
          :protocolos="protocolosExibidos"
          @despachar="abrirDespacho"
          @integrar="integrarAncoraSuperOs"
          @detalhes="verDetalhes"
          @ver-cluster-ia="abrirMapaIa"
        />
        <div
          v-else-if="modoVisualizacao === 'mapa'"
          class="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <!-- Widget IA (Lateral) -->
          <div class="lg:col-span-1 h-[calc(100vh-24rem)] lg:h-[calc(100vh-16rem)]">
            <WidgetSugestoesIA
              @refresh="carregarSugestoesIA"
              @visualizar-no-mapa="destacarSugestaoNoMapa"
              @sugestao-aprovada="onSugestaoAprovada"
              @sugestao-erro="(msg) => mostrarToast(msg, true)"
            />
          </div>
          
          <!-- Mapa (Principal) -->
          <div class="lg:col-span-2 h-[calc(100vh-24rem)] lg:h-[calc(100vh-16rem)]">
            <MapaClustersView
              :protocolos="protocolosParaMapa"
              :sugestao-destacada="sugestaoDestacadaMapa"
              @protocolo-selecionado="verDetalhes"
              @super-os-criada="onSuperOSCriada"
              @super-os-erro="(msg) => mostrarToast(msg, true)"
            />
          </div>
        </div>
      </transition>
      </template>
    </main>

    <DespacharProtocolo
      v-if="protocoloSelecionado"
      :protocolo="protocoloSelecionado"
      :aberto="mostrarDespacho"
      :salvando="despachando"
      :prefill-ordens="prefillOrdens"
      @fechar="fecharDespacho"
      @confirmar="confirmarDespacho"
    />

    <ModalFiltrosAvancadosMesa
      :aberto="mostrarFiltrosAvancados"
      :filtros-atuais="filtros"
      :unidades="unidades"
      :opcoes="opcoesFiltrosMesa"
      @fechar="mostrarFiltrosAvancados = false"
      @aplicar="aplicarFiltrosAvancados"
    />

    <Teleport to="body">
      <transition name="mesa-toast">
        <div
          v-if="toastAberto"
          class="mesa-toast"
          :class="{ 'mesa-toast--erro': toastErro }"
          role="status"
        >
          {{ toastMensagem }}
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { watchDebounced } from '@vueuse/core'
import {
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  BoltIcon,
  FunnelIcon,
  Squares2X2Icon,
  Bars3Icon,
  MapIcon,
  XMarkIcon,
  ClockIcon,
  CheckCircleIcon,
  PencilSquareIcon,
  ShieldCheckIcon,
  InboxIcon
} from '@heroicons/vue/24/outline'

import BoardKanban from '@/components/backoffice/BoardKanban.vue'
import TabelaProtocolos from '@/components/backoffice/TabelaProtocolos.vue'
import DespacharProtocolo from '@/components/backoffice/DespacharProtocolo.vue'
import ModalFiltrosAvancadosMesa from '@/components/backoffice/ModalFiltrosAvancadosMesa.vue'
import AssinaturasPendentesPanel from '@/components/backoffice/AssinaturasPendentesPanel.vue'
import WidgetSugestoesIA from '@/components/backoffice/ia/WidgetSugestoesIA.vue'
import MapaClustersView from '@/components/backoffice/ia/MapaClustersView.vue'
import ResumoIaMesa from '@/components/backoffice/ia/ResumoIaMesa.vue'
import { useBackofficeStore } from '@/stores/backoffice'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import { useAssinaturasStore } from '@/stores/assinaturas'
import { useSuperOSStore } from '@/stores/super_os'
import { useDialog } from '@/composables/useDialog'
import { getApiErrorMessage } from '@/utils/apiError'
import { protocolosElegiveisMapa } from '@/utils/superOsMappers'

const router = useRouter()
const backofficeStore = useBackofficeStore()
const notificacoesInternasStore = useNotificacoesInternasStore()
const assinaturasStore = useAssinaturasStore()
const superOSStore = useSuperOSStore()
const dialog = useDialog()

const abaMesa = ref('protocolos')
const toastErro = ref(false)

const {
  filtros,
  contadores,
  protocolosExibidos,
  loading,
  despachando,
  erro,
  unidades,
  opcoesFiltrosMesa,
  totalFiltrosAvancados
} = storeToRefs(backofficeStore)

const mostrarFiltrosAvancados = ref(false)

const modoVisualizacao = ref('kanban')
const mostrarDespacho = ref(false)
const protocoloSelecionado = ref(null)
const prefillOrdens = ref([])
const toastAberto = ref(false)
const toastMensagem = ref('')
let toastTimer = null

// Estados para Mapa & IA
const sugestaoDestacadaMapa = ref(null)

const protocolosParaMapa = computed(() => protocolosElegiveisMapa(protocolosExibidos.value))

const STATUS_LABEL = {
  em_analise: 'Em análise',
  em_andamento: 'Em andamento',
  aguardando_cidadao: 'Aguardando cidadão',
  aguardando_revisao: 'Aguardando validação',
  resolvido: 'Resolvido',
  rejeitado: 'Rejeitado'
}

const temFiltrosAtivos = computed(
  () =>
    Boolean(
      filtros.value.busca ||
        filtros.value.slaVencido ||
        filtros.value.urgentes ||
        totalFiltrosAvancados.value > 0
    )
)

const filtrosAtivosArray = computed(() => {
  const ativos = []
  const f = filtros.value
  if (f.slaVencido) ativos.push({ key: 'slaVencido', label: 'SLA vencido' })
  if (f.urgentes) ativos.push({ key: 'urgentes', label: 'Urgentes (alta/crítica)' })
  if (f.busca) ativos.push({ key: 'busca', label: `Busca: ${f.busca}` })
  for (const id of f.unidadesIds || []) {
    const u = unidades.value.find((x) => x.id === id)
    ativos.push({ key: `unidade:${id}`, kind: 'unidade', id, label: u?.sigla || u?.nome || 'Setor' })
  }
  for (const id of f.servicoIds || []) {
    const s = opcoesFiltrosMesa.value.servicos?.find((x) => x.id === id)
    ativos.push({ key: `servico:${id}`, kind: 'servico', id, label: s?.nome || 'Serviço' })
  }
  for (const b of f.bairros || []) {
    ativos.push({ key: `bairro:${b}`, kind: 'bairro', value: b, label: `Bairro: ${b}` })
  }
  for (const st of f.statusLista || []) {
    ativos.push({
      key: `status:${st}`,
      kind: 'status',
      value: st,
      label: STATUS_LABEL[st] || st
    })
  }
  for (const u of f.urgenciaLista || []) {
    ativos.push({
      key: `urgencia:${u}`,
      kind: 'urgencia',
      value: u,
      label: `Urgência: ${u}`
    })
  }
  if (f.equipamentoId) {
    ativos.push({
      key: 'equipamento',
      kind: 'equipamento',
      label: f.equipamentoRotulo ? `Equipamento: ${f.equipamentoRotulo}` : 'Equipamento'
    })
  }
  if (f.apenasCobrados) {
    ativos.push({ key: 'apenasCobrados', kind: 'apenasCobrados', label: 'Cobrados pelo cidadão' })
  }
  if (f.apenasReabertos) {
    ativos.push({ key: 'apenasReabertos', kind: 'apenasReabertos', label: 'Apenas reabertos' })
  }
  return ativos
})

function mostrarToast(mensagem, isErro = false) {
  toastMensagem.value = mensagem
  toastErro.value = Boolean(isErro)
  toastAberto.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastAberto.value = false
  }, isErro ? 5500 : 4500)
}

function irParaAssinaturas() {
  abaMesa.value = 'assinaturas'
}

async function onAssinaturaConcluida() {
  await Promise.all([
    recarregar(),
    notificacoesInternasStore.carregar({ silencioso: true }).catch(() => null),
    assinaturasStore.carregarPendentes().catch(() => null)
  ])
}

async function sincronizarSugestoesIa() {
  await superOSStore.buscarSugestoes(protocolosExibidos.value).catch(() => null)
}

async function abrirMapaIa(protocolo = null) {
  modoVisualizacao.value = 'mapa'
  if (protocolo?.id) {
    const sug = superOSStore.sugestaoParaProtocolo(protocolo.id)
    if (sug) {
      sugestaoDestacadaMapa.value = sug
    }
  }
  await sincronizarSugestoesIa()
}

async function recarregar() {
  try {
    await backofficeStore.carregarProtocolos()
    await sincronizarSugestoesIa()
  } catch (e) {
    dialog.info(getApiErrorMessage(e), 'Mesa de Trabalho')
  }
}

function onToggleSlaVencido() {
  backofficeStore.toggleFiltroBoolean('slaVencido')
  recarregar()
}

function onToggleUrgentes() {
  backofficeStore.toggleFiltroBoolean('urgentes')
  recarregar()
}

function removerFiltro(key) {
  if (key === 'busca') {
    backofficeStore.setFiltro('busca', '')
  } else if (key === 'slaVencido' || key === 'urgentes') {
    backofficeStore.setFiltro(key, false)
  } else {
    const item = filtrosAtivosArray.value.find((x) => x.key === key)
    if (!item?.kind) return
    const f = { ...filtros.value }
    if (item.kind === 'unidade') {
      f.unidadesIds = f.unidadesIds.filter((id) => id !== item.id)
    } else if (item.kind === 'servico') {
      f.servicoIds = f.servicoIds.filter((id) => id !== item.id)
    } else if (item.kind === 'bairro') {
      f.bairros = f.bairros.filter((b) => b !== item.value)
    } else if (item.kind === 'status') {
      f.statusLista = f.statusLista.filter((s) => s !== item.value)
    } else if (item.kind === 'urgencia') {
      f.urgenciaLista = f.urgenciaLista.filter((u) => u !== item.value)
    } else if (item.kind === 'equipamento') {
      f.equipamentoId = ''
      f.equipamentoRotulo = ''
    } else if (item.kind === 'apenasCobrados') {
      f.apenasCobrados = false
    } else if (item.kind === 'apenasReabertos') {
      f.apenasReabertos = false
    }
    backofficeStore.aplicarFiltrosAvancados({
      unidadesIds: f.unidadesIds,
      servicoIds: f.servicoIds,
      bairros: f.bairros,
      statusLista: f.statusLista,
      urgenciaLista: f.urgenciaLista,
      equipamentoId: f.equipamentoId,
      equipamentoRotulo: f.equipamentoRotulo,
      apenasCobrados: f.apenasCobrados,
      apenasReabertos: f.apenasReabertos
    })
  }
  recarregar()
}

function limparFiltrosERecarregar() {
  backofficeStore.limparFiltros()
  recarregar()
}

async function abrirFiltrosAvancados() {
  try {
    await backofficeStore.carregarOpcoesFiltrosMesa()
  } catch (e) {
    dialog.info(getApiErrorMessage(e, 'Não foi possível carregar opções de filtro.'), 'Filtros')
  }
  mostrarFiltrosAvancados.value = true
}

function aplicarFiltrosAvancados(payload) {
  backofficeStore.aplicarFiltrosAvancados(payload)
  mostrarFiltrosAvancados.value = false
  recarregar()
}

const despachoModoSuperOs = ref(false)

async function integrarAncoraSuperOs(item) {
  if (!item?.id) return
  try {
    await superOSStore.integrarAncoraSuperOS(item.id)
    mostrarToast(
      `OS do setorial integrada à ${item.codigo}. Incidente unificado em andamento.`
    )
    await recarregar()
  } catch (e) {
    dialog.info(
      getApiErrorMessage(e, 'Não foi possível integrar a ordem existente.'),
      'Integração'
    )
  }
}

function abrirDespacho(item) {
  if (item?.precisaIntegracaoAncora) {
    integrarAncoraSuperOs(item)
    return
  }
  if (item?.tipo === 'super_os') {
    router.push({
      name: 'backoffice-super-os-detalhes',
      params: { id: item.id },
      query: { despachar: '1' }
    })
    return
  }
  despachoModoSuperOs.value = false
  protocoloSelecionado.value = item
  prefillOrdens.value = []
  mostrarDespacho.value = true
}

function fecharDespacho() {
  mostrarDespacho.value = false
  prefillOrdens.value = []
  setTimeout(() => {
    protocoloSelecionado.value = null
  }, 300)
}

async function confirmarDespacho(payload) {
  if (!protocoloSelecionado.value?.id) return
  if (despachoModoSuperOs.value) return
  try {
    await backofficeStore.despacharProtocolo(protocoloSelecionado.value.id, payload)
    fecharDespacho()
    mostrarToast('Despacho realizado com sucesso.')
    await backofficeStore.carregarProtocolos()
    notificacoesInternasStore.carregar({ silencioso: true }).catch(() => null)
  } catch (e) {
    dialog.info(
      getApiErrorMessage(e, 'Não foi possível concluir o despacho.'),
      'Erro no despacho'
    )
  }
}

function verDetalhes(item) {
  const id = item.id || item.codigo || item.numero
  if (item.tipo === 'super_os') {
    router.push({ name: 'backoffice-super-os-detalhes', params: { id } })
    return
  }
  router.push({ name: 'backoffice-protocolo-detalhes', params: { id } })
}

// Funções para Mapa & IA
async function carregarSugestoesIA() {
  try {
    await superOSStore.buscarSugestoes(protocolosExibidos.value)
    mostrarToast('Sugestões de IA atualizadas')
  } catch (error) {
    mostrarToast(
      getApiErrorMessage(error, 'Erro ao atualizar sugestões de IA'),
      true
    )
  }
}

async function aposCriarSuperOS() {
  await recarregar()
  await superOSStore.buscarSugestoes(protocolosExibidos.value).catch(() => null)
}

function destacarSugestaoNoMapa(sugestao) {
  sugestaoDestacadaMapa.value = sugestao
  
  // Limpar destaque após 3 segundos
  setTimeout(() => {
    sugestaoDestacadaMapa.value = null
  }, 3000)
}

async function onSugestaoAprovada(dados) {
  const codigo = dados.codigo ? ` (${dados.codigo})` : ''
  if (dados.tipo_acao === 'anexar') {
    mostrarToast(
      `Protocolo(s) anexado(s) à Super OS${codigo} · ${dados.protocolos} item(ns).`
    )
  } else if (dados.tipo_acao === 'criar_retroativa') {
    mostrarToast(
      `Super OS retroativa criada${codigo} — ${dados.protocolos} protocolo(s) unidos à âncora.`
    )
  } else {
    mostrarToast(
      `Super OS criada${codigo}: ${dados.titulo} · ${dados.protocolos} protocolo(s).`
    )
  }
  await aposCriarSuperOS()
}

async function onSuperOSCriada(dados) {
  const codigo = dados.codigo ? ` (${dados.codigo})` : ''
  mostrarToast(
    `Super OS criada${codigo}: ${dados.titulo} · ${dados.quantidade} protocolo(s).`
  )
  await aposCriarSuperOS()
}

watchDebounced(
  () => filtros.value.busca,
  () => recarregar(),
  { debounce: 450 }
)

watch(modoVisualizacao, async () => {
  try {
    await sincronizarSugestoesIa()
  } catch (e) {
    if (modoVisualizacao.value === 'mapa') {
      mostrarToast(getApiErrorMessage(e, 'Erro ao carregar dados do mapa.'), true)
    }
  }
})

onMounted(async () => {
  await Promise.all([
    backofficeStore.carregarUnidades().catch(() => {}),
    backofficeStore.carregarOpcoesFiltrosMesa().catch(() => null),
    recarregar(),
    assinaturasStore.carregarPendentes().catch(() => null)
  ])
  await superOSStore.buscarSugestoes(protocolosExibidos.value).catch(() => null)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.mesa-toast {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  transform: translateX(-50%);
  z-index: 60;
  padding: 0.875rem 1.25rem;
  border-radius: 0.75rem;
  background: #059669;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  box-shadow: 0 10px 25px rgb(5 150 105 / 0.35);
}

.mesa-toast--erro {
  background: #dc2626;
  box-shadow: 0 10px 25px rgb(220 38 38 / 0.35);
}

.mesa-toast-enter-active,
.mesa-toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.mesa-toast-enter-from,
.mesa-toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(0.5rem);
}
</style>
