<template>
  <section
    class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm"
    aria-labelledby="titulo-origem-abertura"
  >
    <h2
      id="titulo-origem-abertura"
      class="text-lg font-semibold text-gray-900 dark:text-white mb-1"
    >
      Origem dos Atendimentos (IA × Catálogo Guiado)
    </h2>
    <p class="text-xs text-gray-500 dark:text-gray-400 mb-5">
      Como o cidadão abriu o protocolo no aplicativo (telemetria v4.20).
    </p>

    <div v-if="!temDados" class="text-sm text-gray-600 dark:text-gray-400 py-4 text-center">
      Ainda não há protocolos suficientes para comparar os dois caminhos neste período.
    </div>

    <div v-else class="space-y-5">
      <div
        v-for="item in itens"
        :key="item.chave"
        class="space-y-2"
      >
        <div class="flex items-center justify-between gap-2 text-sm">
          <span class="font-medium text-gray-800 dark:text-gray-200">{{ item.rotulo }}</span>
          <span class="text-gray-600 dark:text-gray-400 tabular-nums">
            {{ item.total }} · {{ item.percentualLabel }}
          </span>
        </div>
        <div
          class="h-3 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden"
          role="presentation"
        >
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="item.barClass"
            :style="{ width: `${Math.min(100, Math.max(0, item.percentual))}%` }"
          />
        </div>
        <dl class="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
          <div>
            <dt class="font-semibold text-gray-500 dark:text-gray-500">TMA médio</dt>
            <dd class="text-gray-900 dark:text-gray-100">{{ item.tmaLabel }}</dd>
          </div>
          <div>
            <dt class="font-semibold text-gray-500 dark:text-gray-500">CSAT médio</dt>
            <dd class="text-gray-900 dark:text-gray-100">{{ item.csatLabel }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  resumo: {
    type: Object,
    default: () => null
  }
})

function fmtPercentual(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toFixed(1)}%`
}

function fmtHoras(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toFixed(1)} h`
}

function fmtCsat(v) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return `${Number(v).toFixed(1)}/5`
}

const itens = computed(() => {
  const raw = props.resumo || {}
  const defs = [
    { chave: 'chat_ia', rotulo: 'Assistente IA', barClass: 'bg-primary-500 dark:bg-primary-400' },
    {
      chave: 'catalogo_guiado',
      rotulo: 'Catálogo Guiado',
      barClass: 'bg-emerald-500 dark:bg-emerald-400'
    }
  ]
  return defs.map((d) => {
    const bloco = raw[d.chave] || {}
    return {
      ...d,
      rotulo: bloco.rotulo || d.rotulo,
      total: Number(bloco.total_protocolos) || 0,
      percentual: Number(bloco.percentual) || 0,
      percentualLabel: fmtPercentual(bloco.percentual),
      tmaLabel: fmtHoras(bloco.tma_horas),
      csatLabel: fmtCsat(bloco.media_csat)
    }
  })
})

const temDados = computed(() =>
  itens.value.some((i) => i.total > 0)
)
</script>