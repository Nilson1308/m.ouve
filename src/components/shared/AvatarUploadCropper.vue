<template>
  <div class="inline-flex flex-col items-center gap-3">
    <div class="relative" :style="{ width: `${tamanhoExibicao}px`, height: `${tamanhoExibicao}px` }">
      <div
        class="w-full h-full rounded-full overflow-hidden flex items-center justify-center shadow-md ring-2"
        :class="theme === 'backoffice'
          ? 'ring-slate-600/50 bg-gradient-to-br from-primary-500 to-cyan-600'
          : 'ring-gray-200 dark:ring-gray-700 bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400'"
      >
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          alt=""
          class="w-full h-full object-cover"
        />
        <span
          v-else
          class="font-bold text-white high-contrast:text-black"
          :class="tamanhoExibicao >= 96 ? 'text-3xl' : 'text-sm'"
          aria-hidden="true"
        >
          {{ iniciais }}
        </span>
      </div>
      <button
        type="button"
        class="absolute bottom-0 right-0 min-w-[2.75rem] min-h-[2.75rem] rounded-full flex items-center justify-center shadow-md border-2 transition-transform hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        :class="theme === 'backoffice'
          ? 'bg-slate-800 border-slate-600 text-white'
          : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300'"
        :aria-label="avatarUrl ? 'Alterar foto de perfil' : 'Adicionar foto de perfil'"
        :disabled="carregando"
        @click="abrirSeletor"
      >
        <CameraIcon class="w-5 h-5" aria-hidden="true" />
      </button>
    </div>

    <div class="flex flex-wrap items-center justify-center gap-2">
      <button
        v-if="avatarUrl"
        type="button"
        class="text-xs font-semibold underline-offset-2 hover:underline disabled:opacity-50"
        :class="theme === 'backoffice'
          ? 'text-red-400 hover:text-red-300'
          : 'text-red-600 dark:text-red-400'"
        :disabled="carregando"
        @click="remover"
      >
        Remover foto
      </button>
    </div>

    <p
      v-if="feedback"
      class="text-xs text-center max-w-xs"
      :class="feedbackErro
        ? 'text-red-600 dark:text-red-400'
        : 'text-emerald-600 dark:text-emerald-400'"
      role="status"
    >
      {{ feedback }}
    </p>

    <input
      ref="inputArquivoRef"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="sr-only"
      :aria-label="'Selecionar imagem de perfil'"
      @change="aoSelecionarArquivo"
    />

    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="cropAberto"
          class="fixed inset-0 z-[10050] flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="avatar-crop-title"
          @click.self="fecharCrop"
        >
          <div
            ref="dialogCropRef"
            class="w-full max-w-md rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90dvh]"
            :class="theme === 'backoffice'
              ? 'bg-gray-900 border border-gray-700 text-white'
              : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700'"
            @keydown.esc.prevent="fecharCrop"
          >
            <header class="shrink-0 px-5 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 id="avatar-crop-title" class="text-lg font-bold">Ajustar foto</h2>
              <p class="text-xs mt-1 opacity-80">Arraste para posicionar e use o zoom</p>
            </header>

            <div class="flex-1 min-h-0 overflow-y-auto p-5 flex flex-col items-center gap-4">
              <div
                class="relative touch-none select-none"
                :style="{ width: `${VIEW_SIZE}px`, height: `${VIEW_SIZE}px` }"
              >
                <canvas
                  ref="canvasPreviewRef"
                  :width="VIEW_SIZE"
                  :height="VIEW_SIZE"
                  class="rounded-full border-2 border-primary-500/60 shadow-inner cursor-grab active:cursor-grabbing"
                  :class="theme === 'backoffice' ? 'bg-gray-800' : 'bg-gray-100 dark:bg-gray-800'"
                  aria-label="Área de recorte — arraste para reposicionar"
                  @pointerdown="iniciarArraste"
                  @pointermove="moverArraste"
                  @pointerup="finalizarArraste"
                  @pointercancel="finalizarArraste"
                  @pointerleave="finalizarArraste"
                />
                <div
                  class="pointer-events-none absolute inset-0 rounded-full ring-4 ring-white/30 dark:ring-black/20"
                  aria-hidden="true"
                />
              </div>

              <label class="w-full max-w-xs text-sm font-medium flex flex-col gap-2">
                <span>Zoom</span>
                <input
                  v-model.number="zoomSlider"
                  type="range"
                  min="100"
                  max="300"
                  step="1"
                  class="w-full accent-primary-600"
                  @input="aplicarZoomSlider"
                />
              </label>
            </div>

            <footer class="shrink-0 flex gap-2 p-5 border-t border-gray-200 dark:border-gray-700">
              <button type="button" class="btn-secondary flex-1" @click="fecharCrop">Cancelar</button>
              <button
                type="button"
                class="btn-primary flex-1"
                :disabled="exportando"
                @click="confirmarCrop"
              >
                {{ exportando ? 'Processando…' : 'Usar foto' }}
              </button>
            </footer>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { CameraIcon } from '@heroicons/vue/24/outline'
