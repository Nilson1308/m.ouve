from django.contrib import admin

from atendimentos.models import (
    AnexoChatSessao,
    AnexoOrdemServico,
    AnexoProtocolo,
    AvaliacaoProtocolo,
    CobrancaProtocolo,
    DiligenciaProtocolo,
    ReaberturaProtocolo,
    AvaliacaoInsightIA,
    BriefingOperacionalIA,
    MensagemCopilotoGestor,
    SessaoCopilotoGestor,
    ConfiguracaoAgenteGestao,
    ConfiguracaoMatrizUrgencia,
    ConfiguracaoSlaCobranca,
    ConfiguracaoSistema,
    RelatorioSlaEnvio,
    MensagemChat,
    NotificacaoCidadao,
    NotificacaoInterna,
    PushSubscription,
    OrdemServico,
    Protocolo,
    ProtocoloComentario,
    ProtocoloHistorico,
    SessaoChat,
    SolicitacaoAssinatura,
    SuperOS,
    TextoPadraoDespacho,
)


@admin.register(TextoPadraoDespacho)
class TextoPadraoDespachoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "unidade", "ativo", "atualizado_em")
    list_filter = ("ativo", "unidade")
    search_fields = ("titulo", "texto")


@admin.register(SolicitacaoAssinatura)
class SolicitacaoAssinaturaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ordem_servico",
        "solicitante",
        "assinante_destino",
        "status",
        "criado_em",
    )
    list_filter = ("status",)
    raw_id_fields = ("ordem_servico", "solicitante", "assinante_destino")
    search_fields = ("despacho_tecnico", "hash_assinatura")


@admin.register(NotificacaoCidadao)
class NotificacaoCidadaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "protocolo", "lida", "criada_em")
    list_filter = ("lida",)
    raw_id_fields = ("usuario", "protocolo")
    search_fields = ("titulo", "mensagem")


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "endpoint", "atualizado_em")
    raw_id_fields = ("usuario",)
    search_fields = ("endpoint",)


@admin.register(NotificacaoInterna)
class NotificacaoInternaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario_destino", "lida", "data_criacao")
    list_filter = ("lida",)
    raw_id_fields = ("usuario_destino",)


@admin.register(AvaliacaoProtocolo)
class AvaliacaoProtocoloAdmin(admin.ModelAdmin):
    list_display = ("protocolo", "nota", "criada_em")
    list_filter = ("nota",)
    raw_id_fields = ("protocolo",)


@admin.register(ConfiguracaoSlaCobranca)
class ConfiguracaoSlaCobrancaAdmin(admin.ModelAdmin):
    list_display = (
        "singleton_id",
        "cobranca_cidadao_ativa",
        "cooldown_cobranca_horas",
        "digest_email_ativo",
        "digest_periodicidade",
        "digest_hora_envio",
        "atualizado_em",
    )
    readonly_fields = ("atualizado_em",)

    def has_add_permission(self, request):
        return not ConfiguracaoSlaCobranca.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReaberturaProtocolo)
class ReaberturaProtocoloAdmin(admin.ModelAdmin):
    list_display = ("protocolo", "solicitante", "nota_csat_origem", "criado_em")
    list_filter = ("criado_em",)
    raw_id_fields = ("protocolo", "solicitante", "ordem_servico_criada")
    search_fields = ("protocolo__codigo", "motivo")


@admin.register(DiligenciaProtocolo)
class DiligenciaProtocoloAdmin(admin.ModelAdmin):
    list_display = (
        "protocolo",
        "status",
        "prazo_resposta",
        "exige_anexo",
        "unidade_solicitante",
        "criado_em",
    )
    list_filter = ("status", "exige_anexo")
    search_fields = ("pergunta", "protocolo__codigo", "resposta_cidadao")
    raw_id_fields = ("protocolo", "ordem_servico", "autor_servidor", "unidade_solicitante")


@admin.register(CobrancaProtocolo)
class CobrancaProtocoloAdmin(admin.ModelAdmin):
    list_display = ("protocolo", "solicitante", "criado_em")
    raw_id_fields = ("protocolo", "solicitante")
    search_fields = ("protocolo__codigo",)


@admin.register(RelatorioSlaEnvio)
class RelatorioSlaEnvioAdmin(admin.ModelAdmin):
    list_display = ("tipo", "status", "total_protocolos", "criado_em")
    list_filter = ("tipo", "status")
    raw_id_fields = ("unidade", "disparado_por")


@admin.register(ConfiguracaoAgenteGestao)
class ConfiguracaoAgenteGestaoAdmin(admin.ModelAdmin):
    list_display = (
        "singleton_id",
        "agente_ativo",
        "briefing_proativo_ativo",
        "briefing_hora_geracao",
        "orcamento_tokens_mensal",
        "atualizado_em",
    )
    readonly_fields = ("atualizado_em",)

    def has_add_permission(self, request):
        return not ConfiguracaoAgenteGestao.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BriefingOperacionalIA)
