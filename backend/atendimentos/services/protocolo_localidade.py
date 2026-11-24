"""Extração de bairro/localidade para filtros territoriais e mesa."""

from __future__ import annotations

import re


_CHAVES_BAIRRO_JSON = (
    "bairro",
    "nome_bairro",
    "bairro_nome",
    "district",
    "suburb",
)

_NOISE_ENDERECO = (
    "brasil",
    "região",
    "regiao",
    "sudeste",
    "são paulo",
    "sao paulo",
)


def bairro_de_dados_dinamicos(dados) -> str:
    if not isinstance(dados, dict):
        return ""
    for chave in _CHAVES_BAIRRO_JSON:
        valor = (dados.get(chave) or "").strip()
        if valor:
            return valor
    return ""


def _parte_eh_ruido(parte: str) -> bool:
    pl = parte.strip().lower()
    if not pl:
        return True
    if re.fullmatch(r"\d{5}-?\d{0,3}", pl.replace(" ", "")):
        return True
    return any(r in pl for r in _NOISE_ENDERECO)


def bairro_de_endereco_texto(texto: str) -> str:
    """
    Infere bairro a partir de ``Protocolo.endereco_texto`` (Nominatim ou formulário).
    Ex.: ``Rua X, Vila da Prata, Mogi das Cruzes...`` → ``Vila da Prata``.
    """
    texto = (texto or "").strip()
    if not texto:
        return ""

    partes = [p.strip() for p in texto.split(",") if p.strip()]
    if not partes:
        return ""

    limpas = [p for p in partes if not _parte_e_ruido(p)]
    if not limpas:
        limpas = partes

    cidade_idx = None
    for i, parte in enumerate(limpas):
        pl = parte.lower()
        if "mogi das cruzes" in pl or "/sp" in pl or pl.endswith(" sp"):
            cidade_idx = i
            break

    if cidade_idx is not None and cidade_idx > 0:
        return _escolher_bairro_antes_cidade(limpas, cidade_idx)

    if len(limpas) >= 3:
        return limpas[1]
    if len(limpas) >= 2:
        segunda = limpas[1]
        if not re.fullmatch(r"\d+[a-zA-Z]?", segunda.replace(" ", "")):
            return segunda
    return ""


def _parte_e_ruido(parte: str) -> bool:
    return _parte_eh_ruido(parte)


def _escolher_bairro_antes_cidade(partes: list[str], cidade_idx: int) -> str:
    """Volta do índice da cidade ignorando número, bloco, apartamento."""
    pular_padrao = re.compile(
        r"^(n[oº°]?\s*\d+|apto\.?|bloco|quadra|lote|\d+\s*$)",
        re.IGNORECASE,
    )
    for i in range(cidade_idx - 1, -1, -1):
        candidato = partes[i].strip()
        if not candidato:
            continue
        if pular_padrao.match(candidato) or re.fullmatch(r"\d+[a-zA-Z]?", candidato):
            continue
        return candidato
    return partes[max(0, cidade_idx - 1)]


def bairro_protocolo(dados_dinamicos, endereco_texto: str, endereco_usuario: str = "") -> str:
    """Prioridade: JSON do protocolo → endereço do protocolo → cadastro do cidadão."""
    b = bairro_de_dados_dinamicos(dados_dinamicos)
    if b:
        return b
    b = bairro_de_endereco_texto(endereco_texto)
    if b:
        return b
    return (endereco_usuario or "").strip()


def _bairro_usuario(protocolo) -> str:
    usuario = getattr(protocolo, "usuario", None)
    if not usuario:
        return ""
    endereco = getattr(usuario, "endereco", None)
    if endereco and getattr(endereco, "bairro", None):
        return (endereco.bairro or "").strip()
    return ""


def _enriquecer_via_geocode(protocolo) -> tuple[str, str, str]:
    """Reverse geocode quando há ponto e o texto ainda não basta. Retorna bairro, cidade, endereco."""
    if not protocolo.localizacao:
        return "", "", ""
    from atendimentos.geocoding import reverse_geocode

    lat = float(protocolo.localizacao.y)
    lng = float(protocolo.localizacao.x)
    dados = reverse_geocode(lat, lng)
    if not dados:
        return "", "", ""
    bairro = (dados.get("bairro") or "").strip()
    cidade = (dados.get("cidade") or "").strip()
    endereco = (dados.get("endereco_completo") or "").strip()
    return bairro, cidade, endereco


def _bairro_equipamento_vinculado(protocolo) -> str:
    eq_id = getattr(protocolo, "equipamento_id", None)
    if not eq_id:
        return ""
    eq = getattr(protocolo, "equipamento", None)
    if eq is None:
        from catalogo.models import EquipamentoPublico

        eq = EquipamentoPublico.objects.filter(pk=eq_id).only("bairro").first()
    if eq and (eq.bairro or "").strip():
        return (eq.bairro or "").strip()
    return ""


def sincronizar_localidade_protocolo(protocolo, *, persistir: bool = True) -> bool:
    """
    Garante ``dados_dinamicos.bairro`` (e ``cidade`` quando possível) no protocolo.
    Ordem: JSON existente → equipamento vinculado → ``endereco_texto`` → cidadão → geocode.
    """
    dados = dict(protocolo.dados_dinamicos or {})
    alterou_dados = False
    alterou_endereco = False

    bairro_equipamento = _bairro_equipamento_vinculado(protocolo)
    if bairro_equipamento:
        bairro = bairro_equipamento
    else:
        bairro = bairro_de_dados_dinamicos(dados)
        if not bairro:
            bairro = bairro_de_endereco_texto(protocolo.endereco_texto or "")
        if not bairro:
            bairro = _bairro_usuario(protocolo)
    cidade = (dados.get("cidade") or "").strip()

    if not cidade or (not bairro and not bairro_equipamento):
        geo_bairro, geo_cidade, geo_endereco = _enriquecer_via_geocode(protocolo)
        if not bairro and geo_bairro and not bairro_equipamento:
            bairro = geo_bairro
        if not cidade and geo_cidade:
            cidade = geo_cidade
        if not (protocolo.endereco_texto or "").strip() and geo_endereco:
            protocolo.endereco_texto = geo_endereco[:500]
            alterou_endereco = True

    if bairro and dados.get("bairro") != bairro:
        dados["bairro"] = bairro
        alterou_dados = True
    if cidade and dados.get("cidade") != cidade:
        dados["cidade"] = cidade
        alterou_dados = True

    if alterou_dados:
        protocolo.dados_dinamicos = dados

    if not (alterou_dados or alterou_endereco):
        return False

    if persistir and protocolo.pk:
        campos = []
        if alterou_dados:
            campos.append("dados_dinamicos")
        if alterou_endereco:
            campos.append("endereco_texto")
        if campos:
            protocolo.save(update_fields=campos + ["data_atualizacao"])
    return True