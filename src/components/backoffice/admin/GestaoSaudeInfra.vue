<template>
  <div class="max-w-7xl mx-auto">
    <div
      class="relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700/60 bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 shadow-2xl"
    >
      <div
        class="absolute inset-0 opacity-[0.07] pointer-events-none"
        style="
          background-image: radial-gradient(circle at 1px 1px, rgb(148 163 184) 1px, transparent 0);
          background-size: 24px 24px;
        "
        aria-hidden="true"
      />
      <div
        class="absolute -top-24 -right-24 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl pointer-events-none"
        aria-hidden="true"
      />

      <div class="relative p-6 sm:p-8 space-y-8">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <p class="text-[11px] uppercase tracking-[0.2em] text-slate-500 font-semibold mb-1">
              NOC · Confiança operacional
            </p>
            <h2 class="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <SignalIcon class="w-7 h-7 text-cyan-600 dark:text-cyan-400" />
              Saúde do sistema — Chat IA
            </h2>
            <p class="text-sm text-slate-600 dark:text-slate-400 mt-2 max-w-2xl">
              Monitoramento em tempo real do broker Redis e dos workers Celery que processam filas
              conversacionais do PWA e canais integrados.
            </p>
          </div>

          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-800 dark:text-slate-100 text-sm font-medium transition-colors disabled:opacity-50 shadow-sm"
            :disabled="loadingInicial || atualizando"
            @click="atualizarManual"
          >
            <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': atualizando }" />
            Atualizar status
          </button>
        </div>

        <div v-if="loadingInicial" class="space-y-6">
          <div class="h-28 rounded-xl bg-slate-200 dark:bg-slate-800/60 animate-pulse" />
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="h-52 rounded-xl bg-slate-200 dark:bg-slate-800/50 animate-pulse" />
            <div class="h-52 rounded-xl bg-slate-200 dark:bg-slate-800/50 animate-pulse" />
          </div>
        </div>

        <template v-else>
          <div
            class="rounded-xl border p-5 sm:p-6 transition-colors"
            :class="
              operacional
                ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-700/50'
                : 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-700/50'
            "
          >
            <div class="flex flex-col sm:flex-row sm:items-center gap-4">
              <div
                class="flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center"
                :class="operacional ? 'bg-emerald-500/20' : 'bg-red-500/20'"
              >
                <CheckCircleIcon v-if="operacional" class="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
                <ExclamationTriangleIcon v-else class="w-8 h-8 text-red-600 dark:text-red-400" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-3">
                  <span
                    class="text-lg sm:text-xl font-bold"
                    :class="operacional ? 'text-emerald-900 dark:text-emerald-100' : 'text-red-900 dark:text-red-100'"
                  >
                    {{ operacional ? 'Sistemas operacionais' : 'Instabilidade detectada' }}
                  </span>
                  <span
                    class="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded-full border"
                    :class="
                      operacional
                        ? 'text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-600/60 bg-emerald-100/80 dark:bg-emerald-900/30'
                        : 'text-red-800 dark:text-red-300 border-red-300 dark:border-red-600/60 bg-red-100/80 dark:bg-red-900/30'
                    "
                  >
                    <span
                      class="w-2 h-2 rounded-full ping-dot"
                      :class="
                        operacional
                          ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
                          : 'bg-red-500 shadow-[0_0_8px_rgba(248,113,113,0.8)]'
                      "
                    />
                    {{ operacional ? 'Chat operacional' : 'Chat degradado' }}
                  </span>
                </div>
                <p v-if="!operacional" class="text-sm text-red-800/90 dark:text-red-200/90 mt-2 leading-relaxed">
                  O atendimento via IA pelo WhatsApp/PWA pode estar inoperante. Verifique Redis e
                  workers Celery abaixo ou acione a equipe de infraestrutura.
                </p>
                <p v-else class="text-sm text-emerald-800/90 dark:text-emerald-200/80 mt-2">
                  Broker e filas respondendo dentro dos parâmetros esperados.
                </p>
                <p v-if="erroHttp" class="text-xs text-amber-700 dark:text-amber-300/90 mt-2 font-mono">
                  Erro na consulta: {{ erroHttp }}
                </p>
              </div>
            </div>
          </div>

          <article
            class="rounded-xl border backdrop-blur-md bg-white/90 dark:bg-slate-900/60 p-5 sm:p-6 shadow-sm"
            :class="cardBorderClassAgente"
          >
            <header class="flex items-start justify-between gap-3 mb-4">
              <div class="flex items-center gap-3">
                <div class="p-2.5 rounded-xl bg-violet-500/10 dark:bg-violet-500/15 border border-violet-200 dark:border-violet-500/30">
                  <SparklesIcon class="w-6 h-6 text-violet-600 dark:text-violet-300" />
                </div>
                <div>
                  <h3 class="text-base font-bold text-slate-900 dark:text-white">Agente IA &amp; Orçamento de Tokens</h3>
                  <p class="text-xs text-slate-500">Radar operacional · consumo mensal</p>
                </div>
              </div>
              <span
                v-if="agenteIa?.ativo"
                class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-600/50 bg-emerald-50 dark:bg-emerald-950/50"
              >
                Ativo
              </span>
              <span
                v-else
                class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-600"
              >
                Inativo
              </span>
            </header>

            <div v-if="agenteIa" class="space-y-3">
              <div class="flex justify-between text-sm text-slate-700 dark:text-slate-300">
                <span>{{ formatarNumero(agenteIa.tokens_mes_atual) }} tokens usados</span>
                <span class="font-semibold" :class="classePercentualAgente">
                  {{ percentualAgenteFmt }}%
                </span>
              </div>
              <div
                class="h-3 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden border border-slate-300/50 dark:border-slate-600/50"
                role="progressbar"
                :aria-valuenow="percentualAgenteNum"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="barraAgenteClass"
                  :style="{ width: `${Math.min(percentualAgenteNum, 100)}%` }"
                />
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400">
                Orçamento mensal: {{ formatarNumero(agenteIa.orcamento_tokens_mensal) }} tokens
              </p>
              <p
                v-if="agenteIa.alerta_budget_80 && !agenteIa.budget_esgotado"
                class="text-xs font-medium text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2"
              >
                Consumo acima de 80% — considere revisar o orçamento ou ajustar sensibilidade.
              </p>
              <p
                v-if="agenteIa.budget_esgotado"
                class="text-xs font-medium text-red-800 dark:text-red-200 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg px-3 py-2"
              >
                Orçamento esgotado — Radar em modo determinístico (sem custo adicional de modelo).
              </p>
              <p class="text-[11px] text-slate-500 dark:text-slate-500">
                Último briefing: {{ formatarIso(agenteIa.ultimo_briefing_em) }}
              </p>
            </div>
            <p v-else class="text-sm text-slate-500">Dados do agente indisponíveis.</p>
          </article>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <article
              class="rounded-xl border backdrop-blur-md bg-white/90 dark:bg-slate-900/60 p-5 sm:p-6 flex flex-col min-h-[220px] shadow-sm"
              :class="cardBorderClass(redisOk)"
            >
              <header class="flex items-start justify-between gap-3 mb-4">
                <div class="flex items-center gap-3">
                  <div class="p-2.5 rounded-xl bg-rose-500/10 dark:bg-rose-500/15 border border-rose-200 dark:border-rose-500/30">
                    <CircleStackIcon class="w-6 h-6 text-rose-600 dark:text-rose-300" />
                  </div>
                  <div>
                    <h3 class="text-base font-bold text-slate-900 dark:text-white">Redis</h3>
                    <p class="text-xs text-slate-500">Broker de mensageria</p>
                  </div>
                </div>
                <span
                  class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border"
                  :class="
                    redisOk
                      ? 'text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-600/50 bg-emerald-50 dark:bg-emerald-950/50'
                      : 'text-red-800 dark:text-red-300 border-red-300 dark:border-red-600/50 bg-red-50 dark:bg-red-950/50'
                  "
                >
                  {{ redisStatus }}
                </span>
              </header>

              <div class="flex-1 space-y-3">
                <div class="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                  <span
                    class="w-2.5 h-2.5 rounded-full shrink-0"
                    :class="[
                      redisOk ? 'bg-emerald-400 ping-dot' : 'bg-red-500',
                      redisOk ? 'shadow-[0_0_10px_rgba(52,211,153,0.7)]' : ''
                    ]"
                  />
                  <span>{{ redisOk ? 'Conexão ativa (ping OK)' : 'Sem resposta do broker' }}</span>
                </div>
                <p
                  v-if="dados?.redis?.detalhe"
                  class="text-xs font-mono text-red-800 dark:text-red-300/90 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg p-3 leading-relaxed break-words"
                >
                  {{ dados.redis.detalhe }}
                </p>
              </div>

              <footer class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700/80 text-[11px] text-slate-500">
                Última verificação: {{ formatadoEm }}
              </footer>
            </article>

            <article
              class="rounded-xl border backdrop-blur-md bg-white/90 dark:bg-slate-900/60 p-5 sm:p-6 flex flex-col min-h-[220px] shadow-sm"
              :class="cardBorderClass(celeryOk)"
            >
              <header class="flex items-start justify-between gap-3 mb-4">
                <div class="flex items-center gap-3">
                  <div class="p-2.5 rounded-xl bg-violet-500/10 dark:bg-violet-500/15 border border-violet-200 dark:border-violet-500/30">
                    <ServerStackIcon class="w-6 h-6 text-violet-600 dark:text-violet-300" />
                  </div>
                  <div>
                    <h3 class="text-base font-bold text-slate-900 dark:text-white">Celery</h3>
                    <p class="text-xs text-slate-500">Workers assíncronos</p>
                  </div>
                </div>
                <span
                  class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border"
                  :class="
                    celeryOk
                      ? 'text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-600/50 bg-emerald-50 dark:bg-emerald-950/50'
                      : 'text-red-800 dark:text-red-300 border-red-300 dark:border-red-600/50 bg-red-50 dark:bg-red-950/50'
                  "
                >
                  {{ celeryStatus }}
                </span>
              </header>

              <div class="flex-1 space-y-3">
                <p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
                  {{ workersVivos }}
                  <span class="text-sm font-medium text-slate-500 dark:text-slate-400">
                    {{ workersVivos === 1 ? 'worker ativo' : 'workers ativos' }}
                  </span>
                </p>

                <div v-if="filas.length" class="flex flex-wrap gap-1.5">
                  <span
                    v-for="fila in filas"
                    :key="fila"
                    class="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-600 text-cyan-700 dark:text-cyan-300"
                  >
                    {{ fila }}
                  </span>
                </div>
                <p v-else class="text-xs text-slate-500 italic">Nenhuma fila reportada pelo inspect.</p>

                <p v-if="filaPadrao" class="text-xs text-slate-600 dark:text-slate-400">
                  Fila padrão do projeto:
                  <span class="font-mono text-slate-800 dark:text-slate-200">{{ filaPadrao }}</span>
                </p>

                <p
                  v-if="dados?.celery?.detalhe && !celeryOk"
                  class="text-xs font-mono text-red-800 dark:text-red-300/90 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg p-3 leading-relaxed break-words"
                >
                  {{ dados.celery.detalhe }}
                </p>
              </div>

              <footer class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700/80 text-[11px] text-slate-500">
                Última verificação: {{ formatadoEm }}
              </footer>
            </article>
          </div>

          <p class="text-center text-[11px] text-slate-500 dark:text-slate-600">
            Atualização automática a cada 30 segundos
            <span v-if="atualizando" class="text-cyan-600 dark:text-cyan-500/80"> · sincronizando…</span>
          </p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  ArrowPathIcon,
  CheckCircleIcon,
  CircleStackIcon,
  ExclamationTriangleIcon,
  ServerStackIcon,
  SignalIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'
