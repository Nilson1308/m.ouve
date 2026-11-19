# Arquitetura do M.Ouve

## Visão Geral

O M.Ouve é um PWA (Progressive Web App) construído com Vue.js 3, focado em proporcionar uma experiência mobile-first para cidadãos acessarem serviços de ouvidoria e zeladoria urbana.

## Princípios de Design

### 1. Mobile-First
- Interface otimizada para smartphones
- Gestos touch-friendly
- Performance em conexões lentas
- Suporte offline (PWA)

### 2. Acessibilidade (WCAG 2.1)
- Contraste adequado de cores
- Navegação por teclado
- Leitores de tela
- Texto responsivo

### 3. Gov.br Design System
- Paleta de cores governamental
- Tipografia e espaçamentos padronizados
- Componentes reutilizáveis

## Estrutura de Diretórios

```
src/
├── assets/              # Assets estáticos (CSS, imagens, fonts)
│   └── main.css         # Tailwind + Design System
│
├── components/          # Componentes reutilizáveis
│   ├── LoadingSpinner.vue
│   ├── EmptyState.vue
│   ├── ModalBase.vue
│   └── StatusBadge.vue
│
├── composables/         # Lógica reutilizável (Composition API)
│   ├── useGeolocation.js
│   └── useAudioRecorder.js
│
├── router/              # Configuração de rotas
│   └── index.js
│
├── services/            # Serviços de API
│   └── api.js           # (A ser criado)
│
├── stores/              # Gerenciamento de estado (Pinia)
│   ├── auth.js          # Autenticação
│   └── protocolos.js    # Protocolos/Solicitações
│
├── views/               # Páginas/Views
│   ├── LoginView.vue
│   ├── DashboardView.vue
│   ├── NovaSolicitacaoView.vue
│   ├── FormularioSolicitacaoView.vue
│   └── DetalhesProtocoloView.vue
│
├── App.vue              # Componente raiz
└── main.js              # Entry point
```

## Fluxo de Dados

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       v
┌─────────────┐      ┌──────────────┐
│   Views     │ <──> │  Composables │
└──────┬──────┘      └──────────────┘
       │
       v
┌─────────────┐      ┌──────────────┐
│   Stores    │ <──> │   Services   │
│   (Pinia)   │      │   (API)      │
└─────────────┘      └──────┬───────┘
                            │
                            v
                     ┌──────────────┐
                     │   Backend    │
                     │  Django API  │
                     └──────────────┘
```

## Camadas da Aplicação

### 1. Presentation Layer (Views + Components)
- **Responsabilidade:** Interface do usuário
- **Tecnologia:** Vue 3 SFC, Tailwind CSS
- **Princípios:**
  - Componentes pequenos e reutilizáveis
  - Props down, events up
  - Minimal business logic

### 2. State Management (Pinia Stores)
- **Responsabilidade:** Estado global da aplicação
- **Tecnologia:** Pinia
- **Stores:**
  - `auth`: Autenticação, usuário logado
  - `protocolos`: Lista de protocolos, CRUD
  - `notifications`: (Futuro) Notificações
  - `ui`: (Futuro) Estado da UI (modals, toasts)

### 3. Business Logic (Composables)
- **Responsabilidade:** Lógica reutilizável
- **Tecnologia:** Composition API
- **Composables:**
  - `useGeolocation`: GPS e geocoding
  - `useAudioRecorder`: Gravação e transcrição
  - `useImageUpload`: (Futuro) Upload de imagens
  - `useNotifications`: (Futuro) Push notifications

### 4. Data Access Layer (Services)
- **Responsabilidade:** Comunicação com backend
- **Tecnologia:** Axios
- **Estrutura:**
```javascript
// services/api.js
export const authService = {
  login: (credentials) => axios.post('/auth/login', credentials),
  logout: () => axios.post('/auth/logout')
}

export const protocolosService = {
  list: (filters) => axios.get('/protocolos', { params: filters }),
  create: (data) => axios.post('/protocolos', data),
  get: (id) => axios.get(`/protocolos/${id}`)
}
```

## Padrões de Código

### Vue 3 Composition API

**✅ Boas Práticas:**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  id: { type: String, required: true }
})

// Emits
const emit = defineEmits(['update', 'delete'])

// State
const loading = ref(false)
const data = ref(null)

// Computed
const isValid = computed(() => data.value?.status === 'active')

// Methods
function handleUpdate() {
  emit('update', data.value)
}

// Lifecycle
onMounted(() => {
  // Load data
})
</script>
```

