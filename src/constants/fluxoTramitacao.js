/** Opções de `fluxo_tramitacao` (API catálogo). */

export const FLUXO_TRAMITACAO_OPCOES = [
  {
    value: 'direto_secretaria',
    label: 'Direto para Secretaria',
    descricao:
      'Abre OS automaticamente na secretaria executora. Homologação da Ouvidoria opcional (toggle).'
  },
  {
    value: 'ouvidoria_encaminha',
    label: 'Ouvidoria (encaminhamento)',
    descricao:
      'Abertura na Mesa com triagem e despacho assistido; homologação obrigatória da Ouvidoria.'
  }
]

export const LOOKUP_DATASOURCE_UNIDADES = 'unidades_administrativas'
export const LOOKUP_DATASOURCE_EQUIPAMENTOS = 'equipamentos_publicos'