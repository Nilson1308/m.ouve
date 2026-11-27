import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usuarioPode } from '@/composables/useRbac'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/app/dashboard'
    },

    {
      path: '/login',
      redirect: '/app/login'
    },

    {
      path: '/app/login',
      name: 'app-login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresGuest: true, audience: 'app' }
    },

    {
      path: '/backoffice/login',
      name: 'backoffice-login',
      component: () => import('@/views/backoffice/BackofficeLoginView.vue'),
      meta: { requiresGuest: true, audience: 'backoffice' }
    },

    {
      path: '/campo/:token',
      name: 'campo-evidencias',
      component: () => import('@/views/pwa/MagicLinkCampoView.vue'),
      props: true,
      meta: { requiresAuth: false }
    },

    {
      path: '/design-system',
      name: 'design-system',
      component: () => import('@/views/DesignSystemView.vue'),
      meta: { requiresAuth: false }
    },

    {
      path: '/app',
      component: () => import('@/layouts/PwaLayout.vue'),
      meta: { requiresAuth: true, audience: 'app' },
      children: [
        {
          path: '',
          redirect: '/app/dashboard'
        },
        {
          path: 'dashboard',
          name: 'pwa-dashboard',
          component: () => import('@/views/pwa/DashboardView.vue')
        },
        {
          path: 'nova-solicitacao',
          name: 'pwa-nova-solicitacao',
          component: () => import('@/views/pwa/NovaSolicitacaoView.vue'),
          meta: { pwaHideShellHeader: true }
        },
        {
          path: 'nova-solicitacao/:categoriaSlug',
          name: 'pwa-nova-solicitacao-categoria',
          component: () => import('@/views/pwa/NovaSolicitacaoCategoriaView.vue'),
          props: true,
          meta: { pwaHideShellHeader: true }
        },
        {
          path: 'chat/:categoriaNome',
          name: 'pwa-chat-solicitacao',
          component: () => import('@/views/pwa/ChatSolicitacaoView.vue'),
          props: true,
          meta: { pwaHideShellHeader: true }
        },
        {
          path: 'protocolo/:id',
          name: 'pwa-detalhes-protocolo',
          component: () => import('@/views/pwa/DetalhesProtocoloView.vue'),
          props: true,
          meta: { pwaHideShellHeader: true }
        },
        {
          path: 'perfil',
          name: 'pwa-perfil',
          component: () => import('@/views/pwa/PerfilUsuarioView.vue'),
          meta: { pwaHideShellHeader: true }
        },
        {
          path: 'notificacoes',
          name: 'pwa-notificacoes',
          component: () => import('@/views/pwa/NotificacoesCidadaoView.vue'),
          meta: { pwaHideShellHeader: true }
        },
        {
          path: 'ajuda',
          name: 'pwa-ajuda',
          component: () => import('@/views/pwa/AjudaCidadaoView.vue'),
          meta: { pwaHideShellHeader: true, pageTitle: 'Central de Ajuda' }
        }
      ]
    },

    {
      path: '/backoffice',
      component: () => import('@/layouts/BackofficeLayout.vue'),
      meta: { requiresAuth: true, requiresBackoffice: true },
      children: [
        {
          path: '',
          redirect: '/backoffice/mesa-trabalho'
        },
        {
          path: 'acesso-negado',
          name: 'backoffice-acesso-negado',
          component: () => import('@/views/backoffice/AcessoNegadoView.vue')
        },
        {
          path: 'perfil',
          name: 'backoffice-perfil',
          component: () => import('@/views/backoffice/MeuPerfilView.vue')
        },
        {
          path: 'dashboard',
          name: 'backoffice-dashboard',
          component: () => import('@/views/backoffice/DashboardEficienciaView.vue'),
          meta: { requirePermission: 'mesa_trabalho.ler', pageTitle: 'Visão Executiva' }
        },
        {
          path: 'dashboard/mapa-gis',
          name: 'backoffice-dashboard-mapa-gis',
          component: () => import('@/views/backoffice/DashboardMapaGISView.vue'),
          meta: { requirePermission: 'mapa_ia.ler', pageTitle: 'Visão Territorial' }
        },
        {
          path: 'dashboard/inelegibilidade',
          name: 'backoffice-dashboard-inelegibilidade',
          component: () => import('@/views/backoffice/DashboardInelegibilidadeView.vue'),
          meta: { requirePermission: 'mesa_trabalho.ler', pageTitle: 'Triagem e Bloqueios' }
        },
        {
          path: 'mesa-trabalho',
          name: 'backoffice-mesa-trabalho',
          component: () => import('@/views/backoffice/MesaTrabalhoView.vue'),
          meta: { requirePermission: 'mesa_trabalho.ler', pageTitle: 'Mesa de Trabalho' }
        },
        {
          path: 'relatorios/sla-cobrancas',
          name: 'backoffice-sla-cobrancas',
          component: () => import('@/views/backoffice/SlaCobrancasView.vue'),
          meta: { requirePermission: 'mesa_trabalho.ler', pageTitle: 'SLA & Cobranças' }
        },
        {
          path: 'protocolo/:id',
          name: 'backoffice-protocolo-detalhes',
          component: () => import('@/views/backoffice/DetalhesProtocoloInternoView.vue'),
          props: true,
          meta: { requirePermission: 'mesa_trabalho.ler' }
        },
        {
          path: 'super-os/:id',
          name: 'backoffice-super-os-detalhes',
          component: () => import('@/views/backoffice/DetalhesSuperOSView.vue'),
          props: true,
          meta: { requirePermission: 'mesa_trabalho.ler' }
        },
        {
          path: 'setorial',
          name: 'backoffice-setorial',
          component: () => import('@/views/backoffice/PainelSetorialView.vue'),
          meta: { requirePermission: 'painel_setorial.ler', pageTitle: 'Painel Setorial' }
        },
        {
          path: 'textos-padrao',
          name: 'backoffice-textos-padrao',
          component: () => import('@/views/backoffice/TextosPadraoBackofficeView.vue'),
          meta: { requirePermission: 'textos_padrao.ler', pageTitle: 'Textos padrão' }
        },
        {
          path: 'configuracoes',
          name: 'backoffice-configuracoes',
          component: () => import('@/views/backoffice/ConfiguracoesView.vue'),
          meta: { requireConfigAccess: true, pageTitle: 'Configurações' }
        },
        {
          path: 'notificacoes',
          name: 'backoffice-notificacoes',
          component: () => import('@/views/backoffice/NotificacoesInternasView.vue'),
          meta: { requirePermission: 'mesa_trabalho.ler', pageTitle: 'Notificações' }
        },
        {
          path: 'manual',
          name: 'backoffice-manual',
          component: () => import('@/views/backoffice/ManualSistemaView.vue'),
          meta: { pageTitle: 'Manual do Sistema' }
        }
      ]
    },

    {
      path: '/dashboard',
      redirect: '/app/dashboard'
    },
    {
      path: '/nova-solicitacao',
      redirect: '/app/nova-solicitacao'
    },
    {
      path: '/chat/:categoriaNome',
      redirect: (to) => `/app/chat/${to.params.categoriaNome}`
    },
    {
      path: '/protocolo/:id',
      redirect: (to) => `/app/protocolo/${to.params.id}`
    },
    {
      path: '/perfil',
      redirect: '/app/perfil'
    },
    {
      path: '/backoffice/configuracoes/textos-padrao',
      redirect: { name: 'backoffice-textos-padrao' }
    }
  ]
})

