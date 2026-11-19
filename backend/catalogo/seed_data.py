"""Carga inicial do catálogo — espelha o mock em ``src/stores/catalogo.js``."""

import uuid

from catalogo.models import CategoriaCatalogo, ServicoCatalogo

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _id(codigo: str) -> uuid.UUID:
    """IDs estáveis para ambientes de dev e testes."""
    return uuid.uuid5(_NAMESPACE, f"ouvia.catalogo.{codigo}")


CATEGORIAS_CATALOGO_INICIAL = [
    {
        "id": _id("cat-ouvidoria"),
        "nome": "Ouvidoria",
        "slug": "ouvidoria",
        "descricao": "Manifestações, denúncias e pedidos de informação ao município.",
        "icone": "chat-bubble",
        "ordem": 10,
        "tipo_legado": CategoriaCatalogo.TipoLegado.OUVIDORIA,
        "ativo": True,
    },
    {
        "id": _id("cat-zeladoria"),
        "nome": "Zeladoria Urbana",
        "slug": "zeladoria_urbana",
        "descricao": "Problemas em vias, iluminação, limpeza e acessibilidade no espaço público.",
        "icone": "building-office",
        "ordem": 20,
        "tipo_legado": CategoriaCatalogo.TipoLegado.ZELADORIA,
        "ativo": True,
    },
]


