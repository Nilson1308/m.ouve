"""Modelos universais de protocolo e execução operacional (agnósticos ao negócio)."""

import uuid

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from pgvector.django import VectorField


class Protocolo(models.Model):
    """Registro cidadão vinculado a um serviço do catálogo."""

    class Status(models.TextChoices):
        EM_ANALISE = "em_analise", "Em análise"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        AGUARDANDO_REVISAO = "aguardando_revisao", "Aguardando revisão"
        AGUARDANDO_CIDADAO = "aguardando_cidadao", "Aguardando cidadão"
        RESOLVIDO = "resolvido", "Resolvido"
        REJEITADO = "rejeitado", "Rejeitado"

    class NotaSatisfacao(models.IntegerChoices):
        UMA = 1, "1"
        DUAS = 2, "2"
        TRES = 3, "3"
        QUATRO = 4, "4"
        CINCO = 5, "5"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="protocolos",
    )
    servico = models.ForeignKey(
        "catalogo.ServicoCatalogo",
        on_delete=models.PROTECT,
        related_name="protocolos",
    )
    dados_dinamicos = models.JSONField(default=dict, blank=True)
    descricao = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.EM_ANALISE
    )
    endereco_texto = models.CharField(max_length=500, blank=True)
    localizacao = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    embedding = VectorField(dimensions=settings.EMBEDDING_DIMENSIONS, null=True, blank=True)
    resposta_cidadao = models.TextField(
        blank=True,
        default="",
        help_text="Texto enviado ao cidadão na validação final do protocolo.",
    )
    observacoes_internas = models.TextField(
        blank=True,
        default="",
        help_text="Notas internas do gestor (não expostas ao cidadão).",
    )
    super_os = models.ForeignKey(
        "SuperOS",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="protocolos_filhos",
        help_text="Incidente mestre (Super OS) ao qual este protocolo foi agrupado.",
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    nota_satisfacao = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=NotaSatisfacao.choices,
        help_text="Nota da pesquisa de satisfação (1 a 5), preenchida na conclusão.",
    )
    comentario_satisfacao = models.TextField(
        null=True,
        blank=True,
        help_text="Comentário opcional do cidadão na pesquisa de satisfação.",
    )
    triagem_sugerida = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Sugestões estruturadas do motor de triagem (determinístico/LLM) "
            "para apoio ao despacho na Mesa."
        ),
    )
    equipamento = models.ForeignKey(
        "catalogo.EquipamentoPublico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="protocolos",
    )
    qtd_cobrancas_cidadao = models.PositiveIntegerField(default=0, db_index=True)
    ultima_cobranca_em = models.DateTimeField(null=True, blank=True)
    ultimo_alerta_sla_nivel = models.CharField(max_length=32, blank=True, default="")
    prazo_sla = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Prazo absoluto do SLA (prorrogável após pausas de diligência).",
    )
    sla_pausado_desde = models.DateTimeField(null=True, blank=True)
    tempo_sla_pausado_segundos = models.PositiveIntegerField(default=0)
    status_anterior_diligencia = models.CharField(max_length=40, blank=True, default="")
    qtd_reaberturas = models.PositiveIntegerField(default=0, db_index=True)
    ultima_reabertura_em = models.DateTimeField(null=True, blank=True)
    reabertura_ate = models.DateTimeField(null=True, blank=True, db_index=True)
    encerrado_definitivamente_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-data_criacao"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["servico"]),
            models.Index(fields=["super_os"]),
            models.Index(fields=["nota_satisfacao"]),
            models.Index(fields=["equipamento"]),
            models.Index(fields=["qtd_cobrancas_cidadao"]),
        ]

    def __str__(self):
        return self.codigo

    @staticmethod
    def gerar_codigo():
        from django.utils import timezone

        ano = timezone.now().year
        prefix = f"PROT-{ano}-"
        ultimo = (
            Protocolo.objects.filter(codigo__startswith=prefix)
            .order_by("-codigo")
            .values_list("codigo", flat=True)
            .first()
        )
        seq = 1
        if ultimo:
            try:
                seq = int(ultimo.split("-")[-1]) + 1
            except ValueError:
                seq = Protocolo.objects.count() + 1
        return f"{prefix}{seq:03d}"


