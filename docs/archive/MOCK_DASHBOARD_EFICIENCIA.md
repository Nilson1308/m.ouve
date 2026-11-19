# 🧪 Mock de Dados - Dashboard de Eficiência

## 📋 Como Usar o Mock

Se o backend ainda não estiver pronto, você pode testar o dashboard localmente usando dados mockados.

---

## ✅ OPÇÃO 1: Mock Inline no Componente

### Modificação Temporária em `DashboardEficienciaView.vue`

Substitua a função `carregarDados()` por esta versão com mock:

```javascript
// src/views/backoffice/DashboardEficienciaView.vue

async function carregarDados() {
  carregando.value = true
  erro.value = null
  
  try {
    // ========================================
    // 🧪 MOCK: Comentar para usar API real
    // ========================================
    await new Promise(resolve => setTimeout(resolve, 1500)) // Simula delay de rede
    
    dados.value = {
      tma_global_horas: 132.5,
      tma_variacao: -12.5,
      taxa_sla_cumprido: 87.3,
      sla_variacao: 5.2,
      total_protocolos: 6423,
      total_no_prazo: 5189,
      total_vencido: 1234,
      meta_tma_dias: 5,
      ranking_unidades: [
        {
          id: 1,
          nome: "Secretaria de Mobilidade Urbana",
          sigla: "SEMOB",
          tma_horas: 197,
          total: 850,
          no_prazo: 510,
          vencido: 340
        },
        {
          id: 2,
          nome: "Secretaria de Infraestrutura",
          sigla: "SEINFRA",
          tma_horas: 170,
          total: 1200,
          no_prazo: 960,
          vencido: 240
        },
        {
          id: 3,
          nome: "Secretaria de Educação",
          sigla: "SEDUC",
          tma_horas: 96,
          total: 450,
          no_prazo: 405,
          vencido: 45
        },
        {
          id: 4,
          nome: "Secretaria de Saúde",
          sigla: "SESAU",
          tma_horas: 120,
          total: 980,
          no_prazo: 784,
          vencido: 196
        },
        {
          id: 5,
          nome: "Secretaria de Meio Ambiente",
          sigla: "SEMA",
          tma_horas: 88,
          total: 320,
          no_prazo: 280,
          vencido: 40
        },
        {
          id: 6,
          nome: "Secretaria de Cultura",
          sigla: "SECULT",
          tma_horas: 72,
          total: 180,
          no_prazo: 162,
          vencido: 18
        },
        {
          id: 7,
          nome: "Secretaria de Obras",
          sigla: "SEOBRAS",
          tma_horas: 156,
          total: 1100,
          no_prazo: 880,
          vencido: 220
        },
        {
          id: 8,
          nome: "Secretaria de Desenvolvimento Social",
          sigla: "SEDES",
          tma_horas: 104,
          total: 543,
          no_prazo: 489,
          vencido: 54
        }
      ]
    }
    
    ultimaAtualizacao.value = new Date()
    // ========================================
    // 🧪 FIM DO MOCK
    // ========================================
    
    // ========================================
    // 🌐 API REAL: Descomentar para usar backend
    // ========================================
    // const resposta = await dashboardService.getEficiencia()
    // dados.value = resposta
    // ultimaAtualizacao.value = new Date()
    // ========================================
    
  } catch (err) {
    erro.value = 'Erro ao carregar dados do dashboard'
    console.error('Erro ao carregar dashboard:', err)
  } finally {
    carregando.value = false
  }
}
```

---

## ✅ OPÇÃO 2: Mock via Interceptor Axios

Crie um arquivo de mock que intercepta chamadas ao Axios:

### 1. Criar arquivo de mock

