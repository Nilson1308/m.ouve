<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <header>
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Abertura no Aplicativo do Cidadão</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">
        Defina como as pessoas iniciam uma nova solicitação no aplicativo. A mudança vale na hora, sem reinstalar o app.
      </p>
    </header>

    <div v-if="carregando" class="space-y-4" role="status" aria-live="polite">
      <div class="h-32 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
      <div class="h-32 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
    </div>

    <fieldset v-else class="space-y-4 border-0 p-0 m-0">
      <legend class="sr-only">Modo de abertura no PWA</legend>

      <label
        v-for="opcao in opcoes"
        :key="opcao.valor"
        class="block cursor-pointer rounded-2xl border p-5 transition-colors min-h-[44px]"
        :class="cardClasse(opcao.valor)"
      >
        <input
          v-model="modoSelecionado"
          type="radio"
          name="modo_abertura_pwa"
          class="sr-only"
          :value="opcao.valor"
          :disabled="!podeEditar || salvando"
        />
        <span class="flex items-start gap-3">
          <span
            class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2"
            :class="
              modoSelecionado === opcao.valor
                ? 'border-primary-600 bg-primary-600 dark:border-primary-400'
                : 'border-slate-300 dark:border-slate-600'
            "
            aria-hidden="true"
          >
            <span
              v-if="modoSelecionado === opcao.valor"
              class="h-2 w-2 rounded-full bg-white"
            />
          </span>
          <span class="min-w-0">
            <span class="block text-base font-bold text-slate-900 dark:text-white">
              {{ opcao.titulo }}
              <span
                v-if="opcao.recomendado"
                class="ml-2 text-xs font-semibold text-primary-700 dark:text-primary-300"
              >
                (Recomendado)
              </span>
            </span>
            <span class="mt-1 block text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              {{ opcao.descricao }}
            </span>
          </span>
        </span>
      </label>
    </fieldset>

    <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed border-l-2 border-slate-200 dark:border-slate-700 pl-3">
      A alteração entra em vigor imediatamente no aplicativo do cidadão, sem necessidade de reinstalação.
      Categorias com apenas 1 serviço publicado abrem o atendimento direto.
    </p>

    <div v-if="erro" class="text-sm text-red-600 dark:text-red-400" role="alert">{{ erro }}</div>

    <button
      v-if="podeEditar"
      type="button"
      class="btn-primary min-h-[44px] px-6 disabled:opacity-50"
      :disabled="salvando || !alterado"
      @click="salvar"
    >
      {{ salvando ? 'Salvando...' : 'Salvar preferência' }}
    </button>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { atendimentoPwaService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useRbac } from '@/composables/useRbac'
import { useAdminToast } from '@/composables/useAdminToast'

const { can } = useRbac()
const { mostrarToast } = useAdminToast()

const podeEditar = computed(() => can('configuracoes.editar'))

const opcoes = [
  {
    valor: 'hibrido',
    titulo: 'Modo Híbrido',
    recomendado: true,
    descricao:
      'Oferece o Assistente IA em destaque e também a lista de serviços por categoria para o cidadão escolher como prefere abrir.'
  },
  {
    valor: 'chat_ia',
    titulo: 'Somente Assistente IA',
    recomendado: false,
    descricao: 'O cidadão entra direto na conversa e a IA identifica o serviço automaticamente.'
  },
  {
    valor: 'catalogo_guiado',
    titulo: 'Catálogo Guiado (Lista de Serviços)',
    recomendado: false,
    descricao: 'O cidadão escolhe obrigatoriamente o serviço na lista antes de iniciar a coleta.'
  }
]

const carregando = ref(true)
const salvando = ref(false)
const modoSelecionado = ref('hibrido')
const modoPersistido = ref('hibrido')
const erro = ref('')

const alterado = computed(() => modoSelecionado.value !== modoPersistido.value)

function cardClasse(valor) {
  const ativo = modoSelecionado.value === valor
  return ativo
    ? 'border-primary-500 bg-primary-50/80 dark:bg-primary-950/30 ring-1 ring-primary-500/40 dark:ring-primary-500/50'
    : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800/80'
}

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const data = await atendimentoPwaService.obter()
    const modo = data?.modo_abertura_pwa || 'hibrido'
    modoSelecionado.value = modo
    modoPersistido.value = modo
  } catch (e) {
    erro.value = getApiErrorMessage(e, 'Não foi possível carregar a configuração.')
  } finally {
    carregando.value = false
  }
}

async function salvar() {
  if (!podeEditar.value || !alterado.value) return
  salvando.value = true
  erro.value = ''
  try {
    const data = await atendimentoPwaService.salvar(modoSelecionado.value)
    modoPersistido.value = data?.modo_abertura_pwa || modoSelecionado.value
    mostrarToast('Preferência de abertura atualizada no aplicativo.', false)
  } catch (e) {
    erro.value = getApiErrorMessage(e, 'Erro ao salvar.')
    mostrarToast(erro.value, true)
  } finally {
    salvando.value = false
  }
}

onMounted(() => {
  void carregar()
})

watch(modoSelecionado, () => {
  erro.value = ''
})
</script>