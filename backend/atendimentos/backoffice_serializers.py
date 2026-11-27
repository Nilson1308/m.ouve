"""Serializers da API de backoffice (mesa de trabalho / scatter-gather)."""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from atendimentos.models import (
    AnexoOrdemServico,
    MensagemChat,
    OrdemServico,
    Protocolo,
    ProtocoloHistorico,
    SessaoChat,
)
from atendimentos.campo_exibicao import dados_coletados_para_exibicao
from catalogo.models import ServicoCatalogo, UnidadeAdministrativa
from atendimentos.urgencia_constants import normalizar_nivel
from core_auth.rbac import usuario_pode_alterar_urgencia
from ouvia_core.url_utils import public_absolute_uri

_DADOS_RESUMO_KEYS = (
    "urgencia",
    "prioridade",
    "categoria_problema",
    "tema",
    "tipo_manifestacao",
    "bairro",
)


def resumir_dados_dinamicos(dados: dict | None) -> dict:
    if not dados:
        return {}
    return {k: dados[k] for k in _DADOS_RESUMO_KEYS if k in dados}


def extrair_urgencia(protocolo_or_dados) -> str:
    if isinstance(protocolo_or_dados, Protocolo):
        if protocolo_or_dados.urgencia:
            return normalizar_nivel(protocolo_or_dados.urgencia)
        return extrair_urgencia(protocolo_or_dados.dados_dinamicos)
    dados = protocolo_or_dados
    if not dados:
        return "normal"
    for key in ("urgencia", "prioridade", "urgencia_estimada"):
        val = dados.get(key)
        if val:
            return normalizar_nivel(str(val))
    return "normal"


def calcular_sla(protocolo: Protocolo) -> dict:
    sla_horas = protocolo.servico.sla_horas if protocolo.servico_id else 72
    if protocolo.prazo_sla:
        prazo = protocolo.prazo_sla
    else:
        prazo = protocolo.data_criacao + timedelta(hours=sla_horas)
    agora = timezone.now()
    delta_horas = (prazo - agora).total_seconds() / 3600
    return {
        "sla_horas": sla_horas,
        "prazo_em": prazo.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vencido": agora > prazo,
        "horas_restantes": round(delta_horas, 1),
    }


class UnidadeAdministrativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeAdministrativa
        fields = ("id", "nome", "sigla", "ativo")


class BackofficeServicoResumoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)
    categoria_slug = serializers.CharField(source="categoria.slug", read_only=True)

    class Meta:
        model = ServicoCatalogo
        fields = (
            "id",
            "nome",
            "sla_horas",
            "categoria_nome",
            "categoria_slug",
            "fluxo_tramitacao",
        )


class BackofficeAnexoOrdemServicoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = AnexoOrdemServico
        fields = (
            "id",
            "url",
            "tipo_mime",
            "nome_original",
            "tipo_evidencia",
            "criado_em",
        )

    def get_url(self, obj):
        request = self.context.get("request")
        return public_absolute_uri(
            request, obj.arquivo.url if obj.arquivo else None
        )


