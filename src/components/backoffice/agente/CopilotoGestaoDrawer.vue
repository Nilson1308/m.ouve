<template>
  <Teleport to="body">
    <Transition name="copiloto-fade">
      <button
        v-if="store.aberto"
        type="button"
        class="fixed inset-0 z-[60] bg-slate-900/30 dark:bg-black/50 lg:hidden backdrop-blur-[1px]"
        aria-label="Fechar Copiloto"
        @click="store.fecharDrawer()"
      />
    </Transition>

    <Transition name="copiloto-slide">
      <aside
        v-if="store.aberto"
        class="fixed top-0 right-0 z-[70] flex flex-col h-[100dvh] w-full sm:w-[440px] lg:w-[480px] border-l border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-2xl overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="copiloto-titulo"
        id="copiloto-gestao-drawer"
      >
        <header
          class="shrink-0 px-4 py-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50/90 dark:bg-slate-900/95"
        >
          <div class="flex items-start gap-2">
            <SparklesIcon class="w-5 h-5 mt-0.5 shrink-0 text-violet-600 dark:text-violet-300" aria-hidden="true" />
            <div class="min-w-0 flex-1">
              <h2 id="copiloto-titulo" class="text-base font-bold text-slate-900 dark:text-white">
                Copiloto de Gestão
              </h2>
              <div class="flex flex-wrap items-center gap-1.5 mt-1">
                <span
                  class="text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200"
                >
                  {{ rotuloLente }}
                </span>
                <span
                  v-if="cfg"
                  class="text-[10px] font-medium text-slate-600 dark:text-slate-300"
                >
                  {{ cfg.perguntasHoje }}/{{ cfg.limiteDiario }} hoje
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1 shrink-0">
              <button
                type="button"
                class="btn-copiloto-icon"
                title="Nova conversa"
                @click="store.novaConversa()"
              >
                <PlusIcon class="w-5 h-5" />
              </button>
              <button
                type="button"
                class="btn-copiloto-icon"
                :class="store.mostrarHistorico ? 'bg-primary-100 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300' : ''"
                title="Histórico"
                @click="toggleHistorico"
              >
                <ClockIcon class="w-5 h-5" />
              </button>
              <button type="button" class="btn-copiloto-icon" title="Fechar" @click="store.fecharDrawer()">
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        <div v-if="store.mostrarHistorico" class="flex-1 min-h-0 overflow-y-auto p-4 space-y-2">
          <p class="text-xs font-semibold text-slate-600 dark:text-slate-300 mb-2">Conversas recentes</p>
          <div v-if="store.historicoCarregando" class="text-sm text-slate-500 dark:text-slate-400">Carregando…</div>
          <ul v-else class="space-y-2">
            <li
              v-for="s in store.sessoes"
              :key="s.id"
              class="group flex items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/80 dark:bg-slate-800/50"
            >
              <button
                type="button"
                class="flex-1 text-left px-3 py-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700/60 active:bg-slate-200/80 dark:active:bg-slate-600/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
                @click="store.abrirSessao(s.id)"
              >
                <span class="block text-sm font-medium text-slate-900 dark:text-white truncate">
                  {{ s.titulo }}
                </span>
                <span class="block text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  {{ formatarData(s.atualizadoEm) }}
                </span>
              </button>
              <button
                type="button"
                class="shrink-0 p-2 mr-1 rounded-lg text-slate-500 hover:text-red-600 dark:text-slate-400 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
                title="Excluir conversa"
                @click="confirmarExclusao(s)"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
            </li>
          </ul>
          <p
            v-if="!store.historicoCarregando && !store.sessoes.length"
            class="text-sm text-slate-500 dark:text-slate-400"
          >
            Nenhuma conversa anterior.
          </p>
        </div>

        <div
          v-if="!store.mostrarHistorico"
          ref="areaMensagens"
          class="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-4"
        >
          <section
            v-if="store.conversaVazia"
            class="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/90 dark:bg-slate-800/40 p-4 space-y-3"
          >
            <p class="text-sm text-slate-800 dark:text-slate-100 leading-relaxed">
              {{ textoSaudacao }}
            </p>
            <div class="flex flex-col gap-2">
              <button
                v-for="(sug, i) in sugestoes"
                :key="i"
                type="button"
                class="text-left text-sm px-3 py-2.5 rounded-xl border border-violet-200 dark:border-violet-800/80 bg-violet-50/80 dark:bg-violet-950/30 text-violet-900 dark:text-violet-100 hover:bg-violet-100 dark:hover:bg-violet-950/50 active:bg-violet-200/70 dark:active:bg-violet-900/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 dark:focus-visible:ring-violet-400 transition-colors"
                :disabled="!store.copilotoHabilitado || store.enviando"
                @click="enviarSugestao(sug)"
              >
                {{ sug }}
              </button>
            </div>
          </section>

          <template v-for="msg in store.mensagens" :key="msg.id">
            <div
              v-if="msg.papel === 'usuario'"
              class="flex justify-end"
            >
              <div
                class="max-w-[92%] rounded-2xl rounded-br-md px-3.5 py-2.5 bg-primary-600 text-white dark:bg-primary-500 shadow-sm"
              >
                <p class="text-sm whitespace-pre-wrap">{{ msg.conteudo }}</p>
              </div>
            </div>

            <div v-else class="flex justify-start">
              <div
                class="max-w-[95%] rounded-2xl rounded-bl-md px-3.5 py-3 border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800/90 shadow-sm"
              >
                <div
                  v-if="msg.statusProcessamento === 'processando' && !msg.conteudo"
                  class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300"
                  role="status"
                >
                  <span class="inline-flex gap-1" aria-hidden="true">
                    <span class="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:0ms]" />
                    <span class="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:150ms]" />
                    <span class="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce [animation-delay:300ms]" />
                  </span>
                  Consultando indicadores operacionais da sua área…
                </div>
                <CopilotoMensagemFormatada v-else-if="msg.conteudo" :texto="msg.conteudo" />

                <div
                  v-if="msg.referencias?.length"
                  class="flex flex-wrap gap-2 mt-3 pt-2 border-t border-slate-200/80 dark:border-slate-600/80"
                >
                  <button
                    v-for="(ref, ri) in refsValidas(msg.referencias)"
                    :key="`${ref.rota}-${ri}`"
                    type="button"
                    class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold border border-primary-200 dark:border-primary-700 bg-primary-50 dark:bg-primary-950/40 text-primary-800 dark:text-primary-100 hover:bg-primary-100 dark:hover:bg-primary-900/50 active:bg-primary-200/80 dark:active:bg-primary-800/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400 transition-colors"
                    @click="navegarReferencia(ref)"
                  >
                    <ArrowTopRightOnSquareIcon class="w-3.5 h-3.5 shrink-0 opacity-80" />
                    {{ ref.label }}
                  </button>
                </div>

                <footer
                  v-if="msg.statusProcessamento === 'concluida' && (msg.ferramentasUsadas?.length || msg.modoGeracao)"
                  class="mt-3 pt-2 border-t border-dashed border-slate-200 dark:border-slate-600 text-[11px] text-slate-500 dark:text-slate-400 flex flex-wrap gap-x-2 gap-y-1"
                >
                  <span v-if="fontesLabel(msg)">Fontes: {{ fontesLabel(msg) }}</span>
                  <span
                    v-if="msg.modoGeracao === 'deterministico_fallback'"
                    class="font-medium text-amber-700 dark:text-amber-300"
                  >
                    Modo determinístico (orçamento IA)
                  </span>
                </footer>

                <p
                  v-if="msg.statusProcessamento === 'erro'"
                  class="mt-2 text-xs text-red-700 dark:text-red-300"
                  role="alert"
                >
                  {{ msg.erroDetalhe || 'Erro ao gerar resposta.' }}
                </p>
              </div>
            </div>
          </template>

          <p
            v-if="store.erro"
            class="text-sm rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 text-red-800 dark:text-red-200 px-3 py-2"
            role="alert"
          >
            {{ store.erro }}
          </p>
        </div>

        <footer
          v-if="!store.mostrarHistorico"
          class="shrink-0 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-3 space-y-2"
        >
          <p
            v-if="cfg?.budgetEsgotado"
            class="text-xs rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 text-amber-900 dark:text-amber-100 px-2.5 py-2"
          >
            Orçamento mensal de IA esgotado. Respostas podem usar modo determinístico.
          </p>
          <p
            v-else-if="store.cotaAtingida"
            class="text-xs rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 text-amber-900 dark:text-amber-100 px-2.5 py-2"
          >
            Você atingiu o limite diário de perguntas ao Copiloto.
          </p>
          <div class="flex gap-2 items-end">
            <textarea
              ref="inputRef"
              v-model="rascunho"
              rows="1"
              maxlength="600"
              :disabled="!store.copilotoHabilitado || store.enviando || store.cotaAtingida"
              class="flex-1 min-h-[2.75rem] max-h-32 resize-none rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm px-3 py-2 placeholder:text-slate-500 dark:placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 disabled:opacity-60"
              placeholder="Pergunte sobre fila, SLA, qualidade…"
              @input="ajustarAltura"
              @keydown="onKeydownInput"
            />
            <button
              type="button"
              class="shrink-0 inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold bg-violet-600 text-white hover:bg-violet-700 active:bg-violet-800 dark:bg-violet-500 dark:hover:bg-violet-600 dark:active:bg-violet-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 dark:focus-visible:ring-violet-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              :disabled="!podeEnviar"
              @click="enviar"
            >
              Enviar
            </button>
          </div>
          <p class="text-[10px] text-right text-slate-500 dark:text-slate-400">
            {{ rascunho.length }}/600 · Enter envia · Shift+Enter quebra linha
          </p>
        </footer>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  SparklesIcon,
  XMarkIcon,
  PlusIcon,
  ClockIcon,
  TrashIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline'
