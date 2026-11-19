/**
 * Ditado por voz gratuito no navegador (Web Speech API — sem custo de API).
 * Suporte: Chrome/Edge/Android; Safari/iOS pode variar.
 */

import { ref, onBeforeUnmount } from 'vue'

function getSpeechRecognition() {
  if (typeof window === 'undefined') return null
  return window.SpeechRecognition || window.webkitSpeechRecognition || null
}

export function useSpeechDictation({ onFinalText, lang = 'pt-BR' } = {}) {
  const suportado = ref(Boolean(getSpeechRecognition()))
  const ouvindo = ref(false)
  const erro = ref(null)
  const parcial = ref('')

  let recognition = null

  function parar() {
    ouvindo.value = false
    parcial.value = ''
    if (recognition) {
      try {
        recognition.stop()
      } catch {
        /* já parado */
      }
    }
  }

  function iniciar() {
    erro.value = null
    const Ctor = getSpeechRecognition()
    if (!Ctor) {
      erro.value =
        'Seu navegador não suporta ditado por voz. Digite a descrição manualmente.'
      return false
    }

    if (recognition) {
      parar()
    }

    recognition = new Ctor()
    recognition.lang = lang
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onresult = (event) => {
      let finalChunk = ''
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        const text = result[0]?.transcript || ''
        if (result.isFinal) {
          finalChunk += text
        } else {
          interim += text
        }
      }
      parcial.value = interim.trim()
      if (finalChunk.trim() && typeof onFinalText === 'function') {
        onFinalText(finalChunk.trim())
      }
    }

    recognition.onerror = (event) => {
      if (event.error === 'aborted' || event.error === 'no-speech') {
        return
      }
      ouvindo.value = false
      parcial.value = ''
      const mensagens = {
        'not-allowed': 'Permissão do microfone negada.',
        'service-not-allowed': 'Ditado indisponível neste dispositivo.',
        network: 'Ditado precisa de internet (motor do navegador).'
      }
      erro.value =
        mensagens[event.error] ||
        'Não foi possível usar o ditado. Digite o texto manualmente.'
    }

    recognition.onend = () => {
      if (ouvindo.value) {
        try {
          recognition.start()
        } catch {
          ouvindo.value = false
        }
      }
    }

    try {
      recognition.start()
      ouvindo.value = true
      return true
    } catch {
      erro.value = 'Não foi possível iniciar o microfone.'
      return false
    }
  }

  function alternar() {
    if (ouvindo.value) {
      parar()
      return false
    }
    return iniciar()
  }

  onBeforeUnmount(() => {
    parar()
    recognition = null
  })

  return {
    suportado,
    ouvindo,
    erro,
    parcial,
    iniciar,
    parar,
    alternar
  }
}
