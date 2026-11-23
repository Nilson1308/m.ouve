<template>
  <CardSecao
    titulo="Matriz de roteamento"
    subtitulo="Regras temáticas para sugerir secretarias no despacho (motor determinístico)"
    :icon="ArrowsRightLeftIcon"
  >
    <p
      v-if="!servicoId"
      class="text-sm text-gray-600 dark:text-gray-400 rounded-lg border border-dashed border-gray-300 dark:border-gray-600 p-4 bg-gray-50/80 dark:bg-gray-900/40"
    >
      Salve o serviço primeiro para configurar regras de roteamento.
    </p>

    <template v-else>
      <div
        class="mb-6 rounded-xl border border-gray-200 dark:border-gray-600 bg-white/60 dark:bg-gray-900/50 p-4 flex flex-col sm:flex-row sm:items-start gap-4"
      >
        <button
          type="button"
          role="switch"
          :aria-checked="triagemIaAtiva"
          :aria-labelledby="`triagem-ia-label-${servicoId}`"
          :disabled="!iaTriagemDisponivel"
          :class="[
            'relative inline-flex h-7 w-12 shrink-0 rounded-full border-2 border-transparent transition-colors mt-0.5',
            triagemIaAtiva && iaTriagemDisponivel ? 'bg-violet-600' : 'bg-gray-300 dark:bg-gray-600',
            !iaTriagemDisponivel ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
          ]"
          @click="alternarTriagemIa"
        >
          <span
            :class="[
              'pointer-events-none inline-block h-6 w-6 rounded-full bg-white shadow transition',
              triagemIaAtiva ? 'translate-x-5' : 'translate-x-0'
            ]"
          />
        </button>
        <div class="flex-1 min-w-0">
          <p
            :id="`triagem-ia-label-${servicoId}`"
            class="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2"
          >
            <SparklesIcon class="w-5 h-5 text-violet-600 dark:text-violet-400" />
            Sugerir unidade executora com IA (Triagem Semântica)
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 leading-relaxed">
            Analisa o relato do cidadão e o histórico do chat em segundo plano para sugerir
            secretarias na mesa de trabalho. O despacho continua exigindo confirmação manual.
          </p>
          <p
            v-if="!iaTriagemDisponivel"
            class="text-xs text-sky-800 dark:text-sky-200 mt-2 rounded-md bg-sky-50 dark:bg-sky-950/40 px-2 py-1.5 border border-sky-200/80 dark:border-sky-800/60"
          >
            A triagem por IA atua apenas nos fluxos <strong>Ouvidoria (encaminhamento)</strong> e
            <strong>Híbrido</strong>.
          </p>
          <p
            v-else-if="triagemIaAtiva"
            class="text-xs text-violet-800 dark:text-violet-200 mt-2 inline-flex items-start gap-1.5 rounded-md bg-violet-50 dark:bg-violet-950/40 px-2.5 py-1.5 border border-violet-200/80 dark:border-violet-800/60"
          >
            <span class="font-semibold uppercase tracking-wide text-[10px] text-violet-600 dark:text-violet-300 shrink-0 mt-0.5">
              IA ativa
            </span>
            <span>
              Com a IA ativa, as regras manuais abaixo são <strong>opcionais</strong> — use-as apenas para fixar
              atalhos exatos por opção do formulário.
            </span>
          </p>
        </div>
      </div>

      <div
        v-if="fluxoTramitacao === 'direto_secretaria'"
        class="mb-5 rounded-lg border border-sky-200 dark:border-sky-800 bg-sky-50/90 dark:bg-sky-950/30 px-4 py-3 text-sm text-sky-900 dark:text-sky-100"
      >
        <div class="flex gap-2">
          <InformationCircleIcon class="w-5 h-5 shrink-0 text-sky-600 dark:text-sky-400" />
          <p>
            Neste fluxo o protocolo vai direto à secretaria responsável. A matriz é mais útil em
            <strong>Ouvidoria (encaminhamento)</strong> ou <strong>Híbrido</strong>, quando a Mesa precisa sugerir executores.
          </p>
        </div>
      </div>

      <div
        v-if="opcoesCampos.length === 0"
        class="rounded-xl border border-dashed border-amber-300 dark:border-amber-700 bg-amber-50/50 dark:bg-amber-950/20 p-6 mb-6 text-center space-y-4"
      >
        <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed max-w-lg mx-auto">
          Adicione pelo menos um campo na aba <strong>Formulário &amp; IA</strong> para criar regras de roteamento
          sem risco de erro.
        </p>
        <button
          type="button"
          class="btn-primary !py-2.5 !px-5 text-sm min-h-11"
          @click="emit('ir-para-formulario')"
        >
          Ir para Formulário &amp; IA
        </button>
      </div>

      <form
        v-else
        class="rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50/60 dark:bg-gray-900/40 p-4 space-y-4 mb-6"
        @submit.prevent="criarRegra"
      >
        <h4 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <PlusCircleIcon class="w-5 h-5 text-primary-500" />
          Nova regra
        </h4>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              Campo do formulário *
            </label>
            <select
              v-if="opcoesCampos.length"
              v-model="form.chave_schema"
              class="input w-full"
              required
            >
              <option value="" disabled>Selecione…</option>
              <option v-for="c in opcoesCampos" :key="c.value" :value="c.value">
                {{ c.label }}
              </option>
            </select>
            <input
              v-else
              v-model="form.chave_schema"
              type="text"
              class="input w-full"
              placeholder="ex.: categoria"
              required
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              Valor / condição *
            </label>
            <select
              v-if="opcoesValorCondicao.length"
              v-model="form.valor_condicao"
              class="input w-full"
              required
            >
              <option value="" disabled>Selecione…</option>
              <option v-for="v in opcoesValorCondicao" :key="v" :value="v">
                {{ v }}
              </option>
            </select>
            <input
              v-else
              v-model="form.valor_condicao"
              type="text"
              class="input w-full"
              placeholder="Valor exato no protocolo"
              required
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
              Unidade sugerida *
            </label>
            <select
              v-model="form.unidade_sugerida"
              class="input w-full"
              :disabled="loadingUnidades"
              required
            >
              <option value="" disabled>
                {{ loadingUnidades ? 'Carregando unidades…' : 'Selecione a secretaria…' }}
              </option>
              <option v-for="u in unidades" :key="u.id" :value="u.id">
                {{ u.nome }}
              </option>
            </select>
          </div>
        </div>

        <p v-if="erroForm" class="text-sm text-red-600 dark:text-red-400">{{ erroForm }}</p>

        <button
          type="submit"
          class="btn-primary btn-sm"
          :disabled="salvando || loadingRegras"
        >
          {{ salvando ? 'Salvando…' : 'Adicionar regra' }}
        </button>
      </form>

      <div v-if="loadingRegras" class="text-sm text-gray-500 dark:text-gray-400 py-6 text-center">
        Carregando regras…
      </div>

      <p
        v-else-if="!regras.length"
        class="text-sm text-gray-500 dark:text-gray-400 italic py-4 text-center border border-dashed rounded-lg"
      >
        Nenhuma regra cadastrada para este serviço.
      </p>

      <div v-else class="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
        <table class="min-w-full text-sm">
          <thead class="bg-gray-100 dark:bg-gray-900/80 text-left text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400">
            <tr>
              <th class="px-4 py-3 font-semibold">Condição</th>
              <th class="px-4 py-3 font-semibold">Unidade sugerida</th>
              <th class="px-4 py-3 font-semibold w-28">Ativa</th>
              <th class="px-4 py-3 font-semibold w-24 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800/80">
            <tr v-for="regra in regras" :key="regra.id" class="hover:bg-gray-50/80 dark:hover:bg-gray-700/30">
              <td class="px-4 py-3 font-mono text-xs text-gray-800 dark:text-gray-200">
                {{ regra.chave_schema }}
                <span class="text-gray-400">=</span>
                <span class="font-semibold">{{ regra.valor_condicao }}</span>
              </td>
              <td class="px-4 py-3 text-gray-900 dark:text-white">
                {{ regra.unidade_sugerida_nome || '—' }}
              </td>
              <td class="px-4 py-3">
                <button
                  type="button"
                  role="switch"
                  :aria-checked="regra.ativo"
                  :class="[
                    'relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 border-transparent transition-colors',
                    regra.ativo ? 'bg-green-600' : 'bg-gray-300 dark:bg-gray-600',
                    atualizandoId === regra.id ? 'opacity-50' : ''
                  ]"
                  :disabled="atualizandoId === regra.id"
                  @click="alternarAtivo(regra)"
                >
                  <span
                    :class="[
                      'inline-block h-5 w-5 rounded-full bg-white shadow transition',
                      regra.ativo ? 'translate-x-5' : 'translate-x-0'
                    ]"
                  />
                </button>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  type="button"
                  class="p-2 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40"
                  title="Excluir regra"
                  :disabled="removendoId === regra.id"
                  @click="excluirRegra(regra)"
                >
                  <TrashIcon class="w-5 h-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </CardSecao>
