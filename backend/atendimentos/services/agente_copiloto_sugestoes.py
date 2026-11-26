from __future__ import annotations

from typing import Final

# Rotas reais do Backoffice (src/router/index.js — filhos de /backoffice)
ROTAS_BACKOFFICE_VUE: Final[tuple[str, ...]] = (
    "/backoffice/mesa-trabalho",
    "/backoffice/dashboard",
    "/backoffice/dashboard/mapa-gis",
    "/backoffice/dashboard/inelegibilidade",
    "/backoffice/relatorios/sla-cobrancas",
    "/backoffice/setorial",
    "/backoffice/notificacoes",
    "/backoffice/configuracoes",
    "/backoffice/textos-padrao",
    "/backoffice/manual",
)

# Fragmentos de caminho permitidos (só os usados no router ou aliases estáveis do front)
FRAGMENTOS_ROTA_PERMITIDOS: Final[frozenset[str]] = frozenset(
    {
        "mesa-trabalho",
        "mesa",
        "protocolo",
        "dashboard",
        "mapa-gis",
        "inelegibilidade",
        "triagem",
        "bloqueios",
        "sla-cobrancas",
        "sla",
        "setorial",
        # Aliases aceitos em query/contexto (não existem como path no router)
        "eficiencia",
        "executiva",
        "executivo",
        "territorial",
        "mapa",
        "gis",
    }
)

# 3 sugestões padrão por perspectiva (100% SaaS, somente leitura, zero PII)
SUGESTOES_COPILOTO_POR_PERFIL: Final[dict[str, tuple[str, str, str]]] = {
    "controladoria": (
        "Quais secretarias concentram mais atrasos de SLA e cobranças de cidadãos hoje?",
        "Onde a taxa de retrabalho subiu ou a satisfação (CSAT) caiu nos últimos 30 dias?",
        "Quais equipamentos públicos ou bairros com ocorrência georreferenciada tiveram pico nas últimas duas semanas?",
    ),
    "ouvidoria": (
        "Quais protocolos estão parados há mais tempo na triagem ou aguardando homologação?",
        "Existem protocolos críticos sem ordem de serviço ou sugestões de urgência da IA pendentes?",
        "Quais regras de inelegibilidade mais barraram cidadãos no chat nos últimos 30 dias?",
    ),
    "unidade": (
        "Quais ordens de serviço da minha pasta estão vencidas, críticas ou perto do prazo?",
        "Temos diligências já respondidas pelo cidadão aguardando ação da equipe?",
        "Quais serviços ou equipamentos da minha unidade tiveram mais reaberturas neste mês?",
    ),
}

# Sobreposição das 2 primeiras sugestões por rota ativa (escopo municipal: controladoria / ouvidoria)
# Cada entrada: (fragmentos, rotas_canonicas, sugestões) — ordem: mais específica primeiro.
SUGESTOES_COPILOTO_POR_ROTA_MUNICIPAL: Final[
    tuple[tuple[tuple[str, ...], tuple[str, ...], tuple[str, str]], ...]
] = (
    (
        ("sla-cobrancas", "sla"),
        ("/backoffice/relatorios/sla-cobrancas",),
        (
            "Quais protocolos atrasados já acumularam cobrança do cidadão?",
            "Onde está o maior risco de escalonamento para a Controladoria esta semana?",
        ),
    ),
    (
        ("inelegibilidade", "triagem", "bloqueios"),
        ("/backoffice/dashboard/inelegibilidade",),
        (
            "Qual serviço concentra mais bloqueios de inelegibilidade no chat?",
            "Quais motivos de bloqueio indicam falta de orientação clara ao cidadão?",
        ),
    ),
    (
        ("mapa-gis", "territorial", "mapa", "gis"),
        ("/backoffice/dashboard/mapa-gis",),
        (
            "Quais bairros com ocorrência georreferenciada mais cresceram nos últimos 14 dias?",
            "Quais equipamentos públicos concentram mais chamados abertos no momento?",
        ),
    ),
    (
        ("eficiencia", "executiva", "executivo", "dashboard"),
        ("/backoffice/dashboard",),
        (
            "Faça um resumo executivo de SLA, TMA, CSAT e retrabalho dos últimos 30 dias.",
            "Qual é o principal gargalo estrutural reduzindo nossa eficiência hoje?",
        ),
    ),
    (
        ("setorial",),
        ("/backoffice/setorial",),
        (
            "Quais ordens de serviço estão atrasadas ou próximas do vencimento na operação?",
            "Quais protocolos reabertos ou com diligência respondida aguardam ação em campo?",
        ),
    ),
    (
        ("mesa-trabalho", "mesa", "protocolo"),
        ("/backoffice/mesa-trabalho",),
        (
            "O que exige ação imediata na fila de triagem e homologação hoje?",
            "Quais protocolos têm sugestão de urgência da IA pendente de revisão?",
        ),
    ),
)

