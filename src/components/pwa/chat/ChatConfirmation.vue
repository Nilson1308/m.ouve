<template>
  <div class="flex flex-wrap gap-2 justify-end animate-scale-in">
    <button
      v-for="opcao in opcoes"
      :key="opcao.valor"
      @click="$emit('confirmar', opcao.valor)"
      :disabled="disabled"
      class="text-sm py-2.5 px-6 min-w-[100px] min-h-[44px] disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
      :class="
        opcao.primary
          ? 'btn-primary !text-white font-semibold shadow-button'
          : 'btn-secondary'
      "
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
