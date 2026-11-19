"""Simulador de chat do catálogo — dry-run em memória (sem SessaoChat/Protocolo)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from catalogo.models import ServicoCatalogo


@dataclass
class SessaoSandbox:
    """
    Duck-type mínimo de ``SessaoChat`` para o orquestrador.
    Produção persiste sessão; sandbox só mantém estado em RAM nesta requisição.
    """

    servico: ServicoCatalogo
    dados_coletados: dict[str, Any] = field(default_factory=dict)
    sandbox_qtd_anexos: int = 0
    historico: list[dict[str, str]] = field(default_factory=list)

    @property
    def servico_identificado(self) -> ServicoCatalogo:
        return self.servico

    @property
    def servico_identificado_id(self):
        return self.servico.pk


def montar_sessao_sandbox(
    servico: ServicoCatalogo,
    *,
    dados_parciais: dict | None = None,
    localizacao_ok: bool = False,
    localizacao: dict | None = None,
    anexos_count: int = 0,
    historico: list | None = None,
) -> SessaoSandbox:
    dados = dict(dados_parciais or {})
    if localizacao_ok or localizacao:
        loc = dict(localizacao or {})
        if localizacao_ok and not loc.get("latitude"):
            loc.setdefault("latitude", -23.5)
            loc.setdefault("longitude", -46.6)
            loc.setdefault("endereco", loc.get("endereco") or "Local simulado (sandbox)")
        dados["_localizacao"] = loc
    return SessaoSandbox(
        servico=servico,
        dados_coletados=dados,
        sandbox_qtd_anexos=max(0, int(anexos_count or 0)),
        historico=list(historico or []),
    )


def mesclar_dados_sandbox(sessao: SessaoSandbox, extraidos: dict | None) -> None:
    if not extraidos:
        return
    dados = dict(sessao.dados_coletados or {})
    for chave, valor in extraidos.items():
        if str(chave).startswith("_"):
            continue
        dados[chave] = valor
    sessao.dados_coletados = dados


def turno_sandbox_para_resposta(turno, dados: dict) -> dict[str, Any]:
    from atendimentos.llm_orchestrator import TurnResult

    if not isinstance(turno, TurnResult):
        raise TypeError("turno deve ser TurnResult")
    slots = {k: v for k, v in (dados or {}).items() if not str(k).startswith("_")}
    payload_ui = turno.config_escolha
    out = {
        "modo": "sandbox",
        "resposta_cidadao": turno.resposta_cidadao,
        "acao_ui": turno.acao_ui,
        "payload_ui": payload_ui,
        "dados_parciais": slots,
        "dados_extraidos_turno": turno.dados_extraidos or {},
        "ir_para_revisao": turno.ir_para_revisao,
        "fluxo_bloqueado": turno.fluxo_bloqueado,
    }
    if turno.fluxo_bloqueado:
        out["mensagem_bloqueio"] = turno.resposta_cidadao
    return out