/** Opções de `fluxo_tramitacao` (API catálogo). */

export const FLUXO_TRAMITACAO_OPCOES = [
  {
    value: 'direto_secretaria',
    label: 'Direto para Secretaria',
    descricao: 'A unidade vinculada ao serviço é a executora padrão.'
  },
  {
    value: 'ouvidoria_encaminha',
    label: 'Ouvidoria (encaminhamento)',
    descricao: 'A unidade do serviço atua como canal; secretarias executam via despacho.'
  },
  {
    value: 'hibrido',
    label: 'Híbrido',
    descricao: 'Canal titular com executor padrão e encaminhamento quando necessário.'
  }
]

export const LOOKUP_DATASOURCE_UNIDADES = 'unidades_administrativas'