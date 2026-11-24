<template>
  <section
    v-if="diligenciaAtiva"
    class="card border-2 border-amber-400 dark:border-amber-600 high-contrast:border-yellow-300 bg-gradient-to-br from-amber-50 to-white dark:from-amber-950/40 dark:to-gray-900 shadow-soft"
    :aria-labelledby="tituloId"
  >
    <div class="flex items-start gap-3 mb-4">
      <div
        class="w-12 h-12 rounded-avatar bg-amber-200 dark:bg-amber-900/50 flex items-center justify-center shrink-0"
        aria-hidden="true"
      >
        <ClipboardDocumentCheckIcon class="w-7 h-7 text-amber-900 dark:text-amber-200 high-contrast:text-yellow-300" />
      </div>
      <div class="min-w-0 flex-1">
        <h2 :id="tituloId" class="text-lg font-bold text-amber-950 dark:text-amber-50 high-contrast:text-yellow-300">
          Complementação solicitada
        </h2>
        <p class="text-sm text-amber-900/90 dark:text-amber-100 mt-1">
          <span class="font-semibold">{{ diligenciaAtiva.unidade_nome || 'Unidade municipal' }}</span>
          pediu informações adicionais.
        </p>
        <p class="text-xs text-amber-800 dark:text-amber-200 mt-2">
          Prazo para responder:
          <time :datetime="diligenciaAtiva.prazo_resposta" class="font-semibold">
            {{ prazoFormatado }}
          </time>
        </p>
        <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white mt-2 italic">
          O prazo de atendimento está pausado aguardando sua resposta.
        </p>
      </div>
    </div>

    <div class="rounded-card border border-amber-200 dark:border-amber-800 bg-white/80 dark:bg-gray-900/50 p-4 mb-4">
      <p class="text-xs font-bold uppercase tracking-wide text-amber-800 dark:text-amber-300 mb-2">Instrução</p>
      <p class="text-sm text-gray-900 dark:text-gray-100 whitespace-pre-line leading-relaxed">
        {{ diligenciaAtiva.pergunta }}
      </p>
      <p
        v-if="diligenciaAtiva.exige_anexo"
        class="text-xs font-semibold text-amber-900 dark:text-amber-200 mt-3"
      >
        (Obrigatório enviar ao menos 1 foto/anexo)
      </p>
    </div>

    <div
      v-if="sucesso"
      class="rounded-card border border-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 px-4 py-3 text-sm text-emerald-900 dark:text-emerald-100 mb-4"
      role="status"
    >
      Complementação enviada! Seu protocolo voltou para análise.
    </div>

    <form v-if="!sucesso" class="space-y-4" @submit.prevent="enviar">
      <div>
        <label for="diligencia-resposta" class="block text-sm font-semibold text-gray-900 dark:text-white mb-1">
          Sua resposta <span class="text-red-600" aria-hidden="true">*</span>
        </label>
        <textarea
          id="diligencia-resposta"
          v-model="resposta"
          rows="4"
          class="input w-full min-h-[96px] text-base"
          placeholder="Descreva as informações solicitadas de forma clara."
          :disabled="enviando"
          required
        />
      </div>

      <div>
        <p class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Fotos ou anexos</p>
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="min-h-[44px] inline-flex items-center gap-2 px-4 py-2 rounded-button border border-gray-300 dark:border-gray-600 text-sm font-medium"
            :disabled="enviando || enviandoAnexos"
            @click="abrirCamera"
          >
            <CameraIcon class="w-5 h-5" aria-hidden="true" />
            Tirar foto
          </button>
          <button
            type="button"
            class="min-h-[44px] inline-flex items-center gap-2 px-4 py-2 rounded-button border border-gray-300 dark:border-gray-600 text-sm font-medium"
            :disabled="enviando || enviandoAnexos"
            @click="abrirGaleria"
          >
            <PhotoIcon class="w-5 h-5" aria-hidden="true" />
            Escolher arquivo
          </button>
        </div>
        <input
          ref="cameraRef"
          type="file"
          accept="image/*"
          capture="environment"
          class="sr-only"
          tabindex="-1"
          @change="onArquivos"
        />
        <input
          ref="galeriaRef"
          type="file"
          accept="image/*"
          multiple
          class="sr-only"
          tabindex="-1"
          @change="onArquivos"
        />
        <p v-if="enviandoAnexos" class="text-xs text-primary-600 dark:text-primary-400 mt-2" role="status">
          Enviando anexos…
        </p>
        <ul v-if="anexosEnviados.length" class="mt-3 space-y-1 text-xs text-gray-600 dark:text-gray-400">
          <li v-for="a in anexosEnviados" :key="a.id">
            Anexo enviado: {{ a.nome || a.id }}
          </li>
        </ul>
      </div>

      <p v-if="erro" class="text-sm text-red-700 dark:text-red-300" role="alert">{{ erro }}</p>

      <button
        type="submit"
        class="w-full min-h-[48px] btn-primary font-bold"
        :disabled="!podeEnviar"
      >
        {{ enviando ? 'Enviando…' : 'Enviar complementação' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  CameraIcon,
  PhotoIcon,
  ClipboardDocumentCheckIcon
} from '@heroicons/vue/24/outline'
import { protocolosService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { formatarPrazoHumano } from '@/utils/diligenciaHelpers'
import { prepareChatImageFiles } from '@/utils/prepareChatImage'

const props = defineProps({
  protocoloId: { type: String, required: true },
  diligenciaAtiva: { type: Object, required: true }
})

const emit = defineEmits(['respondido'])

const tituloId = 'pwa-diligencia-ativa'
const resposta = ref('')
const anexosIds = ref([])
const anexosEnviados = ref([])
const enviando = ref(false)
const enviandoAnexos = ref(false)
const erro = ref('')
const sucesso = ref(false)
const cameraRef = ref(null)
const galeriaRef = ref(null)

const prazoFormatado = computed(() => formatarPrazoHumano(props.diligenciaAtiva?.prazo_resposta))

const podeEnviar = computed(() => {
  if (enviando.value || enviandoAnexos.value) return false
  if (!resposta.value.trim()) return false
  if (props.diligenciaAtiva?.exige_anexo && anexosIds.value.length === 0) return false
  return true
})

function abrirCamera() {
  cameraRef.value?.click()
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
        anexosEnviados.value.push({
          id: a.id,
          nome: a.nome || a.url?.split('/').pop()
        })
      }
    }
  } catch (e) {
    erro.value = getApiErrorMessage(
      e,
      'Não foi possível enviar o anexo. Tente novamente ou use uma foto já vinculada ao protocolo.'
    )
  } finally {
    enviandoAnexos.value = false
  }
}

async function enviar() {
  if (!podeEnviar.value) return
  enviando.value = true
  erro.value = ''
  try {
    await protocolosService.responderDiligencia(props.protocoloId, {
      resposta: resposta.value.trim(),
      anexos_ids: [...anexosIds.value]
    })
    sucesso.value = true
    emit('respondido')
  } catch (e) {
    erro.value = getApiErrorMessage(e, 'Não foi possível enviar sua resposta.')
  } finally {
    enviando.value = false
  }
}
</script>