<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div
      v-if="loadingDetalhes"
      class="flex min-h-screen items-center justify-center p-12"
    >
      <div class="card mx-auto flex w-full max-w-lg flex-col items-center justify-center gap-4 p-12">
        <div
          class="h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent"
          aria-hidden="true"
        />
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Carregando visão 360º do protocolo…
        </p>
      </div>
    </div>

    <div
      v-else-if="erroCarregamento"
      class="flex min-h-screen items-center justify-center p-6"
    >
      <div class="card max-w-md p-8 text-center">
        <p class="mb-4 text-gray-700 dark:text-gray-300">{{ erroCarregamento }}</p>
        <button type="button" class="btn-primary" @click="voltarMesa">
          Voltar à Mesa de Trabalho
        </button>
      </div>
    </div>

    <template v-else-if="protocolo">
      <header class="sticky top-0 z-30 border-b border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div class="px-6 py-4">
          <div class="mb-3 flex items-center justify-between">
            <div class="flex items-center gap-4">
              <button
                type="button"
                class="rounded-lg p-2 transition-colors text-gray-600 dark:text-gray-300 hover:bg-gray-100 active:bg-gray-200 dark:hover:bg-gray-700 dark:active:bg-gray-600 focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
                title="Voltar"
                @click="voltarMesa"
              >
                <ArrowLeftIcon class="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>

              <div>
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                  {{ protocolo.numero }}
                </h1>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Aberto em {{ formatarData(protocolo.criadoEm) }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <button type="button" class="btn-icon" title="Imprimir">
                <PrinterIcon class="h-5 w-5" />
              </button>
              <button type="button" class="btn-icon" title="Compartilhar">
                <ShareIcon class="h-5 w-5" />
              </button>
              <button type="button" class="btn-icon" title="Mais opções">
                <EllipsisVerticalIcon class="h-5 w-5" />
              </button>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <StatusBadge :status="protocolo.status" tipo="zeladoria" :show-icon="true" size="lg" />

            <UrgenciaBadge
              :nivel="protocolo.urgencia"
              :sugestao-ia-pendente="sugestaoUrgenciaPendente"
              size="lg"
            />

            <button
              v-if="podeAlterarUrgenciaEfetivo"
              type="button"
              class="btn-secondary text-sm min-h-[40px] focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
              @click="modalAlterarUrgencia = true"
            >
              Alterar urgência
            </button>

            <div
              :class="slaBadgeClass"
              class="inline-flex items-center gap-2 rounded-badge px-4 py-2 font-semibold"
            >
              <ClockIcon class="h-5 w-5" />
              <span>{{ formatarSLA(protocolo.sla) }}</span>
            </div>

            <div
              class="inline-flex items-center gap-2 rounded-badge bg-primary-100 px-4 py-2 font-semibold text-primary-700 dark:bg-primary-900 dark:text-primary-300"
            >
              <WrenchScrewdriverIcon class="h-5 w-5" />
              <span>{{ protocolo.servico }}</span>
            </div>

            <div
              class="inline-flex items-center gap-2 rounded-badge bg-gray-100 px-4 py-2 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
            >
              <UserIcon class="h-5 w-5" />
              <span>{{ protocolo.cidadao?.nome || '—' }}</span>
            </div>

            <span
              v-if="indicadorFluxoDireto"
              class="inline-flex items-center gap-2 rounded-badge px-4 py-2 text-xs font-semibold bg-teal-50 text-teal-900 dark:bg-teal-950/40 dark:text-teal-100 border border-teal-200/80 dark:border-teal-700/50"
              :title="indicadorFluxoDireto.title"
            >
              <ArrowsRightLeftIcon class="h-4 w-4 shrink-0" />
              {{ indicadorFluxoDireto.label }}
            </span>
          </div>
        </div>
      </header>

      <div class="px-6 pt-4">
        <BannerAlertaIA
          v-if="sugestaoIaAtual && !protocoloIntegradoSuperOs"
          :sugestao="sugestaoIaAtual"
          :processando="processandoSugestaoIa"
          @acao="executarSugestaoIaBanner"
        />
      </div>

      <div class="flex gap-6 p-6">
        <div class="flex-1 space-y-6">
          <ProtocoloContexto
            :protocolo="protocolo"
            :pode-alterar-urgencia="podeAlterarUrgenciaEfetivo"
            :processando-urgencia="processandoUrgencia"
            @abrir-diligencia="mostrarModalDiligencia = true"
            @atualizar-diligencia="recarregarDiligencia"
            @alterar-urgencia="modalAlterarUrgencia = true"
            @acao-urgencia-ia="onAcaoUrgenciaIa"
          />
        </div>

        <div class="w-full max-w-xl lg:w-[540px] shrink-0 space-y-6 lg:sticky lg:top-28 lg:self-start lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto">
          <ProtocoloOperacao
            :protocolo="protocolo"
            :integrado-super-os="protocoloIntegradoSuperOs"
            :super-os-codigo="protocolo.superOsCodigo"
            :super-os-id="protocolo.superOsId"
            :salvando-validacao="salvandoValidacao"
            :salvando-devolucao="salvandoDevolucao"
            @validar="onValidar"
            @devolver="onDevolver"
            @adicionar-setor="abrirDespachoContinuo"
            @preencher-despacho="preencherDespachoComTriagem"
          />
        </div>
      </div>
    </template>

    <ModalAbrirDiligencia
      :aberto="mostrarModalDiligencia"
      :protocolo="protocolo"
      @fechar="mostrarModalDiligencia = false"
      @criada="recarregarDiligencia"
    />

    <DespacharProtocolo
      v-if="protocolo && !protocoloIntegradoSuperOs"
      :protocolo="protocolo"
      :aberto="mostrarDespacho"
      :salvando="despachando"
      :prefill-ordens="prefillOrdens"
      @fechar="fecharDespacho"
      @confirmar="confirmarDespacho"
    />

    <ModalAlterarUrgencia
      :aberto="modalAlterarUrgencia"
      :protocolo="protocolo"
      :salvando="processandoUrgencia"
      @fechar="modalAlterarUrgencia = false"
      @confirmar="confirmarAlteracaoUrgencia"
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
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  ArrowLeftIcon,
  ClockIcon,
  PrinterIcon,
  ShareIcon,
  EllipsisVerticalIcon,
  WrenchScrewdriverIcon,
  UserIcon,
  ArrowsRightLeftIcon
} from '@heroicons/vue/24/outline'
import { indicadorFluxoDiretoProtocolo } from '@/constants/governancaFluxo'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import ProtocoloContexto from '@/components/backoffice/protocolo/ProtocoloContexto.vue'
import ModalAbrirDiligencia from '@/components/backoffice/protocolo/ModalAbrirDiligencia.vue'
import ProtocoloOperacao from '@/components/backoffice/protocolo/ProtocoloOperacao.vue'
import DespacharProtocolo from '@/components/backoffice/DespacharProtocolo.vue'
import BannerAlertaIA from '@/components/backoffice/ia/BannerAlertaIA.vue'
import UrgenciaBadge from '@/components/backoffice/common/UrgenciaBadge.vue'
import ModalAlterarUrgencia from '@/components/backoffice/protocolo/ModalAlterarUrgencia.vue'
import { useBackofficeStore } from '@/stores/backoffice'
import { useRbac } from '@/composables/useRbac'
import { sugestaoIaPendente } from '@/utils/urgenciaHelpers'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import { useSuperOSStore } from '@/stores/super_os'
import { useFormatacao } from '@/composables/useFormatacao'
import { getApiErrorMessage } from '@/utils/apiError'
import { buildPrefillOrdensFromTriagem } from '@/utils/triagemEncaminhamento'

