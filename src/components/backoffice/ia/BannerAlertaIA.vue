<template>
  <div
    v-if="sugestao"
    class="relative overflow-hidden rounded-xl border-2 border-primary-300/60 dark:border-primary-600/50 shadow-lg"
  >
    <div
      class="absolute inset-0 bg-gradient-to-r from-primary-500/10 via-purple-500/10 to-pink-500/10 dark:from-primary-500/20 dark:via-purple-500/15 dark:to-pink-500/15"
      aria-hidden="true"
    />
    <div
      class="absolute -top-12 -right-12 h-32 w-32 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 opacity-20 blur-2xl"
      aria-hidden="true"
    />

    <div class="relative flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-start gap-3 min-w-0">
        <div class="relative shrink-0">
          <div
            class="absolute inset-0 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 opacity-60 blur-sm animate-pulse"
          />
          <div
            class="relative flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-purple-600"
          >
            <SparklesIcon class="h-6 w-6 text-white" />
          </div>
        </div>
        <div class="min-w-0 flex-1">
          <p
            class="text-xs font-bold uppercase tracking-wide text-primary-700 dark:text-primary-300 mb-1"
          >
            Sugestão da IA
          </p>
          <p class="text-sm text-gray-900 dark:text-white leading-relaxed">
            <template v-if="sugestao.tipo_acao === 'anexar'">
              💡 Este serviço já está sendo executado na
              <strong class="font-semibold text-primary-700 dark:text-primary-300">
                {{ tituloSuperOs }}
              </strong>.
            </template>
            <template v-else-if="sugestao.tipo_acao === 'criar_retroativa'">
              💡 Um protocolo já está no Painel Setorial
              <strong v-if="sugestao.protocolo_ancora_codigo" class="text-primary-700 dark:text-primary-300">
                ({{ sugestao.protocolo_ancora_codigo }})
              </strong>.
              Junte os {{ sugestao.quantidade }} relato(s) sem novo despacho.
            </template>
            <template v-else>
              💡 A IA encontrou protocolos similares. Agrupe-os para otimizar o atendimento.
            </template>
          </p>
          <p
            v-if="sugestao.tipo_acao === 'criar' && sugestao.quantidade > 1"
            class="text-xs text-gray-600 dark:text-gray-400 mt-1"
          >
            {{ sugestao.quantidade }} relatos no mesmo cluster · {{ sugestao.tipo_servico }}
          </p>
        </div>
      </div>

      <button
        type="button"
        class="shrink-0 inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 shadow-lg shadow-primary-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="processando"
        @click="$emit('acao')"
      >
        <span
          v-if="processando"
          class="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"
        />
        <SparklesIcon v-else class="h-4 w-4" />
        {{ rotuloBotao }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { SparklesIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  sugestao: {
    type: Object,
    default: null
  },
  processando: {
    type: Boolean,
    default: false
  }
})

defineEmits(['acao'])

const tituloSuperOs = computed(() => {
  const s = props.sugestao
  if (!s) return 'Super OS'
  if (s.super_os_titulo) return s.super_os_titulo
  if (s.super_os_codigo) return s.super_os_codigo
  return 'Super OS existente'
})

const rotuloBotao = computed(() => {
  if (props.processando) {
    const t = props.sugestao?.tipo_acao
    if (t === 'anexar') return 'Anexando…'
    if (t === 'criar_retroativa') return 'Agrupando…'
    return 'Criando…'
  }
  if (props.sugestao?.tipo_acao === 'anexar') {
    return 'Anexar a esta Super OS'
  }
  if (props.sugestao?.tipo_acao === 'criar_retroativa') {
    return 'Agrupar na âncora operacional'
  }
  return 'Criar Nova Super OS'
})
</script>