/** Níveis canônicos da Matriz de Urgência (API v4.16). */

export const NIVEIS_URGENCIA = ['baixa', 'normal', 'alta', 'critica']

const ALIASES = {
  media: 'normal',
  média: 'normal',
  urgente: 'alta',
  critico: 'critica',
  crítico: 'critica',
  crítica: 'critica'
}

export function normalizarUrgencia(valor) {
  const v = String(valor || 'normal')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
  return ALIASES[v] || (NIVEIS_URGENCIA.includes(v) ? v : 'normal')
}

export const OPCOES_URGENCIA_FILTRO = [
  { value: 'baixa', label: 'Baixa' },
  { value: 'normal', label: 'Normal' },
  { value: 'alta', label: 'Alta' },
  { value: 'critica', label: 'Crítica' }
]

export const LABEL_URGENCIA = {
  baixa: 'Baixa',
  normal: 'Normal',
  alta: 'Alta',
  critica: 'Crítica'
}

export function labelUrgencia(nivel) {
  return LABEL_URGENCIA[normalizarUrgencia(nivel)] || 'Normal'
}

export function formatarConfiancaIa(valor) {
  if (valor == null || Number.isNaN(Number(valor))) return null
  return `${Math.round(Number(valor) * 100)}%`
}

export function sugestaoIaPendente(protocolo) {
  return (
    protocolo?.urgencia_sugestao_status === 'pendente' ||
    protocolo?.urgenciaSugestaoStatus === 'pendente'
  )
}