### Pinia Stores

**✅ Boas Práticas:**

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMyStore = defineStore('myStore', () => {
  // State
  const items = ref([])
  const loading = ref(false)
  
  // Getters
  const activeItems = computed(() => 
    items.value.filter(item => item.active)
  )
  
  // Actions
  async function fetchItems() {
    loading.value = true
    try {
      const response = await api.getItems()
      items.value = response.data
    } finally {
      loading.value = false
    }
  }
  
  return {
    items,
    loading,
    activeItems,
    fetchItems
  }
})
```

### Composables

**✅ Boas Práticas:**

```javascript
export function useMyFeature() {
  const state = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  async function doSomething() {
    loading.value = true
    error.value = null
    
    try {
      // logic here
      return { success: true }
    } catch (err) {
      error.value = err.message
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  return {
    state,
    loading,
    error,
    doSomething
  }
}
```

## Estratégias de Performance

### 1. Code Splitting
```javascript
// router/index.js
{
  path: '/dashboard',
  component: () => import('@/views/DashboardView.vue')
}
```

### 2. Lazy Loading de Componentes
```vue
<script setup>
const HeavyComponent = defineAsyncComponent(() => 
  import('./HeavyComponent.vue')
)
</script>
```

### 3. Virtualization (para listas grandes)
```bash
npm install vue-virtual-scroller
```

### 4. Service Worker (PWA)
- Cache de assets estáticos
- Estratégia cache-first para imagens
- Network-first para API calls

## Tratamento de Erros

### Global Error Handler
```javascript
// main.js
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  // Enviar para Sentry/logging service
}
```

### API Error Handler
```javascript
// services/api.js
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Redirect to login
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

## Segurança

### 1. XSS Prevention
- Vue automaticamente escapa conteúdo
- Evitar `v-html` quando possível
- Sanitizar input do usuário

### 2. CSRF Protection
- Token CSRF em todas as requisições de mutação
- SameSite cookies

### 3. Autenticação
- JWT armazenado em localStorage (com expiração curta)
- Refresh token em httpOnly cookie
- Auto-refresh do token antes de expirar

### 4. Validação
- Validação client-side (UX)
- Validação server-side (Segurança)
- Nunca confiar apenas no frontend

## Testing Strategy

### Unit Tests (Vitest)
```bash
# Adicionar quando necessário
npm install -D vitest @vue/test-utils
```

```javascript
// components/__tests__/StatusBadge.spec.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '../StatusBadge.vue'

describe('StatusBadge', () => {
  it('renders correct label', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'resolvido' }
    })
    expect(wrapper.text()).toContain('Resolvido')
  })
})
```

### E2E Tests (Playwright)
```bash
# Adicionar quando necessário
npm install -D @playwright/test
```

## Deployment

### Build para Produção
```bash
npm run build
```

### Variáveis de Ambiente
```env
VITE_API_BASE_URL=https://api.sinapse.gov.br
VITE_GOVBR_CLIENT_ID=xxx
```

### Checklist de Deploy
- [ ] Build sem warnings
- [ ] Testes passando
- [ ] Variáveis de ambiente configuradas
- [ ] Service Worker funcionando
- [ ] Lighthouse score > 90
- [ ] HTTPS habilitado
- [ ] CORS configurado no backend

## Monitoramento

### Métricas Importantes
- **Performance:**
  - Largest Contentful Paint (LCP)
  - First Input Delay (FID)
  - Cumulative Layout Shift (CLS)

- **Business:**
  - Taxa de conversão (protocolos criados)
  - Tempo médio de criação
  - Taxa de abandono

### Ferramentas
- Google Analytics / Matomo
- Sentry (error tracking)
- LogRocket (session replay)

## Roadmap Técnico

### Fase 1 (Atual) ✅
- [x] Estrutura base
- [x] Autenticação
- [x] CRUD de protocolos
- [x] Interface mobile-first

### Fase 2 (Próxima) 🔄
- [ ] Integração com backend real
- [ ] Gravação de áudio
- [ ] Mapas interativos
- [ ] Upload de imagens real

### Fase 3 (Futuro) 📋
- [ ] Notificações push
- [ ] Chat em tempo real
- [ ] Suporte offline completo
- [ ] Inteligência artificial (NLP/RAG)

---

**Última atualização:** 09/11/2024  
**Versão:** 0.1.0