class BriefingOperacionalIAAdmin(admin.ModelAdmin):
    list_display = ("escopo_tipo", "unidade", "data_referencia", "modo_geracao", "criado_em")
    list_filter = ("escopo_tipo", "modo_geracao", "data_referencia")
    raw_id_fields = ("unidade",)


@admin.register(AvaliacaoInsightIA)
class AvaliacaoInsightIAAdmin(admin.ModelAdmin):
    list_display = ("briefing", "insight_id", "usuario", "util", "criado_em")
    raw_id_fields = ("briefing", "usuario")


@admin.register(SessaoCopilotoGestor)
class SessaoCopilotoGestorAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "perspectiva", "unidade", "criado_em", "atualizado_em")
    list_filter = ("perspectiva",)
    search_fields = ("titulo", "usuario__nome", "usuario__cpf")
    raw_id_fields = ("usuario", "unidade")
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(MensagemCopilotoGestor)
class MensagemCopilotoGestorAdmin(admin.ModelAdmin):
    list_display = (
        "sessao",
        "papel",
        "status_processamento",
        "modo_geracao",
        "tokens_entrada",
        "tokens_saida",
        "criado_em",
    )
    list_filter = ("papel", "status_processamento", "modo_geracao")
    raw_id_fields = ("sessao",)
    readonly_fields = ("criado_em",)


@admin.register(ConfiguracaoMatrizUrgencia)
class ConfiguracaoMatrizUrgenciaAdmin(admin.ModelAdmin):
    list_display = (
        "singleton_id",
        "matriz_ativa",
        "ia_urgencia_modo",
        "super_os_limite_alta",
        "super_os_limite_critica",
        "atualizado_em",
    )
    readonly_fields = ("atualizado_em",)

    def has_add_permission(self, request):
        return not ConfiguracaoMatrizUrgencia.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = (
        "singleton_id",
        "modo_abertura_pwa",
        "dias_busca_cluster_ia",
        "notificar_novos_despachos",
        "notificar_sla_vencido",
        "notificar_novas_super_os",
        "atualizado_em",
    )
    fields = (
        "modo_abertura_pwa",
        "dias_busca_cluster_ia",
        "notificar_novos_despachos",
        "notificar_sla_vencido",
        "notificar_novas_super_os",
        "atualizado_em",
    )
    readonly_fields = ("atualizado_em",)

    def has_add_permission(self, request):
        return not ConfiguracaoSistema.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SuperOS)
class SuperOSAdmin(admin.ModelAdmin):
    list_display = ("codigo", "titulo_resumo", "status", "criado_em")
    list_filter = ("status",)
    search_fields = ("codigo", "titulo_resumo")


@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "servico",
        "status",
        "origem_abertura",
        "super_os",
        "usuario",
        "data_criacao",
    )
    list_filter = ("status", "origem_abertura", "servico__categoria")
    raw_id_fields = ("servico", "usuario", "super_os")
    search_fields = ("codigo", "descricao")


class AnexoOrdemServicoInline(admin.TabularInline):
    model = AnexoOrdemServico
    extra = 0
    readonly_fields = ("criado_em",)


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "protocolo",
        "unidade",
        "status",
        "magic_link_token",
        "nome_equipe",
        "prazo_horas",
    )
    list_filter = ("status", "unidade")
    raw_id_fields = ("protocolo", "unidade", "formalizado_por")
    autocomplete_fields = ("unidade",)
    inlines = [AnexoOrdemServicoInline]
    readonly_fields = ("magic_link_gerado_em", "magic_link_expira_em", "magic_link_acessos")


admin.site.register(AnexoProtocolo)
admin.site.register(ProtocoloHistorico)
admin.site.register(ProtocoloComentario)


class MensagemChatInline(admin.TabularInline):
    model = MensagemChat
    extra = 0
    readonly_fields = ("autor", "conteudo_texto", "tipo_acao", "criado_em")
    can_delete = False


@admin.register(AnexoChatSessao)
class AnexoChatSessaoAdmin(admin.ModelAdmin):
    list_display = ("id", "sessao", "nome_original", "tipo_mime", "criado_em")
    raw_id_fields = ("sessao", "mensagem")


@admin.register(SessaoChat)
class SessaoChatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "categoria_inicial",
        "origem_abertura",
        "servico_identificado",
        "status",
        "atualizado_em",
    )
    list_filter = ("status", "origem_abertura", "categoria_inicial")
    search_fields = ("id", "usuario__cpf", "categoria_inicial")
    raw_id_fields = ("usuario", "servico_identificado", "protocolo_final")
    inlines = [MensagemChatInline]
