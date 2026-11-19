<template>
  <div class="flex flex-col xl:flex-row gap-6 xl:gap-8 h-full min-h-0">
    <!-- Celular virtual -->
    <div class="flex-shrink-0 flex flex-col items-center xl:items-stretch">
      <div
        class="relative w-full max-w-[340px] mx-auto rounded-[2.25rem] border-[10px] border-gray-900 dark:border-gray-950 bg-gray-900 shadow-2xl overflow-hidden"
      >
        <div class="absolute top-2 left-1/2 -translate-x-1/2 w-20 h-5 bg-gray-900 rounded-b-2xl z-10" aria-hidden="true" />

        <div class="bg-gray-100 dark:bg-gray-950 pt-8 pb-2 px-0 flex flex-col h-[560px]">
          <div
            class="px-4 py-3 flex flex-col gap-2 border-b border-gray-200 dark:border-gray-800 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm"
          >
            <div class="flex items-center gap-2">
              <div class="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center shrink-0">
                <SparklesIcon class="w-5 h-5 text-white" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ nomeServico }}</p>
                <p class="text-[10px] text-gray-500 dark:text-gray-400 font-medium">Sandbox · simulação</p>
              </div>
              <span
                class="shrink-0 text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full"
                :class="
                  origemSchema === 'rascunho'
                    ? 'bg-amber-100 text-amber-900 dark:bg-amber-950/50 dark:text-amber-200'
                    : 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                "
              >
                {{ origemSchema === 'rascunho' ? 'Testando: Rascunho' : 'Testando: Publicado' }}
              </span>
            </div>
            <div
              v-if="temRascunhoPendente"
              class="flex items-center justify-between gap-2 pl-11"
            >
              <span class="text-[10px] text-gray-500 dark:text-gray-400">Origem do schema</span>
              <div
                class="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 p-0.5 bg-gray-100 dark:bg-gray-800"
                role="group"
                aria-label="Alternar rascunho ou publicado"
              >
                <button
                  type="button"
                  class="px-2 py-0.5 text-[10px] font-semibold rounded-md transition-colors"
                  :class="
                    usarRascunho
                      ? 'bg-amber-500 text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400'
                  "
                  @click="alternarOrigem(true)"
                >
                  Rascunho
                </button>
                <button
                  type="button"
                  class="px-2 py-0.5 text-[10px] font-semibold rounded-md transition-colors"
                  :class="
                    !usarRascunho
                      ? 'bg-green-600 text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-400'
                  "
                  @click="alternarOrigem(false)"
                >
                  Publicado
                </button>
              </div>
            </div>
          </div>

          <div ref="scrollArea" class="flex-1 overflow-y-auto px-3 py-4 space-y-3 scroll-smooth">
            <p
              v-if="!mensagens.length && !digitando"
              class="text-center text-xs text-gray-500 dark:text-gray-400 py-8"
            >
              Iniciando conversa simulada…
            </p>

            <div v-for="msg in mensagens" :key="msg.id" class="animate-fade-in">
              <div v-if="msg.tipo === 'ia'" class="flex items-start gap-2 max-w-[92%]">
                <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center shrink-0">
                  <SparklesIcon class="w-3.5 h-3.5 text-white" />
                </div>
                <div class="space-y-2 min-w-0">
                  <div
                    class="rounded-2xl rounded-tl-sm px-3 py-2 text-sm leading-relaxed shadow-sm"
                    :class="
                      msg.bloqueio
                        ? 'bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-100'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-100 dark:border-gray-700'
                    "
                  >
                    {{ msg.conteudo }}
                  </div>

                  <div v-if="msg.ui && (msg.ui.tipo === 'revisao_final' || uiInterativa(msg))" class="pl-1 space-y-2">
                    <template v-if="msg.ui.tipo === 'escolha_campo' && msg.ui.config">
                      <p class="text-[10px] text-gray-500 dark:text-gray-400">{{ msg.ui.config.dica }}</p>
                      <div class="flex flex-wrap gap-1.5">
                        <button
                          v-for="op in msg.ui.config.opcoes || []"
                          :key="op.valor"
                          type="button"
                          class="text-xs px-3 py-1.5 rounded-full bg-white dark:bg-gray-800 border border-primary-300 dark:border-primary-700 text-primary-700 dark:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-950/40 transition-colors disabled:opacity-40"
                          :disabled="!uiInterativa(msg)"
                          @click="escolherOpcao(msg.ui.config, op)"
                        >
                          {{ op.rotulo }}
                        </button>
                      </div>
                    </template>

                    <button
                      v-else-if="msg.ui.tipo === 'solicitar_localizacao'"
                      type="button"
                      class="text-xs w-full py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-dashed border-primary-400 text-primary-700 dark:text-primary-300 font-medium hover:bg-primary-50 dark:hover:bg-primary-950/30 transition-colors disabled:opacity-40"
                      :disabled="!uiInterativa(msg)"
                      @click="simularLocalizacao"
                    >
                      📍 Abrir mapa (simulado)
                    </button>

                    <button
                      v-else-if="msg.ui.tipo === 'solicitar_foto'"
                      type="button"
                      class="text-xs w-full py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-dashed border-primary-400 text-primary-700 dark:text-primary-300 font-medium hover:bg-primary-50 dark:hover:bg-primary-950/30 transition-colors disabled:opacity-40"
                      :disabled="!uiInterativa(msg)"
                      @click="simularFoto"
                    >
                      📷 Abrir câmera (simulado)
                    </button>

                    <p
                      v-else-if="msg.ui.tipo === 'revisao_final'"
                      class="text-[11px] px-2 py-1 rounded-lg bg-primary-50 dark:bg-primary-950/40 text-primary-700 dark:text-primary-300 font-semibold"
                    >
                      ✓ Tela de revisão final (simulada)
                    </p>
                  </div>
                </div>
              </div>

              <div v-else class="flex justify-end">
                <div
                  class="max-w-[85%] rounded-2xl rounded-tr-sm px-3 py-2 text-sm bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-sm"
                >
                  {{ msg.conteudo }}
                </div>
              </div>
            </div>

            <div v-if="digitando" class="flex items-start gap-2">
              <div class="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-cyan-500 flex items-center justify-center">
                <SparklesIcon class="w-3.5 h-3.5 text-white" />
              </div>
              <div class="bg-white dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3 border border-gray-100 dark:border-gray-700">
                <div class="flex gap-1">
                  <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms" />
                  <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms" />
                  <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms" />
                </div>
              </div>
            </div>
          </div>

          <footer class="px-3 pb-3 pt-2 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
            <div class="flex items-center gap-2">
              <input
                v-model="textoEntrada"
                type="text"
                class="flex-1 text-sm py-2.5 px-3 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:ring-2 focus:ring-primary-500 outline-none"
                placeholder="Como o cidadão falaria…"
                :disabled="digitando || fluxoEncerrado"
                @keydown.enter.exact.prevent="enviarTexto"
              />
              <button
                type="button"
                class="p-2.5 rounded-xl bg-primary-600 hover:bg-primary-700 text-white transition-colors disabled:opacity-40"
                :disabled="!textoEntrada.trim() || digitando || fluxoEncerrado"
                aria-label="Enviar"
                @click="enviarTexto"
              >
                <PaperAirplaneIcon class="w-5 h-5" />
              </button>
            </div>
          </footer>
        </div>
      </div>

      <button
        type="button"
        class="mt-3 text-xs text-gray-500 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400 underline"
        @click="reiniciar"
      >
        Reiniciar simulação
      </button>
    </div>

    <!-- Debug -->
    <div class="flex-1 min-w-0 flex flex-col min-h-[320px] xl:min-h-0">
      <div class="flex items-center justify-between gap-2 mb-3">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white">Dados extraídos</h3>
        <span
          class="text-[10px] uppercase tracking-wide font-semibold px-2 py-0.5 rounded-full"
          :class="
            fluxoEncerrado
              ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200'
              : 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200'
          "
        >
          {{ fluxoEncerrado ? 'Bloqueado' : 'Ao vivo' }}
        </span>
      </div>

      <div
        class="flex-1 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-950 text-gray-100 p-4 overflow-auto font-mono text-xs leading-relaxed shadow-inner"
      >
        <pre v-if="Object.keys(dadosParciais).length" class="whitespace-pre-wrap break-words">{{
          jsonFormatado
        }}</pre>
        <p v-else class="text-gray-500 italic">Nenhum slot preenchido ainda — converse no celular ao lado.</p>
      </div>

      <p v-if="ultimaAcao" class="mt-2 text-[11px] text-gray-500 dark:text-gray-400">
        Último gatilho UI: <span class="font-mono text-primary-600 dark:text-primary-400">{{ ultimaAcao }}</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useCatalogoStore } from '@/stores/catalogo'
