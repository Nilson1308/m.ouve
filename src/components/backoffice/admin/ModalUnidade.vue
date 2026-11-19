<template>
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
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="$emit('fechar')"
    >
      <!-- Modal -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden max-h-[92vh] flex flex-col"
        >
          <!-- Header -->
          <div
            class="shrink-0 px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-primary-100 dark:bg-primary-900/40 rounded-lg">
                  <BuildingOfficeIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                    {{ unidade ? 'Editar Unidade' : 'Nova Unidade Administrativa' }}
                  </h2>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    {{
                      unidade
                        ? 'Altere os dados da secretaria ou órgão'
                        : 'Cadastre uma nova secretaria ou órgão executivo'
                    }}
                  </p>
                </div>
              </div>

              <button
                type="button"
                class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                @click="$emit('fechar')"
              >
                <XMarkIcon class="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          </div>

          <!-- Formulário -->
          <form class="flex-1 overflow-y-auto p-6 space-y-6" @submit.prevent="salvar">
            <!-- Nome -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Nome da Unidade *
              </label>
              <input
                v-model="formulario.nome"
                type="text"
                placeholder="Ex: Secretaria Municipal de Infraestrutura e Obras"
                required
                class="input"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Nome completo oficial da secretaria ou órgão
              </p>
            </div>

            <!-- Sigla -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Sigla *
              </label>
              <input
                v-model="formulario.sigla"
                type="text"
                placeholder="Ex: SINFRA-OBRAS"
                required
                maxlength="20"
                class="input font-mono"
                @input="formulario.sigla = formulario.sigla.toUpperCase()"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Abreviação para identificação rápida (máx. 20 caracteres)
              </p>
            </div>

            <!-- Descrição -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Descrição
              </label>
              <textarea
                v-model="formulario.descricao"
                rows="3"
                placeholder="Breve descrição das atribuições e responsabilidades..."
                class="input resize-none"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Ajuda os usuários a entender o escopo de atuação
              </p>
            </div>

            <!-- Tom da IA -->
            <section
              class="pt-2 border-t border-gray-200 dark:border-gray-700 space-y-4"
              aria-labelledby="tom-ia-titulo"
            >
              <div class="flex items-start gap-2">
                <SparklesIcon class="w-5 h-5 text-primary-600 dark:text-primary-400 shrink-0 mt-0.5" />
                <div>
                  <h3
                    id="tom-ia-titulo"
                    class="text-sm font-bold text-gray-900 dark:text-white"
                  >
                    Personalidade da IA (Tom de Voz)
                  </h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    Define como o assistente virtual fala nos serviços vinculados a esta secretaria.
                  </p>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  v-for="opcao in TOM_IA_OPCOES"
                  :key="opcao.value"
                  type="button"
                  class="group relative text-left p-4 rounded-xl border-2 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-gray-800"
                  :class="
                    formulario.tom_ia === opcao.value
                      ? 'border-primary-500 bg-primary-50/80 dark:bg-primary-900/25 shadow-md shadow-primary-500/10'
                      : 'border-gray-200 dark:border-gray-600 bg-gray-50/50 dark:bg-gray-700/30 hover:border-gray-300 dark:hover:border-gray-500 hover:bg-white dark:hover:bg-gray-700/50'
                  "
                  @click="formulario.tom_ia = opcao.value"
                >
                  <div class="flex items-start gap-3">
                    <div
                      class="p-2 rounded-lg shrink-0 transition-colors"
                      :class="
                        formulario.tom_ia === opcao.value
                          ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300'
                          : 'bg-gray-100 dark:bg-gray-600/50 text-gray-600 dark:text-gray-300 group-hover:bg-gray-200 dark:group-hover:bg-gray-600'
                      "
                    >
                      <component :is="iconesTom[opcao.icon]" class="w-5 h-5" />
                    </div>
                    <div class="min-w-0 flex-1">
                      <p class="text-sm font-bold text-gray-900 dark:text-white">
                        {{ opcao.titulo }}
                      </p>
                      <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5 leading-snug">
                        {{ opcao.subtitulo }}
                      </p>
                      <p class="text-[11px] text-gray-500 dark:text-gray-500 mt-1.5">
                        {{ opcao.hint }}
                      </p>
                    </div>
                    <CheckCircleIcon
                      v-if="formulario.tom_ia === opcao.value"
                      class="w-5 h-5 text-primary-600 dark:text-primary-400 shrink-0"
                    />
                  </div>
                </button>
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Diretrizes específicas (opcional)
                </label>
                <textarea
                  v-model="formulario.diretrizes_tom_ia"
                  rows="3"
                  :maxlength="DIRETRIZES_TOM_MAX"
                  placeholder="Ex: Use linguagem simples, sem termos jurídicos; demonstre empatia com tutores de animais."
                  class="input resize-none"
                  :class="{
                    'border-red-400 dark:border-red-500 focus:ring-red-500': diretrizesInvalidas
                  }"
                />
                <div class="flex items-center justify-between mt-1.5">
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Refinam vocabulário e estilo além do tom escolhido.
                  </p>
                  <span
                    class="text-xs font-mono tabular-nums"
                    :class="
                      diretrizesInvalidas
                        ? 'text-red-600 dark:text-red-400 font-semibold'
                        : 'text-gray-500 dark:text-gray-400'
                    "
                  >
                    {{ diretrizesLength }} / {{ DIRETRIZES_TOM_MAX }}
                  </span>
                </div>
                <p
                  v-if="diretrizesInvalidas"
                  class="text-xs text-red-600 dark:text-red-400 mt-1"
                >
                  Reduza o texto para no máximo {{ DIRETRIZES_TOM_MAX }} caracteres.
                </p>
              </div>

              <!-- Prévia -->
              <div
                class="p-4 rounded-xl bg-gray-50 dark:bg-gray-900/40 border border-gray-200 dark:border-gray-600/80"
              >
                <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
                  Como a IA vai falar
                </p>
                <Transition
                  mode="out-in"
                  enter-active-class="transition-all duration-200 ease-out"
                  enter-from-class="opacity-0 translate-y-1"
                  enter-to-class="opacity-100 translate-y-0"
                  leave-active-class="transition-all duration-150 ease-in"
                  leave-from-class="opacity-100"
                  leave-to-class="opacity-0"
                >
                  <div
                    :key="formulario.tom_ia"
                    class="flex gap-3 items-start"
                  >
                    <div
                      class="shrink-0 w-9 h-9 rounded-full bg-primary-600 flex items-center justify-center shadow-sm"
                    >
                      <ChatBubbleLeftRightIcon class="w-5 h-5 text-white" />
                    </div>
                    <div
                      class="flex-1 px-4 py-3 rounded-2xl rounded-tl-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-sm text-gray-800 dark:text-gray-200 leading-relaxed shadow-sm"
                    >
                      {{ textoPrevia }}
                    </div>
                  </div>
                </Transition>
              </div>
            </section>

            <!-- Status Ativo/Inativo -->
            <div
              class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <input
                id="unidade-ativa"
                v-model="formulario.ativo"
                type="checkbox"
                class="mt-0.5 w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <div class="flex-1">
                <label
                  for="unidade-ativa"
                  class="block text-sm font-semibold text-gray-900 dark:text-white cursor-pointer"
                >
                  Unidade Ativa
                </label>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Unidades inativas não aparecem nos filtros e não podem receber novos protocolos
                </p>
              </div>
            </div>

            <!-- Informações Adicionais (Se estiver editando) -->
            <div
              v-if="unidade"
              class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
            >
              <div class="flex items-start gap-3">
                <InformationCircleIcon class="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                <div class="text-sm text-blue-800 dark:text-blue-200">
                  <p class="font-semibold mb-1">Informações da Unidade</p>
                  <ul class="space-y-1 text-xs">
                    <li>
                      <strong>Usuários vinculados:</strong> {{ unidade.usuarios_count }}
                    </li>
                    <li>
                      <strong>Criado em:</strong> {{ formatarData(unidade.criado_em) }}
                    </li>
                    <li v-if="unidade.atualizado_em !== unidade.criado_em">
                      <strong>Última atualização:</strong> {{ formatarData(unidade.atualizado_em) }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </form>

          <!-- Footer -->
          <div
            class="shrink-0 px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex items-center justify-between"
          >
            <p class="text-xs text-gray-500 dark:text-gray-400">* Campos obrigatórios</p>

            <div class="flex items-center gap-3">
              <button
                type="button"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
                @click="$emit('fechar')"
              >
                Cancelar
              </button>
              <button
                type="button"
                :disabled="!formularioValido || salvando"
                class="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                @click="salvar"
              >
                <div
                  v-if="salvando"
                  class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                />
                <CheckIcon v-else class="w-5 h-5" />
                {{ salvando ? 'Salvando...' : unidade ? 'Salvar Alterações' : 'Criar Unidade' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  BuildingOfficeIcon,
  BuildingLibraryIcon,
  HeartIcon,
  BoltIcon,
  ClipboardDocumentListIcon,
  XMarkIcon,
  CheckIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/vue/24/outline'
import {
  TOM_IA_OPCOES,
  TOM_IA_DEFAULT,
  TOM_IA_PREVIA,
  DIRETRIZES_TOM_MAX,
  normalizeTomIa
} from '@/utils/tomIaUnidade'

const props = defineProps({
  unidade: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['fechar', 'salvar'])

const iconesTom = {
  BuildingLibraryIcon,
  HeartIcon,
  BoltIcon,
  ClipboardDocumentListIcon
}

const formularioVazio = () => ({
  nome: '',
  sigla: '',
  descricao: '',
  tom_ia: TOM_IA_DEFAULT,
  diretrizes_tom_ia: '',
  ativo: true
})

const formulario = ref(formularioVazio())
const salvando = ref(false)

watch(
  () => props.unidade,
  (unidade) => {
    if (unidade) {
      formulario.value = {
        nome: unidade.nome || '',
        sigla: unidade.sigla || '',
        descricao: unidade.descricao || '',
        tom_ia: normalizeTomIa(unidade.tom_ia),
        diretrizes_tom_ia: unidade.diretrizes_tom_ia || '',
        ativo: unidade.ativo !== false
      }
    } else {
      formulario.value = formularioVazio()
    }
  },
  { immediate: true }
)

const diretrizesLength = computed(() => (formulario.value.diretrizes_tom_ia || '').length)

const diretrizesInvalidas = computed(() => diretrizesLength.value > DIRETRIZES_TOM_MAX)

const textoPrevia = computed(() => {
  const base = TOM_IA_PREVIA[formulario.value.tom_ia] || TOM_IA_PREVIA.institucional
  const extra = (formulario.value.diretrizes_tom_ia || '').trim()
  if (!extra || diretrizesInvalidas.value) return base
  return `${base} (${extra})`
})

const formularioValido = computed(() => {
  return (
    formulario.value.nome.trim().length >= 3 &&
    formulario.value.sigla.trim().length >= 2 &&
    !diretrizesInvalidas.value
  )
})

async function salvar() {
  if (!formularioValido.value) return

  salvando.value = true

  try {
    emit('salvar', {
      ...formulario.value,
      tom_ia: normalizeTomIa(formulario.value.tom_ia),
      diretrizes_tom_ia: (formulario.value.diretrizes_tom_ia || '').trim()
    })
  } finally {
    salvando.value = false
  }
}

function formatarData(data) {
  if (!data) return '-'
  const d = new Date(data)
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>