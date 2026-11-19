<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="aberto"
        class="fixed inset-0 z-[10060] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="$emit('fechar')"
      >
        <div
          class="w-full max-w-lg max-h-[85vh] flex flex-col rounded-2xl bg-white dark:bg-gray-800 shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
          role="dialog"
          aria-labelledby="historico-versoes-title"
        >
          <header
            class="shrink-0 px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-start justify-between gap-3"
          >
            <div>
              <h3 id="historico-versoes-title" class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <ClockIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                Histórico de versões
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Publicadas em produção (PWA). Versão atual: v{{ versaoAtual }}.
              </p>
            </div>
            <button
              type="button"
              class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Fechar"
              @click="$emit('fechar')"
            >
              <XMarkIcon class="w-5 h-5 text-gray-500" />
            </button>
          </header>

          <div class="flex-1 overflow-y-auto px-5 py-4">
            <div v-if="carregando" class="py-12 flex justify-center">
              <div class="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            </div>

            <p v-else-if="erro" class="text-sm text-red-600 dark:text-red-400 text-center py-8">{{ erro }}</p>

            <p v-else-if="!versoes.length" class="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              Nenhuma versão publicada ainda. Publique um rascunho para criar o histórico.
            </p>

            <ol v-else class="relative border-l-2 border-gray-200 dark:border-gray-600 ml-3 space-y-6">
              <li
                v-for="v in versoes"
                :key="v.id || v.numero_versao"
                class="relative pl-6"
              >
                <span
                  class="absolute -left-[7px] top-1.5 w-3 h-3 rounded-full ring-4 ring-white dark:ring-gray-800"
                  :class="
                    v.numero_versao === versaoAtual
                      ? 'bg-primary-500'
                      : 'bg-gray-300 dark:bg-gray-600'
                  "
                />
                <div
                  class="rounded-xl border p-4 transition-colors"
                  :class="
                    v.numero_versao === versaoAtual
                      ? 'border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-950/20'
                      : 'border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/40'
                  "
                >
                  <div class="flex items-center justify-between gap-2 flex-wrap">
                    <span class="text-sm font-bold text-gray-900 dark:text-white">
                      v{{ v.numero_versao }}
                      <span
                        v-if="v.numero_versao === versaoAtual"
                        class="ml-1 text-[10px] font-semibold uppercase text-primary-600 dark:text-primary-400"
                      >
                        atual
                      </span>
                    </span>
                    <time class="text-[11px] text-gray-500 dark:text-gray-400 tabular-nums">
                      {{ formatarData(v.publicado_em) }}
                    </time>
                  </div>
                  <p v-if="v.publicado_por_nome" class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Por {{ v.publicado_por_nome }}
                  </p>
                  <p
                    v-if="v.nota_versao"
                    class="text-sm text-gray-700 dark:text-gray-300 mt-2 italic"
                  >
                    «{{ v.nota_versao }}»
                  </p>
                  <p v-else class="text-xs text-gray-400 dark:text-gray-500 mt-2">Sem nota de versão</p>

                  <button
                    v-if="v.numero_versao !== versaoAtual"
                    type="button"
                    class="mt-3 text-xs font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 disabled:opacity-50"
                    :disabled="restaurando === v.numero_versao"
                    @click="$emit('restaurar', v.numero_versao)"
                  >
                    {{
                      restaurando === v.numero_versao
                        ? 'Restaurando…'
                        : 'Restaurar para rascunho'
                    }}
                  </button>
                </div>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ClockIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useCatalogoStore } from '@/stores/catalogo'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  servicoId: { type: String, default: '' },
  versaoAtual: { type: Number, default: 1 },
  restaurando: { type: [Number, null], default: null }
})

defineEmits(['fechar', 'restaurar'])

const catalogoStore = useCatalogoStore()
const versoes = ref([])
const carregando = ref(false)
const erro = ref('')

function formatarData(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return iso
  }
}

async function carregar() {
  if (!props.servicoId) return
  carregando.value = true
  erro.value = ''
  try {
    versoes.value = await catalogoStore.buscarVersoes(props.servicoId)
  } catch (e) {
    erro.value = getApiErrorMessage(e, 'Não foi possível carregar o histórico.')
    versoes.value = []
  } finally {
    carregando.value = false
  }
}

watch(
  () => [props.aberto, props.servicoId],
  ([open]) => {
    if (open) carregar()
  }
)
</script>