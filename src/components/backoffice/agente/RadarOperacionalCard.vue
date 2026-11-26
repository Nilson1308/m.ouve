<template>
  <section
    v-if="deveExibir"
    class="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-gray-800/90 shadow-sm overflow-hidden mb-4"
  >
    <header
      class="flex flex-wrap items-center gap-2 px-4 py-3 border-b border-slate-100 dark:border-slate-700/80 bg-slate-50/80 dark:bg-slate-900/40"
    >
      <button
        type="button"
        class="inline-flex items-center gap-2 text-left flex-1 min-w-0 rounded-lg py-1 pr-2 hover:bg-slate-100 dark:hover:bg-slate-800/80 active:bg-slate-200/80 dark:active:bg-slate-700/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400 transition-colors"
        :aria-expanded="expandido"
        @click="toggleExpandido"
      >
        <SparklesIcon class="w-5 h-5 shrink-0 text-primary-600 dark:text-primary-400" aria-hidden="true" />
        <span class="text-sm font-bold text-gray-900 dark:text-white truncate">Radar Operacional IA</span>
        <ChevronDownIcon
          class="w-4 h-4 shrink-0 text-slate-500 transition-transform"
          :class="expandido ? 'rotate-180' : ''"
          aria-hidden="true"
        />
      </button>

      <span
        v-if="briefing"
        class="text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200"
      >
        {{ rotuloLente }}
      </span>
      <span
        v-if="briefing"
        class="text-[10px] font-medium px-2 py-0.5 rounded-full"
        :class="
          briefing.modoGeracao === 'llm'
            ? 'bg-violet-100 text-violet-800 dark:bg-violet-950/60 dark:text-violet-200'
            : 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-200'
        "
      >
        {{ labelModoGeracao(briefing.modoGeracao) }}
      </span>
      <span v-if="textoGeracao" class="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:inline">
        {{ textoGeracao }}
      </span>

      <button
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-700 active:bg-slate-100 dark:active:bg-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="atualizando || Boolean(bloqueioAte)"
        :title="bloqueioAte ? mensagemBloqueio : 'Gerar nova leitura do dia'"
        @click="forcarAtualizacao"
      >
        <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': atualizando }" />
        Atualizar
      </button>
    </header>

    <div v-if="expandido" class="p-4 sm:p-5 space-y-4">
      <p
        v-if="bloqueioAte"
        class="text-xs rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 text-amber-900 dark:text-amber-100 px-3 py-2"
        role="status"
      >
        {{ mensagemBloqueio }}
      </p>

      <div v-if="carregando" class="space-y-3" aria-busy="true">
        <div class="h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />
        <div class="h-20 rounded-xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="h-32 rounded-xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
          <div class="h-32 rounded-xl bg-slate-200 dark:bg-slate-700 animate-pulse" />
        </div>
      </div>

      <p v-else-if="erroLeitura" class="text-sm text-red-600 dark:text-red-400">{{ erroLeitura }}</p>

      <template v-else-if="briefing">
        <p class="text-sm leading-relaxed text-slate-800 dark:text-slate-200 font-medium">
          {{ briefing.resumoExecutivo }}
        </p>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
          <article
            v-for="insight in insightsVisiveis"
            :key="insight.id"
            class="rounded-xl border border-slate-200 dark:border-slate-700 border-l-4 p-4 flex flex-col gap-2 shadow-sm"
            :class="[categoriaInsightClasses(insight.categoria).border, categoriaInsightClasses(insight.categoria).bg]"
          >
            <div class="flex items-start gap-2">
              <BoltIcon
                class="w-5 h-5 shrink-0 mt-0.5"
                :class="categoriaInsightClasses(insight.categoria).icon"
                aria-hidden="true"
              />
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-bold text-gray-900 dark:text-white leading-snug">{{ insight.titulo }}</h3>
                <span
                  v-if="insight.evidencia_numerica"
                  class="inline-block mt-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-full"
                  :class="categoriaInsightClasses(insight.categoria).pill"
                >
                  {{ insight.evidencia_numerica }}
                </span>
              </div>
            </div>
            <p v-if="insight.recomendacao" class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed flex-1">
              {{ insight.recomendacao }}
            </p>
            <button
              v-if="acaoValida(insight)"
              type="button"
              class="self-start text-xs font-semibold px-3 py-1.5 rounded-lg bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 dark:focus-visible:ring-offset-gray-900 transition-colors"
              @click="irParaAcao(insight)"
            >
              {{ insight.acao_sugerida.label || 'Ver detalhes' }}
            </button>
            <div class="flex items-center gap-2 pt-2 border-t border-slate-200/80 dark:border-slate-600/50">
              <span class="text-[10px] text-slate-500 dark:text-slate-500 mr-auto">Esta leitura foi útil?</span>
              <button
                type="button"
                class="p-1.5 rounded-lg border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                :class="
                  avaliacaoDe(insight.id) === true
                    ? 'border-emerald-400 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300'
                    : 'border-transparent text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-emerald-600 dark:hover:text-emerald-400'
                "
                title="Útil"
                @click="enviarAvaliacao(insight.id, true)"
              >
                <HandThumbUpIcon class="w-4 h-4" />
              </button>
              <button
                type="button"
                class="p-1.5 rounded-lg border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                :class="
                  avaliacaoDe(insight.id) === false
                    ? 'border-red-300 bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300'
                    : 'border-transparent text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-red-600 dark:hover:text-red-400'
                "
                title="Não útil"
                @click="enviarAvaliacao(insight.id, false)"
              >
                <HandThumbDownIcon class="w-4 h-4" />
              </button>
            </div>
          </article>
        </div>

        <p v-if="!insightsVisiveis.length" class="text-xs text-slate-500 dark:text-slate-400">
          Nenhum apontamento prioritário no momento. A operação está dentro dos parâmetros habituais.
        </p>
      </template>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowPathIcon,
  BoltIcon,
  ChevronDownIcon,
  HandThumbDownIcon,
  HandThumbUpIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'
