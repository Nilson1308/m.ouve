<template>
  <div class="flex flex-col h-[calc(100dvh-5rem)] max-h-[calc(100dvh-5rem)] min-h-0 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 high-contrast:from-black high-contrast:to-black">
    <!-- Header -->
    <header class="flex-shrink-0 z-20 backdrop-blur-xl bg-white/95 dark:bg-gray-900/95 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft safe-area-inset-top">
      <div class="px-4 py-3 flex items-center gap-3">
        <!-- Botão Voltar -->
        <button type="button" @click="voltar" class="btn-icon flex-shrink-0" aria-label="Voltar para categorias">
          <ChevronLeftIcon class="w-6 h-6" aria-hidden="true" />
        </button>
        
        <!-- Avatar e Info da IA -->
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="flex-shrink-0 w-10 h-10 rounded-avatar bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 flex items-center justify-center shadow-button">
            <SparklesIcon class="w-6 h-6 text-white high-contrast:text-black" aria-hidden="true" />
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 truncate">
              {{ categoriaNome }}
            </h1>
            <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold flex items-center gap-1">
              <span v-if="!chatStore.loading" class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span v-else class="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
              {{ chatStore.loading ? 'Conectando...' : 'Assistente M.Ouve online' }}
            </p>
          </div>
        </div>

        <!-- Ações do Header -->
        <PwaA11yMenu class="flex-shrink-0" />
        <ThemeToggle surface="light" class="flex-shrink-0" />
        <button
          type="button"
          class="btn-icon flex-shrink-0"
          :aria-label="mostrarInfo ? 'Ocultar informações sobre a assistente' : 'Mostrar informações sobre a assistente'"
          :aria-expanded="mostrarInfo"
          @click="mostrarInfo = !mostrarInfo"
        >
          <InformationCircleIcon class="w-6 h-6" aria-hidden="true" />
        </button>
      </div>

      <!-- Info Card (colapsável) -->
      <transition name="slide-down">
        <div v-if="mostrarInfo" class="px-4 pb-3">
          <div class="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/10 high-contrast:bg-transparent border-blue-200 dark:border-blue-800 high-contrast:border-yellow-300 p-3">
            <p class="text-xs text-blue-800 dark:text-blue-200 high-contrast:text-white high-contrast:font-bold">
              A assistente virtual da M.Ouve vai conversar com você para entender e registrar sua solicitação de forma natural.
            </p>
          </div>
        </div>
      </transition>
    </header>

  <main id="conteudo-principal" tabindex="-1" class="flex flex-col flex-1 min-h-0">
    <!-- Área de Mensagens -->
    <div
      ref="messagesContainer"
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      aria-label="Conversa com a assistente"
      class="flex-1 min-h-0 overflow-y-auto px-4 py-6 space-y-4 scroll-smooth"
    >
      <div v-for="(mensagem, index) in chatStore.mensagens" :key="mensagem.id || index" class="animate-fade-in motion-reduce:animate-none">
        <!-- Mensagem da IA (Esquerda) -->
        <div v-if="mensagem.tipo === 'ia'" class="flex items-start gap-2 max-w-[85%]">
          <div class="flex-shrink-0 w-8 h-8 rounded-avatar bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 flex items-center justify-center">
            <SparklesIcon class="w-4 h-4 text-white high-contrast:text-black" aria-hidden="true" />
          </div>
          <div class="flex-1">
            <div class="bg-white dark:bg-gray-800 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 rounded-bubble-left px-4 py-3 shadow-soft">
              <p class="text-sm text-gray-900 dark:text-white high-contrast:text-white high-contrast:font-bold leading-relaxed whitespace-pre-wrap">
                {{ mensagem.conteudo }}
              </p>
            </div>
            <span class="text-xs text-gray-500 dark:text-gray-500 high-contrast:text-white high-contrast:font-bold ml-2 mt-1 inline-block">
              {{ mensagem.timestamp }}
            </span>

            <ChatInelegibilidadeAcoes
              v-if="deveExibirAcoesInelegibilidade(index)"
              @escolher-outro-servico="irEscolherOutroServico"
              @voltar-inicio="irInicioPwa"
            />

            <!-- Componentes de Ação baseados em tipo_acao -->
            <div v-if="mensagem.tipoAcao && !atendimentoBloqueadoInelegivel" class="mt-3 ml-10">
              <!-- Confirmação de Serviço -->
              <ChatConfirmation
                v-if="mensagem.tipoAcao === 'confirmar_servico'"
                @confirmar="handleConfirmarServico"
                :disabled="chatStore.isTyping"
              />

              <!-- Seletor de Localização Híbrido -->
              <ChatLocationPicker
                v-else-if="mensagem.tipoAcao === 'solicitar_localizacao'"
                @confirmar="handleConfirmarLocalizacao"
                @cancelar="handleCancelarLocalizacao"
              />

              <!-- Card de Revisão Final -->
              <ChatReviewCard
                v-else-if="mensagem.tipoAcao === 'revisao_final'"
                :resumo="chatStore.sessaoAtual?.resumo_revisao || {}"
                :confirmando="confirmandoProtocolo"
                @confirmar="handleConfirmarProtocolo"
                @editar="handleEditarRevisao"
              />

              <!-- Pesquisa de Satisfação -->
              <ChatSatisfacao
                v-else-if="mensagem.tipoAcao === 'pesquisa_satisfacao'"
                :enviando="enviandoSatisfacaoAbertura"
                @enviar="handleEnviarSatisfacao"
                @cancelar="handleCancelarSatisfacao"
              />

              <!-- Escolha de campo (single/multi/outro) -->
              <ChatFieldLookupUnidades
                v-else-if="mensagem.tipoAcao === 'escolha_campo' && escolhaLookupUnidadesAtiva(mensagem)"
                :config="configEscolhaMensagem(mensagem)"
                :desabilitado="chatStore.isTyping"
                @confirmar="handleEscolhaCampo"
              />

              <ChatFieldLookupEquipamentos
                v-else-if="mensagem.tipoAcao === 'escolha_campo' && escolhaLookupEquipamentosAtiva(mensagem)"
                :config="configEscolhaMensagem(mensagem)"
                :desabilitado="chatStore.isTyping"
                @confirmar="handleEscolhaCampo"
                @pular="handleEscolhaCampo"
              />

              <ChatFieldChoices
                v-else-if="mensagem.tipoAcao === 'escolha_campo' && escolhaCampoAtiva(mensagem)"
                :config="configEscolhaMensagem(mensagem)"
                :desabilitado="chatStore.isTyping"
                @confirmar="handleEscolhaCampo"
              />

              <!-- Quick Replies legado -->
              <ChatConfirmation
                v-else-if="mensagem.tipoAcao?.startsWith('quick_reply:')"
                :opcoes="parseQuickReplies(mensagem.tipoAcao)"
                @confirmar="handleQuickReply"
                :disabled="chatStore.isTyping"
              />
            </div>
          </div>
        </div>

        <!-- Mensagem do Cidadão (Direita) -->
        <div v-else-if="mensagem.tipo === 'cidadao'" class="flex items-start gap-2 justify-end">
          <div class="flex-1 flex flex-col items-end max-w-[85%]">
            <!-- Se tiver texto -->
            <div v-if="mensagem.conteudo" class="bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 rounded-bubble-right px-4 py-3 shadow-soft mb-1">
              <p class="text-sm text-white high-contrast:text-black high-contrast:font-bold leading-relaxed whitespace-pre-wrap">
                {{ mensagem.conteudo }}
              </p>
            </div>
            
            <!-- Se tiver localização -->
            <div v-if="mensagem.localizacao" class="bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 rounded-bubble-right p-3 shadow-soft mb-1">
              <div class="bg-white/20 backdrop-blur-sm rounded-card p-3 mb-2">
                <div class="flex items-center gap-2 mb-2">
                  <MapPinIcon class="w-5 h-5 text-white high-contrast:text-black" aria-hidden="true" />
                  <span class="text-xs font-bold text-white high-contrast:text-black">Localização Compartilhada</span>
                </div>
                <div class="bg-white/30 rounded-card p-2 text-center">
                  <MapIcon class="w-12 h-12 mx-auto text-white high-contrast:text-black opacity-80 mb-1" aria-hidden="true" />
                  <p class="text-xs text-white high-contrast:text-black high-contrast:font-bold">
                    Lat: {{ mensagem.localizacao.latitude.toFixed(5) }}<br>
                    Lng: {{ mensagem.localizacao.longitude.toFixed(5) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Se tiver fotos -->
            <div v-if="mensagem.fotos && mensagem.fotos.length > 0" class="bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 rounded-bubble-right p-3 shadow-soft mb-1">
              <ChatPhotoPreview
                :fotos="mensagem.fotos"
                :editavel="false"
                @visualizar="handleVisualizarFoto"
              />
            </div>
            
            <span class="text-xs text-gray-500 dark:text-gray-500 high-contrast:text-white high-contrast:font-bold mr-2 mt-1">
              {{ mensagem.timestamp }}
            </span>
          </div>
        </div>

        <!-- Mensagem de Sistema/Erro -->
        <div v-else-if="mensagem.tipo === 'sistema'" class="flex justify-center">
          <div class="card bg-red-50 dark:bg-red-900/20 high-contrast:bg-transparent border-red-200 dark:border-red-800 high-contrast:border-red-500 px-4 py-2 max-w-md">
            <div class="flex items-center gap-2">
              <ExclamationCircleIcon class="w-5 h-5 text-red-600 dark:text-red-400 high-contrast:text-red-300 flex-shrink-0" aria-hidden="true" />
              <p class="text-xs text-red-800 dark:text-red-200 high-contrast:text-white high-contrast:font-bold">
                {{ mensagem.conteudo }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Aguardando resposta da IA (in-app + Celery) -->
      <div
        v-if="aguardandoRespostaIA"
        role="status"
        aria-live="polite"
        aria-busy="true"
        class="flex items-start gap-2 max-w-[92%] pb-2 animate-fade-in motion-reduce:animate-none"
      >
        <span class="sr-only">{{ textoAguardandoIA }}</span>
        <div
          class="flex-shrink-0 w-8 h-8 rounded-avatar bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 flex items-center justify-center"
          aria-hidden="true"
        >
          <SparklesIcon class="w-4 h-4 text-white high-contrast:text-black" />
        </div>
        <div
          class="bg-white dark:bg-gray-800 high-contrast:bg-gray-900 high-contrast:border high-contrast:border-yellow-300 rounded-bubble-left px-4 py-3 shadow-soft min-w-[12rem]"
        >
          <div class="flex items-center gap-2" aria-hidden="true">
            <svg
              class="w-4 h-4 text-primary-500 dark:text-primary-400 high-contrast:text-yellow-300 animate-spin motion-reduce:animate-none shrink-0"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" />
              <path
                class="opacity-90"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v3a5 5 0 00-5 5H4z"
              />
            </svg>
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 bg-primary-400/80 rounded-full animate-bounce motion-reduce:animate-none" style="animation-delay: 0ms" />
              <span class="w-2 h-2 bg-primary-400/80 rounded-full animate-bounce motion-reduce:animate-none" style="animation-delay: 150ms" />
              <span class="w-2 h-2 bg-primary-400/80 rounded-full animate-bounce motion-reduce:animate-none" style="animation-delay: 300ms" />
            </div>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-300 high-contrast:text-white mt-2 leading-snug">
            {{ textoAguardandoIA }}
          </p>
        </div>
      </div>

    </div>

  </main>

    <!-- Barra de Input -->
    <footer
      v-if="atendimentoBloqueadoInelegivel"
      class="chat-composer-footer flex-shrink-0 z-30 bg-gray-50 dark:bg-gray-900 high-contrast:bg-black border-t border-amber-200 dark:border-amber-800 high-contrast:border-yellow-300 safe-area-inset-bottom"
      role="status"
      aria-live="polite"
    >
      <div class="px-4 py-4 text-center">
        <p class="text-sm font-medium text-amber-900 dark:text-amber-100 high-contrast:text-yellow-300">
          Atendimento encerrado por fora de escopo
        </p>
        <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white mt-1">
          Use os botões acima para escolher outro serviço ou voltar ao início.
        </p>
      </div>
    </footer>
    <footer
      v-else
      class="chat-composer-footer flex-shrink-0 z-30 bg-white dark:bg-gray-900 high-contrast:bg-black border-t border-gray-200 dark:border-gray-800 high-contrast:border-yellow-300 safe-area-inset-bottom"
    >
      <div class="px-3 py-3 sm:px-4">
        <div class="chat-composer-grid">
          <!-- Coluna esquerda: câmera + anexos -->
          <div class="chat-composer-rail" aria-label="Mídia e anexos">
            <button
              type="button"
              class="chat-composer-btn"
              :disabled="chatStore.isTyping || enviandoAnexo"
              title="Tirar foto"
              aria-label="Abrir câmera"
              @click="triggerCameraInput"
            >
              <CameraIcon class="w-5 h-5 text-gray-700 dark:text-gray-200 high-contrast:text-white" aria-hidden="true" />
            </button>
            <button
              type="button"
              class="chat-composer-btn"
              :disabled="chatStore.isTyping || enviandoAnexo"
              title="Fotos, PDF, Word, Excel ou texto"
              aria-label="Anexar fotos ou documentos"
              @click="triggerGalleryInput"
            >
              <PaperClipIcon class="w-5 h-5 text-gray-700 dark:text-gray-200 high-contrast:text-white" aria-hidden="true" />
            </button>
          </div>

          <!-- Campo de texto -->
          <textarea
            ref="textareaRef"
            v-model="mensagemAtual"
            class="chat-composer-input input resize-none max-h-32"
            placeholder="Digite sua mensagem..."
            rows="2"
            aria-label="Mensagem para a assistente"
            :disabled="chatStore.isTyping || enviandoAnexo"
            :aria-busy="enviandoAnexo"
            @keydown.enter.exact.prevent="enviarMensagem"
            @input="ajustarAlturaTextarea"
          />

          <!-- Coluna direita: microfone + enviar -->
          <div
            class="chat-composer-rail"
            :class="{ 'justify-end': !voiceEnabled }"
            aria-label="Voz e envio"
          >
            <button
              v-if="voiceEnabled"
              type="button"
              class="chat-composer-btn"
              :class="{ 'chat-composer-btn--recording': gravandoAudio }"
              :disabled="chatStore.isTyping || transcrevendoAudio"
              :title="gravandoAudio ? 'Toque para parar e transcrever' : 'Gravar mensagem de voz'"
              :aria-label="gravandoAudio ? 'Parar gravação' : 'Gravar áudio'"
              @click="toggleGravacaoAudio"
            >
              <StopIcon v-if="gravandoAudio" class="w-5 h-5 text-white" aria-hidden="true" />
              <MicrophoneIcon
                v-else
                class="w-5 h-5 text-gray-700 dark:text-gray-200 high-contrast:text-yellow-300"
                aria-hidden="true"
              />
            </button>
            <button
              type="button"
              class="chat-composer-btn chat-composer-btn--send"
              :disabled="!mensagemAtual.trim() || chatStore.isTyping"
              title="Enviar mensagem"
              aria-label="Enviar mensagem"
              @click="enviarMensagem"
            >
              <PaperAirplaneIcon class="w-5 h-5 text-white" aria-hidden="true" />
            </button>
          </div>
        </div>

        <!-- Envio de anexo -->
        <transition name="slide-up">
          <div
            v-if="enviandoAnexo && textoStatusAnexo"
            class="mt-2 flex items-center gap-2 text-sm font-semibold text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300"
            role="status"
            aria-live="polite"
          >
            <span
              class="inline-block w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin flex-shrink-0"
            />
            {{ textoStatusAnexo }}
          </div>
        </transition>

        <!-- Indicador de Gravação / Transcrição -->
        <transition name="slide-up">
          <div
            v-if="gravandoAudio || transcrevendoAudio"
            class="mt-2 flex items-center gap-2 text-sm font-semibold"
            :class="transcrevendoAudio
              ? 'text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300'
              : 'text-red-600 dark:text-red-400 high-contrast:text-red-300'"
          >
            <span
              class="w-3 h-3 rounded-full animate-pulse"
              :class="transcrevendoAudio ? 'bg-primary-500' : 'bg-red-500'"
            ></span>
            {{ transcrevendoAudio ? 'Transcrevendo áudio...' : 'Gravando — toque no microfone para enviar' }}
            <span v-if="gravandoAudio" class="ml-auto text-gray-600 dark:text-gray-400 high-contrast:text-white">
              {{ tempoGravacao }}s
            </span>
          </div>
        </transition>
      </div>
    </footer>

    <input
      ref="cameraInputRef"
      type="file"
      accept="image/*"
      capture="environment"
      class="sr-only"
      tabindex="-1"
      @change="handleFileSelect"
    />
    <input
      ref="galleryInputRef"
      type="file"
      :accept="CHAT_GALLERY_ACCEPT"
      multiple
      class="sr-only"
      tabindex="-1"
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useDialog } from '@/composables/useDialog'
import { chatService } from '@/services/api'
import { prepareChatImageFiles } from '@/utils/prepareChatImage'
import {
  CHAT_GALLERY_ACCEPT,
  mensagemStatusAnexo,
  textoResumoAnexos
} from '@/utils/chatAttachments'
import ChatConfirmation from '@/components/pwa/chat/ChatConfirmation.vue'
import ChatLocationPicker from '@/components/pwa/chat/ChatLocationPicker.vue'
import ChatReviewCard from '@/components/pwa/chat/ChatReviewCard.vue'
import ChatPhotoPreview from '@/components/pwa/chat/ChatPhotoPreview.vue'
import ChatSatisfacao from '@/components/pwa/chat/ChatSatisfacao.vue'
import ChatFieldChoices from '@/components/pwa/chat/ChatFieldChoices.vue'
import ChatFieldLookupUnidades from '@/components/pwa/chat/ChatFieldLookupUnidades.vue'
import ChatFieldLookupEquipamentos from '@/components/pwa/chat/ChatFieldLookupEquipamentos.vue'
import { LOOKUP_DATASOURCE_EQUIPAMENTOS, LOOKUP_DATASOURCE_UNIDADES } from '@/constants/fluxoTramitacao'
import ChatInelegibilidadeAcoes from '@/components/pwa/chat/ChatInelegibilidadeAcoes.vue'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import PwaA11yMenu from '@/components/pwa/PwaA11yMenu.vue'
import {
  ChevronLeftIcon,
  SparklesIcon,
  InformationCircleIcon,
  MapPinIcon,
  MapIcon,
  CameraIcon,
  PaperClipIcon,
  MicrophoneIcon,
  StopIcon,
  PaperAirplaneIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import { useAudioRecorder } from '@/composables/useAudioRecorder'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

const aguardandoRespostaIA = computed(
  () => chatStore.isTyping || (chatStore.loading && chatStore.mensagens.length === 0)
)

const textoAguardandoIA = computed(() => {
  if (chatStore.loading && chatStore.mensagens.length === 0) {
    return 'Conectando com a assistente...'
  }
  return 'A IA está analisando sua solicitação...'
})

const atendimentoBloqueadoInelegivel = computed(
  () => (chatStore.sessaoAtual?.fase || '').toLowerCase() === 'inelegivel'
)

const indiceUltimaMensagemIa = computed(() => {
  const msgs = chatStore.mensagens
  for (let i = msgs.length - 1; i >= 0; i--) {
    if (msgs[i].tipo === 'ia') return i
  }
  return -1
})

function deveExibirAcoesInelegibilidade(index) {
  return atendimentoBloqueadoInelegivel.value && index === indiceUltimaMensagemIa.value
}

function irEscolherOutroServico() {
  chatStore.pararPolling?.()
  router.push({ name: 'pwa-nova-solicitacao' })
}

function irInicioPwa() {
  chatStore.pararPolling?.()
  router.push({ name: 'pwa-dashboard' })
}
const dialog = useDialog()

const categoriaNome = computed(() => route.params.categoriaNome)
const messagesContainer = ref(null)
const textareaRef = ref(null)
const cameraInputRef = ref(null)
const galleryInputRef = ref(null)
const mensagemAtual = ref('')
const enviandoAnexo = ref(false)
const faseEnvioAnexo = ref(null)
const quantidadeAnexosPendente = ref(0)

const textoStatusAnexo = computed(() =>
  mensagemStatusAnexo(faseEnvioAnexo.value, quantidadeAnexosPendente.value)
)
const voiceEnabled = import.meta.env.VITE_ENABLE_VOICE_INPUT !== 'false'
const audioRecorder = useAudioRecorder()
const gravandoAudio = ref(false)
const transcrevendoAudio = ref(false)
const tempoGravacao = ref(0)
const mostrarInfo = ref(false)
const confirmandoProtocolo = ref(false)
const MAX_SEGUNDOS_GRAVACAO = 90
const MIN_SEGUNDOS_GRAVACAO = 1
let intervaloGravacao = null

// Scroll automático para o final
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Ajusta altura do textarea dinamicamente
function ajustarAlturaTextarea() {
  const textarea = textareaRef.value
  if (textarea) {
    const minPx = 92
    textarea.style.height = 'auto'
    textarea.style.height = `${Math.max(minPx, textarea.scrollHeight)}px`
  }
}

// Enviar mensagem
async function enviarMensagem() {
  if (atendimentoBloqueadoInelegivel.value) return
  const texto = mensagemAtual.value.trim()
  if (!texto || chatStore.isTyping) return
  
  mensagemAtual.value = ''
  ajustarAlturaTextarea()
  
  const resultado = await chatStore.enviarMensagem({ texto })
  if (resultado.success && resultado.protocolo) {
    encerrarSeNecessario(resultado)
  }
}

// Handler: Confirmar Serviço
async function handleConfirmarServico(valor) {
  if (valor === 'sim') {
    await chatStore.enviarMensagem({ texto: 'sim' })
  } else {
    await chatStore.enviarMensagem({ texto: 'nao' })
  }
}

// Handler: Confirmar Localização
async function handleConfirmarLocalizacao(dadosLocalizacao) {
  const resultado = await chatStore.enviarMensagem({
    texto: `📍 ${dadosLocalizacao.endereco_texto}`,
    localizacao: {
      latitude: dadosLocalizacao.latitude,
      longitude: dadosLocalizacao.longitude,
      endereco: dadosLocalizacao.endereco_texto
    }
  })
  
  if (resultado.success && resultado.protocolo) {
    encerrarSeNecessario(resultado)
  }
}

// Handler: Cancelar Localização
function handleCancelarLocalizacao() {
  chatStore.adicionarMensagemErro('Envio de localização cancelado.')
}

// Handler: Quick Reply Genérico
async function handleQuickReply(valor) {
  await chatStore.enviarMensagem({ texto: valor })
}

function escolhaUiAtiva(mensagem) {
  const ultimaIa = [...chatStore.mensagens].reverse().find((m) => m.tipo === 'ia')
  return ultimaIa?.id === mensagem.id
}

function escolhaLookupUnidadesAtiva(mensagem) {
  const config = configEscolhaMensagem(mensagem)
  if (!config?.campo || config?.datasource !== LOOKUP_DATASOURCE_UNIDADES) return false
  return escolhaUiAtiva(mensagem)
}

function escolhaLookupEquipamentosAtiva(mensagem) {
  const config = configEscolhaMensagem(mensagem)
  if (!config?.campo || config?.datasource !== LOOKUP_DATASOURCE_EQUIPAMENTOS) return false
  return escolhaUiAtiva(mensagem)
}

function escolhaCampoAtiva(mensagem) {
  const config = configEscolhaMensagem(mensagem)
  if (!config?.campo) return false
  if (config?.datasource === LOOKUP_DATASOURCE_UNIDADES) return false
  if (config?.datasource === LOOKUP_DATASOURCE_EQUIPAMENTOS) return false
  return escolhaUiAtiva(mensagem)
}

function configEscolhaMensagem(mensagem) {
  return (
    mensagem.escolhaConfig ||
    chatStore.sessaoAtual?.pending_escolha ||
    null
  )
}

async function handleEscolhaCampo({ texto, dados_slot }) {
  await chatStore.enviarMensagem({ texto, dados_slot })
}

// Handler: Confirmar Protocolo (Revisão Final)
async function handleConfirmarProtocolo() {
  if (confirmandoProtocolo.value) return
  confirmandoProtocolo.value = true
  try {
    const resultado = await chatStore.enviarMensagem({
      texto: 'Confirmar e gerar protocolo',
      confirmar_protocolo: true
    })

    if (resultado.success && resultado.protocolo) {
      encerrarSeNecessario(resultado)
    }
  } finally {
    confirmandoProtocolo.value = false
  }
}

function encerrarSeNecessario(resultado) {
  const acao =
    resultado.mensagemResposta?.tipoAcao ??
    resultado.mensagemResposta?.tipo_acao
  if (resultado.protocolo && acao !== 'pesquisa_satisfacao') {
    tratarFinalizacaoComProtocolo(resultado.protocolo)
  }
}

// Handler: Editar Revisão
function handleEditarRevisao() {
  chatStore.adicionarMensagemErro('Para editar, descreva o que precisa ser alterado.')
}

async function resolverProtocoloParaAvaliacao() {
  if (chatStore.protocoloPendente?.id) {
    return chatStore.protocoloPendente.id
  }
  if (chatStore.sessaoAtual?.protocolo_final_id) {
    return chatStore.sessaoAtual.protocolo_final_id
  }
  const sessaoId = chatStore.sessaoAtual?.id
  if (!sessaoId) return null

  try {
    const data = await chatService.listarMensagens(sessaoId)
    if (data.sessao) {
      chatStore.sessaoAtual = data.sessao
    }
    if (data.protocolo?.id) {
      chatStore.protocoloPendente = data.protocolo
      return data.protocolo.id
    }
    return data.sessao?.protocolo_final_id || null
  } catch {
    return null
  }
}

const enviandoSatisfacaoAbertura = ref(false)

// Handler: Enviar Satisfação (experiência de abertura no chat — não CSAT de resolução)
async function handleEnviarSatisfacao(dados) {
  if (enviandoSatisfacaoAbertura.value) return

  const sessaoId = chatStore.sessaoAtual?.id
  if (!sessaoId) {
    chatStore.adicionarMensagemErro('Não foi possível identificar a conversa para avaliação.')
    return
  }

  const protocoloId = await resolverProtocoloParaAvaliacao()

  enviandoSatisfacaoAbertura.value = true
  try {
    await chatService.avaliarAbertura(sessaoId, {
      nota: dados.nota,
      comentario: dados.comentario || ''
    })
    chatStore.adicionarMensagemLocal({
      id: `avaliacao-${Date.now()}`,
      autor: 'sistema',
      conteudo_texto: 'Obrigado! Sua avaliação sobre a abertura da solicitação foi registrada.',
      criado_em: new Date().toISOString()
    })
    if (protocoloId) {
      tratarFinalizacaoComProtocolo(
        chatStore.protocoloPendente || { id: protocoloId, codigo: '' }
      )
    }
  } catch {
    chatStore.adicionarMensagemErro('Erro ao enviar avaliação. Tente novamente.')
  } finally {
    enviandoSatisfacaoAbertura.value = false
  }
}

// Handler: Cancelar Satisfação
function handleCancelarSatisfacao() {
  chatStore.adicionarMensagemLocal({
    id: `pular-${Date.now()}`,
    autor: 'cidadao',
    conteudo_texto: 'Prefiro não avaliar agora',
    criado_em: new Date().toISOString()
  })
  const protocoloId =
    chatStore.protocoloPendente?.id || chatStore.sessaoAtual?.protocolo_final_id
  if (protocoloId) {
    tratarFinalizacaoComProtocolo(
      chatStore.protocoloPendente || { id: protocoloId, codigo: '' }
    )
  }
}

// Parse Quick Replies do tipo_acao
function parseQuickReplies(tipoAcao) {
  const opcoes = tipoAcao.replace('quick_reply:', '').split(',').map(o => o.trim())
  return opcoes.map((texto, index) => ({
    texto,
    valor: texto,
    primary: index === 0
  }))
}

function triggerCameraInput() {
  cameraInputRef.value?.click()
}

function triggerGalleryInput() {
  galleryInputRef.value?.click()
}

// Manipula seleção de arquivos
async function handleFileSelect(event) {
  const brutos = Array.from(event.target.files || [])
  event.target.value = ''

  if (brutos.length === 0 || enviandoAnexo.value) return

  quantidadeAnexosPendente.value = brutos.length
  enviandoAnexo.value = true
  faseEnvioAnexo.value = 'preparando'
  try {
    const arquivos = await prepareChatImageFiles(brutos)
    if (!arquivos.length) return

    faseEnvioAnexo.value = 'enviando'
    quantidadeAnexosPendente.value = arquivos.length

    const resultado = await chatStore.enviarMensagem({
      texto: textoResumoAnexos(arquivos),
      arquivos
    })

    if (resultado.success && resultado.protocolo) {
      encerrarSeNecessario(resultado)
    }
  } finally {
    enviandoAnexo.value = false
    faseEnvioAnexo.value = null
    quantidadeAnexosPendente.value = 0
  }
}

// Visualizar foto (placeholder)
function handleVisualizarFoto(index) {
  // TODO: Implementar modal de visualização em tela cheia
  console.log('Visualizar foto', index)
}

function pararTimerGravacao() {
  if (intervaloGravacao) {
    clearInterval(intervaloGravacao)
    intervaloGravacao = null
  }
}

async function toggleGravacaoAudio() {
  if (!voiceEnabled || chatStore.isTyping || transcrevendoAudio.value) return

  if (!audioRecorder.supported) {
    await dialog.alert(
      'Seu navegador não suporta gravação de áudio ou o site não está em HTTPS.',
      'Microfone indisponível'
    )
    return
  }

  if (!gravandoAudio.value) {
    const inicio = await audioRecorder.startRecording()
    if (!inicio.success) {
      await dialog.alert(inicio.error || audioRecorder.error.value, 'Microfone')
      return
    }

    gravandoAudio.value = true
    tempoGravacao.value = 0
    pararTimerGravacao()
    intervaloGravacao = setInterval(() => {
      tempoGravacao.value += 1
      if (tempoGravacao.value >= MAX_SEGUNDOS_GRAVACAO) {
        void finalizarGravacaoAudio()
      }
    }, 1000)
    return
  }

  await finalizarGravacaoAudio()
}

async function finalizarGravacaoAudio() {
  pararTimerGravacao()
  const duracao = tempoGravacao.value
  gravandoAudio.value = false

  if (duracao < MIN_SEGUNDOS_GRAVACAO) {
    audioRecorder.cancelRecording()
    await dialog.alert('Grave pelo menos 1 segundo antes de parar.', 'Áudio muito curto')
    return
  }

  transcrevendoAudio.value = true
  try {
    const blob = await audioRecorder.stopRecording()
    const resultado = await audioRecorder.transcribeAudio(blob)
    if (resultado.success) {
      mensagemAtual.value = resultado.text
      await nextTick()
      ajustarAlturaTextarea()
      textareaRef.value?.focus()
    } else {
      await dialog.alert(resultado.error, 'Transcrição')
    }
  } catch {
    chatStore.adicionarMensagemErro('Erro ao processar o áudio. Tente novamente ou digite a mensagem.')
  } finally {
    transcrevendoAudio.value = false
    tempoGravacao.value = 0
  }
}

// Tratamento de finalização com protocolo
function tratarFinalizacaoComProtocolo(protocolo) {
  if (!protocolo || !protocolo.id) return
  
  // Exibe mensagem de sucesso
  chatStore.adicionarMensagemLocal({
    id: `sucesso-${Date.now()}`,
    autor: 'sistema',
    conteudo_texto: `✅ Protocolo gerado com sucesso!\n\nCódigo: ${protocolo.codigo}\n\nRedirecionando...`,
    criado_em: new Date().toISOString()
  })
  
  // Redireciona após 3 segundos
  setTimeout(() => {
    router.push(`/protocolo/${protocolo.id}`)
  }, 3000)
}

// Voltar
async function voltar() {
  const sair = await dialog.confirm(
    'O progresso desta conversa não será salvo se você sair agora.',
    'Sair da conversa?',
    { confirmText: 'Sair', cancelText: 'Continuar no chat' }
  )
  if (sair) {
    chatStore.resetar()
    router.push('/nova-solicitacao')
  }
}

// Inicialização
onMounted(async () => {
  // Reseta store anterior
  chatStore.resetar()
  
  // Inicia nova sessão
  await chatStore.iniciarSessao(categoriaNome.value)
})

// Cleanup
onBeforeUnmount(() => {
  chatStore.pararPolling({ desligarTyping: true })
  pararTimerGravacao()
  if (gravandoAudio.value) {
    audioRecorder.cancelRecording()
    gravandoAudio.value = false
  }
})

// Watch para scroll automático
watch(
  () => [
    chatStore.mensagens.length,
    chatStore.mensagens.at(-1)?.id,
    aguardandoRespostaIA.value
  ],
  () => {
    scrollToBottom()
  }
)

</script>

<style scoped>
.chat-composer-grid {
  @apply grid gap-2 items-stretch;
  grid-template-columns: auto 1fr auto;
}

.chat-composer-rail {
  @apply flex flex-col gap-2 justify-between;
}

.chat-composer-btn {
  @apply inline-flex flex-shrink-0 items-center justify-center;
  @apply w-11 h-11 rounded-xl;
  @apply bg-gray-100 dark:bg-primary-900/90 high-contrast:bg-gray-900;
  @apply border border-gray-300 dark:border-primary-800/50 high-contrast:border-yellow-300;
  @apply shadow-soft transition-all duration-200;
  @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900;
  @apply disabled:opacity-45 disabled:cursor-not-allowed disabled:shadow-none;
}

.chat-composer-btn:not(:disabled):hover {
  @apply bg-gray-200 dark:bg-primary-800/95 high-contrast:bg-yellow-300/20;
}

.chat-composer-btn--recording {
  @apply bg-red-500 border-red-400 animate-pulse;
}

.chat-composer-btn--send {
  @apply bg-gradient-to-br from-primary-500 to-primary-600 border-primary-500;
  @apply high-contrast:from-blue-600 high-contrast:to-blue-700 high-contrast:border-yellow-300;
}

.chat-composer-btn--send:not(:disabled):hover {
  @apply from-primary-600 to-primary-700;
}

.chat-composer-input {
  @apply min-h-[5.75rem] h-full self-stretch py-3 text-base leading-snug;
}

/* Bolhas de mensagem */
.rounded-bubble-left {
  border-radius: 1.25rem 1.25rem 1.25rem 0.375rem;
}

.rounded-bubble-right {
  border-radius: 1.25rem 1.25rem 0.375rem 1.25rem;
}

/* Animações */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Scrollbar customizada */
main::-webkit-scrollbar {
  width: 6px;
}

main::-webkit-scrollbar-track {
  background: transparent;
}

main::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 3px;
}

main::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}

/* Dark mode scrollbar */
.dark main::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.5);
}

.dark main::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 0.7);
}
</style>
