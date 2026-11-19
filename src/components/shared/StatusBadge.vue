<template>
  <span :class="['badge', badgeClass, sizeClass, 'inline-flex items-center gap-1.5']">
    <component
      v-if="showIcon && iconComponent"
      :is="iconComponent"
      :class="iconSizeClass"
      aria-hidden="true"
    />
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import {
  CpuChipIcon,
  EyeIcon,
  ClockIcon,
  TruckIcon,
  WrenchScrewdriverIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  PaperAirplaneIcon,
  CheckBadgeIcon,
  ArchiveBoxIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  tipo: {
    type: String,
    default: 'zeladoria', // 'zeladoria' ou 'ouvidoria'
    validator: (value) => ['zeladoria', 'ouvidoria'].includes(value)
  },
  showIcon: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'sm',
    validator: (v) => ['sm', 'lg'].includes(v)
  },
  /** Badge sobre fundo primary (ex.: hero do protocolo) — corrige contraste no tema claro */
  surface: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary'].includes(v)
  }
})

const sizeClass = computed(() =>
  props.size === 'lg' ? 'text-sm sm:text-base px-3.5 py-1.5 font-semibold' : ''
)

const iconSizeClass = computed(() =>
  props.size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'
)

// Mapeamento de badges por tipo
const badgeClass = computed(() => {
  if (props.surface === 'primary') {
    return 'badge-on-primary-surface'
  }
  if (props.tipo === 'zeladoria') {
    return getZeladoriaClass(props.status)
  } else if (props.tipo === 'ouvidoria') {
    return getOuvidoriaClass(props.status)
  }
  return 'badge-zeladoria-triagem-ia'
})

function getZeladoriaClass(status) {
  const classes = {
    // Novo sistema
    'triagem_ia': 'badge-zeladoria-triagem-ia',
    'validacao': 'badge-zeladoria-validacao',
    'aguardando_equipe': 'badge-zeladoria-aguardando-equipe',
    'em_deslocamento': 'badge-zeladoria-em-deslocamento',
    'em_execucao': 'badge-zeladoria-em-execucao',
    'concluido': 'badge-zeladoria-concluido',
    'nao_procedente': 'badge-zeladoria-nao-procedente',
    
    // Compatibilidade (legado)
    'em_analise': 'badge-zeladoria-triagem-ia',
    'em_andamento': 'badge-zeladoria-em-deslocamento',
    'aguardando_revisao': 'badge-zeladoria-validacao',
    'resolvido': 'badge-zeladoria-concluido',
    'rejeitado': 'badge-zeladoria-nao-procedente',
  }
  return classes[status] || 'badge-zeladoria-triagem-ia'
}

function getOuvidoriaClass(status) {
  const classes = {
    'triagem': 'badge-ouvidoria-triagem',
    'analise': 'badge-ouvidoria-analise',
    'encaminhado': 'badge-ouvidoria-encaminhado',
    'respondido': 'badge-ouvidoria-respondido',
    'arquivado': 'badge-ouvidoria-arquivado',
    
    // Compatibilidade
    'em_analise': 'badge-ouvidoria-triagem',
    'resolvido': 'badge-ouvidoria-respondido',
  }
  return classes[status] || 'badge-ouvidoria-triagem'
}

// Labels descritivas
const label = computed(() => {
  if (props.tipo === 'zeladoria') {
    return getZeladoriaLabel(props.status)
  } else if (props.tipo === 'ouvidoria') {
    return getOuvidoriaLabel(props.status)
  }
  return props.status
})

function getZeladoriaLabel(status) {
  const labels = {
    'triagem_ia': 'Triagem IA',
    'validacao': 'Em Validação',
    'aguardando_equipe': 'Aguardando Equipe',
    'em_deslocamento': 'Equipe em Deslocamento',
    'em_execucao': 'Em Execução',
    'concluido': 'Concluído',
    'nao_procedente': 'Não Procedente',
    
    // Legado
    'em_analise': 'Em Análise',
    'em_andamento': 'Equipe em Deslocamento',
    'aguardando_revisao': 'Aguardando validação',
    'resolvido': 'Resolvido',
    'rejeitado': 'Não Procedente',
  }
  return labels[status] || status
}

function getOuvidoriaLabel(status) {
  const labels = {
    'triagem': 'Em Triagem',
    'analise': 'Em Análise',
    'encaminhado': 'Encaminhado',
    'respondido': 'Respondido',
    'arquivado': 'Arquivado',
    
    // Legado
    'em_analise': 'Em Triagem',
    'resolvido': 'Respondido',
  }
  return labels[status] || status
}

// Ícones do Heroicons
const iconComponent = computed(() => {
  if (props.tipo === 'zeladoria') {
    return getZeladoriaIcon(props.status)
  } else if (props.tipo === 'ouvidoria') {
    return getOuvidoriaIcon(props.status)
  }
  return null
})

function getZeladoriaIcon(status) {
  const icons = {
    'triagem_ia': CpuChipIcon,          // IA/Robô
    'validacao': EyeIcon,                // Olho para validação
    'aguardando_equipe': ClockIcon,      // Relógio para aguardar
    'em_deslocamento': TruckIcon,        // Caminhão para deslocamento
    'em_execucao': WrenchScrewdriverIcon, // Ferramentas para execução
    'concluido': CheckCircleIcon,        // Check para concluído
    'nao_procedente': XCircleIcon,       // X para não procedente
    
    // Legado
    'em_analise': ClockIcon,
    'em_andamento': TruckIcon,
    'aguardando_revisao': EyeIcon,
    'resolvido': CheckCircleIcon,
    'rejeitado': XCircleIcon,
  }
  return icons[status] || null
}

function getOuvidoriaIcon(status) {
  const icons = {
    'triagem': DocumentTextIcon,         // Documento para triagem
    'analise': MagnifyingGlassIcon,      // Lupa para análise
    'encaminhado': PaperAirplaneIcon,    // Avião de papel para envio
    'respondido': CheckBadgeIcon,        // Badge check para respondido
    'arquivado': ArchiveBoxIcon,         // Caixa para arquivo
    
    // Legado
    'em_analise': DocumentTextIcon,
    'resolvido': CheckBadgeIcon,
  }
  return icons[status] || null
}
</script>