SERVICOS_CATALOGO_INICIAL = [
    {
        "id": _id("ouv-001"),
        "nome": "Denúncia",
        "descricao": "Relatar irregularidades, corrupção ou má conduta de servidores públicos",
        "categoria_slug": "ouvidoria",
        "sla_horas": 72,
        "ativo": True,
        "schema_formulario": {
            "type": "object",
            "properties": {
                "tipo_manifestacao": {
                    "type": "string",
                    "title": "Tipo de Manifestação",
                    "enum": ["denuncia", "reclamacao", "sugestao", "elogio"],
                    "enumNames": ["Denúncia", "Reclamação", "Sugestão", "Elogio"],
                },
                "categoria": {
                    "type": "string",
                    "title": "Categoria",
                    "enum": [
                        "saude",
                        "educacao",
                        "transporte",
                        "seguranca",
                        "assistencia_social",
                        "meio_ambiente",
                        "outros",
                    ],
                    "enumNames": [
                        "Saúde",
                        "Educação",
                        "Transporte",
                        "Segurança",
                        "Assistência Social",
                        "Meio Ambiente",
                        "Outros",
                    ],
                },
                "descricao_detalhada": {
                    "type": "string",
                    "title": "Descrição Detalhada",
                    "format": "textarea",
                    "minLength": 20,
                },
                "anonimo": {
                    "type": "boolean",
                    "title": "Manifestação anônima",
                    "default": False,
                },
            },
            "required": ["tipo_manifestacao", "categoria", "descricao_detalhada"],
            "$metadata": {"exige_localizacao": False},
        },
    },
    {
        "id": _id("ouv-002"),
        "nome": "Solicitação de Informação",
        "descricao": "Solicitar informações sobre serviços públicos, processos e documentos",
        "categoria_slug": "ouvidoria",
        "sla_horas": 48,
        "ativo": True,
        "schema_formulario": {
            "type": "object",
            "properties": {
                "assunto": {
                    "type": "string",
                    "title": "Assunto da Solicitação",
                    "enum": ["processos", "documentos", "servicos", "legislacao", "outros"],
                    "enumNames": [
                        "Processos Administrativos",
                        "Documentos",
                        "Serviços Públicos",
                        "Legislação",
                        "Outros",
                    ],
                },
                "informacao_solicitada": {
                    "type": "string",
                    "title": "Informação Solicitada",
                    "format": "textarea",
                },
                "prazo_desejado": {
                    "type": "string",
                    "title": "Prazo Desejado",
                    "enum": ["urgente", "normal", "sem_pressa"],
                    "enumNames": [
                        "Urgente (até 3 dias)",
                        "Normal (até 7 dias)",
                        "Sem pressa (até 15 dias)",
                    ],
                },
            },
            "required": ["assunto", "informacao_solicitada"],
            "$metadata": {"exige_localizacao": False},
        },
    },
    {
        "id": _id("zel-001"),
        "nome": "Buracos e Pavimentação",
        "descricao": "Reportar buracos, rachaduras e problemas no asfalto das vias públicas",
        "categoria_slug": "zeladoria_urbana",
        "sla_horas": 48,
        "ativo": True,
        "schema_formulario": {
            "type": "object",
            "properties": {
                "tipo_problema": {
                    "type": "array",
                    "title": "Tipo de Problema",
                    "minItems": 1,
                    "uniqueItems": True,
                    "x-ouvia-selection": "multi",
                    "x-ouvia-allow-other": True,
                    "items": {
                        "type": "string",
                        "enum": ["buraco", "rachadura", "afundamento", "desgaste", "outro"],
                        "enumNames": [
                            "Buraco",
                            "Rachadura",
                            "Afundamento",
                            "Desgaste Geral",
                            "Outro (descrever)",
                        ],
                    },
                },
                "tamanho_aproximado": {
                    "type": "string",
                    "title": "Tamanho Aproximado",
                    "enum": ["pequeno", "medio", "grande"],
                    "enumNames": ["Pequeno (até 50cm)", "Médio (50cm a 1m)", "Grande (mais de 1m)"],
                },
                "causa_risco": {
                    "type": "boolean",
                    "title": "Causa risco imediato aos pedestres ou veículos",
                    "default": False,
                },
                "observacoes": {
                    "type": "string",
                    "title": "Observações Adicionais",
                    "format": "textarea",
                },
            },
            "required": ["tipo_problema", "tamanho_aproximado"],
            "$metadata": {"exige_localizacao": True},
        },
    },
    {
        "id": _id("zel-002"),
        "nome": "Iluminação Pública",
        "descricao": "Reportar postes queimados, lâmpadas apagadas ou problemas na iluminação",
        "categoria_slug": "zeladoria_urbana",
        "sla_horas": 24,
        "ativo": True,
        "schema_formulario": {
            "type": "object",
            "properties": {
                "tipo_problema": {
                    "type": "string",
                    "title": "Tipo de Problema",
                    "enum": [
                        "lampada_queimada",
                        "lampada_acesa_dia",
                        "poste_danificado",
                        "fiacao_exposta",
                        "outro",
                    ],
                    "enumNames": [
                        "Lâmpada Queimada",
                        "Lâmpada Acesa Durante o Dia",
                        "Poste Danificado",
                        "Fiação Exposta",
                        "Outro",
                    ],
                },
                "numero_poste": {
                    "type": "string",
                    "title": "Número do Poste (se visível)",
                    "pattern": "^[A-Z0-9-]*$",
                },
                "quantidade_postes": {
                    "type": "integer",
                    "title": "Quantidade de Postes Afetados",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 1,
                },
                "observacoes": {
                    "type": "string",
                    "title": "Observações",
                    "format": "textarea",
                },
            },
            "required": ["tipo_problema"],
            "$metadata": {"exige_localizacao": True},
        },
    },
    {
        "id": _id("zel-003"),
        "nome": "Limpeza Urbana",
        "descricao": "Reportar acúmulo de lixo, entulho ou problemas com coleta",
        "categoria_slug": "zeladoria_urbana",
        "sla_horas": 48,
        "ativo": True,
        "schema_formulario": {
            "type": "object",
            "properties": {
                "tipo_problema": {
                    "type": "array",
                    "title": "Tipo de Problema",
                    "minItems": 1,
                    "uniqueItems": True,
                    "x-ouvia-selection": "multi",
                    "x-ouvia-allow-other": True,
                    "items": {
                        "type": "string",
                        "enum": [
                            "acumulo_lixo",
                            "entulho",
                            "coleta_nao_realizada",
                            "lixeira_danificada",
                            "outro",
                        ],
                        "enumNames": [
                            "Acúmulo de Lixo",
                            "Entulho",
                            "Coleta Não Realizada",
                            "Lixeira Danificada",
                            "Outro (descrever)",
                        ],
                    },
                },
                "volume_estimado": {
                    "type": "string",
                    "title": "Volume Estimado",
                    "x-ouvia-selection": "single",
                    "enum": ["pequeno", "medio", "grande"],
                    "enumNames": [
                        "Pequeno (alguns sacos)",
                        "Médio (vários sacos ou móveis)",
                        "Grande (caminhão completo)",
                    ],
                },
                "ha_mau_cheiro": {
                    "type": "boolean",
                    "title": "Há mau cheiro ou risco à saúde",
                    "default": False,
                },
                "observacoes": {
                    "type": "string",
                    "title": "Observações",
                    "format": "textarea",
                },
            },
            "required": ["tipo_problema", "volume_estimado"],
            "$metadata": {"exige_localizacao": True},
        },
    },
    {
        "id": _id("zel-004"),
        "nome": "Calçadas e Acessibilidade",
        "descricao": "Reportar problemas em calçadas, rampas de acesso e mobiliário urbano",
        "categoria_slug": "zeladoria_urbana",
        "sla_horas": 72,
        "ativo": True,
        "schema_formulario": {
            "type": "object",
            "properties": {
                "tipo_problema": {
                    "type": "string",
                    "title": "Tipo de Problema",
                    "enum": [
                        "calcada_irregular",
                        "rampa_ausente",
                        "rampa_danificada",
                        "obstrucao",
                        "outro",
                    ],
                    "enumNames": [
                        "Calçada Irregular",
                        "Rampa de Acesso Ausente",
                        "Rampa Danificada",
                        "Obstrução da Passagem",
                        "Outro",
                    ],
                },
                "impede_acessibilidade": {
                    "type": "boolean",
                    "title": "Impede a acessibilidade de pessoas com deficiência ou mobilidade reduzida",
                    "default": False,
                },
                "descricao_problema": {
                    "type": "string",
                    "title": "Descrição do Problema",
                    "format": "textarea",
                },
            },
            "required": ["tipo_problema", "descricao_problema"],
            "$metadata": {"exige_localizacao": True},
        },
    },
]


