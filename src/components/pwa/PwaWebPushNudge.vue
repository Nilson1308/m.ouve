<template>
  <section
    v-if="visivel"
    class="card border border-primary-200 dark:border-primary-800 bg-gradient-to-br from-primary-50/80 to-white dark:from-primary-950/40 dark:to-gray-900/60 high-contrast:border-yellow-300 high-contrast:bg-black p-4"
    :aria-labelledby="headingId"
  >
    <h2 :id="headingId" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-1">
      {{ titulo }}
    </h2>
    <p class="text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white leading-relaxed mb-3">
      {{ descricao }}
    </p>
    <p
      v-if="mostrarDicaIos"
      class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-gray-200 bg-white/70 dark:bg-gray-800/50 rounded-card px-3 py-2 mb-3 border border-gray-200/80 dark:border-gray-700"
      role="note"
    >
      No iPhone/iPad, toque em <strong class="font-semibold">Compartilhar</strong> e depois em
      <strong class="font-semibold">Adicionar à Tela de Início</strong> para poder receber notificações.
    </p>
    <button
      type="button"
      class="btn-primary w-full sm:w-auto min-h-[44px] disabled:opacity-50"
      :disabled="ativando || pushAtivo"
      @click="ativarPush"
    >
      {{ pushAtivo ? 'Notificações push ativas' : ativando ? 'Ativando…' : 'Ativar notificações' }}
    </button>
    <p v-if="erro" class="text-sm text-red-600 dark:text-red-400 mt-2" role="alert">
      {{ erro }}
    </p>
    <p v-if="sucesso" class="text-sm text-green-700 dark:text-green-400 mt-2" role="status">
      {{ sucesso }}
    </p>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ativarWebPush, pushJaInscrito, pushSuportado } from '@/utils/webPush'
import { precisaInstrucaoIosAddToHome } from '@/utils/platform'

const props = defineProps({
  titulo: {
    type: String,
    default: 'Fique por dentro'
  },
  descricao: {
    type: String,
    default: 'Ative as notificações para ser avisado quando seu protocolo for atualizado.'
  },
  headingSuffix: {
    type: String,
    default: 'push'
  }
})

const emit = defineEmits(['ativado', 'erro'])

const ativando = ref(false)
const pushAtivo = ref(false)
const erro = ref('')
const sucesso = ref('')

const headingId = computed(() => `titulo-ativar-push-${props.headingSuffix}`)
const mostrarDicaIos = computed(() => precisaInstrucaoIosAddToHome())

const permissaoPadrao = computed(() => {
  if (typeof Notification === 'undefined') return false
  return Notification.permission === 'default'
})

const visivel = computed(
  () => pushSuportado() && permissaoPadrao.value && !pushAtivo.value
)

async function atualizarEstadoPush() {
  pushAtivo.value = await pushJaInscrito()
}

async function ativarPush() {
  erro.value = ''
  sucesso.value = ''
  ativando.value = true
  try {
    await ativarWebPush()
    pushAtivo.value = true
    sucesso.value = 'Pronto! Você receberá avisos neste dispositivo.'
    emit('ativado')
  } catch (err) {
    erro.value = err?.message || 'Não foi possível ativar as notificações.'
    emit('erro', erro.value)
  } finally {
    ativando.value = false
  }
}

onMounted(() => {
  void atualizarEstadoPush()
})

defineExpose({ atualizarEstadoPush, ativarPush })
</script>