import { useSistemaStore } from '@/stores/sistema'

const INTERVALO_MS = 30_000

const sistemaStore = useSistemaStore()
const { saudeInfra, loadingSaude, atualizandoSaude, erroSaude } = storeToRefs(sistemaStore)

const loadingInicial = computed(() => loadingSaude.value && !saudeInfra.value)
const atualizando = computed(() => atualizandoSaude.value)
const dados = computed(() => saudeInfra.value)
const erroHttp = computed(() => erroSaude.value)

const operacional = computed(() => Boolean(dados.value?.chat_operacional))
const redisOk = computed(() => Boolean(dados.value?.redis?.ok))
const celeryOk = computed(() => Boolean(dados.value?.celery?.ok))
const redisStatus = computed(() => dados.value?.redis?.status || 'OFFLINE')
const celeryStatus = computed(() => dados.value?.celery?.status || 'OFFLINE')
const workersVivos = computed(() => Number(dados.value?.celery?.workers_vivos ?? 0))
const filas = computed(() => dados.value?.celery?.filas_detectadas || [])
const filaPadrao = computed(() => dados.value?.celery?.fila_padrao)

const agenteIa = computed(() => dados.value?.agente_ia || null)

const percentualAgenteNum = computed(() => {
  const pct = Number(agenteIa.value?.percentual_consumo)
  if (Number.isFinite(pct)) return Math.max(0, pct)
  const uso = Number(agenteIa.value?.tokens_mes_atual || 0)
  const cap = Number(agenteIa.value?.orcamento_tokens_mensal || 0)
  return cap > 0 ? (100 * uso) / cap : 0
})