class BackofficeOrdemServicoSerializer(serializers.ModelSerializer):
    unidade = UnidadeAdministrativaSerializer(read_only=True)
    unidade_id = serializers.UUIDField(source="unidade.id", read_only=True)
    exigir_validacao_ouvidoria = serializers.SerializerMethodField()
    encerramento_direto_secretaria = serializers.SerializerMethodField()
    super_os_id = serializers.UUIDField(read_only=True, allow_null=True)
    super_os_codigo = serializers.CharField(
        source="super_os.codigo", read_only=True, allow_null=True
    )
    is_super_os = serializers.SerializerMethodField()
    qtd_chamados_vinculados = serializers.SerializerMethodField()

    class Meta:
        model = OrdemServico
        fields = (
            "id",
            "super_os_id",
            "super_os_codigo",
            "is_super_os",
            "qtd_chamados_vinculados",
            "unidade_id",
            "unidade",
            "nome_equipe",
            "descricao",
            "instrucao",
            "prazo_horas",
            "status",
            "despacho_tecnico",
            "observacoes_extras",
            "observacoes_execucao",
            "concluido_em",
            "criado_em",
            "atualizado_em",
            "exigir_validacao_ouvidoria",
            "encerramento_direto_secretaria",
        )

    def _governanca_protocolo(self, obj):
        protocolo = obj.protocolo
        if not protocolo or not getattr(protocolo, "servico_id", None):
            return {"exigir_validacao_ouvidoria": True, "encerramento_direto_secretaria": False}
        from atendimentos.services.fluxo_governanca_service import (
            metadados_governanca_protocolo,
        )

        return metadados_governanca_protocolo(protocolo)

    def get_exigir_validacao_ouvidoria(self, obj):
        return self._governanca_protocolo(obj)["exigir_validacao_ouvidoria"]

    def get_encerramento_direto_secretaria(self, obj):
        return self._governanca_protocolo(obj)["encerramento_direto_secretaria"]

    instrucao = serializers.CharField(source="descricao", read_only=True)
    concluido_em = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", allow_null=True
    )
    criado_em = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    atualizado_em = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    def get_is_super_os(self, obj):
        return bool(obj.super_os_id)

    def get_qtd_chamados_vinculados(self, obj):
        if not obj.super_os_id:
            return 1
        anotado = getattr(obj, "super_os_qtd_filhos", None)
        if anotado:
            return int(anotado)
        if getattr(obj, "super_os", None):
            return obj.super_os.protocolos_filhos.count()
        return 1


