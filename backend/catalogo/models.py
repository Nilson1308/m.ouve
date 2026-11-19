"""Catálogo dinâmico de serviços (metadados + JSON Schema)."""

import uuid

from django.conf import settings
from django.db import models

from catalogo.form_builder import formulario_schema_padrao


class CategoriaCatalogo(models.Model):
    """Agrupamento de negócio (Ouvidoria, Zeladoria Urbana, etc.)."""

    class TipoLegado(models.TextChoices):
        OUVIDORIA = "ouvidoria", "Ouvidoria"
        ZELADORIA = "zeladoria", "Zeladoria"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(
        max_length=80,
        unique=True,
        help_text="Identificador estável (ex.: ouvidoria, zeladoria_urbana).",
    )
    descricao = models.TextField(blank=True)
    icone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nome lógico do ícone no frontend (ex.: chat-bubble).",
    )
    ordem = models.PositiveSmallIntegerField(
        default=0,
        help_text="Ordem de exibição na tela de nova solicitação.",
    )
    tipo_legado = models.CharField(
        max_length=20,
        choices=TipoLegado.choices,
        blank=True,
        help_text="Compatibilidade com filtro API `tipo=ouvidoria|zeladoria`.",
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "categoria do catálogo"
        verbose_name_plural = "categorias do catálogo"

    def __str__(self):
        return self.nome


class UnidadeAdministrativa(models.Model):
    """Secretaria, departamento ou equipe executora (despacho scatter-gather)."""

    class TomIA(models.TextChoices):
        INSTITUCIONAL = "institucional", "Cordial, claro e padronizado"
        ACOLHEDOR = "acolhedor", "Empático, gentil e paciente"
        OBJETIVO = "objetivo", "Direto ao ponto, ágil e conciso"
        TECNICO = "tecnico", "Preciso e detalhista na coleta de evidências"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=20, blank=True)
    descricao = models.TextField(blank=True)
    tom_ia = models.CharField(
        max_length=30,
        choices=TomIA.choices,
        default=TomIA.INSTITUCIONAL,
        help_text="Personalidade do assistente virtual para serviços desta secretaria.",
    )
    diretrizes_tom_ia = models.TextField(
        blank=True,
        default="",
        help_text="Instruções adicionais de tom ou vocabulário para a IA desta secretaria.",
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "unidade administrativa"
        verbose_name_plural = "unidades administrativas"
        indexes = [
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        return self.sigla or self.nome


class ServicoCatalogo(models.Model):
    """
    Serviço ofertado ao cidadão. O ``schema_formulario`` define campos extras
    validados em ``Protocolo.dados_dinamicos``.

    ``unidade_responsavel`` depende de ``fluxo_tramitacao``:
    - ``direto_secretaria``: executor padrão ao abrir protocolo / OS.
    - ``ouvidoria_encaminha``: **unidade do canal** (recebe e monitora); executores via despacho/triagem.
    - ``hibrido``: canal titular com executor padrão opcional + encaminhamento.
    """

    class FluxoTramitacao(models.TextChoices):
        DIRETO_SECRETARIA = "direto_secretaria", "Direto à secretaria"
        OUVIDORIA_ENCAMINHA = "ouvidoria_encaminha", "Ouvidoria encaminha"
        HIBRIDO = "hibrido", "Híbrido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categoria = models.ForeignKey(
        CategoriaCatalogo,
        on_delete=models.PROTECT,
        related_name="servicos",
    )
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    icone = models.CharField(
        max_length=120,
        blank=True,
        help_text="Nome lógico do ícone ou URL para o app do cidadão.",
    )
    sla_horas = models.PositiveIntegerField(
        default=72,
        help_text="Prazo alvo de atendimento em horas (SLA padrão).",
    )
    permite_cluster = models.BooleanField(
        default=True,
        help_text=(
            "Quando ativo, permite agrupar demandas próximas deste serviço em clusters/Super OS. "
            "Desative para atendimentos individuais ou sensíveis."
        ),
    )
    fluxo_tramitacao = models.CharField(
        max_length=32,
        choices=FluxoTramitacao.choices,
        default=FluxoTramitacao.DIRETO_SECRETARIA,
        db_index=True,
        help_text=(
            "Define como o protocolo é titulado e encaminhado. "
            "Em ouvidoria_encaminha, unidade_responsavel é a unidade do canal."
        ),
    )
    unidade_responsavel = models.ForeignKey(
        UnidadeAdministrativa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servicos_catalogo",
        help_text=(
            "Unidade padrão vinculada ao serviço. "
            "direto_secretaria: executor; ouvidoria_encaminha: unidade do canal (ouvidoria); "
            "hibrido: canal titular com executor sugerido."
        ),
    )
    formulario_schema = models.JSONField(
        default=formulario_schema_padrao,
        blank=True,
        help_text="Lista de campos do Form Builder (app cidadão).",
    )
    schema_formulario = models.JSONField(
        default=dict,
        help_text="JSON Schema legado (chat/validação). Mantido por compatibilidade.",
    )
    formulario_schema_rascunho = models.JSONField(
        null=True,
        blank=True,
        help_text="Rascunho do Form Builder (não exposto ao PWA até publicar).",
    )
    schema_formulario_rascunho = models.JSONField(
        null=True,
        blank=True,
        help_text="Rascunho do JSON Schema (chat/IA).",
    )
    versao_publicada = models.PositiveIntegerField(default=1)
    publicado_em = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Última publicação dos schemas para produção (PWA/chat).",
    )
    ativo = models.BooleanField(default=True)
    is_template = models.BooleanField(
        default=False,
        help_text=(
            "Se True, é um modelo global da plataforma e não aparece para o cidadão."
        ),
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["categoria__ordem", "categoria__nome", "nome"]
        verbose_name = "serviço do catálogo"
        verbose_name_plural = "serviços do catálogo"
        indexes = [
            models.Index(fields=["ativo", "categoria"]),
            models.Index(fields=["is_template", "ativo"]),
        ]

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome})"

    @property
    def sla_padrao_horas(self) -> int:
        return int(self.sla_horas)

    @property
    def tem_rascunho_pendente(self) -> bool:
        return (
            self.formulario_schema_rascunho is not None
            or self.schema_formulario_rascunho is not None
        )

    @property
    def exige_localizacao(self) -> bool:
        meta = self.schema_formulario.get("$metadata") or {}
        if meta.get("exige_localizacao"):
            return True
        for campo in self.formulario_schema or []:
            if not isinstance(campo, dict):
                continue
            if campo.get("type") in ("geo", "location", "address"):
                return True
        return False


