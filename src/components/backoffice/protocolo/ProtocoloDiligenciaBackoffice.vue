<template>
  <section class="card space-y-4" aria-labelledby="titulo-diligencia-bo">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 id="titulo-diligencia-bo" class="text-lg font-bold text-gray-900 dark:text-white">
          Diligência com o cidadão
        </h2>
        <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
          Solicite complementação e pause o SLA enquanto aguarda resposta.
        </p>
      </div>
      <template v-if="protocolo.diligenciaAtiva">
        <span
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100 border border-amber-300/80"
        >
          <PauseCircleIcon class="w-4 h-4" aria-hidden="true" />
          SLA pausado · Aguardando cidadão
        </span>
      </template>
    </div>

    <div
      v-if="protocolo.diligenciaAtiva"
      class="rounded-xl border-2 border-amber-300 dark:border-amber-700 bg-amber-50/80 dark:bg-amber-950/30 p-4 space-y-3"
    >
      <p class="text-sm text-gray-900 dark:text-white whitespace-pre-line">
        {{ protocolo.diligenciaAtiva.pergunta }}
      </p>
      <p class="text-xs text-gray-700 dark:text-gray-300">
        Prazo limite:
        <time :datetime="protocolo.diligenciaAtiva.prazo_resposta">
          {{ formatarPrazoHumano(protocolo.diligenciaAtiva.prazo_resposta) }}
        </time>
        <span v-if="protocolo.diligenciaAtiva.exige_anexo" class="block mt-1 font-semibold text-amber-900 dark:text-amber-200">
          Exige anexo na resposta
        </span>
      </p>
      <button
        type="button"
        class="btn-secondary min-h-[44px] text-sm"
        :disabled="cancelando"
        @click="confirmarCancelar"
      >
        {{ cancelando ? 'Cancelando…' : 'Cancelar diligência' }}
      </button>
    </div>

    <div v-else class="flex flex-col sm:flex-row sm:items-center gap-3">
      <button
        type="button"
        class="btn-primary min-h-[44px]"
        :disabled="!protocolo.podeAbrirDiligencia"
        :title="tooltipBloqueio"
        @click="$emit('abrir-modal')"
      >
        Pedir complementação (Diligência)
      </button>
      <p v-if="!protocolo.podeAbrirDiligencia && textoBloqueio" class="text-xs text-gray-600 dark:text-gray-400 max-w-md">
        {{ textoBloqueio }}
      </p>
    </div>

    <div v-if="historico.length" class="border-t border-gray-200 dark:border-gray-700 pt-4">
      <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Histórico de diligências</h3>
      <ul class="space-y-3">
        <li
          v-for="d in historico"
          :key="d.id"
          class="rounded-lg border border-gray-200 dark:border-gray-700 p-3 text-sm"
        >
          <div class="flex flex-wrap items-center gap-2 mb-2">
            <span class="text-xs font-bold uppercase text-gray-500">{{ labelStatusDiligencia(d.status) }}</span>
            <time class="text-xs text-gray-500" :datetime="d.criado_em">{{ formatarPrazoHumano(d.criado_em) }}</time>
          </div>
          <p class="text-gray-800 dark:text-gray-200 whitespace-pre-line"><strong>Pergunta:</strong> {{ d.pergunta }}</p>
          <p v-if="d.resposta_cidadao" class="mt-2 text-gray-700 dark:text-gray-300 whitespace-pre-line">
            <strong>Resposta:</strong> {{ d.resposta_cidadao }}
          </p>
          <DiligenciaAnexosGrade
            v-if="d.anexos?.length"
            :anexos="d.anexos"
          />
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { PauseCircleIcon } from '@heroicons/vue/24/outline'
import { diligenciaBackofficeService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  formatarPrazoHumano,
  labelStatusDiligencia,
  textoMotivoBloqueioDiligencia
} from '@/utils/diligenciaHelpers'
import DiligenciaAnexosGrade from '@/components/diligencia/DiligenciaAnexosGrade.vue'
import { useDialog } from '@/composables/useDialog'

const { confirm } = useDialog()

const props = defineProps({
  protocolo: { type: Object, required: true }
})

const emit = defineEmits(['abrir-modal', 'atualizado'])

const cancelando = ref(false)

const historico = computed(() => props.protocolo?.diligencias || [])

const textoBloqueio = computed(() =>
  textoMotivoBloqueioDiligencia(props.protocolo?.motivoBloqueioDiligencia)
)

const tooltipBloqueio = computed(() => textoBloqueio.value || '')

async function confirmarCancelar() {
  const d = props.protocolo?.diligenciaAtiva
  if (!d?.id) return
  const ok = await confirm(
    'Cancelar a diligência? O protocolo voltará ao status anterior e o SLA será retomado.',
    'Cancelar diligência'
  )
  if (!ok) return
  const motivo = window.prompt('Motivo opcional (pode deixar em branco):') || ''
  cancelando.value = true
  try {
    await diligenciaBackofficeService.cancelar(d.id, { motivo })
    emit('atualizado')
  } catch (e) {
    window.alert(getApiErrorMessage(e, 'Não foi possível cancelar.'))
  } finally {
    cancelando.value = false
  }
}
</script>