<template>
  <div
    v-if="config && config.campo"
    role="group"
    :aria-label="config.titulo || 'Escolha uma opção'"
    class="card bg-white dark:bg-gray-800 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 border border-gray-200 dark:border-gray-700 p-4 max-w-lg space-y-4 animate-scale-in motion-reduce:animate-none"
  >
    <h3 v-if="config.titulo" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
      {{ config.titulo }}
    </h3>
    <p v-if="config.dica" class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white">
      {{ config.dica }}
    </p>

    <div class="flex flex-wrap gap-2">
      <button
        v-for="op in config.opcoes"
        :key="op.valor"
        type="button"
        :disabled="desabilitado"
        :aria-pressed="selecionados.includes(op.valor)"
        class="text-sm py-2 px-4 min-h-[44px] rounded-full border transition-all disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
        :class="botaoClasse(op.valor)"
        @click="alternar(op.valor)"
      >
        <span
          v-if="modoSelecao === 'multi'"
          class="inline-block w-4 h-4 mr-1 border rounded align-middle"
          :class="selecionados.includes(op.valor) ? 'bg-primary-500 border-primary-500' : 'border-gray-400'"
        />
        {{ op.rotulo }}
      </button>
    </div>

    <div v-if="modoSelecao === 'multi'" class="flex flex-wrap gap-2">
      <button type="button" class="text-xs underline text-primary-600" :disabled="desabilitado" @click="marcarTodos">
        Marcar todos
      </button>
      <button type="button" class="text-xs underline text-gray-600" :disabled="desabilitado" @click="limpar">
        Limpar
      </button>
    </div>

    <div
      v-if="config.permite_outro && (mostrarOutro || selecionouOutro)"
      class="space-y-2"
    >
      <label class="text-sm font-semibold text-gray-800 dark:text-gray-200">
        Descreva o que não está na lista
      </label>
      <textarea
        v-model="textoOutro"
        rows="2"
        class="input resize-none text-sm"
        placeholder="Ex.: cratera na esquina, piso irregular..."
        :disabled="desabilitado"
      />
    </div>

    <button
      v-if="modoSelecao === 'multi'"
      type="button"
      class="btn-primary w-full"
      :disabled="desabilitado || !podeConfirmar"
      @click="confirmar"
    >
      Confirmar escolha
    </button>

    <button
      v-else-if="config.permite_outro && !selecionados.length"
      type="button"
      class="btn-secondary w-full text-sm"
      :disabled="desabilitado"
      @click="mostrarOutro = !mostrarOutro"
    >
      {{ mostrarOutro ? 'Ocultar campo livre' : 'Não está na lista? Descreva aqui' }}
    </button>

    <button
      v-if="modoSelecao !== 'multi' && (mostrarOutro || textoOutro) && !selecionados.length"
      type="button"
      class="btn-primary w-full"
      :disabled="desabilitado || !textoOutro.trim()"
      @click="confirmar"
    >
      Enviar descrição
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  config: {
    type: Object,
    default: null
  },
  desabilitado: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['confirmar'])

const selecionados = ref([])
const textoOutro = ref('')
const mostrarOutro = ref(false)

const modoSelecao = computed(() => props.config?.modo || 'single')

const precisaConfirmar = computed(() => modoSelecao.value === 'multi')

const selecionouOutro = computed(() => {
  const outroVal = props.config?.opcoes?.find((o) => String(o.valor).toLowerCase() === 'outro')
  return outroVal ? selecionados.value.includes(outroVal.valor) : mostrarOutro.value
})

const podeConfirmar = computed(() => {
  if (modoSelecao.value === 'multi') {
    if (selecionados.value.length === 0 && !textoOutro.value.trim()) return false
    if (selecionouOutro.value && !textoOutro.value.trim()) return false
    return selecionados.value.length > 0 || textoOutro.value.trim().length > 0
  }
  if (selecionados.value.length === 1) {
    if (String(selecionados.value[0]).toLowerCase() === 'outro') {
      return textoOutro.value.trim().length > 0
    }
    return true
  }
  return textoOutro.value.trim().length > 0
})

function botaoClasse(valor) {
  const ativo = selecionados.value.includes(valor)
  return ativo
    ? 'bg-primary-500 text-white border-primary-600 shadow-soft'
    : 'bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600'
}

function alternar(valor) {
  if (modoSelecao.value === 'multi') {
    const idx = selecionados.value.indexOf(valor)
    if (idx >= 0) {
      selecionados.value.splice(idx, 1)
    } else {
      selecionados.value.push(valor)
    }
    return
  }
  selecionados.value = [valor]
  if (String(valor).toLowerCase() === 'outro') {
    mostrarOutro.value = true
    return
  }
  confirmar()
}

function marcarTodos() {
  selecionados.value = props.config.opcoes.map((o) => o.valor)
}

function limpar() {
  selecionados.value = []
  textoOutro.value = ''
}

function rotulosSelecionados() {
  const mapa = Object.fromEntries((props.config.opcoes || []).map((o) => [o.valor, o.rotulo]))
  return selecionados.value.map((v) => mapa[v] || v)
}

function confirmar() {
  const campo = props.config.campo
  const dadosSlot = {}
  let texto = ''

  if (modoSelecao.value === 'multi') {
    let valores = [...selecionados.value]
    if (textoOutro.value.trim() && !valores.includes('outro')) {
      valores.push('outro')
    }
  if (!valores.length && textoOutro.value.trim()) {
      valores = ['outro']
    }
    dadosSlot[campo] = valores
    if (valores.includes('outro') || textoOutro.value.trim()) {
      dadosSlot[`${campo}_outro`] = textoOutro.value.trim()
    }
    const partes = rotulosSelecionados()
    if (textoOutro.value.trim()) partes.push(`Outro: ${textoOutro.value.trim()}`)
    texto = `✓ ${props.config.titulo}: ${partes.join(', ')}`
  } else {
    const valor = selecionados.value[0]
    if (valor) {
      dadosSlot[campo] = valor
      if (String(valor).toLowerCase() === 'outro') {
        dadosSlot[`${campo}_outro`] = textoOutro.value.trim()
        texto = `✓ ${props.config.titulo}: ${textoOutro.value.trim()}`
      } else {
        const rotulo = props.config.opcoes.find((o) => o.valor === valor)?.rotulo || valor
        texto = `✓ ${props.config.titulo}: ${rotulo}`
      }
    } else if (textoOutro.value.trim()) {
      dadosSlot[campo] = 'outro'
      dadosSlot[`${campo}_outro`] = textoOutro.value.trim()
      texto = `✓ ${props.config.titulo}: ${textoOutro.value.trim()}`
    }
  }

  emit('confirmar', { texto, dados_slot: dadosSlot })
}

watch(
  () => props.config?.campo,
  () => {
    selecionados.value = []
    textoOutro.value = ''
    mostrarOutro.value = false
  }
)
</script>
