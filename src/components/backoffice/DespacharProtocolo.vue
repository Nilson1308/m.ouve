<template>
  <!-- Overlay -->
  <Transition name="fade">
    <div
      v-if="aberto"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="fechar"
    >
      <!-- Modal -->
      <Transition name="slide-up">
        <div
          v-if="aberto"
          class="bg-white dark:bg-gray-900 rounded-modal shadow-float dark:shadow-float-dark w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
        >
          <!-- Header -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-500 to-primary-600">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <PaperAirplaneIcon class="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 class="text-2xl font-bold text-white">
                      {{ modo === 'super_os' ? 'Despachar Super OS' : 'Despachar Protocolo' }}
                    </h2>
                    <p class="text-primary-100 text-sm mt-0.5">
                      {{
                        modo === 'super_os'
                          ? 'Scatter-Gather consolidado · todas as unidades atendem o incidente em massa'
                          : 'Fragmentação Scatter-Gather · Multi-Setorial'
                      }}
                    </p>
                  </div>
                </div>
              </div>
              <button
                @click="fechar"
                class="text-white/80 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/10"
              >
                <XMarkIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Informações do Protocolo Pai -->
            <div class="card bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border-2 border-primary-200 dark:border-primary-800">
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0 w-16 h-16 rounded-xl bg-primary-500 text-white flex items-center justify-center">
                  <component :is="getIconeCategoria(protocolo.categoria)" class="w-8 h-8" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-sm font-mono font-bold text-primary-600 dark:text-primary-400">
                      {{ protocolo.numero }}
                    </span>
                    <StatusBadge :status="protocolo.status" tipo="zeladoria" :show-icon="true" />
                  </div>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {{ protocolo.servico }}
                  </h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                      <MapPinIcon class="w-4 h-4 text-gray-400" />
                      <span>{{ protocolo.endereco }}, {{ protocolo.bairro }}</span>
                    </div>
                    <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                      <UserIcon class="w-4 h-4 text-gray-400" />
                      <span>{{ protocolo.cidadao.nome }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Explicação do Scatter-Gather -->
            <div class="alert-info">
              <InformationCircleIcon class="w-5 h-5 flex-shrink-0" />
              <div>
                <strong class="font-semibold">💡 Despacho Inteligente Multi-Setorial</strong>
                <p class="text-sm mt-1">
                  Este protocolo pode ser fragmentado e despachado para múltiplas secretarias/departamentos. 
                  Cada unidade receberá uma <strong>Ordem de Serviço específica</strong> com instruções personalizadas e prazos independentes.
                </p>
              </div>
            </div>

            <!-- Lista de Ordens de Serviço -->
            <div>
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <BuildingOfficeIcon class="w-5 h-5 text-primary-500" />
                  Ordens de Serviço
                </h3>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ ordensServico.length }} {{ ordensServico.length === 1 ? 'unidade' : 'unidades' }}
                </span>
              </div>

              <!-- Ordens criadas -->
              <div class="space-y-4">
                <TransitionGroup name="list">
                  <div
                    v-for="(ordem, index) in ordensServico"
                    :key="ordem.id"
                    class="card-ordem border-l-4 border-primary-500"
                  >
                    <div class="flex items-start gap-4">
                      <!-- Número da Ordem -->
                      <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 font-bold text-lg flex items-center justify-center">
                        {{ index + 1 }}
                      </div>

                      <!-- Conteúdo -->
                      <div class="flex-1 space-y-4">
                        <!-- Seleção de Unidade/Secretaria -->
                        <div>
                          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Unidade / Secretaria Responsável
                          </label>
                          <select
                            v-model="ordem.unidadeId"
                            class="input-select"
                            required
                          >
                            <option value="">
                              {{ loadingUnidades ? 'Carregando unidades...' : 'Selecione a unidade...' }}
                            </option>
                            <option
                              v-for="unidade in unidadesDisponiveis"
                              :key="unidade.id"
                              :value="unidade.id"
                              :disabled="unidadeJaSelecionada(unidade.id, ordem.id)"
                            >
                              {{ unidade.nome }}
                            </option>
                          </select>
                        </div>

                        <!-- Instrução Específica -->
                        <div>
                          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Instrução / Despacho Específico
                          </label>
                          <textarea
                            v-model="ordem.instrucao"
                            rows="3"
                            class="input-textarea"
                            placeholder="Ex: Realizar vistoria técnica no local e providenciar reparo emergencial da via..."
                            required
                          ></textarea>
                          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Seja específico sobre o que esta unidade deve realizar
                          </p>
                        </div>

                        <!-- Prazo (horas — contrato API) -->
                        <div>
                          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Prazo (horas)
                          </label>
                          <input
                            v-model.number="ordem.prazo_horas"
                            type="number"
                            min="1"
                            max="8760"
                            class="input-field"
                            placeholder="Ex.: 48"
                            required
                          />
                          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Prazo operacional desta unidade, em horas.
                          </p>
                        </div>
                      </div>

                      <!-- Botão Remover -->
                      <button
                        v-if="ordensServico.length > 1"
                        @click="removerOrdem(index)"
                        class="flex-shrink-0 p-2 text-danger-500 hover:text-danger-700 hover:bg-danger-50 dark:hover:bg-danger-900/20 rounded-lg transition-colors"
                        title="Remover ordem"
                      >
                        <TrashIcon class="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </TransitionGroup>
              </div>

              <!-- Botão Adicionar Ordem -->
              <button
                @click="adicionarOrdem"
                class="w-full mt-4 btn-secondary flex items-center justify-center gap-2"
              >
                <PlusCircleIcon class="w-5 h-5" />
                Adicionar Unidade / Secretaria
              </button>
            </div>

            <!-- Observações Gerais (Opcional) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Observações Gerais (Opcional)
              </label>
              <textarea
                v-model="observacoesGerais"
                rows="2"
                class="input-textarea"
                placeholder="Observações que serão compartilhadas com todas as unidades..."
              ></textarea>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <div class="flex items-center justify-between gap-4">
              <button
                @click="fechar"
                class="btn-secondary"
              >
                Cancelar
              </button>
              <button
                @click="confirmar"
                :disabled="!formularioValido || salvando"
                class="btn-primary flex items-center gap-2"
                :class="{ 'opacity-50 cursor-not-allowed': !formularioValido || salvando }"
              >
                <PaperAirplaneIcon class="w-5 h-5" />
                Despachar {{ ordensServico.length }} {{ ordensServico.length === 1 ? 'Ordem de Serviço' : 'Ordens de Serviço' }}
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
import { useBackofficeStore } from '@/stores/backoffice'
import { storeToRefs } from 'pinia'
import {
  XMarkIcon,
  PaperAirplaneIcon,
  MapPinIcon,
  UserIcon,
  InformationCircleIcon,
  BuildingOfficeIcon,
  PlusCircleIcon,
  TrashIcon,
  WrenchScrewdriverIcon,
  LightBulbIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const props = defineProps({
  protocolo: {
    type: Object,
    required: true
  },
  aberto: {
    type: Boolean,
    default: false
  },
  salvando: {
    type: Boolean,
    default: false
  },
  modo: {
    type: String,
    default: 'protocolo'
  },
  /** Ordens sugeridas pela triagem (pré-preenchimento — confirmação manual). */
  prefillOrdens: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['fechar', 'confirmar'])

const backofficeStore = useBackofficeStore()
const { unidades, loadingUnidades } = storeToRefs(backofficeStore)
const unidadesDisponiveis = unidades

const ordensServico = ref([])
const observacoesGerais = ref('')
let proximoId = 1

const formularioValido = computed(() => {
  if (ordensServico.value.length === 0) return false

  return ordensServico.value.every(
    (ordem) =>
      ordem.unidadeId &&
      ordem.instrucao.trim() &&
      Number(ordem.prazo_horas) >= 1
  )
})

// Métodos
function adicionarOrdem() {
  ordensServico.value.push({
    id: proximoId++,
    unidadeId: '',
    instrucao: '',
    prazo_horas: 48
  })
}

function removerOrdem(index) {
  ordensServico.value.splice(index, 1)
}

function unidadeJaSelecionada(unidadeId, ordemIdAtual) {
  return ordensServico.value.some(ordem => 
    ordem.id !== ordemIdAtual && ordem.unidadeId === unidadeId
  )
}

function fechar() {
  emit('fechar')
}

function confirmar() {
  if (!formularioValido.value || props.salvando) return

  emit('confirmar', {
    ordens: ordensServico.value.map((ordem) => ({
      unidade_id: ordem.unidadeId,
      instrucao: ordem.instrucao.trim(),
      prazo_horas: Number(ordem.prazo_horas)
    })),
    observacao_geral: observacoesGerais.value.trim()
  })
}

function getIconeCategoria(categoria) {
  const icones = {
    via_publica: WrenchScrewdriverIcon,
    iluminacao: LightBulbIcon,
    limpeza: SparklesIcon,
    arborizacao: SparklesIcon,
    calcada: WrenchScrewdriverIcon,
    sinalizacao: SparklesIcon
  }
  return icones[categoria] || WrenchScrewdriverIcon
}

function montarOrdensIniciais() {
  const prazoPadrao = props.protocolo?.sla?.slaHoras || 48
  if (props.prefillOrdens?.length) {
    ordensServico.value = props.prefillOrdens.map((ordem) => ({
      id: proximoId++,
      unidadeId: String(ordem.unidadeId || ordem.unidade_id || ''),
      instrucao: ordem.instrucao || '',
      prazo_horas: Number(ordem.prazo_horas) > 0 ? Number(ordem.prazo_horas) : prazoPadrao
    }))
    return
  }
  ordensServico.value = [
    {
      id: proximoId++,
      unidadeId: '',
      instrucao: '',
      prazo_horas: prazoPadrao
    }
  ]
}

// Inicializar quando o modal abre (com ou sem triagem)
watch(
  () => props.aberto,
  async (novoValor) => {
    if (novoValor) {
      montarOrdensIniciais()
      observacoesGerais.value = ''
      try {
        await backofficeStore.carregarUnidades()
      } catch {
        /* erro tratado na view */
      }
    }
  }
)

watch(
  () => props.prefillOrdens,
  () => {
    if (props.aberto) montarOrdensIniciais()
  },
  { deep: true }
)
</script>

<style scoped>
/* Transições */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Transição de lista */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Card de ordem */
.card-ordem {
  @apply card p-5 bg-white dark:bg-gray-800 transition-all duration-200;
  @apply hover:shadow-card-hover;
}

/* Inputs */
.input-field,
.input-select,
.input-textarea {
  @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-input;
  @apply bg-white dark:bg-gray-700 text-gray-900 dark:text-white;
  @apply placeholder-gray-500 dark:placeholder-gray-400;
  @apply focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  @apply transition-all duration-200;
}

.input-textarea {
  @apply resize-none;
}

.input-select {
  @apply cursor-pointer;
}

.input-select option:disabled {
  @apply text-gray-400;
}
</style>
