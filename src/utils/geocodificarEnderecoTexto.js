/** Estratégias de geocodificação para endereços brasileiros (backoffice). */

const CEP_RE = /\b(\d{5})-?(\d{3})\b/

export function extrairCep(texto) {
  const m = String(texto || '').match(CEP_RE)
  if (!m) return null
  return `${m[1]}${m[2]}`
}

export function extrairNumeroDoEndereco(texto) {
  const t = String(texto || '')
  const antesTraco = t.match(/,\s*(\d{1,6}[A-Za-z]?)\s*[-–]/)
  if (antesTraco) return antesTraco[1]
  const simples = t.match(/,\s*(\d{1,6}[A-Za-z]?)\s*,/)
  return simples ? simples[1] : ''
}

/** Gera consultas alternativas para o Nominatim (menos falsos negativos). */
export function variantesBuscaEndereco({ endereco = '', bairro = '' } = {}) {
  const linha = String(endereco || '').trim()
  const bairroExtra = String(bairro || '').trim()
  const conjunto = new Set()

  function add(q) {
    const s = String(q || '').trim().replace(/\s+/g, ' ')
    if (s.length > 3) conjunto.add(s)
  }

  if (linha) add(linha)
  if (linha) add(linha.replace(/\s+-\s+/g, ', '))

  const semCep = linha.replace(CEP_RE, '').replace(/,\s*$/, '').trim()
  if (semCep && semCep !== linha) {
    add(semCep)
    add(semCep.replace(/\s+-\s+/g, ', '))
  }

  if (linha && bairroExtra && !linha.toLowerCase().includes(bairroExtra.toLowerCase())) {
    add(`${linha}, ${bairroExtra}`)
    add(`${semCep || linha}, ${bairroExtra}`)
  }

  for (const base of [...conjunto]) {
    if (!/brasil/i.test(base)) add(`${base}, Brasil`)
  }

  return [...conjunto]
}

/**
 * Resolve lat/lng a partir de texto de endereço.
 * @param {{ endereco: string, bairro?: string }} entradas
 * @param {{ buscarEndereco: Function, buscarCepComGeocoding: Function }} servicos
 */
export async function resolverCoordenadasPorEndereco(entradas, servicos) {
  const { endereco = '', bairro = '' } = entradas
  const cep = extrairCep(endereco)

  if (cep && servicos.buscarCepComGeocoding) {
    const numero = extrairNumeroDoEndereco(endereco)
    const viaCep = await servicos.buscarCepComGeocoding(cep, numero)
    if (viaCep?.success && viaCep.coordenadas?.latitude != null) {
      return {
        latitude: viaCep.coordenadas.latitude,
        longitude: viaCep.coordenadas.longitude,
        enderecoCompleto: viaCep.endereco?.enderecoCompleto || null,
        multiplos: [],
        origem: 'cep'
      }
    }
  }

  const variantes = variantesBuscaEndereco({ endereco, bairro })
  let ultimaLista = []

  for (const query of variantes) {
    try {
      const data = await servicos.buscarEndereco(query)
      const lista = data?.resultados || []
      if (!lista.length) continue
      ultimaLista = lista
      if (lista.length === 1) {
        const item = lista[0]
        return {
          latitude: item.latitude,
          longitude: item.longitude,
          enderecoCompleto: item.endereco_completo,
          multiplos: [],
          origem: 'busca'
        }
      }
      return {
        latitude: null,
        longitude: null,
        enderecoCompleto: null,
        multiplos: lista.slice(0, 6),
        origem: 'busca'
      }
    } catch {
      /* tenta próxima variante */
    }
  }

  if (ultimaLista.length > 1) {
    return {
      latitude: null,
      longitude: null,
      enderecoCompleto: null,
      multiplos: ultimaLista.slice(0, 6),
      origem: 'busca'
    }
  }

  return null
}