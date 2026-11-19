# 🧪 Mock de Dados - Dashboard de Mapa GIS

## 📋 Como Usar o Mock

Se o backend ainda não estiver pronto, você pode testar o mapa localmente usando dados mockados.

---

## ✅ OPÇÃO 1: Mock Inline na Store

### Modificação Temporária em `src/stores/dashboard.js`

Substitua a função `carregarMapaCalor()` por esta versão com mock:

```javascript
// src/stores/dashboard.js

async function carregarMapaCalor(filtros = null) {
  loadingMapaCalor.value = true
  erro.value = null
  
  try {
    // ========================================
    // 🧪 MOCK: Comentar para usar API real
    // ========================================
    await new Promise(resolve => setTimeout(resolve, 1500)) // Simula delay
    
    const quantidade = 150 // Número de pontos no mapa
    mapaCalor.value = {
      coordenadas: gerarCoordenadasMogiDasCruzes(quantidade),
      periodo: {
        inicio: filtros?.dataInicial || '2024-01-01',
        fim: filtros?.dataFinal || '2024-11-17'
      },
      total: quantidade
    }
    
    return mapaCalor.value
    // ========================================
    // 🧪 FIM DO MOCK
    // ========================================
    
    // ========================================
    // 🌐 API REAL: Descomentar para usar backend
    // ========================================
    // const params = {}
    // const f = filtros || filtrosMapaCalor.value
    // if (f.dataInicial) params.data_inicial = f.dataInicial
    // if (f.dataFinal) params.data_final = f.dataFinal
    // if (f.status && f.status.length > 0) params.status = f.status.join(',')
    // if (f.servico) params.servico = f.servico
    // 
    // const { data } = await api.get('/backoffice/dashboard/mapa-calor/', { params })
    // mapaCalor.value = data
    // return data
    // ========================================
    
  } catch (err) {
    erro.value = getErrorMessage(err, 'Erro ao carregar mapa de calor')
    console.error('Erro ao carregar mapa de calor:', err)
    throw err
  } finally {
    loadingMapaCalor.value = false
  }
}

// ========================================
// 🧪 FUNÇÃO DE MOCK: Gerar Coordenadas
// ========================================
function gerarCoordenadasMogiDasCruzes(quantidade) {
  const coordenadas = []
  
  // Centro de Mogi das Cruzes
  const centro = { lat: -23.5222, lng: -46.1883 }
  
  // Bounds aproximados de Mogi
  const bounds = {
    minLat: -23.55,
    maxLat: -23.48,
    minLng: -46.22,
    maxLng: -46.15
  }
  
  // Criar clusters (áreas de concentração)
  const clusters = [
    { lat: -23.5222, lng: -46.1883, densidade: 'alta' },   // Centro
    { lat: -23.5150, lng: -46.1950, densidade: 'media' },  // Zona Norte
    { lat: -23.5300, lng: -46.1800, densidade: 'baixa' },  // Zona Sul
    { lat: -23.5180, lng: -46.1750, densidade: 'media' },  // Zona Leste
    { lat: -23.5280, lng: -46.1950, densidade: 'alta' }    // Zona Oeste
  ]
  
  for (let i = 0; i < quantidade; i++) {
    // Escolher cluster aleatório
    const cluster = clusters[Math.floor(Math.random() * clusters.length)]
    
    // Dispersão baseada na densidade
    const dispersao = {
      alta: 0.008,   // Pontos bem concentrados
      media: 0.015,  // Dispersão média
      baixa: 0.025   // Pontos espalhados
    }[cluster.densidade]
    
    // Gerar coordenada próxima ao cluster
    const latitude = cluster.lat + (Math.random() - 0.5) * dispersao
    const longitude = cluster.lng + (Math.random() - 0.5) * dispersao
    
    // Garantir que está dentro dos bounds
    if (
      latitude >= bounds.minLat && 
      latitude <= bounds.maxLat &&
      longitude >= bounds.minLng && 
      longitude <= bounds.maxLng
    ) {
      // Intensidade baseada na densidade
      const intensidadeBase = {
        alta: [5, 6, 7, 8, 9, 10],
        media: [3, 4, 5, 6],
        baixa: [1, 2, 3]
      }[cluster.densidade]
      
      const intensidade = intensidadeBase[
        Math.floor(Math.random() * intensidadeBase.length)
      ]
      
      coordenadas.push({
        latitude,
        longitude,
        intensidade
      })
    }
  }
  
  return coordenadas
}
```