const percentualAgenteFmt = computed(() => percentualAgenteNum.value.toFixed(1))

const classePercentualAgente = computed(() => {
  if (agenteIa.value?.budget_esgotado) return 'text-red-700 dark:text-red-300'
  if (agenteIa.value?.alerta_budget_80) return 'text-amber-700 dark:text-amber-300'
  return 'text-slate-700 dark:text-slate-200'
})

const barraAgenteClass = computed(() => {
  if (agenteIa.value?.budget_esgotado) return 'bg-red-500 dark:bg-red-500'
  if (agenteIa.value?.alerta_budget_80) return 'bg-amber-500 dark:bg-amber-400'
  return 'bg-violet-500 dark:bg-violet-400'
})

function cardBorderClassAgente() {
  if (agenteIa.value?.budget_esgotado) return 'border-red-200 dark:border-red-800/50'
  if (agenteIa.value?.alerta_budget_80) return 'border-amber-200 dark:border-amber-800/50'
  return 'border-violet-200 dark:border-violet-800/40'
}

function formatarNumero(n) {
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  return new Intl.NumberFormat('pt-BR').format(v)
}

function formatarIso(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

const formatadoEm = computed(() => {
  const iso = dados.value?.verificado_em
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'medium'
    })
  } catch {
    return iso
  }
})

function cardBorderClass(ok) {
  return ok
    ? 'border-emerald-200 dark:border-emerald-800/40'
    : 'border-red-200 dark:border-red-800/50'
}

let timer = null

async function atualizarManual() {
  await sistemaStore.carregarSaudeInfra().catch(() => {})
}

onMounted(async () => {
  await sistemaStore.carregarSaudeInfra().catch(() => {})
  timer = window.setInterval(() => {
    sistemaStore.carregarSaudeInfra({ silencioso: true }).catch(() => {})
  }, INTERVALO_MS)
})

onUnmounted(() => {
  if (timer != null) window.clearInterval(timer)
})
</script>

<style scoped>
.ping-dot {
  animation: ping-pulse 2s ease-in-out infinite;
}

@keyframes ping-pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.65;
    transform: scale(0.92);
  }
}
</style>