/**
 * Composable para busca de CEP e geocodificação
 * Integra ViaCEP + Nominatim para obter endereço completo e coordenadas
 */

import { ref } from 'vue'

export function useCepLookup() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * Busca endereço pelo CEP usando ViaCEP
   * @param {string} cep - CEP no formato 12345-678 ou 12345678
   * @returns {Promise<Object>} Dados do endereço
   */
  async function buscarCep(cep) {
    loading.value = true
    error.value = null

    try {
      // Limpar CEP (remover pontos e hífens)
      const cepLimpo = cep.replace(/\D/g, '')

      if (cepLimpo.length !== 8) {
        throw new Error('CEP inválido. Digite um CEP com 8 dígitos.')
      }

      // Buscar no ViaCEP
      const response = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
      
      if (!response.ok) {
        throw new Error('Erro ao buscar CEP. Tente novamente.')
      }

      const data = await response.json()

      if (data.erro) {
        throw new Error('CEP não encontrado. Verifique o número digitado.')
      }

      // Retornar dados estruturados
      return {
        success: true,
        endereco: {
          cep: data.cep,
          logradouro: data.logradouro,
          numero: '',
          complemento: data.complemento || '',
          bairro: data.bairro,
          cidade: data.localidade,
          estado: data.uf,
          gia: data.gia || '',
          ibge: data.ibge || '',
          enderecoCompleto: `${data.logradouro}, ${data.bairro} - ${data.localidade}/${data.uf}`
        }
      }
    } catch (err) {
      error.value = err.message
      return {
        success: false,
        error: err.message
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Geocodifica um endereço completo para obter lat/lng
   * Usa Nominatim (OpenStreetMap)
   * @param {Object} endereco - Objeto com dados do endereço
   * @returns {Promise<Object>} Coordenadas geográficas
   */
  async function geocodificar(endereco) {
    loading.value = true
    error.value = null

    try {
      // Montar query de busca
      const query = `${endereco.logradouro} ${endereco.numero || ''}, ${endereco.cidade}, ${endereco.estado}, Brasil`
      const encodedQuery = encodeURIComponent(query)

      // Buscar no Nominatim
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodedQuery}&limit=1`,
        {
          headers: {
            'User-Agent': 'M.Ouve/1.0' // Nominatim requer User-Agent
          }
        }
      )

      if (!response.ok) {
        throw new Error('Erro ao geocodificar endereço.')
      }

      const data = await response.json()

      if (!data || data.length === 0) {
        // Fallback: usar coordenadas aproximadas do município
        console.warn('Geocodificação precisa falhou, usando coordenadas da cidade')
        return await geocodificarCidade(endereco.cidade, endereco.estado)
      }

      const result = data[0]

      return {
        success: true,
        coordenadas: {
          latitude: parseFloat(result.lat),
          longitude: parseFloat(result.lon),
          precisao: 'exata' // ou 'cidade' em caso de fallback
        }
      }
    } catch (err) {
      error.value = err.message
      
      // Fallback para coordenadas da cidade em caso de erro
      try {
        return await geocodificarCidade(endereco.cidade, endereco.estado)
      } catch (fallbackErr) {
        return {
          success: false,
          error: 'Não foi possível obter as coordenadas. Continue mesmo assim.'
        }
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Geocodifica apenas cidade + estado (fallback)
   * @param {string} cidade
   * @param {string} estado
   * @returns {Promise<Object>}
   */
  async function geocodificarCidade(cidade, estado) {
    const query = `${cidade}, ${estado}, Brasil`
    const encodedQuery = encodeURIComponent(query)

    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodedQuery}&limit=1`,
      {
    headers: {
      'User-Agent': 'M.Ouve/1.0'
    }
      }
    )

    const data = await response.json()

    if (!data || data.length === 0) {
      throw new Error('Não foi possível geocodificar a cidade')
    }

    const result = data[0]

    return {
      success: true,
      coordenadas: {
        latitude: parseFloat(result.lat),
        longitude: parseFloat(result.lon),
        precisao: 'cidade'
      }
    }
  }

  /**
   * Busca CEP e geocodifica em uma única chamada
   * @param {string} cep
   * @param {string} numero
   * @returns {Promise<Object>}
   */
  async function buscarCepComGeocoding(cep, numero = '') {
    loading.value = true

    try {
      // 1. Buscar CEP
      const resultCep = await buscarCep(cep)
      
      if (!resultCep.success) {
        return resultCep
      }

      // 2. Adicionar número ao endereço
      resultCep.endereco.numero = numero

      // 3. Geocodificar
      const resultGeo = await geocodificar(resultCep.endereco)

      if (!resultGeo.success) {
        // Retornar mesmo assim, mas sem coordenadas
        return {
          success: true,
          endereco: resultCep.endereco,
          coordenadas: null,
          aviso: 'Endereço encontrado mas não foi possível obter coordenadas precisas'
        }
      }

      // 4. Retornar tudo junto
      return {
        success: true,
        endereco: resultCep.endereco,
        coordenadas: resultGeo.coordenadas
      }
    } catch (err) {
      error.value = err.message
      return {
        success: false,
        error: err.message
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Formata CEP para o padrão 12345-678
   * @param {string} cep
   * @returns {string}
   */
  function formatarCep(cep) {
    const limpo = cep.replace(/\D/g, '')
    if (limpo.length <= 5) {
      return limpo
    }
    return limpo.replace(/(\d{5})(\d)/, '$1-$2')
  }

  return {
    loading,
    error,
    buscarCep,
    geocodificar,
    buscarCepComGeocoding,
    formatarCep
  }
}