import { usuarioService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useFormatacao } from '@/composables/useFormatacao'

const props = defineProps({
  avatarUrl: { type: String, default: '' },
  nome: { type: String, default: '' },
  theme: {
    type: String,
    default: 'pwa',
    validator: (v) => ['pwa', 'backoffice'].includes(v)
  },
  tamanhoExibicao: { type: Number, default: 96 }
})

const emit = defineEmits(['atualizado', 'erro'])

const AVATAR_MAX_BYTES = 2 * 1024 * 1024
const TIPOS_VALIDOS = new Set(['image/jpeg', 'image/png', 'image/webp'])
const VIEW_SIZE = 280
const EXPORT_SIZE = 512

const { gerarIniciais } = useFormatacao()

const inputArquivoRef = ref(null)
const canvasPreviewRef = ref(null)
const dialogCropRef = ref(null)
const cropAberto = ref(false)
const carregando = ref(false)
const exportando = ref(false)
const feedback = ref('')
const feedbackErro = ref(false)
const zoomSlider = ref(100)

const imagem = ref(null)
const escala = ref(1)
const minEscala = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const arrastando = ref(false)
const ultimoPonteiro = ref({ x: 0, y: 0 })

const iniciais = computed(() => gerarIniciais(props.nome || '?'))

function limparFeedback() {
  feedback.value = ''
  feedbackErro.value = false
}

function abrirSeletor() {
  limparFeedback()
  inputArquivoRef.value?.click()
}

function validarArquivo(file) {
  if (!file) return 'Nenhum arquivo selecionado.'
  if (!TIPOS_VALIDOS.has(file.type)) {
    return 'Use JPEG, PNG ou WebP.'
  }
  if (file.size > AVATAR_MAX_BYTES) {
    return 'A imagem deve ter no máximo 2 MB.'
  }
  return null
}

function aoSelecionarArquivo(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  const erro = validarArquivo(file)
  if (erro) {
    feedbackErro.value = true
    feedback.value = erro
    emit('erro', erro)
    return
  }
  const url = URL.createObjectURL(file)
  const img = new Image()
  img.onload = () => {
    imagem.value = img
    inicializarCrop()
    cropAberto.value = true
    nextTick(() => {
      dialogCropRef.value?.querySelector('button')?.focus()
      desenharPreview()
    })
  }
  img.onerror = () => {
    URL.revokeObjectURL(url)
    feedbackErro.value = true
    feedback.value = 'Não foi possível ler a imagem.'
  }
  img.src = url
}

function inicializarCrop() {
  const img = imagem.value
  if (!img) return
  const cover = Math.max(VIEW_SIZE / img.width, VIEW_SIZE / img.height)
  minEscala.value = cover
  escala.value = cover
  offsetX.value = (VIEW_SIZE - img.width * cover) / 2
  offsetY.value = (VIEW_SIZE - img.height * cover) / 2
  zoomSlider.value = 100
}

function desenharPreview() {
  const canvas = canvasPreviewRef.value
  const img = imagem.value
  if (!canvas || !img) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, VIEW_SIZE, VIEW_SIZE)
  ctx.save()
  ctx.beginPath()
  ctx.arc(VIEW_SIZE / 2, VIEW_SIZE / 2, VIEW_SIZE / 2, 0, Math.PI * 2)
  ctx.clip()
  const dw = img.width * escala.value
  const dh = img.height * escala.value
  ctx.drawImage(img, offsetX.value, offsetY.value, dw, dh)
  ctx.restore()
}

