<template>
  <div
    v-if="config?.campo"
    class="card bg-white dark:bg-gray-800 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 border border-gray-200 dark:border-gray-700 p-4 max-w-lg space-y-3 animate-scale-in"
  >
    <h3 class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
      {{ config.titulo || 'Selecione a unidade' }}
    </h3>
    <p v-if="config.dica" class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white">
      {{ config.dica }}
    </p>

    <PwaFieldLookupUnidades
      v-model="selecionado"
      :required="true"
      :disabled="desabilitado"
      preload
    />

    <button
      type="button"
      class="btn-primary w-full"
      :disabled="desabilitado || !selecionado || loading || Boolean(erro)"
      @click="confirmar"
    >
      Confirmar
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import PwaFieldLookupUnidades from '@/components/pwa/PwaFieldLookupUnidades.vue'
import { useCatalogoLookup } from '@/composables/useCatalogoLookup'

const props = defineProps({
  config: { type: Object, default: null },
  desabilitado: { type: Boolean, default: false }
})

const emit = defineEmits(['confirmar'])

const selecionado = ref('')
const { unidades, loading, erro } = useCatalogoLookup()

function confirmar() {
  const id = selecionado.value
  if (!id) return
  const nome = unidades.value.find((u) => u.id === id)?.nome || id
  const campo = props.config.campo
  emit('confirmar', {
    texto: `✓ ${props.config.titulo || campo}: ${nome}`,
    dados_slot: { [campo]: id }
  })
}

watch(
  () => props.config?.campo,
  () => {
    selecionado.value = ''
  }
)
</script>