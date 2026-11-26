import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService, usuarioService } from '@/services/api'
import { getApiErrorCode, getApiErrorMessage } from '@/utils/apiError'
import { useAssinaturasStore } from '@/stores/assinaturas'
import { usuarioPode } from '@/composables/useRbac'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => user.value?.nome || '')
  const userCPF = computed(() => user.value?.cpf || '')

  const permissoes = computed(() => user.value?.permissoes || [])
  const isSuperAdmin = computed(() => Boolean(user.value?.is_superadmin))
  const isBackoffice = computed(() => {
    if (isSuperAdmin.value) return true
    if (user.value?.is_backoffice === true) return true
    if (user.value?.tipo_usuario === 'backoffice') return true
    if (user.value?.perfil?.id) return true
    if (permissoes.value.length > 0) return true
    return false
  })
  const isCidadao = computed(() => {
    if (!isAuthenticated.value) return false
    if (isBackoffice.value) return false
    if (user.value?.is_cidadao === true) return true
    if (user.value?.tipo_usuario === 'cidadao') return true
    return true
  })

  function mergeUsuarioPerfil(userData) {
    if (!userData) return
    user.value = { ...(user.value || {}), ...userData }
    localStorage.setItem('sinapse_user', JSON.stringify(user.value))
  }

  const podeAlterarUrgencia = computed(
    () => Boolean(user.value?.pode_alterar_urgencia) || isSuperAdmin.value
  )

  function can(codigo) {
    return usuarioPode({ permissoes: permissoes.value, isSuperAdmin: isSuperAdmin.value }, codigo)
  }

  async function refreshPerfil() {
    if (!token.value) return null
    try {
      const data = await usuarioService.obterPerfil()
      mergeUsuarioPerfil(data)
      return data
    } catch {
      return null
    }
  }

  function checkSession() {
    const savedToken = localStorage.getItem('sinapse_token')
    const savedUser = localStorage.getItem('sinapse_user')

    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  function setAuthData(userData, authToken, refreshToken) {
    user.value = userData
    token.value = authToken

    localStorage.setItem('sinapse_token', authToken)
    localStorage.setItem('sinapse_user', JSON.stringify(userData))
    if (refreshToken) {
      localStorage.setItem('sinapse_refresh_token', refreshToken)
    }
  }

  async function applyAuthResponse(data) {
    setAuthData(data.user, data.token, data.refresh_token)
    await refreshPerfil().catch(() => {})
  }

  function atualizarUsuarioPerfil(userData) {
    if (!userData) return
    user.value = userData
    localStorage.setItem('sinapse_user', JSON.stringify(userData))
  }

  async function loginComGovBr(code = 'dev-stub') {
    loading.value = true
    error.value = null

    try {
      const data = await authService.loginGovBr(code)
      await applyAuthResponse(data)
      return { success: true }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao autenticar com Gov.br')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function loginComSsoMunicipal(ssoToken = 'dev-stub') {
    loading.value = true
    error.value = null

    try {
      const data = await authService.loginSsoMunicipal(ssoToken)
      await applyAuthResponse(data)
      return { success: true }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao autenticar com SSO Municipal')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  /** Cadastro padrão (POST /auth/register) */
  async function loginPadrao(credentials) {
    loading.value = true
    error.value = null

    try {
      const payload = {
        nome: credentials.nome,
        cpf: credentials.cpf,
        email: credentials.email,
        telefone: credentials.telefone,
        senha: credentials.senha,
        endereco: {
          ...credentials.endereco,
          cep: credentials.endereco?.cep || credentials.cep
        }
      }

      const data = await authService.loginPadrao(payload)
      await applyAuthResponse(data)
      return { success: true }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Erro ao criar conta')
      return {
        success: false,
        error: error.value,
        code: getApiErrorCode(err)
      }
    } finally {
      loading.value = false
    }
  }

  async function verificarCpf(cpf) {
    try {
      return await authService.verificarCpf(cpf)
    } catch (err) {
      return {
        valido: false,
        disponivel: false,
        mensagem: getApiErrorMessage(err, 'Não foi possível validar o CPF.')
      }
    }
  }

  async function solicitarRecuperacaoSenha(cpf, canal) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.solicitarRecuperacaoSenha(cpf, canal)
      return { success: true, data }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Não foi possível solicitar a recuperação.')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function redefinirSenhaRecuperacao(token, novaSenha) {
    loading.value = true
    error.value = null
    try {
      const data = await authService.redefinirSenhaRecuperacao(token, novaSenha)
      return { success: true, data }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'Não foi possível redefinir a senha.')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function login(cpf, senha) {
    loading.value = true
    error.value = null

    try {
      const data = await authService.login(cpf, senha)
      await applyAuthResponse(data)
      return { success: true }
    } catch (err) {
      error.value = getApiErrorMessage(err, 'CPF ou senha inválidos')
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
    } catch {
      /* ignora se token expirado */
    }

    user.value = null
    token.value = null
    localStorage.removeItem('sinapse_token')
    localStorage.removeItem('sinapse_refresh_token')
    localStorage.removeItem('sinapse_user')
    try {
      useAssinaturasStore().limpar()
    } catch {
      /* fora do contexto Pinia */
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    userName,
    userCPF,
    permissoes,
    isSuperAdmin,
    isBackoffice,
    isCidadao,
    podeAlterarUrgencia,
    can,
    refreshPerfil,
    mergeUsuarioPerfil,
    checkSession,
    loginComGovBr,
    loginComSsoMunicipal,
    loginPadrao,
    login,
    logout,
    verificarCpf,
    solicitarRecuperacaoSenha,
    redefinirSenhaRecuperacao,
    atualizarUsuarioPerfil
  }
})