function limitarPosicao() {
  const img = imagem.value
  if (!img) return
  const dw = img.width * escala.value
  const dh = img.height * escala.value
  if (dw <= VIEW_SIZE) {
    offsetX.value = (VIEW_SIZE - dw) / 2
  } else {
    offsetX.value = Math.min(0, Math.max(VIEW_SIZE - dw, offsetX.value))
  }
  if (dh <= VIEW_SIZE) {
    offsetY.value = (VIEW_SIZE - dh) / 2
  } else {
    offsetY.value = Math.min(0, Math.max(VIEW_SIZE - dh, offsetY.value))
  }
}

function iniciarArraste(e) {
  if (!cropAberto.value) return
  arrastando.value = true
  ultimoPonteiro.value = { x: e.clientX, y: e.clientY }
  e.currentTarget.setPointerCapture?.(e.pointerId)
}

function moverArraste(e) {
  if (!arrastando.value) return
  const dx = e.clientX - ultimoPonteiro.value.x
  const dy = e.clientY - ultimoPonteiro.value.y
  ultimoPonteiro.value = { x: e.clientX, y: e.clientY }
  offsetX.value += dx
  offsetY.value += dy
  limitarPosicao()
  desenharPreview()
}

function finalizarArraste(e) {
  if (!arrastando.value) return
  arrastando.value = false
  try {
    e.currentTarget?.releasePointerCapture?.(e.pointerId)
  } catch {
    /* ignore */
  }
}

function aplicarZoomSlider() {
  const img = imagem.value
  if (!img) return
  const fator = zoomSlider.value / 100
  const nova = minEscala.value * fator
  const cx = VIEW_SIZE / 2
  const cy = VIEW_SIZE / 2
  const relX = (cx - offsetX.value) / escala.value
  const relY = (cy - offsetY.value) / escala.value
  escala.value = nova
  offsetX.value = cx - relX * nova
  offsetY.value = cy - relY * nova
  limitarPosicao()
  desenharPreview()
}

function fecharCrop() {
  cropAberto.value = false
  if (imagem.value?.src?.startsWith('blob:')) {
    URL.revokeObjectURL(imagem.value.src)
  }
  imagem.value = null
}

function exportarBlob() {
  return new Promise((resolve, reject) => {
    const img = imagem.value
    if (!img) {
      reject(new Error('Sem imagem'))
      return
    }
    const canvas = document.createElement('canvas')
    canvas.width = EXPORT_SIZE
    canvas.height = EXPORT_SIZE
    const ctx = canvas.getContext('2d')
    const sx = -offsetX.value / escala.value
    const sy = -offsetY.value / escala.value
    const sw = VIEW_SIZE / escala.value
    const sh = VIEW_SIZE / escala.value
    ctx.drawImage(img, sx, sy, sw, sh, 0, 0, EXPORT_SIZE, EXPORT_SIZE)
    const tentar = (mime, qualidade) => {
      canvas.toBlob(
        (blob) => {
          if (blob) resolve(blob)
          else if (mime === 'image/webp') tentar('image/jpeg', qualidade)
          else reject(new Error('Falha ao exportar imagem'))
        },
        mime,
        qualidade
      )
    }
    tentar('image/webp', 0.85)
  })
}

async function confirmarCrop() {
  exportando.value = true
  limparFeedback()
  try {
    const blob = await exportarBlob()
    const ext = blob.type === 'image/png' ? 'png' : blob.type.includes('webp') ? 'webp' : 'jpg'
    const file = new File([blob], `avatar.${ext}`, { type: blob.type || 'image/webp' })
    carregando.value = true
    fecharCrop()
    const usuario = await usuarioService.enviarAvatar(file)
    feedbackErro.value = false
    feedback.value = 'Foto atualizada.'
    emit('atualizado', usuario)
  } catch (e) {
    feedbackErro.value = true
    feedback.value = getApiErrorMessage(e, 'Não foi possível enviar a foto.')
    emit('erro', feedback.value)
  } finally {
    exportando.value = false
    carregando.value = false
  }
}

async function remover() {
  if (!props.avatarUrl) return
  carregando.value = true
  limparFeedback()
  try {
    const usuario = await usuarioService.removerAvatar()
    feedbackErro.value = false
    feedback.value = 'Foto removida.'
    emit('atualizado', usuario)
  } catch (e) {
    feedbackErro.value = true
    feedback.value = getApiErrorMessage(e, 'Não foi possível remover a foto.')
    emit('erro', feedback.value)
  } finally {
    carregando.value = false
  }
}

watch(cropAberto, (aberto) => {
  document.body.style.overflow = aberto ? 'hidden' : ''
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  fecharCrop()
})
</script>