```javascript
// src/mocks/dashboardMock.js

export const mockDashboardEficiencia = {
  tma_global_horas: 132.5,
  tma_variacao: -12.5,
  taxa_sla_cumprido: 87.3,
  sla_variacao: 5.2,
  total_protocolos: 6423,
  total_no_prazo: 5189,
  total_vencido: 1234,
  meta_tma_dias: 5,
  ranking_unidades: [
    {
      id: 1,
      nome: "Secretaria de Mobilidade Urbana",
      sigla: "SEMOB",
      tma_horas: 197,
      total: 850,
      no_prazo: 510,
      vencido: 340
    },
    {
      id: 2,
      nome: "Secretaria de Infraestrutura",
      sigla: "SEINFRA",
      tma_horas: 170,
      total: 1200,
      no_prazo: 960,
      vencido: 240
    },
    {
      id: 3,
      nome: "Secretaria de Educação",
      sigla: "SEDUC",
      tma_horas: 96,
      total: 450,
      no_prazo: 405,
      vencido: 45
    },
    {
      id: 4,
      nome: "Secretaria de Saúde",
      sigla: "SESAU",
      tma_horas: 120,
      total: 980,
      no_prazo: 784,
      vencido: 196
    },
    {
      id: 5,
      nome: "Secretaria de Meio Ambiente",
      sigla: "SEMA",
      tma_horas: 88,
      total: 320,
      no_prazo: 280,
      vencido: 40
    },
    {
      id: 6,
      nome: "Secretaria de Cultura",
      sigla: "SECULT",
      tma_horas: 72,
      total: 180,
      no_prazo: 162,
      vencido: 18
    },
    {
      id: 7,
      nome: "Secretaria de Obras",
      sigla: "SEOBRAS",
      tma_horas: 156,
      total: 1100,
      no_prazo: 880,
      vencido: 220
    },
    {
      id: 8,
      nome: "Secretaria de Desenvolvimento Social",
      sigla: "SEDES",
      tma_horas: 104,
      total: 543,
      no_prazo: 489,
      vencido: 54
    }
  ]
}

// Função para simular variação nos dados (opcional)
export function gerarDadosVariaveis() {
  return {
    ...mockDashboardEficiencia,
    tma_global_horas: 120 + Math.random() * 50, // 120-170h
    tma_variacao: -20 + Math.random() * 40,     // -20% a +20%
    taxa_sla_cumprido: 75 + Math.random() * 20, // 75-95%
    sla_variacao: -10 + Math.random() * 20,     // -10% a +10%
    ranking_unidades: mockDashboardEficiencia.ranking_unidades.map(u => ({
      ...u,
      tma_horas: u.tma_horas + Math.random() * 20 - 10,
      vencido: Math.floor(u.total * (0.1 + Math.random() * 0.3))
    }))
  }
}
```

### 2. Criar interceptor

```javascript
// src/mocks/mockInterceptor.js

import api from '@/services/api'
import { mockDashboardEficiencia } from './dashboardMock'

let mockEnabled = false

export function enableMocks() {
  if (mockEnabled) return
  
  mockEnabled = true
  
  // Intercepta apenas a rota do dashboard
  api.interceptors.request.use((config) => {
    if (config.url === '/backoffice/dashboard/eficiencia/') {
      return Promise.reject({
        config,
        _isMock: true
      })
    }
    return config
  })
  
  api.interceptors.response.use(null, (error) => {
    if (error._isMock && error.config.url === '/backoffice/dashboard/eficiencia/') {
      // Simula delay de rede
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: mockDashboardEficiencia,
            status: 200,
            statusText: 'OK',
            headers: {},
            config: error.config
          })
        }, 1500)
      })
    }
    return Promise.reject(error)
  })
  
  console.log('🧪 Mock do Dashboard de Eficiência ativado!')
}

export function disableMocks() {
  mockEnabled = false
  console.log('🌐 Usando API real')
}
```

### 3. Ativar no main.js

```javascript
// src/main.js

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// 🧪 MOCK: Ativar apenas em desenvolvimento
if (import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS === 'true') {
  import('./mocks/mockInterceptor').then(({ enableMocks }) => {
    enableMocks()
  })
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

### 4. Adicionar variável de ambiente

```bash
# .env.local

VITE_USE_MOCKS=true
```

---

## ✅ OPÇÃO 3: MSW (Mock Service Worker)

Para uma solução mais profissional e completa:

### 1. Instalar MSW

```bash
npm install --save-dev msw
```

### 2. Criar handlers

```javascript
// src/mocks/handlers.js

