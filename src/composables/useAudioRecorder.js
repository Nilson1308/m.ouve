import { ref } from 'vue'
import { atendimentosService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

const MIME_CANDIDATES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/mp4',
  'audio/ogg;codecs=opus'
]

function pickMimeType() {
  if (typeof MediaRecorder === 'undefined') return ''
  for (const mime of MIME_CANDIDATES) {
    if (MediaRecorder.isTypeSupported(mime)) return mime
  }
  return ''
}

export function useAudioRecorder() {
  const recording = ref(false)
  const audioBlob = ref(null)
  const error = ref(null)
  const supported =
    typeof navigator !== 'undefined' &&
    !!navigator.mediaDevices?.getUserMedia &&
    typeof MediaRecorder !== 'undefined'

  let mediaRecorder = null
  let audioChunks = []
  let mediaStream = null
  let mimeType = 'audio/webm'

  function releaseStream() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop())
      mediaStream = null
    }
  }

  async function startRecording() {
    error.value = null
    if (!supported) {
      error.value = 'Gravação de áudio não é suportada neste navegador.'
      return { success: false, error: error.value }
    }

    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true
        }
      })
      mimeType = pickMimeType() || 'audio/webm'
      mediaRecorder = mimeType
        ? new MediaRecorder(mediaStream, { mimeType })
        : new MediaRecorder(mediaStream)
      audioChunks = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data?.size > 0) {
          audioChunks.push(event.data)
        }
      }

      mediaRecorder.start(250)
      recording.value = true
      return { success: true }
    } catch (err) {
      releaseStream()
      recording.value = false
      const denied = err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError'
      error.value = denied
        ? 'Permissão do microfone negada. Libere o acesso nas configurações do navegador.'
        : 'Erro ao acessar o microfone.'
      return { success: false, error: error.value }
    }
  }

  function cancelRecording() {
    if (mediaRecorder && recording.value) {
      mediaRecorder.onstop = null
      try {
        mediaRecorder.stop()
      } catch {
        /* noop */
      }
    }
    releaseStream()
    recording.value = false
    audioChunks = []
    mediaRecorder = null
  }

  function stopRecording() {
    return new Promise((resolve) => {
      if (!mediaRecorder || !recording.value) {
        resolve(null)
        return
      }

      mediaRecorder.onstop = () => {
        const type = mimeType || mediaRecorder.mimeType || 'audio/webm'
        const blob = audioChunks.length
          ? new Blob(audioChunks, { type })
          : null
        audioBlob.value = blob
        releaseStream()
        recording.value = false
        mediaRecorder = null
        audioChunks = []
        resolve(blob)
      }

      try {
        mediaRecorder.stop()
      } catch {
        releaseStream()
        recording.value = false
        resolve(null)
      }
    })
  }

  async function transcribeAudio(blob) {
    if (!blob || blob.size < 200) {
      return {
        success: false,
        error: 'Áudio muito curto. Grave novamente.'
      }
    }

    const ext = blob.type.includes('mp4') ? 'm4a' : blob.type.includes('ogg') ? 'ogg' : 'webm'
    const file = new File([blob], `gravacao.${ext}`, { type: blob.type || 'audio/webm' })

    try {
      const data = await atendimentosService.transcreverAudio(file)
      const text = (data.texto || '').trim()
      if (!text) {
        return { success: false, error: 'Não foi possível entender o áudio.' }
      }
      return { success: true, text, confianca: data.confianca }
    } catch (err) {
      return {
        success: false,
        error: getApiErrorMessage(err, 'Falha ao transcrever o áudio.')
      }
    }
  }

  return {
    recording,
    audioBlob,
    error,
    supported,
    startRecording,
    stopRecording,
    cancelRecording,
    transcribeAudio
  }
}