---

## ✅ OPÇÃO 2: Mock com Dados Fixos

Para testes mais previsíveis, use coordenadas fixas:

```javascript
// src/stores/dashboard.js

function gerarCoordenadasFixas() {
  return [
    // Centro de Mogi (alta densidade)
    { latitude: -23.5222, longitude: -46.1883, intensidade: 10 },
    { latitude: -23.5225, longitude: -46.1880, intensidade: 9 },
    { latitude: -23.5220, longitude: -46.1885, intensidade: 8 },
    { latitude: -23.5218, longitude: -46.1888, intensidade: 7 },
    
    // Zona Norte (média densidade)
    { latitude: -23.5150, longitude: -46.1950, intensidade: 5 },
    { latitude: -23.5155, longitude: -46.1945, intensidade: 4 },
    { latitude: -23.5145, longitude: -46.1955, intensidade: 6 },
    
    // Zona Sul (baixa densidade)
    { latitude: -23.5300, longitude: -46.1800, intensidade: 2 },
    { latitude: -23.5305, longitude: -46.1795, intensidade: 1 },
    { latitude: -23.5295, longitude: -46.1805, intensidade: 3 },
    
    // Zona Leste
    { latitude: -23.5180, longitude: -46.1750, intensidade: 4 },
    { latitude: -23.5185, longitude: -46.1745, intensidade: 5 },
    
    // Zona Oeste (crítica)
    { latitude: -23.5280, longitude: -46.1950, intensidade: 9 },
    { latitude: -23.5285, longitude: -46.1955, intensidade: 10 },
    { latitude: -23.5275, longitude: -46.1945, intensidade: 8 }
  ]
}
```

---

## 🎯 CENÁRIOS DE TESTE

### Cenário 1: Alta Densidade (Crítico)

**Objetivo:** Testar visualização de zona crítica

```javascript
function cenarioCritico() {
  const centro = { lat: -23.5222, lng: -46.1883 }
  const coords = []
  
  // Gerar 50 pontos concentrados no centro com alta intensidade
  for (let i = 0; i < 50; i++) {
    coords.push({
      latitude: centro.lat + (Math.random() - 0.5) * 0.01,
      longitude: centro.lng + (Math.random() - 0.5) * 0.01,
      intensidade: 8 + Math.floor(Math.random() * 3) // 8-10
    })
  }
  
  return coords
}
```

**Resultado Esperado:**
- ✅ Área vermelha concentrada no centro
- ✅ Badge contador mostra "50 ocorrências"
- ✅ FitBounds centraliza na área crítica

---

### Cenário 2: Dispersão Uniforme

**Objetivo:** Testar cobertura total do município

```javascript
function cenarioDispersao() {
  const coords = []
  const bounds = {
    minLat: -23.55,
    maxLat: -23.48,
    minLng: -46.22,
    maxLng: -46.15
  }
  
  // Distribuir 100 pontos uniformemente
  for (let i = 0; i < 100; i++) {
    coords.push({
      latitude: bounds.minLat + Math.random() * (bounds.maxLat - bounds.minLat),
      longitude: bounds.minLng + Math.random() * (bounds.maxLng - bounds.minLng),
      intensidade: 1 + Math.floor(Math.random() * 5) // 1-5
    })
  }
  
  return coords
}
```

**Resultado Esperado:**
- ✅ Heatmap cobre toda a cidade
- ✅ Cores predominantemente verde/amarelo
- ✅ Zoom ajusta para mostrar todo o município

---

### Cenário 3: Múltiplos Clusters

**Objetivo:** Testar várias zonas problemáticas