class SuperOS(models.Model):
    """Incidente mestre — agrupamento operacional de protocolos duplicados/similares."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=24, unique=True, db_index=True)
    titulo_resumo = models.CharField(max_length=255)
    descricao_geral = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Protocolo.Status.choices,
        default=Protocolo.Status.EM_ANALISE,
    )
    latitude_centro = models.FloatField(null=True, blank=True)
    longitude_centro = models.FloatField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Super OS"
        verbose_name_plural = "Super OS"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["codigo"]),
        ]

    def __str__(self):
        return self.codigo

    @staticmethod
    def gerar_codigo():
        from django.utils import timezone

        ano = timezone.now().year
        prefix = f"SOS-{ano}-"
        ultimo = (
            SuperOS.objects.filter(codigo__startswith=prefix)
            .order_by("-codigo")
            .values_list("codigo", flat=True)
            .first()
        )
        seq = 1
        if ultimo:
            try:
                seq = int(ultimo.split("-")[-1]) + 1
            except ValueError:
                seq = SuperOS.objects.count() + 1
        return f"{prefix}{seq:03d}"


class AnexoProtocolo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, related_name="anexos"
    )
    arquivo = models.FileField(upload_to="protocolos/anexos/%Y/%m/")
    tipo_mime = models.CharField(max_length=120, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)


class ProtocoloHistorico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, related_name="historico"
    )
    status = models.CharField(max_length=20, choices=Protocolo.Status.choices)
    descricao = models.TextField()
    equipe_nome = models.CharField(max_length=255, blank=True)
    registrado_em = models.DateTimeField(auto_now_add=True)


class AvaliacaoProtocolo(models.Model):
    """Pesquisa de satisfação do cidadão após conclusão do protocolo (CSAT)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.OneToOneField(
        Protocolo,
        on_delete=models.CASCADE,
        related_name="avaliacao",
    )
    nota = models.PositiveSmallIntegerField(choices=Protocolo.NotaSatisfacao.choices)
    comentario = models.TextField(blank=True, default="", max_length=500)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]

    def __str__(self):
        return f"Avaliação {self.nota}/5 — {self.protocolo.codigo}"


class ProtocoloComentario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, related_name="comentarios"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comentarios_protocolo",
    )
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)


class OrdemServico(models.Model):
    """Sub-tarefa operacional (scatter-gather) vinculada a um protocolo pai."""

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        AGUARDANDO_CIDADAO = "aguardando_cidadao", "Aguardando cidadão"
        AGUARDANDO_FORMALIZACAO = "aguardando_formalizacao", "Aguardando formalização"
        AGUARDANDO_ASSINATURA = "aguardando_assinatura", "Aguardando assinatura"
        CONCLUIDA = "concluida", "Concluída"
        CANCELADA = "cancelada", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, related_name="ordens_servico"
    )
    super_os = models.ForeignKey(
        SuperOS,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ordens_servico",
        help_text="Quando preenchido, a OS opera o incidente mestre (Super OS).",
    )
    unidade = models.ForeignKey(
        "catalogo.UnidadeAdministrativa",
        on_delete=models.PROTECT,
        related_name="ordens_servico",
    )
    nome_equipe = models.CharField(max_length=255, blank=True)
    descricao = models.TextField(blank=True)
    prazo_horas = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Prazo operacional da ordem em horas (scatter-gather).",
    )
    observacoes_execucao = models.TextField(blank=True)
    despacho_tecnico = models.TextField(blank=True)
    observacoes_extras = models.TextField(blank=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDENTE
    )
    concluido_em = models.DateTimeField(null=True, blank=True)
    magic_link_token = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Token do link mágico para envio de evidências sem login.",
    )
    magic_link_expira_em = models.DateTimeField(null=True, blank=True)
    magic_link_gerado_em = models.DateTimeField(null=True, blank=True)
    magic_link_acessos = models.PositiveIntegerField(default=0)
    formalizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordens_formalizadas",
    )
    despachado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordens_despachadas",
        help_text="Servidor da ouvidoria que criou o despacho scatter desta OS.",
    )
    assinatura_digital_hash = models.CharField(max_length=64, blank=True)
    data_formalizacao = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Momento da assinatura eletrônica simples na formalização setorial.",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    prazo_sla = models.DateTimeField(null=True, blank=True)
    sla_pausado_desde = models.DateTimeField(null=True, blank=True)
    tempo_sla_pausado_segundos = models.PositiveIntegerField(default=0)
    status_anterior_diligencia = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        verbose_name = "ordem de serviço"
        verbose_name_plural = "ordens de serviço"
        ordering = ["criado_em"]
        indexes = [
            models.Index(fields=["super_os"]),
        ]


