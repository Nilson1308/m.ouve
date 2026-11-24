<template>
  <div v-if="badges.length" class="flex flex-wrap gap-1.5">
    <span
      v-for="b in badges"
      :key="b.key"
      :class="[
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-[10px] sm:text-xs font-bold leading-tight',
        b.className
      ]"
    >
      <component :is="b.icon" v-if="b.icon" class="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
      {{ b.label }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { PauseCircleIcon, CheckBadgeIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  ordem: { type: Object, required: true }
})

const badges = computed(() => {
  const o = props.ordem
  const out = []
  const aguardando = Boolean(o.aguardando_cidadao ?? o.aguardandoCidadao)
  const slaPausado = Boolean(o.sla_pausado ?? o.slaPausado)
  if (aguardando || slaPausado) {
    out.push({
      key: 'aguardando',
      label: 'Aguardando cidadão · SLA pausado',
      className:
        'bg-amber-100 text-amber-950 dark:bg-amber-900/40 dark:text-amber-100 border border-amber-300/70 dark:border-amber-700',
      icon: PauseCircleIcon
    })
  }
  const qtdResp = Number(o.qtd_diligencias_respondidas ?? o.qtdDiligenciasRespondidas ?? 0)
  const qtdAnexos = Number(o.qtd_anexos_diligencias ?? o.qtdAnexosDiligencias ?? 0)
  if (!aguardando && qtdResp > 0) {
    const anexoTxt =
      qtdAnexos > 0
        ? ` · ${qtdAnexos} anexo${qtdAnexos > 1 ? 's' : ''}`
        : ''
    out.push({
      key: 'resposta',
      label: `Complementação recebida${anexoTxt}`,
      className:
        'bg-cyan-100 text-cyan-950 dark:bg-cyan-900/40 dark:text-cyan-100 border border-cyan-300/70 dark:border-cyan-700',
      icon: CheckBadgeIcon
    })
  }
  return out
})
</script>