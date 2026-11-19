/**
 * Curadoria de ícones Heroicons v2 (outline) para categorias do catálogo.
 * Persistimos o id em kebab-case (alinhado à nomenclatura Heroicons).
 */

import {
  AcademicCapIcon,
  BeakerIcon,
  BoltIcon,
  BuildingLibraryIcon,
  BuildingOffice2Icon,
  ChatBubbleLeftRightIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  FireIcon,
  GlobeAmericasIcon,
  HeartIcon,
  HomeModernIcon,
  InboxIcon,
  LightBulbIcon,
  MapPinIcon,
  MegaphoneIcon,
  ScaleIcon,
  ShieldCheckIcon,
  SparklesIcon,
  SunIcon,
  TrashIcon,
  TruckIcon,
  UserGroupIcon,
  WrenchScrewdriverIcon,
  FolderIcon
} from '@heroicons/vue/24/outline'

/** Aliases legados (seed / cadastros antigos) → id canônico */
const ALIASES_ICONE = {
  'chat-bubble': 'chat-bubble-left-right',
  'building-office': 'building-office-2',
  wrench: 'wrench-screwdriver'
}

export const FALLBACK_ICONE_ID = 'sparkles'
export const FALLBACK_ICONE = SparklesIcon

/** Grade do backoffice + metadados visuais no PWA (24 ícones) */
export const ICONES_CATEGORIA_CATALOGO = [
  { id: 'chat-bubble-left-right', label: 'Ouvidoria', gradient: 'from-blue-500 to-blue-600' },
  { id: 'building-office-2', label: 'Urbano / obras', gradient: 'from-teal-500 to-teal-600' },
  { id: 'heart', label: 'Saúde / bem-estar', gradient: 'from-rose-500 to-rose-600' },
  { id: 'academic-cap', label: 'Educação', gradient: 'from-purple-500 to-purple-600' },
  { id: 'shield-check', label: 'Segurança', gradient: 'from-slate-600 to-slate-700' },
  { id: 'user-group', label: 'Assistência social', gradient: 'from-orange-500 to-orange-600' },
  { id: 'wrench-screwdriver', label: 'Manutenção', gradient: 'from-amber-500 to-amber-600' },
  { id: 'truck', label: 'Transporte', gradient: 'from-cyan-600 to-cyan-700' },
  { id: 'bolt', label: 'Energia / iluminação', gradient: 'from-yellow-500 to-yellow-600' },
  { id: 'trash', label: 'Limpeza urbana', gradient: 'from-emerald-600 to-emerald-700' },
  { id: 'sun', label: 'Meio ambiente', gradient: 'from-green-500 to-green-600' },
  { id: 'beaker', label: 'Saneamento', gradient: 'from-sky-500 to-sky-600' },
  { id: 'map-pin', label: 'Território / mapa', gradient: 'from-indigo-500 to-indigo-600' },
  { id: 'document-text', label: 'Documentos / LAI', gradient: 'from-gray-500 to-gray-600' },
  { id: 'megaphone', label: 'Comunicação', gradient: 'from-pink-500 to-pink-600' },
  { id: 'scale', label: 'Jurídico', gradient: 'from-violet-500 to-violet-600' },
  { id: 'building-library', label: 'Cultura', gradient: 'from-fuchsia-500 to-fuchsia-600' },
  { id: 'currency-dollar', label: 'Finanças', gradient: 'from-lime-600 to-lime-700' },
  { id: 'light-bulb', label: 'Sugestões', gradient: 'from-amber-400 to-orange-500' },
  { id: 'home-modern', label: 'Habitação', gradient: 'from-stone-500 to-stone-600' },
  { id: 'inbox', label: 'Pedidos gerais', gradient: 'from-blue-400 to-blue-500' },
  { id: 'fire', label: 'Proteção / emergência', gradient: 'from-red-500 to-red-600' },
  { id: 'globe-americas', label: 'Turismo / cidadania', gradient: 'from-cyan-500 to-blue-600' },
  { id: 'sparkles', label: 'Digital / IA', gradient: 'from-primary-500 to-cyan-500' }
]

const MAPA_COMPONENTES = {
  'academic-cap': AcademicCapIcon,
  beaker: BeakerIcon,
  bolt: BoltIcon,
  'building-library': BuildingLibraryIcon,
  'building-office-2': BuildingOffice2Icon,
  'chat-bubble-left-right': ChatBubbleLeftRightIcon,
  'currency-dollar': CurrencyDollarIcon,
  'document-text': DocumentTextIcon,
  fire: FireIcon,
  folder: FolderIcon,
  'globe-americas': GlobeAmericasIcon,
  heart: HeartIcon,
  'home-modern': HomeModernIcon,
  inbox: InboxIcon,
  'light-bulb': LightBulbIcon,
  'map-pin': MapPinIcon,
  megaphone: MegaphoneIcon,
  scale: ScaleIcon,
  'shield-check': ShieldCheckIcon,
  sparkles: SparklesIcon,
  sun: SunIcon,
  trash: TrashIcon,
  truck: TruckIcon,
  'user-group': UserGroupIcon,
  'wrench-screwdriver': WrenchScrewdriverIcon
}

const GRADIENTE_POR_ID = Object.fromEntries(ICONES_CATEGORIA_CATALOGO.map((i) => [i.id, i.gradient]))

export function normalizarIdIconeCategoria(raw) {
  const id = String(raw || '')
    .trim()
    .toLowerCase()
  if (!id) return ''
  return ALIASES_ICONE[id] || id
}

export function componenteIconeCategoria(raw) {
  const id = normalizarIdIconeCategoria(raw)
  if (id && MAPA_COMPONENTES[id]) return MAPA_COMPONENTES[id]
  return FALLBACK_ICONE
}

export function gradienteIconeCategoria(raw) {
  const id = normalizarIdIconeCategoria(raw) || FALLBACK_ICONE_ID
  return GRADIENTE_POR_ID[id] || 'from-primary-500 to-primary-600'
}

export function classeGradienteIconeCategoria(raw) {
  return `bg-gradient-to-br ${gradienteIconeCategoria(raw)}`
}

export function rotuloIconeCategoria(raw) {
  const id = normalizarIdIconeCategoria(raw)
  const item = ICONES_CATEGORIA_CATALOGO.find((i) => i.id === id)
  return item?.label || 'Ícone personalizado'
}

export function componentePorIdCatalogo(id) {
  return MAPA_COMPONENTES[id] || null
}