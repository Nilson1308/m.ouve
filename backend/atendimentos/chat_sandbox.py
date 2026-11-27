"""Simulador de chat do catálogo — dry-run em memória (sem SessaoChat/Protocolo)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from catalogo.models import ServicoCatalogo


def is_sessao_sandbox(sessao) -> bool:
    return type(sessao).__name__ == "SessaoSandbox"


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

    def save(self, update_fields=None, **kwargs):
        """No-op — persistência só em ``SessaoChat``."""

    def refresh_from_db(self, fields=None):
        """No-op — sem registro no banco."""


CHAVES_ESTADO_SANDBOX = (
    "_campos_pulados",
    "_meta",
    "_localizacao",
    "_anexos_count",
)


def exportar_dados_parciais_sandbox(dados: dict | None) -> dict[str, Any]:
    """
    Slots visíveis + chaves internas necessárias para o próximo turno do sandbox
  (mesma máquina de estados do PWA, sem SessaoChat persistida).
    """
    bruto = dict(dados or {})
    out = {k: v for k, v in bruto.items() if not str(k).startswith("_")}
    for chave in CHAVES_ESTADO_SANDBOX:
        val = bruto.get(chave)
        if val is None:
            continue
        if chave == "_campos_pulados" and not val:
            continue
        if chave == "_meta" and not val:
            continue
        out[chave] = val
    return out


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
    qtd_anexos = max(0, int(anexos_count or 0))
    if qtd_anexos:
        dados["_anexos_count"] = qtd_anexos
    return SessaoSandbox(
        servico=servico,
        dados_coletados=dados,
        sandbox_qtd_anexos=qtd_anexos,
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
    slots = exportar_dados_parciais_sandbox(dados)
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