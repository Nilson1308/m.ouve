<template>
  <section
    v-if="protocolo"
    class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-5 shadow-sm space-y-4"
  >
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wide">Urgência</h2>
        <div class="mt-2 flex flex-wrap items-center gap-2">
          <UrgenciaBadge :nivel="protocolo.urgencia" :sugestao-ia-pendente="pendente" size="lg" />
          <span v-if="protocolo.urgenciaOrigem" class="text-xs text-slate-500 dark:text-slate-400">
            Origem: {{ labelOrigem }}
          </span>
        </div>
      </div>
      <button
        v-if="podeAlterar"
        type="button"
        class="btn-secondary text-sm min-h-[40px] focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
        @click="$emit('alterar-manual')"
      >
        Alterar urgência
      </button>
    </div>

    <div
      v-if="pendente"
      class="rounded-xl border border-violet-200 dark:border-violet-800 bg-violet-50 dark:bg-violet-950/30 p-4 space-y-3"
    >
      <p class="text-sm font-semibold text-violet-900 dark:text-violet-100 flex flex-wrap items-center gap-2">
        A IA sugere elevar para
        <UrgenciaBadge :nivel="sugestaoIa" size="sm" />
        <span v-if="confiancaFmt" class="font-normal text-violet-800 dark:text-violet-200"
          >(confiança {{ confiancaFmt }})</span
        >
      </p>
      <p v-if="motivoIa" class="text-xs text-violet-800 dark:text-violet-200 leading-relaxed">{{ motivoIa }}</p>
      <div v-if="podeAlterar" class="flex flex-wrap gap-2">
        <button
          type="button"
          class="btn-primary text-sm min-h-[40px] focus-visible:ring-2 focus-visible:ring-violet-500"
          :disabled="processando"
          @click="$emit('acao-ia', { acao: 'aceitar_sugestao_ia' })"
        >
          Aceitar sugestão
        </button>
        <button
          type="button"
          class="btn-secondary text-sm min-h-[40px] focus-visible:ring-2 focus-visible:ring-slate-400"
          :disabled="processando"
          @click="$emit('acao-ia', { acao: 'descartar_sugestao_ia' })"
        >
          Descartar
        </button>
      </div>
      <p v-else class="text-xs text-violet-700 dark:text-violet-300">
        Informação para triagem — seu perfil não permite alterar a urgência.
      </p>
    </div>

    <p
      v-if="protocolo.urgenciaReduzSlaAtivo"
      class="text-xs text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2"
    >
      Elevações para Alta ou Crítica podem encurtar o prazo (SLA) conforme a Matriz de Urgência.
    </p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import UrgenciaBadge from '@/components/backoffice/common/UrgenciaBadge.vue'
import { formatarConfiancaIa, sugestaoIaPendente } from '@/utils/urgenciaHelpers'

const props = defineProps({
  protocolo: { type: Object, required: true },
  podeAlterar: { type: Boolean, default: false },
  processando: { type: Boolean, default: false }
})

defineEmits(['alterar-manual', 'acao-ia'])

const pendente = computed(() => sugestaoIaPendente(props.protocolo))

const sugestaoIa = computed(
  () => props.protocolo?.urgenciaSugeridaIa || props.protocolo?.urgencia_sugerida_ia || 'alta'
)

const confiancaFmt = computed(() =>
  formatarConfiancaIa(props.protocolo?.urgenciaConfiancaIa ?? props.protocolo?.urgencia_confianca_ia)
)

const motivoIa = computed(
  () => props.protocolo?.urgenciaMotivoIa || props.protocolo?.urgencia_motivo_ia || ''
)

const labelOrigem = computed(() => {
  const map = {
    catalogo: 'Catálogo',
    regra: 'Regra de campo',
    ia: 'Inteligência artificial',
    super_os: 'Super OS',
    manual: 'Alteração manual'
  }
  const o = props.protocolo?.urgenciaOrigem || props.protocolo?.urgencia_origem
  return map[o] || o || '—'
})
</script>