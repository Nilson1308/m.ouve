"""Montagem de resumo legível para revisão do chat (cidadão)."""

from __future__ import annotations

from typing import Any

from atendimentos.campo_exibicao import (
    formatar_valor_campo,
    ordem_campos_exibicao,
    rotulo_campo_schema,
)
from atendimentos.models import AnexoChatSessao, MensagemChat, SessaoChat

_MSG_CIDADAO_IGNORAR = frozenset({"sim", "nao", "não", "ok", "s", "n", "(sem texto)"})
_MSG_PREFIXOS_IGNORAR = ("📍", "📷", "✅", "(o cidadão", "(confirmação", "confirmar protocolo")
_CHAVES_NARRATIVA = (
    "descricao_detalhada",
    "descricao_problema",
    "descricao",
    "d",
    "informacao_solicitada",
    "observacoes",
    "relato",
)


def _schema_props(schema: dict) -> dict:
    s = dict(schema or {})
    s.pop("$metadata", None)
    s.pop("$schema", None)
    return s.get("properties") or {}


def _dados_negocio(sessao: SessaoChat) -> dict[str, Any]:
    return {k: v for k, v in (sessao.dados_coletados or {}).items() if not str(k).startswith("_")}


def _formatar_valor(prop: dict, valor: Any) -> str:
    return formatar_valor_campo(prop, valor)


def _mensagem_cidadao_util(texto: str) -> bool:
    t = (texto or "").strip()
    if len(t) < 4:
        return False
    tl = t.lower()
    if tl in _MSG_CIDADAO_IGNORAR:
        return False
    if any(tl.startswith(p) for p in _MSG_PREFIXOS_IGNORAR):
        return False
    if "✓" in t or "?:" in t:
        return False
    if "confirmar e gerar protocolo" in tl:
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


def _dados_negocio_dict(dados: dict | None) -> dict[str, Any]:
    return {k: v for k, v in (dados or {}).items() if not str(k).startswith("_")}


def _narrativa_de_dados(servico, dados: dict) -> str:
    props = _schema_props(servico.schema_formulario) if servico else {}
    for chave in _CHAVES_NARRATIVA:
        val = dados.get(chave)
        if isinstance(val, str) and len(val.strip()) >= 8:
            return val.strip()
    candidatos: list[tuple[int, str]] = []
    for chave, valor in dados.items():
        if not isinstance(valor, str):
            continue
        txt = valor.strip()
        if len(txt) < 12:
            continue
        prop = props.get(chave) or {}
        if prop.get("format") == "textarea" or len(txt) >= 40:
            candidatos.append((len(txt), txt))
    if candidatos:
        return max(candidatos, key=lambda x: x[0])[1]
    return ""


def limpar_descricao_legada(texto: str) -> str:
    """Remove blocos repetidos de protocolos gerados com formato antigo do chat."""
    if not texto:
        return ""
    t = texto
    if "Dados da solicitação:" in t:
        t = t.split("Dados da solicitação:")[0]
    linhas_uteis: list[str] = []
    for raw in t.splitlines():
        line = raw.strip()
        if not line or line.startswith("Serviço:"):
            continue
        if line in ("Relato do cidadão:", "Dados da solicitação:"):
            continue
        if line.startswith("Local informado:") or line.startswith("Anexos na conversa:"):
            continue
        if line.startswith("•"):
            line = line.lstrip("• ").strip()
        if "✓" in line or "?:" in line:
            continue
        if len(line) < 8:
            continue
        linhas_uteis.append(line)
    vistos: set[str] = set()
    unicos: list[str] = []
    for ln in linhas_uteis:
        chave = ln.lower()
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(ln)
    if unicos:
        return max(unicos, key=len)
    return t.strip()[:2000]


def narrativa_protocolo(servico, dados_dinamicos: dict | None, descricao_armazenada: str = "") -> str:
    dados = _dados_negocio_dict(dados_dinamicos)
    narrativa = _narrativa_de_dados(servico, dados)
    if narrativa:
        return narrativa
    return limpar_descricao_legada(descricao_armazenada or "")


def descricao_exibicao_cidadao(protocolo) -> str:
    """Texto único para o PWA — sem repetir campos estruturados."""
    texto = narrativa_protocolo(
        protocolo.servico,
        protocolo.dados_dinamicos,
        protocolo.descricao or "",
    )
    return texto or "Solicitação registrada."


def montar_campos_protocolo_publico(servico, dados_dinamicos: dict | None) -> list[dict[str, str]]:
    """Campos estruturados com rótulos do schema (evita chaves ``d``/``o``/``q`` na UI)."""
    dados = _dados_negocio_dict(dados_dinamicos)
    if not dados:
        return []
    props = _schema_props(servico.schema_formulario) if servico else {}
    narrativa = _narrativa_de_dados(servico, dados) if servico else ""

    ordem = ordem_campos_exibicao(servico, dados) if servico else list(dados.keys())

    campos: list[dict[str, str]] = []
    vistos: set[str] = set()
    for chave in ordem:
        if chave in vistos or chave not in dados:
            continue
        vistos.add(chave)
        prop = props.get(chave) or {}
        valor_fmt = _formatar_valor(prop, dados.get(chave))
        if valor_fmt == "—":
            continue
        if narrativa and isinstance(dados.get(chave), str) and dados.get(chave).strip() == narrativa:
            continue
        campos.append(
            {
                "chave": chave,
                "rotulo": rotulo_campo_schema(prop, chave),
                "valor": valor_fmt,
            }
        )
    return campos


def montar_descricao_protocolo(sessao: SessaoChat, *, max_caracteres: int = 8000) -> str:
    """Texto persistido em ``Protocolo.descricao``: apenas a narrativa (campos ficam em ``dados_dinamicos``)."""
    servico = sessao.servico_identificado
    dados = _dados_negocio(sessao)
    narrativa = _descricao_inicial(sessao) or _narrativa_de_dados(servico, dados)
    if not narrativa:
        mensagens = _mensagens_cidadao(sessao)
        if mensagens:
            narrativa = max(mensagens, key=len)
    texto = (narrativa or "").strip() or "Solicitação registrada via chat M.Ouve"
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
    ordem = ordem_campos_exibicao(servico, dados) if servico else list(dados.keys())

    for chave in ordem:
        if chave in vistos or chave not in dados:
            continue
        vistos.add(chave)
        prop = props.get(chave) or {}
        campos.append(
            {
                "chave": chave,
                "rotulo": rotulo_campo_schema(prop, chave),
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
