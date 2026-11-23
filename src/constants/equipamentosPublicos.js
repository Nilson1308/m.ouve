/** Choices de tipo — espelham ``EquipamentoPublico.Tipo`` (API v4.11). */

export const TIPOS_EQUIPAMENTO_PUBLICO = [
  { value: 'ubs', label: 'UBS' },
  { value: 'upa', label: 'UPA' },
  { value: 'hospital', label: 'Hospital' },
  { value: 'escola', label: 'Escola' },
  { value: 'creche', label: 'Creche' },
  { value: 'parque', label: 'Parque' },
  { value: 'quadra', label: 'Quadra esportiva' },
  { value: 'cras', label: 'CRAS' },
  { value: 'equipamento_cultural', label: 'Equipamento cultural' },
  { value: 'predio_administrativo', label: 'Prédio administrativo' },
  { value: 'outro', label: 'Outro' }
]

const LABEL_MAP = Object.fromEntries(TIPOS_EQUIPAMENTO_PUBLICO.map((t) => [t.value, t.label]))

export function labelTipoEquipamento(tipo) {
  return LABEL_MAP[tipo] || tipo || '—'
}

export function badgeClassTipoEquipamento(tipo) {
  const base = 'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium'
  const map = {
    ubs: 'bg-sky-100 text-sky-800 dark:bg-sky-900/40 dark:text-sky-200',
    upa: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-200',
    hospital: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200',
    escola: 'bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200',
    creche: 'bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-200',
    parque: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200'
  }
  return `${base} ${map[tipo] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-200'}`
}