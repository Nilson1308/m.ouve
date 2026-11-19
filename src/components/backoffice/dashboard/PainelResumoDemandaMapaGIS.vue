<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="translate-x-8 opacity-0 lg:translate-x-full max-lg:translate-y-full"
    enter-to-class="translate-x-0 opacity-100 max-lg:translate-y-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="translate-x-0 opacity-100 max-lg:translate-y-0"
    leave-to-class="translate-x-8 opacity-0 lg:translate-x-full max-lg:translate-y-full"
  >
    <aside
      v-if="demanda"
      class="flex flex-col w-full max-w-md max-h-[min(85vh,calc(100vh-5rem))] overflow-hidden bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 rounded-xl shadow-2xl"
      role="dialog"
      aria-labelledby="resumo-demanda-titulo"
      aria-modal="true"
    >
      <header class="flex-shrink-0 px-5 pt-5 pb-3 border-b border-gray-200/60 dark:border-gray-700/60">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3 min-w-0">
            <div
              class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary-500/25"
            >
              <MapPinIcon class="w-5 h-5 text-white" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                Demanda no território
              </p>
              <h2
                id="resumo-demanda-titulo"
                class="text-sm font-mono font-bold text-primary-600 dark:text-primary-400 truncate"
              >
                {{ demanda.codigo }}
              </h2>
            </div>
          </div>
          <button
            type="button"
            class="btn-icon flex-shrink-0"
            aria-label="Fechar resumo"
            @click="$emit('fechar')"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        <div class="mt-3 flex flex-wrap items-center gap-2">
          <StatusBadge :status="demanda.status" tipo="zeladoria" :show-icon="true" size="sm" />
          <span
            v-if="demanda.sla?.vencido"
            class="badge badge-sm bg-danger-100 text-danger-700 dark:bg-danger-900/40 dark:text-danger-300"
          >
            SLA vencido
          </span>
        </div>
      </header>

      <div class="flex-1 min-h-0 overflow-y-auto overscroll-contain px-5 py-4 space-y-4">
        <section>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white leading-snug line-clamp-2">
            {{ demanda.servico?.nome || 'Serviço não informado' }}
          </h3>
          <p
            v-if="demanda.descricaoResumo"
            class="mt-2 text-sm text-gray-600 dark:text-gray-300 leading-relaxed line-clamp-4"
          >
            {{ demanda.descricaoResumo }}
          </p>
        </section>

        <section class="rounded-lg border border-gray-200/80 dark:border-gray-700/80 bg-gray-50/80 dark:bg-gray-900/40 p-3 space-y-2">
          <div v-if="demanda.bairro || demanda.endereco" class="flex gap-2 text-xs text-gray-700 dark:text-gray-300">
            <MapPinIcon class="w-4 h-4 text-primary-500 flex-shrink-0 mt-0.5" />
            <div>
              <p v-if="demanda.bairro" class="font-semibold">{{ demanda.bairro }}</p>
              <p class="text-gray-600 dark:text-gray-400 line-clamp-2">{{ demanda.endereco || 'Endereço não detalhado' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300">
            <UserIcon class="w-4 h-4 text-gray-400" />
            <span class="truncate">{{ demanda.cidadao?.nome }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
            <CalendarDaysIcon class="w-4 h-4 text-gray-400" />
            <span>Aberto em {{ dataFormatada }}</span>
          </div>
        </section>

        <section v-if="demanda.sla && !demanda.sla.vencido && demanda.sla.horasRestantes != null">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-gray-600 dark:text-gray-400 font-medium">Prazo SLA</span>
            <span class="text-emerald-700 dark:text-emerald-400 font-semibold">
              {{ textoSlaRestante }}
            </span>
          </div>
        </section>
      </div>

      <footer class="flex-shrink-0 px-5 py-4 border-t border-gray-200/60 dark:border-gray-700/60 bg-white/80 dark:bg-gray-900/50 space-y-2">
        <button
          type="button"
          class="w-full btn-primary flex items-center justify-center gap-2 py-2.5 text-sm font-semibold"
          @click="$emit('abrir-visao-360', demanda)"
        >
          <ViewfinderCircleIcon class="w-5 h-5" />
          Visão 360º da demanda
        </button>
        <button type="button" class="w-full btn-secondary py-2 text-sm" @click="$emit('fechar')">
          Continuar no mapa
        </button>
      </footer>
    </aside>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import {
  MapPinIcon,
  UserIcon,
  CalendarDaysIcon,
  XMarkIcon,
  ViewfinderCircleIcon
} from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const props = defineProps({
  demanda: {
    type: Object,
    default: null
  }
})

defineEmits(['fechar', 'abrir-visao-360'])

const dataFormatada = computed(() => {
  if (!props.demanda?.dataCriacao) return '—'
  const d = new Date(props.demanda.dataCriacao)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const textoSlaRestante = computed(() => {
  const h = props.demanda?.sla?.horasRestantes
  if (h == null) return ''
  if (h <= 0) return 'Prazo esgotado'
  if (h < 24) return `${Math.round(h)}h restantes`
  const dias = Math.floor(h / 24)
  return `${dias}d restantes`
})
</script>