const { formatarSLA } = useFormatacao()

const router = useRouter()
const route = useRoute()
const backofficeStore = useBackofficeStore()
const notificacoesInternasStore = useNotificacoesInternasStore()
const superOSStore = useSuperOSStore()
const { podeAlterarUrgencia } = useRbac()

const {
  protocoloAtual,
  loadingDetalhes,
  salvandoValidacao,
  salvandoDevolucao,
  despachando
} = storeToRefs(backofficeStore)

const mostrarDespacho = ref(false)
const mostrarModalDiligencia = ref(false)
const prefillOrdens = ref([])
const erroCarregamento = ref(null)
const toastAberto = ref(false)
const toastMensagem = ref('')
const toastSucesso = ref(false)
const processandoSugestaoIa = ref(false)
const modalAlterarUrgencia = ref(false)
const processandoUrgencia = ref(false)
let toastTimer = null

const protocolo = computed(() => protocoloAtual.value)

const sugestaoUrgenciaPendente = computed(() => sugestaoIaPendente(protocolo.value))

const podeAlterarUrgenciaEfetivo = computed(() => {
  if (protocolo.value && protocolo.value.podeAlterarUrgencia !== undefined) {
    return Boolean(protocolo.value.podeAlterarUrgencia)
  }
  return Boolean(podeAlterarUrgencia.value)
})

