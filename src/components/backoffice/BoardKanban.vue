<template>
  <div class="kanban-board">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Coluna: Novos/Triagem -->
      <div class="kanban-column">
        <div class="kanban-header">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-primary-500"></div>
            <h3 class="font-semibold text-gray-900 dark:text-white">Novos / Triagem</h3>
          </div>
          <span class="badge bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
            {{ protocolosPorStatus('em_analise').length }}
          </span>
        </div>
        <div class="kanban-cards">
          <template v-for="item in protocolosPorStatus('em_analise')" :key="item.id">
            <CardSuperOS
              v-if="item.tipo === 'super_os'"
              :item="item"
              @despachar="emit('despachar', $event)"
              @integrar="emit('integrar', $event)"
              @detalhes="emit('detalhes', $event)"
            />
            <CardProtocolo
              v-else
              :protocolo="item"
              @despachar="emit('despachar', $event)"
              @detalhes="emit('detalhes', $event)"
              @ver-cluster-ia="emit('ver-cluster-ia', $event)"
            />
          </template>
          <div v-if="protocolosPorStatus('em_analise').length === 0" class="empty-column">
            <InboxIcon class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
            <p class="text-sm text-gray-500 dark:text-gray-400">Nenhum protocolo</p>
          </div>
        </div>
      </div>

      <!-- Coluna: Em Andamento -->
      <div class="kanban-column">
        <div class="kanban-header">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-warning-500"></div>
            <h3 class="font-semibold text-gray-900 dark:text-white">Em Andamento</h3>
          </div>
          <span class="badge bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300">
            {{ protocolosEmTramitacao.length }}
          </span>
        </div>
        <div class="kanban-cards">
          <template v-for="item in protocolosEmTramitacao" :key="item.id">
            <CardSuperOS
              v-if="item.tipo === 'super_os'"
              :item="item"
              @despachar="emit('despachar', $event)"
              @integrar="emit('integrar', $event)"
              @detalhes="emit('detalhes', $event)"
            />
            <CardProtocolo
              v-else
              :protocolo="item"
              destacar-nos-abertos
              @despachar="emit('despachar', $event)"
              @detalhes="emit('detalhes', $event)"
              @ver-cluster-ia="emit('ver-cluster-ia', $event)"
            />
          </template>
          <div v-if="protocolosEmTramitacao.length === 0" class="empty-column">
            <InboxIcon class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
            <p class="text-sm text-gray-500 dark:text-gray-400">Nenhum protocolo</p>
          </div>
        </div>
      </div>

      <!-- Coluna: Aguardando validação (Ouvidoria) -->
      <div class="kanban-column border-2 border-purple-200 dark:border-purple-800/60">
        <div class="kanban-header">
          <div class="flex items-center gap-2 min-w-0">
            <div class="w-3 h-3 rounded-full bg-purple-500 shrink-0"></div>
            <h3 class="font-semibold text-gray-900 dark:text-white truncate">
              Aguardando validação
            </h3>
          </div>
          <span class="badge bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-200 shrink-0">
            {{ protocolosAguardandoValidacao.length }}
          </span>
        </div>
        <p class="text-[11px] text-gray-500 dark:text-gray-400 mb-3 -mt-2">
          Gather completo · validação final da Ouvidoria
        </p>
        <div class="kanban-cards">
          <template v-for="item in protocolosAguardandoValidacao" :key="item.id">
            <CardSuperOS
              v-if="item.tipo === 'super_os'"
              :item="item"
              modo-validacao
              @detalhes="emit('detalhes', $event)"
            />
            <CardProtocolo
              v-else
              :protocolo="item"
              modo-validacao
              @detalhes="emit('detalhes', $event)"
              @ver-cluster-ia="emit('ver-cluster-ia', $event)"
            />
          </template>
          <div v-if="protocolosAguardandoValidacao.length === 0" class="empty-column">
            <InboxIcon class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
            <p class="text-sm text-gray-500 dark:text-gray-400">Nenhum protocolo</p>
          </div>
        </div>
      </div>

      <!-- Coluna: Concluídos -->
      <div class="kanban-column">
        <div class="kanban-header">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-success-500"></div>
            <h3 class="font-semibold text-gray-900 dark:text-white">Concluídos</h3>
          </div>
          <span class="badge bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300">
            {{ protocolosPorStatus('resolvido', 'rejeitado').length }}
          </span>
        </div>
        <div class="kanban-cards">
          <template v-for="item in protocolosPorStatus('resolvido', 'rejeitado')" :key="item.id">
            <CardSuperOS
              v-if="item.tipo === 'super_os'"
              :item="item"
              @detalhes="emit('detalhes', $event)"
            />
            <CardProtocolo
              v-else
              :protocolo="item"
              @detalhes="emit('detalhes', $event)"
              @ver-cluster-ia="emit('ver-cluster-ia', $event)"
            />
          </template>
          <div v-if="protocolosPorStatus('resolvido', 'rejeitado').length === 0" class="empty-column">
            <InboxIcon class="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
            <p class="text-sm text-gray-500 dark:text-gray-400">Nenhum protocolo</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { InboxIcon } from '@heroicons/vue/24/outline'
import CardProtocolo from './CardProtocolo.vue'
import CardSuperOS from './CardSuperOS.vue'
import {
  protocoloAguardandoValidacao,
  protocoloEmTramitacao
} from '@/utils/scatterGather'

const props = defineProps({
  protocolos: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['despachar', 'detalhes', 'ver-cluster-ia', 'integrar'])

function protocolosPorStatus(...statuses) {
  return props.protocolos.filter((p) => statuses.includes(p.status))
}

const protocolosAguardandoValidacao = computed(() =>
  props.protocolos.filter((p) => protocoloAguardandoValidacao(p))
)

const protocolosEmTramitacao = computed(() =>
  props.protocolos.filter((p) => protocoloEmTramitacao(p))
)
</script>

<style scoped>
.kanban-board {
  @apply min-h-[600px];
}

.kanban-column {
  @apply flex flex-col bg-gray-100 dark:bg-gray-800 rounded-card p-4 min-h-[600px];
}

.kanban-header {
  @apply flex items-center justify-between mb-4 pb-3 border-b border-gray-300 dark:border-gray-700;
}

.kanban-cards {
  @apply flex-1 space-y-3 overflow-y-auto;
  max-height: calc(100vh - 400px);
}

.kanban-cards::-webkit-scrollbar {
  width: 6px;
}

.kanban-cards::-webkit-scrollbar-track {
  @apply bg-gray-200 dark:bg-gray-700 rounded-full;
}

.kanban-cards::-webkit-scrollbar-thumb {
  @apply bg-gray-400 dark:bg-gray-600 rounded-full;
}

.kanban-cards::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500 dark:bg-gray-500;
}

.empty-column {
  @apply flex flex-col items-center justify-center py-12 text-center;
}
</style>