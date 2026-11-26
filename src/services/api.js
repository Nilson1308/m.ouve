import axios from 'axios'
import router from '@/router'
import {
  mapDashboardEficiencia,
  mapDashboardQualidade,
  mapMapaCalorApi
} from '@/utils/dashboardMappers'
import {
  normalizarBriefing,
  normalizarConfigAgente
} from '@/services/agenteGestaoMappers'

// Configuração base do Axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Interceptor de Request - Adiciona token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sinapse_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // FormData: o browser deve definir Content-Type com boundary (Safari mobile quebra sem isso).
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor de Response - Tratamento de erros
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Token expirado - tentar refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('sinapse_refresh_token')
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        )

        const { token } = response.data
        localStorage.setItem('sinapse_token', token)

        // Retry da requisição original
        originalRequest.headers.Authorization = `Bearer ${token}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh falhou, fazer logout
        localStorage.removeItem('sinapse_token')
        localStorage.removeItem('sinapse_refresh_token')
        localStorage.removeItem('sinapse_user')
        const path = router.currentRoute.value?.path || ''
        if (path.startsWith('/backoffice')) {
          router.push('/backoffice/login')
        } else {
          router.push('/app/login')
        }
        return Promise.reject(refreshError)
      }
    }

    // Outros erros
    return Promise.reject(error)
  }
)

// ==================== AUTH SERVICES ====================

export const authService = {
  /**
   * Login com Gov.br
   */
  async loginGovBr(code) {
    const response = await api.post('/auth/govbr/callback', { code })
    return response.data
  },

  /**
   * Login com SSO Municipal
   */
  async loginSsoMunicipal(token) {
    const response = await api.post('/auth/sso-municipal/callback', { token })
    return response.data
  },

  /**
   * Cadastro/Login padrão
   */
  async loginPadrao(credentials) {
    const response = await api.post('/auth/register', credentials)
    return response.data
  },

  /**
   * Login com CPF e senha
   */
  async login(cpf, senha) {
    const response = await api.post('/auth/login', { cpf, senha })
    return response.data
  },

  /**
   * Logout
   */
  async logout() {
    await api.post('/auth/logout')
  },

  /**
   * Refresh token
   */
  async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  /** Valida CPF e indica se já existe na base (pré-cadastro). */
  async verificarCpf(cpf) {
    const response = await api.post('/auth/cpf/verificar', { cpf })
    return response.data
  },

  /** Solicita recuperação de senha por e-mail, SMS ou WhatsApp. */
  async solicitarRecuperacaoSenha(cpf, canal) {
    const response = await api.post('/auth/recuperar-senha/solicitar', { cpf, canal })
    return response.data
  },

  /** Conclui redefinição com token recebido no canal escolhido. */
  async redefinirSenhaRecuperacao(token, novaSenha) {
    const response = await api.post('/auth/recuperar-senha/redefinir', {
      token,
      nova_senha: novaSenha
    })
    return response.data
  },

  /** LGPD — solicita anonimização da conta. */
  async anonimizar({ refresh_token = null } = {}) {
    const response = await api.post('/usuario/anonimizar', { refresh_token })
    return response.data
  }
}

// ==================== PERFIL DO CIDADÃO ====================

export const usuarioService = {
  async obterPerfil() {
    const response = await api.get('/auth/me')
    return response.data
  },

  async atualizarPerfil(payload) {
    const response = await api.patch('/auth/me', payload)
    return response.data
  },

  async alterarSenha({ senha_atual, nova_senha, confirmar_nova_senha }) {
    const response = await api.post('/auth/me/alterar-senha', {
      senha_atual,
      nova_senha,
      confirmar_nova_senha: confirmar_nova_senha ?? nova_senha
    })
    return response.data
  },

  /** multipart/form-data — campo `avatar` */
  async enviarAvatar(arquivo) {
    const fd = new FormData()
    fd.append('avatar', arquivo, arquivo.name || 'avatar.webp')
    const response = await api.post('/auth/me/avatar', fd)
    return response.data
  },

  async removerAvatar() {
    const response = await api.delete('/auth/me/avatar')
    return response.data
  },

  async desativar({ refresh_token = null } = {}) {
    const response = await api.delete('/usuario/desativar', {
      data: { refresh_token }
    })
    return response.data
  }
}

// ==================== AVALIAÇÕES ====================

export const avaliacoesService = {
  async criar({ protocolo_id, nota, comentario = '' }) {
    const response = await api.post('/avaliacoes', {
      protocolo_id,
      nota,
      comentario
    })
    return response.data
  }
}

// ==================== PROTOCOLOS SERVICES ====================

export const protocolosService = {
  /**
   * Lista protocolos do usuário
   */
  async list(filters = {}) {
    const response = await api.get('/protocolos', { params: filters })
    return response.data
  },

  /**
   * Busca protocolo por ID
   */
  async get(id) {
    const response = await api.get(`/protocolos/${id}`)
    return response.data
  },

  /**
   * Cobrança de retorno pelo cidadão (SLA vencido) — POST sem trailing slash (v4.12).
   */
  async cobrar(protocoloId, { mensagem = '' } = {}) {
    const response = await api.post(
      `/protocolos/${encodeURIComponent(protocoloId)}/cobrar`,
      { mensagem }
    )
    return response.data
  },

  /**
   * Resposta à diligência (v4.14) — POST sem trailing slash.
   */
  async responderDiligencia(protocoloId, { resposta, anexos_ids = [] }) {
    const response = await api.post(
      `/protocolos/${encodeURIComponent(protocoloId)}/responder-diligencia`,
      { resposta, anexos_ids }
    )
    return response.data
  },

  /**
   * Anexa fotos ao protocolo (mesmo padrão multipart do create: fotos[]).
   * Retorna lista com { id, url, tipo }.
   */
  async anexarFotos(protocoloId, files) {
    const formData = new FormData()
    for (const file of files) {
      formData.append('fotos[]', file)
    }
    const response = await api.post(
      `/protocolos/${encodeURIComponent(protocoloId)}/anexos`,
      formData,
      { timeout: 120000 }
    )
    return response.data
  },

  /**
   * Registra avaliação CSAT (nota 1–5) no protocolo resolvido.
   */
  async avaliar(protocoloId, { nota, comentario = '' }) {
    const response = await api.post(`/app/protocolos/${encodeURIComponent(protocoloId)}/avaliar`, {
      nota,
      comentario
    })
    return response.data
  },

  /**
   * Contestação / reabertura (v4.15) — POST sem trailing slash.
   */
  async reabrir(protocoloId, { motivo, anexos_ids = [] }) {
    const response = await api.post(`/protocolos/${encodeURIComponent(protocoloId)}/reabrir`, {
      motivo,
      anexos_ids
    })
    return response.data
  },

  /**
   * Cria novo protocolo
   */
  async create(data) {
    // Se tiver arquivos, usar FormData
    if (data.fotos || data.audio) {
      const formData = new FormData()
      
      Object.keys(data).forEach(key => {
        if (key === 'fotos' && Array.isArray(data.fotos)) {
          data.fotos.forEach(foto => {
            formData.append('fotos[]', foto)
          })
        } else if (key === 'audio') {
          formData.append('audio', data.audio)
        } else if (key === 'dados_dinamicos') {
          formData.append(key, JSON.stringify(data[key] || {}))
        } else if (data[key] !== undefined && data[key] !== null) {
          formData.append(key, data[key])
        }
      })

      const response = await api.post('/protocolos', formData, {
        timeout: 120000
      })
      return response.data
    }

    // Sem arquivos, enviar JSON
    const response = await api.post('/protocolos', data)
    return response.data
  },

  /**
   * Adiciona comentário ao protocolo
   */
  async addComment(id, texto) {
    const response = await api.post(`/protocolos/${id}/comentarios`, { texto })
    return response.data
  },

  /**
   * Busca protocolos similares
   */
  async getSimilares(id) {
    const response = await api.get(`/protocolos/${id}/similares`)
    return response.data
  }
}

// ==================== CATÁLOGO DE SERVIÇOS ====================

export const catalogoService = {
  /** Lista categorias ativas do catálogo. */
  async listCategorias() {
    const response = await api.get('/catalogo-categorias')
    return response.data
  },

  /**
   * Lista serviços ativos com JSON Schema do formulário dinâmico.
   * @param {Object} params - ex.: { categoria: 'ouvidoria' | 'zeladoria_urbana' }
   */
  async list(params = {}) {
    const baseURL = (api.defaults.baseURL || '').replace(/\/$/, '')
    const url = new URL(`${baseURL}/catalogo-servicos`)
    Object.entries(params).forEach(([key, value]) => {
      if (value != null && value !== '') {
        url.searchParams.set(key, String(value))
      }
    })

    const headers = { Accept: 'application/json' }
    const token = localStorage.getItem('sinapse_token')
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers,
      credentials: 'omit'
    })

    if (!response.ok) {
      const err = new Error(`Catálogo indisponível (${response.status})`)
      err.response = { status: response.status }
      throw err
    }

    return response.json()
  }
}

/** Lookup de listas do sistema para campos dinâmicos (PWA). */
export const catalogoLookupService = {
  async listarUnidades(params = {}) {
    const response = await api.get('/catalogo/lookup/unidades', { params })
    const data = response.data
    return Array.isArray(data?.items) ? data.items : []
  },

  async listarEquipamentos(params = {}) {
    const response = await api.get('/catalogo/lookup/equipamentos', { params })
    const data = response.data
    return Array.isArray(data?.items) ? data.items : []
  }
}

/** Matriz de roteamento temático (Onda 3 — governança). */
export const matrizRoteamentoService = {
  async listar(servicoId) {
    const response = await api.get(
      `/backoffice/catalogo/servicos/${servicoId}/roteamento`
    )
    return Array.isArray(response.data) ? response.data : []
  },

  async criar(servicoId, payload) {
    const response = await api.post(
      `/backoffice/catalogo/servicos/${servicoId}/roteamento`,
      payload
    )
    return response.data
  },

  async atualizar(servicoId, regraId, payload) {
    const response = await api.patch(
      `/backoffice/catalogo/servicos/${servicoId}/roteamento/${regraId}`,
      payload
    )
    return response.data
  },

  async remover(servicoId, regraId) {
    await api.delete(
      `/backoffice/catalogo/servicos/${servicoId}/roteamento/${regraId}`
    )
  }
}

// ==================== ATENDIMENTOS (assistente + geocodificação) ====================

export const atendimentosService = {
  async analisarRelato(texto) {
    const response = await api.post('/atendimentos/assistente/analisar', { texto })
    return response.data
  },

  async transcreverAudio(audioBlob) {
    const formData = new FormData()
    const nome =
      audioBlob instanceof File
        ? audioBlob.name
        : `gravacao.${audioBlob.type?.includes('mp4') ? 'm4a' : 'webm'}`
    formData.append('audio', audioBlob, nome)

    const response = await api.post('/atendimentos/assistente/transcrever', formData, {
      timeout: 60000
    })
    return response.data
  },

  async geocodeReverso(latitude, longitude) {
    const response = await api.get('/atendimentos/geocode/reverse', {
      params: { latitude, longitude }
    })
    return response.data
  },

  async buscarEndereco(query) {
    const response = await api.get('/atendimentos/geocode/search', {
      params: { query }
    })
    return response.data
  }
}

/** @deprecated use atendimentosService — alias temporário para migração do frontend */
export const zeladoriaService = atendimentosService

// ==================== NOTIFICAÇÕES SERVICES ====================

/** Notificações internas (servidores / backoffice) — distinto de notificacoesCidadaoAppService (cidadão PWA) */
export const notificacoesInternasService = {
  async listar(params = {}) {
    const response = await api.get('/backoffice/notificacoes', { params })
    return response.data
  },

  async marcarLida(id) {
    const response = await api.post(`/backoffice/notificacoes/${id}/marcar-lida`)
    return response.data
  }
}

/** Textos padrão de despacho por unidade (painel setorial) */
export const textosPadraoService = {
  async listar() {
    const response = await api.get('/backoffice/textos-padrao')
    return response.data
  },

  async criar(payload) {
    const response = await api.post('/backoffice/textos-padrao', payload)
    return response.data
  },

  async atualizar(id, payload) {
    const response = await api.put(`/backoffice/textos-padrao/${id}`, payload)
    return response.data
  },

  async remover(id) {
    await api.delete(`/backoffice/textos-padrao/${id}`)
  }
}

// ==================== NOTIFICAÇÕES CIDADÃO (Onda 4 — /app/notificacoes) ====================

export const notificacoesCidadaoAppService = {
  async listar(params = {}) {
    const response = await api.get('/app/notificacoes', { params })
    return response.data
  },

  async marcarLida(id) {
    const response = await api.patch(`/app/notificacoes/${id}/marcar-lida`)
    return response.data
  },

  async obterVapidPublicKey() {
    const response = await api.get('/app/notificacoes/vapid-public-key')
    return response.data
  },

  async pushSubscribe(payload) {
    const response = await api.post('/app/notificacoes/push-subscribe', payload)
    return response.data
  }
}

// ==================== ADMIN SERVICES ====================

export const adminService = {
  /**
   * Estatísticas gerais
   */
  async getEstatisticas(dataInicio, dataFim, tipo = null) {
    const response = await api.get('/admin/estatisticas', {
      params: { data_inicio: dataInicio, data_fim: dataFim, tipo }
    })
    return response.data
  }
}

// ==================== DASHBOARD SERVICES ====================

export const dashboardService = {
  /**
   * Obtém dados de eficiência para dashboard executivo
   * @returns {Promise<Object>} Dados de TMA, SLA e ranking de unidades (formato da view)
   */
  async getEficiencia() {
    const response = await api.get('/backoffice/dashboard/eficiencia')
    return mapDashboardEficiencia(response.data)
  },

  /**
   * Pontos GIS para heatmap executivo
   * @param {Object} params - data_inicio, data_fim, categoria_id, servico_id, unidade_responsavel_id, status
   */
  async getMapaCalor(params = {}) {
    const response = await api.get('/backoffice/dashboard/mapa-calor', { params })
    return mapMapaCalorApi(response.data)
  },

  /**
   * Matriz SLA × satisfação por secretaria (protocolos resolvidos)
   * @param {Object} params - bairro, unidade_responsavel_id (opcionais)
   */
  async getQualidade(params = {}) {
    const response = await api.get('/backoffice/dashboard/qualidade', { params })
    return mapDashboardQualidade(response.data)
  }
}

// ==================== CHAT CONVERSACIONAL (RAG + LLM) ====================

export const chatService = {
  /**
   * Inicia nova sessão de chat com uma categoria
   * @param {string} categoriaInicial - Nome da categoria (ex: "Zeladoria Urbana")
   * @returns {Promise<{sessao: Object, mensagem: Object}>}
   */
  async iniciarSessao(categoriaInicial) {
    const response = await api.post('/chat/sessao', {
      categoria_inicial: categoriaInicial
    })
    return response.data
  },

  /**
   * Enfileira turno do cidadão (HTTP 202 — resposta da IA via polling).
   */
  async interagir(sessaoId, payload) {
    const {
      texto = '',
      localizacao = null,
      arquivos = [],
      confirmar_protocolo = false,
      dados_slot = null
    } = payload

    // Se tiver arquivos, usar FormData
    if (arquivos && arquivos.length > 0) {
      const formData = new FormData()
      formData.append('sessao_id', sessaoId)
      formData.append('texto', texto)
      if (confirmar_protocolo) {
        formData.append('confirmar_protocolo', 'true')
      }

      if (localizacao) {
        formData.append('localizacao', JSON.stringify(localizacao))
      }
      if (dados_slot) {
        formData.append('dados_slot', JSON.stringify(dados_slot))
      }

      arquivos.forEach(arquivo => {
        formData.append('midia', arquivo)
      })

      const response = await api.post('/chat/interagir', formData, {
        timeout: 120000
      })
      return response.data
    }

    // Sem arquivos, enviar JSON
    const body = {
      sessao_id: sessaoId,
      texto,
      localizacao,
      confirmar_protocolo: Boolean(confirmar_protocolo)
    }
    if (dados_slot) {
      body.dados_slot = dados_slot
    }
    const response = await api.post('/chat/interagir', body)
    return response.data
  },

  /**
   * Polling: mensagens da sessão ordenadas cronologicamente.
   */
  async listarMensagens(sessaoId) {
    const response = await api.get(`/chat/sessao/${sessaoId}/mensagens`)
    return response.data
  },

  /** Satisfação com a abertura da solicitação no chat (não é CSAT de protocolo resolvido). */
  async avaliarAbertura(sessaoId, { nota, comentario = '' }) {
    const response = await api.post(`/chat/sessao/${sessaoId}/avaliar-abertura`, {
      nota,
      comentario
    })
    return response.data
  }
}

// ==================== SLA & COBRANÇA (v4.12) ====================

export const diligenciaBackofficeService = {
  async abrir(protocoloId, body) {
    const { data } = await api.post(`/backoffice/protocolos/${protocoloId}/diligencias`, body)
    return data
  },

  async cancelar(diligenciaId, body = {}) {
    const { data } = await api.post(`/backoffice/diligencias/${diligenciaId}/cancelar`, body)
    return data
  }
}

export const matrizUrgenciaService = {
  async obterConfiguracao() {
    const { data } = await api.get('/backoffice/configuracoes/matriz-urgencia')
    return data
  },

  async salvarConfiguracao(patch) {
    const { data } = await api.patch('/backoffice/configuracoes/matriz-urgencia', patch)
    return data
  },

  async alterarUrgenciaProtocolo(protocoloId, body) {
    const { data } = await api.post(`/backoffice/protocolos/${protocoloId}/urgencia`, body)
    return data
  }
}

export const slaCobrancaService = {
  async obterConfiguracao() {
    const { data } = await api.get('/backoffice/configuracoes/sla-cobranca')
    return data
  },

  async salvarConfiguracao(patch) {
    const { data } = await api.patch('/backoffice/configuracoes/sla-cobranca', patch)
    return data
  },

  async listarAtrasados(params = {}) {
    const { data } = await api.get('/backoffice/relatorios/sla-atrasados', { params })
    return data
  },

  async exportarAtrasadosCsv(params = {}) {
    return api.get('/backoffice/relatorios/sla-atrasados/exportar', {
      params,
      responseType: 'blob'
    })
  },

  async dispararDigest(body = {}) {
    const { data } = await api.post('/backoffice/relatorios/sla-atrasados/disparar-agora', body)
    return data
  },

  async listarEnvios(params = {}) {
    const { data } = await api.get('/backoffice/relatorios/sla-atrasados/envios', { params })
    return data
  }
}

// ==================== AGENTE IA GESTÃO (v4.17) ====================

export const agenteGestaoService = {
  async obterConfiguracao() {
    const { data } = await api.get('/backoffice/configuracoes/agente-gestao')
    return normalizarConfigAgente(data)
  },

  async salvarConfiguracao(patch) {
    const { data } = await api.patch('/backoffice/configuracoes/agente-gestao', patch)
    return normalizarConfigAgente(data)
  },

  async obterBriefing(params = {}) {
    const { data } = await api.get('/backoffice/agente/briefing', { params })
    return normalizarBriefing(data)
  },

  async atualizarBriefing(params = {}) {
    const { data } = await api.get('/backoffice/agente/briefing', {
      params: { ...params, forcar: true }
    })
    return normalizarBriefing(data)
  },

  async avaliarInsight(briefingId, body) {
    const { data } = await api.post(`/backoffice/agente/briefing/${briefingId}/avaliar`, body)
    return data
  }
}

// Exportação default
export default api
