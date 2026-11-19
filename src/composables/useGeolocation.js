import { ref } from 'vue'

export function useGeolocation() {
  const coords = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const supported = 'geolocation' in navigator

  async function getCurrentPosition(options = {}) {
    loading.value = true
    error.value = null

    if (!supported) {
      error.value = 'Geolocalização não é suportada neste navegador'
      loading.value = false
      return { success: false, error: error.value }
    }

    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          resolve,
          reject,
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
            ...options
          }
        )
      })

      coords.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: position.timestamp
      }

      loading.value = false
      return { success: true, coords: coords.value }
    } catch (err) {
      let errorMessage = 'Erro ao obter localização'
      
      switch (err.code) {
        case 1: // PERMISSION_DENIED
          errorMessage = 'Permissão de localização negada. Por favor, habilite nas configurações.'
          break
        case 2: // POSITION_UNAVAILABLE
          errorMessage = 'Localização indisponível no momento.'
          break
        case 3: // TIMEOUT
          errorMessage = 'Tempo limite excedido ao buscar localização.'
          break
      }

      error.value = errorMessage
      loading.value = false
      return { success: false, error: errorMessage }
    }
  }

  async function reverseGeocode(latitude, longitude) {
    const { atendimentosService } = await import('@/services/api')
    try {
      const data = await atendimentosService.geocodeReverso(latitude, longitude)
      return {
        success: true,
        address: data.endereco_completo || data.mensagem || ''
      }
    } catch {
      return { success: false, address: '' }
    }
  }

  return {
    coords,
    loading,
    error,
    supported,
    getCurrentPosition,
    reverseGeocode
  }
}
