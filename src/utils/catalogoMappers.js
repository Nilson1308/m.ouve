/** Catálogo de serviços — API ↔ Form Builder visual */

export const TIPOS_CAMPO_UI = [
  { value: 'text', label: 'Texto Curto' },
  { value: 'textarea', label: 'Texto Longo' },
  { value: 'number', label: 'Número' },
  { value: 'image', label: 'Imagem' },
  { value: 'select', label: 'Seleção (Dropdown)' }
]

export function labelParaName(label, nomesUsados = new Set()) {
  const base =
    String(label || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '') || 'campo'
  let name = base
  let n = 2
  while (nomesUsados.has(name)) {
    name = `${base}_${n++}`
  }
  nomesUsados.add(name)
  return name
}

export function schemaParaCamposUi(schema = []) {
  if (!Array.isArray(schema)) return []
  return schema.map((campo, index) => {
    const options =
      Array.isArray(campo.options) && campo.options.length
        ? campo.options.map((o) => (typeof o === 'object' ? o.label || o.value : String(o))).join(', ')
        : ''
    return {
      _id: `campo-${index}-${campo.name || index}`,
      label: campo.label || campo.name || '',
      name: campo.name || '',
      nameManual: true,
      type: campo.type || 'text',
      required: Boolean(campo.required),
      optionsText: options,
      placeholder: campo.placeholder || ''
    }
  })
}

