<template>
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] flex items-center justify-center p-4 overflow-y-auto"
      @click.self="$emit('fechar')"
    >
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-5xl my-8 overflow-hidden">
          <!-- Header (padrão premium — alinhado a ModalPerfil / GestaoPerfis) -->
          <div class="relative bg-gradient-to-r from-primary-600 via-primary-500 to-cyan-500 p-6 overflow-hidden">
            <div
              class="absolute inset-0 bg-gradient-to-r from-transparent via-white/15 to-transparent animate-shimmer"
              aria-hidden="true"
            />

            <div class="relative flex items-start justify-between gap-4">
              <div class="flex items-center gap-4 min-w-0">
                <div class="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                  <Squares2X2Icon class="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 class="text-2xl font-bold text-white mb-1 flex items-center gap-2">
                    {{ modoEdicao ? 'Editar serviço' : 'Novo serviço no catálogo' }}
                    <SparklesIcon class="w-6 h-6 text-cyan-100 opacity-90" />
                  </h2>
                  <p class="text-primary-100 text-sm">
                    Metadados operacionais e treinamento do assistente conversacional
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-2 shrink-0">
                <button
                  v-if="modoEdicao"
                  type="button"
                  class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-white/15 hover:bg-white/25 text-white transition-colors"
                  title="Histórico de versões publicadas"
                  @click="historicoAberto = true"
                >
                  <ClockIcon class="w-5 h-5" />
                  Histórico
                </button>
                <button
                  type="button"
                  class="p-2 hover:bg-white/20 rounded-lg transition-colors"
                  aria-label="Fechar"
                  @click="$emit('fechar')"
                >
                  <XMarkIcon class="w-6 h-6 text-white" />
                </button>
              </div>
            </div>
          </div>

          <!-- Barra de versionamento -->
          <div
            v-if="modoEdicao"
            class="px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <div class="flex flex-wrap items-center gap-2">
              <span
                class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200 ring-1 ring-slate-200/80 dark:ring-slate-600"
              >
                v{{ meta.versao_publicada }}
              </span>
              <span
                v-if="meta.tem_rascunho_pendente || alteracoesLocais"
                class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 dark:bg-amber-950/50 dark:text-amber-200 ring-1 ring-amber-300/60 dark:ring-amber-800/50"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" aria-hidden="true" />
                Rascunho pendente — alterações ainda não visíveis ao cidadão
              </span>
              <span
                v-else-if="meta.publicado_em"
                class="text-[11px] text-gray-500 dark:text-gray-400"
              >
                Publicado em {{ formatarDataPublicacao(meta.publicado_em) }}
              </span>
            </div>

            <div v-if="modoEdicao" class="flex flex-wrap items-center gap-2 justify-end">
              <button
                v-if="meta.tem_rascunho_pendente"
                type="button"
                class="text-xs font-medium text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 underline-offset-2 hover:underline disabled:opacity-50"
                :disabled="catalogoStore.loadingServicos"
                @click="confirmarDescartar = true"
              >
                Descartar rascunho
              </button>
            </div>
          </div>

          <div class="p-6 space-y-6 max-h-[calc(100vh-14rem)] overflow-y-auto">
            <!-- Governança -->
            <CardSecao
              titulo="Governança do serviço"
              subtitulo="Dados exibidos ao cidadão e roteamento interno"
              :icon="Cog6ToothIcon"
            >
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Nome do serviço *
                  </label>
                  <input
                    v-model="formulario.nome"
                    type="text"
                    class="input"
                    placeholder="Ex.: Buracos e Pavimentação"
                  />
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Descrição
                  </label>
                  <textarea
                    v-model="formulario.descricao"
                    rows="2"
                    class="input resize-none min-h-[88px]"
                    placeholder="Contexto exibido ao cidadão e à IA..."
                  />
                </div>

                <div>
                  <SlaUnidadeInput v-model="formulario.sla_padrao_horas" label="SLA *" />
                </div>

                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Categoria *
                  </label>
                  <select v-model="formulario.categoria_id" class="input" required>
                    <option :value="null" disabled>Selecione a categoria...</option>
                <option
                  v-for="cat in categorias"
                  :key="cat.id"
                  :value="String(cat.id)"
                  :disabled="!cat.ativo && String(cat.id) !== String(formulario.categoria_id)"
                >
                  {{ cat.nome }}{{ cat.ativo ? '' : ' (inativa)' }}
                </option>
                  </select>
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Fluxo de tramitação *
                  </label>
                  <select v-model="formulario.fluxo_tramitacao" class="input">
                    <option
                      v-for="opt in fluxoTramitacaoOpcoes"
                      :key="opt.value"
                      :value="opt.value"
                    >
                      {{ opt.label }}
                    </option>
                  </select>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ descricaoFluxoAtual }}
                  </p>
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    {{ rotuloUnidadeResponsavel }} *
                  </label>
                  <p v-if="formulario.fluxo_tramitacao === 'ouvidoria_encaminha'" class="text-xs text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2 mb-2">
                    Neste fluxo, esta unidade é o <strong>canal</strong> (ex.: Ouvidoria). As secretarias executoras recebem a demanda via despacho.
                  </p>
                  <select v-model="formulario.unidade_responsavel_id" class="input" required>
                    <option :value="null" disabled>Selecione a secretaria...</option>
                    <option
                      v-for="u in unidadesParaSelect"
                      :key="u.id"
                      :value="String(u.id)"
                    >
                      {{ u.nome }}{{ u.sigla ? ` (${u.sigla})` : '' }}
                    </option>
                  </select>
                </div>

                <div
                  class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 md:col-span-2"
                >
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="formulario.permite_cluster"
                    :aria-labelledby="`servico-cluster-label-${uid}`"
                    :class="[
                      'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors mt-0.5',
                      formulario.permite_cluster
                        ? 'bg-primary-600'
                        : 'bg-gray-300 dark:bg-gray-600'
                    ]"
                    @click="formulario.permite_cluster = !formulario.permite_cluster"
                  >
                    <span
                      :class="[
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition',
                        formulario.permite_cluster ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                  <div class="flex-1 min-w-0">
                    <p
                      :id="`servico-cluster-label-${uid}`"
                      class="text-sm font-semibold text-gray-900 dark:text-white"
                    >
                      Permitir agrupamento em Cluster (Super OS)
                    </p>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 leading-relaxed">
                      Quando ativo, demandas próximas deste serviço podem ser unificadas em uma única Ordem de Serviço
                      coletiva. Desative para atendimentos individuais ou sensíveis (ex: Assistência Social, Castração).
                    </p>
                  </div>
                </div>

                <div
                  class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 md:col-span-2"
                >
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="formulario.ativo"
                    :aria-labelledby="`servico-ativo-label-${uid}`"
                    :class="[
                      'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors mt-0.5',
                      formulario.ativo ? 'bg-green-600' : 'bg-gray-300 dark:bg-gray-600'
                    ]"
                    @click="formulario.ativo = !formulario.ativo"
                  >
                    <span
                      :class="[
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition',
                        formulario.ativo ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                  <div class="flex-1 min-w-0">
                    <p
                      :id="`servico-ativo-label-${uid}`"
                      class="text-sm font-semibold text-gray-900 dark:text-white"
                    >
                      Serviço ativo no PWA
                    </p>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 leading-relaxed">
                      Serviços inativos não aparecem para novos atendimentos do cidadão.
                    </p>
                  </div>
                </div>
              </div>
            </CardSecao>

            <RegrasElegibilidadeProtocolo v-model="regrasProtocolo" />

            <AiSchemaBuilder v-model="requisitos" />
          </div>

          <!-- Footer -->
          <div
            class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50"
          >
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ requisitos.length }} dado(s) mapeado(s) para a IA · campos com * são obrigatórios
            </p>

            <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto justify-end">
              <button
                type="button"
                class="flex-1 sm:flex-none px-4 py-2 rounded-lg font-medium transition-colors border border-primary-300 dark:border-primary-600 text-primary-700 dark:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-950/40 disabled:opacity-40 disabled:cursor-not-allowed"
                :disabled="!modoEdicao"
                :title="modoEdicao ? 'Abrir simulador de conversa' : 'Salve o serviço antes de testar o fluxo'"
                @click="abrirSandbox"
              >
                <span class="inline-flex items-center gap-2 justify-center">
                  <DevicePhoneMobileIcon class="w-5 h-5" />
                  Testar fluxo (Sandbox)
                </span>
              </button>
              <template v-if="modoEdicao">
                <button
                  type="button"
                  class="flex-1 sm:flex-none px-4 py-2 rounded-lg font-medium border border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-200 bg-amber-50 dark:bg-amber-950/30 hover:bg-amber-100 dark:hover:bg-amber-950/50 transition-colors disabled:opacity-50"
                  :disabled="catalogoStore.loadingServicos || !formularioValido"
                  @click="salvarRascunho"
                >
                  Salvar rascunho
                </button>
                <button
                  type="button"
                  class="flex-1 sm:flex-none px-4 py-2 rounded-lg font-semibold bg-green-600 hover:bg-green-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="
                    catalogoStore.loadingServicos ||
                    !formularioValido ||
                    (!meta.tem_rascunho_pendente && !alteracoesLocais)
                  "
                  @click="abrirModalPublicar"
                >
                  Publicar versão
                </button>
              </template>
              <button
                type="button"
                class="flex-1 sm:flex-none px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
                @click="$emit('fechar')"
              >
                Cancelar
              </button>
              <button
                v-if="!modoEdicao"
                type="button"
                class="flex-1 sm:flex-none px-6 py-2 btn-primary !py-2 !px-6 min-w-[140px]"
                :disabled="catalogoStore.loadingServicos || !formularioValido"
                @click="salvar"
              >
                <span
                  v-if="catalogoStore.loadingServicos"
                  class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                />
                {{ catalogoStore.loadingServicos ? 'Salvando…' : 'Criar serviço' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>

  <SandboxServicoDrawer
    v-if="modoEdicao"
    :aberto="sandboxAberto"
    :servico-id="String(servicoAtual.id)"
    :nome-servico="formulario.nome || servicoAtual?.nome || 'Serviço'"
    :tem-rascunho-pendente="Boolean(meta.tem_rascunho_pendente)"
    @fechar="sandboxAberto = false"
  />

  <HistoricoVersoesServico
    :aberto="historicoAberto"
    :servico-id="String(servicoAtual?.id || '')"
    :versao-atual="meta.versao_publicada"
    :restaurando="restaurandoVersao"
    @fechar="historicoAberto = false"
    @restaurar="restaurarVersaoHistorico"
  />

  <Teleport to="body">
    <div
      v-if="modalPublicarAberto"
      class="fixed inset-0 z-[10070] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="modalPublicarAberto = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Publicar versão</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          O cidadão passará a ver o rascunho atual. Opcionalmente descreva o que mudou:
        </p>
        <input
          v-model="notaVersao"
          type="text"
          maxlength="255"
          class="input text-sm mb-4"
          placeholder="Ex.: Ajuste na regra de idade"
        />
        <div class="flex gap-3">
          <button type="button" class="btn-secondary flex-1" @click="modalPublicarAberto = false">Cancelar</button>
          <button
            type="button"
            class="flex-1 px-4 py-2 rounded-lg font-semibold bg-green-600 hover:bg-green-700 text-white disabled:opacity-50"
            :disabled="catalogoStore.loadingServicos"
            @click="confirmarPublicacao"
          >
            Publicar
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="confirmarDescartar"
      class="fixed inset-0 z-[10070] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="confirmarDescartar = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Descartar rascunho?</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          As alterações não publicadas serão perdidas. O PWA continua na versão v{{ meta.versao_publicada }}.
        </p>
        <div class="flex gap-3">
          <button type="button" class="btn-secondary flex-1" @click="confirmarDescartar = false">Cancelar</button>
          <button type="button" class="btn-danger flex-1" :disabled="catalogoStore.loadingServicos" @click="executarDescartar">
            Descartar
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCatalogoStore } from '@/stores/catalogo'
import { useAdminStore } from '@/stores/admin'
import {
  requisitosFromFormularioSchema,
  regrasProtocoloFromSchemaFormulario,
  formularioSchemaParaEdicao,
  schemaFormularioParaEdicao
} from '@/utils/catalogoMappers'
import { useAdminToast } from '@/composables/useAdminToast'
import HistoricoVersoesServico from './HistoricoVersoesServico.vue'
import AiSchemaBuilder from './AiSchemaBuilder.vue'
import RegrasElegibilidadeProtocolo from './RegrasElegibilidadeProtocolo.vue'
import SandboxServicoDrawer from './SandboxServicoDrawer.vue'
import CardSecao from './FormBuilderCardSecao.vue'
import SlaUnidadeInput from './SlaUnidadeInput.vue'
import { FLUXO_TRAMITACAO_OPCOES } from '@/constants/fluxoTramitacao'
import {
  XMarkIcon,
  Cog6ToothIcon,
  SparklesIcon,
  Squares2X2Icon,
  DevicePhoneMobileIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  servico: { type: Object, default: null }
})

