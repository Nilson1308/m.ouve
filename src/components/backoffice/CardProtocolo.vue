<template>
  <div
    class="card-protocolo group"
    :class="[
      slaClass,
      { 'ring-2 ring-danger-500': protocolo.sla.vencido && !modoValidacao },
      { 'ring-2 ring-purple-500 dark:ring-purple-400': modoValidacao },
      {
        'ring-2 ring-primary-400/80 dark:ring-primary-500/70 shadow-md shadow-primary-500/10':
          temSugestaoClusterIa && !modoValidacao
      }
    ]"
  >
    <!-- Cabeçalho do Card -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1 min-w-0">
        <!-- Número do Protocolo -->
        <div class="flex flex-wrap items-center gap-2 mb-1">
          <span class="text-xs font-mono font-semibold text-primary-600 dark:text-primary-400">
            {{ protocolo.numero }}
          </span>
          <span
            v-if="temSugestaoClusterIa"
            class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wide bg-gradient-to-r from-primary-500/15 to-purple-500/15 text-primary-800 dark:text-primary-200 border border-primary-300/50 dark:border-primary-600/40"
            title="A IA sugere agrupamento deste protocolo"
          >
            <span aria-hidden="true">✨</span>
            IA Sugere Cluster
          </span>
          <span
            v-if="protocolo.sla.vencido"
            class="badge badge-sm bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300"
          >
            Atrasado
          </span>
        </div>
        
        <!-- Serviço -->
        <h4 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 line-clamp-2">
          {{ typeof protocolo.servico === 'string' ? protocolo.servico : protocolo.servico?.nome }}
        </h4>
        
        <!-- Endereço -->
        <div class="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
          <MapPinIcon class="w-3.5 h-3.5 flex-shrink-0" />
          <span class="truncate">{{ protocolo.endereco }}</span>
        </div>
      </div>

      <!-- Badge de Urgência -->
      <div class="ml-2 flex-shrink-0">
        <span :class="urgenciaClass">
          <BoltIcon v-if="protocolo.urgencia === 'alta' || protocolo.urgencia === 'critica'" class="w-3.5 h-3.5" />
        </span>
      </div>
    </div>

    <!-- Informações Adicionais -->
    <div class="space-y-2 mb-3">
      <!-- Cidadão -->
      <div class="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300">
        <UserIcon class="w-3.5 h-3.5 text-gray-400" />
        <span class="truncate">{{ protocolo.cidadao.nome }}</span>
      </div>

      <!-- Scatter-gather: progresso dos nós -->
      <div v-if="protocolo.ordens_servico?.length" class="space-y-1.5">
        <div class="flex items-center justify-between gap-2 text-[11px]">
          <span class="font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-1">
            <CheckCircleIcon class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            {{ nosResumo.fechados }}/{{ nosResumo.total }} secretarias
          </span>
          <span class="text-gray-500 dark:text-gray-400">{{ nosResumo.percentual }}%</span>
        </div>
        <div class="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full bg-emerald-500 transition-all duration-300"
            :style="{ width: nosResumo.percentual + '%' }"
          />
        </div>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="ordem in protocolo.ordens_servico"
            :key="ordem.id"
            class="badge badge-sm"
            :class="
              noFechado(ordem)
                ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200'
                : 'bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200'
            "
            :title="legendaStatusNo(ordem)"
          >
            {{ emojiStatusNo(ordem) }}
            {{ nomeSecretariaNo(ordem) }}
          </span>
        </div>
        <div
          v-if="destacarNosAbertos && nosAbertosLista.length"
          class="rounded-md border border-amber-200 dark:border-amber-800 bg-amber-50/80 dark:bg-amber-900/20 px-2 py-1.5 text-[11px] text-amber-900 dark:text-amber-100"
        >
          <span class="font-semibold">Nós pendentes:</span>
          <span class="ml-1">{{ rotuloNosAbertos }}</span>
        </div>
        <p
          v-else-if="modoValidacao && nosResumo.total"
          class="text-[11px] font-medium text-purple-700 dark:text-purple-300"
        >
          Todos os nós encerrados · pronto para validação
        </p>
      </div>

      <!-- Responsável/Departamento -->
      <div v-else-if="protocolo.responsavel" class="flex items-center gap-2">
        <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500 text-white text-xs font-semibold flex items-center justify-center">
          {{ protocolo.responsavel.iniciais }}
        </div>
        <span class="text-xs text-gray-700 dark:text-gray-300 truncate">
          {{ protocolo.responsavel.nome }}
        </span>
      </div>
    </div>

    <div
      v-if="temSugestaoClusterIa && resumoSugestaoIa"
      class="mb-3 rounded-lg border border-primary-200 dark:border-primary-700 bg-gradient-to-r from-primary-50/90 to-purple-50/70 dark:from-primary-950/30 dark:to-purple-950/20 px-2.5 py-2"
    >
      <p class="text-[11px] font-semibold text-primary-900 dark:text-primary-100 leading-snug">
        {{
          resumoSugestaoIa.tipo_acao === 'anexar'
            ? `Anexar à Super OS ${resumoSugestaoIa.super_os_codigo || ''}`
            : `Cluster com ${resumoSugestaoIa.quantidade} protocolo(s) similares`
        }}
      </p>
      <button
        type="button"
        class="mt-1.5 text-[11px] font-bold text-primary-700 dark:text-primary-300 hover:underline"
        @click.stop="emit('ver-cluster-ia', protocolo)"
      >
        Ver sugestão no mapa →
      </button>
    </div>

    <!-- Status Badge -->
    <div class="mb-3">
      <StatusBadge :status="protocolo.status" tipo="zeladoria" :show-icon="true" size="sm" />
    </div>

    <!-- Barra de SLA -->
    <div class="mb-3">
      <div class="flex items-center justify-between text-xs mb-1">
        <span class="text-gray-600 dark:text-gray-400 font-medium">SLA</span>
        <span :class="slaTextClass">
          {{ formatarSLA(protocolo.sla) }}
        </span>
      </div>
      <div class="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          :class="slaBarClass"
          :style="{ width: calcularProgressoSLA(protocolo.sla) + '%' }"
          class="h-full rounded-full transition-all duration-300"
        ></div>
      </div>
    </div>

    <!-- Tags/Anexos -->
    <div class="flex items-center gap-2 mb-3">
      <div v-if="protocolo.temAnexos" class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <PaperClipIcon class="w-3.5 h-3.5" />
      </div>
      <div v-if="protocolo.temLocalizacao" class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <MapIcon class="w-3.5 h-3.5" />
      </div>
      <div class="flex-1 flex gap-1 overflow-x-auto">
        <span
          v-for="tag in protocolo.tags.slice(0, 2)"
          :key="tag"
          class="badge badge-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          {{ tag }}
        </span>
      </div>
    </div>

    <!-- Ações -->
    <div class="flex items-center gap-2 pt-3 border-t border-gray-200 dark:border-gray-700">
      <button
        v-if="modoValidacao"
        type="button"
        class="flex-1 btn-sm bg-purple-600 hover:bg-purple-700 text-white group-hover:shadow-button-hover transition-all duration-200"
        @click="emit('detalhes', protocolo)"
      >
        <ShieldCheckIcon class="w-4 h-4 mr-1.5" />
        Validar protocolo
      </button>
      <template v-else-if="protocoloEncerrado">
        <button
          type="button"
          class="flex-1 btn-sm btn-secondary group-hover:shadow-button-hover transition-all duration-200"
          @click="emit('detalhes', protocolo)"
        >
          <EyeIcon class="w-4 h-4 mr-1.5" />
          Detalhes
        </button>
      </template>
      <template v-else>
        <button
          type="button"
          class="flex-1 btn-sm btn-primary group-hover:shadow-button-hover transition-all duration-200"
          @click="emit('despachar', protocolo)"
        >
          <PaperAirplaneIcon class="w-4 h-4 mr-1.5" />
          Despachar
        </button>
        <button type="button" class="btn-sm btn-secondary" @click="emit('detalhes', protocolo)">
          <EyeIcon class="w-4 h-4" />
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useSuperOSStore } from '@/stores/super_os'
import {
  MapPinIcon,
  UserIcon,
  BoltIcon,
  PaperClipIcon,
  MapIcon,
  PaperAirplaneIcon,
  EyeIcon,
  CheckCircleIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import {
  resumoNos,
  noFechado,
  emojiStatusNo,
  legendaStatusNo,
  nomeSecretariaNo,
  nosAbertos
} from '@/utils/scatterGather'

const superOSStore = useSuperOSStore()
const { idsComSugestaoIa } = storeToRefs(superOSStore)

const props = defineProps({
  protocolo: {
    type: Object,
    required: true
  },
  destacarNosAbertos: {
    type: Boolean,
    default: false
  },
  modoValidacao: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['despachar', 'detalhes', 'ver-cluster-ia'])

const STATUS_PROTOCOLO_ENCERRADO = ['resolvido', 'rejeitado']

const protocoloEncerrado = computed(() =>
  STATUS_PROTOCOLO_ENCERRADO.includes(props.protocolo?.status)
)

const temSugestaoClusterIa = computed(() =>
  idsComSugestaoIa.value.has(String(props.protocolo.id))
)

const resumoSugestaoIa = computed(() =>
  superOSStore.sugestaoResumoProtocolo(props.protocolo.id)
)

const nosResumo = computed(() => resumoNos(props.protocolo.ordens_servico))

const nosAbertosLista = computed(() => nosAbertos(props.protocolo.ordens_servico))

const rotuloNosAbertos = computed(() =>
  nosAbertosLista.value.map((o) => nomeSecretariaNo(o)).join(' · ')
)

// Classes de urgência
const urgenciaClass = computed(() => {
  const classes = {
    baixa: 'w-8 h-8 rounded-lg bg-success-100 dark:bg-success-900 text-success-600 dark:text-success-400 flex items-center justify-center',
    media: 'w-8 h-8 rounded-lg bg-warning-100 dark:bg-warning-900 text-warning-600 dark:text-warning-400 flex items-center justify-center',
    alta: 'w-8 h-8 rounded-lg bg-danger-100 dark:bg-danger-900 text-danger-600 dark:text-danger-400 flex items-center justify-center',
    critica: 'w-8 h-8 rounded-lg bg-danger-200 dark:bg-danger-800 text-danger-700 dark:text-danger-300 flex items-center justify-center animate-pulse'
  }
  return classes[props.protocolo.urgencia] || classes.baixa
})

// Classes de SLA
const slaClass = computed(() => {
  if (props.protocolo.sla.vencido) {
    return 'border-l-4 border-danger-500'
  }
  if (props.protocolo.sla.horasRestantes <= 24) {
    return 'border-l-4 border-warning-500'
  }
  return 'border-l-4 border-success-500'
})

const slaTextClass = computed(() => {
  if (props.protocolo.sla.vencido) {
    return 'text-danger-600 dark:text-danger-400 font-semibold'
  }
  if (props.protocolo.sla.horasRestantes <= 24) {
    return 'text-warning-600 dark:text-warning-400 font-semibold'
  }
  return 'text-success-600 dark:text-success-400 font-medium'
})

const slaBarClass = computed(() => {
  if (props.protocolo.sla.vencido) {
    return 'bg-danger-500'
  }
  if (props.protocolo.sla.horasRestantes <= 24) {
    return 'bg-warning-500'
  }
  return 'bg-success-500'
})

// Formatar SLA
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

// Calcular progresso do SLA
function calcularProgressoSLA(sla) {
  if (sla.vencido) return 100
  const totalHoras = sla.slaHoras || 168
  if (!totalHoras) return 0
  const progresso = ((totalHoras - sla.horasRestantes) / totalHoras) * 100
  return Math.min(Math.max(progresso, 0), 100)
}
</script>

<style scoped>
.card-protocolo {
  @apply card p-4 cursor-pointer transition-all duration-200;
  @apply hover:shadow-card-hover hover:-translate-y-0.5;
}

.btn-sm {
  @apply px-3 py-2 rounded-button text-xs font-medium transition-all duration-200;
  @apply inline-flex items-center justify-center;
}

.badge-sm {
  @apply px-2 py-0.5 text-xs;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
