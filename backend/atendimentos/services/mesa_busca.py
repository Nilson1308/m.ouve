"""Busca textual da Mesa e painéis — códigos PROT e linguagem natural (tokens)."""

from __future__ import annotations

import re

from django.db.models import Q

from catalogo.equipamento_utils import normalizar_texto_busca, tokens_significativos

_RE_PREFIXO_CODIGO = re.compile(r"^(?:PROT|OS|SUPER)[\w\-/]*$", re.IGNORECASE)


def _tokens_busca(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"[\s,;]+", (texto or "").strip()) if p.strip()]


def parece_codigo_protocolo(termo: str) -> bool:
    """Evita confundir palavras comuns (ex.: ilumin) com código PROT/OS."""
    t = (termo or "").strip()
    if not t or len(t) < 5:
        return False
    if _RE_PREFIXO_CODIGO.match(t):
        return True
    if re.search(r"\d", t) and re.search(r"[-/]", t):
        return True
    return False


def _variantes_parte(parte: str) -> list[str]:
    """Grafia digitada + forma sem acento para icontains no PostgreSQL."""
    p = (parte or "").strip()
    if len(p) < 2:
        return []
    saida: list[str] = []
    vistos: set[str] = set()

    def _add(s: str) -> None:
        s = (s or "").strip()
        if len(s) < 2:
            return
        chave = s.casefold()
        if chave in vistos:
            return
        vistos.add(chave)
        saida.append(s)

    _add(p)
    norm = normalizar_texto_busca(p)
    _add(norm)
    for tok in tokens_significativos(p):
        _add(tok)
    # Prefixo tolera divergência de acento no restante da palavra (ex.: iluminacao × Iluminação).
    if len(norm) >= 5:
        for n in (5, 6):
            if len(norm) >= n:
                _add(norm[:n])
    return saida


def _q_icontains(campo: str, valores: list[str]) -> Q:
    q = Q()
    for v in valores:
        q |= Q(**{f"{campo}__icontains": v})
    return q


def _q_token_protocolo_variaveis(valores: list[str]) -> Q:
    """Um token lógico deve casar em pelo menos um campo (variantes OR)."""
    return (
        _q_icontains("codigo", valores)
        | _q_icontains("descricao", valores)
        | _q_icontains("observacoes_internas", valores)
        | _q_icontains("resposta_cidadao", valores)
        | _q_icontains("servico__nome", valores)
        | _q_icontains("servico__categoria__nome", valores)
        | _q_icontains("servico__unidade_responsavel__nome", valores)
        | _q_icontains("servico__unidade_responsavel__sigla", valores)
        | _q_icontains("endereco_texto", valores)
        | _q_icontains("dados_dinamicos__bairro", valores)
        | _q_icontains("dados_dinamicos", valores)
        | _q_icontains("equipamento__nome", valores)
        | _q_icontains("equipamento__bairro", valores)
        | _q_icontains("super_os__codigo", valores)
        | _q_icontains("super_os__titulo_resumo", valores)
        | _q_icontains("super_os__descricao_geral", valores)
    )


def _q_parte_protocolo(parte: str) -> Q:
    variantes = _variantes_parte(parte)
    if not variantes:
        return Q(pk__isnull=True)
    return _q_token_protocolo_variaveis(variantes)


def _filtrar_semantico_protocolo(queryset, termo: str):
    partes = _tokens_busca(termo)
    if not partes:
        return queryset.none()
    q_total = Q()
    for parte in partes:
        if parece_codigo_protocolo(parte):
            q_total &= Q(codigo__iexact=parte) | Q(codigo__icontains=parte)
        else:
            q_total &= _q_parte_protocolo(parte)
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
    if len(partes) > 1 and all(parece_codigo_protocolo(p) for p in partes):
        q = Q()
        for parte in partes:
            q |= Q(codigo__iexact=parte) | Q(codigo__icontains=parte)
        return queryset.filter(q).distinct()

    return _filtrar_semantico_protocolo(queryset, termo)


def _q_token_ordem_variaveis(valores: list[str]) -> Q:
    return (
        _q_icontains("descricao", valores)
        | _q_icontains("nome_equipe", valores)
        | _q_icontains("despacho_tecnico", valores)
        | _q_icontains("observacoes_execucao", valores)
        | _q_icontains("protocolo__codigo", valores)
        | _q_icontains("protocolo__descricao", valores)
        | _q_icontains("protocolo__endereco_texto", valores)
        | _q_icontains("protocolo__dados_dinamicos__bairro", valores)
        | _q_icontains("protocolo__dados_dinamicos", valores)
        | _q_icontains("protocolo__servico__nome", valores)
        | _q_icontains("protocolo__servico__categoria__nome", valores)
        | _q_icontains("protocolo__equipamento__nome", valores)
        | _q_icontains("super_os__codigo", valores)
        | _q_icontains("super_os__titulo_resumo", valores)
    )


def _q_parte_ordem(parte: str) -> Q:
    variantes = _variantes_parte(parte)
    if not variantes:
        return Q(pk__isnull=True)
    return _q_token_ordem_variaveis(variantes)


def filtrar_queryset_busca_ordem_servico(queryset, termo: str):
    """Busca semântica em OS (descricao, protocolo, serviço, bairro)."""
    termo = (termo or "").strip()
    if not termo:
        return queryset

    partes = _tokens_busca(termo)
    if len(partes) > 1 and all(parece_codigo_protocolo(p) for p in partes):
        q = Q()
        for parte in partes:
            q |= Q(protocolo__codigo__iexact=parte) | Q(protocolo__codigo__icontains=parte)
        return queryset.filter(q).distinct()

    if not partes:
        return queryset.none()

    q_total = Q()
    for parte in partes:
        if parece_codigo_protocolo(parte):
            q_total &= Q(protocolo__codigo__iexact=parte) | Q(protocolo__codigo__icontains=parte)
        else:
            q_total &= _q_parte_ordem(parte)
    return queryset.filter(q_total).distinct()