<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <header>
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">SLA, Cobrança e Alertas</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">
        Defina quando o cidadão pode cobrar retorno, como funcionam os alertas de prazo e quem recebe
        os relatórios consolidados de atraso.
      </p>
    </header>

    <div
      v-if="alteracoesPendentes && form"
      class="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
      role="status"
    >
      Você alterou parâmetros que ainda não foram salvos. Clique em
      <strong class="font-semibold">Salvar configurações</strong> para aplicar no sistema.
    </div>

    <div v-if="carregando" class="space-y-4">
      <div class="h-40 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      <div class="h-48 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      <div class="h-56 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
    </div>

    <template v-else-if="form">
      <!-- Card 1 — Cobrança -->
      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
      >
        <div class="flex items-start gap-3">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300"
          >
            <MegaphoneIcon class="h-5 w-5" aria-hidden="true" />
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="text-base font-bold text-slate-900 dark:text-white">Cobrança pelo cidadão</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Botão no aplicativo/portal do cidadão após o prazo vencer
            </p>
          </div>
        </div>

        <CardToggle
          :model-value="form.cobranca_cidadao_ativa"
          :disabled="!podeEditar"
          titulo="Permitir que o cidadão cobre retorno em protocolos atrasados"
          descricao="Exibe o botão «Cobrar retorno» no aplicativo/portal apenas depois que o prazo (SLA) do protocolo vencer. Nunca aparece enquanto o pedido estiver dentro do prazo."
          @update:model-value="form.cobranca_cidadao_ativa = $event"
        />

        <div
          class="space-y-2 transition-opacity duration-200"
          :class="form.cobranca_cidadao_ativa ? '' : 'opacity-50 pointer-events-none select-none'"
        >
          <label for="cooldown-horas" class="block text-sm font-semibold text-slate-800 dark:text-slate-200">
            Intervalo mínimo entre cobranças (horas)
          </label>
          <input
            id="cooldown-horas"
            v-model.number="form.cooldown_cobranca_horas"
            type="number"
            min="1"
            class="input w-full max-w-xs"
            :disabled="!form.cobranca_cidadao_ativa || !podeEditar"
          />
          <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed max-w-prose">
            Proteção anti-spam: após enviar uma cobrança, o cidadão precisa aguardar
            {{ cooldownHorasValido }}h (≈ {{ textoCooldownLegivel }}) para registrar uma nova cobrança
            no mesmo protocolo.
          </p>
          <p v-if="errosCampos.cooldown" class="text-xs text-red-600 dark:text-red-400">
            {{ errosCampos.cooldown }}
          </p>
        </div>
      </section>

      <!-- Card 2 — Régua -->
      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
      >
        <div class="flex items-start gap-3">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-100 text-sky-700 dark:bg-sky-950/50 dark:text-sky-300"
          >
            <ShieldCheckIcon class="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">
              Régua automática de escalonamento
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Avisos internos conforme o prazo do protocolo avança
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label for="alerta-pct" class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Aviso preventivo ao setor (% do prazo consumido)
            </label>
            <input
              id="alerta-pct"
              v-model.number="form.alerta_preventivo_percentual"
              type="number"
              min="50"
              max="99"
              class="input w-full max-w-[7rem] !py-2.5 !text-sm tabular-nums"
              :disabled="!podeEditar"
            />
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
              Notifica internamente a secretaria antes do vencimento. Ex.: em um serviço com prazo de
              {{ exemploPreventivo.diasPrazo }} dias, o aviso dispara no
              <strong class="font-semibold text-slate-800 dark:text-slate-200">{{ exemploPreventivo.dia }}º dia</strong>.
            </p>
            <p v-if="errosCampos.alerta" class="text-xs text-red-600 mt-1">{{ errosCampos.alerta }}</p>
          </div>

          <div>
            <label for="escalonamento-dias" class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
              Escalonar para a Controladoria após (dias de atraso)
            </label>
            <input
              id="escalonamento-dias"
              v-model.number="form.escalonamento_controladoria_dias"
              type="number"
              min="1"
              class="input w-full max-w-[7rem] !py-2.5 !text-sm tabular-nums"
              :disabled="!podeEditar"
            />
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
              Protocolos vencidos há
              <strong class="font-semibold">{{ diasEscalonamentoValido }}</strong>
              dia(s) — ou qualquer protocolo vencido que já tenha recebido cobrança do cidadão — são
              destacados no painel e notificados à Controladoria/Ouvidoria.
            </p>
            <p v-if="errosCampos.escalonamento" class="text-xs text-red-600 mt-1">
              {{ errosCampos.escalonamento }}
            </p>
          </div>
        </div>

        <!-- Prévia da régua -->
        <div
          class="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/90 dark:bg-slate-800/40 p-4 sm:p-5"
          aria-label="Prévia da régua de SLA"
        >
          <p class="text-[11px] font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-5">
            Prévia da régua (exemplo de um protocolo)
          </p>

          <!-- Mobile: lista vertical -->
          <ol class="space-y-0 sm:hidden">
            <li
              v-for="(marco, idx) in marcosRegua"
              :key="'m-' + marco.id"
              class="relative flex gap-3 pb-5 last:pb-0"
            >
              <div class="flex flex-col items-center shrink-0 w-9">
                <span
                  class="flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold shadow-sm ring-2 ring-white dark:ring-slate-800"
                  :class="marco.cor"
                >
                  {{ idx + 1 }}
                </span>
                <span
                  v-if="idx < marcosRegua.length - 1"
                  class="flex-1 w-0.5 min-h-[1.25rem] mt-1 bg-slate-300 dark:bg-slate-600"
                  aria-hidden="true"
                />
              </div>
              <div class="pt-1.5 min-w-0 flex-1">
                <p class="text-sm font-semibold text-slate-900 dark:text-white leading-snug">
                  {{ marco.titulo }}
                </p>
                <p class="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                  {{ marco.descricao }}
                </p>
              </div>
            </li>
          </ol>

          <!-- Desktop: trilha horizontal -->
          <div class="hidden sm:block relative pt-1">
            <div
              class="absolute left-[calc(12.5%-4px)] right-[calc(12.5%-4px)] top-[1.125rem] h-0.5 bg-slate-300 dark:bg-slate-600"
              aria-hidden="true"
            />
            <ol class="grid grid-cols-4 gap-3 relative">
              <li
                v-for="(marco, idx) in marcosRegua"
                :key="'d-' + marco.id"
                class="flex flex-col items-center text-center px-1"
              >
                <span
                  class="relative z-[1] flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold shadow-sm ring-4 ring-slate-50 dark:ring-slate-800/90"
                  :class="marco.cor"
                >
                  {{ idx + 1 }}
                </span>
                <div class="mt-3 w-full min-h-[3.25rem]">
                  <p class="text-xs font-semibold text-slate-900 dark:text-white leading-snug px-0.5">
                    {{ marco.titulo }}
                  </p>
                  <p class="text-[11px] text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">
                    {{ marco.descricao }}
                  </p>
                </div>
              </li>
            </ol>
          </div>
        </div>
      </section>

      <!-- Card 3 — E-mail -->
      <section
        class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5"
      >
        <div class="flex items-start gap-3">
          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
          >
            <EnvelopeIcon class="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">
              Relatório consolidado de atrasos por e-mail
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Um único e-mail com todos os protocolos vencidos
            </p>
          </div>
        </div>

        <CardToggle
          :model-value="form.digest_email_ativo"
          :disabled="!podeEditar"
          titulo="Enviar resumo automático de protocolos em atraso por e-mail"
          descricao="Agrupa todos os protocolos vencidos em um único relatório consolidado por e-mail (evita envio de múltiplos e-mails individuais por protocolo)."
          @update:model-value="form.digest_email_ativo = $event"
        />

        <div
          class="rounded-xl border border-primary-200/80 dark:border-primary-800/60 bg-primary-50/50 dark:bg-primary-950/20 p-4 space-y-3"
        >
          <p class="text-sm font-semibold text-slate-900 dark:text-white">Quem recebe este relatório?</p>
          <div class="flex gap-3">
            <span
              class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white dark:bg-slate-800 text-primary-600 dark:text-primary-400 border border-primary-200/60 dark:border-primary-700/50"
            >
              <BuildingOffice2Icon class="h-4 w-4" aria-hidden="true" />
            </span>
            <div class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
              <p class="font-semibold text-slate-900 dark:text-white">Gestores de cada Secretaria (automático)</p>
              <p class="mt-0.5">
                Todo gestor/responsável ativo vinculado a uma secretaria recebe automaticamente apenas a
                lista de atrasos da própria pasta — não é preciso cadastrar aqui.
              </p>
            </div>
          </div>
          <div class="flex gap-3">
            <span
              class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white dark:bg-slate-800 text-amber-600 dark:text-amber-400 border border-amber-200/60 dark:border-amber-700/50"
            >
              <ChartBarSquareIcon class="h-4 w-4" aria-hidden="true" />
            </span>
            <div class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
              <p class="font-semibold text-slate-900 dark:text-white">Resumo executivo geral (campo abaixo)</p>
              <p class="mt-0.5">
                Recebe o panorama completo de toda a prefeitura (ranking de secretarias em atraso + total de
                cobranças de cidadãos). Ideal para Controladoria e Ouvidoria.
              </p>
            </div>
          </div>
        </div>

        <div
          class="space-y-4 transition-opacity duration-200"
          :class="form.digest_email_ativo ? '' : 'opacity-50 pointer-events-none select-none'"
        >
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="digest-periodicidade" class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
                Periodicidade
              </label>
              <select
                id="digest-periodicidade"
                v-model="form.digest_periodicidade"
                class="input w-full"
                :disabled="!form.digest_email_ativo || !podeEditar"
              >
                <option value="diario">Diário</option>
                <option value="semanal">Semanal</option>
              </select>
            </div>
            <div>
              <label for="digest-hora" class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-1">
                Horário de envio
              </label>
              <select
                id="digest-hora"
                v-model.number="form.digest_hora_envio"
                class="input w-full"
                :disabled="!form.digest_email_ativo || !podeEditar"
              >
                <option v-for="h in horasOpcoes" :key="h" :value="h">
                  {{ formatarHoraOpcao(h) }}
                </option>
              </select>
            </div>
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400">
            {{ textoProximoEnvio }}
          </p>
          <p v-if="errosCampos.hora" class="text-xs text-red-600">{{ errosCampos.hora }}</p>

          <div>
            <label for="email-chip" class="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-2">
              Destinatários do resumo executivo geral (Controladoria / Ouvidoria)
            </label>
            <p class="text-xs text-slate-600 dark:text-slate-400 mb-3 leading-relaxed">
              Digite um e-mail e clique em Adicionar (ou pressione Enter). Se ficar vazio, apenas os gestores
              das secretarias receberão seus resumos individuais.
            </p>
            <div class="flex flex-wrap gap-2 mb-2">
              <span
                v-for="(email, idx) in form.emails_controladoria"
                :key="email + idx"
                class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/40 text-primary-900 dark:text-primary-100"
              >
                {{ email }}
                <button
                  type="button"
                  class="p-0.5 rounded-full hover:bg-primary-200 dark:hover:bg-primary-800"
                  :aria-label="`Remover ${email}`"
                  :disabled="!form.digest_email_ativo || !podeEditar"
                  @click="removerEmail(idx)"
                >
                  ×
                </button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                id="email-chip"
                v-model="emailInput"
                type="email"
                class="input flex-1"
                placeholder="controladoria@municipio.gov.br"
                :disabled="!form.digest_email_ativo || !podeEditar"
                @keydown.enter.prevent="adicionarEmail"
              />
              <button
                type="button"
                class="btn-secondary shrink-0 min-h-[44px]"
                :disabled="!form.digest_email_ativo || !podeEditar"
                @click="adicionarEmail"
              >
                Adicionar
              </button>
            </div>
            <p v-if="erroEmail" class="text-xs text-red-600 mt-1">{{ erroEmail }}</p>
          </div>
        </div>
      </section>

      <p v-if="erroSalvar" class="text-sm text-red-600 dark:text-red-400">{{ erroSalvar }}</p>

      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3 pt-2">
        <p v-if="!podeEditar" class="text-xs text-slate-500 sm:mr-auto">
          Você possui apenas leitura nesta seção.
        </p>
        <button
          type="button"
          class="btn-primary min-h-[44px] px-6 w-full sm:w-auto"
          :disabled="salvando || !podeEditar || !formularioValido"
          @click="salvar"
        >
          {{ salvando ? 'Salvando…' : 'Salvar configurações' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref, watch } from 'vue'
import {
  MegaphoneIcon,
  ShieldCheckIcon,
  EnvelopeIcon,
  BuildingOffice2Icon,
  ChartBarSquareIcon
} from '@heroicons/vue/24/outline'
import { slaCobrancaService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useRbac } from '@/composables/useRbac'
import { useAdminToast } from '@/composables/useAdminToast'

/** Toggle padrão backoffice (mesmo padrão visual de ModalEquipamento). */
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
              'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors mt-0.5 disabled:opacity-50 disabled:cursor-not-allowed',
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

const carregando = ref(true)
const salvando = ref(false)
const form = ref(null)
const baselineJson = ref('')
const emailInput = ref('')
const erroEmail = ref('')
const erroSalvar = ref('')
const podeEditar = computed(() => can('configuracoes.editar'))

const horasOpcoes = Array.from({ length: 24 }, (_, i) => i)

function snapshotForm() {
  if (!form.value) return ''
  const { atualizado_em, ...rest } = form.value
  return JSON.stringify(rest)
}

const alteracoesPendentes = computed(() => {
  if (!form.value || !baselineJson.value) return false
  return snapshotForm() !== baselineJson.value
})

function clampInt(val, fallback, min, max) {
  const n = Number(val)
  if (!Number.isFinite(n)) return fallback
  return Math.min(max, Math.max(min, Math.round(n)))
}

const cooldownHorasValido = computed(() =>
  clampInt(form.value?.cooldown_cobranca_horas, 48, 1, 9999)
)

const diasEscalonamentoValido = computed(() =>
  clampInt(form.value?.escalonamento_controladoria_dias, 3, 1, 9999)
)

const alertaPercentualValido = computed(() =>
  clampInt(form.value?.alerta_preventivo_percentual, 80, 50, 99)
)

function formatCooldownLegivel(horas) {
  const h = Math.max(1, Number(horas) || 1)
  if (h < 24) return `${h} hora(s)`
  const dias = Math.floor(h / 24)
  const rest = h % 24
  if (rest === 0) return `${dias} dia(s)`
  return `${dias} dia(s) e ${rest}h`
}

const textoCooldownLegivel = computed(() => formatCooldownLegivel(cooldownHorasValido.value))

const exemploPreventivo = computed(() => {
  const diasPrazo = 10
  const pct = alertaPercentualValido.value
  const dia = Math.round((diasPrazo * pct) / 100)
  return { diasPrazo, dia, pct }
})

function formatarHoraOpcao(h) {
  return `${String(h).padStart(2, '0')}:00`
}

const textoProximoEnvio = computed(() => {
  if (!form.value?.digest_email_ativo) {
    return 'Relatório automático desligado — nenhum envio agendado.'
  }
  const h = clampInt(form.value.digest_hora_envio, 8, 0, 23)
  const hora = formatarHoraOpcao(h)
  if (form.value.digest_periodicidade === 'semanal') {
    return `Próximo padrão de envio: Semanal (segundas-feiras) às ${hora}.`
  }
  return `Próximo padrão de envio: Diariamente às ${hora}.`
})

const marcosRegua = computed(() => {
  const pct = alertaPercentualValido.value
  const dias = diasEscalonamentoValido.value
  const cobrancaAtiva = Boolean(form.value?.cobranca_cidadao_ativa)
  const sufixoCobranca = cobrancaAtiva ? '' : ' (desativada)'

  return [
    {
      id: 'abertura',
      titulo: 'Abertura',
      descricao: 'Prazo iniciado',
      cor: 'bg-slate-400 text-white'
    },
    {
      id: 'preventivo',
      titulo: `${pct}% do prazo`,
      descricao: 'Aviso preventivo à secretaria',
      cor: 'bg-sky-500 text-white'
    },
    {
      id: 'vencido',
      titulo: '100% (Vencido)',
      descricao: `Alerta ao gestor da pasta + libera cobrança do cidadão${sufixoCobranca}`,
      cor: 'bg-amber-500 text-white'
    },
    {
      id: 'controladoria',
      titulo: `+${dias} dias (ou cobrança)`,
      descricao: 'Escalonado à Controladoria',
      cor: 'bg-red-500 text-white'
    }
  ]
})

const errosCampos = computed(() => {
  const out = {}
  if (!form.value) return out
  const pct = Number(form.value.alerta_preventivo_percentual)
  if (!Number.isFinite(pct) || pct < 50 || pct > 99) {
    out.alerta = 'Informe um percentual entre 50 e 99.'
  }
  const cd = Number(form.value.cooldown_cobranca_horas)
  if (!Number.isFinite(cd) || cd < 1) {
    out.cooldown = 'O intervalo deve ser de pelo menos 1 hora.'
  }
  const esc = Number(form.value.escalonamento_controladoria_dias)
  if (!Number.isFinite(esc) || esc < 1) {
    out.escalonamento = 'Informe pelo menos 1 dia de atraso.'
  }
  const hora = Number(form.value.digest_hora_envio)
  if (!Number.isFinite(hora) || hora < 0 || hora > 23) {
    out.hora = 'Escolha um horário entre 00:00 e 23:00.'
  }
  return out
})

const formularioValido = computed(() => Object.keys(errosCampos.value).length === 0)

onMounted(() => {
  carregar()
})

async function carregar() {
  carregando.value = true
  try {
    form.value = await slaCobrancaService.obterConfiguracao()
    if (!Array.isArray(form.value.emails_controladoria)) {
      form.value.emails_controladoria = []
    }
    baselineJson.value = snapshotForm()
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Erro ao carregar configuração SLA.'), true)
  } finally {
    carregando.value = false
  }
}

function emailValido(val) {
  return typeof val === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim())
}

