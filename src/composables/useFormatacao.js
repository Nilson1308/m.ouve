/**
 * Composable para formatação de dados
 * Utilizado em toda a aplicação para consistência
 */

export function useFormatacao() {
  /**
   * Formata data relativa (ex: "Há 2 horas", "Ontem", "Há 3 dias")
   * @param {string|Date} data - Data a ser formatada
   * @returns {string} Data formatada
   */
  function formatarDataRelativa(data) {
    const date = new Date(data)
    const hoje = new Date()
    const diffMs = hoje - date
    const diffMinutos = Math.floor(diffMs / (1000 * 60))
    const diffHoras = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMinutos < 1) return 'Agora há pouco'
    if (diffMinutos < 60) return `Há ${diffMinutos} min`
    if (diffHoras < 24) return `Há ${diffHoras}h`
    if (diffDias === 1) return 'Ontem'
    if (diffDias < 7) return `Há ${diffDias} dias`
    if (diffDias < 30) {
      const semanas = Math.floor(diffDias / 7)
      return `Há ${semanas} ${semanas === 1 ? 'semana' : 'semanas'}`
    }
    
    return date.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: '2-digit',
      year: diffDias > 365 ? 'numeric' : undefined
    })
  }

  /**
   * Formata data completa (ex: "13/11/2024 às 14:30")
   * @param {string|Date} data - Data a ser formatada
   * @returns {string} Data formatada
   */
  function formatarDataCompleta(data) {
    const date = new Date(data)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  /**
   * Formata SLA de forma legível
   * @param {object} sla - Objeto SLA { vencido, horasRestantes }
   * @returns {string} SLA formatado
   */
  function formatarSLA(sla) {
    if (!sla) return '—'
    const horasTotal = Math.floor(Math.abs(Number(sla.horasRestantes) || 0))

    if (sla.vencido) {
      if (horasTotal < 24) return `Atrasado ${horasTotal}h`
      const dias = Math.floor(horasTotal / 24)
      const horas = horasTotal % 24
      return horas > 0 ? `Atrasado ${dias}d ${horas}h` : `Atrasado ${dias}d`
    }

    if (horasTotal < 24) return `${horasTotal}h restantes`

    const dias = Math.floor(horasTotal / 24)
    const horas = horasTotal % 24
    if (horas === 0) return `${dias}d restantes`
    return `${dias}d ${horas}h restantes`
  }

  /**
   * Formata telefone brasileiro (ex: "(11) 98765-4321")
   * @param {string} telefone - Número de telefone
   * @returns {string} Telefone formatado
   */
  function formatarTelefone(telefone) {
    // Remove tudo que não é dígito
    const numeros = telefone.replace(/\D/g, '')
    
    if (numeros.length === 11) {
      // Celular: (11) 98765-4321
      return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 7)}-${numeros.slice(7)}`
    } else if (numeros.length === 10) {
      // Fixo: (11) 3456-7890
      return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 6)}-${numeros.slice(6)}`
    }
    
    return telefone
  }

  /**
   * Formata CPF brasileiro (ex: "123.456.789-00")
   * @param {string} cpf - CPF
   * @returns {string} CPF formatado
   */
  function formatarCPF(cpf) {
    const numeros = cpf.replace(/\D/g, '')
    
    if (numeros.length === 11) {
      return `${numeros.slice(0, 3)}.${numeros.slice(3, 6)}.${numeros.slice(6, 9)}-${numeros.slice(9)}`
    }
    
    return cpf
  }

  /**
   * Formata número do protocolo (ex: "PROT-2024-001")
   * @param {string|number} numero - Número do protocolo
   * @param {number} ano - Ano do protocolo
   * @returns {string} Protocolo formatado
   */
  function formatarProtocolo(numero, ano = new Date().getFullYear()) {
    const numeroFormatado = String(numero).padStart(3, '0')
    return `PROT-${ano}-${numeroFormatado}`
  }

  /**
   * Formata moeda brasileira (ex: "R$ 1.234,56")
   * @param {number} valor - Valor em reais
   * @returns {string} Valor formatado
   */
  function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor)
  }

  /**
   * Trunca texto longo com reticências
   * @param {string} texto - Texto a ser truncado
   * @param {number} limite - Limite de caracteres
   * @returns {string} Texto truncado
   */
  function truncar(texto, limite = 50) {
    if (texto.length <= limite) return texto
    return texto.slice(0, limite).trim() + '...'
  }

  /**
   * Gera iniciais do nome (ex: "João Silva" -> "JS")
   * @param {string} nome - Nome completo
   * @returns {string} Iniciais
   */
  function gerarIniciais(nome) {
    const partes = nome.trim().split(' ')
    if (partes.length === 1) {
      return partes[0].substring(0, 2).toUpperCase()
    }
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
  }

  /**
   * Calcula progresso do SLA em porcentagem
   * @param {object} sla - Objeto SLA { horasRestantes, vencido }
   * @param {number} totalHoras - Total de horas do SLA (padrão: 168 = 7 dias)
   * @returns {number} Porcentagem de 0 a 100
   */
  function calcularProgressoSLA(sla, totalHoras = 168) {
    if (sla.vencido) return 100
    
    const progresso = ((totalHoras - sla.horasRestantes) / totalHoras) * 100
    return Math.min(Math.max(progresso, 0), 100)
  }

  /**
   * Formata endereço de forma compacta
   * @param {string} endereco - Endereço completo
   * @param {string} bairro - Bairro (opcional)
   * @returns {string} Endereço formatado
   */
  function formatarEndereco(endereco, bairro = null) {
    if (bairro) {
      return `${endereco}, ${bairro}`
    }
    return endereco
  }

  /**
   * Pluraliza palavras
   * @param {number} quantidade - Quantidade
   * @param {string} singular - Palavra no singular
   * @param {string} plural - Palavra no plural (opcional, adiciona 's' por padrão)
   * @returns {string} Palavra pluralizada
   */
  function pluralizar(quantidade, singular, plural = null) {
    if (quantidade === 1) return singular
    return plural || `${singular}s`
  }

  return {
    formatarDataRelativa,
    formatarDataCompleta,
    formatarSLA,
    formatarTelefone,
    formatarCPF,
    formatarProtocolo,
    formatarMoeda,
    truncar,
    gerarIniciais,
    calcularProgressoSLA,
    formatarEndereco,
    pluralizar
  }
}