class BackofficeOrdemServicoDetalheSerializer(BackofficeOrdemServicoSerializer):
    anexos = BackofficeAnexoOrdemServicoSerializer(many=True, read_only=True)
    fotos_execucao = serializers.SerializerMethodField()
    prazo_em = serializers.SerializerMethodField()

    class Meta(BackofficeOrdemServicoSerializer.Meta):
        fields = BackofficeOrdemServicoSerializer.Meta.fields + (
            "anexos",
            "fotos_execucao",
            "prazo_em",
        )

    def get_prazo_em(self, obj):
        if not obj.prazo_horas:
            return None
        prazo = obj.criado_em + timedelta(hours=obj.prazo_horas)
        return prazo.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_fotos_execucao(self, obj):
        request = self.context.get("request")
        fotos = []
        for anexo in obj.anexos.all().order_by("criado_em"):
            url = public_absolute_uri(
                request, anexo.arquivo.url if anexo.arquivo else None
            )
            if not url:
                continue
            legenda_map = dict(AnexoOrdemServico.TipoEvidencia.choices)
            fotos.append(
                {
                    "id": str(anexo.id),
                    "url": url,
                    "legenda": legenda_map.get(anexo.tipo_evidencia, anexo.tipo_evidencia),
                    "tipo_evidencia": anexo.tipo_evidencia,
                    "timestamp": anexo.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
        return fotos


class BackofficeProtocoloKanbanSerializer(serializers.ModelSerializer):
    servico = BackofficeServicoResumoSerializer(read_only=True)
    dados_dinamicos = serializers.SerializerMethodField()
    sla = serializers.SerializerMethodField()
    urgencia_sugerida_ia = serializers.CharField(read_only=True)
    urgencia_motivo_ia = serializers.CharField(read_only=True)
    urgencia_confianca_ia = serializers.FloatField(read_only=True, allow_null=True)
    urgencia_sugestao_status = serializers.CharField(read_only=True)
    urgencia_origem = serializers.CharField(read_only=True)
    urgencia_peso = serializers.IntegerField(read_only=True)
    urgencia_travada_manualmente = serializers.BooleanField(read_only=True)
    pode_alterar_urgencia = serializers.SerializerMethodField()
    urgencia_reduz_sla_ativo = serializers.SerializerMethodField()
    cidadao = serializers.SerializerMethodField()
    endereco = serializers.CharField(source="endereco_texto", read_only=True)
    tem_anexos = serializers.SerializerMethodField()
    tem_localizacao = serializers.SerializerMethodField()
    localizacao = serializers.SerializerMethodField()
    super_os_id = serializers.SerializerMethodField()
    super_os_codigo = serializers.SerializerMethodField()
    ordens_servico = BackofficeOrdemServicoSerializer(many=True, read_only=True)
    data_criacao = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    data_atualizacao = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    triagem_sugerida = serializers.JSONField(read_only=True)
    equipamento = serializers.SerializerMethodField()
    qtd_cobrancas_cidadao = serializers.IntegerField(read_only=True)
    ultima_cobranca_em = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True, allow_null=True
    )
    ultimo_alerta_sla_nivel = serializers.CharField(read_only=True)
    dias_atraso = serializers.SerializerMethodField()
    exigir_validacao_ouvidoria = serializers.SerializerMethodField()
    encerramento_direto_secretaria = serializers.SerializerMethodField()
    equipamento_citado_nao_catalogado = serializers.CharField(read_only=True)
    requer_curadoria_equipamento = serializers.SerializerMethodField()

    class Meta:
        model = Protocolo
        fields = (
            "id",
            "codigo",
            "status",
            "descricao",
            "data_criacao",
            "data_atualizacao",
            "servico",
            "dados_dinamicos",
            "sla",
            "urgencia",
            "urgencia_peso",
            "urgencia_origem",
            "urgencia_sugerida_ia",
            "urgencia_motivo_ia",
            "urgencia_confianca_ia",
            "urgencia_sugestao_status",
            "urgencia_travada_manualmente",
            "pode_alterar_urgencia",
            "urgencia_reduz_sla_ativo",
            "cidadao",
            "endereco",
            "tem_anexos",
            "tem_localizacao",
            "localizacao",
            "super_os_id",
            "super_os_codigo",
            "ordens_servico",
            "triagem_sugerida",
            "equipamento",
            "qtd_cobrancas_cidadao",
            "ultima_cobranca_em",
            "ultimo_alerta_sla_nivel",
            "dias_atraso",
            "exigir_validacao_ouvidoria",
            "encerramento_direto_secretaria",
            "equipamento_citado_nao_catalogado",
            "requer_curadoria_equipamento",
        )

    def get_requer_curadoria_equipamento(self, obj) -> bool:
        return bool((obj.equipamento_citado_nao_catalogado or "").strip())

    def get_exigir_validacao_ouvidoria(self, obj):
        from atendimentos.services.fluxo_governanca_service import (
            metadados_governanca_protocolo,
        )

        return metadados_governanca_protocolo(obj)["exigir_validacao_ouvidoria"]

    def get_encerramento_direto_secretaria(self, obj):
        from atendimentos.services.fluxo_governanca_service import (
            metadados_governanca_protocolo,
        )

        return metadados_governanca_protocolo(obj)["encerramento_direto_secretaria"]

    def get_dias_atraso(self, obj):
        from atendimentos.services.sla_cobranca_service import dias_atraso

        return dias_atraso(obj)

    def get_equipamento(self, obj):
        eq = getattr(obj, "equipamento", None)
        if not eq:
            return None
        return {
            "id": str(eq.id),
            "nome": eq.nome,
            "tipo": eq.tipo,
            "bairro": eq.bairro or "",
        }

    def get_dados_dinamicos(self, obj):
        return resumir_dados_dinamicos(obj.dados_dinamicos)

    def get_sla(self, obj):
        return calcular_sla(obj)

    def get_pode_alterar_urgencia(self, obj):
        request = self.context.get("request")
        if not request or not request.user:
            return False
        return usuario_pode_alterar_urgencia(request.user)

    def get_urgencia_reduz_sla_ativo(self, obj):
        from atendimentos.models import ConfiguracaoMatrizUrgencia

        return ConfiguracaoMatrizUrgencia.load().urgencia_reduz_sla

    def get_cidadao(self, obj):
        u = obj.usuario
        return {
            "id": str(u.id),
            "nome": u.nome,
            "telefone": u.telefone or "",
        }

    def get_tem_anexos(self, obj):
        if hasattr(obj, "_tem_anexos"):
            return obj._tem_anexos
        return obj.anexos.exists()

    def get_tem_localizacao(self, obj):
        return bool(obj.localizacao or obj.endereco_texto)

    def get_localizacao(self, obj):
        payload = {"endereco": obj.endereco_texto or ""}
        if obj.localizacao:
            payload["latitude"] = obj.localizacao.y
            payload["longitude"] = obj.localizacao.x
        else:
            payload["latitude"] = None
            payload["longitude"] = None
        return payload

    def get_super_os_id(self, obj):
        return str(obj.super_os_id) if obj.super_os_id else None

    def get_super_os_codigo(self, obj):
        if obj.super_os_id and obj.super_os:
            return obj.super_os.codigo
        return None


class OrdemDespachoItemSerializer(serializers.Serializer):
    unidade_id = serializers.UUIDField()
    instrucao = serializers.CharField()
    prazo_horas = serializers.IntegerField(min_value=1, max_value=24 * 365)


class DespacharProtocoloSerializer(serializers.Serializer):
    ordens = OrdemDespachoItemSerializer(many=True, min_length=1)
    observacao_geral = serializers.CharField(required=False, allow_blank=True, default="")


def mesclar_dados_coletados(protocolo: Protocolo) -> dict:
    dados = {k: v for k, v in (protocolo.dados_dinamicos or {}).items()}
    sessao = getattr(protocolo, "sessao_chat", None)
    if sessao and sessao.dados_coletados:
        for chave, valor in sessao.dados_coletados.items():
            if str(chave).startswith("_"):
                continue
            if chave not in dados:
                dados[chave] = valor
    return dados


def formatar_historico_chat(sessao: SessaoChat | None, request) -> list[dict]:
    if not sessao:
        return []
    mensagens = (
        MensagemChat.objects.filter(sessao=sessao)
        .prefetch_related("anexos")
        .order_by("criado_em")
    )
    itens = []
    for msg in mensagens:
        tipo = msg.autor
        if tipo == MensagemChat.Autor.IA:
            tipo = "bot"
        anexo = None
        for an in msg.anexos.all().order_by("criado_em"):
            if not (an.tipo_mime or "").startswith("image/"):
                continue
            url = public_absolute_uri(request, an.arquivo.url if an.arquivo else None)
            if url:
                anexo = {
                    "tipo": "imagem",
                    "url": url,
                    "nome": an.nome_original or "anexo.jpg",
                }
                break
        itens.append(
            {
                "id": str(msg.id),
                "tipo": tipo,
                "mensagem": msg.conteudo_texto,
                "timestamp": msg.criado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "anexo": anexo,
            }
        )
    return itens


class BackofficeProtocoloHistoricoSerializer(serializers.ModelSerializer):
    registrado_em = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = ProtocoloHistorico
        fields = ("id", "status", "descricao", "equipe_nome", "registrado_em")


class BackofficeProtocoloDetalheSerializer(BackofficeProtocoloKanbanSerializer):
    dados_coletados = serializers.SerializerMethodField()
    historico_chat = serializers.SerializerMethodField()
    historico_protocolo = BackofficeProtocoloHistoricoSerializer(
        source="historico", many=True, read_only=True
    )
    ordens_servico = BackofficeOrdemServicoDetalheSerializer(many=True, read_only=True)
    resposta_cidadao = serializers.CharField(read_only=True)
    observacoes_internas = serializers.CharField(read_only=True)
    localizacao = serializers.SerializerMethodField()
    diligencia_ativa = serializers.SerializerMethodField()
    diligencias = serializers.SerializerMethodField()
    sla_pausado = serializers.SerializerMethodField()
    tempo_sla_pausado_segundos = serializers.SerializerMethodField()
    pode_abrir_diligencia = serializers.SerializerMethodField()
    motivo_bloqueio_diligencia = serializers.SerializerMethodField()
    qtd_reaberturas = serializers.IntegerField(read_only=True)
    ultima_reabertura_em = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True, allow_null=True
    )
    reabertura_ate = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True, allow_null=True
    )
    reaberto = serializers.SerializerMethodField()
    reaberturas = serializers.SerializerMethodField()

    class Meta(BackofficeProtocoloKanbanSerializer.Meta):
        fields = BackofficeProtocoloKanbanSerializer.Meta.fields + (
            "dados_coletados",
            "historico_chat",
            "historico_protocolo",
            "resposta_cidadao",
            "observacoes_internas",
            "localizacao",
            "diligencia_ativa",
            "diligencias",
            "sla_pausado",
            "tempo_sla_pausado_segundos",
            "pode_abrir_diligencia",
            "motivo_bloqueio_diligencia",
            "qtd_reaberturas",
            "ultima_reabertura_em",
            "reabertura_ate",
            "reaberto",
            "reaberturas",
        )

    def _campos_diligencia(self, obj):
        cached = getattr(obj, "_cache_campos_diligencia", None)
        if cached is None:
            from atendimentos.services.diligencia_service import campos_diligencia_backoffice

            request = self.context.get("request")
            user = getattr(request, "user", None) if request else None
            cached = campos_diligencia_backoffice(obj, request=request, user=user)
            obj._cache_campos_diligencia = cached
        return cached

    def get_diligencia_ativa(self, obj):
        return self._campos_diligencia(obj).get("diligencia_ativa")

    def get_diligencias(self, obj):
        return self._campos_diligencia(obj).get("diligencias")

    def get_sla_pausado(self, obj):
        return self._campos_diligencia(obj).get("sla_pausado")

    def get_tempo_sla_pausado_segundos(self, obj):
        return self._campos_diligencia(obj).get("tempo_sla_pausado_segundos")

    def get_pode_abrir_diligencia(self, obj):
        return self._campos_diligencia(obj).get("pode_abrir_diligencia")

    def get_motivo_bloqueio_diligencia(self, obj):
        return self._campos_diligencia(obj).get("motivo_bloqueio_diligencia")

    def _campos_reabertura(self, obj):
        cached = getattr(obj, "_cache_campos_reabertura", None)
        if cached is None:
            from atendimentos.services.reabertura_service import campos_reabertura_backoffice

            request = self.context.get("request")
            cached = campos_reabertura_backoffice(obj, request=request)
            obj._cache_campos_reabertura = cached
        return cached

    def get_reaberto(self, obj):
        return self._campos_reabertura(obj).get("reaberto", False)

    def get_reaberturas(self, obj):
        return self._campos_reabertura(obj).get("reaberturas", [])

    def get_dados_coletados(self, obj):
        brutos = mesclar_dados_coletados(obj)
        servico = obj.servico if obj.servico_id else None
        return dados_coletados_para_exibicao(servico, brutos)

    def get_historico_chat(self, obj):
        request = self.context.get("request")
        sessao = getattr(obj, "sessao_chat", None)
        return formatar_historico_chat(sessao, request)

    def get_localizacao(self, obj):
        payload = {"endereco": obj.endereco_texto or ""}
        if obj.localizacao:
            payload["latitude"] = obj.localizacao.y
            payload["longitude"] = obj.localizacao.x
        return payload


class ConcluirOrdemServicoSerializer(serializers.Serializer):
    observacoes_execucao = serializers.CharField(required=False, allow_blank=True, default="")


class ValidarProtocoloSerializer(serializers.Serializer):
    resposta_cidadao = serializers.CharField()
    observacoes_internas = serializers.CharField(required=False, allow_blank=True, default="")


class DevolverOrdemServicoSerializer(serializers.Serializer):
    motivo = serializers.CharField(max_length=120)
    justificativa = serializers.CharField()