const emit = defineEmits(['fechar', 'sucesso', 'atualizado'])

const uid = `fb-${Math.random().toString(36).slice(2, 9)}`

const catalogoStore = useCatalogoStore()
const adminStore = useAdminStore()
const { mostrarToast } = useAdminToast()
const { unidadesAtivas, unidades } = storeToRefs(adminStore)

const requisitos = ref([])
const regrasProtocolo = ref([])
const sandboxAberto = ref(false)
const historicoAberto = ref(false)
const modalPublicarAberto = ref(false)
const confirmarDescartar = ref(false)
const notaVersao = ref('')
const alteracoesLocais = ref(false)
const restaurandoVersao = ref(null)
const baselineCarregado = ref(false)

const categorias = computed(() => catalogoStore.categoriasCatalogo)

const fluxoTramitacaoOpcoes = FLUXO_TRAMITACAO_OPCOES

const formulario = reactive({
  nome: '',
  descricao: '',
  sla_padrao_horas: 72,
  fluxo_tramitacao: 'direto_secretaria',
  categoria_id: null,
  unidade_responsavel_id: null,
  ativo: true,
  permite_cluster: true,
  icone: ''
})

const descricaoFluxoAtual = computed(() => {
  return (
    fluxoTramitacaoOpcoes.find((o) => o.value === formulario.fluxo_tramitacao)?.descricao || ''
  )
})

const rotuloUnidadeResponsavel = computed(() => {
  if (formulario.fluxo_tramitacao === 'ouvidoria_encaminha') {
    return 'Unidade do canal (recebe e monitora)'
  }
  if (formulario.fluxo_tramitacao === 'hibrido') {
    return 'Unidade titular / canal'
  }
  return 'Unidade responsável (executora)'
})

const unidadesParaSelect = computed(() => {
  const lista = [...unidadesAtivas.value]
  const idSel = formulario.unidade_responsavel_id
  if (!idSel) return lista
  if (lista.some((u) => String(u.id) === idSel)) return lista
  const daListaCompleta = unidades.value.find((u) => String(u.id) === idSel)
  if (daListaCompleta) return [...lista, daListaCompleta]
  if (props.servico?.unidade_responsavel_nome) {
    return [
      ...lista,
      {
        id: idSel,
        nome: props.servico.unidade_responsavel_nome,
        sigla: '',
        ativo: false
      }
    ]
  }
  return lista
})

const servicoAtual = computed(() => {
  const id = props.servico?.id
  if (!id) return props.servico
  return catalogoStore.getServicoPorId(id) || props.servico
})

const meta = computed(() => ({
  versao_publicada: servicoAtual.value?.versao_publicada ?? 1,
  publicado_em: servicoAtual.value?.publicado_em || null,
  tem_rascunho_pendente: Boolean(servicoAtual.value?.tem_rascunho_pendente)
}))

