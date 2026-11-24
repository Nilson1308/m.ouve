<template>
  <section
    v-if="visivel"
    class="card border-2 border-amber-300 dark:border-amber-700 high-contrast:border-yellow-300 bg-gradient-to-br from-amber-50/90 to-white dark:from-amber-950/30 dark:to-gray-900"
    :aria-labelledby="tituloId"
  >
    <div v-if="podeCobrar" class="space-y-4">
      <div class="flex items-start gap-3">
        <div
          class="w-12 h-12 rounded-avatar bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center shrink-0"
          aria-hidden="true"
        >
          <BellAlertIcon class="w-7 h-7 text-amber-700 dark:text-amber-300 high-contrast:text-yellow-300" />
        </div>
        <div class="min-w-0 flex-1">
          <h2 :id="tituloId" class="text-base font-bold text-amber-950 dark:text-amber-100 high-contrast:text-yellow-300">
            Prazo de atendimento vencido
          </h2>
          <p class="text-sm text-amber-900/90 dark:text-amber-200/90 high-contrast:text-white mt-1 leading-relaxed">
            Você pode registrar uma cobrança de retorno. O setor responsável receberá um alerta imediato.
          </p>
          <p v-if="qtdCobrancas > 0" class="text-xs text-amber-800 dark:text-amber-300 mt-2">
            Cobranças anteriores: {{ qtdCobrancas }}
          </p>
        </div>
      </div>

      <div
        v-if="feedbackSucesso"
        class="rounded-card border border-emerald-300 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 px-4 py-3 text-sm text-emerald-900 dark:text-emerald-100"
        role="status"
      >
        <p class="font-semibold">Cobrança registrada e enviada ao setor responsável.</p>
        <p v-if="proximaCobrancaFormatada" class="mt-1 text-xs">
          Nova cobrança disponível em {{ proximaCobrancaFormatada }}.
        </p>
      </div>

      <button
        type="button"
        class="w-full min-h-[48px] inline-flex items-center justify-center gap-2 px-5 py-3 rounded-button font-bold text-amber-950 bg-amber-400 hover:bg-amber-500 dark:bg-amber-500 dark:hover:bg-amber-400 high-contrast:bg-yellow-300 high-contrast:text-black shadow-button transition-colors motion-reduce:transition-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600 focus-visible:ring-offset-2"
        @click="abrirModal"
      >
        <BellAlertIcon class="w-5 h-5 shrink-0" aria-hidden="true" />
        Cobrar retorno
      </button>
    </div>

    <div v-else-if="motivo === 'em_cooldown'" class="flex items-start gap-3">
      <InformationCircleIcon
        class="w-6 h-6 text-amber-700 dark:text-amber-300 high-contrast:text-yellow-300 shrink-0 mt-0.5"
        aria-hidden="true"
      />
      <p class="text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white leading-relaxed">
        Cobrança registrada ({{ qtdCobrancas }}x).
        <template v-if="proximaCobrancaFormatada">
          Nova cobrança disponível em <time :datetime="proximaCobrancaIso">{{ proximaCobrancaFormatada }}</time>.
        </template>
      </p>
    </div>

    <Teleport to="body">
      <div
        v-if="modalAberto"
        class="fixed inset-0 z-[400] flex items-end sm:items-center justify-center bg-black/50 backdrop-blur-sm p-0 sm:p-4"
        role="presentation"
        @click.self="fecharModal"
      >
        <div
          class="w-full sm:max-w-lg bg-white dark:bg-gray-900 high-contrast:bg-black border border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300 rounded-t-2xl sm:rounded-2xl shadow-float max-h-[90dvh] flex flex-col overflow-hidden"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-cobranca-titulo"
        >
          <div class="shrink-0 px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between gap-3">
            <h3 id="modal-cobranca-titulo" class="text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
              Confirmar cobrança
            </h3>
            <button
              type="button"
              class="btn-icon min-h-[44px] min-w-[44px]"
              aria-label="Fechar"
              @click="fecharModal"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white">
              Mensagem opcional para o setor (até 300 caracteres).
            </p>
            <div>
              <label for="cobranca-obs" class="sr-only">Observação</label>
              <textarea
                id="cobranca-obs"
                v-model="mensagem"
                rows="4"
                maxlength="300"
                class="input w-full text-base min-h-[96px]"
                placeholder="Ex.: Ainda aguardo retorno sobre o prazo informado."
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
                {{ mensagem.length }}/300
              </p>
            </div>
            <p v-if="erroModal" class="text-sm text-red-700 dark:text-red-300" role="alert">
              {{ erroModal }}
            </p>
          </div>

          <div class="shrink-0 px-5 py-4 border-t border-gray-200 dark:border-gray-700 flex flex-col-reverse sm:flex-row gap-2 sm:justify-end bg-gray-50 dark:bg-gray-800/80">
            <button type="button" class="btn-secondary min-h-[44px]" :disabled="enviando" @click="fecharModal">
              Cancelar
            </button>
            <button type="button" class="btn-primary min-h-[44px]" :disabled="enviando" @click="confirmarCobranca">
              {{ enviando ? 'Enviando…' : 'Confirmar cobrança' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { BellAlertIcon, InformationCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { protocolosService } from '@/services/api'

const props = defineProps({
  protocoloId: { type: String, required: true },
  podeCobrar: { type: Boolean, default: false },
  motivo: { type: String, default: null },
  qtdCobrancas: { type: Number, default: 0 },
  proximaCobrancaEm: { type: String, default: null }
})

const emit = defineEmits(['atualizado'])

const tituloId = 'sec-cobranca-protocolo'
const modalAberto = ref(false)
const mensagem = ref('')
const enviando = ref(false)
const erroModal = ref('')
const feedbackSucesso = ref(false)
const proximaLocal = ref(props.proximaCobrancaEm)

const visivel = computed(
  () =>
    props.podeCobrar ||
    props.motivo === 'em_cooldown'
)

const motivo = computed(() => props.motivo)
const podeCobrar = computed(() => props.podeCobrar)

const proximaCobrancaIso = computed(() => proximaLocal.value || props.proximaCobrancaEm || '')

const proximaCobrancaFormatada = computed(() => {
  const raw = proximaCobrancaIso.value
  if (!raw) return ''
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

function abrirModal() {
  erroModal.value = ''
  mensagem.value = ''
  modalAberto.value = true
}

function fecharModal() {
  if (enviando.value) return
  modalAberto.value = false
}

function extrairErroCobranca(err) {
  const data = err?.response?.data
  if (!data) return err?.message || 'Não foi possível registrar a cobrança.'
  if (typeof data.detail === 'string') return data.detail
  if (data.detail && typeof data.detail === 'object') {
    if (data.detail.detalhe) return data.detail.detalhe
    if (data.detail.proxima_cobranca_em) {
      proximaLocal.value = data.detail.proxima_cobranca_em
    }
  }
  if (data.detalhe) return Array.isArray(data.detalhe) ? data.detalhe[0] : data.detalhe
  return 'Não foi possível registrar a cobrança.'
}

async function confirmarCobranca() {
  enviando.value = true
  erroModal.value = ''
  try {
    const res = await protocolosService.cobrar(props.protocoloId, {
      mensagem: mensagem.value.trim()
    })
    feedbackSucesso.value = true
    modalAberto.value = false
    emit('atualizado', {
      qtd_cobrancas_cidadao: res.qtd_cobrancas_cidadao,
      ultima_cobranca_em: res.ultima_cobranca_em,
      pode_cobrar: false,
      motivo_bloqueio_cobranca: 'em_cooldown'
    })
  } catch (err) {
    erroModal.value = extrairErroCobranca(err)
    if (err?.response?.status === 429) {
      const data = err.response.data
      const prox =
        data?.detail?.proxima_cobranca_em || data?.proxima_cobranca_em
      if (prox) proximaLocal.value = prox
    }
  } finally {
    enviando.value = false
  }
}
</script>