import { rest } from 'msw'
import { mockDashboardEficiencia } from './dashboardMock'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const handlers = [
  rest.get(`${baseURL}/backoffice/dashboard/eficiencia/`, (req, res, ctx) => {
    return res(
      ctx.delay(1500), // Simula latência de rede
      ctx.status(200),
      ctx.json(mockDashboardEficiencia)
    )
  })
]
```

### 3. Configurar MSW

```javascript
// src/mocks/browser.js

import { setupWorker } from 'msw'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)
```

### 4. Ativar no main.js

```javascript
// src/main.js

import { createApp } from 'vue'
import App from './App.vue'

async function prepare() {
  if (import.meta.env.DEV && import.meta.env.VITE_USE_MSW === 'true') {
    const { worker } = await import('./mocks/browser')
    await worker.start({
      onUnhandledRequest: 'bypass'
    })
    console.log('🧪 MSW ativado!')
  }
  return Promise.resolve()
}

prepare().then(() => {
  const app = createApp(App)
  // ... resto da configuração
})
```

---

## 📊 DADOS DE TESTE - CENÁRIOS

### Cenário 1: Desempenho Excelente

```javascript
{
  tma_global_horas: 72,        // 3 dias
  tma_variacao: -25,           // Melhorou 25%!
  taxa_sla_cumprido: 95.5,     // Excelente
  sla_variacao: 8,
  total_protocolos: 5000,
  total_no_prazo: 4775,
  total_vencido: 225,
  meta_tma_dias: 5,
  ranking_unidades: [
    // Todas com baixo % vencido
    { ..., vencido: 10, total: 500 }  // 2% vencido
  ]
}
```

**Insights esperados:**
- ✅ "Excelente desempenho! 95.5% de cumprimento de SLA."
- ✅ "TMA melhorou 25% em relação ao período anterior!"
- ✅ Nenhuma secretaria crítica

---

### Cenário 2: Situação Crítica

```javascript
{
  tma_global_horas: 240,       // 10 dias (acima da meta!)
  tma_variacao: 15,            // Piorou 15%
  taxa_sla_cumprido: 58.2,     // Crítico!
  sla_variacao: -12,
  total_protocolos: 8000,
  total_no_prazo: 4656,
  total_vencido: 3344,
  meta_tma_dias: 5,
  ranking_unidades: [
    // Várias com alto % vencido
    { ..., vencido: 450, total: 800 },  // 56% vencido! ⚠️
    { ..., vencido: 380, total: 700 }   // 54% vencido! ⚠️
  ]
}
```

**Insights esperados:**
- ⚠️ "TMA global de 10 dias está acima da meta. Considere revisar processos."
- ⚠️ "Taxa de SLA em 58.2% indica necessidade urgente de intervenção."
- ⚠️ "6 secretaria(s) com mais de 30% dos protocolos em atraso."
- ⚠️ Badges "Situação Crítica" em várias secretarias

---

### Cenário 3: Sem Gargalos

```javascript
{
  tma_global_horas: 96,        // 4 dias
  tma_variacao: -5,
  taxa_sla_cumprido: 92.0,
  sla_variacao: 3,
  total_protocolos: 3000,
  total_no_prazo: 2760,
  total_vencido: 240,
  meta_tma_dias: 5,
  ranking_unidades: [
    // Todas com baixíssimo % vencido
    { ..., vencido: 5, total: 500 },   // 1% vencido
    { ..., vencido: 8, total: 600 },   // 1.3% vencido
    { ..., vencido: 12, total: 700 }   // 1.7% vencido
  ]
}
```

**Resultado:**
- ✅ Nenhuma unidade crítica (0 com >30% vencido)
- ✅ Estado vazio no ranking:
  ```
  ✅ Nenhum Gargalo Identificado
  Todas as unidades estão cumprindo os prazos.
  ```

---

## 🧪 GERADOR DE DADOS ALEATÓRIOS

Para testes dinâmicos, use esta função:

```javascript
// src/mocks/dashboardMock.js

