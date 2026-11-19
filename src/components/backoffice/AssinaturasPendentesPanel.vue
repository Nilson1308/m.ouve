<template>
  <div class="space-y-4">
    <div v-if="assinaturasStore.loadingPendentes" class="card p-12 flex flex-col items-center gap-4">
      <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary-500 border-t-transparent" />
      <p class="text-sm text-gray-600 dark:text-gray-400">Carregando assinaturas pendentes…</p>
    </div>

    <div v-else-if="assinaturasStore.erro" class="alert-danger flex flex-wrap items-center justify-between gap-3">
      <span>{{ assinaturasStore.erro }}</span>
      <button type="button" class="btn-secondary text-sm" @click="recarregar">Tentar novamente</button>
    </div>

    <div
      v-else-if="!assinaturasStore.pendentes.length"
      class="card p-16 text-center text-gray-600 dark:text-gray-400"
    >
      <p class="text-lg font-semibold text-gray-800 dark:text-gray-200">Nenhuma assinatura pendente</p>
      <p class="text-sm mt-2">Quando um operador solicitar sua assinatura, ela aparecerá aqui.</p>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <button
        v-for="item in assinaturasStore.pendentes"
        :key="item.id"
        type="button"
        class="card p-5 text-left hover:shadow-card-hover transition-all border-l-4 border-l-primary-500"
        @click="abrir(item)"
      >
        <div class="flex items-start justify-between gap-3 mb-2">
          <p class="font-mono text-sm font-bold text-primary-700 dark:text-primary-300">
            {{ item.protocoloCodigo || 'Protocolo' }}
          </p>
          <span class="badge bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200">
            Aguardando assinatura
          </span>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ item.unidadeNome }} · solicitado por
          <strong class="text-gray-900 dark:text-white">{{ item.solicitanteNome || '—' }}</strong>
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-500 mt-2 line-clamp-2">
          {{ item.despachoTecnico }}
        </p>
        <p class="text-[10px] text-gray-400 mt-3">
          {{ formatarQuando(item.criadoEm) }}
        </p>
      </button>
    </div>

    <ModalAssinaturaHierarquica
      :aberto="Boolean(solicitacaoAberta)"
      :solicitacao="solicitacaoAberta"
      :processando="assinaturasStore.processando"
      @fechar="fecharModal"
      @assinar="onAssinar"
      @rejeitar="onRejeitar"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAssinaturasStore } from '@/stores/assinaturas'
import { getApiErrorMessage } from '@/utils/apiError'
import { formatarQuandoNotificacao } from '@/utils/notificacaoLink'
import ModalAssinaturaHierarquica from '@/components/backoffice/ModalAssinaturaHierarquica.vue'

const emit = defineEmits(['toast', 'concluido'])

const assinaturasStore = useAssinaturasStore()
const solicitacaoAberta = ref(null)

async function recarregar() {
  try {
    await assinaturasStore.carregarPendentes()
  } catch (e) {
    emit('toast', getApiErrorMessage(e, 'Falha ao carregar pendências.'), true)
  }
}

defineExpose({ recarregar })

function formatarQuando(iso) {
  return formatarQuandoNotificacao(iso)
}

function abrir(item) {
  solicitacaoAberta.value = item
}

function fecharModal() {
  solicitacaoAberta.value = null
}

onMounted(() => {
  recarregar()
})

async function onAssinar({ senha }) {
  if (!solicitacaoAberta.value?.id) return
  try {
    await assinaturasStore.assinar(solicitacaoAberta.value.id, senha)
    emit('toast', 'Despacho assinado com sucesso.', false)
    emit('concluido')
    fecharModal()
  } catch (e) {
    emit('toast', getApiErrorMessage(e, 'Não foi possível assinar.'), true)
  }
}

async function onRejeitar({ motivo }) {
  if (!solicitacaoAberta.value?.id) return
  try {
    await assinaturasStore.rejeitar(solicitacaoAberta.value.id, motivo)
    emit('toast', 'Solicitação rejeitada. O solicitante foi notificado.', false)
    fecharModal()
  } catch (e) {
    emit('toast', getApiErrorMessage(e, 'Não foi possível rejeitar.'), true)
  }
}
</script>