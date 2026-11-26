<template>
  <div
    class="card-super-os group relative"
    :class="[
      slaClass,
      { 'ring-2 ring-danger-500': item.sla.vencido && !modoValidacao },
      { 'ring-2 ring-purple-500 dark:ring-purple-400': modoValidacao }
    ]"
  >
    <div
      class="absolute -right-1 -top-1 h-[calc(100%-6px)] w-[calc(100%-6px)] rounded-card border border-orange-300/40 dark:border-orange-600/30 bg-orange-50/50 dark:bg-orange-950/20 -z-[1] shadow-sm"
      aria-hidden="true"
    />
    <div
      class="absolute -right-0.5 -top-0.5 h-[calc(100%-3px)] w-[calc(100%-3px)] rounded-card border border-amber-400/30 dark:border-amber-500/25 bg-amber-50/30 dark:bg-amber-950/15 -z-[2]"
      aria-hidden="true"
    />

    <div class="relative z-[1]">
      <span
        class="inline-flex items-center gap-1.5 mb-3 px-2.5 py-1 rounded-lg text-xs font-bold bg-gradient-to-r from-orange-500 to-red-600 text-white shadow-md"
      >
        <span aria-hidden="true">🔥</span>
        Super OS — {{ item.qtdFilhos || 0 }} Protocolos
      </span>

      <div class="flex items-start justify-between mb-3">
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap items-center gap-2 mb-1">
            <span class="text-xs font-mono font-semibold text-orange-700 dark:text-orange-300">
              {{ item.codigo }}
            </span>
            <span
              v-if="item.sla.vencido"
              class="badge badge-sm bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300"
            >
              Atrasado
            </span>
          </div>
          <h4 class="font-semibold text-gray-900 dark:text-white text-sm mb-1 line-clamp-2">
            {{ item.titulo || item.servico }}
          </h4>
          <div class="flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-400">
            <MapPinIcon class="w-3.5 h-3.5 flex-shrink-0" />
            <span class="truncate">{{ item.endereco || 'Região consolidada' }}</span>
          </div>
        </div>
        <div class="ml-2 flex-shrink-0">
          <UrgenciaBadge :nivel="item.urgencia" size="md" />
        </div>
      </div>

      <p class="text-[11px] text-gray-500 dark:text-gray-400 mb-3">
        Incidente em massa · {{ item.qtdFilhos || 0 }} cidadãos na mesma região
      </p>

      <StatusBadge :status="item.status" tipo="zeladoria" :show-icon="true" size="sm" class="mb-3" />

      <div class="mb-3">
        <div class="flex items-center justify-between text-xs mb-1">
          <span class="text-gray-600 dark:text-gray-400 font-medium">SLA agregado</span>
          <span :class="slaTextClass">{{ formatarSLA(item.sla) }}</span>
        </div>
        <div class="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            :class="slaBarClass"
            :style="{ width: calcularProgressoSLA(item.sla) + '%' }"
            class="h-full rounded-full transition-all duration-300"
          />
        </div>
      </div>

      <div class="flex items-center gap-2 pt-3 border-t border-gray-200 dark:border-gray-700">
        <button
          v-if="modoValidacao"
          type="button"
          class="flex-1 btn-sm bg-purple-600 hover:bg-purple-700 text-white"
          @click="emit('detalhes', item)"
        >
          <ShieldCheckIcon class="w-4 h-4 mr-1.5" />
          Validar incidente
        </button>
        <template v-else-if="superOsEncerrado">
          <button
            type="button"
            class="flex-1 btn-sm btn-secondary"
            @click="emit('detalhes', item)"
          >
            <EyeIcon class="w-4 h-4 mr-1.5" />
            Detalhes
          </button>
        </template>
        <template v-else>
          <button
            v-if="item.precisaIntegracaoAncora"
            type="button"
            class="flex-1 btn-sm bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white"
            @click="emit('integrar', item)"
          >
            <PaperAirplaneIcon class="w-4 h-4 mr-1.5" />
            Integrar OS do Setorial
          </button>
          <button
            v-else-if="item.status === 'em_analise'"
            type="button"
            class="flex-1 btn-sm bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white"
            @click="emit('despachar', item)"
          >
            <PaperAirplaneIcon class="w-4 h-4 mr-1.5" />
            Despachar Super OS
          </button>
          <button
            v-else
            type="button"
            class="flex-1 btn-sm bg-gradient-to-r from-orange-500 to-red-600 text-white"
            @click="emit('detalhes', item)"
          >
            <EyeIcon class="w-4 h-4 mr-1.5" />
            Gestão consolidada
          </button>
          <button type="button" class="btn-sm btn-secondary" @click="emit('detalhes', item)">
            <EyeIcon class="w-4 h-4" />
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  MapPinIcon,
  PaperAirplaneIcon,
  EyeIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import UrgenciaBadge from '@/components/backoffice/common/UrgenciaBadge.vue'

const props = defineProps({
  item: { type: Object, required: true },
  modoValidacao: { type: Boolean, default: false }
})

const emit = defineEmits(['despachar', 'detalhes', 'integrar'])

const superOsEncerrado = computed(() =>
  ['resolvido', 'rejeitado'].includes(props.item?.status)
)

const slaClass = computed(() => {
  if (props.item.sla.vencido) return 'border-l-4 border-danger-500'
  if (props.item.sla.horasRestantes <= 24) return 'border-l-4 border-warning-500'
  return 'border-l-4 border-orange-500'
})

const slaTextClass = computed(() => {
  if (props.item.sla.vencido) return 'text-danger-600 dark:text-danger-400 font-semibold'
  if (props.item.sla.horasRestantes <= 24) return 'text-warning-600 dark:text-warning-400 font-semibold'
  return 'text-success-600 dark:text-success-400 font-medium'
})

const slaBarClass = computed(() => {
  if (props.item.sla.vencido) return 'bg-danger-500'
  if (props.item.sla.horasRestantes <= 24) return 'bg-warning-500'
  return 'bg-orange-500'
})

function formatarSLA(sla) {
  if (sla.vencido) {
    const horas = Math.abs(sla.horasRestantes)
    return `Atrasado ${horas}h`
  }
  if (sla.horasRestantes < 24) return `${sla.horasRestantes}h restantes`
  const dias = Math.floor(sla.horasRestantes / 24)
  return `${dias}d restantes`
}

function calcularProgressoSLA(sla) {
  if (sla.vencido) return 100
  const totalHoras = sla.slaHoras || 168
  if (!totalHoras) return 0
  const progresso = ((totalHoras - sla.horasRestantes) / totalHoras) * 100
  return Math.min(Math.max(progresso, 0), 100)
}
</script>

<style scoped>
.card-super-os {
  @apply card p-4 cursor-pointer transition-all duration-200 bg-white dark:bg-gray-800;
  @apply hover:shadow-card-hover hover:-translate-y-0.5;
  box-shadow:
    0 1px 2px rgba(249, 115, 22, 0.08),
    0 4px 12px rgba(234, 88, 12, 0.12);
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