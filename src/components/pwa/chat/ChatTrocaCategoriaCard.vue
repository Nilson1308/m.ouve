<template>
  <div
    v-if="config?.tipo_acao === 'sugerir_troca_categoria' || config?.categoria_sugerida"
    class="card bg-gradient-to-br from-blue-50 to-slate-50 dark:from-blue-950/40 dark:to-gray-900 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 border border-blue-200/80 dark:border-blue-800/60 p-4 max-w-lg space-y-4 animate-scale-in"
    role="group"
    :aria-label="ariaTitulo"
  >
    <div class="flex items-start gap-3">
      <div
        class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 flex items-center justify-center shadow-soft"
        aria-hidden="true"
      >
        <ArrowsRightLeftIcon class="w-5 h-5 text-white high-contrast:text-black" />
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
          Parece que sua demanda combina melhor com outra área
        </h3>
        <p v-if="config.motivo" class="text-sm text-gray-700 dark:text-gray-300 mt-2 leading-relaxed">
          {{ config.motivo }}
        </p>
        <p v-if="config.servico_sugerido?.nome" class="text-xs text-gray-600 dark:text-gray-400 mt-2">
          Serviço sugerido: <span class="font-semibold text-gray-800 dark:text-gray-200">{{ config.servico_sugerido.nome }}</span>
        </p>
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <button
        type="button"
        class="btn-primary w-full min-h-[44px] !text-white font-semibold"
        :disabled="desabilitado"
        @click="$emit('ir-categoria-sugerida')"
      >
        Ir para {{ nomeCategoriaSugerida }}
      </button>
      <button
        type="button"
        class="btn-secondary w-full min-h-[44px]"
        :disabled="desabilitado"
        @click="$emit('continuar-categoria-atual')"
      >
        Continuar em {{ nomeCategoriaAtual }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowsRightLeftIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  config: { type: Object, default: null },
  desabilitado: { type: Boolean, default: false }
})

defineEmits(['ir-categoria-sugerida', 'continuar-categoria-atual'])

const nomeCategoriaSugerida = computed(
  () => props.config?.categoria_sugerida?.nome || 'a área indicada'
)
const nomeCategoriaAtual = computed(
  () => props.config?.categoria_atual?.nome || 'esta categoria'
)
const ariaTitulo = computed(
  () => `Sugestão: ${nomeCategoriaSugerida.value} em vez de ${nomeCategoriaAtual.value}`
)
</script>