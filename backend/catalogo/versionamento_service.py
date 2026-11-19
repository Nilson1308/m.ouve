"""Rascunho / publicação / histórico de versões do ``ServicoCatalogo``."""

from __future__ import annotations

from copy import deepcopy

from django.db import transaction
from django.utils import timezone

from catalogo.form_builder import normalizar_formulario_schema
from catalogo.models import ServicoCatalogo, ServicoCatalogoVersao
from catalogo.schema_mapper import formulario_schema_para_schema_formulario


def _resolver_schema_formulario(
    formulario: list,
    schema_formulario: dict | None,
    *,
    base: dict | None,
) -> dict:
    if schema_formulario is not None and isinstance(schema_formulario, dict):
        return deepcopy(schema_formulario)
    return formulario_schema_para_schema_formulario(formulario, schema_base=base)


@transaction.atomic
def salvar_rascunho(
    servico: ServicoCatalogo,
    formulario_schema,
    schema_formulario=None,
) -> ServicoCatalogo:
    """Grava schemas em rascunho; não altera a versão publicada."""
    lista = normalizar_formulario_schema(formulario_schema)
    base = servico.schema_formulario_rascunho or servico.schema_formulario
    schema = _resolver_schema_formulario(lista, schema_formulario, base=base)
    servico.formulario_schema_rascunho = lista
    servico.schema_formulario_rascunho = schema
    servico.save(
        update_fields=[
            "formulario_schema_rascunho",
            "schema_formulario_rascunho",
            "atualizado_em",
        ]
    )
    return servico


@transaction.atomic
def publicar_rascunho(
    servico: ServicoCatalogo,
    user,
    nota_versao: str = "",
) -> ServicoCatalogo:
    """Promove rascunho → publicado, incrementa versão e registra snapshot."""
    if not servico.tem_rascunho_pendente:
        raise ValueError("Não há rascunho pendente para publicar.")

    formulario = servico.formulario_schema_rascunho
    schema = servico.schema_formulario_rascunho
    if formulario is None:
        raise ValueError("Rascunho sem formulario_schema.")
    if schema is None:
        schema = formulario_schema_para_schema_formulario(
            formulario, schema_base=servico.schema_formulario
        )

    servico.formulario_schema = deepcopy(formulario)
    servico.schema_formulario = deepcopy(schema)
    nova_versao = max(1, int(servico.versao_publicada or 0)) + 1
    servico.versao_publicada = nova_versao
    agora = timezone.now()
    servico.publicado_em = agora

    ServicoCatalogoVersao.objects.create(
        servico=servico,
        numero_versao=nova_versao,
        formulario_schema=deepcopy(formulario),
        schema_formulario=deepcopy(schema),
        nota_versao=(nota_versao or "").strip()[:255],
        publicado_por=user if getattr(user, "is_authenticated", False) else None,
    )

    servico.formulario_schema_rascunho = None
    servico.schema_formulario_rascunho = None
    servico.save(
        update_fields=[
            "formulario_schema",
            "schema_formulario",
            "versao_publicada",
            "publicado_em",
            "formulario_schema_rascunho",
            "schema_formulario_rascunho",
            "atualizado_em",
        ]
    )
    return servico


@transaction.atomic
def descartar_rascunho(servico: ServicoCatalogo) -> ServicoCatalogo:
    servico.formulario_schema_rascunho = None
    servico.schema_formulario_rascunho = None
    servico.save(
        update_fields=[
            "formulario_schema_rascunho",
            "schema_formulario_rascunho",
            "atualizado_em",
        ]
    )
    return servico


@transaction.atomic
def restaurar_versao_para_rascunho(
    servico: ServicoCatalogo,
    numero_versao: int,
) -> ServicoCatalogo:
    """Copia snapshot histórico para rascunho (testar no sandbox antes de publicar)."""
    try:
        snap = ServicoCatalogoVersao.objects.get(
            servico=servico, numero_versao=numero_versao
        )
    except ServicoCatalogoVersao.DoesNotExist as exc:
        raise ValueError(f"Versão {numero_versao} não encontrada.") from exc

    servico.formulario_schema_rascunho = deepcopy(snap.formulario_schema)
    servico.schema_formulario_rascunho = deepcopy(snap.schema_formulario)
    servico.save(
        update_fields=[
            "formulario_schema_rascunho",
            "schema_formulario_rascunho",
            "atualizado_em",
        ]
    )
    return servico