class ServicoCatalogoVersao(models.Model):
    """Snapshot imutável de schemas publicados (auditoria / rollback)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    servico = models.ForeignKey(
        ServicoCatalogo,
        on_delete=models.CASCADE,
        related_name="versoes",
    )
    numero_versao = models.PositiveIntegerField()
    formulario_schema = models.JSONField()
    schema_formulario = models.JSONField()
    nota_versao = models.CharField(max_length=255, blank=True, default="")
    publicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalogo_versoes_publicadas",
    )
    publicado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-numero_versao"]
        verbose_name = "versão publicada do serviço"
        verbose_name_plural = "versões publicadas do serviço"
        constraints = [
            models.UniqueConstraint(
                fields=["servico", "numero_versao"],
                name="catalogo_servico_versao_unica",
            ),
        ]
        indexes = [
            models.Index(fields=["servico", "numero_versao"]),
        ]

    def __str__(self):
        return f"{self.servico.nome} v{self.numero_versao}"


class MatrizRoteamentoTematico(models.Model):
    """
    Triagem determinística: valor de um campo do formulário (ex.: categoria=saude)
    sugere unidade executora para despacho.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    servico = models.ForeignKey(
        ServicoCatalogo,
        on_delete=models.CASCADE,
        related_name="matriz_roteamento_tematico",
    )
    chave_schema = models.CharField(
        max_length=80,
        help_text="Nome do campo no JSON Schema / formulario_schema (ex.: categoria).",
    )
    valor_condicao = models.CharField(
        max_length=120,
        help_text="Valor exato da resposta (ex.: saude, educacao).",
    )
    unidade_sugerida = models.ForeignKey(
        UnidadeAdministrativa,
        on_delete=models.PROTECT,
        related_name="roteamentos_tematicos",
        help_text="Unidade executora sugerida quando a condição é atendida.",
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["servico", "chave_schema", "valor_condicao"]
        verbose_name = "matriz de roteamento temático"
        verbose_name_plural = "matrizes de roteamento temático"
        constraints = [
            models.UniqueConstraint(
                fields=["servico", "chave_schema", "valor_condicao"],
                name="catalogo_matriz_roteamento_unica",
            ),
        ]
        indexes = [
            models.Index(fields=["servico", "chave_schema"]),
        ]

    def __str__(self):
        return (
            f"{self.servico.nome}: {self.chave_schema}={self.valor_condicao} → "
            f"{self.unidade_sugerida.sigla or self.unidade_sugerida.nome}"
        )
