import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/** Mesa municipal / Ouvidoria — mesma regra já usada na Mesa de Trabalho. */
export function usePerspectivaRadarMesa() {
  const authStore = useAuthStore()
  return computed(() => (authStore.user?.unidade_id ? '' : 'ouvidoria'))
}

/** Visão executiva (controladoria municipal; ouvidor mantém lente ouvidoria). */
export function usePerspectivaRadarExecutiva() {
  const authStore = useAuthStore()
  return computed(() => {
    if (authStore.user?.unidade_id) return ''
    const codigo = (authStore.user?.perfil_acesso?.codigo || authStore.user?.perfil_codigo || '')
      .toString()
      .toLowerCase()
    if (codigo.includes('ouvidor')) return 'ouvidoria'
    return ''
  })
}