function adicionarEmail() {
  erroEmail.value = ''
  const e = emailInput.value.trim().toLowerCase()
  if (!emailValido(e)) {
    erroEmail.value = 'Informe um e-mail válido.'
    return
  }
  if (form.value.emails_controladoria.includes(e)) {
    erroEmail.value = 'E-mail já adicionado.'
    return
  }
  form.value.emails_controladoria.push(e)
  emailInput.value = ''
}

function removerEmail(idx) {
  form.value.emails_controladoria.splice(idx, 1)
}

async function salvar() {
  if (!podeEditar.value || !formularioValido.value) {
    erroSalvar.value = 'Corrija os campos destacados antes de salvar.'
    return
  }
  salvando.value = true
  erroSalvar.value = ''
  try {
    const payload = { ...form.value }
    delete payload.atualizado_em
    form.value = await slaCobrancaService.salvarConfiguracao(payload)
    baselineJson.value = snapshotForm()
    mostrarToast('Configurações salvas com sucesso. A régua e os relatórios usarão estes parâmetros.', false)
  } catch (e) {
    erroSalvar.value = getApiErrorMessage(e, 'Erro ao salvar.')
    mostrarToast(erroSalvar.value, true)
  } finally {
    salvando.value = false
  }
}

watch(
  () => form.value?.digest_email_ativo,
  (ativo) => {
    if (!form.value) return
    if (!ativo) erroEmail.value = ''
  }
)
</script>