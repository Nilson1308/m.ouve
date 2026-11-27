"""Consultas e cache público do catálogo no PWA."""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db.models import Q

from atendimentos.models import ConfiguracaoSistema
from catalogo.equipamento_utils import normalizar_texto_busca
from catalogo.models import CategoriaCatalogo, ServicoCatalogo
from catalogo.catalogo_queries import filtrar_servicos_por_categoria

PWA_CONFIG_CACHE_KEY = "catalogo:config-pwa:v1"
PWA_CONFIG_CACHE_TTL_SEG = 300


def invalidar_cache_config_pwa() -> None:
    cache.delete(PWA_CONFIG_CACHE_KEY)


def queryset_servicos_pwa_publicados():
    return ServicoCatalogo.objects.filter(
        ativo=True,
        is_template=False,
        visivel_catalogo_pwa=True,
        publicado_em__isnull=False,
    ).select_related("categoria")


def servicos_visiveis_por_categoria(categoria_ref: str):
    qs = queryset_servicos_pwa_publicados()
    return filtrar_servicos_por_categoria(qs, categoria_ref)


def categoria_coincide(servico: ServicoCatalogo, categoria_ref: str) -> bool:
    ref = (categoria_ref or "").strip()
    if not ref:
        return True
    cat = servico.categoria
    legado = ref.lower()
    if legado in ("ouvidoria", "zeladoria"):
        return (cat.tipo_legado or "").lower() == legado
    slug = legado.replace(" ", "_")
    ref_cf = ref.casefold()
    return (
        (cat.slug or "").casefold() == slug.casefold()
        or (cat.nome or "").casefold() == ref_cf
        or (cat.slug or "").casefold() == ref_cf
    )


def filtrar_servicos_busca_pwa(qs, busca: str):
    termo = (busca or "").strip()
    if not termo:
        return qs
    norm_term = normalizar_texto_busca(termo)
    tokens = [t for t in norm_term.split() if t]
    if not tokens:
        return qs
    ids: list = []
    for servico in qs.iterator():
        hay = normalizar_texto_busca(f"{servico.nome} {servico.descricao}")
        if all(t in hay for t in tokens):
            ids.append(servico.pk)
    return qs.filter(pk__in=ids)


def montar_payload_config_pwa() -> dict[str, Any]:
    cfg = ConfiguracaoSistema.load()
    categorias_out: list[dict[str, Any]] = []
    categorias = CategoriaCatalogo.objects.filter(ativo=True).order_by("ordem", "nome")
    for cat in categorias:
        visiveis = list(
            queryset_servicos_pwa_publicados()
            .filter(categoria=cat)
            .order_by("ordem_exibicao_pwa", "nome")
        )
        total = len(visiveis)
        servico_unico_id = None
        if total == 1:
            servico_unico_id = str(visiveis[0].id)
        categorias_out.append(
            {
                "slug": cat.slug,
                "nome": cat.nome,
                "descricao": cat.descricao or "",
                "total_servicos_visiveis": total,
                "servico_unico_id": servico_unico_id,
            }
        )
    return {
        "modo_abertura_pwa": cfg.modo_abertura_pwa,
        "categorias": categorias_out,
    }


def obter_config_pwa_cached() -> dict[str, Any]:
    payload = cache.get(PWA_CONFIG_CACHE_KEY)
    if isinstance(payload, dict) and "modo_abertura_pwa" in payload:
        return payload
    payload = montar_payload_config_pwa()
    cache.set(PWA_CONFIG_CACHE_KEY, payload, PWA_CONFIG_CACHE_TTL_SEG)
    return payload