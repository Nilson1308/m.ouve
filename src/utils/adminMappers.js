/** Mapeamento API governança ↔ painel Configurações. */

import { DIRETRIZES_TOM_MAX, TOM_IA_DEFAULT, normalizeTomIa } from '@/utils/tomIaUnidade'

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function mapUnidadeAdmin(api) {
  if (!api) return null
  return {
    id: String(api.id),
    nome: api.nome,
    sigla: api.sigla || '',
    descricao: api.descricao || '',
    tom_ia: normalizeTomIa(api.tom_ia),
    tom_ia_display: api.tom_ia_display || null,
    diretrizes_tom_ia: (api.diretrizes_tom_ia || '').slice(0, DIRETRIZES_TOM_MAX),
    ativo: api.ativo !== false,
    usuarios_count: api.usuarios_count ?? api.qtd_usuarios ?? 0,
    qtd_usuarios: api.qtd_usuarios ?? api.usuarios_count ?? 0,
    criado_em: api.criado_em,
    atualizado_em: api.atualizado_em
  }
}

export function mapPerfilAcesso(api) {
  if (!api) return null
  const slug = api.slug || api.codigo || ''
  return {
    id: String(api.id),
    slug,
    codigo: slug,
    nome: api.nome,
    descricao: api.descricao || '',
    permissoes: api.permissoes || {},
    requer_vinculo: Boolean(api.requer_vinculo),
    ativo: api.ativo !== false,
    sistema: api.sistema === true,
    usuarios_count: api.usuarios_count ?? api.qtd_usuarios ?? 0,
    qtd_usuarios: api.qtd_usuarios ?? api.usuarios_count ?? 0,
    criado_em: api.criado_em,
    atualizado_em: api.atualizado_em
  }
}

export function mapUsuarioAdmin(api) {
  if (!api) return null
  const perfilId = api.perfil_acesso_id
    ? String(api.perfil_acesso_id)
    : api.perfil || ''
  return {
    id: String(api.id),
    nome: api.nome,
    email: api.email,
    cpf: api.cpf,
    perfil: perfilId,
    perfil_acesso_id: api.perfil_acesso_id ? String(api.perfil_acesso_id) : null,
    perfil_codigo: api.perfil || null,
    perfil_acesso_nome: api.perfil_acesso_nome || null,
    unidade_id: api.unidade_id ? String(api.unidade_id) : null,
    unidade_nome: api.unidade_nome || null,
    ativo: api.ativo !== false,
    ultimo_acesso: api.ultimo_acesso || null,
    criado_em: api.criado_em,
    atualizado_em: api.atualizado_em
  }
}

export function normalizePerfilApi(perfil) {
  if (!perfil) return ''
  return String(perfil).trim().toLowerCase()
}

export function payloadUnidadeAdmin(form) {
  let diretrizes = (form.diretrizes_tom_ia || '').trim()
  if (diretrizes.length > DIRETRIZES_TOM_MAX) {
    diretrizes = diretrizes.slice(0, DIRETRIZES_TOM_MAX)
  }
  return {
    nome: (form.nome || '').trim(),
    sigla: (form.sigla || '').trim(),
    descricao: (form.descricao || '').trim(),
    tom_ia: normalizeTomIa(form.tom_ia),
    diretrizes_tom_ia: diretrizes,
    ativo: form.ativo !== false
  }
}

export function payloadPerfilAcesso(form) {
  const slug = (form.slug || form.codigo || '').trim().toLowerCase().replace(/\s+/g, '_')
  return {
    nome: (form.nome || '').trim(),
    slug,
    descricao: (form.descricao || '').trim(),
    requer_vinculo: Boolean(form.requer_vinculo),
    ativo: form.ativo !== false,
    permissoes: form.permissoes || {}
  }
}

export function payloadUsuarioAdmin(form, perfisAcesso = []) {
  const cpf = String(form.cpf || '').replace(/\D/g, '')
  const perfilRef = form.perfil || form.perfil_acesso_id

  let perfilEscolhido = null
  if (perfilRef && UUID_RE.test(String(perfilRef))) {
    perfilEscolhido = perfisAcesso.find((p) => p.id === String(perfilRef))
  } else if (perfilRef) {
    perfilEscolhido = perfisAcesso.find(
      (p) => p.slug === perfilRef || p.codigo === perfilRef
    )
  }

  const body = {
    nome: (form.nome || '').trim(),
    email: (form.email || '').trim().toLowerCase(),
    cpf,
    ativo: form.ativo !== false
  }

  if (perfilRef) {
    body.perfil_acesso_id = UUID_RE.test(String(perfilRef))
      ? String(perfilRef)
      : undefined
    if (!body.perfil_acesso_id && perfilEscolhido) {
      body.perfil_acesso_id = perfilEscolhido.id
    }
    if (!body.perfil_acesso_id) {
      body.perfil = String(perfilRef)
    }
  }

  const exigeUnidade = perfilEscolhido?.requer_vinculo
  if (exigeUnidade && form.unidade_id) {
    body.unidade_id = form.unidade_id
  } else {
    body.unidade_id = null
  }

  return body
}