import { agenteGestaoService } from '@/services/api'
import {
  categoriaInsightClasses,
  labelEscopoBriefing,
  labelModoGeracao
} from '@/services/agenteGestaoMappers'
import { useRbac } from '@/composables/useRbac'
import { useAuthStore } from '@/stores/auth'
import { useSetorialStore } from '@/stores/setorial'

const props = defineProps({
  /** Chave única por tela para persistir colapso no localStorage */
  storageKey: { type: String, required: true },
  /** Query ?perspectiva= (ex.: ouvidoria na Mesa municipal) */
  perspectiva: { type: String, default: '' },
  /** Nome da secretaria exibido na lente (setorial) */
  unidadeNomeOverride: { type: String, default: '' }
})

const router = useRouter()
const { can } = useRbac()
const authStore = useAuthStore()
const setorialStore = useSetorialStore()

const habilitadoConfig = ref(true)
const configVerificada = ref(false)
/** Perfis sem configuracoes.ler: card só aparece após GET briefing 200 */
const briefingDisponivel = ref(false)

const comConfigGestao = computed(() => can('configuracoes.ler'))
const briefing = ref(null)
const carregando = ref(false)
const atualizando = ref(false)
const erroLeitura = ref('')
const bloqueioAte = ref(null)
const minhasAvaliacoes = ref({})

const LS_PREFIX = 'ouve_radar_expandido_'

const expandido = ref(true)

const podeBriefing = computed(() => can('mesa_trabalho.ler'))

const deveExibir = computed(() => {
  if (!podeBriefing.value) return false
  if (comConfigGestao.value) {
    if (!configVerificada.value) return false
    if (habilitadoConfig.value === false) return false
    return true
  }
  return briefingDisponivel.value
})

const insightsVisiveis = computed(() => (briefing.value?.insights || []).slice(0, 5))

const rotuloLente = computed(() => {
  if (!briefing.value) return ''
  const nome =
    props.unidadeNomeOverride ||
    setorialStore.unidade?.nome ||
    authStore.user?.unidade_nome ||
    ''
  return labelEscopoBriefing(briefing.value.escopoTipo, nome)
})

const textoGeracao = computed(() => {
  if (!briefing.value?.dataReferencia) return ''
  try {
    const d = new Date(`${briefing.value.dataReferencia}T12:00:00`)
    return `Referência ${d.toLocaleDateString('pt-BR')}`
  } catch {
    return `Referência ${briefing.value.dataReferencia}`
  }
})

const mensagemBloqueio = computed(() => {
  if (!bloqueioAte.value) return ''
  const hora = bloqueioAte.value.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return `Atualização disponível novamente às ${hora} (limite de uma atualização a cada 15 minutos).`
})