def popular_categorias_inicial() -> dict[str, CategoriaCatalogo]:
    """Garante categorias base e retorna mapa slug → instância."""
    por_slug: dict[str, CategoriaCatalogo] = {}
    for dados in CATEGORIAS_CATALOGO_INICIAL:
        slug = dados["slug"]
        fields = {k: v for k, v in dados.items() if k not in ("id", "slug")}
        obj, created = CategoriaCatalogo.objects.update_or_create(slug=slug, defaults=fields)
        if created:
            obj.id = dados["id"]
            obj.save(update_fields=["id"])
        por_slug[obj.slug] = obj
    return por_slug


def popular_catalogo_inicial(*, limpar: bool = True) -> int:
    """
    Recria o catálogo base (categorias + 6 serviços).

    ``limpar=True`` remove serviços antes (falha se houver protocolos vinculados).
    """
    if limpar:
        ServicoCatalogo.objects.all().delete()

    categorias = popular_categorias_inicial()

    for dados in SERVICOS_CATALOGO_INICIAL:
        pk = dados["id"]
        slug = dados["categoria_slug"]
        categoria = categorias.get(slug)
        if not categoria:
            categoria = CategoriaCatalogo.objects.filter(slug=slug).first()
        if not categoria:
            raise ValueError(f"Categoria ausente para slug={slug!r}")

        defaults = {
            k: v
            for k, v in dados.items()
            if k not in ("id", "categoria_slug")
        }
        defaults["categoria"] = categoria
        ServicoCatalogo.objects.update_or_create(id=pk, defaults=defaults)

    return len(SERVICOS_CATALOGO_INICIAL)
