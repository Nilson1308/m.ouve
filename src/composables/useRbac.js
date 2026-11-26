import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/** Sinônimos usados na UI → códigos canônicos do backend */
const ALIASES = {
  'setorial.ler': 'painel_setorial.ler',
  'setorial.criar': 'painel_setorial.criar',
  'setorial.editar': 'painel_setorial.editar',
  'setorial.excluir': 'painel_setorial.excluir',
  'dashboards.ler': null
}

function resolveCodigo(codigo) {
  const c = (codigo || '').trim()
  if (ALIASES[c] === null) {
    return c
  }
  return ALIASES[c] ?? c
}

export function usuarioPode(store, codigo) {
  if (!codigo) return true
  if (store.isSuperAdmin) return true

  const permissoes = store.permissoes || []
  const resolved = resolveCodigo(codigo)

  if (codigo === 'dashboards.ler' || resolved === 'dashboards.ler') {
    return (
      permissoes.includes('mesa_trabalho.ler') ||
      permissoes.includes('mapa_ia.ler')
    )
  }

  if (permissoes.includes(resolved)) return true

  return false
}

export function useRbac() {
  const authStore = useAuthStore()

  const permissoes = computed(() => authStore.permissoes)
  const isSuperAdmin = computed(() => authStore.isSuperAdmin)
  const isBackoffice = computed(() => authStore.isBackoffice)
  const isCidadao = computed(() => authStore.isCidadao)
  const podeAlterarUrgencia = computed(
    () => Boolean(authStore.user?.pode_alterar_urgencia) || authStore.isSuperAdmin
  )

  function can(codigo) {
    return usuarioPode(authStore, codigo)
  }

  return { can, permissoes, isSuperAdmin, isBackoffice, isCidadao, podeAlterarUrgencia }
}