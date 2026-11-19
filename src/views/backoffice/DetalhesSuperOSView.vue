<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div
      v-if="loadingDetalhe"
      class="flex min-h-screen items-center justify-center p-12"
    >
      <div class="card mx-auto flex w-full max-w-lg flex-col items-center justify-center gap-4 p-12">
        <div
          class="h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent"
        />
        <p class="text-sm text-gray-600 dark:text-gray-400">Carregando dossiê da Super OS…</p>
      </div>
    </div>

    <div
      v-else-if="erroCarregamento"
      class="flex min-h-screen items-center justify-center p-6"
    >
      <div class="card max-w-md p-8 text-center">
        <p class="mb-4 text-gray-700 dark:text-gray-300">{{ erroCarregamento }}</p>
        <button type="button" class="btn-primary" @click="voltarMesa">Voltar à Mesa</button>
      </div>
    </div>

    <template v-else-if="superOs">
      <header class="sticky top-0 z-30 border-b border-orange-200 bg-white shadow-sm dark:border-orange-900/50 dark:bg-gray-800">
        <div class="px-6 py-4">
          <div class="mb-3 flex items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <button
                type="button"
                class="rounded-lg p-2 transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
                title="Voltar"
                @click="voltarMesa"
              >
                <ArrowLeftIcon class="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>
              <div>
                <p class="text-xs font-bold uppercase tracking-wide text-orange-600 dark:text-orange-400 mb-0.5">
                  Incidente em massa
                </p>
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                  {{ superOs.codigo }}
                </h1>
                <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                  {{ superOs.tituloResumo }}
                </p>
              </div>
            </div>
            <span
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-bold bg-gradient-to-r from-orange-500 to-red-600 text-white"
            >
              🔥 {{ superOs.quantidadeProtocolos }} protocolos
            </span>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <StatusBadge :status="superOs.status" tipo="zeladoria" :show-icon="true" size="lg" />
            <div
              :class="slaBadgeClass"
              class="inline-flex items-center gap-2 rounded-badge px-4 py-2 font-semibold"
            >
              <ClockIcon class="h-5 w-5" />
              <span>{{ formatarSLA(superOs.sla) }}</span>
            </div>
            <div
              class="inline-flex items-center gap-2 rounded-badge bg-orange-100 px-4 py-2 font-semibold text-orange-800 dark:bg-orange-900/40 dark:text-orange-200"
            >
              <WrenchScrewdriverIcon class="h-5 w-5" />
              <span>{{ superOs.servico }}</span>
            </div>
          </div>
        </div>
      </header>

      <div class="flex gap-6 p-6">
        <div class="flex-1 min-w-0">
          <SuperOSContexto :super-os="superOs" />
        </div>

        <div
          class="w-full max-w-xl lg:w-[540px] shrink-0 space-y-6 lg:sticky lg:top-28 lg:self-start lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto"
        >
          <ProtocoloOperacao
            v-if="protocoloOperacao"
            :protocolo="protocoloOperacao"
            :salvando-validacao="salvandoValidacao"
            :salvando-devolucao="salvandoDevolucao"
            @validar="onValidar"
            @devolver="onDevolver"
            @adicionar-setor="abrirDespachoContinuo"
          />
        </div>
      </div>
    </template>

    <DespacharProtocolo
      v-if="superOs && protocoloOperacao"
      :protocolo="protocoloOperacao"
      :aberto="mostrarDespacho"
      :salvando="despachandoSuper"
      modo="super_os"
      @fechar="fecharDespacho"
      @confirmar="confirmarDespacho"
    />

    <Teleport to="body">
      <transition name="mesa-toast">
        <div
          v-if="toastAberto"
          class="mesa-toast"
          :class="{ 'mesa-toast--success': toastSucesso }"
          role="status"
        >
          {{ toastMensagem }}
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  ArrowLeftIcon,
  ClockIcon,
  WrenchScrewdriverIcon
} from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import SuperOSContexto from '@/components/backoffice/super_os/SuperOSContexto.vue'
import ProtocoloOperacao from '@/components/backoffice/protocolo/ProtocoloOperacao.vue'
import DespacharProtocolo from '@/components/backoffice/DespacharProtocolo.vue'
import { useSuperOSStore } from '@/stores/super_os'
import { useBackofficeStore } from '@/stores/backoffice'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import { superOsComoProtocoloOperacao } from '@/utils/superOsMappers'
import { useFormatacao } from '@/composables/useFormatacao'
import { getApiErrorMessage } from '@/utils/apiError'

