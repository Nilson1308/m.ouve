"""Busca textual da Mesa e painéis — códigos PROT e linguagem natural (tokens)."""

from __future__ import annotations

import re

from django.db.models import Q

from catalogo.equipamento_utils import tokens_significativos

_RE_CODIGO = re.compile(r"^[A-Za-z0-9][\w\-/]{2,}$")


def _tokens_busca(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"[\s,;]+", (texto or "").strip()) if p.strip()]


def _q_token_protocolo(tok: str) -> Q:
    """Um token deve casar em pelo menos um campo indexável do protocolo."""
    q = (
        Q(codigo__icontains=tok)
        | Q(descricao__icontains=tok)
        | Q(servico__nome__icontains=tok)
        | Q(servico__categoria__nome__icontains=tok)
        | Q(servico__unidade_responsavel__nome__icontains=tok)
        | Q(servico__unidade_responsavel__sigla__icontains=tok)
        | Q(endereco_texto__icontains=tok)
        | Q(dados_dinamicos__bairro__icontains=tok)
        | Q(equipamento__nome__icontains=tok)
        | Q(equipamento__bairro__icontains=tok)
    )
    return q


def _filtrar_semantico_protocolo(queryset, termo: str):
    tokens = tokens_significativos(termo)
    if not tokens:
        tokens = [t for t in _tokens_busca(termo) if t]
    if not tokens:
        return queryset.none()
    q_total = Q()
    for tok in tokens:
        q_total &= _q_token_protocolo(tok)
    return queryset.filter(q_total).distinct()


def filtrar_queryset_busca_protocolo(queryset, termo: str):
    """
    Suporta:
    - vários códigos PROT na mesma string (espaço/vírgula);
    - busca semântica por tokens (serviço, bairro, descrição, equipamento, secretaria).
    """
    termo = (termo or "").strip()
    if not termo:
        return queryset

    partes = _tokens_busca(termo)
    if len(partes) > 1 and all(_RE_CODIGO.match(p) for p in partes):
        q = Q()
        for parte in partes:
            q |= Q(codigo__iexact=parte) | Q(codigo__icontains=parte)
        return queryset.filter(q).distinct()

    if len(partes) > 1:
        q_total = Q()
        for parte in partes:
            if _RE_CODIGO.match(parte):
                q_total &= Q(codigo__iexact=parte) | Q(codigo__icontains=parte)
            else:
                q_total &= _q_token_protocolo(parte)
        return queryset.filter(q_total).distinct()

    if _RE_CODIGO.match(termo):
        return queryset.filter(Q(codigo__iexact=termo) | Q(codigo__icontains=termo)).distinct()

    return _filtrar_semantico_protocolo(queryset, termo)


def filtrar_queryset_busca_ordem_servico(queryset, termo: str):
    """Busca semântica em OS (descricao, protocolo, serviço, bairro)."""
    termo = (termo or "").strip()
    if not termo:
        return queryset

    partes = _tokens_busca(termo)
    if len(partes) > 1 and all(_RE_CODIGO.match(p) for p in partes):
        q = Q()
        for parte in partes:
            q |= Q(protocolo__codigo__iexact=parte) | Q(protocolo__codigo__icontains=parte)
        return queryset.filter(q).distinct()

    tokens = tokens_significativos(termo) or partes
    if not tokens:
        return queryset.none()

    q_total = Q()
    for tok in tokens:
        q_tok = (
            Q(descricao__icontains=tok)
            | Q(nome_equipe__icontains=tok)
            | Q(despacho_tecnico__icontains=tok)
            | Q(observacoes_execucao__icontains=tok)
            | Q(protocolo__codigo__icontains=tok)
            | Q(protocolo__descricao__icontains=tok)
            | Q(protocolo__endereco_texto__icontains=tok)
            | Q(protocolo__dados_dinamicos__bairro__icontains=tok)
            | Q(protocolo__servico__nome__icontains=tok)
            | Q(protocolo__servico__categoria__nome__icontains=tok)
            | Q(protocolo__equipamento__nome__icontains=tok)
            | Q(super_os__codigo__icontains=tok)
        )
        q_total &= q_tok
    return queryset.filter(q_total).distinct()