# Sobreposição das 2 primeiras sugestões por rota ativa para escopo estrito de unidade (anti-IDOR UX)
SUGESTOES_COPILOTO_POR_ROTA_UNIDADE: Final[
    tuple[tuple[tuple[str, ...], tuple[str, ...], tuple[str, str]], ...]
] = (
    (
        ("sla-cobrancas", "sla"),
        ("/backoffice/relatorios/sla-cobrancas",),
        (
            "Quais protocolos da minha pasta estão atrasados ou com cobrança do cidadão?",
            "Quais ordens de serviço da minha unidade vencem nas próximas 48 horas?",
        ),
    ),
    (
        ("inelegibilidade", "triagem", "bloqueios"),
        ("/backoffice/dashboard/inelegibilidade",),
        (
            "Quais serviços da minha pasta tiveram mais bloqueios de inelegibilidade no chat?",
            "Quais motivos de bloqueio na minha unidade indicam necessidade de orientar melhor o cidadão?",
        ),
    ),
    (
        ("mapa-gis", "territorial", "mapa", "gis"),
        ("/backoffice/dashboard/mapa-gis",),
        (
            "Quais equipamentos públicos da minha pasta concentram mais chamados abertos?",
            "Em quais bairros com ocorrência georreferenciada a demanda da minha unidade cresceu?",
        ),
    ),
    (
        ("eficiencia", "executiva", "executivo", "dashboard"),
        ("/backoffice/dashboard",),
        (
            "Faça um resumo de SLA, TMA, CSAT e retrabalho da minha unidade nos últimos 30 dias.",
            "Qual serviço da minha pasta mais impacta o tempo médio de atendimento hoje?",
        ),
    ),
    (
        ("setorial", "mesa-trabalho", "mesa", "protocolo"),
        ("/backoffice/setorial", "/backoffice/mesa-trabalho"),
        (
            "Quais ordens de serviço da minha pasta vencem nas próximas 48 horas ou já atrasaram?",
            "Quais protocolos reabertos ou com diligência respondida precisam de equipe?",
        ),
    ),
)

_TERMOS_PROIBIDOS_ESCOPO_UNIDADE: Final[tuple[str, ...]] = (
    "secretarias",
    "qual secretaria",
    "entre secretarias",
    "no município",
    "no municipio",
    "concentram mais atrasos",
    "escalonamento para a controladoria",
)


def _normalizar_rota(rota: str | None) -> str:
    if not rota:
        return ""
    caminho = rota.strip().lower().split("?", 1)[0].split("#", 1)[0]
    if not caminho.startswith("/"):
        caminho = f"/{caminho}"
    return caminho.rstrip("/") or caminho


def _fragmento_valido(frag: str) -> bool:
    return frag.lower() in FRAGMENTOS_ROTA_PERMITIDOS


def _casa_rota_contexto(
    caminho: str,
    fragmentos: tuple[str, ...],
    rotas_canonicas: tuple[str, ...],
) -> bool:
    for canon in rotas_canonicas:
        base = canon.rstrip("/")
        if caminho == base or caminho.startswith(f"{base}/"):
            return True
    return any(frag in caminho and _fragmento_valido(frag) for frag in fragmentos)


def _buscar_sugestoes_por_rota(perspectiva: str, rota: str | None) -> tuple[str, str] | None:
    caminho = _normalizar_rota(rota)
    if not caminho:
        return None

    tabela = (
        SUGESTOES_COPILOTO_POR_ROTA_UNIDADE
        if perspectiva == "unidade"
        else SUGESTOES_COPILOTO_POR_ROTA_MUNICIPAL
    )
    for fragmentos, rotas_canonicas, sugestoes in tabela:
        if _casa_rota_contexto(caminho, fragmentos, rotas_canonicas):
            return sugestoes
    return None


def _sugestao_permitida_escopo_unidade(texto: str) -> bool:
    low = (texto or "").strip().lower()
    return bool(low) and not any(termo in low for termo in _TERMOS_PROIBIDOS_ESCOPO_UNIDADE)


def _preencher_limite(resultado: list[str], fonte: tuple[str, ...], limite: int) -> list[str]:
    vistas = {s.strip().lower() for s in resultado}
    for item in fonte:
        chave = item.strip().lower()
        if chave and chave not in vistas:
            vistas.add(chave)
            resultado.append(item)
        if len(resultado) >= limite:
            break
    return resultado


def obter_sugestoes_iniciais_copiloto(
    perspectiva: str,
    rota: str | None = None,
    limite: int = 3,
) -> list[str]:
    """
    Retorna até 3 perguntas prontas adaptadas à perspectiva (controladoria, ouvidoria, unidade)
    e à rota ativa do Backoffice, preservando isolamento de escopo para perfis setoriais.
    """
    perspectiva_valida = (
        perspectiva if perspectiva in SUGESTOES_COPILOTO_POR_PERFIL else "unidade"
    )
    base_perfil = SUGESTOES_COPILOTO_POR_PERFIL[perspectiva_valida]
    contextuais = _buscar_sugestoes_por_rota(perspectiva_valida, rota)

    candidatas: list[str] = []
    if contextuais:
        candidatas.extend(contextuais)
    candidatas.extend(base_perfil)

    resultado: list[str] = []
    vistas: set[str] = set()
    for item in candidatas:
        if perspectiva_valida == "unidade" and not _sugestao_permitida_escopo_unidade(item):
            continue
        chave = item.strip().lower()
        if chave and chave not in vistas:
            vistas.add(chave)
            resultado.append(item)
        if len(resultado) >= limite:
            break

    if len(resultado) < limite and perspectiva_valida == "unidade":
        resultado = _preencher_limite(
            resultado,
            tuple(x for x in base_perfil if _sugestao_permitida_escopo_unidade(x)),
            limite,
        )

    return resultado[:limite]