class AnexoOrdemServico(models.Model):
    """Evidências (antes/depois) anexadas pela equipe ao concluir a ordem."""

    class TipoEvidencia(models.TextChoices):
        ANTES = "antes", "Antes"
        DEPOIS = "depois", "Depois"
        DURANTE = "durante", "Durante"
        OUTRO = "outro", "Outro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordem = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name="anexos",
    )
    arquivo = models.FileField(upload_to="ordens/anexos/%Y/%m/")
    tipo_mime = models.CharField(max_length=120, blank=True)
    nome_original = models.CharField(max_length=255, blank=True)
    tipo_evidencia = models.CharField(
        max_length=16,
        choices=TipoEvidencia.choices,
        default=TipoEvidencia.DEPOIS,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        verbose_name = "anexo de ordem de serviço"
        verbose_name_plural = "anexos de ordem de serviço"


class TextoPadraoDespacho(models.Model):
    """Textos de despacho técnico reutilizáveis por unidade administrativa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unidade = models.ForeignKey(
        "catalogo.UnidadeAdministrativa",
        on_delete=models.CASCADE,
        related_name="textos_padrao_despacho",
    )
    titulo = models.CharField(max_length=120)
    texto = models.TextField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["titulo"]
        verbose_name = "texto padrão de despacho"
        verbose_name_plural = "textos padrão de despacho"
        indexes = [
            models.Index(fields=["unidade", "ativo"]),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.unidade_id})"


class NotificacaoInterna(models.Model):
    """Notificações in-app para servidores do backoffice."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario_destino = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificacoes_internas",
    )
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    link_acao = models.CharField(max_length=500, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_criacao"]
        indexes = [
            models.Index(fields=["usuario_destino", "lida", "-data_criacao"]),
        ]
        verbose_name = "notificação interna"
        verbose_name_plural = "notificações internas"

    def __str__(self):
        return f"{self.titulo} → {self.usuario_destino_id}"


class SolicitacaoAssinatura(models.Model):
    """Pedido de assinatura eletrônica de despacho por superior hierárquico."""

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        ASSINADA = "assinada", "Assinada"
        REJEITADA = "rejeitada", "Rejeitada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordem_servico = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name="solicitacoes_assinatura",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="solicitacoes_assinatura_enviadas",
    )
    assinante_destino = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="solicitacoes_assinatura_pendentes",
    )
    despacho_tecnico = models.TextField(
        help_text="Texto exato submetido à assinatura (conteúdo do hash).",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDENTE,
        db_index=True,
    )
    hash_assinatura = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text="SHA-256 gerado no ato da assinatura pelo assinante.",
    )
    assinada_em = models.DateTimeField(null=True, blank=True)
    motivo_rejeicao = models.TextField(blank=True)
    rejeitada_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "solicitação de assinatura"
        verbose_name_plural = "solicitações de assinatura"
        indexes = [
            models.Index(fields=["assinante_destino", "status", "-criado_em"]),
            models.Index(fields=["ordem_servico", "status"]),
        ]

    def __str__(self):
        return f"Assinatura {self.pk} — {self.status}"


class SessaoChat(models.Model):
    """Sessão conversacional stateful entre cidadão e orquestrador de IA."""

    class Status(models.TextChoices):
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        FINALIZADO_PROTOCOLO = "finalizado_protocolo", "Protocolo gerado"
        CANCELADO = "cancelado", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessoes_chat",
    )
    categoria_inicial = models.CharField(
        max_length=80,
        help_text="Slug ou nome da categoria escolhida no frontend (ex.: zeladoria_urbana).",
    )
    servico_identificado = models.ForeignKey(
        "catalogo.ServicoCatalogo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessoes_chat",
    )
    dados_coletados = models.JSONField(
        default=dict,
        blank=True,
        help_text="Slot filling incremental (JSON Schema do serviço).",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.EM_ANDAMENTO,
    )
    protocolo_final = models.OneToOneField(
        Protocolo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessao_chat",
    )
    motivo_inelegibilidade = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Rótulo da regra que bloqueou o atendimento (métricas / escudo político).",
    )
    nota_abertura = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Satisfação com o processo de abertura da solicitação no chat (1–5).",
    )
    comentario_abertura = models.TextField(blank=True, default="", max_length=500)
    avaliacao_abertura_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizado_em"]
        indexes = [
            models.Index(fields=["usuario", "status"]),
            models.Index(fields=["categoria_inicial"]),
        ]

    def __str__(self):
        return f"Chat {self.id} ({self.status})"


