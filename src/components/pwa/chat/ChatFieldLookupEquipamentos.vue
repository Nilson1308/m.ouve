<template>
  <div
    v-if="config?.campo"
    class="card bg-white dark:bg-gray-800 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 border border-gray-200 dark:border-gray-700 p-4 max-w-lg space-y-3 animate-scale-in"
  >
    <h3 class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
      {{ config.titulo || 'Selecione o equipamento' }}
    </h3>
    <p v-if="config.dica" class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white">
      {{ config.dica }}
    </p>

    <PwaFieldLookupEquipamentos
      v-model="selecionado"
      :required="!opcional"
      :disabled="desabilitado"
      :filtro-datasource="filtroSchema"
      preload
      @manual="confirmarManual"
    />

    <button
      type="button"
      class="btn-primary w-full min-h-[44px] !text-white font-semibold"
      :disabled="desabilitado || !selecionado || loading || Boolean(erro)"
      @click="confirmar"
    >
      Confirmar da lista
    </button>

    <button
      v-if="opcional"
      type="button"
      class="btn-secondary w-full text-sm min-h-[44px]"
      :disabled="desabilitado || loading"
      @click="pular"
    >
      Não se aplica / Pular
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import PwaFieldLookupEquipamentos from '@/components/pwa/PwaFieldLookupEquipamentos.vue'
import { useCatalogoLookup } from '@/composables/useCatalogoLookup'

const props = defineProps({
  config: { type: Object, default: null },
  desabilitado: { type: Boolean, default: false }
})

const emit = defineEmits(['confirmar', 'pular'])

const selecionado = ref('')
const { equipamentos, loading, erro } = useCatalogoLookup()

const opcional = computed(() => Boolean(props.config?.opcional))
const filtroSchema = computed(() => props.config?.filtro || {})

function confirmar() {
  const id = selecionado.value
  if (!id) return
  const nome = equipamentos.value.find((u) => u.id === id)?.nome || id
  const campo = props.config.campo
  emit('confirmar', {
    texto: `✓ ${props.config.titulo || campo}: ${nome}`,
    dados_slot: { [campo]: id }
  })
}

function confirmarManual(nomeInformado) {
  const campo = props.config.campo
  const texto = (nomeInformado || '').trim()
  if (!texto) return
  emit('confirmar', {
    texto: `✓ ${props.config.titulo || campo}: ${texto}`,
    dados_slot: {
      [campo]: { nao_catalogado: true, texto }
    }
  })
}

function pular() {
  const campo = props.config.campo
  emit('pular', {
    texto: `— ${props.config.titulo || campo}: não se aplica`,
    dados_slot: { __pular_campo: campo }
  })
}

watch(
  () => props.config?.campo,
  () => {
    selecionado.value = ''
  }
)
</script>