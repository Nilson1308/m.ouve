<template>
  <div class="flex flex-wrap gap-2 justify-end animate-scale-in">
    <button
      v-for="opcao in opcoes"
      :key="opcao.valor"
      @click="$emit('confirmar', opcao.valor)"
      :disabled="disabled"
      class="btn-secondary text-sm py-2.5 px-6 min-w-[100px] disabled:opacity-50 disabled:cursor-not-allowed"
      :class="opcao.primary ? 'btn-primary' : 'btn-secondary'"
    >
      <component v-if="opcao.icone" :is="opcao.icone" class="w-4 h-4 inline-block mr-1" />
      {{ opcao.texto }}
    </button>
  </div>
</template>

<script setup>
import { CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'

defineProps({
  opcoes: {
    type: Array,
    default: () => [
      { texto: 'Sim', valor: 'sim', primary: true, icone: CheckIcon },
      { texto: 'Não', valor: 'nao', primary: false, icone: XMarkIcon }
    ]
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirmar'])
</script>
