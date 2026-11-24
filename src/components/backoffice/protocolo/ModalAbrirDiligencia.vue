<template>
  <Teleport to="body">
    <div
      v-if="aberto"
      class="fixed inset-0 z-[350] flex items-end sm:items-center justify-center bg-black/50 p-0 sm:p-4"
      role="presentation"
      @click.self="fechar"
    >
      <div
        class="w-full sm:max-w-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-t-2xl sm:rounded-2xl shadow-float max-h-[90dvh] flex flex-col overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-diligencia-titulo"
      >
        <header class="shrink-0 px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 id="modal-diligencia-titulo" class="text-lg font-bold text-gray-900 dark:text-white">
            Pedir complementação ao cidadão
          </h3>
          <button type="button" class="btn-icon min-h-[44px] min-w-[44px]" aria-label="Fechar" @click="fechar">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </header>

        <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          <div>
            <label for="diligencia-pergunta" class="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
              Pergunta / instrução ao cidadão
            </label>
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
              Seja objetivo: explique exatamente qual informação ou foto falta para concluir o atendimento.
            </p>
            <textarea
              id="diligencia-pergunta"
              v-model="pergunta"
              rows="5"
              class="input w-full min-h-[120px]"
              :disabled="salvando"
            />
          </div>

          <div class="flex items-start gap-3">
            <button
              type="button"
              role="switch"
              :aria-checked="exigeAnexo"
              class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors mt-0.5"
              :class="exigeAnexo ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'"
              @click="exigeAnexo = !exigeAnexo"
            >
              <span
                class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition"
                :class="exigeAnexo ? 'translate-x-5' : 'translate-x-0'"
              />
            </button>
            <div>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">
                Exigir envio de foto ou anexo na resposta
              </p>
            </div>
          </div>

          <div v-if="ordensAbertas.length > 1">
            <label for="diligencia-os" class="block text-sm font-semibold mb-1">Vincular ordem de serviço (opcional)</label>
            <select id="diligencia-os" v-model="ordemServicoId" class="input w-full">
              <option value="">— Todas / protocolo geral —</option>
              <option v-for="o in ordensAbertas" :key="o.id" :value="o.id">
                {{ nomeOs(o) }}
              </option>
            </select>
          </div>

          <div
            class="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30 p-4 text-xs text-amber-950 dark:text-amber-100 leading-relaxed"
          >
            Ao enviar, o protocolo mudará para <strong>Aguardando cidadão</strong> e o relógio do SLA ficará
            pausado até a resposta ou expiração do prazo.
          </div>

          <p v-if="erro" class="text-sm text-red-600" role="alert">{{ erro }}</p>
        </div>

        <footer class="shrink-0 px-5 py-4 border-t border-gray-200 dark:border-gray-700 flex flex-col-reverse sm:flex-row gap-2 sm:justify-end bg-gray-50 dark:bg-gray-800/80">
          <button type="button" class="btn-secondary min-h-[44px]" :disabled="salvando" @click="fechar">Cancelar</button>
          <button type="button" class="btn-primary min-h-[44px]" :disabled="salvando || !pergunta.trim()" @click="confirmar">
            {{ salvando ? 'Enviando…' : 'Enviar solicitação' }}
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { diligenciaBackofficeService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { noAberto, nomeSecretariaNo } from '@/utils/scatterGather'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  protocolo: { type: Object, required: true },
  unidadeUsuarioId: { type: String, default: null }
})

const emit = defineEmits(['fechar', 'criada'])

const pergunta = ref('')
const exigeAnexo = ref(false)
const ordemServicoId = ref('')
const salvando = ref(false)
const erro = ref('')

const ordensAbertas = computed(() => {
  const lista = props.protocolo?.ordens_servico || []
  let abertas = lista.filter((o) => noAberto(o))
  if (props.unidadeUsuarioId) {
    const filtradas = abertas.filter(
      (o) =>
        String(o.unidade?.id || o.unidade_id) === String(props.unidadeUsuarioId)
    )
    if (filtradas.length) abertas = filtradas
  }
  return abertas
})

watch(
  () => props.aberto,
  (v) => {
    if (v) {
      pergunta.value = ''
      exigeAnexo.value = false
      erro.value = ''
      ordemServicoId.value =
        ordensAbertas.value.length === 1 ? String(ordensAbertas.value[0].id) : ''
    }
  }
)

function nomeOs(ordem) {
  return nomeSecretariaNo(ordem)
}

function fechar() {
  if (salvando.value) return
  emit('fechar')
}

async function confirmar() {
  if (!pergunta.value.trim()) return
  salvando.value = true
  erro.value = ''
  try {
    const body = {
      pergunta: pergunta.value.trim(),
      exige_anexo: exigeAnexo.value
    }
    if (ordemServicoId.value) body.ordem_servico_id = ordemServicoId.value
    const data = await diligenciaBackofficeService.abrir(props.protocolo.id, body)
    emit('criada', data)
    emit('fechar')
  } catch (e) {
    erro.value = getApiErrorMessage(e, 'Não foi possível abrir a diligência.')
  } finally {
    salvando.value = false
  }
}
</script>