</template>

<script setup>
import { computed, defineModel, reactive, ref, watch, onMounted } from 'vue'
import {
  ArrowsRightLeftIcon,
  InformationCircleIcon,
  PlusCircleIcon,
  SparklesIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import CardSecao from './FormBuilderCardSecao.vue'
import { matrizRoteamentoService, catalogoLookupService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

const triagemIaAtiva = defineModel('triagemIaAtiva', { type: Boolean, default: true })

const emit = defineEmits(['ir-para-formulario'])

const props = defineProps({
  servicoId: { type: String, default: '' },
  fluxoTramitacao: { type: String, default: 'direto_secretaria' },
  requisitos: { type: Array, default: () => [] }
})

const iaTriagemDisponivel = computed(
  () => props.fluxoTramitacao !== 'direto_secretaria'
)

function alternarTriagemIa() {
  if (!iaTriagemDisponivel.value) return
  triagemIaAtiva.value = !triagemIaAtiva.value
}

const regras = ref([])
const loadingRegras = ref(false)
const salvando = ref(false)
const erroForm = ref('')
const atualizandoId = ref(null)
const removendoId = ref(null)
const unidades = ref([])
const loadingUnidades = ref(false)

const form = reactive({
  chave_schema: '',
  valor_condicao: '',
  unidade_sugerida: ''
})

const opcoesCampos = computed(() =>
  (props.requisitos || [])
    .filter((r) => String(r.name || '').trim())
    .map((r) => ({
      value: r.name,
      label: r.pergunta?.trim() ? `${r.pergunta} (${r.name})` : r.name
    }))
)

const campoSelecionado = computed(() =>
  (props.requisitos || []).find((r) => r.name === form.chave_schema)
)

const opcoesValorCondicao = computed(() => {
  const campo = campoSelecionado.value
  if (!campo || campo.type !== 'select') return []
  const texto = String(campo.optionsText || '')
  return texto
    .split(/[,;|\n]/)
    .map((s) => s.trim())
    .filter(Boolean)
})

watch(
  () => form.chave_schema,
  () => {
    if (opcoesValorCondicao.value.length && !opcoesValorCondicao.value.includes(form.valor_condicao)) {
      form.valor_condicao = ''
    }
  }
)

async function carregarRegras() {
  if (!props.servicoId) return
  loadingRegras.value = true
  try {
    regras.value = await matrizRoteamentoService.listar(props.servicoId)
  } catch (e) {
    erroForm.value = getApiErrorMessage(e, 'Não foi possível carregar as regras.')
  } finally {
    loadingRegras.value = false
  }
}

async function carregarUnidades() {
  loadingUnidades.value = true
  try {
    unidades.value = await catalogoLookupService.listarUnidades()
  } catch {
    unidades.value = []
  } finally {
    loadingUnidades.value = false
  }
}

async function criarRegra() {
  erroForm.value = ''
  salvando.value = true
  try {
    const criada = await matrizRoteamentoService.criar(props.servicoId, {
      chave_schema: form.chave_schema.trim(),
      valor_condicao: form.valor_condicao.trim(),
      unidade_sugerida: form.unidade_sugerida,
      ativo: true
    })
    regras.value = [...regras.value, criada].sort((a, b) =>
      `${a.chave_schema}${a.valor_condicao}`.localeCompare(`${b.chave_schema}${b.valor_condicao}`)
    )
    form.chave_schema = ''
    form.valor_condicao = ''
    form.unidade_sugerida = ''
  } catch (e) {
    erroForm.value = getApiErrorMessage(e, 'Não foi possível criar a regra. Verifique duplicidade.')
  } finally {
    salvando.value = false
  }
}

async function alternarAtivo(regra) {
  atualizandoId.value = regra.id
  try {
    const atualizada = await matrizRoteamentoService.atualizar(props.servicoId, regra.id, {
      ativo: !regra.ativo
    })
    const idx = regras.value.findIndex((r) => r.id === regra.id)
    if (idx >= 0) regras.value[idx] = atualizada
  } catch (e) {
    erroForm.value = getApiErrorMessage(e, 'Não foi possível atualizar a regra.')
  } finally {
    atualizandoId.value = null
  }
}

async function excluirRegra(regra) {
  if (!window.confirm('Remover esta regra de roteamento?')) return
  removendoId.value = regra.id
  try {
    await matrizRoteamentoService.remover(props.servicoId, regra.id)
    regras.value = regras.value.filter((r) => r.id !== regra.id)
  } catch (e) {
    erroForm.value = getApiErrorMessage(e, 'Não foi possível excluir a regra.')
  } finally {
    removendoId.value = null
  }
}

watch(
  () => props.servicoId,
  (id) => {
    if (id) carregarRegras()
    else regras.value = []
  },
  { immediate: true }
)

onMounted(() => {
  carregarUnidades()
})
</script>