const { formatarSLA } = useFormatacao()
const route = useRoute()
const router = useRouter()
const superOSStore = useSuperOSStore()
const backofficeStore = useBackofficeStore()
const notificacoesInternasStore = useNotificacoesInternasStore()

const { superOsAtual, loadingDetalhe } = storeToRefs(superOSStore)
const { salvandoValidacao, salvandoDevolucao } = storeToRefs(backofficeStore)

const erroCarregamento = ref(null)
const mostrarDespacho = ref(false)
const despachandoSuper = ref(false)
const toastAberto = ref(false)
const toastMensagem = ref('')
const toastSucesso = ref(false)
let toastTimer = null

const superOs = computed(() => superOsAtual.value)
const protocoloOperacao = computed(() => superOsComoProtocoloOperacao(superOs.value))

const slaBadgeClass = computed(() => {
  const sla = superOs.value?.sla
  if (!sla) return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  if (sla.vencido) return 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300'
  if (sla.horasRestantes <= 24) {
    return 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300'
  }
  return 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300'
})

function mostrarToast(mensagem, sucesso = false) {
  toastMensagem.value = mensagem
  toastSucesso.value = sucesso
  toastAberto.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastAberto.value = false
    toastSucesso.value = false
  }, 4500)
}

function voltarMesa() {
  router.push({ name: 'backoffice-mesa-trabalho' })
}

async function carregar() {
  const id = route.params.id
  if (!id) {
    erroCarregamento.value = 'Super OS não informada na URL.'
    return
  }
  erroCarregamento.value = null
  try {
    await superOSStore.carregarDetalhes(id)
  } catch (e) {
    erroCarregamento.value = getApiErrorMessage(e, 'Não foi possível carregar o dossiê.')
  }
}

async function onValidar(dados) {
  const filhos = superOs.value?.protocolosFilhos || []
  if (!filhos.length) return
  try {
    const payload = {
      resposta_cidadao: (dados.resposta || dados.resposta_cidadao || '').trim(),
      observacoes_internas: (dados.observacoes || dados.observacoes_internas || '').trim()
    }
    for (const filho of filhos) {
      await backofficeStore.validarProtocolo(filho.id, payload)
    }
    mostrarToast('Super OS validada — todos os protocolos filhos foram encerrados.', true)
    setTimeout(() => voltarMesa(), 900)
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível validar o incidente.'))
  }
}

async function onDevolver(dados) {
  const ordemId = dados.ordemId || dados.ordem_servico_id
  if (!ordemId) {
    mostrarToast('Selecione a ordem de serviço a devolver.')
    return
  }
  try {
    await backofficeStore.devolverOrdemServico(ordemId, {
      motivo: dados.motivo,
      justificativa: dados.justificativa
    })
    await superOSStore.carregarDetalhes(route.params.id)
    mostrarToast('Ordem devolvida.')
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível devolver a ordem.'))
  }
}

function abrirDespachoContinuo() {
  mostrarDespacho.value = true
}

function fecharDespacho() {
  mostrarDespacho.value = false
}

async function confirmarDespacho(payload) {
  const id = superOs.value?.id
  if (!id) return
  despachandoSuper.value = true
  try {
    await superOSStore.despacharSuperOS(id, {
      ordens: payload.ordens,
      observacao_geral: payload.observacao_geral
    })
    fecharDespacho()
    mostrarToast('Despacho consolidado realizado com sucesso.', true)
    await superOSStore.carregarDetalhes(id)
    notificacoesInternasStore.carregar({ silencioso: true }).catch(() => null)
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível despachar a Super OS.'))
  } finally {
    despachandoSuper.value = false
  }
}

onMounted(async () => {
  await carregar()
  if (route.query.despachar === '1' && superOs.value?.status === 'em_analise') {
    const semOrdens = !(superOs.value?.ordens_servico || []).length
    if (semOrdens) {
      mostrarDespacho.value = true
    }
    const q = { ...route.query }
    delete q.despachar
    router.replace({ query: q })
  }
})
onUnmounted(() => superOSStore.limparSuperOsAtual())
</script>

<style scoped>
.mesa-toast {
  @apply fixed bottom-6 left-1/2 z-[200] -translate-x-1/2 rounded-xl px-5 py-3 text-sm font-medium shadow-lg;
  @apply bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900;
}
.mesa-toast--success {
  @apply bg-emerald-700 text-white dark:bg-emerald-600;
}
</style>