export function gerarDashboardAleatorio(severidade = 'medio') {
  const configs = {
    excelente: {
      tmaMin: 60,
      tmaMax: 90,
      slaMin: 88,
      slaMax: 97,
      vencidoMax: 15
    },
    medio: {
      tmaMin: 100,
      tmaMax: 150,
      slaMin: 75,
      slaMax: 88,
      vencidoMax: 30
    },
    critico: {
      tmaMin: 180,
      tmaMax: 300,
      slaMin: 50,
      slaMax: 70,
      vencidoMax: 55
    }
  }
  
  const cfg = configs[severidade]
  
  const tma = cfg.tmaMin + Math.random() * (cfg.tmaMax - cfg.tmaMin)
  const sla = cfg.slaMin + Math.random() * (cfg.slaMax - cfg.slaMin)
  const total = 5000 + Math.floor(Math.random() * 3000)
  const noPrazo = Math.floor(total * (sla / 100))
  
  const secretarias = [
    "Secretaria de Mobilidade Urbana",
    "Secretaria de Infraestrutura",
    "Secretaria de Educação",
    "Secretaria de Saúde",
    "Secretaria de Meio Ambiente",
    "Secretaria de Cultura",
    "Secretaria de Obras",
    "Secretaria de Desenvolvimento Social"
  ]
  
  return {
    tma_global_horas: tma,
    tma_variacao: -20 + Math.random() * 40,
    taxa_sla_cumprido: sla,
    sla_variacao: -10 + Math.random() * 20,
    total_protocolos: total,
    total_no_prazo: noPrazo,
    total_vencido: total - noPrazo,
    meta_tma_dias: 5,
    ranking_unidades: secretarias.map((nome, index) => {
      const total = 300 + Math.floor(Math.random() * 1000)
      const percentVencido = Math.random() * cfg.vencidoMax / 100
      const vencido = Math.floor(total * percentVencido)
      
      return {
        id: index + 1,
        nome,
        sigla: nome.split(' ').slice(2, 4).map(s => s[0]).join('') || 'SEC',
        tma_horas: tma + (Math.random() * 100 - 50),
        total,
        no_prazo: total - vencido,
        vencido
      }
    }).sort((a, b) => (b.vencido / b.total) - (a.vencido / a.total))
  }
}
```

**Uso:**

```javascript
// Gerar dados críticos
const dadosCriticos = gerarDashboardAleatorio('critico')

// Gerar dados excelentes
const dadosExcelentes = gerarDashboardAleatorio('excelente')

// Gerar dados médios
const dadosMedios = gerarDashboardAleatorio('medio')
```

---

## 🎯 TESTANDO TODOS OS ESTADOS

### Teste 1: Loading

```javascript
// Força estado de loading por 10 segundos
async function carregarDados() {
  carregando.value = true
  await new Promise(resolve => setTimeout(resolve, 10000))
  // ... resto do código
}
```

**Resultado:** Skeletons aparecem por 10 segundos

---

### Teste 2: Erro

```javascript
async function carregarDados() {
  carregando.value = true
  
  // Simula erro
  await new Promise(resolve => setTimeout(resolve, 1000))
  dados.value = null
  erro.value = 'Erro ao carregar dados'
  
  carregando.value = false
}
```

**Resultado:** Alerta amarelo aparece

---

### Teste 3: Sem Gargalos

```javascript
dados.value = {
  // ... outros dados
  ranking_unidades: [
    { ..., vencido: 5, total: 500 },   // 1% vencido
    { ..., vencido: 8, total: 600 },   // 1.3% vencido
  ]
}
```

**Resultado:** Estado vazio no ranking

---

## 🔄 ALTERNANDO ENTRE MOCK E API REAL

### Via Variável de Ambiente

```bash
# Usar mock
VITE_USE_MOCKS=true npm run dev

# Usar API real
VITE_USE_MOCKS=false npm run dev
```

### Via Console do Navegador

```javascript
// Ativar mock
localStorage.setItem('useMocks', 'true')
location.reload()

// Desativar mock
localStorage.removeItem('useMocks')
location.reload()
```

### Via Toggle na UI (Desenvolvimento)

Adicione um botão oculto:

```vue
<button 
  v-if="isDev"
  @click="toggleMock"
  class="fixed bottom-4 right-4 btn-secondary text-xs"
>
  {{ usandoMock ? '🧪 Mock' : '🌐 API' }}
</button>
```

---

**🧪 Mock completo para testes do Dashboard de Eficiência!**

*Escolha a opção que melhor se adapta ao seu fluxo de trabalho.*