const indicadorFluxoDireto = computed(() => indicadorFluxoDiretoProtocolo(protocolo.value))

const protocoloIntegradoSuperOs = computed(() => Boolean(protocolo.value?.superOsId))

const sugestaoIaAtual = computed(() => {
  const id = protocolo.value?.id
  if (!id || protocoloIntegradoSuperOs.value) return null
  return superOSStore.sugestaoParaProtocolo(id)
})

const slaBadgeClass = computed(() => {
  const sla = protocolo.value?.sla
  if (protocolo.value?.slaPausado || protocolo.value?.status === 'aguardando_cidadao') {
    return 'bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100'
  }
  if (!sla) return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  if (sla.vencido) {
    return 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300'
  }
  if (sla.horasRestantes <= 24) {
    return 'bg-warning-100 text-warning-700 dark:bg-warning-900 dark:text-warning-300'
  }
  return 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300'
})

function formatarData(data) {
  if (!data) return '—'
  return new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

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

async function recarregarDiligencia() {
  const id = route.params.id
  if (!id) return
  try {
    await backofficeStore.carregarDetalhesProtocolo(id)
    mostrarToast('Diligência atualizada.', true)
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Falha ao atualizar.'), false)
  }
}

async function onAcaoUrgenciaIa({ acao }) {
  const id = protocolo.value?.id
  if (!id || !acao) return
  processandoUrgencia.value = true
  try {
    await backofficeStore.alterarUrgenciaProtocolo(id, { acao })
    mostrarToast('Urgência atualizada com sucesso.', true)
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível atualizar a urgência.'), false)
  } finally {
    processandoUrgencia.value = false
  }
}

async function confirmarAlteracaoUrgencia(payload) {
  const id = protocolo.value?.id
  if (!id) return
  processandoUrgencia.value = true
  try {
    await backofficeStore.alterarUrgenciaProtocolo(id, payload)
    modalAlterarUrgencia.value = false
    mostrarToast('Urgência alterada e registrada no histórico.', true)
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível alterar a urgência.'), false)
  } finally {
    processandoUrgencia.value = false
  }
}

async function carregar() {
  const id = route.params.id
  if (!id) {
    erroCarregamento.value = 'Protocolo não informado na URL.'
    return
  }
  erroCarregamento.value = null
  try {
    await Promise.all([
      backofficeStore.carregarDetalhesProtocolo(id),
      superOSStore.buscarSugestoes().catch(() => null)
    ])
  } catch (e) {
    erroCarregamento.value = getApiErrorMessage(
      e,
      'Não foi possível carregar os detalhes do protocolo.'
    )
  }
}

async function onValidar(dados) {
  const id = protocolo.value?.id
  if (!id) return
  try {
    await backofficeStore.validarProtocolo(id, {
      resposta_cidadao: (dados.resposta || dados.resposta_cidadao || '').trim(),
      observacoes_internas: (dados.observacoes || dados.observacoes_internas || '').trim()
    })
    mostrarToast('Protocolo validado e encerrado com sucesso.')
    setTimeout(() => voltarMesa(), 800)
  } catch (e) {
    mostrarToast(
      getApiErrorMessage(e, 'Não foi possível validar o protocolo.')
    )
  }
}

function abrirDespachoContinuo() {
  prefillOrdens.value = []
  mostrarDespacho.value = true
}

function preencherDespachoComTriagem(unidades) {
  const lista = Array.isArray(unidades) ? unidades : []
  if (!lista.length) return
  const ordens = buildPrefillOrdensFromTriagem(protocolo.value, lista)
  if (!ordens.length) {
    mostrarToast('As unidades sugeridas já possuem ordem neste protocolo.')
    return
  }
  prefillOrdens.value = ordens
  mostrarDespacho.value = true
}

function fecharDespacho() {
  mostrarDespacho.value = false
  prefillOrdens.value = []
}

async function confirmarDespacho(payload) {
  const id = protocolo.value?.id
  if (!id) return
  try {
    await backofficeStore.despacharProtocolo(id, payload)
    fecharDespacho()
    mostrarToast('Nova secretaria acionada no protocolo.')
    await backofficeStore.carregarDetalhesProtocolo(id)
    notificacoesInternasStore.carregar({ silencioso: true }).catch(() => null)
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível concluir o despacho.'))
  }
}

async function executarSugestaoIaBanner() {
  const sug = sugestaoIaAtual.value
  const id = protocolo.value?.id
  if (!sug || !id) return

  processandoSugestaoIa.value = true
  try {
    if (sug.tipo_acao === 'anexar') {
      const data = await superOSStore.anexarProtocolo(sug.super_os_id, id)
      await backofficeStore.carregarDetalhesProtocolo(id)
      const codigo = data?.super_os?.codigo || sug.super_os_codigo || ''
      mostrarToast(
        `Protocolo anexado à Super OS${codigo ? ` ${codigo}` : ''} com sucesso.`,
        true
      )
    } else {
      const data = await superOSStore.aprovarSugestao(sug)
      await backofficeStore.carregarDetalhesProtocolo(id)
      const codigo = data?.super_os?.codigo || ''
      mostrarToast(
        `Super OS criada${codigo ? ` (${codigo})` : ''}. Protocolos agrupados.`,
        true
      )
    }
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível aplicar a sugestão da IA.'))
  } finally {
    processandoSugestaoIa.value = false
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
    mostrarToast('Ordem devolvida à secretaria. O protocolo voltou para acompanhamento.')
    setTimeout(() => voltarMesa(), 800)
  } catch (e) {
    mostrarToast(
      getApiErrorMessage(e, 'Não foi possível devolver a ordem.')
    )
  }
}

onMounted(() => {
  carregar()
})

onUnmounted(() => {
  backofficeStore.limparProtocoloAtual()
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<style scoped>
.mesa-toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 60;
  max-width: 22rem;
  padding: 0.875rem 1.25rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(135deg, #0f766e, #0d9488);
  box-shadow: 0 10px 25px rgba(15, 118, 110, 0.35);
}

.mesa-toast--success {
  background: linear-gradient(135deg, #15803d, #22c55e);
  box-shadow: 0 10px 25px rgba(21, 128, 61, 0.35);
}

.mesa-toast-enter-active,
.mesa-toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.mesa-toast-enter-from,
.mesa-toast-leave-to {
  opacity: 0;
  transform: translateY(0.5rem);
}
</style>