function storageKeyExpandido() {
  return `${LS_PREFIX}${props.storageKey}`
}

function toggleExpandido() {
  expandido.value = !expandido.value
  try {
    localStorage.setItem(storageKeyExpandido(), expandido.value ? '1' : '0')
  } catch {
    /* ignore */
  }
}

function restaurarExpandido() {
  try {
    const raw = localStorage.getItem(storageKeyExpandido())
    if (raw === '0') expandido.value = false
    else if (raw === '1') expandido.value = true
  } catch {
    expandido.value = true
  }
}

function avaliacaoDe(insightId) {
  const v = minhasAvaliacoes.value[insightId]
  if (v === true) return true
  if (v === false) return false
  return null
}

function paramsBriefing() {
  const p = {}
  if (props.perspectiva) p.perspectiva = props.perspectiva
  return p
}

async function resolverHabilitado() {
  if (!can('configuracoes.ler')) {
    habilitadoConfig.value = true
    configVerificada.value = true
    return
  }
  try {
    const cfg = await agenteGestaoService.obterConfiguracao()
    habilitadoConfig.value = Boolean(cfg.agente_ativo && cfg.briefing_proativo_ativo)
  } catch {
    habilitadoConfig.value = true
  } finally {
    configVerificada.value = true
  }
}

async function carregarBriefing(forcar = false) {
  if (comConfigGestao.value) {
    if (!configVerificada.value) return
    if (habilitadoConfig.value === false && !forcar) return
  }
  erroLeitura.value = ''
  if (forcar) atualizando.value = true
  else carregando.value = true
  try {
    const data = forcar
      ? await agenteGestaoService.atualizarBriefing(paramsBriefing())
      : await agenteGestaoService.obterBriefing(paramsBriefing())
    briefing.value = data
    minhasAvaliacoes.value = { ...(data?.minhasAvaliacoes || {}) }
    bloqueioAte.value = null
    briefingDisponivel.value = true
  } catch (e) {
    const status = e?.response?.status
    if (status === 429) {
      const detail = e?.response?.data?.detail
      const prox =
        (detail && typeof detail === 'object' && detail.proxima_atualizacao_em) ||
        e?.response?.data?.proxima_atualizacao_em
      if (prox) {
        bloqueioAte.value = new Date(prox)
      }
      erroLeitura.value = ''
      if (briefing.value) {
        briefingDisponivel.value = true
      }
    } else if (status === 403) {
      if (comConfigGestao.value) {
        habilitadoConfig.value = false
      }
      briefingDisponivel.value = false
    } else {
      if (!comConfigGestao.value && !briefing.value) {
        briefingDisponivel.value = false
      } else if (comConfigGestao.value) {
        erroLeitura.value = 'Não foi possível carregar o Radar operacional neste momento.'
      }
    }
  } finally {
    carregando.value = false
    atualizando.value = false
  }
}

async function forcarAtualizacao() {
  await carregarBriefing(true)
}

function acaoValida(insight) {
  const acao = insight?.acao_sugerida
  if (!acao?.rota) return false
  try {
    const alvo = router.resolve({ path: acao.rota, query: acao.query || {} })
    return Boolean(alvo?.name || alvo?.matched?.length)
  } catch {
    return false
  }
}

function irParaAcao(insight) {
  const acao = insight.acao_sugerida
  if (!acao?.rota || !acaoValida(insight)) return
  router.push({ path: acao.rota, query: acao.query || {} })
}

async function enviarAvaliacao(insightId, util) {
  if (!briefing.value?.briefingId) return
  minhasAvaliacoes.value = { ...minhasAvaliacoes.value, [insightId]: util }
  try {
    await agenteGestaoService.avaliarInsight(briefing.value.briefingId, {
      insight_id: insightId,
      util,
      comentario: ''
    })
  } catch {
  // mantém estado otimista
  }
}

onMounted(async () => {
  restaurarExpandido()
  if (comConfigGestao.value) {
    await resolverHabilitado()
    if (habilitadoConfig.value !== false) {
      await carregarBriefing(false)
    }
  } else {
    configVerificada.value = true
    await carregarBriefing(false)
  }
})

watch(
  () => props.perspectiva,
  () => {
    if (comConfigGestao.value && !deveExibir.value) return
    if (!comConfigGestao.value || deveExibir.value) {
      carregarBriefing(false)
    }
  }
)
</script>