<template>
  <Teleport to="body">
    <div
      v-if="aberto"
      class="fixed inset-0 z-[360] flex items-end sm:items-center justify-center bg-black/50 p-0 sm:p-4"
      role="presentation"
      @click.self="fechar"
    >
      <div
        class="w-full sm:max-w-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-t-2xl sm:rounded-2xl shadow-float max-h-[90dvh] flex flex-col overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-reabrir-titulo"
      >
        <header class="shrink-0 px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 id="modal-reabrir-titulo" class="text-lg font-bold text-gray-900 dark:text-white">
            Contestar conclusão
          </h3>
          <button type="button" class="btn-icon min-h-[44px] min-w-[44px]" aria-label="Fechar" @click="fechar">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </header>

        <div class="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Descreva o que ainda não foi resolvido. Sua solicitação voltará para a fila com um novo prazo.
          </p>

          <div>
            <label for="reabrir-motivo" class="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
              Motivo da contestação
              <span class="text-red-600" aria-hidden="true">*</span>
            </label>
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
              Explique o que ficou pendente ou por que o problema continua.
            </p>
            <textarea
              id="reabrir-motivo"
              v-model="motivo"
              rows="5"
              maxlength="5000"
              class="input w-full min-h-[120px]"
              :disabled="enviando"
            />
            <p class="text-xs mt-1" :class="motivoOk ? 'text-gray-500' : 'text-amber-700 dark:text-amber-300'">
              {{ motivo.trim().length }} / 10 caracteres mínimos
            </p>
          </div>

          <div>
            <p class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Fotos comprobatórias (opcional)</p>
            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class="min-h-[44px] min-w-[44px] px-3 btn-secondary text-sm inline-flex items-center gap-2"
                :disabled="enviando || enviandoAnexos"
                @click="abrirGaleria"
              >
                <PhotoIcon class="w-5 h-5" />
                Anexar fotos
              </button>
            </div>
            <input
              ref="galeriaRef"
              type="file"
              accept="image/*"
              multiple
              class="sr-only"
              @change="onArquivos"
            />
            <ul v-if="anexosPreview.length" class="mt-3 flex flex-wrap gap-2 text-xs text-gray-600 dark:text-gray-400">
              <li v-for="a in anexosPreview" :key="a.id">{{ a.nome }}</li>
            </ul>
          </div>

          <p v-if="erro" class="text-sm text-red-700 dark:text-red-300" role="alert">{{ erro }}</p>
        </div>

        <footer class="shrink-0 px-5 py-4 border-t border-gray-200 dark:border-gray-700 flex flex-col-reverse sm:flex-row gap-2 sm:justify-end bg-gray-50 dark:bg-gray-800/80">
          <button type="button" class="btn-secondary min-h-[44px]" :disabled="enviando" @click="fechar">
            Cancelar
          </button>
          <button
            type="button"
            class="btn-primary min-h-[44px]"
            :disabled="enviando || enviandoAnexos || !motivoOk"
            @click="confirmar"
          >
            {{ enviando ? 'Enviando…' : 'Confirmar contestação' }}
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { PhotoIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { protocolosService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { prepareChatImageFiles } from '@/utils/prepareChatImage'

const props = defineProps({
  aberto: Boolean,
  protocoloId: { type: String, required: true }
})

const emit = defineEmits(['fechar', 'concluido'])

const motivo = ref('')
const anexosIds = ref([])
const anexosPreview = ref([])
const enviando = ref(false)
const enviandoAnexos = ref(false)
const erro = ref('')
const galeriaRef = ref(null)

const motivoOk = computed(() => motivo.value.trim().length >= 10)

watch(
  () => props.aberto,
  (v) => {
    if (!v) return
    motivo.value = ''
    anexosIds.value = []
    anexosPreview.value = []
    erro.value = ''
  }
)

function fechar() {
  if (enviando.value) return
  emit('fechar')
}

function abrirGaleria() {
  galeriaRef.value?.click()
}

async function onArquivos(event) {
  const input = event.target
  const files = Array.from(input.files || [])
  input.value = ''
  if (!files.length) return
  enviandoAnexos.value = true
  erro.value = ''
  try {
    const preparados = await prepareChatImageFiles(files)
    const data = await protocolosService.anexarFotos(props.protocoloId, preparados)
    const lista = Array.isArray(data) ? data : data?.anexos || []
    for (const a of lista) {
      if (a?.id) {
        anexosIds.value.push(String(a.id))
        anexosPreview.value.push({
          id: String(a.id),
          nome: a.nome || a.nome_arquivo || 'Foto anexada'
        })
      }
    }
  } catch (err) {
    erro.value = getApiErrorMessage(err, 'Não foi possível enviar as fotos.')
  } finally {
    enviandoAnexos.value = false
  }
}

async function confirmar() {
  if (!motivoOk.value || enviando.value) return
  enviando.value = true
  erro.value = ''
  try {
    const data = await protocolosService.reabrir(props.protocoloId, {
      motivo: motivo.value.trim(),
      anexos_ids: anexosIds.value
    })
    emit('concluido', data)
    emit('fechar')
  } catch (err) {
    erro.value = getApiErrorMessage(err, 'Não foi possível reabrir o protocolo.')
  } finally {
    enviando.value = false
  }
}
</script>