class MensagemChat(models.Model):
    """Mensagem individual dentro de uma sessão."""

    class Autor(models.TextChoices):
        CIDADAO = "cidadao", "Cidadão"
        IA = "ia", "IA"
        SISTEMA = "sistema", "Sistema"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(
        SessaoChat,
        on_delete=models.CASCADE,
        related_name="mensagens",
    )
    autor = models.CharField(max_length=16, choices=Autor.choices)
    conteudo_texto = models.TextField()
    localizacao = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    tipo_acao = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Comando de UI para o frontend (ex.: solicitar_gps, quick_reply:...).",
    )
    payload_ui = models.JSONField(
        blank=True,
        null=True,
        help_text="Snapshot de UI (ex.: config escolha_campo) no momento da mensagem.",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        indexes = [
            models.Index(fields=["sessao", "criado_em"]),
        ]

    def __str__(self):
        return f"{self.autor}: {self.conteudo_texto[:40]}"


class AnexoChatSessao(models.Model):
    """Mídia enviada durante o chat; vinculada ao protocolo no fechamento."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessao = models.ForeignKey(
        SessaoChat,
        on_delete=models.CASCADE,
        related_name="anexos_sessao",
    )
    mensagem = models.ForeignKey(
        MensagemChat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anexos",
    )
    arquivo = models.FileField(upload_to="chat/sessoes/%Y/%m/")
    tipo_mime = models.CharField(max_length=120, blank=True)
    nome_original = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        verbose_name = "anexo de sessão de chat"
        verbose_name_plural = "anexos de sessão de chat"


class NotificacaoCidadao(models.Model):
    """Notificação in-app do PWA (cidadão), com deep link opcional ao protocolo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificacoes_cidadao",
    )
    protocolo = models.ForeignKey(
        "Protocolo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notificacoes_cidadao",
    )
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]
        indexes = [
            models.Index(fields=["usuario", "lida", "-criada_em"]),
        ]
        verbose_name = "notificação do cidadão"
        verbose_name_plural = "notificações do cidadão"

    def __str__(self):
        return f"{self.titulo} → {self.usuario_id}"


class PushSubscription(models.Model):
    """Inscrição Web Push (VAPID) do navegador PWA."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.URLField(max_length=1024, unique=True)
    p256dh = models.CharField(max_length=512)
    auth = models.CharField(max_length=512)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["usuario", "-atualizado_em"]),
        ]
        verbose_name = "inscrição Web Push"
        verbose_name_plural = "inscrições Web Push"

    def __str__(self):
        return f"Push {self.usuario_id} ({self.endpoint[:48]}…)"


class ConfiguracaoSlaCobranca(models.Model):
    """Parâmetros de SLA, cobrança do cidadão e digest (singleton id=1)."""

    singleton_id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )
    cobranca_cidadao_ativa = models.BooleanField(default=True)
    cooldown_cobranca_horas = models.PositiveIntegerField(default=48)
    alerta_preventivo_percentual = models.PositiveIntegerField(default=80)
    escalonamento_controladoria_dias = models.PositiveIntegerField(default=3)
    emails_controladoria = models.JSONField(default=list, blank=True)
    digest_email_ativo = models.BooleanField(default=True)
    digest_periodicidade = models.CharField(
        max_length=16,
        choices=(
            ("diario", "Diário"),
            ("semanal", "Semanal"),
        ),
        default="diario",
    )
    digest_hora_envio = models.PositiveSmallIntegerField(default=8)
    diligencia_ativa = models.BooleanField(default=True)
    prazo_diligencia_dias = models.PositiveIntegerField(default=5)
    max_diligencias_por_protocolo = models.PositiveIntegerField(default=2)
    acao_expiracao_diligencia = models.CharField(
        max_length=32,
        choices=(
            ("devolver_fila", "Devolver para a fila"),
            ("encerrar_sem_resposta", "Encerrar por falta de resposta"),
        ),
        default="devolver_fila",
    )
    reabertura_ativa = models.BooleanField(default=True)
    prazo_reabertura_dias = models.PositiveIntegerField(default=7)
    max_reaberturas_por_protocolo = models.PositiveIntegerField(default=1)
    nota_csat_gatilho_reabertura = models.PositiveSmallIntegerField(default=2)
    prazo_sla_reabertura_dias = models.PositiveIntegerField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração SLA e cobrança"
        verbose_name_plural = "Configuração SLA e cobrança"

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "ConfiguracaoSlaCobranca":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuração SLA e cobrança"


class ReaberturaProtocolo(models.Model):
    """Contestação do cidadão — reabertura dentro da janela configurável."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name="reaberturas",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reaberturas_solicitadas",
    )
    motivo = models.TextField()
    anexos_ids = models.JSONField(default=list, blank=True)
    nota_csat_origem = models.PositiveSmallIntegerField(null=True, blank=True)
    prazo_sla_anterior = models.DateTimeField(null=True, blank=True)
    novo_prazo_sla = models.DateTimeField(null=True, blank=True)
    ordem_servico_criada = models.ForeignKey(
        "OrdemServico",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reabertura_origem",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "reabertura de protocolo"
        verbose_name_plural = "reaberturas de protocolo"

    def __str__(self):
        return f"Reabertura {self.protocolo_id} — {self.criado_em:%Y-%m-%d}"


class DiligenciaProtocolo(models.Model):
    """Pedido de complementação ao cidadão com pausa de SLA."""

    class Status(models.TextChoices):
        AGUARDANDO_CIDADAO = "aguardando_cidadao", "Aguardando cidadão"
        RESPONDIDA = "respondida", "Respondida"
        EXPIRADA = "expirada", "Expirada"
        CANCELADA = "cancelada", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name="diligencias",
    )
    ordem_servico = models.ForeignKey(
        "OrdemServico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diligencias",
    )
    unidade_solicitante = models.ForeignKey(
        "catalogo.UnidadeAdministrativa",
        on_delete=models.PROTECT,
        related_name="diligencias_solicitadas",
    )
    autor_servidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="diligencias_criadas",
    )
    pergunta = models.TextField()
    exige_anexo = models.BooleanField(default=False)
    prazo_resposta = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.AGUARDANDO_CIDADAO,
        db_index=True,
    )
    resposta_cidadao = models.TextField(blank=True, default="")
    anexos_ids = models.JSONField(default=list, blank=True)
    respondida_em = models.DateTimeField(null=True, blank=True)
    encerrada_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["protocolo", "-criado_em"]),
            models.Index(fields=["status", "prazo_resposta"]),
        ]