```javascript
function cenarioClusters() {
  const coords = []
  
  const zonas = [
    { nome: 'Centro', lat: -23.5222, lng: -46.1883, criticidade: 'alta' },
    { nome: 'Brás Cubas', lat: -23.5100, lng: -46.1950, criticidade: 'media' },
    { nome: 'Vila Oliveira', lat: -23.5350, lng: -46.1850, criticidade: 'baixa' },
    { nome: 'Jundiapeba', lat: -23.5180, lng: -46.1700, criticidade: 'alta' }
  ]
  
  zonas.forEach(zona => {
    const quantidade = zona.criticidade === 'alta' ? 30 : 
                       zona.criticidade === 'media' ? 20 : 10
    
    const intensidade = zona.criticidade === 'alta' ? [8, 9, 10] :
                        zona.criticidade === 'media' ? [4, 5, 6] : [1, 2, 3]
    
    for (let i = 0; i < quantidade; i++) {
      coords.push({
        latitude: zona.lat + (Math.random() - 0.5) * 0.01,
        longitude: zona.lng + (Math.random() - 0.5) * 0.01,
        intensidade: intensidade[Math.floor(Math.random() * intensidade.length)]
      })
    }
  })
  
  return coords
}
```

**Resultado Esperado:**
- ✅ 4 zonas distintas visíveis
- ✅ Centro e Jundiapeba em vermelho
- ✅ Brás Cubas em amarelo
- ✅ Vila Oliveira em verde

---

### Cenário 4: Dados Vazios

**Objetivo:** Testar estado vazio

```javascript
function cenarioVazio() {
  return []
}
```

**Resultado Esperado:**
- ✅ Mapa mostra centro de Mogi
- ✅ Overlay com mensagem "Nenhuma Ocorrência Encontrada"
- ✅ Ícone de mapa cinza grande
- ✅ Texto explicativo

---

### Cenário 5: Ponto Único

**Objetivo:** Testar visualização de ocorrência isolada

```javascript
function cenarioPontoUnico() {
  return [
    { latitude: -23.5222, longitude: -46.1883, intensidade: 5 }
  ]
}
```

**Resultado Esperado:**
- ✅ Mapa centraliza no ponto
- ✅ Zoom: 15
- ✅ Heatmap mostra círculo amarelo/verde
- ✅ Badge: "1 ocorrência"

---

## 🔄 ALTERNANDO ENTRE MOCK E API

### Via Variável de Ambiente

```bash
# .env.local

# Usar mock
VITE_USE_MOCKS=true

# Usar API real
VITE_USE_MOCKS=false
```

```javascript
// src/stores/dashboard.js

async function carregarMapaCalor(filtros = null) {
  loadingMapaCalor.value = true
  
  // Decidir entre mock e API
  if (import.meta.env.VITE_USE_MOCKS === 'true') {
    // Mock
    await new Promise(resolve => setTimeout(resolve, 1500))
    mapaCalor.value = {
      coordenadas: gerarCoordenadasMogiDasCruzes(150),
      total: 150
    }
  } else {
    // API real
    const { data } = await api.get('/backoffice/dashboard/mapa-calor/')
    mapaCalor.value = data
  }
  
  loadingMapaCalor.value = false
}
```

---

## 🎮 CONTROLE VIA CONSOLE

Para desenvolvedores, adicione funções globais para teste:

```javascript
// src/stores/dashboard.js

// Expor funções de mock no window (apenas em dev)
if (import.meta.env.DEV) {
  window.mockDashboard = {
    critico: () => gerarCoordenadasMogiDasCruzes(50, 'alta'),
    disperso: () => gerarCoordenadasMogiDasCruzes(100, 'media'),
    clusters: () => cenarioClusters(),
    vazio: () => [],
    pontoUnico: () => [{ latitude: -23.5222, longitude: -46.1883, intensidade: 5 }]
  }
}
```

**Uso no Console:**

```javascript
// No navegador (F12 → Console)

// Aplicar cenário crítico
const store = useDashboardStore()
store.mapaCalor = { 
  coordenadas: window.mockDashboard.critico(),
  total: 50
}

// Aplicar cenário vazio
store.mapaCalor = { 
  coordenadas: window.mockDashboard.vazio(),
  total: 0
}
```

---

## 📊 GERANDO DADOS REALISTAS

### Baseado em Bairros Reais de Mogi:

```javascript
const bairrosMogi = [
  { nome: 'Centro', lat: -23.5222, lng: -46.1883, densidade: 0.8 },
  { nome: 'Vila Mogilar', lat: -23.5100, lng: -46.1950, densidade: 0.6 },
  { nome: 'Brás Cubas', lat: -23.5180, lng: -46.2000, densidade: 0.7 },
  { nome: 'Jundiapeba', lat: -23.5180, lng: -46.1700, densidade: 0.5 },
  { nome: 'Cesar de Souza', lat: -23.5350, lng: -46.1750, densidade: 0.4 },
  { nome: 'Vila Oliveira', lat: -23.5400, lng: -46.1850, densidade: 0.3 }
]

function gerarPorBairros(totalOcorrencias) {
  const coords = []
  
  bairrosMogi.forEach(bairro => {
    const quantidade = Math.floor(totalOcorrencias * bairro.densidade)
    
    for (let i = 0; i < quantidade; i++) {
      coords.push({
        latitude: bairro.lat + (Math.random() - 0.5) * 0.02,
        longitude: bairro.lng + (Math.random() - 0.5) * 0.02,
        intensidade: Math.floor(bairro.densidade * 10) + Math.floor(Math.random() * 3)
      })
    }
  })
  
  return coords
}
```

**Uso:**

```javascript
const coords = gerarPorBairros(200) // 200 ocorrências distribuídas
// Centro: 160 (80%)
// Vila Mogilar: 120 (60%)
// Brás Cubas: 140 (70%)
// ...
```

---

## 🧪 TESTE DE PERFORMANCE

### Estresse: 1000 Pontos

```javascript
function testeEstresse() {
  const coords = []
  
  for (let i = 0; i < 1000; i++) {
    coords.push({
      latitude: -23.55 + Math.random() * 0.07,
      longitude: -46.22 + Math.random() * 0.07,
      intensidade: 1 + Math.floor(Math.random() * 10)
    })
  }
  
  return coords
}
```

**Resultado Esperado:**
- ✅ Renderiza em < 2 segundos
- ✅ Heatmap smooth (sem lag)
- ✅ Zoom/pan fluidos

---

## 🎯 CHECKLIST DE TESTES

### Testes Visuais:

- [ ] Heatmap renderiza corretamente
- [ ] Gradiente de cores (verde → amarelo → vermelho)
- [ ] Badge contador mostra valor correto
- [ ] Legenda posicionada corretamente
- [ ] Painel de filtros sobrepõe o mapa
- [ ] Dark mode funcionando

### Testes Funcionais:

- [ ] Aplicar filtros recarrega o mapa
- [ ] Limpar filtros reseta tudo
- [ ] FitBounds ajusta zoom corretamente
- [ ] Loading overlay aparece/desaparece
- [ ] Estado vazio mostra mensagem
- [ ] Toast de erro funciona

### Testes Responsivos:

- [ ] Desktop: painel sidebar esquerda
- [ ] Mobile: painel drawer bottom
- [ ] Botão toggle funciona (mobile)
- [ ] Mapa ocupa 100% da altura

---

## 💡 DICAS DE DEBUGGING

### 1. Ver Coordenadas no Console:

```javascript
// src/components/backoffice/dashboard/MapaCalorExecutivo.vue

watch(() => props.coordenadas, (novas) => {
  console.log('🗺️ Coordenadas recebidas:', novas.length)
  console.table(novas.slice(0, 10)) // Primeiras 10
})
```

### 2. Monitorar Bounds:

```javascript
function ajustarBounds(pontos) {
  const bounds = L.latLngBounds(latLngs)
  console.log('📐 Bounds:', bounds.toBBoxString())
  
  mapa.fitBounds(bounds)
}
```

### 3. Verificar Plugin Heatmap:

```javascript
import L from 'leaflet'
import 'leaflet.heat'

console.log('🔥 Heatmap plugin:', L.heatLayer ? 'OK' : 'ERRO')
```

---

**🧪 Mock completo para testes do Dashboard de Mapa GIS!**

*Escolha a opção que melhor se adapta ao seu fluxo de trabalho e comece a testar!*