import { getApiErrorMessage } from '@/utils/apiError'
import { PaperAirplaneIcon, SparklesIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  servicoId: { type: String, required: true },
  nomeServico: { type: String, default: 'Serviço' },
  temRascunhoPendente: { type: Boolean, default: false }
})

const catalogoStore = useCatalogoStore()

const mensagens = ref([])
const historico = ref([])
const dadosParciais = ref({})
const textoEntrada = ref('')
const digitando = ref(false)
const fluxoEncerrado = ref(false)
const ultimaAcao = ref('')
const scrollArea = ref(null)

const localizacaoOk = ref(false)
const anexosCount = ref(0)
const origemSchema = ref('publicado')
const usarRascunho = ref(props.temRascunhoPendente)

let seq = 0

const jsonFormatado = computed(() => JSON.stringify(dadosParciais.value, null, 2))

const ultimaMensagemIaId = computed(() => {
  for (let i = mensagens.value.length - 1; i >= 0; i--) {
    if (mensagens.value[i].tipo === 'ia') return mensagens.value[i].id
  }
  return null
})

function uiInterativa(msg) {
  return msg.id === ultimaMensagemIaId.value && !digitando.value && !fluxoEncerrado.value
}

function scrollFim() {
  nextTick(() => {
    const el = scrollArea.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function adicionarCidadao(texto) {
  mensagens.value.push({ id: `c-${++seq}`, tipo: 'cidadao', conteudo: texto })
  scrollFim()
}

function adicionarIa(resposta, acaoUi, payloadUi, bloqueio = false) {
  const ui = montarUiMeta(acaoUi, payloadUi)
  mensagens.value.push({
    id: `ia-${++seq}`,
    tipo: 'ia',
    conteudo: resposta || '…',
    ui,
    bloqueio
  })
  scrollFim()
}

function montarUiMeta(acaoUi, payloadUi) {
  if (!acaoUi) return null
  if (acaoUi === 'escolha_campo') return { tipo: 'escolha_campo', config: payloadUi }
  if (acaoUi === 'solicitar_localizacao') return { tipo: 'solicitar_localizacao' }
  if (acaoUi === 'solicitar_foto') return { tipo: 'solicitar_foto' }
  if (acaoUi === 'revisao_final') return { tipo: 'revisao_final' }
  return { tipo: acaoUi }
}

async function executarTurno(payload) {
  digitando.value = true
  try {
    const data = await catalogoStore.sandboxServicoCatalogo(props.servicoId, payload)
    if (data.origem_schema) {
      origemSchema.value = data.origem_schema
    }
    if (Array.isArray(data.historico_sugerido)) {
      historico.value = data.historico_sugerido
    }
    dadosParciais.value = { ...(data.dados_parciais || {}) }
    ultimaAcao.value = data.acao_ui || '—'
    if (data.fluxo_bloqueado) fluxoEncerrado.value = true
    adicionarIa(
      data.resposta_cidadao || data.erro,
      data.acao_ui,
      data.payload_ui,
      Boolean(data.fluxo_bloqueado)
    )
    return data
  } catch (err) {
    adicionarIa(getApiErrorMessage(err, 'Falha na simulação.'), null, null)
    throw err
  } finally {
    digitando.value = false
  }
}

function payloadBase() {
  const base = {
    dados_parciais: { ...dadosParciais.value },
    historico: historico.value,
    localizacao_ok: localizacaoOk.value,
    anexos_novos: 0
  }
  if (props.temRascunhoPendente) {
    base.usar_rascunho = usarRascunho.value
  }
  return base
}

async function enviarTexto() {
  const texto = textoEntrada.value.trim()
  if (!texto || digitando.value || fluxoEncerrado.value) return
  textoEntrada.value = ''
  adicionarCidadao(texto)
  await executarTurno({ ...payloadBase(), mensagem: texto })
}

async function escolherOpcao(config, op) {
  if (digitando.value || fluxoEncerrado.value) return
  const rotulo = op.rotulo || op.valor
  const dadosSlot = { [config.campo]: op.valor }
  const texto = `✓ ${config.titulo || config.campo}: ${rotulo}`
  adicionarCidadao(texto)
  await executarTurno({
    ...payloadBase(),
    mensagem: texto,
    dados_slot: dadosSlot
  })
}

async function simularLocalizacao() {
  if (digitando.value || fluxoEncerrado.value) return
  localizacaoOk.value = true
  adicionarCidadao('📍 Localização confirmada (simulação)')
  await executarTurno({
    ...payloadBase(),
    mensagem: '',
    localizacao_ok: true,
    localizacao: {
      latitude: -23.52,
      longitude: -46.18,
      endereco: 'Endereço simulado — sandbox'
    }
  })
}

async function simularFoto() {
  if (digitando.value || fluxoEncerrado.value) return
  adicionarCidadao('📷 Foto anexada (simulação)')
  await executarTurno({
    ...payloadBase(),
    mensagem: '',
    anexos_novos: 1
  })
  anexosCount.value += 1
}

async function alternarOrigem(rascunho) {
  if (usarRascunho.value === rascunho) return
  usarRascunho.value = rascunho
  await reiniciar()
}

async function reiniciar() {
  mensagens.value = []
  historico.value = []
  dadosParciais.value = {}
  fluxoEncerrado.value = false
  localizacaoOk.value = false
  anexosCount.value = 0
  ultimaAcao.value = ''
  origemSchema.value = usarRascunho.value ? 'rascunho' : 'publicado'
  await iniciarConversa()
}

async function iniciarConversa() {
  await executarTurno({
    mensagem: '',
    dados_parciais: {},
    historico: []
  })
}

watch(
  () => props.servicoId,
  () => reiniciar(),
  { immediate: true }
)

watch(
  () => props.temRascunhoPendente,
  (tem) => {
    usarRascunho.value = tem
  }
)
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in {
  animation: fade-in 0.25s ease-out;
}
</style>