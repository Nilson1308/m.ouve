/**
 * Composable para gerenciamento de cores e status
 * Sistema de design semântico para Ouvidoria e Zeladoria
 */

export function useStatusColors() {
  
  // Mapeamento de cores para status de Zeladoria
  const zeladoriaColors = {
    triagem_ia: {
      bg: 'bg-primary-100',
      text: 'text-primary-800',
      border: 'border-primary-500',
      ring: 'ring-primary-500/20',
      hex: '#3b82f6'
    },
    validacao: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      border: 'border-purple-500',
      ring: 'ring-purple-500/20',
      hex: '#8b5cf6'
    },
    aguardando_equipe: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-500',
      ring: 'ring-amber-500/20',
      hex: '#f59e0b'
    },
    em_deslocamento: {
      bg: 'bg-orange-100',
      text: 'text-orange-800',
      border: 'border-orange-500',
      ring: 'ring-orange-500/20',
      hex: '#f59e0b'
    },
    em_execucao: {
      bg: 'bg-teal-100',
      text: 'text-teal-800',
      border: 'border-teal-500',
      ring: 'ring-teal-500/20',
      hex: '#14b8a6'
    },
    concluido: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-500',
      ring: 'ring-green-500/20',
      hex: '#10b981'
    },
    nao_procedente: {
      bg: 'bg-gray-100',
      text: 'text-gray-600',
      border: 'border-gray-400',
      ring: 'ring-gray-400/20',
      hex: '#6b7280'
    }
  }

  // Mapeamento de cores para status de Ouvidoria
  const ouvidoriaColors = {
    triagem: {
      bg: 'bg-primary-100',
      text: 'text-primary-800',
      border: 'border-primary-500',
      ring: 'ring-primary-500/20',
      hex: '#3b82f6'
    },
    analise: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      border: 'border-purple-500',
      ring: 'ring-purple-500/20',
      hex: '#8b5cf6'
    },
    encaminhado: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-500',
      ring: 'ring-amber-500/20',
      hex: '#f59e0b'
    },
    respondido: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-500',
      ring: 'ring-green-500/20',
      hex: '#10b981'
    },
    arquivado: {
      bg: 'bg-gray-100',
      text: 'text-gray-600',
      border: 'border-gray-400',
      ring: 'ring-gray-400/20',
      hex: '#6b7280'
    }
  }

  // Cores para tipos de manifestação
  const manifestacaoColors = {
    denuncia: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-500',
      hex: '#ef4444'
    },
    reclamacao: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-500',
      hex: '#f59e0b'
    },
    sugestao: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-500',
      hex: '#3b82f6'
    },
    elogio: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-500',
      hex: '#10b981'
    }
  }

  // Cores para níveis de urgência
  const urgenciaColors = {
    baixa: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-500',
      hex: '#10b981'
    },
    media: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-500',
      hex: '#f59e0b'
    },
    alta: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-500',
      hex: '#ef4444'
    },
    critica: {
      bg: 'bg-red-200',
      text: 'text-red-900',
      border: 'border-red-600',
      hex: '#dc2626'
    }
  }

  // Cores para categorias
  const categoriaColors = {
    'via_publica': '#3b82f6',
    'iluminacao': '#f59e0b',
    'limpeza': '#10b981',
    'calcada': '#8b5cf6',
    'arborizacao': '#059669',
    'sinalizacao': '#dc2626',
  }

  /**
   * Obtém classes de cor para um status
   * @param {string} status - Status do protocolo
   * @param {string} tipo - Tipo: 'zeladoria' ou 'ouvidoria'
   * @returns {object} Objeto com classes CSS
   */
  function getStatusColors(status, tipo = 'zeladoria') {
    const normalizedStatus = status.toLowerCase().replace(/-/g, '_')
    
    if (tipo === 'zeladoria') {
      return zeladoriaColors[normalizedStatus] || zeladoriaColors.triagem_ia
    } else if (tipo === 'ouvidoria') {
      return ouvidoriaColors[normalizedStatus] || ouvidoriaColors.triagem
    }
    
    return zeladoriaColors.triagem_ia
  }

  /**
   * Obtém classes para tipo de manifestação
   * @param {string} tipo - Tipo da manifestação
   * @returns {object} Objeto com classes CSS
   */
  function getManifestacaoColors(tipo) {
    const normalizedTipo = tipo.toLowerCase()
    return manifestacaoColors[normalizedTipo] || manifestacaoColors.sugestao
  }

  /**
   * Obtém classes para nível de urgência
   * @param {string} nivel - Nível de urgência
   * @returns {object} Objeto com classes CSS
   */
  function getUrgenciaColors(nivel) {
    const normalizedNivel = nivel.toLowerCase()
    return urgenciaColors[normalizedNivel] || urgenciaColors.baixa
  }

  /**
   * Obtém cor hexadecimal para categoria
   * @param {string} categoria - Nome da categoria
   * @returns {string} Código hexadecimal da cor
   */
  function getCategoriaColor(categoria) {
    const normalized = categoria.toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_')
    return categoriaColors[normalized] || '#3b82f6'
  }

  /**
   * Gera classes CSS para card com borda lateral colorida
   * @param {string} status - Status do protocolo
   * @param {string} tipo - Tipo do protocolo
   * @returns {string} Classes CSS
   */
  function getCardBorderClass(status, tipo = 'zeladoria') {
    const colors = getStatusColors(status, tipo)
    return `border-l-4 ${colors.border}`
  }

  /**
   * Gera background gradient para header
   * @param {string} color - Cor hexadecimal
   * @returns {string} Estilo inline para gradient
   */
  function getGradientStyle(color) {
    return `background: linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`
  }

  /**
   * Obtém classe de badge completa
   * @param {string} status - Status
   * @param {string} tipo - Tipo
   * @returns {string} Classe CSS completa
   */
  function getBadgeClass(status, tipo = 'zeladoria') {
    const normalized = status.toLowerCase().replace(/-/g, '_')
    
    if (tipo === 'zeladoria') {
      return `badge-zeladoria-${normalized.replace(/_/g, '-')}`
    } else if (tipo === 'ouvidoria') {
      return `badge-ouvidoria-${normalized.replace(/_/g, '-')}`
    }
    
    return 'badge'
  }

  /**
   * Compatibilidade com sistema antigo
   * @param {string} statusLegado - Status no formato antigo
   * @returns {string} Status no formato novo
   */
  function mapLegacyStatus(statusLegado) {
    const mapping = {
      'em_analise': 'triagem_ia',
      'em_andamento': 'em_deslocamento',
      'resolvido': 'concluido',
      'rejeitado': 'nao_procedente'
    }
    return mapping[statusLegado] || statusLegado
  }

  return {
    // Getters
    getStatusColors,
    getManifestacaoColors,
    getUrgenciaColors,
    getCategoriaColor,
    getCardBorderClass,
    getGradientStyle,
    getBadgeClass,
    
    // Mappers
    mapLegacyStatus,
    
    // Constants
    zeladoriaColors,
    ouvidoriaColors,
    manifestacaoColors,
    urgenciaColors,
    categoriaColors
  }
}
