<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
      <div class="px-6 py-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <BuildingOffice2Icon class="w-8 h-8 text-primary-500" />
              {{ unidade.nome }}
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Gestão de Ordens de Serviço · {{ unidade.codigo }}
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              @click="atualizarDados"
              class="btn-secondary"
              :disabled="loading"
            >
              <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': loading }" />
              Atualizar
            </button>
          </div>
        </div>

        <p v-if="erro" class="mb-3 text-sm text-red-600 dark:text-red-400">{{ erro }}</p>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-card p-4 border border-blue-200 dark:border-blue-800">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-sm font-medium text-blue-700 dark:text-blue-300">OS Pendentes</p>
                <p class="text-3xl font-bold text-blue-900 dark:text-blue-100 mt-2">
                  {{ kpis.pendentes }}
                </p>
              </div>
              <ClockIcon class="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div class="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-card p-4 border border-red-200 dark:border-red-800">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-sm font-medium text-red-700 dark:text-red-300">OS Atrasadas (SLA)</p>
                <p class="text-3xl font-bold text-red-900 dark:text-red-100 mt-2">
                  {{ kpis.atrasadas }}
                </p>
              </div>
              <ExclamationTriangleIcon class="w-8 h-8 text-red-500" />
            </div>
          </div>

          <div class="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 rounded-card p-4 border border-amber-200 dark:border-amber-800">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-sm font-medium text-amber-700 dark:text-amber-300">Aguardando Campo</p>
                <p class="text-3xl font-bold text-amber-900 dark:text-amber-100 mt-2">
                  {{ kpis.aguardandoCampo }}
                </p>
              </div>
              <TruckIcon class="w-8 h-8 text-amber-500" />
            </div>
          </div>

          <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-card p-4 border border-green-200 dark:border-green-800">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-sm font-medium text-green-700 dark:text-green-300">Concluídas Hoje</p>
                <p class="text-3xl font-bold text-green-900 dark:text-green-100 mt-2">
                  {{ kpis.concluidasHoje }}
                </p>
              </div>
              <CheckCircleIcon class="w-8 h-8 text-green-500" />
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="px-6 pt-4">
      <RadarOperacionalCard
        storage-key="radar-setorial"
        :unidade-nome-override="unidade.nome"
        class="mb-4"
      />
    </div>

    <div class="px-6 py-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-3 flex-wrap">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              :value="filtros.busca"
              type="text"
              placeholder="Buscar OS ou protocolo..."
              class="input pl-10 w-80 max-w-full"
              @input="onBuscaInput"
            />
          </div>

          <button
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-button text-sm font-medium transition-all
                   bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200
                   border border-gray-300 dark:border-gray-600
                   hover:border-primary-500 hover:text-primary-500"
            :class="totalFiltrosAvancados > 0 ? 'border-primary-500 text-primary-600 dark:text-primary-400 ring-1 ring-primary-500/30' : ''"
            @click="abrirFiltrosAvancados"
          >
            <FunnelIcon class="w-5 h-5" />
            <span>Mais filtros</span>
            <span
              v-if="totalFiltrosAvancados > 0"
              class="badge bg-primary-600 text-white min-w-[1.25rem] justify-center"
            >
              {{ totalFiltrosAvancados }}
            </span>
          </button>
        </div>

        <div class="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-input p-1">
          <button
            type="button"
            @click="visualizacao = 'lista'"
            :class="visualizacao === 'lista' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''"
            class="px-4 py-2 rounded-lg text-sm font-medium"
          >
            Lista
          </button>
          <button
            type="button"
            @click="visualizacao = 'kanban'"
            :class="visualizacao === 'kanban' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''"
            class="px-4 py-2 rounded-lg text-sm font-medium"
          >
            Kanban
          </button>
        </div>
      </div>

      <div
        v-if="filtrosAtivosArray.length"
        class="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700"
      >
        <span class="text-xs text-gray-500 dark:text-gray-400">Filtros ativos:</span>
        <button
          v-for="filtro in filtrosAtivosArray"
          :key="filtro.key"
          type="button"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
                 bg-primary-50 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200
                 hover:bg-primary-100 dark:hover:bg-primary-900/50"
          @click="removerFiltro(filtro.key)"
        >
          {{ filtro.label }}
          <XMarkIcon class="w-3.5 h-3.5" />
        </button>
        <button
          type="button"
          class="text-xs text-gray-500 hover:text-primary-600 underline"
          @click="limparFiltrosERecarregar"
        >
          Limpar todos
        </button>
      </div>
    </div>

    <div id="setorial-worklist" class="px-6 py-6">
      <WorklistOS
        :ordens="ordensFiltradas"
        :visualizacao="visualizacao"
        :carregando="loading"
        @abrir-os="abrirOS"
      />
    </div>

    <ModalFormalizacaoOS
      v-if="osAtual && modalAberto"
      :ordem="osAtual"
      :aberto="modalAberto"
      :gerando-link="gerandoLink"
      :enviando="solicitandoAssinatura"
      :textos-padrao="textosPadraoAtivos"
      :carregando-textos="textosPadraoLoading"
      :textos-padrao-tentou-carregar="textosPadraoTentouCarregar"
      :erro-textos-padrao="erroTextosPadrao"
      :enviando-evidencias="enviandoEvidencias"
      :solicitando-assinatura="solicitandoAssinatura"
      @fechar="fecharModal"
      @enviar-gestor="enviarDespachoAoGestor"
      @enviar-evidencias="onEnviarEvidencias"
      @gerar-link="onGerarLink"
      @toast="mostrarToast"
      @diligencia-atualizada="onDiligenciaAtualizada"
    />

    <ModalFiltrosAvancadosSetorial
      :aberto="mostrarFiltrosAvancados"
      :filtros-atuais="filtros"
      :opcoes="opcoesFiltrosSetorial"
      @fechar="mostrarFiltrosAvancados = false"
      @aplicar="aplicarFiltrosAvancados"
    />

    <Teleport to="body">
      <transition name="setorial-toast">
        <div
          v-if="toastAberto"
          class="setorial-toast"
          :class="{ 'setorial-toast--sucesso-no': toastSucessoNo }"
          role="status"
        >
          <CheckCircleIcon v-if="toastSucessoNo" class="w-5 h-5 shrink-0" aria-hidden="true" />
          <span>{{ toastMensagem }}</span>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { watchDebounced } from '@vueuse/core'
