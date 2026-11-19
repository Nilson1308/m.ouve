# 🧭 Exemplo de Navegação - Mesa de Trabalho

## Como Adicionar Link no Menu

### Opção 1: No Dashboard (DashboardView.vue)

Se você tiver um menu/sidebar no dashboard, adicione:

```vue
<template>
  <div class="dashboard">
    <!-- Menu Lateral -->
    <nav class="sidebar">
      <ul class="nav-list">
        <!-- Link existente -->
        <li>
          <router-link to="/dashboard" class="nav-item">
            <HomeIcon class="w-5 h-5" />
            <span>Início</span>
          </router-link>
        </li>

        <!-- NOVO: Mesa de Trabalho -->
        <li>
          <router-link to="/backoffice/mesa-trabalho" class="nav-item">
            <ClipboardDocumentListIcon class="w-5 h-5" />
            <span>Mesa de Trabalho</span>
          </router-link>
        </li>

        <!-- Outros links... -->
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { ClipboardDocumentListIcon, HomeIcon } from '@heroicons/vue/24/outline'
</script>
```

---

### Opção 2: Card de Acesso Rápido

Adicione um card clicável no dashboard:

```vue
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Card Mesa de Trabalho -->
    <router-link 
      to="/backoffice/mesa-trabalho"
      class="card-interactive group"
    >
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 rounded-xl bg-primary-500 text-white flex items-center justify-center group-hover:scale-110 transition-transform">
          <ClipboardDocumentListIcon class="w-8 h-8" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Mesa de Trabalho
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Gestão de Protocolos
          </p>
        </div>
      </div>
      <div class="mt-4 flex items-center justify-between">
        <span class="text-sm text-gray-500 dark:text-gray-400">
          Backoffice
        </span>
        <ArrowRightIcon class="w-5 h-5 text-primary-500 group-hover:translate-x-1 transition-transform" />
      </div>
    </router-link>

    <!-- Outros cards... -->
  </div>
</template>

<script setup>
import { 
  ClipboardDocumentListIcon, 
  ArrowRightIcon 
} from '@heroicons/vue/24/outline'
</script>
```

---

### Opção 3: Header Global

Se tiver um header global na aplicação:

```vue
<template>
  <header class="app-header">
    <nav class="flex items-center gap-6">
      <router-link to="/dashboard" class="nav-link">
        Dashboard
      </router-link>
      
      <!-- NOVO -->
      <router-link to="/backoffice/mesa-trabalho" class="nav-link">
        Mesa de Trabalho
      </router-link>
      
      <router-link to="/perfil" class="nav-link">
        Perfil
      </router-link>
    </nav>
  </header>
</template>

<style scoped>
.nav-link {
  @apply text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400;
  @apply font-medium transition-colors;
  @apply relative;
}

.nav-link.router-link-active::after {
  content: '';
  @apply absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500;
}
</style>
```

---

## 🔐 Controle de Acesso

### Guard para Usuários de Backoffice

Se necessário, adicione uma verificação no router:

```javascript
// router/index.js
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Verifica autenticação
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/login')
  }
  
  // NOVO: Verifica permissão de backoffice
  if (to.meta.requiresBackoffice && !authStore.user.isBackoffice) {
    return next({
      name: 'dashboard',
      query: { erro: 'acesso-negado' }
    })
  }
  
  next()
})
```

### Adicione no Store de Auth:

```javascript
// stores/auth.js
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: {
      id: null,
      nome: null,
      email: null,
      tipo: null, // 'cidadao' ou 'servidor'
      isBackoffice: false, // NOVO
      permissoes: []
    }
  }),
  
  getters: {
    podeAcessarBackoffice: (state) => {
      return state.user.isBackoffice || 
             state.user.tipo === 'servidor' ||
             state.user.permissoes.includes('backoffice.acesso')
    }
  }
})
```

---

## 🎨 Estilização do Link Ativo

### CSS Global (main.css):

```css
/* Link de navegação ativo */
.router-link-active {
  @apply text-primary-600 dark:text-primary-400;
  @apply font-semibold;
}

/* Item de menu com background ativo */
.nav-item.router-link-active {
  @apply bg-primary-50 dark:bg-primary-900/20;
  @apply text-primary-600 dark:text-primary-400;
  @apply border-l-4 border-primary-500;
}
```

---

## 📱 Menu Mobile (Hamburguer)

### Exemplo Responsivo:

