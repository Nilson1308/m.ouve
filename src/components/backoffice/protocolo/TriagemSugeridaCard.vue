<template>
  <section
    v-if="mostrarCard"
    class="card border-2 border-violet-300/80 dark:border-violet-600/60 bg-gradient-to-br from-violet-50/90 via-white to-indigo-50/50 dark:from-violet-950/35 dark:via-gray-800 dark:to-indigo-950/30 p-5 shadow-lg shadow-violet-500/5"
  >
    <header class="flex items-start gap-3 mb-4">
      <div
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-violet-600/15 dark:bg-violet-500/20 text-violet-700 dark:text-violet-300"
      >
        <SparklesIcon class="w-6 h-6" />
      </div>
      <div class="flex-1 min-w-0">
        <h2 class="text-base font-bold text-gray-900 dark:text-white">
          Sugestão de encaminhamento
        </h2>
        <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
          {{ labelMotorTriagem(meta.versaoMotor) }}
          <span v-if="meta.geradaEm"> · {{ meta.geradaEm }}</span>
        </p>
      </div>
    </header>

    <blockquote
      v-if="resumoMotivo"
      class="mb-4 rounded-lg border border-violet-200/60 dark:border-violet-800/40 bg-violet-50/50 dark:bg-violet-950/25 px-4 py-3 text-sm text-gray-800 dark:text-gray-200 leading-relaxed"
    >
      <p class="text-[10px] font-semibold uppercase tracking-wide text-violet-700 dark:text-violet-300 mb-1">
        Síntese da IA
      </p>
      {{ resumoMotivo }}
    </blockquote>

    <ul v-if="unidades.length" class="space-y-3 mb-4">
      <li
        v-for="item in unidades"
        :key="item.id"
        class="rounded-lg border border-violet-200/70 dark:border-violet-800/50 bg-white/80 dark:bg-gray-900/50 px-4 py-3"
      >
        <div class="flex flex-wrap items-start justify-between gap-2">
          <p class="font-semibold text-gray-900 dark:text-white">{{ item.nome }}</p>
          <div class="flex flex-wrap gap-1.5 shrink-0 items-center">
            <span
              class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-100 text-violet-800 dark:bg-violet-900/50 dark:text-violet-200"
            >
              {{ formatarConfiancaTriagem(item.confianca) }}
            </span>
            <span :class="classeBadgeFonteTriagem(item.fonte)">
              <SparklesIcon
                v-if="item.fonte === 'llm'"
                class="w-3.5 h-3.5"
                aria-hidden="true"
              />
              <BuildingOffice2Icon
                v-else-if="item.fonte === 'equipamento_publico'"
                class="w-3.5 h-3.5"
                aria-hidden="true"
              />
              {{ labelFonteTriagem(item.fonte) }}
            </span>
          </div>
        </div>
        <p v-if="item.motivo" class="text-xs text-gray-600 dark:text-gray-400 mt-2 leading-relaxed">
          {{ item.motivo }}
        </p>
        <button
          v-if="podeDespachar"
          type="button"
          class="mt-3 text-xs font-semibold text-violet-700 dark:text-violet-300 hover:underline"
          @click="emit('preencher-despacho', [item])"
        >
          Pré-preencher só esta unidade
        </button>
      </li>
    </ul>

    <div v-if="podeDespachar && unidades.length" class="flex flex-col sm:flex-row gap-2">
      <button
        type="button"
        class="btn-primary flex-1 inline-flex items-center justify-center gap-2"
        @click="emit('preencher-despacho', unidades)"
      >
        <PaperAirplaneIcon class="w-5 h-5" />
        Pré-preencher despacho ({{ unidades.length }})
      </button>
    </div>
    <p v-else-if="!podeDespachar" class="text-xs text-gray-500 dark:text-gray-400">
      Sugestão informativa — despacho não disponível neste status.
    </p>

    <p
      v-if="textoAuditoria"
      class="mt-4 pt-3 border-t border-violet-200/40 dark:border-violet-800/30 text-xs text-slate-500 dark:text-slate-400"
    >
      {{ textoAuditoria }}
    </p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { SparklesIcon, PaperAirplaneIcon, BuildingOffice2Icon } from '@heroicons/vue/24/outline'
import {
  classeBadgeFonteTriagem,
  formatarConfiancaTriagem,
  labelFonteTriagem,
  labelMotorTriagem,
  textoAuditoriaTriagem
} from '@/constants/triagemSugerida'

const props = defineProps({
  triagem: { type: Object, default: null },
  podeDespachar: { type: Boolean, default: false }
})

const emit = defineEmits(['preencher-despacho'])

const unidades = computed(() => {
  const lista = props.triagem?.unidades_sugeridas ?? props.triagem?.unidadesSugeridas
  return Array.isArray(lista) ? lista : []
})

const resumoMotivo = computed(() => {
  const t = props.triagem || {}
  return (t.resumo_motivo || t.resumoMotivo || '').trim()
})

const mostrarCard = computed(
  () => unidades.value.length > 0 || Boolean(resumoMotivo.value)
)

const meta = computed(() => {
  const t = props.triagem || {}
  let geradaEm = t.gerada_em || t.geradaEm
  if (geradaEm) {
    try {
      geradaEm = new Date(geradaEm).toLocaleString('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short'
      })
    } catch {
      /* mantém ISO */
    }
  }
  return {
    geradaEm,
    versaoMotor: t.versao_motor || t.versaoMotor
  }
})

const textoAuditoria = computed(() => textoAuditoriaTriagem(props.triagem || {}))
</script>