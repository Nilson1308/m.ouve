<template>
  <div class="card overflow-hidden">
    <div
      v-if="!protocolos.length"
      class="flex flex-col items-center justify-center py-16 px-6 text-center"
      role="status"
    >
      <InboxIcon class="w-14 h-14 text-gray-300 dark:text-gray-600 opacity-75 mb-4" aria-hidden="true" />
      <p class="text-base font-semibold text-gray-800 dark:text-gray-200">Nenhum protocolo nesta lista</p>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-2 max-w-md">
        Ajuste os filtros ou aguarde novos despachos — os registros aparecerão na tabela assim que forem atribuídos à sua mesa.
      </p>
    </div>
    <!-- Tabela -->
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <tr>
            <th
              v-for="coluna in colunas"
              :key="coluna.key"
              @click="coluna.sortable && ordenar(coluna.key)"
              :class="[
                'px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider',
                { 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-200': coluna.sortable }
              ]"
            >
              <div class="flex items-center gap-2">
                <span>{{ coluna.label }}</span>
                <div v-if="coluna.sortable" class="flex flex-col">
                  <ChevronUpIcon
                    :class="[
                      'w-3 h-3 -mb-1',
                      ordenacao.campo === coluna.key && ordenacao.direcao === 'asc'
                        ? 'text-primary-600 dark:text-primary-400'
                        : 'text-gray-400'
                    ]"
                  />
                  <ChevronDownIcon
                    :class="[
                      'w-3 h-3',
                      ordenacao.campo === coluna.key && ordenacao.direcao === 'desc'
                        ? 'text-primary-600 dark:text-primary-400'
                        : 'text-gray-400'
                    ]"
                  />
                </div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="protocolo in protocolosOrdenados"
            :key="protocolo.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-150 cursor-pointer"
            @click="emit('detalhes', protocolo)"
          >
            <!-- Protocolo -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <div
                  :class="[
                    'w-1 h-12 rounded-full',
                    protocolo.sla.vencido ? 'bg-danger-500' :
                    protocolo.sla.horasRestantes <= 24 ? 'bg-warning-500' :
                    'bg-success-500'
                  ]"
                ></div>
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <span
                      class="text-sm font-mono font-semibold"
                      :class="
                        protocolo.tipo === 'super_os'
                          ? 'text-orange-600 dark:text-orange-400'
                          : 'text-primary-600 dark:text-primary-400'
                      "
                    >
                      {{ protocolo.numero }}
                    </span>
                    <span
                      v-if="protocolo.tipo === 'super_os'"
                      class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-gradient-to-r from-orange-500/20 to-red-500/20 text-orange-900 dark:text-orange-200 border border-orange-400/40"
                    >
                      🔥 Super OS
                    </span>
                    <span
                      v-if="protocoloNaIa(protocolo.id)"
                      class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide bg-gradient-to-r from-primary-500/15 to-purple-500/15 text-primary-800 dark:text-primary-200 border border-primary-300/50"
                      title="IA sugere cluster"
                    >
                      ✨ IA Cluster
                    </span>
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatarData(protocolo.criadoEm) }}
                  </div>
                </div>
              </div>
            </td>

            <!-- Serviço/Solicitação -->
            <td class="px-6 py-4">
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                  <component :is="getIconeCategoria(protocolo.categoria)" class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ protocolo.servico }}
                  </div>
                  <TriagemSugeridaIndicador
                    v-if="temTriagem(protocolo)"
                    :triagem="protocolo.triagemSugerida"
                    variante="inline"
                    class="mt-0.5"
                  />
                  <div class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-1">
                    <MapPinIcon class="w-3.5 h-3.5" />
                    {{ protocolo.endereco }}
                  </div>
                </div>
              </div>
            </td>

            <!-- Cidadão -->
            <td class="px-6 py-4 whitespace-nowrap">
              <template v-if="protocolo.tipo === 'super_os'">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ protocolo.qtdFilhos }} cidadãos
                </div>
                <div class="text-xs text-orange-600 dark:text-orange-400">Incidente múltiplo</div>
              </template>
              <template v-else>
                <div class="text-sm text-gray-900 dark:text-white">{{ protocolo.cidadao.nome }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ protocolo.cidadao.telefone }}</div>
              </template>
            </td>

            <!-- Status -->
            <td class="px-6 py-4 whitespace-nowrap">
              <StatusBadge :status="protocolo.status" tipo="zeladoria" :show-icon="true" />
            </td>

            <!-- Urgência -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="urgenciaBadgeClass(protocolo.urgencia)">
                {{ urgenciaLabel(protocolo.urgencia) }}
              </span>
            </td>

            <!-- SLA -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex flex-col gap-1.5">
                <span :class="slaTextClass(protocolo.sla)" class="text-xs font-medium">
                  {{ formatarSLA(protocolo.sla) }}
                </span>
                <div class="w-24 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    :class="slaBarClass(protocolo.sla)"
                    :style="{ width: calcularProgressoSLA(protocolo.sla) + '%' }"
                    class="h-full rounded-full transition-all duration-300"
                  ></div>
                </div>
              </div>
            </td>

            <!-- Responsável -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div v-if="protocolo.responsavel" class="flex items-center gap-2">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary-500 text-white text-xs font-semibold flex items-center justify-center">
                  {{ protocolo.responsavel.iniciais }}
                </div>
                <div class="min-w-0">
                  <div class="text-sm text-gray-900 dark:text-white truncate">
                    {{ protocolo.responsavel.nome }}
                  </div>
                </div>
              </div>
              <span v-else class="text-sm text-gray-400 dark:text-gray-500">Não atribuído</span>
            </td>

            <!-- Ações -->
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex items-center justify-end gap-2">
                <button
                  v-if="protocoloNaIa(protocolo.id)"
                  type="button"
                  @click.stop="emit('ver-cluster-ia', protocolo)"
                  class="btn-action text-purple-600 hover:text-purple-900 dark:text-purple-400"
                  title="Ver cluster sugerido pela IA"
                >
                  <SparklesIcon class="w-5 h-5" />
                </button>
                <button
                  v-if="podeDespachar(protocolo)"
                  @click.stop="emit('despachar', protocolo)"
                  class="btn-action text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
                  :title="protocolo.tipo === 'super_os' ? 'Gestão Super OS' : 'Despachar'"
                >
                  <PaperAirplaneIcon class="w-5 h-5" />
                </button>
                <button
                  @click.stop="emit('detalhes', protocolo)"
                  class="btn-action text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300"
                  title="Ver detalhes"
                >
                  <EyeIcon class="w-5 h-5" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação -->
    <div class="bg-white dark:bg-gray-900 px-6 py-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700 dark:text-gray-300">
          Mostrando <span class="font-medium">{{ inicioRegistros }}</span> até 
          <span class="font-medium">{{ fimRegistros }}</span> de 
          <span class="font-medium">{{ totalProtocolos }}</span> protocolos
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="paginaAnterior"
            :disabled="paginaAtual === 1"
            class="btn-pagination"
            :class="{ 'opacity-50 cursor-not-allowed': paginaAtual === 1 }"
          >
            <ChevronLeftIcon class="w-5 h-5" />
          </button>
          <span class="text-sm text-gray-700 dark:text-gray-300">
            Página {{ paginaAtual }} de {{ totalPaginas }}
          </span>
          <button
            @click="proximaPagina"
            :disabled="paginaAtual === totalPaginas"
            class="btn-pagination"
            :class="{ 'opacity-50 cursor-not-allowed': paginaAtual === totalPaginas }"
          >
            <ChevronRightIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import {
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  MapPinIcon,
  PaperAirplaneIcon,
  EyeIcon,
  WrenchScrewdriverIcon,
  LightBulbIcon,
  TrashIcon,
  SparklesIcon,
  InboxIcon
} from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import TriagemSugeridaIndicador from '@/components/backoffice/protocolo/TriagemSugeridaIndicador.vue'
import { useSuperOSStore } from '@/stores/super_os'
import { temTriagemEncaminhamento } from '@/utils/triagemEncaminhamento'

