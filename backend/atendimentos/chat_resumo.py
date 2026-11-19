"""Montagem de resumo legível para revisão do chat (cidadão)."""

from __future__ import annotations

from typing import Any

from atendimentos.models import AnexoChatSessao, MensagemChat, SessaoChat

_MSG_CIDADAO_IGNORAR = frozenset({"sim", "nao", "não", "ok", "s", "n", "(sem texto)"})
_MSG_PREFIXOS_IGNORAR = ("📍", "📷", "✅", "(o cidadão", "(confirmação", "confirmar protocolo")


def _schema_props(schema: dict) -> dict:
    s = dict(schema or {})
    s.pop("$metadata", None)
    s.pop("$schema", None)
    return s.get("properties") or {}


def _dados_negocio(sessao: SessaoChat) -> dict[str, Any]:
    return {k: v for k, v in (sessao.dados_coletados or {}).items() if not str(k).startswith("_")}


def _formatar_valor(prop: dict, valor: Any) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, bool):
        return "Sim" if valor else "Não"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, list):
        items = prop.get("items") or {}
        enums = items.get("enum") or prop.get("enum") or []
        names = items.get("enumNames") or prop.get("enumNames") or []
        partes: list[str] = []
        for v in valor:
            if enums and v in enums:
                idx = enums.index(v)
                partes.append(names[idx] if idx < len(names) else str(v))
            else:
                partes.append(str(v))
        return ", ".join(partes) if partes else "—"
    enums = prop.get("enum") or []
    names = prop.get("enumNames") or []
    if enums and valor in enums:
        idx = enums.index(valor)
        if idx < len(names):
            return names[idx]
    s = str(valor).strip()
    return s if s else "—"


def _mensagem_cidadao_util(texto: str) -> bool:
    t = (texto or "").strip()
    if len(t) < 4:
        return False
    tl = t.lower()
    if tl in _MSG_CIDADAO_IGNORAR:
        return False
    if any(tl.startswith(p) for p in _MSG_PREFIXOS_IGNORAR):
        return False
    return True


def _mensagens_cidadao(sessao: SessaoChat) -> list[str]:
    vistos: set[str] = set()
    linhas: list[str] = []
    for msg in sessao.mensagens.filter(autor=MensagemChat.Autor.CIDADAO).order_by("criado_em"):
        t = (msg.conteudo_texto or "").strip()
        if not _mensagem_cidadao_util(t):
            continue
        chave = t.lower()
        if chave in vistos:
            continue
        vistos.add(chave)
        linhas.append(t)
    return linhas


def _descricao_inicial(sessao: SessaoChat) -> str:
    dados = _dados_negocio(sessao)
    for chave in (
        "descricao_detalhada",
        "descricao_problema",
        "informacao_solicitada",
        "observacoes",
    ):
        val = dados.get(chave)
        if isinstance(val, str) and len(val.strip()) >= 8:
            return val.strip()
    mensagens = _mensagens_cidadao(sessao)
    return mensagens[0] if mensagens else ""


def _linhas_campos_coletados(sessao: SessaoChat, dados: dict) -> list[str]:
    servico = sessao.servico_identificado
    if not servico or not dados:
        return []
    props = _schema_props(servico.schema_formulario)
    ordem = list((servico.schema_formulario or {}).get("required") or [])
    ordem.extend(k for k in dados if k not in ordem)
    linhas: list[str] = []
    vistos: set[str] = set()
    for chave in ordem:
        if chave in vistos or chave not in dados:
            continue
        vistos.add(chave)
        prop = props.get(chave) or {}
        rotulo = prop.get("title") or chave.replace("_", " ").title()
        valor = _formatar_valor(prop, dados.get(chave))
        if valor == "—":
            continue
        outro = dados.get(f"{chave}_outro")
        if outro and str(outro).strip():
            valor = f"{valor}; detalhe: {str(outro).strip()}" if valor != "—" else str(outro).strip()
        linhas.append(f"{rotulo}: {valor}")
    return linhas


def montar_descricao_protocolo(sessao: SessaoChat, *, max_caracteres: int = 8000) -> str:
    """Texto persistido em ``Protocolo.descricao``: solicitação do cidadão, não resposta da IA."""
    partes: list[str] = []
    servico = sessao.servico_identificado
    if servico:
        partes.append(f"Serviço: {servico.nome}")

    mensagens = _mensagens_cidadao(sessao)
    if mensagens:
        partes.append("")
        partes.append("Relato do cidadão:")
        for msg in mensagens:
            partes.append(f"• {msg}")

    dados = _dados_negocio(sessao)
    campos = _linhas_campos_coletados(sessao, dados)
    if campos:
        partes.append("")
        partes.append("Dados da solicitação:")
        partes.extend(f"• {linha}" for linha in campos)

    loc = (sessao.dados_coletados or {}).get("_localizacao") or {}
    endereco = (loc.get("endereco") or "").strip()
    if endereco:
        partes.append("")
        partes.append(f"Local informado: {endereco}")

    qtd = AnexoChatSessao.objects.filter(sessao=sessao).count()
    if qtd:
        partes.append(f"Anexos na conversa: {qtd}")

    texto = "\n".join(partes).strip()
    if not texto:
        return "Solicitação registrada via chat M.Ouve"
    if len(texto) > max_caracteres:
        return texto[: max_caracteres - 3].rstrip() + "..."
    return texto


def montar_resumo_revisao(sessao: SessaoChat, request=None) -> dict[str, Any]:
    servico = sessao.servico_identificado
    dados = _dados_negocio(sessao)
    loc = (sessao.dados_coletados or {}).get("_localizacao") or {}
    props = _schema_props(servico.schema_formulario) if servico else {}

    campos: list[dict[str, str]] = []
    vistos: set[str] = set()
    ordem = list((servico.schema_formulario or {}).get("required") or []) if servico else []
    ordem.extend(k for k in dados if k not in ordem)

    for chave in ordem:
        if chave in vistos or chave not in dados:
            continue
        vistos.add(chave)
        prop = props.get(chave) or {}
        campos.append(
            {
                "chave": chave,
                "rotulo": prop.get("title") or chave.replace("_", " ").title(),
                "valor": _formatar_valor(prop, dados.get(chave)),
            }
        )

    localizacao = None
    if loc.get("latitude") is not None and loc.get("longitude") is not None:
        localizacao = {
            "endereco": (loc.get("endereco") or "").strip() or "Localização no mapa",
            "latitude": float(loc["latitude"]),
            "longitude": float(loc["longitude"]),
        }

    anexos = AnexoChatSessao.objects.filter(sessao=sessao).order_by("criado_em")
    fotos = []
    for a in anexos:
        if not (a.tipo_mime or "").startswith("image/"):
            continue
        url = a.arquivo.url if a.arquivo else None
        if url:
            from ouvia_core.url_utils import public_absolute_uri

            url = public_absolute_uri(request, url)
        fotos.append({"nome": a.nome_original or "Foto", "url": url})

    return {
        "servico_nome": servico.nome if servico else "",
        "categoria": servico.categoria.nome if servico and servico.categoria_id else "",
        "descricao_inicial": _descricao_inicial(sessao),
        "campos": campos,
        "localizacao": localizacao,
        "fotos": fotos,
        "total_anexos": anexos.count(),
    }