const modoEdicao = computed(() => Boolean(servicoAtual.value?.id))

const formularioValido = computed(() => {
  return (
    String(formulario.nome || '').trim().length > 0 &&
    Number(formulario.sla_padrao_horas) > 0 &&
    formulario.categoria_id &&
    formulario.unidade_responsavel_id
  )
})

function preencherFormulario(servico) {
  baselineCarregado.value = false
  alteracoesLocais.value = false
  formulario.nome = servico?.nome || ''
  formulario.descricao = servico?.descricao || ''
  formulario.sla_padrao_horas = servico?.sla_padrao_horas ?? servico?.sla_horas ?? 72
  formulario.fluxo_tramitacao = servico?.fluxo_tramitacao || 'direto_secretaria'
  formulario.categoria_id = servico?.categoria_id ? String(servico.categoria_id) : null
  formulario.unidade_responsavel_id = servico?.unidade_responsavel_id
    ? String(servico.unidade_responsavel_id)
    : null
  formulario.ativo = servico?.ativo !== false
  formulario.permite_cluster = servico?.permite_cluster !== false
  formulario.icone = servico?.icone || ''

  const schemaLista = formularioSchemaParaEdicao(servico)
  requisitos.value = requisitosFromFormularioSchema(schemaLista)
  regrasProtocolo.value = regrasProtocoloFromSchemaFormulario(schemaFormularioParaEdicao(servico))
  requestAnimationFrame(() => {
    baselineCarregado.value = true
  })
}

