<template>
  <div class="max-w-3xl mx-auto space-y-8">
  <div>
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">SLA & Cobrança</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">
        Parametrize cobrança do cidadão, régua de escalonamento e relatório digest por e-mail.
      </p>
    </div>

    <div v-if="carregando" class="space-y-4">
      <div class="h-32 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      <div class="h-32 rounded-xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
    </div>

    <template v-else-if="form">
      <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5">
        <h3 class="text-sm font-bold uppercase tracking-wide text-slate-500">Cobrança do cidadão</h3>

        <label class="flex items-center justify-between gap-4 cursor-pointer min-h-[44px]">
          <span class="text-sm font-medium text-slate-800 dark:text-slate-200">Ativar cobrança pelo PWA</span>
          <input v-model="form.cobranca_cidadao_ativa" type="checkbox" class="w-5 h-5 rounded text-primary-600" />
        </label>

        <div>
          <label for="cooldown-horas" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Intervalo entre cobranças (horas)
          </label>
          <input
            id="cooldown-horas"
            v-model.number="form.cooldown_cobranca_horas"
            type="number"
            min="1"
            class="input w-full max-w-xs"
          />
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5">
        <h3 class="text-sm font-bold uppercase tracking-wide text-slate-500">Régua de escalonamento</h3>

        <div>
          <label for="alerta-pct" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Alerta preventivo (% do prazo, 50–99)
          </label>
          <input
            id="alerta-pct"
            v-model.number="form.alerta_preventivo_percentual"
            type="number"
            min="50"
            max="99"
            class="input w-full max-w-xs"
          />
        </div>

        <div>
          <label for="escalonamento-dias" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Escalonar à controladoria após (dias de atraso)
          </label>
          <input
            id="escalonamento-dias"
            v-model.number="form.escalonamento_controladoria_dias"
            type="number"
            min="0"
            class="input w-full max-w-xs"
          />
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm space-y-5">
        <h3 class="text-sm font-bold uppercase tracking-wide text-slate-500">Relatório digest por e-mail</h3>

        <label class="flex items-center justify-between gap-4 cursor-pointer min-h-[44px]">
          <span class="text-sm font-medium text-slate-800 dark:text-slate-200">Enviar digest automático</span>
          <input v-model="form.digest_email_ativo" type="checkbox" class="w-5 h-5 rounded text-primary-600" />
        </label>

        <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 px-3 py-2.5">
          Os gestores ativos de cada secretaria recebem automaticamente o resumo dos próprios protocolos
          atrasados. Use o campo abaixo apenas para o relatório consolidado geral (Controladoria / Ouvidoria).
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="digest-periodicidade" class="block text-sm font-medium mb-1">Periodicidade</label>
            <select id="digest-periodicidade" v-model="form.digest_periodicidade" class="input w-full">
              <option value="diario">Diário</option>
              <option value="semanal">Semanal</option>
            </select>
          </div>
          <div>
            <label for="digest-hora" class="block text-sm font-medium mb-1">Hora de envio (0–23)</label>
            <input
              id="digest-hora"
              v-model.number="form.digest_hora_envio"
              type="number"
              min="0"
              max="23"
              class="input w-full"
            />
          </div>
        </div>

        <div>
          <label for="email-chip" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            E-mails da controladoria
          </label>
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
              @keydown.enter.prevent="adicionarEmail"
            />
            <button type="button" class="btn-secondary shrink-0 min-h-[44px]" @click="adicionarEmail">
              Adicionar
            </button>
          </div>
          <p v-if="erroEmail" class="text-xs text-red-600 mt-1">{{ erroEmail }}</p>
        </div>
      </section>

      <p v-if="erroSalvar" class="text-sm text-red-600">{{ erroSalvar }}</p>

      <div class="flex justify-end">
        <button
          type="button"
          class="btn-primary min-h-[44px] px-6"
          :disabled="salvando || !podeEditar"
          @click="salvar"
        >
          {{ salvando ? 'Salvando…' : 'Salvar configurações' }}
        </button>
      </div>
      <p v-if="!podeEditar" class="text-xs text-slate-500 text-right">
        Você possui apenas leitura nesta seção.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { slaCobrancaService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useRbac } from '@/composables/useRbac'
import { useAdminToast } from '@/composables/useAdminToast'

const { can } = useRbac()
const { mostrarToast } = useAdminToast()

const carregando = ref(true)
const salvando = ref(false)
const form = ref(null)
const emailInput = ref('')
const erroEmail = ref('')
const erroSalvar = ref('')
const podeEditar = computed(() => can('configuracoes.editar'))

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
  } catch (e) {
    mostrarToast(getApiErrorMessage(e, 'Erro ao carregar configuração SLA.'), true)
  } finally {
    carregando.value = false
  }
}

function emailValido(val) {
  return typeof val === 'string' && val.includes('@') && val.trim().length >= 5
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
  if (!podeEditar.value) return
  salvando.value = true
  erroSalvar.value = ''
  try {
    const payload = { ...form.value }
    delete payload.atualizado_em
    form.value = await slaCobrancaService.salvarConfiguracao(payload)
    mostrarToast('Configurações de SLA salvas.', false)
  } catch (e) {
    erroSalvar.value = getApiErrorMessage(e, 'Erro ao salvar.')
    mostrarToast(erroSalvar.value, true)
  } finally {
    salvando.value = false
  }
}
</script>