const superOSStore = useSuperOSStore()
const { idsComSugestaoIa } = storeToRefs(superOSStore)

const STATUS_PROTOCOLO_ENCERRADO = ['resolvido', 'rejeitado', 'aguardando_revisao']

function protocoloNaIa(id) {
  return idsComSugestaoIa.value.has(String(id))
}

function temTriagem(protocolo) {
  return temTriagemEncaminhamento(protocolo)
}

function podeDespachar(protocolo) {
  if (STATUS_PROTOCOLO_ENCERRADO.includes(protocolo.status)) return false
  if (protocolo.tipo === 'super_os' && protocolo.status !== 'em_analise') return false
  return true
}

const props = defineProps({
  protocolos: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['despachar', 'detalhes', 'ver-cluster-ia'])

// Paginação
const paginaAtual = ref(1)
const itensPorPagina = ref(10)

const totalProtocolos = computed(() => props.protocolos.length)
const totalPaginas = computed(() => Math.ceil(totalProtocolos.value / itensPorPagina.value))
const inicioRegistros = computed(() => (paginaAtual.value - 1) * itensPorPagina.value + 1)
const fimRegistros = computed(() => Math.min(paginaAtual.value * itensPorPagina.value, totalProtocolos.value))

// Ordenação
const ordenacao = ref({
  campo: 'criadoEm',
  direcao: 'desc'
})

const colunas = [
  { key: 'numero', label: 'Protocolo', sortable: true },
  { key: 'servico', label: 'Serviço/Solicitação', sortable: true },
  { key: 'cidadao', label: 'Cidadão', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'urgencia', label: 'Urgência', sortable: true },
  { key: 'sla', label: 'SLA', sortable: true },
  { key: 'responsavel', label: 'Responsável', sortable: false },
  { key: 'acoes', label: 'Ações', sortable: false }
]

// Protocolos ordenados e paginados
const protocolosOrdenados = computed(() => {
  let resultado = [...props.protocolos]

  // Ordenar
  resultado.sort((a, b) => {
    let valorA, valorB

    switch (ordenacao.value.campo) {
      case 'numero':
        valorA = a.numero
        valorB = b.numero
        break
      case 'servico':
        valorA = a.servico
        valorB = b.servico
        break
      case 'cidadao':
        valorA = a.cidadao.nome
        valorB = b.cidadao.nome
        break
      case 'status':
        valorA = a.status
        valorB = b.status
        break
      case 'urgencia':
        const ordemUrgencia = { baixa: 1, media: 2, alta: 3, critica: 4 }
        valorA = ordemUrgencia[a.urgencia]
        valorB = ordemUrgencia[b.urgencia]
        break
      case 'sla':
        valorA = a.sla.horasRestantes
        valorB = b.sla.horasRestantes
        break
      default:
        valorA = a.criadoEm
        valorB = b.criadoEm
    }

    if (ordenacao.value.direcao === 'asc') {
      return valorA > valorB ? 1 : -1
    } else {
      return valorA < valorB ? 1 : -1
    }
  })

  // Paginar
  const inicio = (paginaAtual.value - 1) * itensPorPagina.value
  const fim = inicio + itensPorPagina.value
  return resultado.slice(inicio, fim)
})

// Métodos
function ordenar(campo) {
  if (ordenacao.value.campo === campo) {
    ordenacao.value.direcao = ordenacao.value.direcao === 'asc' ? 'desc' : 'asc'
  } else {
    ordenacao.value.campo = campo
    ordenacao.value.direcao = 'asc'
  }
}

function paginaAnterior() {
  if (paginaAtual.value > 1) {
    paginaAtual.value--
  }
}

function proximaPagina() {
  if (paginaAtual.value < totalPaginas.value) {
    paginaAtual.value++
  }
}

function formatarData(data) {
  const date = new Date(data)
  const hoje = new Date()
  const diffHoras = Math.floor((hoje - date) / (1000 * 60 * 60))
  
  if (diffHoras < 1) return 'Agora há pouco'
  if (diffHoras < 24) return `Há ${diffHoras}h`
  
  const diffDias = Math.floor(diffHoras / 24)
  if (diffDias === 1) return 'Ontem'
  if (diffDias < 7) return `Há ${diffDias} dias`
  
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

function formatarSLA(sla) {
  if (sla.vencido) {
    const horas = Math.abs(sla.horasRestantes)
    return `Atrasado ${horas}h`
  }
  if (sla.horasRestantes < 24) {
    return `${sla.horasRestantes}h restantes`
  }
  const dias = Math.floor(sla.horasRestantes / 24)
  return `${dias}d restantes`
}

function calcularProgressoSLA(sla) {
  if (sla.vencido) return 100
  const totalHoras = 168
  const progresso = ((totalHoras - sla.horasRestantes) / totalHoras) * 100
  return Math.min(Math.max(progresso, 0), 100)
}

function slaTextClass(sla) {
  if (sla.vencido) return 'text-danger-600 dark:text-danger-400'
  if (sla.horasRestantes <= 24) return 'text-warning-600 dark:text-warning-400'
  return 'text-success-600 dark:text-success-400'
}

function slaBarClass(sla) {
  if (sla.vencido) return 'bg-danger-500'
  if (sla.horasRestantes <= 24) return 'bg-warning-500'
  return 'bg-success-500'
}

function urgenciaLabel(urgencia) {
  const labels = {
    baixa: 'Baixa',
    media: 'Média',
    alta: 'Alta',
    critica: 'Crítica'
  }
  return labels[urgencia] || urgencia
}

function urgenciaBadgeClass(urgencia) {
  const classes = {
    baixa: 'badge bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300',
    media: 'badge bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300',
    alta: 'badge bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300',
    critica: 'badge bg-danger-200 text-danger-900 dark:bg-danger-800 dark:text-danger-200 animate-pulse'
  }
  return classes[urgencia] || classes.baixa
}

function getIconeCategoria(categoria) {
  const icones = {
    via_publica: WrenchScrewdriverIcon,
    iluminacao: LightBulbIcon,
    limpeza: TrashIcon,
    arborizacao: SparklesIcon,
    calcada: WrenchScrewdriverIcon,
    sinalizacao: SparklesIcon
  }
  return icones[categoria] || WrenchScrewdriverIcon
}
</script>

<style scoped>
.btn-action {
  @apply p-1.5 rounded-lg transition-all duration-200;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800;
}

.btn-pagination {
  @apply px-3 py-2 rounded-button border border-gray-300 dark:border-gray-600;
  @apply bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200;
}
</style>
