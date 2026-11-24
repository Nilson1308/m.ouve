<template>
  <div>
    <!-- Loading State -->
    <div v-if="carregando" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="ordens.length === 0" class="text-center py-12">
      <InboxIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        Nenhuma Ordem de Serviço encontrada
      </h3>
      <p class="text-gray-600 dark:text-gray-400">
        Não há ordens de serviço correspondentes aos filtros selecionados.
      </p>
    </div>

    <!-- Lista -->
    <div v-else-if="visualizacao === 'lista'">
      <div class="bg-white dark:bg-gray-800 rounded-card shadow-card overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                ID / Protocolo
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Serviço / Local
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Prioridade
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Prazo / SLA
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Evidências
              </th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="ordem in ordens"
              :key="ordem.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
              :class="
                ordem.is_super_os
                  ? 'bg-orange-50/30 dark:bg-orange-950/10 hover:bg-orange-50/50 dark:hover:bg-orange-950/20'
                  : ''
              "
              @click="$emit('abrir-os', ordem)"
            >
              <!-- ID / Protocolo -->
              <td class="px-6 py-4 border-l-4" :class="ordem.is_super_os ? 'border-orange-500' : 'border-transparent'">
                <div class="flex flex-col gap-1.5">
                  <div class="flex flex-wrap items-center gap-1.5">
                    <BadgeSuperOS v-if="ordem.is_super_os" :ordem="ordem" />
                  </div>
                  <span
                    v-if="ordem.super_os_codigo"
                    class="text-sm font-semibold text-orange-700 dark:text-orange-300 font-mono"
                  >
                    {{ ordem.super_os_codigo }}
                  </span>
                  <span
                    class="text-xs font-mono"
                    :class="
                      ordem.is_super_os
                        ? 'text-gray-600 dark:text-gray-400'
                        : 'text-primary-600 dark:text-primary-400'
                    "
                  >
                    {{ ordem.is_super_os && ordem.protocolo_codigo ? `ref. ${ordem.protocolo_codigo}` : ordem.protocolo_id }}
                  </span>
                </div>
              </td>

              <!-- Serviço / Local -->
              <td class="px-6 py-4">
                <div class="flex flex-col gap-1">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ ordem.servico }}
                    <span
                      v-if="ordem.is_super_os && ordem.qtd_chamados_vinculados > 1"
                      class="ml-1 text-xs font-semibold text-orange-600 dark:text-orange-400"
                    >
                      · {{ ordem.qtd_chamados_vinculados }}×
                    </span>
                  </span>
                  <span class="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1">
                    <MapPinIcon class="w-3 h-3" />
                    {{ ordem.endereco }}
                  </span>
                </div>
              </td>

              <!-- Prioridade -->
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    ordem.prioridade === 'urgente'
                      ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                      : ordem.prioridade === 'alta'
                      ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                      : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                  ]"
                >
                  <ExclamationCircleIcon v-if="ordem.prioridade === 'urgente'" class="w-3.5 h-3.5" />
                  <FireIcon v-else-if="ordem.prioridade === 'alta'" class="w-3.5 h-3.5" />
                  {{ ordem.prioridade === 'urgente' ? 'Urgente' : ordem.prioridade === 'alta' ? 'Alta' : 'Normal' }}
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4">
                <BadgeDiligenciaOS :ordem="ordem" class="mb-2" />
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    ordem.status === 'nova'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                      : ordem.status === 'aguardando_campo'
                      ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
                      : ordem.status === 'em_execucao'
                      ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                      : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                  ]"
                >
                  <div
                    :class="[
                      'w-2 h-2 rounded-full',
                      ordem.status === 'nova' ? 'bg-blue-500' :
                      ordem.status === 'aguardando_campo' ? 'bg-amber-500' :
                      ordem.status === 'em_execucao' ? 'bg-purple-500' : 'bg-green-500'
                    ]"
                  ></div>
                  {{ getStatusLabel(ordem.status) }}
                </span>
              </td>

              <!-- Prazo / SLA -->
              <td class="px-6 py-4">
                <div class="flex flex-col gap-1">
                  <span class="text-xs text-gray-900 dark:text-white font-medium">
                    {{ formatarData(ordem.prazo_interno) }}
                  </span>
                  <span
                    :class="[
                      'text-xs font-semibold flex items-center gap-1',
                      ordem.sla_status === 'vencido'
                        ? 'text-red-600 dark:text-red-400'
                        : ordem.sla_status === 'atencao'
                        ? 'text-amber-600 dark:text-amber-400'
                        : 'text-green-600 dark:text-green-400'
                    ]"
                  >
                    <ClockIcon class="w-3.5 h-3.5" />
                    {{ getSLALabel(ordem.sla_status, ordem.prazo_interno) }}
                  </span>
                </div>
              </td>

              <!-- Evidências -->
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <div
                    v-if="ordem.evidencias.length > 0"
                    class="flex items-center gap-1.5 text-sm"
                  >
                    <PhotoIcon class="w-5 h-5 text-green-600 dark:text-green-400" />
                    <span class="font-semibold text-green-700 dark:text-green-300">
                      {{ ordem.evidencias.length }}
                    </span>
                  </div>
                  <div v-else class="flex items-center gap-1.5 text-sm text-gray-400">
                    <PhotoIcon class="w-5 h-5" />
                    <span>0</span>
                  </div>
                  
                  <!-- Magic Link Status -->
                  <LinkIcon
                    v-if="ordem.magic_link"
                    class="w-4 h-4 text-primary-500"
                    title="Link Mágico gerado"
                  />
                </div>
              </td>

              <!-- Ações -->
              <td class="px-6 py-4 text-right">
                <button
                  v-if="ordemSomenteLeitura(ordem)"
                  @click.stop="$emit('abrir-os', ordem)"
                  class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700/50 rounded-lg transition-colors border border-slate-200 dark:border-slate-600"
                >
                  <EyeIcon class="w-4 h-4" />
                  Detalhes
                </button>
                <button
                  v-else
                  @click.stop="$emit('abrir-os', ordem)"
                  class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-primary-700 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                >
                  <PencilSquareIcon class="w-4 h-4" />
                  Formalizar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Kanban -->
    <div v-else class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <!-- Coluna: Nova -->
      <div class="flex flex-col gap-4">
        <div class="bg-blue-100 dark:bg-blue-900/30 rounded-lg px-4 py-2">
          <h3 class="text-sm font-semibold text-blue-900 dark:text-blue-100">
            Nova ({{ ordensNovas.length }})
          </h3>
        </div>
        <div class="space-y-3 min-h-[8rem]">
          <CardOrdemKanban
            v-for="ordem in ordensNovas"
            :key="ordem.id"
            :ordem="ordem"
            @click="$emit('abrir-os', ordem)"
          />
          <div v-if="!ordensNovas.length" class="text-center py-8 px-2 text-sm text-gray-500 dark:text-gray-400" role="status">
            <InboxIcon class="w-10 h-10 mx-auto mb-2 opacity-50" aria-hidden="true" />
            Nenhuma OS nova para o setor.
          </div>
        </div>
      </div>

      <!-- Coluna: Aguardando Campo -->
      <div class="flex flex-col gap-4">
        <div class="bg-amber-100 dark:bg-amber-900/30 rounded-lg px-4 py-2">
          <h3 class="text-sm font-semibold text-amber-900 dark:text-amber-100">
            Aguardando Campo ({{ ordensAguardando.length }})
          </h3>
        </div>
        <div class="space-y-3 min-h-[8rem]">
          <CardOrdemKanban
            v-for="ordem in ordensAguardando"
            :key="ordem.id"
            :ordem="ordem"
            @click="$emit('abrir-os', ordem)"
          />
          <div
            v-if="!ordensAguardando.length"
            class="text-center py-8 px-2 text-sm text-gray-500 dark:text-gray-400"
            role="status"
          >
            <ClockIcon class="w-10 h-10 mx-auto mb-2 opacity-50" aria-hidden="true" />
            Nenhuma OS aguardando campo.
          </div>
        </div>
      </div>

      <!-- Coluna: Em Execução -->
      <div class="flex flex-col gap-4">
        <div class="bg-purple-100 dark:bg-purple-900/30 rounded-lg px-4 py-2">
          <h3 class="text-sm font-semibold text-purple-900 dark:text-purple-100">
            Em Execução ({{ ordensEmExecucao.length }})
          </h3>
        </div>
        <div class="space-y-3 min-h-[8rem]">
          <CardOrdemKanban
            v-for="ordem in ordensEmExecucao"
            :key="ordem.id"
            :ordem="ordem"
            @click="$emit('abrir-os', ordem)"
          />
          <div v-if="!ordensEmExecucao.length" class="text-center py-8 px-2 text-sm text-gray-500 dark:text-gray-400" role="status">
            <WrenchScrewdriverIcon class="w-10 h-10 mx-auto mb-2 opacity-50" aria-hidden="true" />
            Nenhuma OS em execução.
          </div>
        </div>
      </div>

      <!-- Coluna: Concluída -->
      <div class="flex flex-col gap-4">
        <div class="bg-green-100 dark:bg-green-900/30 rounded-lg px-4 py-2">
          <h3 class="text-sm font-semibold text-green-900 dark:text-green-100">
            Concluída ({{ ordensConcluidas.length }})
          </h3>
        </div>
        <div class="space-y-3 min-h-[8rem]">
          <CardOrdemKanban
            v-for="ordem in ordensConcluidas"
            :key="ordem.id"
            :ordem="ordem"
            @click="$emit('abrir-os', ordem)"
          />
          <div v-if="!ordensConcluidas.length" class="text-center py-8 px-2 text-sm text-gray-500 dark:text-gray-400" role="status">
            <CheckCircleIcon class="w-10 h-10 mx-auto mb-2 opacity-50" aria-hidden="true" />
            Nenhuma OS concluída no período.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  InboxIcon,
  MapPinIcon,
  ExclamationCircleIcon,
  FireIcon,
  ClockIcon,
  PhotoIcon,
  LinkIcon,
  PencilSquareIcon,
  EyeIcon,
  WrenchScrewdriverIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'
