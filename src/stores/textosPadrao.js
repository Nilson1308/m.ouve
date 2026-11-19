import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

function mapTexto(api) {
  return {
    id: api.id,
    unidade: api.unidade,
    unidadeNome: api.unidade_nome || '',
    unidadeSigla: api.unidade_sigla || '',
    titulo: api.titulo || '',
    texto: api.texto || '',
    ativo: api.ativo !== false,
    criadoEm: api.criado_em,
    atualizadoEm: api.atualizado_em
  }
}

export const useTextosPadraoStore = defineStore('textosPadrao', () => {
  const itens = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const erro = ref(null)
  const semPermissaoUnidade = ref(false)

  const ativos = computed(() => itens.value.filter((t) => t.ativo))
  const inativos = computed(() => itens.value.filter((t) => !t.ativo))

  async function carregar() {
    loading.value = true
    erro.value = null
    semPermissaoUnidade.value = false
    try {
      const { data } = await api.get('/backoffice/textos-padrao')
      itens.value = (data.results || []).map(mapTexto)
      return itens.value
    } catch (e) {
      const status = e?.response?.status
      if (status === 403) {
        semPermissaoUnidade.value = true
        erro.value =
          'Sua conta não está vinculada a uma secretaria. Peça ao administrador para definir sua unidade.'
      } else {
        erro.value = getApiErrorMessage(
          e,
          'Não foi possível carregar os textos padrão da unidade.'
        )
      }
      itens.value = []
      throw e
    } finally {
      loading.value = false
    }
  }

  const total = computed(() => itens.value.length)

  async function criar(payload) {
    saving.value = true
    erro.value = null
    try {
      const { data } = await api.post('/backoffice/textos-padrao', payload)
      const mapped = mapTexto(data)
      itens.value.push(mapped)
      itens.value.sort((a, b) => a.titulo.localeCompare(b.titulo, 'pt-BR'))
      return mapped
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível criar o texto.')
      throw e
    } finally {
      saving.value = false
    }
  }

  async function atualizar(id, payload) {
    saving.value = true
    erro.value = null
    try {
      const { data } = await api.put(`/backoffice/textos-padrao/${id}`, payload)
      const mapped = mapTexto(data)
      const idx = itens.value.findIndex((t) => t.id === id)
      if (idx >= 0) itens.value[idx] = mapped
      return mapped
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível salvar alterações.')
      throw e
    } finally {
      saving.value = false
    }
  }

  async function remover(id) {
    saving.value = true
    erro.value = null
    try {
      await api.delete(`/backoffice/textos-padrao/${id}`)
      itens.value = itens.value.filter((t) => t.id !== id)
    } catch (e) {
      erro.value = getApiErrorMessage(e, 'Não foi possível excluir o texto.')
      throw e
    } finally {
      saving.value = false
    }
  }

  async function alternarAtivo(item) {
    return atualizar(item.id, {
      titulo: item.titulo,
      texto: item.texto,
      ativo: !item.ativo
    })
  }

  return {
    itens,
    loading,
    saving,
    erro,
    semPermissaoUnidade,
    ativos,
    inativos,
    carregar,
    criar,
    atualizar,
    remover,
    alternarAtivo,
    total
  }
})
