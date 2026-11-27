"""Clonagem de templates e duplicação de serviços do catálogo."""

from __future__ import annotations

import copy

from catalogo.models import ServicoCatalogo, UnidadeAdministrativa

_SUFIXO_COPIA = " (Cópia)"


def _nome_unico_duplicacao(nome_base: str) -> str:
    """Evita colisão de nomes ao duplicar o mesmo serviço várias vezes."""
    base = (nome_base or "").strip() or "Serviço"
    if base.endswith(_SUFIXO_COPIA):
        base = base[: -len(_SUFIXO_COPIA)].rstrip()
    candidato = f"{base}{_SUFIXO_COPIA}"
    if not ServicoCatalogo.objects.filter(nome=candidato, is_template=False).exists():
        return candidato
    n = 2
    while True:
        candidato = f"{base} (Cópia {n})"
        if not ServicoCatalogo.objects.filter(nome=candidato, is_template=False).exists():
            return candidato
        n += 1


def clonar_servico_catalogo_de_template(
    template: ServicoCatalogo,
    *,
    unidade_responsavel: UnidadeAdministrativa,
) -> ServicoCatalogo:
    if not template.is_template:
        raise ValueError("Somente registros com is_template=True podem ser clonados como template.")
    if not unidade_responsavel or not unidade_responsavel.ativo:
        raise ValueError("Informe uma unidade administrativa ativa.")

    novo = ServicoCatalogo(
        categoria=template.categoria,
        nome=template.nome,
        descricao=template.descricao,
        icone=template.icone,
        sla_horas=template.sla_horas,
        unidade_responsavel=unidade_responsavel,
        formulario_schema=copy.deepcopy(template.formulario_schema or []),
        schema_formulario=copy.deepcopy(template.schema_formulario or {}),
        permite_cluster=template.permite_cluster,
        fluxo_tramitacao=template.fluxo_tramitacao,
        triagem_ia_ativa=template.triagem_ia_ativa,
        visivel_catalogo_pwa=template.visivel_catalogo_pwa,
        ordem_exibicao_pwa=template.ordem_exibicao_pwa,
        ativo=True,
        is_template=False,
    )
    novo.save()
    return novo


def duplicar_servico_catalogo(
    origem: ServicoCatalogo,
    *,
    unidade_responsavel: UnidadeAdministrativa | None = None,
) -> ServicoCatalogo:
    """Copia um serviço municipal existente (não template). Nasce inativo para revisão."""
    if origem.is_template:
        raise ValueError("Use a clonagem de template para modelos globais (is_template=True).")
    if unidade_responsavel is not None and not unidade_responsavel.ativo:
        raise ValueError("Informe uma unidade administrativa ativa.")

    unidade = unidade_responsavel if unidade_responsavel is not None else origem.unidade_responsavel

    novo = ServicoCatalogo(
        categoria=origem.categoria,
        nome=_nome_unico_duplicacao(origem.nome),
        descricao=origem.descricao,
        icone=origem.icone,
        sla_horas=origem.sla_horas,
        unidade_responsavel=unidade,
        formulario_schema=copy.deepcopy(origem.formulario_schema or []),
        schema_formulario=copy.deepcopy(origem.schema_formulario or {}),
        permite_cluster=origem.permite_cluster,
        fluxo_tramitacao=origem.fluxo_tramitacao,
        triagem_ia_ativa=origem.triagem_ia_ativa,
        visivel_catalogo_pwa=origem.visivel_catalogo_pwa,
        ordem_exibicao_pwa=origem.ordem_exibicao_pwa,
        ativo=False,
        is_template=False,
    )
    novo.save()
    return novo


def instanciar_servico_catalogo(
    origem: ServicoCatalogo,
    *,
    unidade_responsavel: UnidadeAdministrativa | None = None,
) -> ServicoCatalogo:
    """Template → clone ativo; serviço regular → duplicata inativa com sufixo (Cópia)."""
    if origem.is_template:
        if unidade_responsavel is None:
            raise ValueError("unidade_responsavel_id é obrigatório para modelos da biblioteca.")
        return clonar_servico_catalogo_de_template(
            origem,
            unidade_responsavel=unidade_responsavel,
        )
    return duplicar_servico_catalogo(origem, unidade_responsavel=unidade_responsavel)