function formatarDataPublicacao(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

watch(
  () => servicoAtual.value?.id,
  (id) => {
    if (id) preencherFormulario(servicoAtual.value)
  },
  { immediate: true }
)

watch(
  [requisitos, regrasProtocolo, formulario],
  () => {
    if (modoEdicao.value && baselineCarregado.value) {
      alteracoesLocais.value = true
    }
  },
  { deep: true }
)

function abrirSandbox() {
  if (!modoEdicao.value) return
  sandboxAberto.value = true
}

function payloadForm() {
  return {
    nome: formulario.nome,
    descricao: formulario.descricao,
    icone: formulario.icone,
    sla_padrao_horas: formulario.sla_padrao_horas,
    fluxo_tramitacao: formulario.fluxo_tramitacao,
    categoria_id: formulario.categoria_id,
    unidade_responsavel_id: formulario.unidade_responsavel_id,
    ativo: formulario.ativo,
    permite_cluster: formulario.permite_cluster
  }
}

async function salvar() {
  if (!formularioValido.value) return

  try {
    await catalogoStore.criarServicoCatalogo(payloadForm(), requisitos.value, regrasProtocolo.value)
    emit('sucesso')
  } catch (err) {
    console.error('Erro ao salvar serviço:', err)
    mostrarToast(catalogoStore.erro || 'Erro ao criar serviço.', true)
  }
}

async function salvarRascunho() {
  if (!modoEdicao.value || !formularioValido.value) return
  try {
    const atualizado = await catalogoStore.atualizarServicoCatalogo(
      servicoAtual.value.id,
      payloadForm(),
      requisitos.value,
      regrasProtocolo.value,
      { salvar_como_rascunho: true }
    )
    alteracoesLocais.value = false
    baselineCarregado.value = true
    preencherFormulario(atualizado)
    emit('atualizado', atualizado)
    mostrarToast('Rascunho salvo. O PWA do cidadão segue na versão publicada.')
  } catch (err) {
    console.error(err)
    mostrarToast(catalogoStore.erro || 'Erro ao salvar rascunho.', true)
  }
}

function abrirModalPublicar() {
  notaVersao.value = ''
  modalPublicarAberto.value = true
}

async function confirmarPublicacao() {
  if (!modoEdicao.value) return
  try {
    if (alteracoesLocais.value) {
      await catalogoStore.atualizarServicoCatalogo(
        servicoAtual.value.id,
        payloadForm(),
        requisitos.value,
        regrasProtocolo.value,
        { salvar_como_rascunho: true }
      )
    }
    const publicado = await catalogoStore.publicarRascunho(servicoAtual.value.id, notaVersao.value)
    modalPublicarAberto.value = false
    alteracoesLocais.value = false
    preencherFormulario(publicado)
    emit('atualizado', publicado)
    mostrarToast(`Versão v${publicado.versao_publicada} publicada para o cidadão.`)
  } catch (err) {
    console.error(err)
    mostrarToast(catalogoStore.erro || 'Erro ao publicar.', true)
  }
}

async function executarDescartar() {
  try {
    const atualizado = await catalogoStore.descartarRascunho(servicoAtual.value.id)
    confirmarDescartar.value = false
    alteracoesLocais.value = false
    preencherFormulario(atualizado)
    emit('atualizado', atualizado)
    mostrarToast('Rascunho descartado. Formulário recarregado da versão publicada.')
  } catch (err) {
    mostrarToast(catalogoStore.erro || 'Erro ao descartar rascunho.', true)
  }
}

async function restaurarVersaoHistorico(numero) {
  restaurandoVersao.value = numero
  try {
    const atualizado = await catalogoStore.restaurarVersao(servicoAtual.value.id, numero)
    historicoAberto.value = false
    preencherFormulario(atualizado)
    emit('atualizado', atualizado)
    mostrarToast(
      `Versão v${numero} restaurada como rascunho. Teste no Sandbox antes de publicar.`
    )
  } catch (err) {
    mostrarToast(catalogoStore.erro || 'Erro ao restaurar versão.', true)
  } finally {
    restaurandoVersao.value = null
  }
}

onMounted(async () => {
  if (!unidadesAtivas.value.length) {
    await adminStore.carregarUnidades({ silencioso: true }).catch(() => {})
  }

  try {
    if (!catalogoStore.categoriasCatalogo.length) {
      await catalogoStore.carregarCategoriasCatalogo()
    }
    const ativas = catalogoStore.categoriasCatalogo.filter((c) => c.ativo)
    if (!formulario.categoria_id && ativas.length === 1) {
      formulario.categoria_id = String(ativas[0].id)
    }
  } catch (err) {
    console.error('Erro ao carregar categorias:', err)
  }

  if (!props.servico) {
    requisitos.value = []
    regrasProtocolo.value = []
  }
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 3s infinite;
}
</style>