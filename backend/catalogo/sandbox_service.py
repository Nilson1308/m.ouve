"""Serviço de simulação (dry-run) do fluxo conversacional do catálogo."""

from __future__ import annotations

import logging
from atendimentos.chat_sandbox import (
    montar_sessao_sandbox,
    turno_sandbox_para_resposta,
)
from atendimentos.llm_orchestrator import ChatOrchestrationError, LLMOrchestrator
from catalogo.models import ServicoCatalogo

logger = logging.getLogger(__name__)


class _ServicoSandboxOverlay:
    """Proxy mínimo — schemas de rascunho sem alterar o registro persistido."""

    def __init__(self, servico: ServicoCatalogo, formulario, schema):
        object.__setattr__(self, "_servico", servico)
        object.__setattr__(self, "formulario_schema", formulario)
        object.__setattr__(self, "schema_formulario", schema)

    def __getattr__(self, name):
        return getattr(self._servico, name)

    @property
    def pk(self):
        return self._servico.pk


def servico_sandbox_com_origem(
    servico: ServicoCatalogo,
    *,
    usar_rascunho: bool | None = None,
) -> tuple[ServicoCatalogo, str]:
    """
    Retorna serviço efetivo no sandbox e rótulo ``origem_schema`` (rascunho|publicado).
    ``usar_rascunho`` None → True se houver rascunho pendente.
    """
    usar = usar_rascunho
    if usar is None:
        usar = servico.tem_rascunho_pendente
    if usar and servico.tem_rascunho_pendente:
        formulario = (
            servico.formulario_schema_rascunho
            if servico.formulario_schema_rascunho is not None
            else servico.formulario_schema
        )
        schema = (
            servico.schema_formulario_rascunho
            if servico.schema_formulario_rascunho is not None
            else servico.schema_formulario
        )
        return _ServicoSandboxOverlay(servico, formulario, schema), "rascunho"  # type: ignore[return-value]
    return servico, "publicado"


def executar_sandbox_servico_catalogo(
    servico: ServicoCatalogo,
    *,
    mensagem: str = "",
    dados_parciais: dict | None = None,
    dados_slot: dict | None = None,
    anexos_novos: int = 0,
    localizacao_ok: bool = False,
    localizacao: dict | None = None,
    historico: list | None = None,
    usar_rascunho: bool | None = None,
) -> dict:
    """
    Roda extração + próximo passo sem persistir SessaoChat ou Protocolo.
    Estado vive apenas nesta chamada (``SessaoSandbox``).
    """
    servico_efetivo, origem_schema = servico_sandbox_com_origem(
        servico, usar_rascunho=usar_rascunho
    )
    ctx = montar_sessao_sandbox(
        servico_efetivo,
        dados_parciais=dados_parciais,
        localizacao_ok=localizacao_ok,
        localizacao=localizacao,
        anexos_count=int(dados_parciais.get("_anexos_count", 0) if dados_parciais else 0)
        + anexos_novos,
        historico=historico,
    )
    texto = (mensagem or "").strip()
    if texto:
        ctx.historico = [*ctx.historico, {"role": "user", "content": texto}]

    orchestrator = LLMOrchestrator()
    try:
        turno = orchestrator.simular_turno_catalogo_sandbox(
            ctx,
            texto_usuario=texto,
            dados_slot=dados_slot,
            anexos_novos=anexos_novos,
        )
    except ChatOrchestrationError as exc:
        logger.warning("Sandbox LLM: %s", exc)
        return {
            "modo": "sandbox",
            "origem_schema": origem_schema,
            "erro": str(exc),
            "resposta_cidadao": str(exc),
            "acao_ui": None,
            "payload_ui": None,
            "dados_parciais": {
                k: v for k, v in (ctx.dados_coletados or {}).items() if not str(k).startswith("_")
            },
            "servico_id": str(servico.id),
            "servico_nome": servico.nome,
        }

    resposta = turno_sandbox_para_resposta(turno, ctx.dados_coletados)
    resposta["origem_schema"] = origem_schema
    resposta["servico_id"] = str(servico.id)
    resposta["servico_nome"] = servico.nome
    if turno.resposta_cidadao:
        ctx.historico = [*ctx.historico, {"role": "assistant", "content": turno.resposta_cidadao}]
    resposta["historico_sugerido"] = ctx.historico
    return resposta