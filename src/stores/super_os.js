import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { mapSugestaoSuperOS, mapSuperOSDetalhe } from '@/utils/superOsMappers'

export const useSuperOSStore = defineStore('super_os', () => {
  const sugestoes = ref([])
  const loading = ref(false)
  const erro = ref(null)
  const ultimaAtualizacao = ref(null)
  const ultimaSuperOS = ref(null)
  const superOsAtual = ref(null)
  const loadingDetalhe = ref(false)

  const totalSugestoes = computed(() => sugestoes.value.length)
  const totalProtocolosAgrupáveis = computed(() =>
    sugestoes.value.reduce(
      (acc, sug) => acc + (sug.quantidade || sug.protocolo_ids?.length || sug.protocolos?.length || 0),
      0
    )
  )

  const idsComSugestaoIa = computed(() => {
    const ids = new Set()
    for (const s of sugestoes.value) {
      for (const pid of s.protocolo_ids || []) {
        ids.add(String(pid))
      }
    }
    return ids
  })

  function indiceProtocolos(protocolosLista = []) {
    return new Map((protocolosLista || []).map((p) => [String(p.id), p]))
  }

  function protocoloTemSugestaoIa(protocoloId) {
    if (!protocoloId) return false
    return idsComSugestaoIa.value.has(String(protocoloId))
  }

  function sugestaoParaProtocolo(protocoloId) {
    const alvo = String(protocoloId)
    return (
      sugestoes.value.find((s) =>
        (s.protocolo_ids || []).some((pid) => String(pid) === alvo)
      ) || null
    )
  }

  function atualizarListaAposRemoverProtocolo(protocoloId, superOsIdAnexar = null) {
    const pid = String(protocoloId)
    sugestoes.value = sugestoes.value
      .map((s) => {
        if (!(s.protocolo_ids || []).some((id) => String(id) === pid)) {
          return s
        }
        const novosIds = (s.protocolo_ids || []).filter((id) => String(id) !== pid)
        if (s.tipo_acao === 'criar' && novosIds.length < 2) {
          return null
        }
        if (!novosIds.length) {
          return null
        }
        return {
          ...s,
          protocolo_ids: novosIds,
          quantidade: novosIds.length,
          protocolos: (s.protocolos || []).filter((p) => String(p.id) !== pid)
        }
      })
      .filter(Boolean)
  }

  async function buscarSugestoes(protocolosLista = []) {
    loading.value = true
    erro.value = null
    try {
      const { data } = await api.get('/backoffice/super-os/sugestoes')
      const lista = data.sugestoes || []
      const index = indiceProtocolos(protocolosLista)
      sugestoes.value = lista.map((item) => mapSugestaoSuperOS(item, index))
      ultimaAtualizacao.value = new Date().toISOString()
      return sugestoes.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao buscar sugestões de agrupamento')
      sugestoes.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  async function criarSuperOSMapa(payload) {
    loading.value = true
    erro.value = null
    try {
      const body = {
        titulo_resumo: payload.titulo_resumo || payload.titulo,
        protocolos_ids: payload.protocolos_ids,
        descricao_geral: payload.descricao_geral || ''
      }
      const { data } = await api.post('/backoffice/super-os/agrupar-mapa', body)
      ultimaSuperOS.value = data.super_os || null
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar Super OS')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function anexarProtocolo(superOsId, protocoloId) {
    loading.value = true
    erro.value = null
    try {
      const { data } = await api.post(`/backoffice/super-os/${superOsId}/anexar`, {
        protocolo_id: protocoloId
      })
      if (data.super_os) {
        ultimaSuperOS.value = data.super_os
      }
      atualizarListaAposRemoverProtocolo(protocoloId, superOsId)
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao anexar protocolo à Super OS')
      throw err
    } finally {
      loading.value = false
    }
  }

  /** Aprova sugestão tipo `criar` */
  async function aprovarSugestao(sugestao) {
    const ids =
      sugestao.protocolo_ids ||
      (sugestao.protocolos || []).map((p) => p.id).filter(Boolean)
    if (!ids.length) {
      throw new Error('Sugestão sem protocolos vinculados.')
    }
    const data = await criarSuperOSMapa({
      titulo_resumo: sugestao.titulo_resumo,
      protocolos_ids: ids
    })
    sugestoes.value = sugestoes.value.filter((s) => s.id !== sugestao.id)
    return data
  }

  /** Anexa todos os protocolos de uma sugestão tipo `anexar` */
  async function anexarSugestao(sugestao) {
    const superOsId = sugestao.super_os_id
    if (!superOsId) {
      throw new Error('Sugestão de anexação sem Super OS de destino.')
    }
    const ids =
      sugestao.protocolo_ids ||
      (sugestao.protocolos || []).map((p) => p.id).filter(Boolean)
    if (!ids.length) {
      throw new Error('Sugestão sem protocolos para anexar.')
    }

    loading.value = true
    erro.value = null
    let ultimo = null
    try {
      for (const protocoloId of ids) {
        const { data } = await api.post(`/backoffice/super-os/${superOsId}/anexar`, {
          protocolo_id: protocoloId
        })
        ultimo = data
        atualizarListaAposRemoverProtocolo(protocoloId, superOsId)
      }
      if (ultimo?.super_os) {
        ultimaSuperOS.value = ultimo.super_os
      }
      sugestoes.value = sugestoes.value.filter((s) => s.id !== sugestao.id)
      return ultimo
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao anexar protocolos à Super OS')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function criarSuperOSRetroativa(sugestao) {
    loading.value = true
    erro.value = null
    try {
      const ids =
        sugestao.protocolo_ids ||
        (sugestao.protocolos || []).map((p) => p.id).filter(Boolean)
      const body = {
        protocolo_ancora_id: sugestao.protocolo_ancora_id,
        protocolos_ids: ids,
        titulo_resumo: sugestao.titulo_resumo || sugestao.titulo,
        descricao_geral: sugestao.descricao_geral || ''
      }
      const { data } = await api.post('/backoffice/super-os/retroativa', body)
      if (data.super_os) {
        ultimaSuperOS.value = data.super_os
      }
      for (const pid of ids) {
        atualizarListaAposRemoverProtocolo(pid)
      }
      if (sugestao.protocolo_ancora_id) {
        atualizarListaAposRemoverProtocolo(sugestao.protocolo_ancora_id)
      }
      sugestoes.value = sugestoes.value.filter((s) => s.id !== sugestao.id)
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao criar Super OS retroativa')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function executarSugestao(sugestao) {
    if (sugestao.tipo_acao === 'anexar') {
      return anexarSugestao(sugestao)
    }
    if (sugestao.tipo_acao === 'criar_retroativa') {
      return criarSuperOSRetroativa(sugestao)
    }
    return aprovarSugestao(sugestao)
  }

  async function integrarAncoraSuperOS(superOsId) {
    loading.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        `/backoffice/super-os/${superOsId}/integrar-ancora`
      )
      if (data.super_os) {
        ultimaSuperOS.value = data.super_os
      }
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(
        err,
        'Não foi possível integrar a OS existente à Super OS.'
      )
      throw err
    } finally {
      loading.value = false
    }
  }

  async function despacharSuperOS(superOsId, payload) {
    loading.value = true
    erro.value = null
    try {
      const { data } = await api.post(
        `/backoffice/super-os/${superOsId}/despachar`,
        payload
      )
      if (data.super_os) {
        ultimaSuperOS.value = data.super_os
      }
      return data
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Erro ao despachar Super OS')
      throw err
    } finally {
      loading.value = false
    }
  }

  function limparErro() {
    erro.value = null
  }

  async function carregarDetalhes(superOsId) {
    loadingDetalhe.value = true
    erro.value = null
    try {
      const { data } = await api.get(`/backoffice/super-os/${superOsId}`)
      superOsAtual.value = mapSuperOSDetalhe(data)
      return superOsAtual.value
    } catch (err) {
      erro.value = getApiErrorMessage(err, 'Não foi possível carregar o dossiê da Super OS.')
      superOsAtual.value = null
      throw err
    } finally {
      loadingDetalhe.value = false
    }
  }

  function limparSuperOsAtual() {
    superOsAtual.value = null
  }

  /** Mapa protocolo UUID → sugestão (reativo para Kanban/Lista). */
  const indiceSugestaoPorProtocolo = computed(() => {
    const mapa = new Map()
    for (const s of sugestoes.value) {
      for (const pid of s.protocolo_ids || []) {
        mapa.set(String(pid), s)
      }
    }
    return mapa
  })

  function sugestaoResumoProtocolo(protocoloId) {
    const s = indiceSugestaoPorProtocolo.value.get(String(protocoloId))
    if (!s) return null
    return {
      tipo_acao: s.tipo_acao || 'criar',
      titulo: s.titulo_resumo,
      quantidade: s.quantidade,
      super_os_codigo: s.super_os_codigo
    }
  }

  return {
    sugestoes,
    loading,
    erro,
    ultimaAtualizacao,
    ultimaSuperOS,
    superOsAtual,
    loadingDetalhe,
    totalSugestoes,
    totalProtocolosAgrupáveis,
    idsComSugestaoIa,
    indiceSugestaoPorProtocolo,
    sugestaoResumoProtocolo,
    buscarSugestoes,
    aprovarSugestao,
    anexarProtocolo,
    anexarSugestao,
    executarSugestao,
    criarSuperOSMapa,
    despacharSuperOS,
    criarSuperOSRetroativa,
    integrarAncoraSuperOS,
    protocoloTemSugestaoIa,
    sugestaoParaProtocolo,
    limparErro,
    carregarDetalhes,
    limparSuperOsAtual
  }
})