```vue
<template>
  <div>
    <!-- Botão Hamburguer (mobile) -->
    <button 
      @click="menuAberto = !menuAberto"
      class="lg:hidden btn-icon"
    >
      <Bars3Icon v-if="!menuAberto" class="w-6 h-6" />
      <XMarkIcon v-else class="w-6 h-6" />
    </button>

    <!-- Menu Mobile -->
    <Transition name="slide">
      <nav 
        v-if="menuAberto" 
        class="fixed inset-0 bg-white dark:bg-gray-900 z-50 p-6 lg:hidden"
      >
        <ul class="space-y-4">
          <li>
            <router-link 
              to="/dashboard" 
              @click="menuAberto = false"
              class="nav-item-mobile"
            >
              <HomeIcon class="w-6 h-6" />
              <span>Dashboard</span>
            </router-link>
          </li>
          
          <!-- Mesa de Trabalho -->
          <li>
            <router-link 
              to="/backoffice/mesa-trabalho"
              @click="menuAberto = false"
              class="nav-item-mobile"
            >
              <ClipboardDocumentListIcon class="w-6 h-6" />
              <span>Mesa de Trabalho</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  Bars3Icon, 
  XMarkIcon,
  HomeIcon,
  ClipboardDocumentListIcon 
} from '@heroicons/vue/24/outline'

const menuAberto = ref(false)
</script>

<style scoped>
.nav-item-mobile {
  @apply flex items-center gap-4 p-4 rounded-button;
  @apply text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800;
  @apply transition-colors;
}

.nav-item-mobile.router-link-active {
  @apply bg-primary-100 dark:bg-primary-900;
  @apply text-primary-600 dark:text-primary-400;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}
</style>
```

---

## 🎯 Breadcrumb (Migalha de Pão)

### Componente de Breadcrumb:

```vue
<template>
  <nav class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
    <router-link to="/dashboard" class="hover:text-primary-600">
      Home
    </router-link>
    <ChevronRightIcon class="w-4 h-4" />
    <router-link to="/backoffice/mesa-trabalho" class="hover:text-primary-600">
      Backoffice
    </router-link>
    <ChevronRightIcon class="w-4 h-4" />
    <span class="text-gray-900 dark:text-white font-medium">
      Mesa de Trabalho
    </span>
  </nav>
</template>

<script setup>
import { ChevronRightIcon } from '@heroicons/vue/24/outline'
</script>
```

---

## 🚀 Acesso Direto (Dev)

### Acesse diretamente no navegador:

```
http://localhost:5173/backoffice/mesa-trabalho
```

ou

```
http://localhost:3000/backoffice/mesa-trabalho
```

(Dependendo da porta configurada no seu `vite.config.js`)

---

## ✅ Checklist de Navegação

- [ ] Link adicionado no menu principal
- [ ] Ícone importado (`ClipboardDocumentListIcon`)
- [ ] Rota registrada no router (`/backoffice/mesa-trabalho`)
- [ ] Permissões configuradas (se necessário)
- [ ] Estilo de link ativo aplicado
- [ ] Menu mobile funcional
- [ ] Breadcrumb implementado (opcional)

---

## 📊 Exemplo Completo de Menu Lateral

```vue
<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">
        Ouv.IA
      </h2>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Backoffice
      </p>
    </div>

    <nav class="sidebar-nav">
      <!-- Dashboard -->
      <router-link to="/dashboard" class="sidebar-item">
        <HomeIcon class="w-5 h-5" />
        <span>Dashboard</span>
      </router-link>

      <!-- Mesa de Trabalho -->
      <router-link to="/backoffice/mesa-trabalho" class="sidebar-item">
        <ClipboardDocumentListIcon class="w-5 h-5" />
        <span>Mesa de Trabalho</span>
        <span class="badge-count">{{ totalProtocolos }}</span>
      </router-link>

      <!-- Separador -->
      <div class="sidebar-separator">
        <span class="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold">
          Gestão
        </span>
      </div>

      <!-- Relatórios -->
      <router-link to="/backoffice/relatorios" class="sidebar-item">
        <ChartBarIcon class="w-5 h-5" />
        <span>Relatórios</span>
      </router-link>

      <!-- Configurações -->
      <router-link to="/backoffice/configuracoes" class="sidebar-item">
        <Cog6ToothIcon class="w-5 h-5" />
        <span>Configurações</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { 
  HomeIcon,
  ClipboardDocumentListIcon,
  ChartBarIcon,
  Cog6ToothIcon
} from '@heroicons/vue/24/outline'

// Exemplo de contador dinâmico
const totalProtocolos = computed(() => 12)
</script>

<style scoped>
.sidebar {
  @apply w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700;
  @apply flex flex-col h-screen fixed left-0 top-0;
}

.sidebar-header {
  @apply p-6 border-b border-gray-200 dark:border-gray-700;
}

.sidebar-nav {
  @apply flex-1 p-4 space-y-2 overflow-y-auto;
}

.sidebar-item {
  @apply flex items-center gap-3 px-4 py-3 rounded-button;
  @apply text-gray-700 dark:text-gray-300;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
  @apply transition-colors relative;
}

.sidebar-item.router-link-active {
  @apply bg-primary-50 dark:bg-primary-900/20;
  @apply text-primary-600 dark:text-primary-400;
  @apply font-semibold;
}

.sidebar-item.router-link-active::before {
  content: '';
  @apply absolute left-0 top-0 bottom-0 w-1 bg-primary-500 rounded-r-full;
}

.sidebar-separator {
  @apply my-4 px-4;
}

.badge-count {
  @apply ml-auto badge bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300;
}
</style>
```

---

**Pronto! Agora é só escolher o estilo de navegação que melhor se encaixa no seu projeto.** 🎉