import CardOrdemKanban from './CardOrdemKanban.vue'
import BadgeSuperOS from './BadgeSuperOS.vue'
import BadgeDiligenciaOS from './BadgeDiligenciaOS.vue'

const props = defineProps({
  ordens: {
    type: Array,
    required: true
  },
  visualizacao: {
    type: String,
    required: true
  },
  carregando: {
    type: Boolean,
    default: false
  }
})

defineEmits(['abrir-os'])

function ordemSomenteLeitura(ordem) {
  return (
    ordem?.status === 'concluida' ||
    ordem?.status_api === 'concluida'
  )
}

// Ordens por status (para Kanban)
const ordensNovas = computed(() => props.ordens.filter(os => os.status === 'nova'))
const ordensAguardando = computed(() => props.ordens.filter(os => os.status === 'aguardando_campo'))
const ordensEmExecucao = computed(() =>
  props.ordens.filter(
    (os) =>
      os.status === 'em_execucao' || os.status === 'aguardando_assinatura'
  )
)
const ordensConcluidas = computed(() => props.ordens.filter(os => os.status === 'concluida'))

// Helpers
function getStatusLabel(status) {
  const labels = {
    nova: 'Nova',
    aguardando_campo: 'Aguardando Campo',
    em_execucao: 'Em Execução',
    aguardando_assinatura: 'Aguardando gestor',
    concluida: 'Concluída'
  }
  return labels[status] || status
}

function getSLALabel(sla, prazo) {
  if (sla === 'vencido') return 'Vencido'
  if (sla === 'atencao') return 'Vence hoje'
  
  const agora = new Date()
  const prazoDate = new Date(prazo)
  const diff = prazoDate - agora
  const horas = Math.floor(diff / (1000 * 60 * 60))
  
  if (horas < 24) return `${horas}h restantes`
  const dias = Math.floor(horas / 24)
  return `${dias}d restantes`
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
