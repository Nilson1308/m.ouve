<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <header>
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Matriz de Urgência</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">
        Defina como os protocolos são classificados na abertura, quando a inteligência artificial sugere
        elevação e como agrupamentos (Super OS) impactam a prioridade nas filas.
      </p>
    </header>

    <div
      v-if="alteracoesPendentes && form"
      class="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
      role="status"
    >
      Alterações ainda não salvas. Use <strong class="font-semibold">Salvar configurações</strong>.
    </div>

    <div v-if="carregando" class="space-y-4">
      <div class="h-32 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      <div class="h-64 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
    </div>

    <template v-else-if="form">
      <CardToggle
        :model-value="form.matriz_ativa"
        :disabled="!podeEditar"
        titulo="Matriz de urgência ativa"
        descricao="Quando desligada, os protocolos mantêm apenas a urgência padrão do catálogo."
        @update:model-value="form.matriz_ativa = $event"
      />

      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm"
        :class="form.matriz_ativa ? '' : 'opacity-60'"
      >
        <h3 class="text-sm font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-4">
          Os quatro níveis de prioridade
        </h3>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <UrgenciaBadge v-for="n in niveis" :key="n" :nivel="n" size="lg" />
        </div>
        <p class="text-xs text-slate-600 dark:text-slate-400 mt-4 leading-relaxed">
          <template v-if="form.ia_urgencia_ativa">A IA pode sugerir elevação com base nos sinais cadastrados.</template>
          <template v-else>A análise por IA está desligada — apenas catálogo, regras de campo e Super OS alteram o nível.</template>
          <template v-if="form.super_os_escalonamento_ativo"> Agrupamentos elevam a urgência por volume.</template>
          <template v-if="!form.urgencia_reduz_sla"> Os prazos oficiais do catálogo não são encurtados.</template>
        </p>
      </section>

      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
        :class="blocoDesativado"
      >
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Classificação assistida por IA</h3>
        <CardToggle
          :model-value="form.ia_urgencia_ativa"
          :disabled="!podeEditar"
          titulo="Analisar relato do cidadão para identificar sinais de urgência ou risco"
          @update:model-value="form.ia_urgencia_ativa = $event"
        />
        <div
          class="space-y-3 pl-4 border-l-2 border-violet-200 dark:border-violet-800"
          :class="form.ia_urgencia_ativa ? '' : 'opacity-50 pointer-events-none'"
        >
          <p class="text-sm font-semibold text-slate-800 dark:text-slate-200">Modo de atuação</p>
          <div class="flex flex-col sm:flex-row gap-2">
            <button
              type="button"
              class="rounded-xl border px-4 py-3 text-left text-sm min-h-[44px] transition-colors focus-visible:ring-2 focus-visible:ring-primary-500"
              :class="modoSugerirClass"
              :disabled="!podeEditar || !form.ia_urgencia_ativa"
              @click="form.ia_urgencia_modo = 'sugerir'"
            >
              Apenas sugerir na Mesa (recomendado)
            </button>
            <button
              type="button"
              class="rounded-xl border px-4 py-3 text-left text-sm min-h-[44px] transition-colors focus-visible:ring-2 focus-visible:ring-amber-500"
              :class="modoAutoClass"
              :disabled="!podeEditar || !form.ia_urgencia_ativa"
              @click="form.ia_urgencia_modo = 'aplicar_automatico'"
            >
              Elevar urgência automaticamente
            </button>
          </div>
          <div v-if="form.ia_urgencia_modo === 'aplicar_automatico'" class="space-y-1">
            <label class="text-xs font-semibold text-slate-600 dark:text-slate-300">
              Confiança mínima: {{ confiancaPercentual }}%
            </label>
            <input
              v-model.number="confiancaPercentual"
              type="range"
              min="50"
              max="100"
              class="w-full max-w-xs accent-primary-600"
              :disabled="!podeEditar"
            />
          </div>
          <EditorSinais
            titulo="Sinais de urgência alta"
            dica="Ex.: prioridade legal, escola, denúncia sensível"
            :model-value="sinaisAlta"
            :disabled="!form.ia_urgencia_ativa || !podeEditar"
            @update:model-value="atualizarSinais('alta', $event)"
          />
          <EditorSinais
            titulo="Sinais de urgência crítica"
            dica="Ex.: risco à vida, falta grave de medicamento, desabamento"
            :model-value="sinaisCritica"
            :disabled="!form.ia_urgencia_ativa || !podeEditar"
            @update:model-value="atualizarSinais('critica', $event)"
          />
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-4"
        :class="blocoDesativado"
      >
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Escalonamento por volume (Super OS)</h3>
        <CardToggle
          :model-value="form.super_os_escalonamento_ativo"
          :disabled="!podeEditar"
          titulo="Elevar urgência quando vários relatos forem agrupados"
          @update:model-value="form.super_os_escalonamento_ativo = $event"
        />
        <div
          class="grid sm:grid-cols-2 gap-4"
          :class="form.super_os_escalonamento_ativo ? '' : 'opacity-50 pointer-events-none'"
        >
          <div>
            <label class="text-sm font-semibold text-slate-800 dark:text-slate-200">Limite para Alta</label>
            <input
              v-model.number="form.super_os_limite_alta"
              type="number"
              min="2"
              class="input max-w-[6rem] mt-1"
              :disabled="!podeEditar"
            />
          </div>
          <div>
            <label class="text-sm font-semibold text-slate-800 dark:text-slate-200">Limite para Crítica</label>
            <input
              v-model.number="form.super_os_limite_critica"
              type="number"
              min="3"
              class="input max-w-[6rem] mt-1"
              :disabled="!podeEditar"
            />
          </div>
          <p class="sm:col-span-2 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            Quando um mesmo incidente atingir {{ form.super_os_limite_alta }} solicitações agrupadas, sobe
            automaticamente para Alta; ao atingir {{ form.super_os_limite_critica }}, sobe para Crítica.
          </p>
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
        :class="blocoDesativado"
      >
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Impacto nos prazos e alertas</h3>
        <CardToggle
          :model-value="form.urgencia_reduz_sla"
          :disabled="!podeEditar"
          titulo="Encurtar prazo de atendimento (SLA) em protocolos Alta e Crítica"
          :descricao="
            form.urgencia_reduz_sla
              ? ''
              : 'Desligado: a urgência reordena as filas e antecipa alertas sem alterar os prazos oficiais do catálogo.'
          "
          @update:model-value="form.urgencia_reduz_sla = $event"
        />
        <div
          v-if="form.urgencia_reduz_sla"
          class="rounded-xl bg-slate-50 dark:bg-slate-800/40 p-4 space-y-3"
        >
          <div class="grid sm:grid-cols-3 gap-3">
            <div>
              <label class="text-xs font-semibold text-slate-600 dark:text-slate-300">% SLA em Alta</label>
              <input
                v-model.number="form.fator_sla_alta_percentual"
                type="number"
                min="10"
                max="95"
                class="input max-w-[6rem] mt-1"
                :disabled="!podeEditar"
              />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-600 dark:text-slate-300">% SLA em Crítica</label>
              <input
                v-model.number="form.fator_sla_critica_percentual"
                type="number"
                min="5"
                max="90"
                class="input max-w-[6rem] mt-1"
                :disabled="!podeEditar"
              />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-600 dark:text-slate-300">Piso crítica (horas)</label>
              <input
                v-model.number="form.sla_minimo_critica_horas"
                type="number"
                min="1"
                class="input max-w-[6rem] mt-1"
                :disabled="!podeEditar"
              />
            </div>
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400">{{ textoExemploSla }}</p>
        </div>
        <CardToggle
          :model-value="form.notificar_gestor_em_alta"
          :disabled="!podeEditar"
          titulo="Notificar gestores da secretaria quando um protocolo subir para Alta"
          @update:model-value="form.notificar_gestor_em_alta = $event"
        />
        <CardToggle
          :model-value="form.notificar_controladoria_em_critica"
          :disabled="!podeEditar"
          titulo="Notificar Controladoria e Ouvidoria quando um protocolo subir para Crítica"
          @update:model-value="form.notificar_controladoria_em_critica = $event"
        />
      </section>

      <div class="flex justify-end">
        <button
          type="button"
          class="btn-primary min-h-[44px] px-6 focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
          :disabled="salvando || !podeEditar"
          @click="salvar"
        >
          {{ salvando ? 'Salvando…' : 'Salvar configurações' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import UrgenciaBadge from '@/components/backoffice/common/UrgenciaBadge.vue'
import { matrizUrgenciaService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useRbac } from '@/composables/useRbac'
import { useAdminToast } from '@/composables/useAdminToast'

const niveis = ['baixa', 'normal', 'alta', 'critica']

const CardToggle = defineComponent({
  name: 'CardToggle',
  props: {
    modelValue: { type: Boolean, required: true },
    titulo: { type: String, required: true },
    descricao: { type: String, default: '' },
    disabled: { type: Boolean, default: false }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'flex items-start gap-3' }, [
        h(
          'button',
          {
            type: 'button',
            role: 'switch',
            'aria-checked': props.modelValue,
            disabled: props.disabled,
            class: [
              'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors mt-0.5 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400',
              props.modelValue ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
            ],
            onClick: () => !props.disabled && emit('update:modelValue', !props.modelValue)
          },
          [
            h('span', {
              class: [
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition',
                props.modelValue ? 'translate-x-5' : 'translate-x-0'
              ]
            })
          ]
        ),
        h('div', { class: 'flex-1 min-w-0' }, [
          h('p', { class: 'text-sm font-semibold text-slate-900 dark:text-white' }, props.titulo),
          props.descricao
            ? h('p', { class: 'text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed' }, props.descricao)
            : null
        ])
      ])
  }
})

