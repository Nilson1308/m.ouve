<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <header>
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Agente IA de Gestão</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">
        Configure o Radar Operacional que orienta gestores e controladoria com leituras diárias da
        demanda, sem expor dados pessoais dos cidadãos.
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
      <div class="h-48 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
    </div>

    <template v-else-if="form">
      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
      >
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Radar proativo e e-mail consolidado</h3>

        <CardToggle
          :model-value="form.agente_ativo"
          :disabled="!podeEditar"
          titulo="Ativar Agente de Inteligência Operacional"
          descricao="Liga o Radar nas telas do backoffice e permite sínteses automáticas. Desligado, o painel não exibe o recurso."
          @update:model-value="form.agente_ativo = $event"
        />

        <div class="space-y-4" :class="form.agente_ativo ? '' : 'opacity-50 pointer-events-none select-none'">
          <CardToggle
            :model-value="form.briefing_proativo_ativo"
            :disabled="!podeEditar || !form.agente_ativo"
            titulo="Gerar Radar Operacional diário automaticamente"
            descricao="O sistema prepara a leitura do dia nos horários definidos, sem esperar abertura manual do painel."
            @update:model-value="form.briefing_proativo_ativo = $event"
          />

          <div>
            <label for="hora-radar" class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Horário de geração automática
            </label>
            <select
              id="hora-radar"
              v-model.number="form.briefing_hora_geracao"
              class="input w-full max-w-xs"
              :disabled="!podeEditar || !form.agente_ativo"
            >
              <option v-for="h in horasDia" :key="h" :value="h">{{ formatarHora(h) }}</option>
            </select>
          </div>

          <CardToggle
            :model-value="form.incluir_resumo_no_digest_email"
            :disabled="!podeEditar || !form.agente_ativo"
            titulo="Incluir síntese do Radar IA no topo dos relatórios consolidados por e-mail"
            descricao="Enriquece o relatório de atrasos de cada secretaria e o resumo enviado à Controladoria, sem substituir as tabelas de pendências."
            @update:model-value="form.incluir_resumo_no_digest_email = $event"
          />
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
        :class="form.agente_ativo ? '' : 'opacity-50 pointer-events-none'"
      >
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Sensibilidade de anomalias e gargalos</h3>

        <div>
          <label class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
            Alertar pico quando volume subir acima de (%)
          </label>
          <input
            v-model.number="form.anomalia_percentual_minimo"
            type="number"
            min="10"
            max="500"
            class="input w-full max-w-xs"
            :disabled="!podeEditar"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
            Volume mínimo de chamados para considerar anomalia
          </label>
          <input
            v-model.number="form.anomalia_volume_minimo"
            type="number"
            min="2"
            class="input w-full max-w-xs"
            :disabled="!podeEditar"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
            Alertar protocolo parado na triagem após (dias)
          </label>
          <input
            v-model.number="form.dias_parado_triagem_alerta"
            type="number"
            min="1"
            class="input w-full max-w-xs"
            :disabled="!podeEditar"
          />
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
        :class="form.agente_ativo ? '' : 'opacity-50'"
      >
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Controle de custos e copiloto (fase B)</h3>

        <div>
          <label class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
            Orçamento mensal máximo de processamento IA (tokens)
          </label>
          <input
            v-model.number="form.orcamento_tokens_mensal"
            type="number"
            min="10000"
            step="1000"
            class="input w-full max-w-sm"
            :disabled="!podeEditar"
          />
          <p class="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed max-w-prose">
            Ao atingir 80%, o painel de monitoramento exibe alerta. Ao atingir 100%, o Radar continua
            operando em modo determinístico, sem custo adicional de modelo.
          </p>
        </div>

        <div :class="form.agente_ativo ? '' : 'pointer-events-none select-none opacity-60'">
          <CardToggle
            :model-value="form.copiloto_chat_ativo"
            :disabled="!podeEditar || !form.agente_ativo"
            titulo="Copiloto conversacional no backoffice (em breve)"
            descricao="Parâmetro já salvo para a próxima fase; não altera o comportamento atual do chat com o cidadão."
            @update:model-value="form.copiloto_chat_ativo = $event"
          />

          <div
            v-if="form.copiloto_chat_ativo"
            class="mt-4"
            :class="form.copiloto_chat_ativo ? '' : 'opacity-50 pointer-events-none'"
          >
            <label class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Limite de perguntas por dia e por usuário
            </label>
            <input
              v-model.number="form.limite_perguntas_dia_por_usuario"
              type="number"
              min="1"
              class="input w-full max-w-xs"
              :disabled="!podeEditar || !form.copiloto_chat_ativo"
            />
          </div>
        </div>
      </section>

      <div
        v-if="podeEditar"
        class="flex flex-wrap gap-3 justify-end sticky bottom-4 z-10"
      >
        <button
          type="button"
          class="btn-secondary"
          :disabled="salvando || !alteracoesPendentes"
          @click="descartar"
        >
          Descartar
        </button>
        <button
          type="button"
          class="btn-primary"
          :disabled="salvando || !alteracoesPendentes"
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
import { agenteGestaoService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useRbac } from '@/composables/useRbac'
import { useAdminToast } from '@/composables/useAdminToast'

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

const { can } = useRbac()
const { mostrarToast } = useAdminToast()

const podeEditar = computed(() => can('configuracoes.editar'))

const carregando = ref(true)
const salvando = ref(false)
const form = ref(null)
const original = ref(null)

const horasDia = Array.from({ length: 24 }, (_, i) => i)

const alteracoesPendentes = computed(() => {
  if (!form.value || !original.value) return false
  return JSON.stringify(form.value) !== JSON.stringify(original.value)
})

function formatarHora(h) {
  return `${String(h).padStart(2, '0')}:00`
}

async function carregar() {
  carregando.value = true
  try {
    const data = await agenteGestaoService.obterConfiguracao()
    form.value = { ...data }
    original.value = JSON.parse(JSON.stringify(data))
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Não foi possível carregar o Agente IA.'), true)
  } finally {
    carregando.value = false
  }
}

function descartar() {
  if (original.value) {
    form.value = JSON.parse(JSON.stringify(original.value))
  }
}

async function salvar() {
  if (!form.value || !podeEditar.value) return
  salvando.value = true
  try {
    const salvo = await agenteGestaoService.salvarConfiguracao(form.value)
    form.value = { ...salvo }
    original.value = JSON.parse(JSON.stringify(salvo))
    mostrarToast('Configurações do Agente IA salvas.')
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Falha ao salvar.'), true)
  } finally {
    salvando.value = false
  }
}

onMounted(carregar)
</script>