import {
  BuildingOffice2Icon,
  ArrowPathIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  TruckIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

import RadarOperacionalCard from '@/components/backoffice/agente/RadarOperacionalCard.vue'
import { aplicarQueryRadarNoSetorial } from '@/composables/useRadarQuerySync'
import WorklistOS from '@/components/backoffice/setorial/WorklistOS.vue'
import ModalFormalizacaoOS from '@/components/backoffice/setorial/ModalFormalizacaoOS.vue'
import ModalFiltrosAvancadosSetorial from '@/components/backoffice/setorial/ModalFiltrosAvancadosSetorial.vue'
import { useSetorialStore } from '@/stores/setorial'
import { useTextosPadraoStore } from '@/stores/textosPadrao'
import { useNotificacoesInternasStore } from '@/stores/notificacoesInternas'
import { useAssinaturasStore } from '@/stores/assinaturas'
import { getApiErrorMessage } from '@/utils/apiError'

const route = useRoute()
const setorialStore = useSetorialStore()
const textosPadraoStore = useTextosPadraoStore()
const notificacoesStore = useNotificacoesInternasStore()
const assinaturasStore = useAssinaturasStore()
const solicitandoAssinatura = computed(() => assinaturasStore.processando)
const {
  ordens,
  loading,
  gerandoLink,
  enviandoEvidencias,
  erro,
  kpis,
  unidade,
  filtros,
  opcoesFiltrosSetorial,
  totalFiltrosAvancados
} = storeToRefs(setorialStore)
const {
  itens: textosPadrao,
  loading: textosPadraoLoading,
  erro: textosStoreErro,
  semPermissaoUnidade
} = storeToRefs(textosPadraoStore)

const textosPadraoTentouCarregar = ref(false)
const erroTextosPadrao = computed(() => {
  if (semPermissaoUnidade.value) {
    return 'Sua conta não tem unidade vinculada; não é possível carregar textos oficiais da secretaria.'
  }
  return textosStoreErro.value || ''
})

const textosPadraoAtivos = computed(() =>
  (textosPadrao.value || []).filter((t) => t.ativo)
)

const visualizacao = ref('lista')
const modalAberto = ref(false)
const osIdModal = ref(null)
const mostrarFiltrosAvancados = ref(false)

const STATUS_OS_LABEL = {
  nova: 'Nova',
  aguardando_campo: 'Aguardando campo',
  aguardando_assinatura: 'Aguardando gestor',
  concluida: 'Concluída'
}

const filtrosAtivosArray = computed(() => {
  const ativos = []
  const f = filtros.value
  if (f.busca) ativos.push({ key: 'busca', label: `Busca: ${f.busca}` })
  for (const id of f.servicoIds || []) {
    const s = opcoesFiltrosSetorial.value.servicos?.find((x) => x.id === id)
    ativos.push({ key: `servico:${id}`, kind: 'servico', id, label: s?.nome || 'Serviço' })
  }
  for (const b of f.bairros || []) {
    ativos.push({ key: `bairro:${b}`, kind: 'bairro', value: b, label: `Bairro: ${b}` })
  }
  for (const st of f.statusLista || []) {
    const stMeta = opcoesFiltrosSetorial.value.status?.find((x) => x.value === st)
    ativos.push({
      key: `status:${st}`,
      kind: 'status',
      value: st,
      label: stMeta?.label || STATUS_OS_LABEL[st] || st
    })
  }
  for (const u of f.urgenciaLista || []) {
    const uMeta = opcoesFiltrosSetorial.value.urgencias?.find((x) => x.value === u)
    ativos.push({
      key: `urgencia:${u}`,
      kind: 'urgencia',
      value: u,
      label: `Urgência: ${uMeta?.label || u}`
    })
  }
  if (f.apenasReabertos) {
    ativos.push({ key: 'apenasReabertos', kind: 'apenasReabertos', label: 'Apenas reabertos' })
  }
  if (f.apenasSugestaoUrgenciaIa) {
    ativos.push({
      key: 'apenasSugestaoUrgenciaIa',
      kind: 'apenasSugestaoUrgenciaIa',
      label: 'Triagem de urgência (revisão pendente)'
    })
  }
  return ativos
})

const toastAberto = ref(false)
const toastMensagem = ref('')
const toastSucessoNo = ref(false)
let toastTimer = null

const osAtual = computed(() =>
  osIdModal.value ? setorialStore.ordemPorId(osIdModal.value) : null
)

const ordensFiltradas = computed(() => {
  const resultado = [...ordens.value]
  resultado.sort((a, b) => {
    if (a.sla_status === 'vencido' && b.sla_status !== 'vencido') return -1
    if (a.sla_status !== 'vencido' && b.sla_status === 'vencido') return 1
    return new Date(b.criado_em) - new Date(a.criado_em)
  })
  return resultado
})

function onBuscaInput(e) {
  setorialStore.setFiltroBusca(e.target.value)
}

async function recarregarOrdens() {
  try {
    await setorialStore.carregarOrdens()
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Erro ao filtrar ordens.'), true)
  }
}

function removerFiltro(key) {
  if (key === 'busca') {
    setorialStore.setFiltroBusca('')
  } else {
    const item = filtrosAtivosArray.value.find((x) => x.key === key)
    if (!item?.kind) return
    const f = { ...filtros.value }
    if (item.kind === 'servico') {
      f.servicoIds = f.servicoIds.filter((id) => id !== item.id)
    } else if (item.kind === 'bairro') {
      f.bairros = f.bairros.filter((b) => b !== item.value)
    } else if (item.kind === 'status') {
      f.statusLista = f.statusLista.filter((s) => s !== item.value)
    } else if (item.kind === 'urgencia') {
      f.urgenciaLista = f.urgenciaLista.filter((u) => u !== item.value)
    } else if (item.kind === 'apenasReabertos') {
      f.apenasReabertos = false
    } else if (item.kind === 'apenasSugestaoUrgenciaIa') {
      f.apenasSugestaoUrgenciaIa = false
    }
    setorialStore.aplicarFiltrosAvancados({
      servicoIds: f.servicoIds,
      bairros: f.bairros,
      statusLista: f.statusLista,
      urgenciaLista: f.urgenciaLista,
      apenasReabertos: f.apenasReabertos,
      apenasSugestaoUrgenciaIa: f.apenasSugestaoUrgenciaIa
    })
  }
  recarregarOrdens()
}

function limparFiltrosERecarregar() {
  setorialStore.limparFiltros()
  recarregarOrdens()
}

async function abrirFiltrosAvancados() {
  try {
    await setorialStore.carregarOpcoesFiltrosSetorial()
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível carregar opções de filtro.'), true)
  }
  mostrarFiltrosAvancados.value = true
}

function aplicarFiltrosAvancados(payload) {
  setorialStore.aplicarFiltrosAvancados(payload)
  mostrarFiltrosAvancados.value = false
  recarregarOrdens()
}

watchDebounced(
  () => filtros.value.busca,
  () => recarregarOrdens(),
  { debounce: 450 }
)

function mostrarToast(mensagem, isErro = false, opts = {}) {
  toastMensagem.value = mensagem
  toastSucessoNo.value = Boolean(opts.noEncerrado)
  toastAberto.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastAberto.value = false
    toastSucessoNo.value = false
  }, isErro ? 5500 : opts.noEncerrado ? 6000 : 4000)
}

