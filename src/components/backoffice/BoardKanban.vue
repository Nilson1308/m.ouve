<template>
  <div class="kanban-board">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <div
        v-for="col in colunasConfig"
        :key="col.id"
        class="kanban-column"
        :class="col.colunaClass"
      >
        <div class="kanban-header">
          <div class="flex items-center gap-2 min-w-0">
            <div class="w-3 h-3 rounded-full shrink-0" :class="col.dotClass" />
            <h3 class="font-semibold text-gray-900 dark:text-white truncate flex items-center gap-1">
              <span>{{ col.titulo }}</span>
              <ContextualHelpIcon :texto="col.ajuda" :label="`Ajuda: coluna ${col.titulo}`" />
            </h3>
          </div>
          <span class="badge shrink-0" :class="col.badgeClass">
            {{ col.itens.length }}
          </span>
        </div>
        <p v-if="col.nota" class="text-[11px] text-gray-500 dark:text-gray-400 mb-3 -mt-2">
          {{ col.nota }}
        </p>
        <div class="kanban-cards">
          <template v-for="item in col.itens" :key="item.id">
            <CardSuperOS
              v-if="item.tipo === 'super_os'"
              :item="item"
              :modo-validacao="col.id === 'validacao'"
              @despachar="emit('despachar', $event)"
              @integrar="emit('integrar', $event)"
              @detalhes="emit('detalhes', $event)"
            />
            <CardProtocolo
              v-else
              :protocolo="item"
              :destacar-nos-abertos="col.id === 'andamento'"
              :modo-validacao="col.id === 'validacao'"
              @despachar="emit('despachar', $event)"
              @detalhes="emit('detalhes', $event)"
              @ver-cluster-ia="emit('ver-cluster-ia', $event)"
            />
          </template>
          <div v-if="col.itens.length === 0" class="empty-column" role="status">
            <component :is="col.emptyIcon" class="w-12 h-12 text-gray-300 dark:text-gray-600 opacity-70 mx-auto mb-3" />
            <p class="text-sm font-medium text-gray-600 dark:text-gray-300">{{ col.emptyTitulo }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-[14rem]">{{ col.emptyDescricao }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { InboxIcon, SparklesIcon, TruckIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import CardProtocolo from './CardProtocolo.vue'
import CardSuperOS from './CardSuperOS.vue'
import ContextualHelpIcon from '@/components/shared/ContextualHelpIcon.vue'
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

const colunasConfig = computed(() => [
  {
    id: 'triagem',
    titulo: 'Novos / Triagem',
    dotClass: 'bg-primary-500',
    badgeClass: 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300',
    colunaClass: '',
    nota: '',
    ajuda: 'Fila de triagem: protocolos recém-abertos aguardando primeira análise e despacho manual.',
    itens: protocolosPorStatus('em_analise'),
    emptyIcon: InboxIcon,
    emptyTitulo: 'Fila de triagem vazia',
    emptyDescricao: 'Novas solicitações dos cidadãos aparecerão aqui para análise.'
  },
  {
    id: 'andamento',
    titulo: 'Em Andamento',
    dotClass: 'bg-warning-500',
    badgeClass: 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300',
    colunaClass: '',
    nota: '',
    ajuda: 'Protocolos com ordens de serviço ativas nos setores (scatter-gather em execução).',
    itens: protocolosEmTramitacao.value,
    emptyIcon: TruckIcon,
    emptyTitulo: 'Nenhum protocolo em campo',
    emptyDescricao: 'Demandas despachadas aos setores ficam visíveis nesta coluna.'
  },
  {
    id: 'validacao',
    titulo: 'Aguardando validação',
    dotClass: 'bg-purple-500',
    badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-200',
    colunaClass: 'border-2 border-purple-200 dark:border-purple-800/60',
    nota: 'Gather completo · validação final da Ouvidoria',
    ajuda: 'Todos os nós encerrados: a Ouvidoria revisa e libera a resposta ao cidadão.',
    itens: protocolosAguardandoValidacao.value,
    emptyIcon: SparklesIcon,
    emptyTitulo: 'Nada aguardando validação',
    emptyDescricao: 'Quando o gather terminar, os protocolos vêm para cá.'
  },
  {
    id: 'concluidos',
    titulo: 'Concluídos',
    dotClass: 'bg-success-500',
    badgeClass: 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300',
    colunaClass: '',
    nota: '',
    ajuda: 'Protocolos resolvidos ou encerrados — consulta e auditoria.',
    itens: protocolosPorStatus('resolvido', 'rejeitado'),
    emptyIcon: CheckCircleIcon,
    emptyTitulo: 'Sem encerramentos recentes',
    emptyDescricao: 'Protocolos finalizados são listados nesta coluna.'
  }
])
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
  @apply flex flex-col items-center justify-center py-12 text-center px-2;
}
</style>