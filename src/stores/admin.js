import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  mapPerfilAcesso,
  mapUnidadeAdmin,
  mapUsuarioAdmin,
  payloadPerfilAcesso,
  payloadUnidadeAdmin,
  payloadUsuarioAdmin
} from '@/utils/adminMappers'

function unwrapList(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  return []
}

export const useAdminStore = defineStore('admin', () => {
  const unidades = ref([])
  const usuarios = ref([])
  const perfisAcesso = ref([]) // Perfis dinâmicos do backend
  const loading = ref(false)
  const loadingPerfis = ref(false)
  const erro = ref(null)

  const unidadesAtivas = computed(() => unidades.value.filter((u) => u.ativo))

  const usuariosAtivos = computed(() => usuarios.value.filter((u) => u.ativo))

  const totalUnidades = computed(() => unidades.value.length)
  const totalUsuarios = computed(() => usuarios.value.length)

  async function carregarUnidades(opcoes = {}) {
    const { silencioso = false } = opcoes
    if (!silencioso) loading.value = true
    erro.value = null

    try {
      const { data } = await api.get('/backoffice/unidades')
      unidades.value = unwrapList(data).map(mapUnidadeAdmin)
      return unidades.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar unidades')
      console.error('Erro ao carregar unidades:', err)
      throw err
    } finally {
      if (!silencioso) loading.value = false
    }
  }

  async function criarUnidade(dados) {
    loading.value = true
    erro.value = null

    try {
      const { data } = await api.post('/backoffice/unidades', payloadUnidadeAdmin(dados))
      const nova = mapUnidadeAdmin(data)
      unidades.value.push(nova)
      return nova
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar unidade')
      console.error('Erro ao criar unidade:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function atualizarUnidade(id, dados) {
    loading.value = true
    erro.value = null

    try {
      const { data } = await api.put(
        `/backoffice/unidades/${id}`,
        payloadUnidadeAdmin({ ...dados, ativo: dados.ativo })
      )
      const atualizada = mapUnidadeAdmin(data)
      const index = unidades.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        unidades.value[index] = atualizada
      } else {
        unidades.value.push(atualizada)
      }
      return atualizada
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao atualizar unidade')
      console.error('Erro ao atualizar unidade:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function carregarUsuarios(params = {}) {
    loading.value = true
    erro.value = null

    try {
      const { data } = await api.get('/backoffice/usuarios', { params })
      usuarios.value = unwrapList(data).map(mapUsuarioAdmin)
      return usuarios.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar usuários')
      console.error('Erro ao carregar usuários:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function criarUsuario(dados) {
    loading.value = true
    erro.value = null

    try {
      const { data } = await api.post(
        '/backoffice/usuarios',
        payloadUsuarioAdmin(dados, perfisAcesso.value)
      )
      const novo = mapUsuarioAdmin(data)
      usuarios.value.push(novo)
      await carregarUnidades({ silencioso: true }).catch(() => {})
      return {
        ...novo,
        senha_inicial: data.senha_inicial || null
      }
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar usuário')
      console.error('Erro ao criar usuário:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function atualizarUsuario(id, dados) {
    loading.value = true
    erro.value = null

    try {
      const { data } = await api.put(
        `/backoffice/usuarios/${id}`,
        payloadUsuarioAdmin(dados, perfisAcesso.value)
      )
      const atualizado = mapUsuarioAdmin(data)
      const index = usuarios.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        usuarios.value[index] = atualizado
      }
      await carregarUnidades({ silencioso: true }).catch(() => {})
      return atualizado
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao atualizar usuário')
      console.error('Erro ao atualizar usuário:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function resetarSenhaUsuario(id) {
    loading.value = true
    erro.value = null

    try {
      const { data } = await api.post(`/backoffice/usuarios/${id}/resetar-senha`, {})
      return {
        sucesso: data.sucesso !== false,
        mensagem: data.mensagem || 'Senha redefinida com sucesso.',
        senha: data.senha,
        email: data.email,
        usuario_id: data.usuario_id
      }
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao resetar senha')
      console.error('Erro ao resetar senha:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // === PERFIS DE ACESSO (RBAC Dinâmico) ===
  async function carregarPerfisAcesso(opcoes = {}) {
    const { silencioso = false } = opcoes
    if (!silencioso) loadingPerfis.value = true
    erro.value = null

    try {
      const { data } = await api.get('/backoffice/perfis-acesso')
      perfisAcesso.value = unwrapList(data).map(mapPerfilAcesso)
      return perfisAcesso.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar perfis de acesso')
      console.error('Erro ao carregar perfis:', err)
      throw err
    } finally {
      if (!silencioso) loadingPerfis.value = false
    }
  }

  async function criarPerfilAcesso(dados) {
    loadingPerfis.value = true
    erro.value = null

    try {
      const { data } = await api.post(
        '/backoffice/perfis-acesso',
        payloadPerfilAcesso(dados)
      )
      const novo = mapPerfilAcesso(data)
      perfisAcesso.value.push(novo)
      return novo
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar perfil de acesso')
      console.error('Erro ao criar perfil:', err)
      throw err
    } finally {
      loadingPerfis.value = false
    }
  }

  async function atualizarPerfilAcesso(id, dados) {
    loadingPerfis.value = true
    erro.value = null

    try {
      const { data } = await api.put(
        `/backoffice/perfis-acesso/${id}`,
        payloadPerfilAcesso(dados)
      )
      const atualizado = mapPerfilAcesso(data)
      const index = perfisAcesso.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        perfisAcesso.value[index] = atualizado
      }
      return atualizado
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao atualizar perfil de acesso')
      console.error('Erro ao atualizar perfil:', err)
      throw err
    } finally {
      loadingPerfis.value = false
    }
  }

  async function excluirPerfilAcesso(id) {
    loadingPerfis.value = true
    erro.value = null

    try {
      await api.delete(`/backoffice/perfis-acesso/${id}`)
      const index = perfisAcesso.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        perfisAcesso.value.splice(index, 1)
      }
      return true
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao excluir perfil de acesso')
      console.error('Erro ao excluir perfil:', err)
      throw err
    } finally {
      loadingPerfis.value = false
    }
  }

  function getPerfilPorId(perfilId) {
    // Buscar primeiro nos perfis dinâmicos
    const perfilDinamico = perfisAcesso.value.find((p) => p.id === perfilId || p.slug === perfilId)
    if (perfilDinamico) return perfilDinamico
    
    // Fallback para perfis legados (se ainda existirem)
    return null
  }

  function limparErro() {
    erro.value = null
  }

  const totalPerfis = computed(() => perfisAcesso.value.length)

  return {
    // Estado
    unidades,
    usuarios,
    perfisAcesso,
    loading,
    loadingPerfis,
    erro,
    
    // Computeds
    unidadesAtivas,
    usuariosAtivos,
    totalUnidades,
    totalUsuarios,
    totalPerfis,
    
    // Actions - Unidades
    carregarUnidades,
    criarUnidade,
    atualizarUnidade,
    
    // Actions - Usuários
    carregarUsuarios,
    criarUsuario,
    atualizarUsuario,
    resetarSenhaUsuario,
    
    // Actions - Perfis de Acesso
    carregarPerfisAcesso,
    criarPerfilAcesso,
    atualizarPerfilAcesso,
    excluirPerfilAcesso,
    
    // Helpers
    getPerfilPorId,
    limparErro
  }
})