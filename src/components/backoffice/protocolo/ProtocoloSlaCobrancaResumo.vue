<template>
  <section
    v-if="exibir"
    class="card border border-amber-200 dark:border-amber-800/60 bg-amber-50/40 dark:bg-amber-950/20"
    aria-labelledby="titulo-sla-cobranca"
  >
    <div class="flex items-start gap-3 mb-4">
      <div class="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center shrink-0">
        <BellAlertIcon class="w-6 h-6 text-amber-700 dark:text-amber-300" />
      </div>
      <div>
        <h2 id="titulo-sla-cobranca" class="text-lg font-semibold text-gray-900 dark:text-white">
          SLA e cobrança do cidadão
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">Sinais de atraso e cobranças registradas no PWA</p>
      </div>
    </div>
    <dl class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
      <div>
        <dt class="text-xs font-medium uppercase text-gray-500">Cobranças do cidadão</dt>
        <dd class="mt-1 font-bold text-amber-900 dark:text-amber-100">{{ qtd }}</dd>
        <p v-if="ultima" class="text-xs text-gray-600 dark:text-gray-400 mt-1">
          Última: {{ ultima }}
        </p>
      </div>
      <div>
        <dt class="text-xs font-medium uppercase text-gray-500">Dias em atraso</dt>
        <dd class="mt-1 font-semibold text-gray-900 dark:text-white">
          <span v-if="dias > 0" class="text-red-700 dark:text-red-300">{{ dias }} dia(s)</span>
          <span v-else>—</span>
        </dd>
      </div>
      <div>
        <dt class="text-xs font-medium uppercase text-gray-500">Nível de alerta</dt>
        <dd class="mt-1">
          <span
            :class="classeNivelAlertaSla(nivel)"
            class="inline-flex text-xs font-semibold px-2.5 py-1 rounded-full border"
          >
            {{ labelNivelAlertaSla(nivel) }}
          </span>
        </dd>
      </div>
    </dl>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { BellAlertIcon } from '@heroicons/vue/24/outline'
import { classeNivelAlertaSla, labelNivelAlertaSla } from '@/utils/slaAlertaLabels'

const props = defineProps({
  protocolo: { type: Object, required: true }
})

const qtd = computed(() => Number(props.protocolo?.qtdCobrancasCidadao ?? 0))
const dias = computed(() => Number(props.protocolo?.diasAtraso ?? 0))
const nivel = computed(() => props.protocolo?.ultimoAlertaSlaNivel || '')

const exibir = computed(
  () => qtd.value > 0 || dias.value > 0 || Boolean(nivel.value)
)

const ultima = computed(() => {
  const raw = props.protocolo?.ultimaCobrancaEm
  if (!raw) return ''
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return raw
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>