const EditorSinais = defineComponent({
  name: 'EditorSinais',
  props: {
    titulo: String,
    dica: String,
    modelValue: { type: Array, default: () => [] },
    disabled: Boolean
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const novo = ref('')
    return () =>
      h('div', { class: 'space-y-2 mt-4' }, [
        h('p', { class: 'text-sm font-semibold text-slate-800 dark:text-slate-200' }, props.titulo),
        h('p', { class: 'text-xs text-slate-500 dark:text-slate-400' }, props.dica),
        h(
          'div',
          { class: 'flex flex-wrap gap-2' },
          (props.modelValue || []).map((item, i) =>
            h(
              'span',
              {
                key: `${item}-${i}`,
                class:
                  'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700'
              },
              [
                item,
                h(
                  'button',
                  {
                    type: 'button',
                    disabled: props.disabled,
                    class:
                      'text-slate-500 hover:text-red-600 dark:hover:text-red-400 focus-visible:ring-2 focus-visible:ring-red-400 rounded px-1',
                    onClick: () =>
                      emit(
                        'update:modelValue',
                        props.modelValue.filter((_, idx) => idx !== i)
                      )
                  },
                  '×'
                )
              ]
            )
          )
        ),
        h('div', { class: 'flex gap-2' }, [
          h('input', {
            class:
              'input flex-1 text-sm focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400',
            value: novo.value,
            disabled: props.disabled,
            placeholder: 'Novo sinal…',
            onInput: (e) => {
              novo.value = e.target.value
            },
            onKeydown: (e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                const t = novo.value.trim()
                if (t && !props.modelValue.includes(t)) {
                  emit('update:modelValue', [...props.modelValue, t])
                  novo.value = ''
                }
              }
            }
          }),
          h(
            'button',
            {
              type: 'button',
              class: 'btn-secondary text-sm min-h-[40px]',
              disabled: props.disabled,
              onClick: () => {
                const t = novo.value.trim()
                if (t && !props.modelValue.includes(t)) {
                  emit('update:modelValue', [...props.modelValue, t])
                  novo.value = ''
                }
              }
            },
            'Adicionar'
          )
        ])
      ])
  }
})

const { can } = useRbac()
const { mostrarToast } = useAdminToast()
const podeEditar = computed(() => can('configuracoes.editar'))

const carregando = ref(true)
const salvando = ref(false)
const form = ref(null)
const baselineJson = ref('')

const blocoDesativado = computed(() => (form.value?.matriz_ativa ? '' : 'opacity-50 pointer-events-none select-none'))

const confiancaPercentual = computed({
  get: () => Math.round((form.value?.ia_confianca_minima ?? 0.85) * 100),
  set: (v) => {
    if (form.value) form.value.ia_confianca_minima = Math.min(1, Math.max(0.5, Number(v) / 100))
  }
})

const modoSugerirClass = computed(() =>
  form.value?.ia_urgencia_modo === 'sugerir'
    ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/40 text-primary-900 dark:text-primary-100'
    : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60 active:bg-slate-100 dark:active:bg-slate-700/50'
)

const modoAutoClass = computed(() =>
  form.value?.ia_urgencia_modo === 'aplicar_automatico'
    ? 'border-amber-500 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-100'
    : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60 active:bg-slate-100 dark:active:bg-slate-700/50'
)

const sinaisAlta = computed(() => extrairSinais('alta'))
const sinaisCritica = computed(() => extrairSinais('critica'))

function extrairSinais(nivel) {
  const bloco = form.value?.criterios_ia_customizados?.[nivel] || {}
  const s = bloco.sinais || bloco.criterios || []
  return Array.isArray(s) ? [...s] : []
}

