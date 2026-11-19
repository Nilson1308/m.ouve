<template>
  <div class="space-y-2">
    <label
      v-if="label != null && label !== ''"
      :for="inputId"
      class="block text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300"
    >
      {{ label }}
      <span v-if="required" class="text-red-500" aria-hidden="true">*</span>
    </label>

    <div v-if="loading" class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 py-2">
      <span
        class="inline-block w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"
        aria-hidden="true"
      />
      Carregando unidades...
    </div>

    <p v-else-if="erro" class="text-sm text-red-600 dark:text-red-400" role="alert">
      {{ erro }}
      <button type="button" class="underline ml-1 font-medium" @click="recarregar">Tentar novamente</button>
    </p>

    <template v-else>
      <input
        v-if="searchable && unidades.length > 8"
        v-model="filtroLocal"
        type="search"
        class="input text-sm"
        placeholder="Buscar secretaria..."
        :aria-controls="inputId"
      />

      <select
        :id="inputId"
        :value="modelValue"
        :required="required"
        :disabled="disabled"
        class="input"
        @change="onChange"
      >
        <option value="">{{ placeholder }}</option>
        <option v-for="u in opcoesFiltradas" :key="u.id" :value="u.id">
          {{ u.nome }}
        </option>
      </select>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useCatalogoLookup } from '@/composables/useCatalogoLookup'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  searchable: { type: Boolean, default: true },
  placeholder: { type: String, default: 'Selecione a unidade...' },
  inputId: { type: String, default: () => `lookup-unid-${Math.random().toString(36).slice(2, 9)}` },
  preload: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const { unidades, loading, erro, carregarUnidades } = useCatalogoLookup()
const filtroLocal = ref('')

const opcoesFiltradas = computed(() => {
  const q = filtroLocal.value.trim().toLowerCase()
  if (!q) return unidades.value
  return unidades.value.filter((u) => (u.nome || '').toLowerCase().includes(q))
})

function onChange(event) {
  emit('update:modelValue', event.target.value)
}

async function recarregar() {
  await carregarUnidades({ force: true })
}

onMounted(() => {
  if (props.preload) {
    carregarUnidades().catch(() => {})
  }
})

watch(
  () => props.modelValue,
  (val) => {
    if (val && !unidades.value.length && props.preload) {
      carregarUnidades().catch(() => {})
    }
  }
)
</script>