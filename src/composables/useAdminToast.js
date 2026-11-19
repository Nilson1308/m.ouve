import { ref } from 'vue'

const toastAberto = ref(false)
const toastMensagem = ref('')
const toastErro = ref(false)
let toastTimer = null

export function useAdminToast() {
  function mostrarToast(mensagem, isErro = false, duracaoMs = null) {
    toastMensagem.value = mensagem
    toastErro.value = Boolean(isErro)
    toastAberto.value = true
    if (toastTimer) clearTimeout(toastTimer)
    const tempo = duracaoMs ?? (isErro ? 5500 : 4000)
    toastTimer = setTimeout(() => {
      toastAberto.value = false
    }, tempo)
  }

  return {
    toastAberto,
    toastMensagem,
    toastErro,
    mostrarToast
  }
}