function destinoLogin(to) {
  if (to.path.startsWith('/backoffice')) return '/backoffice/login'
  return '/app/login'
}

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  authStore.checkSession()

  if (authStore.isAuthenticated && !authStore.user?.permissoes) {
    await authStore.refreshPerfil().catch(() => {})
  }

  const isBackofficeArea = to.path.startsWith('/backoffice')
  const isAppArea = to.path.startsWith('/app')
  const isLoginRoute = to.path === '/app/login' || to.path === '/backoffice/login'

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ path: destinoLogin(to), query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    if (authStore.isBackoffice && to.meta.audience === 'backoffice') {
      next('/backoffice/mesa-trabalho')
    } else if (authStore.isBackoffice) {
      next('/backoffice/mesa-trabalho')
    } else {
      next('/app/dashboard')
    }
    return
  }

  if (isBackofficeArea && !isLoginRoute && authStore.isAuthenticated && !authStore.isBackoffice) {
    next('/app/dashboard')
    return
  }

  if (isAppArea && !isLoginRoute && authStore.isAuthenticated && authStore.isBackoffice) {
    next('/backoffice/mesa-trabalho')
    return
  }

  if (to.meta.requireConfigAccess && authStore.isAuthenticated) {
    const ok =
      authStore.isSuperAdmin ||
      usuarioPode(authStore, 'configuracoes.ler') ||
      usuarioPode(authStore, 'gestao_usuarios.ler')
    if (!ok) {
      next({
        name: 'backoffice-acesso-negado',
        query: { perm: 'configuracoes.ler', from: to.fullPath }
      })
      return
    }
  }

  if (to.meta.requirePermission && authStore.isAuthenticated) {
    const codigo = to.meta.requirePermission
    const superOk = to.meta.allowSuperAdmin && authStore.isSuperAdmin
    if (!superOk && !usuarioPode(authStore, codigo)) {
      next({
        name: 'backoffice-acesso-negado',
        query: { perm: codigo, from: to.fullPath }
      })
      return
    }
  }

  next()
})

export default router