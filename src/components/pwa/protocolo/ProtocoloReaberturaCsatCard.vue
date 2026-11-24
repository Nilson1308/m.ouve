<template>
  <section
    v-if="exibirDestaqueCsat"
    class="card border-2 border-amber-400/80 dark:border-amber-500 bg-amber-50 dark:bg-amber-950/40"
    :aria-labelledby="tituloDestaqueId"
  >
    <h2 :id="tituloDestaqueId" class="text-base font-bold text-amber-950 dark:text-amber-50 mb-2">
      O problema não foi resolvido como esperado?
    </h2>
    <p class="text-sm text-amber-900 dark:text-amber-100 leading-relaxed mb-4">
      Você pode contestar e reabrir esta solicitação até
      <time v-if="reaberturaAteFmt" :datetime="protocolo.reabertura_ate">{{ reaberturaAteFmt }}</time>
      <span v-else>o fim do prazo de contestação</span>.
    </p>
    <button
      type="button"
      class="w-full min-h-[48px] btn-primary bg-amber-600 hover:bg-amber-700 border-amber-700 font-bold"
      @click="abrirModal"
    >
      Contestar / Reabrir solicitação
    </button>
  </section>

  <section
    v-else-if="exibirAcaoSecundaria"
    class="card border border-gray-200 dark:border-gray-700"
    aria-labelledby="titulo-janela-id"
  >
    <h2 id="titulo-janela-id" class="sr-only">Janela de contestação</h2>
    <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">
      Ainda há tempo para contestar a conclusão
      <template v-if="reaberturaAteFmt">
        — até <time :datetime="protocolo.reabertura_ate">{{ reaberturaAteFmt }}</time>
      </template>.
    </p>
    <button type="button" class="min-h-[44px] btn-secondary w-full sm:w-auto" @click="abrirModal">
      Contestar conclusão
    </button>
  </section>

  <p
    v-else-if="exibirAvisoLimite"
    class="text-sm text-gray-600 dark:text-gray-400 px-1"
    role="status"
  >
    O limite de reaberturas deste protocolo já foi atingido.
  </p>

  <ModalReabrirProtocolo
    :aberto="modalAberto"
    :protocolo-id="protocoloId"
    @fechar="modalAberto = false"
    @concluido="onReaberturaConcluida"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import ModalReabrirProtocolo from '@/components/pwa/protocolo/ModalReabrirProtocolo.vue'
import { formatarPrazoHumano } from '@/utils/diligenciaHelpers'

const props = defineProps({
  protocolo: { type: Object, required: true },
  protocoloId: { type: String, required: true },
  sugerirReaberturaCsat: { type: Boolean, default: false }
})

const emit = defineEmits(['reaberto', 'toast'])

const modalAberto = ref(false)
const tituloDestaqueId = 'pwa-reabertura-destaque'

const podeReabrir = computed(() =>
  Boolean(props.protocolo?.podeReabrir ?? props.protocolo?.pode_reabrir)
)

const motivoBloqueio = computed(
  () => props.protocolo?.motivoBloqueioReabertura ?? props.protocolo?.motivo_bloqueio_reabertura
)

const reaberturaAteFmt = computed(() =>
  formatarPrazoHumano(props.protocolo?.reaberturaAte ?? props.protocolo?.reabertura_ate)
)

const exibirDestaqueCsat = computed(
  () => podeReabrir.value && (props.sugerirReaberturaCsat || props.protocolo?.sugerirReaberturaCsat)
)

const exibirAcaoSecundaria = computed(
  () => podeReabrir.value && !exibirDestaqueCsat.value
)

const exibirAvisoLimite = computed(() => motivoBloqueio.value === 'limite_atingido')

function abrirModal() {
  modalAberto.value = true
}

function onReaberturaConcluida(payload) {
  emit('toast', 'Solicitação reaberta! O atendimento voltou para a fila com um novo prazo.')
  const proto = payload?.protocolo ? payload.protocolo : payload
  emit('reaberto', proto)
}
</script>