async function carregarTextosPadrao() {
  textosPadraoTentouCarregar.value = true
  try {
    await textosPadraoStore.carregar()
  } catch {
    /* erro em textosStoreErro / semPermissaoUnidade */
  }
}

async function atualizarDados() {
  try {
    await Promise.all([setorialStore.carregarOrdens(), carregarTextosPadrao()])
  } catch (e) {
    mostrarToast(
      getApiErrorMessage(e, 'Erro ao atualizar ordens.'),
      true
    )
  }
}

async function abrirOS(ordem) {
  osIdModal.value = ordem.id
  modalAberto.value = true
  carregarTextosPadrao()
  try {
    await setorialStore.carregarOrdemDetalhe(ordem.id)
  } catch (e) {
    mostrarToast(
      getApiErrorMessage(e, 'Não foi possível carregar o detalhe da OS.'),
      true
    )
  }
}

async function onDiligenciaAtualizada() {
  if (!osIdModal.value) return
  try {
    await Promise.all([
      setorialStore.carregarOrdemDetalhe(osIdModal.value),
      setorialStore.carregarOrdens()
    ])
    mostrarToast('Diligência atualizada.')
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Diligência salva, mas falhou ao atualizar a lista.'), true)
  }
}

function fecharModal() {
  modalAberto.value = false
  setTimeout(() => {
    osIdModal.value = null
  }, 300)
}

