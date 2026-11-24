<template>
  <div
    class="bg-white dark:bg-gray-800 rounded-card shadow-card hover:shadow-card-hover transition-all cursor-pointer p-4 border-l-4"
    :class="[
      ordem.is_super_os
        ? 'border-orange-500 ring-1 ring-orange-200/50 dark:ring-orange-800/30'
        : ordem.sla_status === 'vencido'
          ? 'border-red-500'
          : ordem.sla_status === 'atencao'
            ? 'border-amber-500'
            : 'border-green-500'
    ]"
    @click="$emit('click')"
  >
    <!-- Header -->
    <div class="flex items-start justify-between mb-3 gap-2">
      <div class="flex-1 min-w-0 space-y-1">
        <BadgeSuperOS v-if="ordem.is_super_os" :ordem="ordem" />
        <p
          v-if="ordem.super_os_codigo"
          class="text-xs font-mono font-semibold text-orange-700 dark:text-orange-300 truncate"
        >
          {{ ordem.super_os_codigo }}
        </p>
        <p class="text-xs font-mono text-gray-500 dark:text-gray-400 truncate">
          {{
            ordem.is_super_os && ordem.protocolo_codigo
              ? `ref. ${ordem.protocolo_codigo}`
              : ordem.protocolo_id
          }}
        </p>
      </div>
      
      <span
        v-if="noEncerrado"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-[10px] font-bold bg-emerald-600 text-white mr-1"
        title="Nó encerrado — somente leitura"
      >
        <LockClosedIcon class="w-3 h-3" aria-hidden="true" />
        Encerrado
      </span>

      <!-- Prioridade Badge -->
      <span
        :class="[
          'inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-xs font-semibold',
          ordem.prioridade === 'urgente'
            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
            : ordem.prioridade === 'alta'
            ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
            : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
        ]"
      >
        <ExclamationCircleIcon v-if="ordem.prioridade === 'urgente'" class="w-3 h-3" />
        <FireIcon v-else-if="ordem.prioridade === 'alta'" class="w-3 h-3" />
        {{ ordem.prioridade === 'urgente' ? 'URG' : ordem.prioridade === 'alta' ? 'ALTA' : 'NORM' }}
      </span>
    </div>

    <!-- Serviço -->
    <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
      {{ ordem.servico }}
    </h4>
    <BadgeDiligenciaOS :ordem="ordem" class="mb-2" />

    <!-- Endereço -->
    <div class="flex items-start gap-1.5 text-xs text-gray-600 dark:text-gray-400 mb-3">
      <MapPinIcon class="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
      <span class="line-clamp-2">{{ ordem.endereco }}</span>
    </div>

    <!-- Prazo e SLA -->
    <div class="flex items-center justify-between mb-3 pb-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center gap-1.5">
        <ClockIcon class="w-4 h-4 text-gray-400" />
        <span class="text-xs text-gray-600 dark:text-gray-400">
          {{ formatarData(ordem.prazo_interno) }}
        </span>
      </div>
      
      <span
        :class="[
          'text-xs font-semibold',
          ordem.sla_status === 'vencido'
            ? 'text-red-600 dark:text-red-400'
            : ordem.sla_status === 'atencao'
            ? 'text-amber-600 dark:text-amber-400'
            : 'text-green-600 dark:text-green-400'
        ]"
      >
        {{ getSLALabel(ordem.sla_status, ordem.prazo_interno) }}
      </span>
    </div>

    <!-- Footer: Evidências e Magic Link -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <!-- Evidências -->
        <div class="flex items-center gap-1.5">
          <PhotoIcon
            :class="[
              'w-4 h-4',
              ordem.evidencias.length > 0
                ? 'text-green-600 dark:text-green-400'
                : 'text-gray-400'
            ]"
          />
          <span
            :class="[
              'text-sm font-semibold',
              ordem.evidencias.length > 0
                ? 'text-green-700 dark:text-green-300'
                : 'text-gray-400'
            ]"
          >
            {{ ordem.evidencias.length }}
          </span>
        </div>

        <!-- Magic Link -->
        <div v-if="ordem.magic_link" class="flex items-center gap-1.5">
          <LinkIcon class="w-4 h-4 text-primary-500" />
          <span class="text-xs text-primary-600 dark:text-primary-400 font-medium">
            Link enviado
          </span>
        </div>
      </div>

      <!-- Botão de ação -->
      <ChevronRightIcon class="w-5 h-5 text-gray-400" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BadgeSuperOS from './BadgeSuperOS.vue'
import BadgeDiligenciaOS from './BadgeDiligenciaOS.vue'
import {
  ExclamationCircleIcon,
  FireIcon,
  MapPinIcon,
  ClockIcon,
  PhotoIcon,
  LinkIcon,
  ChevronRightIcon,
  LockClosedIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  ordem: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const noEncerrado = computed(
  () =>
    props.ordem?.status === 'concluida' ||
    props.ordem?.status_api === 'concluida'
)

function getSLALabel(sla, prazo) {
  if (sla === 'vencido') return 'Vencido!'
  if (sla === 'atencao') return 'Vence hoje'
  
  const agora = new Date()
  const prazoDate = new Date(prazo)
  const diff = prazoDate - agora
  const horas = Math.floor(diff / (1000 * 60 * 60))
  
  if (horas < 24) return `${horas}h`
  const dias = Math.floor(horas / 24)
  return `${dias}d`
}

function formatarData(data) {
  const d = new Date(data)
  const dia = d.getDate().toString().padStart(2, '0')
  const mes = (d.getMonth() + 1).toString().padStart(2, '0')
  const hora = d.getHours().toString().padStart(2, '0')
  const min = d.getMinutes().toString().padStart(2, '0')
  return `${dia}/${mes} ${hora}:${min}`
}
</script>
