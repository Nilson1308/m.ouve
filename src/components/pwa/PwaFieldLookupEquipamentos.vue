<template>
  <div class="space-y-2">
    <label
      v-if="label != null && label !== ''"
      :for="inputIdBusca"
      class="block text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300"
    >
      {{ label }}
      <span v-if="required" class="text-red-500" aria-hidden="true">*</span>
    </label>

    <input
      :id="inputIdBusca"
      v-model="termoBusca"
      type="search"
      class="input text-base min-h-[44px]"
      :placeholder="placeholderBusca"
      :disabled="disabled"
      :aria-controls="listaId"
      :aria-expanded="listaAberta ? 'true' : 'false'"
      autocomplete="off"
      @focus="listaAberta = true"
    />

    <div v-if="loading" class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 py-2 min-h-[44px]">
      <span
        class="inline-block w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"
        aria-hidden="true"
      />
      Carregando equipamentos...
    </div>

    <p v-else-if="erro" class="text-sm text-red-600 dark:text-red-400 min-h-[44px] flex items-center" role="alert">
      {{ erro }}
      <button type="button" class="underline ml-2 font-medium min-h-[44px] px-2" @click="recarregar">
        Tentar novamente
      </button>
    </p>

    <template v-else>
      <p v-if="selecionadoAtual" class="text-sm text-gray-700 dark:text-gray-300">
        Selecionado:
        <strong class="text-gray-900 dark:text-white">{{ rotuloOpcao(selecionadoAtual) }}</strong>
      </p>

      <ul
        v-if="listaAberta || !modelValue"
        :id="listaId"
        class="border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden divide-y divide-gray-200 dark:divide-gray-600 max-h-64 overflow-y-auto"
        role="listbox"
        :aria-label="label || 'Equipamentos'"
      >
        <li v-if="!opcoesExibidas.length" class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 min-h-[44px] flex items-center">
          {{ termoBusca.trim() ? 'Nenhum equipamento encontrado.' : 'Digite para buscar ou aguarde a lista.' }}
        </li>
        <li v-for="eq in opcoesExibidas" :key="eq.id" role="presentation">
          <button
            type="button"
            role="option"
            class="w-full text-left px-4 py-3 min-h-[44px] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            :class="
              modelValue === eq.id
                ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-900 dark:text-primary-100'
                : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-750 text-gray-900 dark:text-gray-100'
            "
            :aria-selected="modelValue === eq.id ? 'true' : 'false'"
            @click="selecionar(eq)"
          >
            <span class="block font-semibold text-base leading-snug">{{ eq.nome }}</span>
            <span class="block text-sm text-gray-600 dark:text-gray-400 mt-0.5">{{ linhaSecundaria(eq) }}</span>
          </button>
        </li>
      </ul>

      <input
        v-if="required"
        :id="inputId"
        type="text"
        class="sr-only"
        tabindex="-1"
        :value="modelValue"
        required
        aria-hidden="true"
      />
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
  placeholder: { type: String, default: 'Selecione o equipamento...' },
  inputId: { type: String, default: () => `lookup-eq-${Math.random().toString(36).slice(2, 9)}` },
  preload: { type: Boolean, default: true },
  filtroDatasource: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue'])

const { equipamentos, loading, erro, carregarEquipamentos } = useCatalogoLookup()
const termoBusca = ref('')
const listaAberta = ref(false)
let debounceTimer = null

const inputIdBusca = computed(() => `${props.inputId}-busca`)
const listaId = computed(() => `${props.inputId}-lista`)
const placeholderBusca = computed(() =>
  props.placeholder?.includes('...') ? 'Buscar equipamento por nome...' : props.placeholder
)

const opcoesExibidas = computed(() => equipamentos.value)

const selecionadoAtual = computed(() =>
  equipamentos.value.find((eq) => eq.id === props.modelValue) || null
)

function rotuloOpcao(eq) {
  if (!eq) return ''
  const partes = [eq.nome]
  if (eq.bairro) partes.push(eq.bairro)
  return partes.join(' · ')
}

function linhaSecundaria(eq) {
  const partes = []
  if (eq.bairro) partes.push(eq.bairro)
  if (eq.unidade_nome) partes.push(eq.unidade_nome)
  return partes.join(' · ') || 'Endereço não cadastrado'
}

function paramsBusca() {
  const filtro = { ...props.filtroDatasource, limit: 30 }
  const q = termoBusca.value.trim()
  if (q) filtro.busca = q
  return filtro
}

function agendarBusca() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    carregarEquipamentos({ filtro: paramsBusca(), force: true }).catch(() => {})
  }, 300)
}

function selecionar(eq) {
  emit('update:modelValue', eq.id)
  termoBusca.value = eq.nome
  listaAberta.value = false
}

async function recarregar() {
  await carregarEquipamentos({ filtro: paramsBusca(), force: true })
}

watch(termoBusca, () => {
  listaAberta.value = true
  agendarBusca()
})

watch(
  () => props.filtroDatasource,
  () => {
    agendarBusca()
  },
  { deep: true }
)

onMounted(() => {
  if (props.preload) {
    carregarEquipamentos({ filtro: paramsBusca() }).catch(() => {})
  }
})

watch(
  () => props.modelValue,
  (val) => {
    if (val && !equipamentos.value.length && props.preload) {
      carregarEquipamentos({ filtro: paramsBusca() }).catch(() => {})
    }
    const sel = equipamentos.value.find((eq) => eq.id === val)
    if (sel) termoBusca.value = sel.nome
  }
)
</script>