import { useCopilotoStore } from '@/stores/copiloto'
import CopilotoMensagemFormatada from '@/components/backoffice/agente/CopilotoMensagemFormatada.vue'
import { labelFerramentaCopiloto } from '@/services/copilotoGestaoMappers'

const store = useCopilotoStore()
const route = useRoute()
const router = useRouter()

const rascunho = ref('')
const inputRef = ref(null)
const areaMensagens = ref(null)

const cfg = computed(() => store.configUsuario)

const rotuloLente = computed(() => {
  const c = cfg.value
  if (!c) return '—'
  if (c.perspectiva === 'unidade' && c.unidadeNome) return c.unidadeNome
  if (c.perspectiva === 'ouvidoria') return 'Ouvidoria'
  if (c.perspectiva === 'controladoria') return 'Controladoria'
  return c.perspectiva
})

const textoSaudacao = computed(() => {
  const c = cfg.value
  if (!c) {
    return 'Carregando configuração do Copiloto…'
  }
  if (c.perspectiva === 'unidade' && c.unidadeNome) {
    return `Olá. Enxergo apenas indicadores e protocolos da ${c.unidadeNome}, sem dados pessoais de cidadãos. As ações operacionais você executa na Mesa ou painéis — eu aponto evidências e atalhos.`
  }
  if (c.perspectiva === 'ouvidoria') {
    return 'Olá. Minha leitura é pela ótica da Ouvidoria: direitos do cidadão, SLA, cobranças e retrabalho no município — sempre sem PII.'
  }
  return 'Olá. Leio o panorama municipal (eficiência, territorio, fila e riscos) dentro do seu perfil — números verificáveis, sem inventar dados.'
})