const textoExemploSla = computed(() => {
  const dias = 10
  const alta =
    (dias * 24 * (form.value?.fator_sla_alta_percentual || 50)) / 100 / 24
  const crit = Math.max(
    (dias * 24 * (form.value?.fator_sla_critica_percentual || 25)) / 100 / 24,
    (form.value?.sla_minimo_critica_horas || 24) / 24
  )
  return `Exemplo: serviço com prazo de ${dias} dias → Alta ~${alta.toFixed(1)} dias; Crítica ~${crit.toFixed(1)} dias (com piso mínimo).`
})

const alteracoesPendentes = computed(() => {
  if (!form.value) return false
  const { atualizado_em, ...rest } = form.value
  return JSON.stringify(rest) !== baselineJson.value
})

function atualizarSinais(nivel, lista) {
  if (!form.value) return
  const crit = { ...(form.value.criterios_ia_customizados || {}) }
  crit[nivel] = { ...(crit[nivel] || {}), sinais: lista }
  form.value.criterios_ia_customizados = crit
}

function snapshotForm() {
  if (!form.value) return ''
  const { atualizado_em, ...rest } = form.value
  return JSON.stringify(rest)
}

async function carregar() {
  carregando.value = true
  try {
    const data = await matrizUrgenciaService.obterConfiguracao()
    form.value = {
      ...data,
      criterios_ia_customizados: data.criterios_ia_customizados || {
        alta: { sinais: [] },
        critica: { sinais: [] }
      }
    }
    baselineJson.value = snapshotForm()
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível carregar a matriz.'), true)
  } finally {
    carregando.value = false
  }
}

async function salvar() {
  if (!form.value || !podeEditar.value) return
  salvando.value = true
  try {
    const { atualizado_em, ...patch } = form.value
    const data = await matrizUrgenciaService.salvarConfiguracao(patch)
    form.value = data
    baselineJson.value = snapshotForm()
    mostrarToast('Matriz de urgência salva.')
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Falha ao salvar.'), true)
  } finally {
    salvando.value = false
  }
}

onMounted(carregar)
</script>