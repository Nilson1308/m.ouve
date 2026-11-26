<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="aberto"
        class="fixed inset-0 z-[120] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-urgencia-titulo"
        @click.self="$emit('fechar')"
      >
        <div
          class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl w-full max-w-lg max-h-[90dvh] flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700"
        >
          <header class="shrink-0 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 id="modal-urgencia-titulo" class="text-lg font-bold text-gray-900 dark:text-white">
              Alterar urgência do protocolo
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              A justificativa ficará registrada no histórico de auditoria.
            </p>
          </header>

          <div class="flex-1 min-h-0 overflow-y-auto overscroll-contain px-6 py-4">
            <p class="text-sm text-gray-700 dark:text-gray-300 mb-3">Selecione o novo nível:</p>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="n in niveis"
                :key="n"
                type="button"
                class="flex items-center justify-center min-h-[48px] rounded-xl border-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
                :class="
                  nivelSelecionado === n
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/40'
                    : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/60 active:bg-gray-100 dark:active:bg-gray-700/50'
                "
                @click="nivelSelecionado = n"
              >
                <UrgenciaBadge :nivel="n" size="lg" />
              </button>
            </div>
            <p v-if="nivelAtual" class="text-xs text-gray-500 dark:text-gray-400 mt-2 flex items-center gap-2">
              Nível atual: <UrgenciaBadge :nivel="nivelAtual" size="sm" />
            </p>

            <label class="block mt-5 text-sm font-semibold text-gray-800 dark:text-gray-200" for="just-urgencia">
              Justificativa *
            </label>
            <textarea
              id="just-urgencia"
              v-model="justificativa"
              rows="4"
              class="input w-full mt-1 resize-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
              placeholder="Descreva o motivo da alteração (mínimo 10 caracteres)"
            />
            <p
              class="text-xs mt-1"
              :class="justificativa.length >= 10 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'"
            >
              {{ justificativa.length }} / 10 caracteres mínimos
            </p>

            <p
              v-if="avisoSla"
              class="mt-4 text-xs text-amber-900 dark:text-amber-100 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2"
            >
              Atenção: elevar para este nível recalculará o prazo (SLA) do protocolo conforme a Matriz de Urgência.
            </p>
          </div>

          <footer
            class="shrink-0 px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex flex-col-reverse sm:flex-row gap-2 sm:justify-end bg-gray-50 dark:bg-gray-800/80"
          >
            <button
              type="button"
              class="btn-secondary min-h-[44px] focus-visible:ring-2 focus-visible:ring-slate-400"
              @click="$emit('fechar')"
            >
              Cancelar
            </button>
            <button
              type="button"
              class="btn-primary min-h-[44px] focus-visible:ring-2 focus-visible:ring-primary-500"
              :disabled="salvando || !formularioValido"
              @click="confirmar"
            >
              {{ salvando ? 'Salvando…' : 'Confirmar alteração' }}
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import UrgenciaBadge from '@/components/backoffice/common/UrgenciaBadge.vue'
import { NIVEIS_URGENCIA, normalizarUrgencia } from '@/utils/urgenciaHelpers'

const props = defineProps({
  aberto: Boolean,
  protocolo: { type: Object, default: null },
  salvando: { type: Boolean, default: false }
})

const emit = defineEmits(['fechar', 'confirmar'])

const niveis = NIVEIS_URGENCIA
const nivelSelecionado = ref('normal')
const justificativa = ref('')

const nivelAtual = computed(() => normalizarUrgencia(props.protocolo?.urgencia))

const avisoSla = computed(() => {
  const ativo = Boolean(
    props.protocolo?.urgenciaReduzSlaAtivo ?? props.protocolo?.urgencia_reduz_sla_ativo
  )
  return ativo && ['alta', 'critica'].includes(nivelSelecionado.value)
})

const formularioValido = computed(
  () => justificativa.value.trim().length >= 10 && nivelSelecionado.value !== nivelAtual.value
)

watch(
  () => props.aberto,
  (open) => {
    if (open && props.protocolo) {
      nivelSelecionado.value = normalizarUrgencia(props.protocolo.urgencia)
      justificativa.value = ''
    }
  }
)

function confirmar() {
  if (!formularioValido.value) return
  emit('confirmar', {
    urgencia: nivelSelecionado.value,
    justificativa: justificativa.value.trim()
  })
}
</script>