const sugestoes = computed(() => cfg.value?.sugestoesIniciais || [])

const podeEnviar = computed(() => {
  const t = rascunho.value.trim()
  return (
    t.length >= 3 &&
    t.length <= 600 &&
    store.copilotoHabilitado &&
    !store.enviando &&
    !store.cotaAtingida
  )
})

watch(
  () => store.mensagens.length,
  () => scrollFim()
)
watch(
  () => store.iaProcessando,
  (v) => {
    if (v) scrollFim()
  }
)

watch(
  () => route.path,
  () => {
    if (store.aberto) {
      store.carregarConfig(route.fullPath)
    }
  }
)

onUnmounted(() => {
  store.aoDesmontar()
})

function scrollFim() {
  nextTick(() => {
    const el = areaMensagens.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function formatarData(iso) {
  if (!iso) return ''
  try {
    return new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short'
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

function fontesLabel(msg) {
  const nomes = (msg.ferramentasUsadas || []).map((f) =>
    labelFerramentaCopiloto(f.nome || f)
  )
  return [...new Set(nomes)].join(', ')
}

function refsValidas(refs) {
  return (refs || []).filter((ref) => {
    try {
      if (!ref?.rota || typeof ref.rota !== 'string') return false
      router.resolve({ path: ref.rota, query: ref.query || {} })
      return true
    } catch {
      return false
    }
  })
}

function navegarReferencia(ref) {
  router.push({ path: ref.rota, query: { ...(ref.query || {}) } })
  if (typeof window !== 'undefined' && window.matchMedia('(max-width: 1023px)').matches) {
    store.fecharDrawer()
  }
}

async function toggleHistorico() {
  store.mostrarHistorico = !store.mostrarHistorico
  if (store.mostrarHistorico) {
    await store.carregarHistorico()
  }
}

async function confirmarExclusao(sessao) {
  if (!window.confirm(`Excluir a conversa «${sessao.titulo}»?`)) return
  try {
    await store.excluirSessao(sessao.id)
  } catch {
    store.erro = 'Não foi possível excluir a conversa.'
  }
}

function ajustarAltura() {
  const el = inputRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 128)}px`
}

function onKeydownInput(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    enviar()
  }
}

async function enviar() {
  if (!podeEnviar.value) return
  const texto = rascunho.value.trim()
  rascunho.value = ''
  ajustarAltura()
  await store.enviarPergunta(texto, route.fullPath)
  scrollFim()
}

function enviarSugestao(texto) {
  rascunho.value = texto
  enviar()
}
</script>

<style scoped>
.btn-copiloto-icon {
  @apply p-2 rounded-lg text-slate-600 dark:text-slate-300;
  @apply hover:bg-slate-200/80 dark:hover:bg-slate-700/80;
  @apply active:bg-slate-300/80 dark:active:bg-slate-600/60;
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400;
  @apply transition-colors;
}

.copiloto-fade-enter-active,
.copiloto-fade-leave-active {
  transition: opacity 0.2s ease;
}
.copiloto-fade-enter-from,
.copiloto-fade-leave-to {
  opacity: 0;
}

.copiloto-slide-enter-active,
.copiloto-slide-leave-active {
  transition: transform 0.28s ease, opacity 0.2s ease;
}
.copiloto-slide-enter-from,
.copiloto-slide-leave-to {
  transform: translateX(100%);
  opacity: 0.6;
}
</style>