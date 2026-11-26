"""Origem geográfica da ocorrência (LGPD) — separada do endereço residencial do cidadão."""

from __future__ import annotations

import math

from django.contrib.gis.geos import Point

from atendimentos.models import Protocolo
from atendimentos.services.protocolo_localidade import (
    bairro_de_dados_dinamicos,
    bairro_de_endereco_texto,
    _bairro_usuario,
)

ORIGENS_GEO_MAPA = frozenset(
    {
        Protocolo.OrigemLocalizacao.OCORRENCIA_GPS,
        Protocolo.OrigemLocalizacao.OCORRENCIA_ENDERECO,
        Protocolo.OrigemLocalizacao.EQUIPAMENTO_PUBLICO,
        Protocolo.OrigemLocalizacao.RESIDENCIA_CONFIRMADA,
    }
)


def queryset_geo_ocorrencia_valida(qs):
    """Protocolos com coordenada atribuída à ocorrência (não contaminados por cadastro)."""
    return qs.filter(
        localizacao__isnull=False,
        origem_localizacao__in=ORIGENS_GEO_MAPA,
    )


def _coords_proximas(p1: Point | None, p2: Point | None, *, metros: float = 35.0) -> bool:
    if not p1 or not p2:
        return False
    lat1, lon1 = float(p1.y), float(p1.x)
    lat2, lon2 = float(p2.y), float(p2.x)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    dist = 2 * 6_371_000 * math.asin(math.sqrt(a))
    return dist <= metros


def origem_residencia_confirmada(sessao_dados: dict | None) -> bool:
    loc = (sessao_dados or {}).get("_localizacao") or {}
    if not isinstance(loc, dict):
        return False
    flag = str(loc.get("origem") or loc.get("tipo") or "").strip().lower()
    return flag in ("residencia", "residencia_confirmada", "casa", "domicilio")


def aplicar_origem_na_abertura(
    protocolo: Protocolo,
    *,
    latitude=None,
    longitude=None,
    endereco_ocorrencia: str = "",
    sessao_dados: dict | None = None,
) -> None:
    if origem_residencia_confirmada(sessao_dados) and latitude is not None and longitude is not None:
        protocolo.origem_localizacao = Protocolo.OrigemLocalizacao.RESIDENCIA_CONFIRMADA
        return
    if latitude is not None and longitude is not None:
        protocolo.origem_localizacao = Protocolo.OrigemLocalizacao.OCORRENCIA_GPS
        return
    if (endereco_ocorrencia or protocolo.endereco_texto or "").strip():
        protocolo.origem_localizacao = Protocolo.OrigemLocalizacao.OCORRENCIA_ENDERECO
        return
    protocolo.origem_localizacao = Protocolo.OrigemLocalizacao.NENHUMA


def marcar_origem_equipamento_publico(protocolo: Protocolo) -> None:
    protocolo.origem_localizacao = Protocolo.OrigemLocalizacao.EQUIPAMENTO_PUBLICO


def protocolo_contaminado_residencia(protocolo: Protocolo) -> bool:
    """
    Ouvidoria sem endereço de ocorrência que herdou bairro/coordenada do cidadão.
    """
    origem = (protocolo.origem_localizacao or Protocolo.OrigemLocalizacao.NENHUMA)
    if origem not in (Protocolo.OrigemLocalizacao.NENHUMA, ""):
        return False
    if (protocolo.endereco_texto or "").strip():
        return False
    if protocolo.equipamento_id:
        return False
    dados = protocolo.dados_dinamicos or {}
    if bairro_de_endereco_texto(protocolo.endereco_texto or ""):
        return False
    if dados.get("latitude") or dados.get("longitude"):
        return False
    loc_sessao = dados.get("_localizacao")
    if isinstance(loc_sessao, dict) and loc_sessao.get("latitude") is not None:
        return False

    user_bairro = _bairro_usuario(protocolo)
    dados_bairro = bairro_de_dados_dinamicos(dados)
    bairro_indevido = bool(
        user_bairro
        and dados_bairro
        and dados_bairro.strip().lower() == user_bairro.strip().lower()
    )

    user_loc = None
    usuario = getattr(protocolo, "usuario", None)
    if usuario:
        endereco = getattr(usuario, "endereco", None)
        if endereco:
            user_loc = getattr(endereco, "localizacao", None)

    coord_indevida = _coords_proximas(protocolo.localizacao, user_loc)
    if coord_indevida:
        return True
    if bairro_indevido and not protocolo.localizacao:
        return True
    if bairro_indevido and coord_indevida:
        return True
    return False


def limpar_contaminacao_residencial(protocolo: Protocolo) -> list[str]:
    """Zera geo/bairro indevidos; retorna campos alterados."""
    alterados: list[str] = []
    protocolo.origem_localizacao = Protocolo.OrigemLocalizacao.NENHUMA
    alterados.append("origem_localizacao")
    if protocolo.localizacao:
        protocolo.localizacao = None
        alterados.append("localizacao")
    dados = dict(protocolo.dados_dinamicos or {})
    user_b = _bairro_usuario(protocolo)
    for chave in ("bairro", "cidade", "nome_bairro", "bairro_nome"):
        val = (dados.get(chave) or "").strip()
        if val and user_b and val.lower() == user_b.lower():
            dados.pop(chave, None)
            alterados.append("dados_dinamicos")
    protocolo.dados_dinamicos = dados
    return alterados