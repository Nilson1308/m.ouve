/** Agrega evidências de campo das OS do protocolo (visão 360º / validação). */

import { nomeSecretariaNo } from '@/utils/scatterGather'

export function mapFotoParaEvidencia(foto, ordem, index = 0) {
  return {
    id: foto.id || `${ordem.id}-foto-${index}`,
    url: foto.url,
    legenda: foto.legenda || 'Evidência',
    enviado_em: foto.timestamp || foto.enviado_em,
    ordemId: ordem.id,
    secretaria: nomeSecretariaNo(ordem)
  }
}

/**
 * @param {object[]} ordens
 * @returns {Array<{ id, url, legenda, enviado_em, ordemId, secretaria }>}
 */
export function evidenciasDoProtocolo(ordens = []) {
  const lista = []
  for (const ordem of ordens || []) {
    const fotos = ordem.fotos_execucao || []
    fotos.forEach((foto, index) => {
      lista.push(mapFotoParaEvidencia(foto, ordem, index))
    })
  }
  return lista
}

/**
 * Relatos de campo por secretaria (OS concluídas com texto).
 * @param {object[]} ordens
 */
export function relatosCampoPorOrdem(ordens = []) {
  return (ordens || [])
    .filter((o) => (o.observacoes_execucao || '').trim())
    .map((o) => ({
      ordemId: o.id,
      secretaria: nomeSecretariaNo(o),
      texto: o.observacoes_execucao.trim()
    }))
}