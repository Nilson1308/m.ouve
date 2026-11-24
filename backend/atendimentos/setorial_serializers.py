"""Serializers do painel setorial e link mágico."""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from atendimentos.magic_link_services import magic_link_payload
from atendimentos.models import AnexoOrdemServico, OrdemServico
from ouvia_core.url_utils import public_absolute_uri


def mascarar_cpf(cpf: str | None) -> str:
    if not cpf:
        return "***.***.***-**"
    digitos = "".join(c for c in cpf if c.isdigit())
    if len(digitos) < 2:
        return "***.***.***-**"
    return f"***.***.***-{digitos[-2:]}"


def status_setorial_ui(status: str) -> str:
    mapa = {
        OrdemServico.Status.PENDENTE: "nova",
        OrdemServico.Status.EM_ANDAMENTO: "aguardando_campo",
        OrdemServico.Status.AGUARDANDO_FORMALIZACAO: "aguardando_campo",
        OrdemServico.Status.AGUARDANDO_ASSINATURA: "aguardando_assinatura",
        OrdemServico.Status.CONCLUIDA: "concluida",
        OrdemServico.Status.CANCELADA: "cancelada",
    }
    return mapa.get(status, status)


def calcular_sla_os(ordem: OrdemServico) -> str:
    if not ordem.prazo_horas:
        return "normal"
    prazo = ordem.criado_em + timedelta(hours=ordem.prazo_horas)
    agora = timezone.now()
    if agora > prazo:
        return "vencido"
    horas = (prazo - agora).total_seconds() / 3600
    if horas <= 24:
        return "atencao"
    return "normal"


class SetorialEvidenciaSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    legenda = serializers.SerializerMethodField()
    enviado_em = serializers.DateTimeField(source="criado_em", format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = AnexoOrdemServico
        fields = (
            "id",
            "tipo",
            "url",
            "legenda",
            "enviado_em",
            "tipo_evidencia",
            "nome_original",
        )

    def get_tipo(self, obj):
        mime = obj.tipo_mime or ""
        return "foto" if mime.startswith("image/") else "arquivo"

    def get_url(self, obj):
        request = self.context.get("request")
        return public_absolute_uri(request, obj.arquivo.url if obj.arquivo else None)

    def get_legenda(self, obj):
        mapa = dict(AnexoOrdemServico.TipoEvidencia.choices)
        return mapa.get(obj.tipo_evidencia, obj.nome_original or "Evidência")


class SetorialOrdemServicoResumoSerializer(serializers.ModelSerializer):
    unidade_nome = serializers.CharField(source="unidade.nome", read_only=True)
    unidade_sigla = serializers.CharField(source="unidade.sigla", read_only=True)
    protocolo_id = serializers.SerializerMethodField()
    protocolo_uuid = serializers.UUIDField(source="protocolo_id", read_only=True)
    servico = serializers.CharField(source="protocolo.servico.nome", read_only=True)
    descricao = serializers.SerializerMethodField()
    endereco = serializers.CharField(source="protocolo.endereco_texto", read_only=True)
    coordenadas = serializers.SerializerMethodField()
    prioridade = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_api = serializers.CharField(source="status", read_only=True)
    sla_status = serializers.SerializerMethodField()
    prazo_interno = serializers.SerializerMethodField()
    cidadao = serializers.SerializerMethodField()
    instrucao_ouvidoria = serializers.CharField(source="descricao", read_only=True)
    magic_link = serializers.SerializerMethodField()
    evidencias = SetorialEvidenciaSerializer(source="anexos", many=True, read_only=True)
    criado_em = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    concluida_em = serializers.DateTimeField(
        source="concluido_em", format="%Y-%m-%dT%H:%M:%SZ", allow_null=True
    )
    despachado_em = serializers.DateTimeField(
        source="magic_link_gerado_em", format="%Y-%m-%dT%H:%M:%SZ", allow_null=True
    )
    assinado_por = serializers.SerializerMethodField()
    assinado_em = serializers.DateTimeField(
        source="concluido_em", format="%Y-%m-%dT%H:%M:%SZ", allow_null=True
    )
    data_formalizacao = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", allow_null=True, read_only=True
    )
    assinatura_digital_hash = serializers.CharField(read_only=True)
    is_super_os = serializers.SerializerMethodField()
    qtd_chamados_vinculados = serializers.SerializerMethodField()
    super_os_codigo = serializers.SerializerMethodField()
    protocolo_codigo = serializers.SerializerMethodField()
    exigir_validacao_ouvidoria = serializers.SerializerMethodField()
    encerramento_direto_secretaria = serializers.SerializerMethodField()
    aguardando_cidadao = serializers.SerializerMethodField()
    sla_pausado = serializers.SerializerMethodField()
    qtd_diligencias_respondidas = serializers.SerializerMethodField()
    ultima_diligencia_respondida_em = serializers.SerializerMethodField()
    qtd_anexos_diligencias = serializers.SerializerMethodField()

    class Meta:
        model = OrdemServico
        fields = (
            "id",
            "unidade_nome",
            "unidade_sigla",
            "protocolo_id",
            "protocolo_uuid",
            "servico",
            "descricao",
            "endereco",
            "coordenadas",
            "prioridade",
            "status",
            "status_api",
            "sla_status",
            "prazo_interno",
            "criado_em",
            "despachado_em",
            "concluida_em",
            "cidadao",
            "instrucao_ouvidoria",
            "despacho_tecnico",
            "observacoes_extras",
            "observacoes_execucao",
            "magic_link",
            "evidencias",
            "assinado_por",
            "assinado_em",
            "data_formalizacao",
            "assinatura_digital_hash",
            "is_super_os",
            "qtd_chamados_vinculados",
            "super_os_codigo",
            "protocolo_codigo",
            "exigir_validacao_ouvidoria",
            "encerramento_direto_secretaria",
            "aguardando_cidadao",
            "sla_pausado",
            "qtd_diligencias_respondidas",
            "ultima_diligencia_respondida_em",
            "qtd_anexos_diligencias",
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

    def get_is_super_os(self, obj):
        return bool(obj.super_os_id)

    def get_qtd_chamados_vinculados(self, obj):
        if not obj.super_os_id:
            return 1
        anotado = getattr(obj, "super_os_qtd_filhos", None)
        if anotado:
            return int(anotado)
        if obj.super_os_id and obj.super_os:
            return obj.super_os.protocolos_filhos.count()
        return 1

    def get_super_os_codigo(self, obj):
        if obj.super_os_id and obj.super_os:
            return obj.super_os.codigo
        return None

    def get_protocolo_codigo(self, obj):
        return obj.protocolo.codigo if obj.protocolo_id else None

    def get_protocolo_id(self, obj):
        if obj.super_os_id:
            return f"{obj.super_os.codigo} · ref. {obj.protocolo.codigo}"
        return obj.protocolo.codigo

    def get_descricao(self, obj):
        if obj.super_os_id:
            titulo = obj.super_os.titulo_resumo
            qtd = obj.super_os.protocolos_filhos.count()
            return f"{titulo} ({qtd} protocolos)"
        servico = getattr(obj.protocolo, "servico", None)
        nome = servico.nome if servico else "Ordem de serviço"
        if obj.protocolo.endereco_texto:
            return f"{nome} — {obj.protocolo.endereco_texto}"
        return nome

    def get_coordenadas(self, obj):
        loc = obj.protocolo.localizacao
        if not loc:
            return None
        return {"lat": loc.y, "lng": loc.x}

    def get_prioridade(self, obj):
        dados = obj.protocolo.dados_dinamicos or {}
        for chave in ("urgencia", "prioridade", "urgencia_estimada"):
            val = dados.get(chave)
            if val:
                return str(val).lower()
        return "normal"

    def get_status(self, obj):
        return status_setorial_ui(obj.status)

    def get_sla_status(self, obj):
        return calcular_sla_os(obj)

    def get_prazo_interno(self, obj):
        if not obj.prazo_horas:
            return None
        prazo = obj.criado_em + timedelta(hours=obj.prazo_horas)
        return prazo.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_cidadao(self, obj):
        u = getattr(obj.protocolo, "usuario", None)
        if not u:
            return {"nome": "—", "cpf": mascarar_cpf(None)}
        return {"nome": u.nome or "—", "cpf": mascarar_cpf(u.cpf)}

    def get_magic_link(self, obj):
        return magic_link_payload(obj)

    def get_assinado_por(self, obj):
        if obj.formalizado_por_id:
            return obj.formalizado_por.nome
        return ""

    def _campos_diligencia_resumo(self, obj):
        cached = getattr(obj, "_cache_diligencia_resumo", None)
        if cached is None:
            from atendimentos.services.diligencia_service import campos_diligencia_setorial_resumo

            cached = campos_diligencia_setorial_resumo(obj.protocolo, obj)
            obj._cache_diligencia_resumo = cached
        return cached

    def get_aguardando_cidadao(self, obj):
        return self._campos_diligencia_resumo(obj).get("aguardando_cidadao", False)

    def get_sla_pausado(self, obj):
        return self._campos_diligencia_resumo(obj).get("sla_pausado", False)

    def get_qtd_diligencias_respondidas(self, obj):
        return self._campos_diligencia_resumo(obj).get("qtd_diligencias_respondidas", 0)

    def get_ultima_diligencia_respondida_em(self, obj):
        return self._campos_diligencia_resumo(obj).get("ultima_diligencia_respondida_em")

    def get_qtd_anexos_diligencias(self, obj):
        return self._campos_diligencia_resumo(obj).get("qtd_anexos_diligencias", 0)


class SetorialOrdemServicoSerializer(SetorialOrdemServicoResumoSerializer):
    """Detalhe da OS no painel setorial (drawer) — inclui histórico de diligências."""

    diligencia_ativa = serializers.SerializerMethodField()
    diligencias = serializers.SerializerMethodField()
    pode_abrir_diligencia = serializers.SerializerMethodField()
    motivo_bloqueio_diligencia = serializers.SerializerMethodField()
    tempo_sla_pausado_segundos = serializers.SerializerMethodField()

    class Meta(SetorialOrdemServicoResumoSerializer.Meta):
        fields = SetorialOrdemServicoResumoSerializer.Meta.fields + (
            "diligencia_ativa",
            "diligencias",
            "pode_abrir_diligencia",
            "motivo_bloqueio_diligencia",
            "tempo_sla_pausado_segundos",
        )

    def _campos_diligencia_detalhe(self, obj):
        cached = getattr(obj, "_cache_diligencia_detalhe", None)
        if cached is None:
            from atendimentos.services.diligencia_service import (
                campos_diligencia_setorial_detalhe,
            )

            request = self.context.get("request")
            user = getattr(request, "user", None) if request else None
            cached = campos_diligencia_setorial_detalhe(
                obj, request=request, user=user
            )
            obj._cache_diligencia_detalhe = cached
        return cached

    def get_diligencia_ativa(self, obj):
        return self._campos_diligencia_detalhe(obj).get("diligencia_ativa")

    def get_diligencias(self, obj):
        return self._campos_diligencia_detalhe(obj).get("diligencias", [])

    def get_pode_abrir_diligencia(self, obj):
        return self._campos_diligencia_detalhe(obj).get("pode_abrir_diligencia", False)

    def get_motivo_bloqueio_diligencia(self, obj):
        return self._campos_diligencia_detalhe(obj).get("motivo_bloqueio_diligencia")

    def get_tempo_sla_pausado_segundos(self, obj):
        return self._campos_diligencia_detalhe(obj).get(
            "tempo_sla_pausado_segundos", 0
        )


class GerarMagicLinkResponseSerializer(serializers.Serializer):
    magic_link = serializers.DictField()
    ordem_servico = SetorialOrdemServicoSerializer()


class FormalizarOrdemSerializer(serializers.Serializer):
    despacho_tecnico = serializers.CharField()
    observacoes_extras = serializers.CharField(required=False, allow_blank=True, default="")
    senha_assinatura = serializers.CharField(write_only=True, trim_whitespace=False)