async function onEnviarEvidencias(arquivos) {
  if (!osIdModal.value) return
  try {
    await setorialStore.enviarEvidencias(osIdModal.value, arquivos)
    mostrarToast(
      `${arquivos.length} arquivo(s) anexado(s) como evidência (opcional para formalizar).`
    )
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Falha no upload das evidências.'), true)
  }
}

async function onGerarLink() {
  if (!osIdModal.value) return
  try {
    const { url } = await setorialStore.gerarLinkMagico(osIdModal.value)
    mostrarToast(url ? 'Link mágico gerado. Copie a URL no painel.' : 'Link gerado com sucesso.')
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Falha ao gerar link.'), true)
  }
}

async function enviarDespachoAoGestor(dados) {
  if (!osIdModal.value) return
  if (!dados.despacho?.trim()) {
    mostrarToast('Preencha a descrição técnica do despacho.', true)
    return
  }
  try {
    const res = await assinaturasStore.solicitar({
      ordemServicoId: dados.ordemId || osIdModal.value,
      despachoTecnico: dados.despacho
    })
    const nome =
      res?.solicitacao_assinatura?.assinante_destino_nome ||
      res?.assinante_destino_nome ||
      'gestor da secretaria'
    const jaPendente = Boolean(res?.already_pending)
    mostrarToast(
      jaPendente
        ? `Despacho já enviado. Aguardando assinatura de ${nome}.`
        : `Despacho enviado para assinatura de ${nome}.`
    )
    fecharModal()
    await Promise.all([
      setorialStore.carregarOrdens(),
      notificacoesStore.carregar({ silencioso: true }).catch(() => null)
    ])
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível enviar o despacho ao gestor.'), true)
  }
}

async function sincronizarQueryRadarSetorial() {
  if (aplicarQueryRadarNoSetorial(route, setorialStore)) {
    await atualizarDados()
    requestAnimationFrame(() => {
      document.getElementById('setorial-worklist')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

watch(
  () => route.query,
  () => {
    if (route.name !== 'backoffice-setorial') return
    sincronizarQueryRadarSetorial()
  },
  { deep: true }
)

onMounted(() => {
  aplicarQueryRadarNoSetorial(route, setorialStore)
  setorialStore.carregarOpcoesFiltrosSetorial().catch(() => null)
  atualizarDados()
})
</script>

<style scoped>
.setorial-toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 70;
  max-width: 24rem;
  padding: 0.875rem 1.25rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  background: linear-gradient(135deg, #0f766e, #0d9488);
  box-shadow: 0 10px 25px rgba(15, 118, 110, 0.35);
}

.setorial-toast--sucesso-no {
  background: linear-gradient(135deg, #047857, #10b981);
  box-shadow: 0 12px 28px rgba(16, 185, 129, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.25);
  font-weight: 600;
}

.setorial-toast-enter-active,
.setorial-toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.setorial-toast-enter-from,
.setorial-toast-leave-to {
  opacity: 0;
  transform: translateY(0.5rem);
}
</style>
