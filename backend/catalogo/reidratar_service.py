"""Reidrata formulários vazios a partir de template ou seed inicial."""

from __future__ import annotations

from copy import deepcopy

from catalogo.formulario_resolution import formulario_schema_para_edicao
from catalogo.models import ServicoCatalogo
from catalogo.schema_mapper import (
    formulario_schema_para_schema_formulario,
    schema_formulario_para_formulario_schema,
)
from catalogo.seed_data import SERVICOS_CATALOGO_INICIAL
from catalogo.versionamento_service import publicar_rascunho, salvar_rascunho

# Serviço municipal → origem (template pelo nome da biblioteca ou seed pelo nome)
_REIDRATAR_POR_NOME: dict[str, tuple[str, str]] = {
    "Iluminação Pública": ("template", "Iluminação: Lâmpada Queimada"),
    "Limpeza Urbana": ("seed", "Limpeza Urbana"),
}


def servico_formulario_vazio(servico: ServicoCatalogo) -> bool:
    lista, _ = formulario_schema_para_edicao(
        formulario=servico.formulario_schema,
        schema_formulario=servico.schema_formulario,
    )
    return not lista


def _schemas_da_origem_formulario(origem: ServicoCatalogo) -> tuple[list, dict]:
    form = deepcopy(origem.formulario_schema or [])
    schema = deepcopy(origem.schema_formulario or {})
    if not form and schema:
        form = schema_formulario_para_formulario_schema(schema)
    if not schema and form:
        schema = formulario_schema_para_schema_formulario(form)
    return form, schema


def _schemas_do_seed(nome: str) -> tuple[list, dict]:
    for dados in SERVICOS_CATALOGO_INICIAL:
        if (dados.get("nome") or "").strip() == nome.strip():
            schema = deepcopy(dados.get("schema_formulario") or {})
            form = schema_formulario_para_formulario_schema(schema)
            return form, schema
    raise ValueError(f"Seed sem serviço nome={nome!r}.")


def resolver_origem_reidratar(servico: ServicoCatalogo) -> tuple[list, dict]:
    chave = (servico.nome or "").strip()
    if chave not in _REIDRATAR_POR_NOME:
        raise ValueError(f"Sem mapeamento de reidratação para {chave!r}.")
    tipo, ref = _REIDRATAR_POR_NOME[chave]
    if tipo == "template":
        template = (
            ServicoCatalogo.objects.filter(is_template=True, nome=ref).order_by("-atualizado_em").first()
        )
        if not template:
            raise ValueError(f"Template não encontrado: {ref!r}.")
        return _schemas_da_origem_formulario(template)
    return _schemas_do_seed(ref)


def reidratar_servico_formulario(
    servico: ServicoCatalogo,
    *,
    publicar: bool = False,
    user=None,
    nota_versao: str = "Reidratação automática (template/seed)",
) -> ServicoCatalogo:
    if not servico_formulario_vazio(servico):
        raise ValueError(f"{servico.nome}: já possui formulário publicado ou importável.")
    form, schema = resolver_origem_reidratar(servico)
    if not form:
        raise ValueError(f"{servico.nome}: origem sem campos.")
    salvar_rascunho(servico, form, schema)
    servico.refresh_from_db()
    if publicar:
        return publicar_rascunho(servico, user, nota_versao=nota_versao)
    return servico