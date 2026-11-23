<template>
  <!-- Painel (modal de despacho) -->
  <div
    v-if="unidades.length && variante === 'panel'"
    class="rounded-xl border-2 border-violet-300/80 dark:border-violet-600/60 bg-gradient-to-br from-violet-50/90 via-white to-indigo-50/50 dark:from-violet-950/35 dark:via-gray-800 dark:to-indigo-950/30 p-4 shadow-sm shadow-violet-500/5"
    :title="tituloCompleto"
  >
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:gap-5">
      <div class="flex items-start gap-3 min-w-0 flex-1">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-600/12 dark:bg-violet-500/20 text-violet-700 dark:text-violet-300"
        >
          <SparklesIcon class="w-5 h-5" aria-hidden="true" />
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold text-gray-900 dark:text-white leading-snug">
            <span class="text-gray-600 dark:text-gray-400 font-medium">Sugere: </span>
            {{ resumoTexto }}
          </p>
          <p
            v-if="primeiraUnidade?.motivo"
            class="text-xs text-gray-600 dark:text-gray-400 mt-1.5 line-clamp-2 leading-relaxed"
          >
            {{ primeiraUnidade.motivo }}
          </p>
          <div v-if="primeiraUnidade" class="flex flex-wrap items-center gap-1.5 mt-2 lg:hidden">
            <span
              class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-100 text-violet-800 dark:bg-violet-900/50 dark:text-violet-200"
            >
              {{ formatarConfiancaTriagem(primeiraUnidade.confianca) }}
            </span>
            <span :class="classeBadgeFonteTriagem(primeiraUnidade.fonte)">
              {{ labelFonteTriagem(primeiraUnidade.fonte) }}
            </span>
          </div>
        </div>
      </div>

      <div
        class="flex flex-col gap-2 sm:flex-row sm:items-center lg:flex-col lg:items-stretch lg:shrink-0 lg:w-52"
      >
        <div v-if="primeiraUnidade" class="hidden lg:flex flex-wrap justify-end gap-1.5">
          <span
            class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-100 text-violet-800 dark:bg-violet-900/50 dark:text-violet-200"
          >
            {{ formatarConfiancaTriagem(primeiraUnidade.confianca) }}
          </span>
          <span :class="classeBadgeFonteTriagem(primeiraUnidade.fonte)">
            {{ labelFonteTriagem(primeiraUnidade.fonte) }}
          </span>
        </div>
        <button
          v-if="mostrarAcao"
          type="button"
          class="btn-primary w-full px-4 py-2.5 text-sm font-semibold shadow-button hover:shadow-button-hover"
          @click="emit('aplicar', unidades)"
        >
          <PaperAirplaneIcon class="w-5 h-5" aria-hidden="true" />
          Aplicar sugestão ({{ unidades.length }})
        </button>
      </div>
    </div>
  </div>

  <!-- Variantes compactas (kanban / lista / badge) -->
  <component
    v-else-if="unidades.length"
    :is="tagRaiz"
    :class="wrapperClass"
    :title="tituloCompleto"
  >
    <SparklesIcon class="w-3.5 h-3.5 shrink-0 text-violet-600 dark:text-violet-400" aria-hidden="true" />
    <div class="min-w-0 flex-1">
      <p v-if="variante !== 'badge'" :class="tituloClass">
        <span>Sugere: </span>
        <span class="font-semibold">{{ resumoTexto }}</span>
      </p>
      <span v-else class="font-semibold truncate max-w-[7rem]">{{ resumoTexto }}</span>
    </div>
    <span
      v-if="primeiraUnidade && variante !== 'badge'"
      class="shrink-0 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-violet-100 text-violet-800 dark:bg-violet-900/50 dark:text-violet-200"
    >
      {{ formatarConfiancaTriagem(primeiraUnidade.confianca) }}
    </span>
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { SparklesIcon, PaperAirplaneIcon } from '@heroicons/vue/24/outline'
import {
  classeBadgeFonteTriagem,
  formatarConfiancaTriagem,
  labelFonteTriagem
} from '@/constants/triagemSugerida'
import {
  resumoEncaminhamentoTexto,
  unidadesTriagemSugeridas
} from '@/utils/triagemEncaminhamento'

const props = defineProps({
  triagem: { type: Object, default: null },
  variante: {
    type: String,
    default: 'inline',
    validator: (v) => ['inline', 'card', 'panel', 'badge'].includes(v)
  },
  mostrarAcao: { type: Boolean, default: true }
})

const emit = defineEmits(['aplicar'])

const unidades = computed(() => unidadesTriagemSugeridas(props.triagem))

const primeiraUnidade = computed(() => unidades.value[0] || null)

const resumoTexto = computed(() => {
  if (!unidades.value.length) return ''
  return resumoEncaminhamentoTexto({ triagemSugerida: props.triagem })
})

const tituloCompleto = computed(() => {
  return unidades.value.map((u) => u.nome).filter(Boolean).join(' · ')
})

const tagRaiz = computed(() => (props.variante === 'inline' || props.variante === 'badge' ? 'span' : 'div'))

const wrapperClass = computed(() => {
  switch (props.variante) {
    case 'badge':
      return 'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide bg-violet-500/15 text-violet-900 dark:text-violet-200 border border-violet-400/40'
    case 'card':
      return 'mb-3 rounded-lg border border-violet-200 dark:border-violet-700 bg-gradient-to-r from-violet-50/90 to-indigo-50/70 dark:from-violet-950/30 dark:to-indigo-950/20 px-2.5 py-2 flex items-start gap-2'
    default:
      return 'flex items-center gap-1.5 text-[11px] text-violet-800 dark:text-violet-200 mt-1'
  }
})

const tituloClass = computed(() => {
  if (props.variante === 'card') {
    return 'text-[11px] font-semibold text-violet-900 dark:text-violet-100 leading-snug'
  }
  return 'truncate'
})
</script>