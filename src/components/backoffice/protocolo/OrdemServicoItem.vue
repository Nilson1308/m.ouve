<template>
  <div class="relative">
    <!-- Indicador de Timeline -->
    <div 
      :class="[
        'absolute -left-8 w-6 h-6 rounded-full border-4 border-white dark:border-gray-900 shadow-lg',
        statusColor
      ]"
    >
      <component 
        :is="statusIcon"
        class="w-4 h-4 text-white absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
      />
    </div>

    <!-- Card da Ordem -->
    <div class="card hover:shadow-card-hover transition-shadow duration-200 overflow-hidden max-w-full">
      <!-- Header -->
      <div class="mb-4 min-w-0">
        <div class="min-w-0">
          <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-1 truncate">
            {{ ordem.unidade }}
            <span v-if="ordem.unidade_sigla" class="text-gray-500 dark:text-gray-400 font-normal">
              ({{ ordem.unidade_sigla }})
            </span>
          </h3>
          <p v-if="!visaoGestao" class="text-sm text-gray-600 dark:text-gray-400 truncate">
            {{ ordem.responsavel }}
          </p>
        </div>
        <div class="flex flex-wrap gap-1.5 mt-3 max-w-full">
          <span
            v-if="encerrado"
            class="badge text-xs font-bold inline-flex items-center gap-1 bg-emerald-600 text-white max-w-full"
          >
            <LockClosedIcon class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
            <span class="truncate">Nó fechado</span>
          </span>
          <span
            class="badge text-xs font-semibold inline-flex items-center gap-1 max-w-full"
            :class="
              encerrado
                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200'
                : 'bg-amber-100 text-amber-900 dark:bg-amber-900/30 dark:text-amber-200'
            "
          >
            <span class="shrink-0">{{ emojiStatusNo(ordem) }}</span>
            <span class="truncate">{{ encerrado ? 'Concluído' : 'Pendente' }} ({{ legendaStatusNo(ordem) }})</span>
          </span>
          <span :class="prioridadeBadgeClass" class="badge text-xs inline-flex items-center shrink-0">
            {{ prioridadeLabel }}
          </span>
          <span
            v-if="mostrarBadgeWorkflow"
            :class="statusBadgeClass"
            class="badge text-xs font-semibold inline-flex items-center max-w-full min-w-0"
            :title="statusLabel"
          >
            <span class="truncate">{{ statusLabel }}</span>
          </span>
        </div>
      </div>

      <!-- Despacho técnico -->
      <div
        v-if="mostrarDespacho"
        class="mb-4 p-4 rounded-lg border-2 border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-900/15"
      >
        <p class="text-xs font-semibold uppercase tracking-wide text-primary-700 dark:text-primary-300 mb-2">
          Despacho técnico
        </p>
        <p
          v-if="ordem.despacho_tecnico"
          class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap leading-relaxed"
        >
          {{ ordem.despacho_tecnico }}
        </p>
        <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">
          Ainda não formalizado ou aguardando elaboração setorial.
        </p>
        <p
          v-if="ordem.observacoes_extras"
          class="text-sm text-gray-600 dark:text-gray-400 mt-3 pt-3 border-t border-primary-200/60 dark:border-primary-800/60 whitespace-pre-wrap"
        >
          <span class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 block mb-1">
            Observações complementares
          </span>
          {{ ordem.observacoes_extras }}
        </p>
      </div>

      <!-- Instrução -->
      <div class="mb-4 p-3 bg-gray-50 dark:bg-gray-800/80 rounded-lg border border-gray-200 dark:border-gray-700">
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
          {{ mostrarDespacho ? 'Instrução original da OS' : 'Instrução original' }}
        </p>
        <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
          {{ ordem.instrucao }}
        </p>
      </div>

      <!-- Prazo -->
      <div class="mb-4 flex items-center gap-4 text-sm">
        <div class="flex items-center gap-2">
          <CalendarIcon class="w-4 h-4 text-gray-400" />
          <span class="text-gray-600 dark:text-gray-400">Prazo:</span>
          <span class="font-medium text-gray-900 dark:text-white">
            {{ formatarDataPrazo(ordem.prazo) }}
          </span>
        </div>
        <div v-if="ordem.concluido_em" class="flex items-center gap-2">
          <CheckCircleIcon class="w-4 h-4 text-success-500" />
          <span class="text-gray-600 dark:text-gray-400">Concluído:</span>
          <span class="font-medium text-success-600 dark:text-success-400">
            {{ formatarDataPrazo(ordem.concluido_em) }}
          </span>
        </div>
      </div>

      <!-- Observações de Execução -->
      <div
        v-if="mostrarEvidenciasCampo && ordem.observacoes_execucao"
        class="mb-4 p-3 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800"
      >
        <div class="flex items-start gap-2 mb-2">
          <DocumentTextIcon class="w-4 h-4 text-success-600 dark:text-success-400 mt-0.5 flex-shrink-0" />
          <p class="text-xs font-semibold text-success-700 dark:text-success-300">
            OBSERVAÇÕES DA EQUIPE:
          </p>
        </div>
        <p class="text-sm text-gray-700 dark:text-gray-300">
          {{ ordem.observacoes_execucao }}
        </p>
      </div>

      <!-- Materiais Utilizados -->
      <div v-if="ordem.materiais_utilizados && ordem.materiais_utilizados.length > 0" class="mb-4">
        <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
          MATERIAIS UTILIZADOS:
        </p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(material, idx) in ordem.materiais_utilizados"
            :key="idx"
            class="badge bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 text-xs"
          >
            {{ material }}
          </span>
        </div>
      </div>

      <!-- Evidências de campo -->
      <div v-if="mostrarEvidenciasCampo && evidenciasOrdem.length" class="mb-2">
        <GaleriaEvidencias :evidencias="evidenciasOrdem" somente-leitura />
      </div>
      <p
        v-else-if="mostrarEvidenciasCampo && encerrado"
        class="text-xs text-gray-500 dark:text-gray-400 italic mb-2"
      >
        Nenhuma foto de evidência registrada nesta OS.
      </p>

      <!-- Timeline de Execução -->
      <div v-if="ordem.iniciado_em" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
          <div class="flex items-center gap-1">
            <ClockIcon class="w-3 h-3" />
            <span>Iniciado: {{ formatarDataHora(ordem.iniciado_em) }}</span>
          </div>
          <div v-if="ordem.concluido_em" class="flex items-center gap-1">
            <CheckCircleIcon class="w-3 h-3 text-success-500" />
            <span>Concluído: {{ formatarDataHora(ordem.concluido_em) }}</span>
          </div>
          <div v-if="ordem.concluido_em && ordem.iniciado_em" class="flex items-center gap-1 ml-auto">
            <span class="font-medium text-gray-900 dark:text-white">
              Duração: {{ calcularDuracao(ordem.iniciado_em, ordem.concluido_em) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  CalendarIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  ClockIcon,
  LockClosedIcon
} from '@heroicons/vue/24/outline'
import GaleriaEvidencias from '@/components/backoffice/setorial/GaleriaEvidencias.vue'
import { mapFotoParaEvidencia } from '@/utils/protocoloEvidencias'
import {
  noFechado,
  emojiStatusNo,
  legendaStatusNo
} from '@/utils/scatterGather'

const props = defineProps({
  ordem: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  /** @deprecated use variant */
  visaoGestao: {
    type: Boolean,
    default: false
  },
  /** gestao | revisao | execucao */
  variant: {
    type: String,
    default: ''
  }
})

const variantEfetivo = computed(() => {
  if (props.variant) return props.variant
  if (props.visaoGestao) return 'gestao'
  return 'execucao'
})

const mostrarDespacho = computed(() => ['gestao', 'revisao'].includes(variantEfetivo.value))
const mostrarEvidenciasCampo = computed(() => ['revisao', 'execucao'].includes(variantEfetivo.value))

const evidenciasOrdem = computed(() =>
  (props.ordem.fotos_execucao || []).map((f, i) => mapFotoParaEvidencia(f, props.ordem, i))
)

const encerrado = computed(() => noFechado(props.ordem))

// Computed
const statusColor = computed(() => {
  const key = statusChave.value
  const cores = {
    concluido: 'bg-success-500',
    concluida: 'bg-success-500',
    em_andamento: 'bg-warning-500',
    pendente: 'bg-gray-400',
    cancelado: 'bg-danger-500',
    cancelada: 'bg-danger-500',
    aguardando_formalizacao: 'bg-indigo-500',
    aguardando_revisao: 'bg-purple-500',
    aguardando_assinatura: 'bg-sky-500'
  }
  return cores[key] || cores[props.ordem.status] || 'bg-gray-400'
})

const statusIcon = computed(() => {
  return CheckCircleIcon
})

const statusChave = computed(() => props.ordem.statusApi || props.ordem.status)

const mostrarBadgeWorkflow = computed(() => {
  const k = statusChave.value
  if (k === 'pendente' || k === 'em_andamento') return false
  if (variantEfetivo.value !== 'execucao' && (k === 'concluida' || k === 'concluido')) return false
  return true
})

const statusLabel = computed(() => {
  const labels = {
    concluido: 'Concluído',
    concluida: 'Concluída',
    em_andamento: 'Em andamento',
    pendente: 'Pendente',
    cancelado: 'Cancelado',
    cancelada: 'Cancelada',
    aguardando_formalizacao: 'Aguard. formalização',
    aguardando_revisao: 'Aguard. revisão',
    aguardando_assinatura: 'Aguardando gestor'
  }
  const raw = labels[statusChave.value] || labels[props.ordem.status]
  if (raw) return raw
  const s = String(props.ordem.status || statusChave.value || '')
  return s.replace(/_/g, ' ')
})

const statusBadgeClass = computed(() => {
  const key = statusChave.value
  const classes = {
    concluido: 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300',
    concluida: 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300',
    em_andamento: 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300',
    pendente: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    cancelado: 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300',
    cancelada: 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300',
    aguardando_formalizacao: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-200',
    aguardando_revisao: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-200',
    aguardando_assinatura: 'bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-200'
  }
  return classes[key] || classes[props.ordem.status] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
})

const prioridadeLabel = computed(() => {
  const labels = {
    'baixa': 'Baixa',
    'media': 'Média',
    'alta': 'Alta',
    'critica': 'Crítica'
  }
  return labels[props.ordem.prioridade] || props.ordem.prioridade
})

const prioridadeBadgeClass = computed(() => {
  const classes = {
    'baixa': 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300',
    'media': 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300',
    'alta': 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300',
    'critica': 'bg-danger-200 text-danger-900 dark:bg-danger-800 dark:text-danger-200'
  }
  return classes[props.ordem.prioridade] || ''
})

// Métodos
function formatarDataPrazo(data) {
  const date = new Date(data)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatarDataHora(data) {
  const date = new Date(data)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatarHora(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function calcularDuracao(inicio, fim) {
  const diffMs = new Date(fim) - new Date(inicio)
  const diffHoras = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutos = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (diffHoras > 0) {
    return `${diffHoras}h ${diffMinutos}min`
  }
  return `${diffMinutos}min`
}

</script>