function humanizarName(name) {
  return String(name || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

function splitLinhasTexto(texto = '') {
  return String(texto || '')
    .split(/[,;|\n]/)
    .map((s) => s.trim())
    .filter(Boolean)
}

/** UI → objeto persistido em formulario_schema.regra_elegibilidade */
export function regraElegibilidadeUiParaApi(c, campoName) {
  const ativa = Boolean(c.regra_elegibilidade_ativa ?? c.regra_bloqueio_ativa)
  if (!ativa) return null

  const mensagem = String(c.regra_elegibilidade_mensagem ?? c.regra_bloqueio_mensagem ?? '').trim()
  if (!mensagem || !campoName) return null

  const tipo = c.regra_tipo === 'texto' ? 'texto' : 'interpretacao'

  if (tipo === 'interpretacao') {
    const condicao = String(c.regra_condicao || '').trim()
    if (!condicao) return null
    return {
      ativo: true,
      tipo: 'interpretacao',
      campo: campoName,
      mensagem,
      condicao
    }
  }

  const valores = splitLinhasTexto(c.regra_texto_valores ?? c.regra_bloqueio_valores)
  if (!valores.length) return null

  return {
    ativo: true,
    tipo: 'texto',
    campo: campoName,
    mensagem,
    valores
  }
}

/** formulario_schema → campos do AiSchemaBuilder */
export function regraElegibilidadeApiParaUi(campo) {
  const r = campo?.regra_elegibilidade
  const legado = campo?.regra_bloqueio
  if (r?.ativo) {
    if (r.tipo === 'idade_faixa') {
      const minM = r.idade_min_meses ?? 12
      const maxA = r.idade_max_anos ?? 9
      return {
        regra_elegibilidade_ativa: true,
        regra_tipo: 'interpretacao',
        regra_condicao: `Bloquear se a idade for menor que ${minM} meses ou maior que ${maxA} anos.`,
        regra_elegibilidade_mensagem: r.mensagem || '',
        regra_texto_valores: ''
      }
    }
    const interpretacao = r.tipo === 'interpretacao' || r.condicao
    return {
      regra_elegibilidade_ativa: true,
      regra_tipo: interpretacao ? 'interpretacao' : 'texto',
      regra_condicao: r.condicao || '',
      regra_elegibilidade_mensagem: r.mensagem || '',
      regra_texto_valores: Array.isArray(r.valores) ? r.valores.join('\n') : ''
    }
  }
  if (legado?.mensagem && Array.isArray(legado.valores) && legado.valores.length) {
    return {
      regra_elegibilidade_ativa: true,
      regra_tipo: 'texto',
      regra_elegibilidade_mensagem: legado.mensagem,
      regra_texto_valores: legado.valores.join('\n')
    }
  }
  return {
    regra_elegibilidade_ativa: false,
    regra_tipo: 'texto',
    regra_elegibilidade_mensagem: '',
    regra_texto_valores: '',
    regra_condicao: ''
  }
}

export function camposUiParaSchema(campos = []) {
  return camposUiParaSchemaRequisitos(campos)
}

/** Mapeador IA → formulario_schema (API governança). */
export function camposUiParaSchemaRequisitos(campos = []) {
  const nomes = new Set()
  return campos.map((c) => {
    const name = (c.name || '').trim() || labelParaName(c.pergunta || c.label || 'campo', nomes)
    nomes.add(name)

    const pergunta = (c.pergunta || c.label || '').trim() || humanizarName(name)
    const item = {
      name,
      type: c.type || 'text',
      label: pergunta,
      required: Boolean(c.required)
    }

    const instrucao = (c.ia_instrucao || '').trim()
    const repescagem = (c.ia_repescagem || '').trim()
    if (pergunta) {
      item.help_text = pergunta
    }
    if (instrucao) {
      item.ia_instrucao = instrucao
    }
    if (repescagem) {
      item.ia_repescagem = repescagem
    }

    const regra = regraElegibilidadeUiParaApi(c, name)
    if (regra) {
      item.regra_elegibilidade = regra
    }

    if (c.type === 'select') {
      const partes = String(c.optionsText || '')
        .split(/[,;|\n]/)
        .map((s) => s.trim())
        .filter(Boolean)
      item.options = partes.map((p) => ({ value: p, label: p }))
    }
    return item
  })
}

export function requisitosFromFormularioSchema(schema = []) {
  if (!Array.isArray(schema)) return []
  return schema.map((campo, index) => {
    const options =
      Array.isArray(campo.options) && campo.options.length
        ? campo.options.map((o) => (typeof o === 'object' ? o.label || o.value : String(o))).join('\n')
        : ''
    let tipo = campo.type || 'text'
    if (tipo === 'location') tipo = 'geo'
    const pergunta = (campo.label || campo.title || '').trim() || humanizarName(campo.name || '')
    const regraUi = regraElegibilidadeApiParaUi(campo)
    return {
      _id: `req-${index}-${campo.name || index}`,
      name: campo.name || '',
      pergunta,
      type: tipo,
      required: Boolean(campo.required),
      ia_instrucao: campo.ia_instrucao || '',
      ia_repescagem: campo.ia_repescagem || '',
      optionsText: options,
      ...regraUi
    }
  })
}

export function regraProtocoloUiParaApi(regra) {
  if (!regra?.ativa) return null
  const mensagem = String(regra.mensagem || '').trim()
  const condicao = String(regra.condicao || '').trim()
  if (!mensagem || condicao.length < 8) return null
  return {
    ativo: true,
    escopo: 'protocolo',
    tipo: 'interpretacao',
    condicao,
    mensagem
  }
}

export function regrasProtocoloFromSchemaFormulario(schemaFormulario = {}) {
  const meta = schemaFormulario?.$metadata || {}
  const lista = meta.regras_elegibilidade
  if (!Array.isArray(lista)) return []
  return lista
    .filter((r) => r?.ativo && r.escopo === 'protocolo')
    .map((r, index) => ({
      _id: `proto-${index}`,
      ativa: true,
      condicao: r.condicao || '',
      mensagem: r.mensagem || ''
    }))
}

export function novoRegraProtocoloUi() {
  return {
    _id: `proto-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    ativa: true,
    condicao: '',
    mensagem: ''
  }
}

/** JSON Schema para validação / chat (metadados x-ouvia-ia-*). */
export function buildSchemaFormularioRequisitos(campos = [], regrasProtocolo = []) {
  const properties = {}
  const required = []

  for (const c of campos) {
    const name = (c.name || '').trim()
    if (!name) continue

    let jsonType = 'string'
    const tituloAmigavel = (c.pergunta || c.label || '').trim() || humanizarName(name)
    const prop = {
      type: jsonType,
      title: tituloAmigavel,
      description: tituloAmigavel
    }

    if (c.type === 'textarea') {
      prop.format = 'textarea'
    }
    if (c.type === 'number') {
      prop.type = 'number'
    }
    if (c.type === 'image') {
      prop.format = 'uri'
      prop['x-ouvia-tipo-campo'] = 'image'
    }
    if (c.type === 'geo') {
      prop['x-ouvia-tipo-campo'] = 'geolocation'
    }
    if (c.type === 'select') {
      const partes = String(c.optionsText || '')
        .split(/[,;|\n]/)
        .map((s) => s.trim())
        .filter(Boolean)
      if (partes.length) {
        prop.enum = partes
        prop.enumNames = partes
      }
    }

    const instrucao = (c.ia_instrucao || '').trim()
    const repescagem = (c.ia_repescagem || '').trim()
    if (instrucao) {
      prop['x-ouvia-ia-extract'] = instrucao
    }
    if (repescagem) {
      prop['x-ouvia-ia-reprompt'] = repescagem
    }
    prop['x-ouvia-ui-pergunta'] = tituloAmigavel

    properties[name] = prop
    if (c.required) required.push(name)
  }

  const ordemCampos = campos.map((c) => (c.name || '').trim()).filter(Boolean)

  const exigeLocalizacao = campos.some((c) => c.type === 'geo')
  const temCampoImagem = campos.some((c) => c.type === 'image')

  const regrasCampos = campos
    .map((c) => regraElegibilidadeUiParaApi(c, (c.name || '').trim()))
    .filter(Boolean)
  const regrasServico = (regrasProtocolo || [])
    .map((r) => regraProtocoloUiParaApi(r))
    .filter(Boolean)
  const regrasElegibilidade = [...regrasCampos, ...regrasServico]

  return {
    type: 'object',
    properties,
    required,
    $metadata: {
      exige_localizacao: exigeLocalizacao,
      exige_foto: temCampoImagem,
      ia_conversacional: true,
      ordem_campos: ordemCampos,
      regras_elegibilidade: regrasElegibilidade
    }
  }
}

export function mapCategoriaCatalogo(api) {
  if (!api) return null
  return {
    id: String(api.id),
    nome: api.nome,
    slug: api.slug || '',
    descricao: api.descricao || '',
    icone: api.icone || '',
    ordem: Number(api.ordem) || 0,
    tipo_legado: api.tipo_legado || '',
    ativo: api.ativo !== false,
    servicos_count: Number(api.servicos_count) || 0
  }
}

export function payloadCategoriaCatalogo(form) {
  return {
    nome: (form.nome || '').trim(),
    slug: (form.slug || '').trim(),
    descricao: (form.descricao || '').trim(),
    icone: (form.icone || '').trim(),
    ordem: Number(form.ordem) || 0,
    tipo_legado: form.tipo_legado || '',
    ativo: form.ativo !== false
  }
}

export function mapServicoCatalogo(api) {
  if (!api) return null
  const temRascunho = Boolean(api.tem_rascunho_pendente)
  return {
    id: String(api.id),
    nome: api.nome,
    descricao: api.descricao || '',
    icone: api.icone || '',
    sla_padrao_horas: api.sla_padrao_horas ?? api.sla_horas ?? 72,
    unidade_responsavel_id: api.unidade_responsavel_id
      ? String(api.unidade_responsavel_id)
      : null,
    unidade_responsavel_nome: api.unidade_responsavel_nome || null,
    categoria_id: api.categoria_id ? String(api.categoria_id) : null,
    categoria_nome: api.categoria_nome || null,
    ativo: api.ativo !== false,
    permite_cluster: api.permite_cluster !== false,
    formulario_schema: Array.isArray(api.formulario_schema) ? api.formulario_schema : [],
    schema_formulario:
      api.schema_formulario && typeof api.schema_formulario === 'object'
        ? api.schema_formulario
        : {},
    formulario_schema_rascunho: Array.isArray(api.formulario_schema_rascunho)
      ? api.formulario_schema_rascunho
      : null,
    schema_formulario_rascunho:
      api.schema_formulario_rascunho && typeof api.schema_formulario_rascunho === 'object'
        ? api.schema_formulario_rascunho
        : null,
    versao_publicada: api.versao_publicada ?? 1,
    publicado_em: api.publicado_em || null,
    tem_rascunho_pendente: temRascunho
  }
}

/** Form Builder: carrega rascunho se pendente, senão versão publicada. */
export function formularioSchemaParaEdicao(servico) {
  if (!servico) return []
  if (servico.tem_rascunho_pendente && Array.isArray(servico.formulario_schema_rascunho)) {
    return servico.formulario_schema_rascunho
  }
  return Array.isArray(servico.formulario_schema) ? servico.formulario_schema : []
}

export function schemaFormularioParaEdicao(servico) {
  if (!servico) return {}
  if (servico.tem_rascunho_pendente && servico.schema_formulario_rascunho) {
    return servico.schema_formulario_rascunho
  }
  return servico.schema_formulario && typeof servico.schema_formulario === 'object'
    ? servico.schema_formulario
    : {}
}

/** GET /catalogo-servicos (PWA / cidadão) */
export function mapServicoCatalogoPublico(api) {
  if (!api) return null
  const categoria = api.categoria || null
  return {
    id: String(api.id),
    nome: api.nome,
    descricao: api.descricao || '',
    icone: api.icone || '',
    sla_horas: api.sla_horas ?? 72,
    ativo: api.ativo !== false,
    categoria,
    schema_formulario:
      api.schema_formulario && typeof api.schema_formulario === 'object'
        ? api.schema_formulario
        : {},
    formulario_schema: Array.isArray(api.formulario_schema) ? api.formulario_schema : [],
    exige_localizacao: Boolean(api.exige_localizacao)
  }
}

export function payloadServicoCatalogo(form, requisitos, regrasProtocolo = [], opcoes = {}) {
  const schemaLista = camposUiParaSchemaRequisitos(requisitos)
  const body = {
    nome: (form.nome || '').trim(),
    descricao: (form.descricao || '').trim(),
    icone: (form.icone || '').trim(),
    sla_padrao_horas: Number(form.sla_padrao_horas ?? form.slaHoras) || 72,
    categoria_id: form.categoria_id ?? form.categoriaId ?? null,
    unidade_responsavel_id:
      form.unidade_responsavel_id ?? form.unidadeResponsavelId ?? null,
    ativo: form.ativo !== false,
    permite_cluster: form.permite_cluster !== false,
    formulario_schema: schemaLista,
    schema_formulario: buildSchemaFormularioRequisitos(requisitos, regrasProtocolo)
  }
  if (opcoes.salvar_como_rascunho) {
    body.salvar_como_rascunho = true
  }
  return body
}