class CobrancaProtocolo(models.Model):
    """Registro de cobrança do munícipe sobre protocolo em atraso."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocolo = models.ForeignKey(
        Protocolo,
        on_delete=models.CASCADE,
        related_name="cobrancas_cidadao",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cobrancas_protocolo",
    )
    mensagem = models.TextField(blank=True, default="", max_length=300)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["protocolo", "-criado_em"]),
        ]


class RelatorioSlaEnvio(models.Model):
    """Auditoria de envios de digest / disparo manual de SLA."""

    class Tipo(models.TextChoices):
        DIGEST_UNIDADE = "digest_unidade", "Digest unidade"
        DIGEST_CONTROLADORIA = "digest_controladoria", "Digest controladoria"
        DISPARO_MANUAL = "disparo_manual", "Disparo manual"

    class Status(models.TextChoices):
        ENVIADO = "enviado", "Enviado"
        ERRO = "erro", "Erro"
        SEM_PENDENCIAS = "sem_pendencias", "Sem pendências"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=32, choices=Tipo.choices)
    unidade = models.ForeignKey(
        "catalogo.UnidadeAdministrativa",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="relatorios_sla_enviados",
    )
    destinatarios = models.JSONField(default=list, blank=True)
    total_protocolos = models.PositiveIntegerField(default=0)
    total_cobrados = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=24, choices=Status.choices)
    erro_detalhe = models.TextField(blank=True, default="")
    disparado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="relatorios_sla_disparados",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]


class ConfiguracaoSistema(models.Model):
    """Parâmetros globais (singleton — registro único id=1)."""

    singleton_id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False,
    )
    dias_busca_cluster_ia = models.PositiveIntegerField(
        default=30,
        help_text=(
            "Janela em dias para o motor de clusterização considerar protocolos "
            "na geração de sugestões de Super OS."
        ),
    )
    notificar_novos_despachos = models.BooleanField(
        default=True,
        help_text="Dispara notificações scatter ao despachar protocolos.",
    )
    notificar_sla_vencido = models.BooleanField(
        default=True,
        help_text="Permite o job automático de alerta de SLA vencido.",
    )
    notificar_novas_super_os = models.BooleanField(
        default=True,
        help_text="Dispara notificações ao despachar ordens de uma Super OS.",
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração do sistema"
        verbose_name_plural = "Configuração do sistema"

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "ConfiguracaoSistema":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Configuração do sistema (janela IA: {self.dias_busca_cluster_ia} dias)"
