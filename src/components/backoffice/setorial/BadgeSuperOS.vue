<template>
  <span
    v-if="ativo"
    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wide bg-gradient-to-r from-orange-500/12 to-red-500/10 text-orange-800 dark:text-orange-200 border border-orange-300/40 dark:border-orange-600/35"
    :title="titulo"
  >
    <span aria-hidden="true">🔥</span>
  Super OS · {{ qtd }} {{ qtd === 1 ? 'chamado' : 'chamados' }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  ordem: {
    type: Object,
    default: null
  },
  ativo: {
    type: Boolean,
    default: undefined
  },
  qtd: {
    type: Number,
    default: undefined
  }
})

const ativo = computed(() =>
  props.ativo !== undefined ? props.ativo : Boolean(props.ordem?.is_super_os)
)

const qtd = computed(() =>
  props.qtd ?? props.ordem?.qtd_chamados_vinculados ?? 1
)

const titulo = computed(() =>
  props.ordem?.super_os_codigo
    ? `Incidente mestre ${props.ordem.super_os_codigo}`
    : 'Incidente em massa (Super OS)'
)
</script>