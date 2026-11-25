"""Contexto operacional do link mágico (LGPD — sem PII do cidadão)."""

from __future__ import annotations

from typing import Any

from django.utils import timezone

from atendimentos.magic_link_services import token_magic_link_valido
from atendimentos.models import (
    AnexoOrdemServico,
    AnexoProtocolo,
    DiligenciaProtocolo,
    OrdemServico,
    ReaberturaProtocolo,
)
from atendimentos.services.diligencia_service import (
    carregar_mapa_anexos_protocolo,
    serializar_anexo_protocolo,
    serializar_anexos_diligencia,
)
from ouvia_core.url_utils import public_absolute_uri


def _coordenadas_ponto(ponto) -> tuple[float | None, float | None]:
    if not ponto:
        return None, None
    return float(ponto.y), float(ponto.x)


def _bairro_protocolo(protocolo) -> str:
    dados = protocolo.dados_dinamicos or {}
    for chave in ("bairro", "nome_bairro", "bairro_informado"):
        val = dados.get(chave)
        if val:
            return str(val).strip()
    eq = protocolo.equipamento
    if eq and eq.bairro:
        return eq.bairro.strip()
    return ""


def _serializar_equipamento(equipamento, request) -> dict | None:
    if not equipamento:
        return None
    lat, lng = _coordenadas_ponto(equipamento.localizacao)
    return {
        "nome": equipamento.nome,
        "tipo": equipamento.tipo,
        "bairro": equipamento.bairro or "",
        "endereco": equipamento.endereco or "",
        "latitude": lat,
        "longitude": lng,
    }


def _serializar_evidencia_campo(anexo: AnexoOrdemServico, *, request) -> dict[str, Any]:
    mime = anexo.tipo_mime or "application/octet-stream"
    nome = (anexo.nome_original or "").strip()
    if not nome and anexo.arquivo and anexo.arquivo.name:
        nome = anexo.arquivo.name.rsplit("/", 1)[-1]
    return {
        "id": str(anexo.id),
        "url": public_absolute_uri(request, anexo.arquivo.url if anexo.arquivo else None),
        "nome": nome or "evidencia",
        "mime_type": mime,
    }


def _serializar_diligencia_publica(d: DiligenciaProtocolo, *, request, mapa_anexos) -> dict[str, Any]:
    return {
        "id": str(d.id),
        "status": d.status,
        "pergunta": d.pergunta,
        "resposta_cidadao": d.resposta_cidadao or "",
        "respondida_em": (
            d.respondida_em.strftime("%Y-%m-%dT%H:%M:%SZ") if d.respondida_em else None
        ),
        "anexos": serializar_anexos_diligencia(
            d.anexos_ids,
            protocolo_id=d.protocolo_id,
            request=request,
            mapa=mapa_anexos,
        ),
    }


def motivo_bloqueio_magic_link(ordem: OrdemServico) -> tuple[int, str] | None:
    """
    Retorna (HTTP status, detail) se o link não puder ser usado; None se OK.
    """
    if ordem.status == OrdemServico.Status.CANCELADA:
        return 410, "Esta ordem não aceita evidências."
    if ordem.status == OrdemServico.Status.CONCLUIDA:
        return 410, "Ordem já concluída — envio de evidências encerrado."
    if ordem.status == OrdemServico.Status.AGUARDANDO_ASSINATURA:
        return 410, "Ordem já formalizada — aguardando assinatura do gestor."
    if ordem.data_formalizacao:
        return 410, "Ordem já formalizada — link encerrado."
    if not token_magic_link_valido(ordem):
        return 410, "Link expirado. Solicite um novo link à secretaria."
    return None


def montar_contexto_magic_link(ordem: OrdemServico, *, request) -> dict[str, Any]:
    protocolo = ordem.protocolo
    servico = protocolo.servico
    lat, lng = _coordenadas_ponto(protocolo.localizacao)

    prazo_sla = ordem.prazo_sla or protocolo.prazo_sla
    prazo_sla_iso = (
        prazo_sla.strftime("%Y-%m-%dT%H:%M:%SZ") if prazo_sla else None
    )

    anexos_protocolo = list(
        AnexoProtocolo.objects.filter(protocolo_id=protocolo.pk).order_by("criado_em")
    )
    anexos_iniciais = [
        {
            "id": item["id"],
            "url": item["url"],
            "nome": item.get("nome") or item.get("nome_arquivo") or "",
            "mime_type": item.get("mime_type") or item.get("tipo") or "",
        }
        for item in (
            serializar_anexo_protocolo(a, request=request) for a in anexos_protocolo
        )
    ]

    diligencias_qs = (
        DiligenciaProtocolo.objects.filter(protocolo_id=protocolo.pk)
        .exclude(status=DiligenciaProtocolo.Status.CANCELADA)
        .order_by("criado_em")
    )
    todos_ids: set[str] = set()
    for d in diligencias_qs:
        for aid in d.anexos_ids or []:
            todos_ids.add(str(aid))
    mapa_anexos = carregar_mapa_anexos_protocolo(protocolo.pk, todos_ids)
    diligencias = [
        _serializar_diligencia_publica(d, request=request, mapa_anexos=mapa_anexos)
        for d in diligencias_qs
    ]

    evidencias_campo = [
        _serializar_evidencia_campo(a, request=request)
        for a in ordem.anexos.all().order_by("criado_em")
    ]

    reab = (
        ReaberturaProtocolo.objects.filter(ordem_servico_criada_id=ordem.pk)
        .order_by("-criado_em")
        .first()
    )
    motivo_reabertura = None
    reabertura_anexos: list[dict] = []
    if reab:
        motivo_reabertura = reab.motivo
        reabertura_anexos = serializar_anexos_diligencia(
            reab.anexos_ids,
            protocolo_id=protocolo.pk,
            request=request,
        )

    despacho = (ordem.despacho_tecnico or "").strip()
    instrucao = (ordem.descricao or "").strip()
    instrucoes = despacho
    if instrucao and instrucao != despacho:
        instrucoes = f"{instrucao}\n\n{despacho}".strip() if despacho else instrucao

    return {
        "ordem_servico_id": str(ordem.id),
        "numero_protocolo": protocolo.codigo,
        "status_os": ordem.status,
        "unidade_nome": ordem.unidade.nome if ordem.unidade_id else "",
        "servico_nome": servico.nome if servico else "",
        "prazo_sla": prazo_sla_iso,
        "magic_link_expira_em": (
            ordem.magic_link_expira_em.strftime("%Y-%m-%dT%H:%M:%SZ")
            if ordem.magic_link_expira_em
            else None
        ),
        "equipamento": _serializar_equipamento(protocolo.equipamento, request),
        "endereco_texto": (protocolo.endereco_texto or "").strip(),
        "bairro": _bairro_protocolo(protocolo),
        "latitude": lat,
        "longitude": lng,
        "descricao_solicitacao": (protocolo.descricao or "").strip(),
        "instrucoes_despacho": instrucoes,
        "motivo_reabertura": motivo_reabertura,
        "reabertura_anexos": reabertura_anexos,
        "anexos_iniciais": anexos_iniciais,
        "diligencias": diligencias,
        "evidencias_campo_enviadas": evidencias_campo,
        "gerado_em": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }