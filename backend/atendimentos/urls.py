from django.urls import include, path
from rest_framework.routers import DefaultRouter

from atendimentos import views
from atendimentos.backoffice_views import (
    BackofficeConcluirOrdemServicoView,
    BackofficeDespacharProtocoloView,
    BackofficeDevolverOrdemServicoView,
    BackofficeFiltrosMesaView,
    BackofficeProtocoloDetalheView,
    BackofficeProtocoloListView,
    BackofficeUnidadesListView,
    BackofficeValidarProtocoloView,
)
from atendimentos.kanban_views import BackofficeKanbanView
from atendimentos.avaliacao_views import AvaliarProtocoloAppView, CriarAvaliacaoView
from atendimentos.notificacoes_cidadao_views import (
    NotificacaoCidadaoListView,
    NotificacaoCidadaoMarcarLidaView,
    PushSubscribeView,
    VapidPublicKeyView,
)
from atendimentos.chat_views import (
    AvaliarAberturaChatView,
    CriarSessaoChatView,
    InteragirChatView,
    ListarMensagensChatView,
)
from atendimentos.public_views import PublicoEvidenciasMagicLinkView
from atendimentos.admin_notificacoes_views import (
    NotificacaoAuditoriaView,
    NotificacaoBroadcastView,
)
from atendimentos.configuracao_sistema_views import ConfiguracaoSistemaAdminView
from atendimentos.diligencia_views import (
    BackofficeAbrirDiligenciaView,
    BackofficeCancelarDiligenciaView,
)
from atendimentos.sla_cobranca_views import (
    ConfiguracaoSlaCobrancaView,
    RelatorioSlaAtrasadosExportarView,
    RelatorioSlaAtrasadosView,
    RelatorioSlaDispararView,
    RelatorioSlaEnviosListView,
)
from atendimentos.saude_infra_views import SaudeInfraAdminView
from atendimentos.dashboard_views import (
    DashboardBairrosView,
    DashboardEficienciaView,
    DashboardInelegibilidadeView,
    DashboardMapaCalorView,
    DashboardQualidadeView,
)
from atendimentos.notificacoes_internas_views import (
    NotificacaoInternaListView,
    NotificacaoInternaMarcarLidaView,
)
from atendimentos.super_os_views import (
    SuperOSIntegrarAncoraView,
    SuperOSAnexarView,
    SuperOSRetroativaView,
    SuperOSAgruparMapaView,
    SuperOSDespacharView,
    SuperOSDetalheView,
    SuperOSSugestoesView,
)
from atendimentos.setorial_views import (
    FormalizarOrdemServicoView,
    GerarMagicLinkOrdemView,
    SetorialFiltrosOpcoesView,
    SetorialOrdensListView,
    UploadEvidenciasOrdemSetorialView,
)
from atendimentos.textos_padrao_views import TextoPadraoDetailView, TextoPadraoListCreateView
from atendimentos.assinatura_views import (
    AssinantesElegiveisListView,
    AssinarSolicitacaoView,
    AssinaturasPendentesListView,
    RejeitarSolicitacaoView,
    SolicitarAssinaturaView,
)

router = DefaultRouter(trailing_slash=False)
router.register("protocolos", views.ProtocoloViewSet, basename="protocolos")

urlpatterns = [
    path("backoffice/dashboard/eficiencia", DashboardEficienciaView.as_view()),
    path("backoffice/dashboard/eficiencia/", DashboardEficienciaView.as_view()),
    path("backoffice/dashboard/mapa-calor", DashboardMapaCalorView.as_view()),
    path("backoffice/dashboard/mapa-calor/", DashboardMapaCalorView.as_view()),
    path("backoffice/dashboard/bairros", DashboardBairrosView.as_view()),
    path("backoffice/dashboard/bairros/", DashboardBairrosView.as_view()),
    path("backoffice/dashboard/qualidade", DashboardQualidadeView.as_view()),
    path("backoffice/dashboard/qualidade/", DashboardQualidadeView.as_view()),
    path("backoffice/dashboard/inelegibilidade", DashboardInelegibilidadeView.as_view()),
    path("backoffice/dashboard/inelegibilidade/", DashboardInelegibilidadeView.as_view()),
    path("backoffice/mesa/unidades", BackofficeUnidadesListView.as_view()),
    path("backoffice/mesa/filtros", BackofficeFiltrosMesaView.as_view()),
    path("backoffice/kanban", BackofficeKanbanView.as_view()),
    path("backoffice/protocolos", BackofficeProtocoloListView.as_view()),
    path(
        "backoffice/protocolos/<str:protocolo_id>/despachar",
        BackofficeDespacharProtocoloView.as_view(),
    ),
    path(
        "backoffice/protocolos/<str:protocolo_id>",
        BackofficeProtocoloDetalheView.as_view(),
    ),
    path(
        "backoffice/protocolos/<str:protocolo_id>/diligencias",
        BackofficeAbrirDiligenciaView.as_view(),
    ),
    path(
        "backoffice/diligencias/<uuid:diligencia_id>/cancelar",
        BackofficeCancelarDiligenciaView.as_view(),
    ),
    path(
        "backoffice/protocolos/<str:protocolo_id>/validar",
        BackofficeValidarProtocoloView.as_view(),
    ),
    path(
        "backoffice/ordens/<uuid:ordem_id>/concluir",
        BackofficeConcluirOrdemServicoView.as_view(),
    ),
    path(
        "backoffice/ordens/<uuid:ordem_id>/devolver",
        BackofficeDevolverOrdemServicoView.as_view(),
    ),
    path(
        "backoffice/ordens/<uuid:ordem_id>/gerar-link",
        GerarMagicLinkOrdemView.as_view(),
    ),
    path(
        "backoffice/ordens/<uuid:ordem_id>/formalizar",
        FormalizarOrdemServicoView.as_view(),
    ),
    path(
        "backoffice/ordens/<uuid:ordem_id>/evidencias",
        UploadEvidenciasOrdemSetorialView.as_view(),
    ),
    path("backoffice/super-os/sugestoes", SuperOSSugestoesView.as_view()),
    path("backoffice/super-os/retroativa", SuperOSRetroativaView.as_view()),
    path("backoffice/super-os/agrupar-mapa", SuperOSAgruparMapaView.as_view()),
    path("backoffice/super-os/<uuid:super_os_id>", SuperOSDetalheView.as_view()),
    path(
        "backoffice/super-os/<uuid:super_os_id>/integrar-ancora",
        SuperOSIntegrarAncoraView.as_view(),
    ),
    path(
        "backoffice/super-os/<uuid:super_os_id>/anexar",
        SuperOSAnexarView.as_view(),
    ),
    path(
        "backoffice/super-os/<uuid:super_os_id>/despachar",
        SuperOSDespacharView.as_view(),
    ),
    path("backoffice/setorial/filtros", SetorialFiltrosOpcoesView.as_view()),
    path("backoffice/setorial/ordens", SetorialOrdensListView.as_view()),
    path("backoffice/textos-padrao", TextoPadraoListCreateView.as_view()),
    path(
        "backoffice/textos-padrao/<uuid:pk>",
        TextoPadraoDetailView.as_view(),
    ),
    path(
        "backoffice/admin/configuracao-sistema",
        ConfiguracaoSistemaAdminView.as_view(),
    ),
    path(
        "backoffice/configuracoes/sla-cobranca",
        ConfiguracaoSlaCobrancaView.as_view(),
    ),
    path(
        "backoffice/configuracoes/sla-cobranca/",
        ConfiguracaoSlaCobrancaView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados",
        RelatorioSlaAtrasadosView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/",
        RelatorioSlaAtrasadosView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/exportar",
        RelatorioSlaAtrasadosExportarView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/exportar/",
        RelatorioSlaAtrasadosExportarView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/disparar-agora",
        RelatorioSlaDispararView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/disparar-agora/",
        RelatorioSlaDispararView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/envios",
        RelatorioSlaEnviosListView.as_view(),
    ),
    path(
        "backoffice/relatorios/sla-atrasados/envios/",
        RelatorioSlaEnviosListView.as_view(),
    ),
    path(
        "backoffice/admin/saude-infra",
        SaudeInfraAdminView.as_view(),
    ),
    path(
        "backoffice/admin/notificacoes/auditoria",
        NotificacaoAuditoriaView.as_view(),
    ),
    path(
        "backoffice/admin/notificacoes/broadcast",
        NotificacaoBroadcastView.as_view(),
    ),
    path("backoffice/notificacoes", NotificacaoInternaListView.as_view()),
    path(
        "backoffice/notificacoes/<uuid:notificacao_id>/marcar-lida",
        NotificacaoInternaMarcarLidaView.as_view(),
    ),
    path(
        "backoffice/notificacoes/<uuid:notificacao_id>/lida",
        NotificacaoInternaMarcarLidaView.as_view(),
    ),
    path(
        "backoffice/assinaturas/pendentes",
        AssinaturasPendentesListView.as_view(),
    ),
    path(
        "backoffice/assinaturas/assinantes",
        AssinantesElegiveisListView.as_view(),
    ),
    path(
        "backoffice/assinaturas/solicitar",
        SolicitarAssinaturaView.as_view(),
    ),
    path(
        "backoffice/assinaturas/<uuid:solicitacao_id>/rejeitar",
        RejeitarSolicitacaoView.as_view(),
    ),
    path(
        "backoffice/assinaturas/<uuid:solicitacao_id>/assinar",
        AssinarSolicitacaoView.as_view(),
    ),
    path(
        "publico/evidencias/<uuid:token_magic_link>",
        PublicoEvidenciasMagicLinkView.as_view(),
    ),
    path("chat/sessao", CriarSessaoChatView.as_view()),
    path("chat/interagir", InteragirChatView.as_view()),
    path(
        "chat/sessao/<uuid:sessao_id>/mensagens",
        ListarMensagensChatView.as_view(),
        name="chat-sessao-mensagens",
    ),
    path(
        "chat/sessao/<uuid:sessao_id>/avaliar-abertura",
        AvaliarAberturaChatView.as_view(),
        name="chat-avaliar-abertura",
    ),
    path("avaliacoes", CriarAvaliacaoView.as_view()),
    path(
        "app/protocolos/<str:protocolo_id>/avaliar",
        AvaliarProtocoloAppView.as_view(),
    ),
    path("app/notificacoes", NotificacaoCidadaoListView.as_view()),
    path(
        "app/notificacoes/<uuid:notificacao_id>/marcar-lida",
        NotificacaoCidadaoMarcarLidaView.as_view(),
    ),
    path("app/notificacoes/push-subscribe", PushSubscribeView.as_view()),
    path("app/notificacoes/vapid-public-key", VapidPublicKeyView.as_view()),
    path("", include(router.urls)),
    path("admin/estatisticas", views.AdminEstatisticasView.as_view()),
    path("atendimentos/assistente/analisar", views.AssistenteAnalisarView.as_view()),
    path("atendimentos/assistente/transcrever", views.AssistenteTranscreverView.as_view()),
    path("atendimentos/geocode/reverse", views.GeocodeReverseView.as_view()),
    path("atendimentos/geocode/search", views.GeocodeSearchView.as_view()),
]
