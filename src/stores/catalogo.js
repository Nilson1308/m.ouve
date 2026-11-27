import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { catalogoService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  mapCategoriaCatalogo,
  mapServicoCatalogo,
  mapServicoCatalogoPublico,
  payloadCategoriaCatalogo,
  payloadServicoCatalogo
} from '@/utils/catalogoMappers'
import { nomeCategoriaServico, ordemCategoriaServico } from '@/utils/catalogo'

function unwrapList(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  return []
}

export const useCatalogoStore = defineStore('catalogo', () => {
  const servicos = ref([])
  const categoriasCatalogo = ref([])
  const loadingServicos = ref(false)
  const loadingCategorias = ref(false)
  const loadingPwa = ref(false)
  const templates = ref([])
  const loadingTemplates = ref(false)
  const clonandoTemplate = ref(false)
  const duplicandoServicoId = ref(null)
  const erro = ref(null)
  const servicoSelecionado = ref(null)
  const configPwa = ref(null)
  const loadingConfigPwa = ref(false)

  const loading = computed(() => loadingPwa.value || loadingConfigPwa.value)
  const error = computed(() => erro.value)

  const totalServicos = computed(() => servicos.value.length)
  const servicosAtivos = computed(() => servicos.value.filter((s) => s.ativo !== false))

  const servicosPorCategoria = computed(() => {
    const grupos = {}

    servicosAtivos.value.forEach((servico) => {
      const categoria = nomeCategoriaServico(servico)
      const catObj = servico.categoria && typeof servico.categoria === 'object' ? servico.categoria : null
      if (!grupos[categoria]) {
        grupos[categoria] = {
          nome: categoria,
          slug: catObj?.slug || '',
          icone: catObj?.icone || '',
          descricao: catObj?.descricao || '',
          ordem: catObj?.ordem ?? ordemCategoriaServico(servico),
          servicos: []
        }
      }
      grupos[categoria].servicos.push(servico)
    })

    return Object.values(grupos).sort((a, b) => {
      const ordemA = ordemCategoriaServico(a.servicos[0])
      const ordemB = ordemCategoriaServico(b.servicos[0])
      return ordemA - ordemB
    })
  })

  function getServicoPorId(id) {
    if (id == null || id === '') return null
    return servicos.value.find((s) => String(s.id) === String(id)) || null
  }

  function selecionarServico(servico) {
    servicoSelecionado.value = servico || null
  }

  /** Catálogo público (PWA) — GET /catalogo-servicos */
  async function carregarCatalogo() {
    loadingPwa.value = true
    erro.value = null
    try {
      const data = await catalogoService.list()
      const lista = Array.isArray(data?.servicos) ? data.servicos : []
      servicos.value = lista.map(mapServicoCatalogoPublico).filter(Boolean)
      return { success: true }
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar categorias')
      servicos.value = []
      console.error('Erro ao carregar catálogo (PWA):', err)
      return { success: false }
    } finally {
      loadingPwa.value = false
    }
  }

  async function carregarConfigPwa() {
    loadingConfigPwa.value = true
    try {
      const data = await catalogoService.getConfigPwa()
      configPwa.value = data
      return { success: true, data }
    } catch (err) {
      console.warn('Config PWA indisponível, usando modo híbrido:', err)
      configPwa.value = { modo_abertura_pwa: 'hibrido', categorias: [] }
      return { success: false }
    } finally {
      loadingConfigPwa.value = false
    }
  }

  function configCategoriaPorRef(ref) {
    const raw = (ref || '').trim()
    if (!raw) return null
    const lista = configPwa.value?.categorias || []
    const legado = raw.toLowerCase()
    return (
      lista.find((c) => (c.slug || '').toLowerCase() === legado.replace(/\s+/g, '_')) ||
      lista.find((c) => (c.nome || '').toLowerCase() === raw.toLowerCase()) ||
      lista.find((c) => (c.slug || '').toLowerCase() === raw.toLowerCase())
    )
  }

  async function carregarCategoriasCatalogo() {
    loadingCategorias.value = true
    erro.value = null
    try {
      const { data } = await api.get('/backoffice/categorias-catalogo')
      categoriasCatalogo.value = unwrapList(data).map(mapCategoriaCatalogo)
      return categoriasCatalogo.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar categorias')
      throw err
    } finally {
      loadingCategorias.value = false
    }
  }

  async function criarCategoriaCatalogo(form) {
    loadingCategorias.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        '/backoffice/categorias-catalogo',
        payloadCategoriaCatalogo(form)
      )
      const novo = mapCategoriaCatalogo(data)
      categoriasCatalogo.value.push(novo)
      categoriasCatalogo.value.sort((a, b) => a.ordem - b.ordem || a.nome.localeCompare(b.nome))
      return novo
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar categoria')
      throw err
    } finally {
      loadingCategorias.value = false
    }
  }

  async function atualizarCategoriaCatalogo(id, form) {
    loadingCategorias.value = true
    erro.value = null
    try {
      const { data } = await api.put(
        `/backoffice/categorias-catalogo/${id}`,
        payloadCategoriaCatalogo(form)
      )
      const atualizado = mapCategoriaCatalogo(data)
      const idx = categoriasCatalogo.value.findIndex((c) => c.id === id)
      if (idx !== -1) categoriasCatalogo.value[idx] = atualizado
      categoriasCatalogo.value.sort((a, b) => a.ordem - b.ordem || a.nome.localeCompare(b.nome))
      return atualizado
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao atualizar categoria')
      throw err
    } finally {
      loadingCategorias.value = false
    }
  }

  async function excluirCategoriaCatalogo(id) {
    loadingCategorias.value = true
    erro.value = null
    try {
      await api.delete(`/backoffice/categorias-catalogo/${id}`)
      await carregarCategoriasCatalogo()
      return true
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao excluir categoria')
      throw err
    } finally {
      loadingCategorias.value = false
    }
  }

  async function carregarServicosCatalogo(params = {}) {
    loadingServicos.value = true
    erro.value = null
    try {
      const { data } = await api.get('/backoffice/servicos-catalogo', { params })
      servicos.value = unwrapList(data).map(mapServicoCatalogo)
      return servicos.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar catálogo de serviços')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  async function criarServicoCatalogo(form, camposUi, regrasProtocolo = []) {
    loadingServicos.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        '/backoffice/servicos-catalogo',
        payloadServicoCatalogo(form, camposUi, regrasProtocolo)
      )
      const novo = mapServicoCatalogo(data)
      servicos.value.push(novo)
      return novo
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar serviço')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  async function atualizarServicoCatalogo(
    id,
    form,
    camposUi,
    regrasProtocolo = [],
    opcoes = {}
  ) {
    loadingServicos.value = true
    erro.value = null
    try {
      const { data } = await api.put(
        `/backoffice/servicos-catalogo/${id}`,
        payloadServicoCatalogo(form, camposUi, regrasProtocolo, opcoes)
      )
      return _aplicarServicoNaLista(data, id)
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao atualizar serviço')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  function _aplicarServicoNaLista(data, idEsperado = null) {
    const atualizado = mapServicoCatalogo(data)
    const id = idEsperado || atualizado?.id
    const idx = servicos.value.findIndex((s) => String(s.id) === String(id))
    if (idx !== -1) servicos.value[idx] = atualizado
    return atualizado
  }

  async function carregarServicoCatalogoPorId(id) {
    erro.value = null
    try {
      const { data } = await api.get(`/backoffice/servicos-catalogo/${id}`)
      return _aplicarServicoNaLista(data, id)
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar serviço')
      throw err
    }
  }

  async function publicarRascunho(id, notaVersao = '') {
    loadingServicos.value = true
    erro.value = null
    try {
      const { data } = await api.post(`/backoffice/servicos-catalogo/${id}/publicar`, {
        nota_versao: (notaVersao || '').trim()
      })
      return _aplicarServicoNaLista(data, id)
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao publicar versão')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  async function descartarRascunho(id) {
    loadingServicos.value = true
    erro.value = null
    try {
      const { data } = await api.post(`/backoffice/servicos-catalogo/${id}/descartar-rascunho`)
      return _aplicarServicoNaLista(data, id)
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao descartar rascunho')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  async function buscarVersoes(id) {
    erro.value = null
    try {
      const { data } = await api.get(`/backoffice/servicos-catalogo/${id}/versoes`)
      return unwrapList(data)
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar histórico de versões')
      throw err
    }
  }

  async function restaurarVersao(id, numeroVersao) {
    loadingServicos.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        `/backoffice/servicos-catalogo/${id}/versoes/${numeroVersao}/restaurar`
      )
      return _aplicarServicoNaLista(data, id)
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao restaurar versão')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  /** DELETE — o backend desativa (soft) se houver protocolos vinculados. */
  async function excluirServicoCatalogo(id) {
    loadingServicos.value = true
    erro.value = null
    try {
      await api.delete(`/backoffice/servicos-catalogo/${id}`)
      const { data } = await api.get('/backoffice/servicos-catalogo')
      servicos.value = unwrapList(data).map(mapServicoCatalogo)
      return true
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao excluir serviço')
      throw err
    } finally {
      loadingServicos.value = false
    }
  }

  async function carregarServicosCatalogoSilencioso() {
    return carregarServicosCatalogo()
  }

  /** POST sandbox — simulação de conversa do serviço (dry-run no backoffice). */
  async function buscarTemplates() {
    loadingTemplates.value = true
    erro.value = null
    try {
      const { data } = await api.get('/backoffice/servicos-catalogo/templates')
      templates.value = unwrapList(data).map(mapServicoCatalogo)
      return templates.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao carregar modelos')
      templates.value = []
      throw err
    } finally {
      loadingTemplates.value = false
    }
  }

  /** Duplica serviço municipal (cópia inativa, unidade herdada). Body vazio. */
  async function duplicarServico(id) {
    duplicandoServicoId.value = id
    erro.value = null
    try {
      const { data } = await api.post(`/backoffice/servicos-catalogo/${id}/clonar`, {})
      const novo = mapServicoCatalogo(data)
      servicos.value.push(novo)
      return novo
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao duplicar serviço')
      throw err
    } finally {
      duplicandoServicoId.value = null
    }
  }

  async function clonarTemplate(templateId, unidadeResponsavelId) {
    clonandoTemplate.value = true
    erro.value = null
    try {
      const { data } = await api.post(`/backoffice/servicos-catalogo/${templateId}/clonar`, {
        unidade_responsavel_id: unidadeResponsavelId
      })
      const novo = mapServicoCatalogo(data)
      servicos.value.push(novo)
      return novo
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao instalar modelo')
      throw err
    } finally {
      clonandoTemplate.value = false
    }
  }

  async function sandboxServicoCatalogo(id, body) {
    try {
      const { data } = await api.post(`/backoffice/servicos-catalogo/${id}/sandbox`, body)
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro na simulação do fluxo')
      throw err
    }
  }

  function limparErro() {
    erro.value = null
  }

  return {
    servicos,
    categoriasCatalogo,
    loadingServicos,
    loadingCategorias,
    loadingPwa,
    templates,
    loadingTemplates,
    clonandoTemplate,
    duplicandoServicoId,
    loading,
    erro,
    error,
    servicoSelecionado,
    configPwa,
    totalServicos,
    servicosAtivos,
    servicosPorCategoria,
    getServicoPorId,
    selecionarServico,
    carregarCatalogo,
    carregarConfigPwa,
    configCategoriaPorRef,
    carregarCategoriasCatalogo,
    criarCategoriaCatalogo,
    atualizarCategoriaCatalogo,
    excluirCategoriaCatalogo,
    carregarServicosCatalogo,
    criarServicoCatalogo,
    atualizarServicoCatalogo,
    carregarServicoCatalogoPorId,
    publicarRascunho,
    descartarRascunho,
    buscarVersoes,
    restaurarVersao,
    excluirServicoCatalogo,
    carregarServicosCatalogoSilencioso,
    buscarTemplates,
    duplicarServico,
    clonarTemplate,
    sandboxServicoCatalogo,
    limparErro
  }
})