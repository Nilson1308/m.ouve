/** Rótulos e formatação da triagem (Mesa / detalhe). */

export const TRIAGEM_FONTE_LABELS = {
  lookup_cidadao: 'Informado pelo cidadão',
  equipamento_publico: 'Equipamento público',
  matriz_eixo: 'Regra temática',
  llm: 'IA Semântica'
}

const MOTOR_LABELS = {
  deterministico_v1: 'Motor determinístico',
  hibrido_llm_v1: 'Motor híbrido IA'
}

export function labelFonteTriagem(fonte) {
  return TRIAGEM_FONTE_LABELS[fonte] || fonte || 'Sugestão'
}

export function formatarConfiancaTriagem(confianca) {
  const n = Number(confianca)
  if (!Number.isFinite(n)) return '—'
  return `${Math.round(n * 100)}%`
}

/** Classes Tailwind do pill de fonte (dark mode). */
export function classeBadgeFonteTriagem(fonte) {
  const base = 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium'
  switch (fonte) {
    case 'llm':
      return `${base} bg-indigo-100 text-indigo-900 dark:bg-indigo-950/60 dark:text-indigo-200 ring-1 ring-indigo-200/80 dark:ring-indigo-700/50`
    case 'lookup_cidadao':
      return `${base} bg-emerald-100 text-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-200`
    case 'matriz_eixo':
      return `${base} bg-amber-100 text-amber-900 dark:bg-amber-950/50 dark:text-amber-200`
    case 'equipamento_publico':
      return `${base} bg-cyan-100 text-cyan-900 dark:bg-cyan-950/50 dark:text-cyan-200 ring-1 ring-cyan-200/80 dark:ring-cyan-700/40`
    default:
      return `${base} bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200`
  }
}

export function labelMotorTriagem(versaoMotor) {
  return MOTOR_LABELS[versaoMotor] || versaoMotor || 'Motor de triagem'
}

export function textoAuditoriaTriagem(triagem = {}) {
  const partes = []
  const motor = triagem.versao_motor || triagem.versaoMotor
  const modelo = triagem.versao_modelo || triagem.versaoModelo
  if (motor) partes.push(labelMotorTriagem(motor))
  if (modelo) partes.push(modelo)
  return partes.join(' · ')
}