<template>
  <section v-if="deveExibir" class="card space-y-4" aria-labelledby="titulo-reaberturas-bo">
    <div class="flex flex-wrap items-start justify-between gap-2">
      <div>
        <h2 id="titulo-reaberturas-bo" class="text-lg font-bold text-gray-900 dark:text-white">
          Reaberturas e contestações
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Histórico de solicitações de retrabalho pelo cidadão
        </p>
      </div>
      <BadgeReabertoProtocolo :qtd-reaberturas="qtd" :reaberto="reaberto" />
    </div>

    <div
      v-if="janelaAberta"
      class="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 px-4 py-3 text-sm text-amber-950 dark:text-amber-100"
    >
      Janela de contestação aberta até
      <time :datetime="reaberturaAte">{{ formatarPrazoHumano(reaberturaAte) }}</time>.
    </div>
    <div
      v-else-if="encerradoDefinitivo && statusResolvido"
      class="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 px-4 py-3 text-sm text-gray-700 dark:text-gray-300"
    >
      Janela de contestação encerrada definitivamente.
    </div>

    <p class="text-xs text-gray-500 dark:text-gray-400">
      Total de reaberturas: <strong>{{ qtd }}</strong>
      <template v-if="ultimaEm">
        · Última em <time :datetime="ultimaEm">{{ formatarPrazoHumano(ultimaEm) }}</time>
      </template>
    </p>

    <ul v-if="lista.length" class="space-y-4">
      <li
        v-for="r in lista"
        :key="r.id"
        class="rounded-xl border border-gray-200 dark:border-gray-700 p-4 text-sm"
      >
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <time v-if="r.criado_em" class="text-xs font-semibold text-gray-500" :datetime="r.criado_em">
            {{ formatarPrazoHumano(r.criado_em) }}
          </time>
          <span
            v-if="r.nota_csat_origem"
            class="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/40 text-amber-900 dark:text-amber-100"
          >
            CSAT original: {{ r.nota_csat_origem }} estrela(s)
          </span>
        </div>
        <p class="text-gray-800 dark:text-gray-200 whitespace-pre-line mb-2">{{ r.motivo }}</p>
        <p v-if="r.novo_prazo_sla" class="text-xs text-gray-600 dark:text-gray-400 mb-2">
          Novo prazo SLA: <time :datetime="r.novo_prazo_sla">{{ formatarPrazoHumano(r.novo_prazo_sla) }}</time>
        </p>
        <DiligenciaAnexosGrade v-if="r.anexos?.length" :anexos="r.anexos" />
      </li>
    </ul>
    <p v-else class="text-sm text-gray-500 dark:text-gray-400">Nenhuma reabertura registrada ainda.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import BadgeReabertoProtocolo from '@/components/backoffice/protocolo/BadgeReabertoProtocolo.vue'
import DiligenciaAnexosGrade from '@/components/diligencia/DiligenciaAnexosGrade.vue'
import { formatarPrazoHumano } from '@/utils/diligenciaHelpers'

const props = defineProps({
  protocolo: { type: Object, default: null }
})

const qtd = computed(() => Number(props.protocolo?.qtdReaberturas ?? props.protocolo?.qtd_reaberturas ?? 0))
const reaberto = computed(() => Boolean(props.protocolo?.reaberto) || qtd.value > 0)
const lista = computed(() => props.protocolo?.reaberturas || [])
const reaberturaAte = computed(() => props.protocolo?.reaberturaAte ?? props.protocolo?.reabertura_ate)
const ultimaEm = computed(() => props.protocolo?.ultimaReaberturaEm ?? props.protocolo?.ultima_reabertura_em)
const podeReabrir = computed(() => Boolean(props.protocolo?.podeReabrir ?? props.protocolo?.pode_reabrir))
const statusResolvido = computed(() => props.protocolo?.status === 'resolvido')

const janelaAberta = computed(() => podeReabrir.value && Boolean(reaberturaAte.value))
const encerradoDefinitivo = computed(
  () => !podeReabrir.value && props.protocolo?.motivoBloqueioReabertura === 'encerrado_definitivamente'
)

const deveExibir = computed(
  () =>
    reaberto.value ||
    lista.value.length > 0 ||
    janelaAberta.value ||
    encerradoDefinitivo.value
)
</script>