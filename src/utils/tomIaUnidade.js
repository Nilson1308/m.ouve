/** Tom da IA por UnidadeAdministrativa (API v4.3). */

export const TOM_IA_DEFAULT = 'institucional'
export const DIRETRIZES_TOM_MAX = 500

export const TOM_IA_OPCOES = [
  {
    value: 'institucional',
    titulo: 'Institucional',
    subtitulo: 'Cordial, claro e padronizado',
    hint: 'Padrão municipal',
    icon: 'BuildingLibraryIcon'
  },
  {
    value: 'acolhedor',
    titulo: 'Acolhedor',
    subtitulo: 'Empático, gentil e paciente',
    hint: 'Saúde, Assistência, Proteção Animal',
    icon: 'HeartIcon'
  },
  {
    value: 'objetivo',
    titulo: 'Objetivo',
    subtitulo: 'Direto ao ponto, ágil e conciso',
    hint: 'Zeladoria, Trânsito, Iluminação',
    icon: 'BoltIcon'
  },
  {
    value: 'tecnico',
    titulo: 'Técnico',
    subtitulo: 'Preciso na coleta de evidências',
    hint: 'Fiscalização, Obras',
    icon: 'ClipboardDocumentListIcon'
  }
]

export const TOM_IA_PREVIA = {
  institucional:
    'Para continuar com seu pedido, por favor indique o local da ocorrência no mapa abaixo.',
  acolhedor:
    'Ficarei feliz em ajudar. Quando puder, marque no mapa onde a situação está acontecendo — isso agiliza o atendimento.',
  objetivo: 'Marque o ponto exato no mapa para seguirmos.',
  tecnico:
    'Precisamos da localização precisa: use o mapa e confirme endereço de referência ou ponto de apoio, se houver.'
}

export const TOM_IA_BADGE_CLASSES = {
  institucional:
    'bg-slate-100 text-slate-700 dark:bg-slate-800/80 dark:text-slate-300 ring-1 ring-slate-200/80 dark:ring-slate-600/50',
  acolhedor:
    'bg-rose-100 text-rose-800 dark:bg-rose-950/40 dark:text-rose-200 ring-1 ring-rose-200/80 dark:ring-rose-800/50',
  objetivo:
    'bg-amber-100 text-amber-900 dark:bg-amber-950/40 dark:text-amber-200 ring-1 ring-amber-200/80 dark:ring-amber-800/50',
  tecnico:
    'bg-violet-100 text-violet-800 dark:bg-violet-950/40 dark:text-violet-200 ring-1 ring-violet-200/80 dark:ring-violet-800/50'
}

export function labelTomIa(unidade) {
  if (!unidade) return 'Institucional'
  return (
    unidade.tom_ia_display ||
    TOM_IA_OPCOES.find((o) => o.value === (unidade.tom_ia || TOM_IA_DEFAULT))?.titulo ||
    'Institucional'
  )
}

export function badgeClassTomIa(tom) {
  return TOM_IA_BADGE_CLASSES[tom] || TOM_IA_BADGE_CLASSES.institucional
}

export function normalizeTomIa(val) {
  const v = (val || TOM_IA_DEFAULT).trim().toLowerCase()
  return TOM_IA_OPCOES.some((o) => o.value === v) ? v : TOM_IA_DEFAULT
}