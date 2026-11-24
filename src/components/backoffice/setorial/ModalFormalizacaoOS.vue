<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="aberto"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100]"
        @click="fechar"
      ></div>
    </Transition>

    <!-- Drawer -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-300 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <div
        v-if="aberto"
        class="fixed top-0 right-0 bottom-0 w-full max-w-4xl bg-gray-50 dark:bg-gray-900 shadow-float z-[110] overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-formalizar-os-titulo"
      >
        <!-- Header Fixo -->
        <div class="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 sm:gap-3 mb-3 flex-wrap">
                <h2
                  id="modal-formalizar-os-titulo"
                  class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white shrink-0"
                >
                  {{
                    somenteLeitura
                      ? 'Detalhes da Ordem de Serviço'
                      : aguardandoAssinaturaGestor
                        ? 'Despacho aguardando gestor'
                        : 'Despacho técnico da OS'
                  }}
                </h2>
                <span
                  v-if="somenteLeitura"
                  class="inline-flex items-center gap-1.5 px-3 py-1 rounded-badge text-xs font-bold shrink-0 whitespace-nowrap bg-emerald-600 text-white shadow-button"
                >
                  <LockClosedIcon class="w-3.5 h-3.5" aria-hidden="true" />
                  Nó encerrado
                </span>
                <span
                  v-else
                  :class="[
                    'inline-flex items-center gap-1.5 px-3 py-1 rounded-badge text-xs font-semibold shrink-0 whitespace-nowrap',
                    ordem.status === 'nova'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                      : ordem.status === 'aguardando_campo'
                      ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
                      : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                  ]"
                >
                  {{ getStatusLabel(ordem.status) }}
                </span>
                <BadgeSuperOS v-if="ordem.is_super_os" :ordem="ordem" class="shrink-0" />
                <span
                  v-if="ordem.super_os_codigo"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-badge text-xs font-semibold font-mono whitespace-nowrap shrink-0 bg-orange-50 text-orange-800 dark:bg-orange-950/40 dark:text-orange-200 border border-orange-200/70 dark:border-orange-700/50"
                  :title="`Super OS ${ordem.super_os_codigo}`"
                >
                  <HashtagIcon class="w-3.5 h-3.5 shrink-0 opacity-80" aria-hidden="true" />
                  {{ ordem.super_os_codigo }}
                </span>
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold font-mono whitespace-nowrap shrink-0 bg-primary-100 text-primary-800 dark:bg-primary-900/40 dark:text-primary-300 border border-primary-200/80 dark:border-primary-700"
                  :title="`Protocolo ${protocoloRef}`"
                >
                  <HashtagIcon class="w-3.5 h-3.5 shrink-0 opacity-80" aria-hidden="true" />
                  {{ protocoloRef }}
                </span>
              </div>

              <div class="flex flex-wrap items-center gap-x-3 gap-y-1 min-w-0 text-sm text-gray-600 dark:text-gray-400">
                <div class="flex items-center gap-2 min-w-0">
                  <MapPinIcon class="w-4 h-4 shrink-0 text-gray-500 dark:text-gray-400" aria-hidden="true" />
                  <span class="truncate" :title="ordem.endereco">{{ ordem.endereco || '—' }}</span>
                </div>
                <span
                  v-if="ordem.is_super_os"
                  class="text-xs text-orange-700/90 dark:text-orange-300/90 font-medium"
                >
                  + pontos próximos na região
                </span>
              </div>
            </div>

            <button
              type="button"
              @click="fechar"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors shrink-0"
              aria-label="Fechar"
            >
              <XMarkIcon class="w-6 h-6 text-gray-500" />
            </button>
          </div>

          <!-- Info Rápida -->
          <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Serviço</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ ordem.servico }}</p>
              <p
                v-if="ordem.is_super_os"
                class="text-xs text-orange-700 dark:text-orange-300 mt-1 font-medium"
              >
                {{ ordem.qtd_chamados_vinculados }} protocolos no incidente
              </p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Prioridade</p>
              <span
                :class="[
                  'inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-xs font-semibold',
                  ordem.prioridade === 'urgente'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                    : ordem.prioridade === 'alta'
                    ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                ]"
              >
                {{ ordem.prioridade === 'urgente' ? 'Urgente' : ordem.prioridade === 'alta' ? 'Alta' : 'Normal' }}
              </span>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Prazo / SLA</p>
              <p
                class="text-sm font-semibold"
                :class="[
                  ordem.sla_status === 'vencido'
                    ? 'text-red-600 dark:text-red-400'
                    : ordem.sla_status === 'atencao'
                    ? 'text-amber-600 dark:text-amber-400'
                    : 'text-green-600 dark:text-green-400'
                ]"
              >
                {{ formatarData(ordem.prazo_interno) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Conteúdo -->
        <div class="px-6 py-6 space-y-6">
          <!-- Instrução da Ouvidoria -->
          <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-card p-4">
            <div class="flex items-start gap-3">
              <div class="p-2 bg-purple-100 dark:bg-purple-900/40 rounded-lg">
                <ChatBubbleLeftRightIcon class="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div class="flex-1">
                <h3 class="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-2">
                  Instrução da Ouvidoria Central
                </h3>
                <p class="text-sm text-purple-800 dark:text-purple-200 whitespace-pre-wrap">
                  {{ ordem.instrucao_ouvidoria || '—' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Seção: Equipe de Rua e Evidências -->
          <div class="bg-white dark:bg-gray-800 rounded-card shadow-card p-6">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1 flex items-center gap-2">
              <TruckIcon class="w-6 h-6 text-primary-500" />
              Equipe de Rua e Evidências
              <span class="text-xs font-normal text-gray-500 dark:text-gray-400">(opcional)</span>
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Use quando houver execução em campo ou documentos complementares. Despachos de impossibilidade técnica podem seguir sem anexos.
            </p>

            <MagicLinkPanel
              v-if="!somenteLeitura"
              :ordem="ordem"
              :gerando="gerandoLink"
              @gerar-link="$emit('gerar-link')"
            />

            <!-- Relato / descrição enviada pela equipe de campo -->
            <div
              v-if="relatoCampo"
              class="mt-6 rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50/80 dark:bg-amber-900/20 p-4"
            >
              <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-2">
                <h4 class="text-sm font-semibold text-amber-900 dark:text-amber-100">
                  Descrição das evidências (equipe de campo)
                </h4>
                <div class="flex flex-wrap gap-2">
                  <button type="button" class="btn-secondary text-xs py-1.5" @click="copiarRelato">
                    Copiar
                  </button>
                  <button
                    type="button"
                    class="btn-secondary text-xs py-1.5"
                    @click="inserirRelatoNaDescricao"
                  >
                    Inserir na descrição técnica
                  </button>
                </div>
              </div>
              <p class="text-sm text-amber-950 dark:text-amber-100 whitespace-pre-wrap leading-relaxed">
                {{ relatoCampo }}
              </p>
              <p class="text-xs text-amber-800/80 dark:text-amber-200/70 mt-2">
                Use o relato acima para compor a descrição técnica do despacho, se fizer sentido.
              </p>
            </div>

            <div class="mt-6">
              <GaleriaEvidencias
                :evidencias="ordem.evidencias"
                :enviando="enviandoEvidencias"
                :somente-leitura="somenteLeitura"
                @enviar-arquivos="onEnviarEvidencias"
              />
            </div>
          </div>

          <!-- Seção: Formalização e Despacho Administrativo -->
          <div class="bg-white dark:bg-gray-800 rounded-card shadow-card p-6">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <DocumentTextIcon class="w-6 h-6 text-primary-500" />
              Formalização e Despacho Administrativo
            </h3>

            <div
              v-if="somenteLeitura"
              class="mb-6 rounded-card border-2 border-emerald-200 dark:border-emerald-800 bg-emerald-50/80 dark:bg-emerald-900/20 p-5"
            >
              <div class="flex items-center gap-2 mb-3 text-emerald-800 dark:text-emerald-200">
                <LockClosedIcon class="w-5 h-5 shrink-0" />
                <h4 class="text-sm font-bold">Descrição técnica assinada</h4>
              </div>
              <p class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap leading-relaxed">
                {{ textoDespachoEncerrado || '—' }}
              </p>
              <div
                v-if="ordem.assinatura_digital_hash"
                class="mt-4 p-3 rounded-lg bg-white/80 dark:bg-gray-900/50 border border-emerald-200 dark:border-emerald-700"
              >
                <p class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                  Hash da assinatura digital (SHA-256)
                </p>
                <p class="text-xs font-mono break-all text-gray-800 dark:text-gray-200">
                  {{ ordem.assinatura_digital_hash }}
                </p>
                <p v-if="ordem.data_formalizacao || ordem.assinado_em" class="text-[10px] text-gray-500 mt-2">
                  Formalizado em {{ formatarData(ordem.data_formalizacao || ordem.assinado_em) }}
                  <span v-if="ordem.assinado_por"> · {{ ordem.assinado_por }}</span>
                </p>
              </div>
            </div>

            <div
              v-else-if="aguardandoAssinaturaGestor"
              class="mb-6 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50 p-4"
            >
              <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">
                Descrição técnica enviada
              </p>
              <p class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                {{ textoDespachoEncerrado || '—' }}
              </p>
            </div>

            <div v-else class="mb-6">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Descrição técnica do despacho *
              </label>
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
                Texto oficial que entra na assinatura digital. Descreva a execução, a impossibilidade técnica ou o encerramento da ordem.
              </p>

              <div
                v-if="opcoesTextoInserir.length"
                class="flex flex-col sm:flex-row gap-2 mb-3"
              >
                <select
                  v-model="textoPadraoSelecionado"
                  class="input text-sm flex-1"
                  :disabled="carregandoTextos"
                >
                  <option value="">
                    {{ carregandoTextos ? 'Carregando textos da secretaria…' : 'Inserir texto padrão (opcional)…' }}
                  </option>
                  <option
                    v-for="item in opcoesTextoInserir"
                    :key="item.id"
                    :value="item.id"
                  >
                    {{ item.titulo }}
                  </option>
                </select>
                <button
                  type="button"
                  class="btn-secondary text-sm shrink-0"
                  :disabled="!textoPadraoSelecionado"
                  @click="aplicarTextoPadrao"
                >
                  Inserir no texto
                </button>
              </div>

              <Editor
                v-model="formulario.descricaoTecnica"
                placeholder="Descreva o que foi feito, o motivo técnico da não execução, materiais, normas aplicáveis, etc."
              />

              <div v-if="erroTextosPadrao" class="mt-3 alert-danger text-sm">
                {{ erroTextosPadrao }}
                <RouterLink
                  to="/backoffice/configuracoes?aba=textos"
                  class="block mt-2 font-semibold text-primary-600 dark:text-primary-400 hover:underline"
                  @click="fechar"
                >
                  Cadastrar textos padrão da secretaria →
                </RouterLink>
              </div>
              <p
                v-else-if="(textosPadrao || []).length"
                class="text-xs text-gray-500 dark:text-gray-400 mt-2"
              >
                {{ opcoesTextoInserir.length }} texto(s) padrão da unidade.
                <RouterLink
                  to="/backoffice/configuracoes?aba=textos"
                  class="ml-1 text-primary-600 dark:text-primary-400 font-medium hover:underline"
                  @click="fechar"
                >
                  Gerenciar
                </RouterLink>
              </p>
            </div>

            <p
              v-if="!somenteLeitura && !aguardandoAssinaturaGestor"
              class="text-sm text-gray-600 dark:text-gray-400 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/60 px-4 py-3"
            >
              Após o envio, o gestor da secretaria recebe o despacho na Mesa de Trabalho para assinatura digital e encerramento do nó.
            </p>

            <div
              v-else-if="aguardandoAssinaturaGestor"
              class="rounded-lg border border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/20 px-4 py-3 text-sm text-indigo-900 dark:text-indigo-100"
            >
              Despacho aguardando assinatura do gestor. A edição ficará disponível após aprovação ou rejeição.
            </div>
          </div>
        </div>

        <!-- Footer Fixo -->
        <div
          class="sticky bottom-0 z-10 bg-white/95 dark:bg-gray-800/95 backdrop-blur border-t border-gray-200 dark:border-gray-700 px-6 py-4 shadow-[0_-8px_24px_rgba(15,23,42,0.06)]"
        >
          <div v-if="somenteLeitura" class="flex justify-end">
            <button type="button" class="btn-primary" @click="fechar">
              Fechar documento
            </button>
          </div>
          <div
            v-else-if="aguardandoAssinaturaGestor"
            class="flex justify-end gap-3"
          >
            <button type="button" class="btn-secondary" @click="fechar">
              Fechar
            </button>
          </div>
          <div v-else class="space-y-3">
            <div
              v-if="textoGovernancaEnvio"
              class="rounded-lg border px-4 py-3 text-sm leading-relaxed"
              :class="
                encerramentoDiretoSecretaria
                  ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-100'
                  : 'bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300'
              "
            >
              {{ textoGovernancaEnvio }}
            </div>
            <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <label class="flex items-start gap-3 cursor-pointer min-w-0 flex-1">
                <input
                  v-model="formulario.assinado"
                  type="checkbox"
                  class="mt-0.5 w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500 shrink-0"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300 leading-snug">
                  Declaro ciência de que a descrição técnica é fidedigna. O gestor da secretaria assinará digitalmente este despacho (Lei 14.063/2020).
                </span>
              </label>

              <div class="flex flex-shrink-0 items-center gap-3 justify-end">
                <button type="button" class="btn-secondary" @click="fechar">
                  Cancelar
                </button>
                <button
                  type="button"
                  class="btn-primary inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!podeEnviarGestor || enviando"
                  @click="enviarParaGestor"
                >
                  <PaperAirplaneIcon class="w-5 h-5" aria-hidden="true" />
                  {{ enviando ? 'Enviando…' : 'Enviar ao gestor' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import {
  XMarkIcon,
  MapPinIcon,
  ChatBubbleLeftRightIcon,
  TruckIcon,
  DocumentTextIcon,
  HashtagIcon,
  LockClosedIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'

import MagicLinkPanel from './MagicLinkPanel.vue'
import GaleriaEvidencias from './GaleriaEvidencias.vue'
import BadgeSuperOS from './BadgeSuperOS.vue'
import Editor from '@/components/shared/Editor.vue'

const props = defineProps({
  ordem: {
    type: Object,
    required: true
  },
  aberto: {
    type: Boolean,
    required: true
  },
  gerandoLink: {
    type: Boolean,
    default: false
  },
  enviando: {
    type: Boolean,
    default: false
  },
  textosPadrao: {
    type: Array,
    default: () => []
  },
  carregandoTextos: {
    type: Boolean,
    default: false
  },
  solicitandoAssinatura: {
    type: Boolean,
    default: false
  },
  enviandoEvidencias: {
    type: Boolean,
    default: false
  },
  textosPadraoTentouCarregar: {
    type: Boolean,
    default: false
  },
  erroTextosPadrao: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'fechar',
  'enviar-gestor',
  'gerar-link',
  'toast',
  'enviar-evidencias'
])

const textoPadraoSelecionado = ref('')

const formulario = ref({
  descricaoTecnica: '',
  assinado: false
})

const protocoloRef = computed(() => {
  const o = props.ordem
  if (o?.protocolo_codigo) return o.protocolo_codigo
  const raw = (o?.protocolo_id || '').trim()
  if (!raw) return '—'
  const idx = raw.indexOf('· ref.')
  if (idx >= 0) return raw.slice(idx + 7).trim()
  return raw.replace(/\s+/g, '')
})

const somenteLeitura = computed(
  () =>
    props.ordem?.status === 'concluida' ||
    props.ordem?.status_api === 'concluida'
)

const descricaoPreenchida = computed(() =>
  Boolean(formulario.value.descricaoTecnica?.trim())
)

const aguardandoAssinaturaGestor = computed(() => {
  const api = props.ordem?.status_api
  const ui = props.ordem?.status
  return (
    api === 'aguardando_assinatura' ||
    ui === 'aguardando_assinatura' ||
  // legado: antes do mapeamento dedicado na API
    (ui === 'em_execucao' && api === 'aguardando_assinatura')
  )
})

const podeEnviarGestor = computed(
  () => descricaoPreenchida.value && formulario.value.assinado
)

const encerramentoDiretoSecretaria = computed(() =>
  Boolean(props.ordem?.encerramento_direto_secretaria)
)

const textoGovernancaEnvio = computed(() => {
  if (encerramentoDiretoSecretaria.value) {
    return 'Fluxo direto autônomo: após a assinatura do gestor, a resposta segue imediatamente ao cidadão e o protocolo é encerrado.'
  }
  if (props.ordem?.exigir_validacao_ouvidoria) {
    return 'A resposta será enviada para revisão/consolidação da Ouvidoria antes de notificar o cidadão.'
  }
  return ''
})

const relatoCampo = computed(() => (props.ordem.observacoes_execucao || '').trim())

/** Registros antigos podem ter texto só em observacoes_extras. */
const textoDespachoEncerrado = computed(() => {
  const partes = [
    props.ordem.despacho_tecnico,
    formulario.value.descricaoTecnica,
    props.ordem.observacoes_extras,
    props.ordem.observacoes_complementares
  ]
    .map((t) => (t || '').trim())
    .filter(Boolean)
  return [...new Set(partes)].join('\n\n')
})

const opcoesTextoInserir = computed(() => {
  const api = props.textosPadrao || []
  return api
    .filter((t) => t.ativo !== false)
    .map((t) => ({
      id: t.id,
      titulo: t.titulo,
      texto: t.texto
    }))
})

function aplicarTextoPadrao() {
  const id = textoPadraoSelecionado.value
  if (!id) return
  const item = opcoesTextoInserir.value.find((t) => t.id === id)
  if (!item?.texto) return
  const atual = formulario.value.descricaoTecnica.trim()
  formulario.value.descricaoTecnica = atual
    ? `${atual}\n\n${item.texto}`
    : item.texto
  textoPadraoSelecionado.value = ''
  emit('toast', 'Texto padrão inserido na descrição.')
}

function onEnviarEvidencias(arquivos) {
  emit('enviar-evidencias', arquivos)
}

function fechar() {
  emit('fechar')
}

function enviarParaGestor() {
  if (!podeEnviarGestor.value) return
  emit('enviar-gestor', {
    ordemId: props.ordem.id,
    despacho: formulario.value.descricaoTecnica
  })
}

async function copiarRelato() {
  if (!relatoCampo.value) return
  try {
    await navigator.clipboard.writeText(relatoCampo.value)
    emit('toast', 'Relato da equipe copiado.')
  } catch {
    emit('toast', 'Não foi possível copiar o texto.')
  }
}

function inserirRelatoNaDescricao() {
  if (!relatoCampo.value) return
  const atual = formulario.value.descricaoTecnica.trim()
  formulario.value.descricaoTecnica = atual
    ? `${atual}\n\n${relatoCampo.value}`
    : relatoCampo.value
}

function getStatusLabel(status) {
  const labels = {
    nova: 'Nova',
    aguardando_campo: 'Aguardando Campo',
    em_execucao: 'Em Execução',
    aguardando_assinatura: 'Aguardando gestor',
    concluida: 'Concluída',
    cancelada: 'Cancelada'
  }
  return labels[status] || status
}

function formatarData(data) {
  if (!data) return '—'
  const d = new Date(data)
  const dia = d.getDate().toString().padStart(2, '0')
  const mes = (d.getMonth() + 1).toString().padStart(2, '0')
  const ano = d.getFullYear()
  const hora = d.getHours().toString().padStart(2, '0')
  const min = d.getMinutes().toString().padStart(2, '0')
  return `${dia}/${mes}/${ano} às ${hora}:${min}`
}

watch(
  () => props.ordem,
  () => {
    const extras =
      props.ordem.observacoes_complementares || props.ordem.observacoes_extras || ''
    const despacho = (props.ordem.despacho_tecnico || '').trim()
    formulario.value = {
      descricaoTecnica: despacho
        ? extras && extras.trim() !== despacho
          ? `${despacho}\n\n${extras.trim()}`
          : despacho
        : extras.trim(),
      assinado: false
    }
    textoPadraoSelecionado.value = ''
  },
  { immediate: true }
)

watch(
  () => props.aberto,
  (aberto) => {
    document.body.style.overflow = aberto ? 'hidden' : ''
  }
)

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>
