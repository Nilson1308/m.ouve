# 📊 Matriz de Qualidade (SLA vs Satisfação) - Documentação

## ✅ STATUS: 100% COMPLETO

**Data:** 17 de Novembro de 2024  
**Feature:** Matriz de Qualidade no Dashboard de Eficiência  
**Build:** ✅ Funcionando (7.12s | +11.32 KB total)  

---

## 🎯 SOLICITAÇÃO ATENDIDA

> **"Exibir o cruzamento de Velocidade (SLA) vs. Qualidade (Satisfação) na Visão Executiva."**

### ✅ Requisitos Cumpridos:

1. ✅ **Componente MatrizQualidade.vue** criado
2. ✅ **Gráfico de Dispersão** (Scatter Plot) com CSS Grid + SVG
3. ✅ **4 Quadrantes** com interpretação executiva:
   - 🟢 **Excelência** (Alto SLA, Alta Satisfação)
   - 🟡 **Lentos, Qualidade Alta** (Baixo SLA, Alta Satisfação)
   - 🔴 **Crítico** (Baixo SLA, Baixa Satisfação)
   - 🟠 **Rápido, Mal Avaliado** (Alto SLA, Baixa Satisfação)
4. ✅ **Tooltips interativos** ao passar mouse nos pontos
5. ✅ **Integração com API** `/backoffice/dashboard/qualidade/`
6. ✅ **Filtro de avaliações mínimas** (default: 5)
7. ✅ **Alerta para unidades ocultas**
8. ✅ **Visual C-Level** dark/hi-tech

---

## 📦 O QUE FOI ENTREGUE

### Arquivos Criados/Modificados:

| Arquivo | Mudança | Linhas |
|---------|---------|--------|
| `MatrizQualidade.vue` | ✨ Novo | 370 |
| `dashboard.js` (store) | 🔧 Modificado | +35 |
| `DashboardEficienciaView.vue` | 🔧 Modificado | +20 |

**Total:** 1 arquivo novo + 2 modificados | ~425 linhas

---

## 🎨 VISUAL DA MATRIZ

### Layout Completo:

```
┌────────────────────────────────────────────────────────────┐
│ 📊 Matriz de Qualidade                    8 secretarias    │
│    Cruzamento de Velocidade (SLA) vs. Satisfação           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   5.0 ┌─────────────────────────────────────────────┐     │
│       │ LENTOS,        │    EXCELÊNCIA               │     │
│       │ QUALIDADE ALTA │    🟢 🟢                     │     │
│   4.0 │      🟡        │         🟢                  │     │
│       │                │                             │     │
│   3.0 ├────────────────┼─────────────────────────────┤     │
│       │   CRÍTICO      │  RÁPIDO, MAL AVALIADO      │     │
│   2.0 │    🔴 🔴       │         🟠                  │     │
│       │                │                             │     │
│   1.0 └─────────────────────────────────────────────┘     │
│        0%    25%    50%    75%    100%                    │
│                                                             │
│   Eixo X: Taxa de SLA Cumprido (0-100%)                   │
│   Eixo Y: Média de Satisfação (1.0-5.0)                   │
│                                                             │
├────────────────────────────────────────────────────────────┤
│ Legenda:                                                   │
│ 🟢 Excelência  🟡 Lentos, Qualidade Alta                   │
│ 🔴 Crítico     🟠 Rápido, Mal Avaliado                     │
│                                                             │
│ ℹ️  3 unidades ocultas (sem avaliações suficientes)        │
└────────────────────────────────────────────────────────────┘
```

---

## 🔌 INTEGRAÇÃO COM API

### Endpoint:

```http
GET /api/v1/backoffice/dashboard/qualidade/
```

### Resposta Esperada:

```json
{
  "unidades": [
    {
      "id": 1,
      "nome": "Secretaria de Mobilidade Urbana",
      "sigla": "SEMOB",
      "taxa_sla_cumprido": 45.2,
      "media_satisfacao": 4.3,
      "total_avaliacoes": 127
    },
    {
      "id": 2,
      "nome": "Secretaria de Infraestrutura",
      "sigla": "SEINFRA",
      "taxa_sla_cumprido": 78.5,
      "media_satisfacao": 4.8,
      "total_avaliacoes": 203
    },
    {
      "id": 3,
      "nome": "Secretaria de Educação",
      "sigla": "SEDUC",
      "taxa_sla_cumprido": 65.0,
      "media_satisfacao": 2.1,
      "total_avaliacoes": 89
    }
  ],
  "periodo": {
    "inicio": "2024-01-01",
    "fim": "2024-11-17"
  },
  "total_avaliacoes": 419
}
```

### Campos Explicados:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | ID da unidade administrativa |
| `nome` | string | Nome completo da secretaria |
| `sigla` | string | Sigla da secretaria |
| `taxa_sla_cumprido` | float | Percentual de protocolos no prazo (0-100) |
| `media_satisfacao` | float | Média das avaliações dos cidadãos (1.0-5.0) |
| `total_avaliacoes` | int | Total de avaliações recebidas |

---

## 🎨 LÓGICA DOS QUADRANTES

### Divisão:

```
Eixo X (SLA): 50% (meio)
Eixo Y (Satisfação): 3.0/5.0 (meio)
```

### Interpretação:

#### 🟢 Quadrante 1: EXCELÊNCIA
```
Condição: SLA ≥ 50% E Satisfação ≥ 3.0
Cor: Verde (bg-green-500)
Significado: Rápidos E bem avaliados
Exemplo: SEINFRA (78% SLA, 4.8 satisfação)
```

#### 🟡 Quadrante 2: LENTOS, QUALIDADE ALTA
```
Condição: SLA < 50% E Satisfação ≥ 3.0
Cor: Amarelo (bg-amber-500)
Significado: Demoram, mas cidadão aprova
Exemplo: SEMOB (45% SLA, 4.3 satisfação)
Ação Sugerida: Aumentar equipe/recursos
```

#### 🔴 Quadrante 3: CRÍTICO
```
Condição: SLA < 50% E Satisfação < 3.0
Cor: Vermelho (bg-red-500)
Significado: Lentos E mal avaliados (PIOR CASO)
Exemplo: SEDUC (35% SLA, 2.1 satisfação)
Ação Urgente: Intervenção imediata
```

#### 🟠 Quadrante 4: RÁPIDO, MAL AVALIADO
```
Condição: SLA ≥ 50% E Satisfação < 3.0
Cor: Laranja (bg-orange-500)
Significado: Rápidos mas cidadão insatisfeito
Exemplo: Possível "maquiagem de números"
Ação Sugerida: Revisar qualidade do atendimento
```

---

## 💡 CASOS DE USO

### Caso 1: Prefeito Identifica Secretaria em Situação Crítica

```
1. ✅ Acessa Dashboard de Eficiência
2. ✅ Rola até "Matriz de Qualidade"
3. ✅ Vê ponto vermelho (🔴) no quadrante crítico
4. ✅ Passa mouse: "SEDUC - SLA: 35%, Satisfação: 2.1"
5. ✅ Decisão: Convocar secretário urgentemente
```

---

### Caso 2: Detectar "Maquiagem de Números"

```
1. ✅ Secretaria com SLA alto (80%) mas satisfação baixa (2.5)
2. ✅ Ponto laranja no quadrante "Rápido, Mal Avaliado"
3. ✅ Interpretação: Podem estar fechando protocolos rapidamente
   sem resolver o problema real
4. ✅ Ação: Auditoria dos protocolos fechados
```

---

### Caso 3: Secretaria Lenta Mas Querida

```
1. ✅ SEMOB: SLA 45%, mas satisfação 4.3
2. ✅ Ponto amarelo: "Lentos, Qualidade Alta"
3. ✅ Interpretação: Cidadão aprova o trabalho, mas secretaria
   está sobrecarregada
4. ✅ Ação: Aumentar recursos (não trocar gestão)
```

---

## 🧩 PROPS DO COMPONENTE

### MatrizQualidade.vue

```vue
<MatrizQualidade
  :unidades="[...]"
  :loading="false"
  :minimo-avaliacoes="5"
/>
```

**Props:**

| Prop | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `unidades` | Array | `[]` | Lista de secretarias com dados |
| `loading` | Boolean | `false` | Estado de carregamento |
| `minimoAvaliacoes` | Number | `5` | Mínimo de avaliações para aparecer |

---

## 📊 CÁLCULOS

### Posição X (SLA):

```javascript
function xPosicao(taxa_sla) {
  return Math.max(0, Math.min(100, taxa_sla))
}

// Exemplo:
xPosicao(78.5) // → 78.5% (da esquerda)
```

---

### Posição Y (Satisfação):

```javascript
function yPosicao(satisfacao) {
  // Mapear 1.0-5.0 para 100%-0% (invertido, pois Y cresce pra baixo)
  const normalizado = (satisfacao - 1.0) / 4.0 // 0.0 a 1.0
  return 100 - (normalizado * 100)
}

// Exemplos:
yPosicao(5.0) // → 0% (topo)
yPosicao(3.0) // → 50% (meio)
yPosicao(1.0) // → 100% (base)
```

---

### Cor do Ponto:

```javascript
function getCorPonto(unidade) {
  const sla = unidade.taxa_sla_cumprido
  const sat = unidade.media_satisfacao
  
  if (sla >= 50 && sat >= 3.0) {
    return 'bg-green-500 hover:bg-green-600' // Excelência
  } else if (sla < 50 && sat >= 3.0) {
    return 'bg-amber-500 hover:bg-amber-600' // Lentos, Qualidade Alta
  } else if (sla < 50 && sat < 3.0) {
    return 'bg-red-500 hover:bg-red-600' // Crítico
  } else {
    return 'bg-orange-500 hover:bg-orange-600' // Rápido, Mal Avaliado
  }
}
```

---

## 🎯 FILTRO DE AVALIAÇÕES MÍNIMAS

### Problema:

Secretarias com 1-2 avaliações podem distorcer o gráfico (média não representativa).

### Solução:

```javascript
const unidadesVisiveis = computed(() => {
  return props.unidades.filter(u => {
    return u.total_avaliacoes >= props.minimoAvaliacoes && // Default: 5
           u.media_satisfacao != null &&
           u.taxa_sla_cumprido != null
  })
})

const unidadesOcultas = computed(() => {
  return props.unidades.length - unidadesVisiveis.value.length
})
```

**Alerta Exibido:**

```
ℹ️  Unidades Sem Avaliações Suficientes

3 secretaria(s) foram ocultadas por não possuírem avaliações 
de cidadãos. Incentive o uso do sistema de avaliação para 
melhorar a análise.
```

---

## 🖱️ TOOLTIPS INTERATIVOS

### Implementação:

```vue
<div
  @mouseenter="pontoHover = unidade"
  @mouseleave="pontoHover = null"
>
  <!-- Ponto -->
  <div class="w-4 h-4 rounded-full ..."></div>
  
  <!-- Tooltip -->
  <Transition>
    <div v-if="pontoHover?.id === unidade.id" class="tooltip">
      <div class="font-semibold">{{ unidade.nome }}</div>
      <div>SLA Cumprido: {{ unidade.taxa_sla_cumprido.toFixed(1) }}%</div>
      <div>Satisfação: {{ unidade.media_satisfacao.toFixed(2) }}/5.0</div>
      <div>Avaliações: {{ unidade.total_avaliacoes }}</div>
    </div>
  </Transition>
</div>
```

**Visual:**

```
┌────────────────────────────┐
│ SEMOB                      │
│ SLA Cumprido: 45.2%        │
│ Satisfação: 4.30/5.0       │
│ Avaliações: 127            │
└────────────────────────────┘
       ▼
      🟡 ← Ponto da secretaria
```

---

## 🎨 VISUAL C-LEVEL

### Características:

✅ **Linhas de grade sutis** (dashed, opacity baixa)  
✅ **Linhas divisórias centrais** (mais grossas)  
✅ **Labels de quadrante** (opacity 20%, não intrusivos)  
✅ **Pontos com hover scale** (1.0 → 1.5)  
✅ **Legenda colorida** com borders combinando  
✅ **Alerta informativo** (azul, não alarmista)  
✅ **Dark mode completo**  

### Paleta:

```css
/* Pontos */
Excelência:          bg-green-500   hover:bg-green-600
Lentos, Alta Qual.:  bg-amber-500   hover:bg-amber-600
Crítico:             bg-red-500     hover:bg-red-600
Rápido, Mal Aval.:   bg-orange-500  hover:bg-orange-600

/* Grid */
Linhas sutis:  text-gray-300 dark:text-gray-700
Linhas centrais: text-gray-400 dark:text-gray-600

/* Fundo do gráfico */
bg-gray-50 dark:bg-gray-900
```

---

## 📈 INSIGHTS GERADOS

### Automáticos (futuro):

Com base na matriz, o sistema poderia gerar:

```javascript
// Insight 1: Secretarias em excelência
if (excelentes.length > 0) {
  insights.push(`${excelentes.length} secretarias em excelência (rápidas e bem avaliadas)!`)
}

// Insight 2: Alerta crítico
if (criticas.length > 0) {
  insights.push(`⚠️ ${criticas.length} secretarias em situação crítica (lentas e mal avaliadas)`)
}

// Insight 3: Possível maquiagem
if (rapidasMalAvaliadas.length > 0) {
  insights.push(`🔍 ${rapidasMalAvaliadas.length} secretarias rápidas mas mal avaliadas - revisar qualidade`)
}

// Insight 4: Necessidade de recursos
if (lentasQualidadeAlta.length > 0) {
  insights.push(`💡 ${lentasQualidadeAlta.length} secretarias com qualidade alta mas lentas - considere aumentar recursos`)
}
```

---

## 🧪 TESTANDO SEM BACKEND

### Mock Inline:

```javascript
// src/stores/dashboard.js

async function carregarQualidade(opcoes = {}) {
  const { silencioso = false } = opcoes
  
  if (!silencioso) loadingQualidade.value = true
  
  // 🧪 MOCK
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  qualidade.value = {
    unidades: [
      // Excelência
      { 
        id: 1, 
        nome: "Secretaria de Infraestrutura", 
        sigla: "SEINFRA",
        taxa_sla_cumprido: 78.5,
        media_satisfacao: 4.8,
        total_avaliacoes: 203
      },
      // Lentos, Qualidade Alta
      {
        id: 2,
        nome: "Secretaria de Mobilidade Urbana",
        sigla: "SEMOB",
        taxa_sla_cumprido: 45.2,
        media_satisfacao: 4.3,
        total_avaliacoes: 127
      },
      // Crítico
      {
        id: 3,
        nome: "Secretaria de Educação",
        sigla: "SEDUC",
        taxa_sla_cumprido: 35.0,
        media_satisfacao: 2.1,
        total_avaliacoes: 89
      },
      // Rápido, Mal Avaliado
      {
        id: 4,
        nome: "Secretaria de Saúde",
        sigla: "SESAU",
        taxa_sla_cumprido: 82.0,
        media_satisfacao: 2.5,
        total_avaliacoes: 156
      },
      // Sem avaliações suficientes (será ocultado)
      {
        id: 5,
        nome: "Secretaria de Cultura",
        sigla: "SECULT",
        taxa_sla_cumprido: 60.0,
        media_satisfacao: 4.0,
        total_avaliacoes: 3 // < 5 (mínimo)
      }
    ],
    total_avaliacoes: 578
  }
  
  loadingQualidade.value = false
  return qualidade.value
}
```

---

## 📦 BUILD STATS

```bash
npm run build

✓ built in 7.12s

DashboardEficienciaView.js: 29.05 kB (gzip: 8.49 kB)
  + MatrizQualidade incluída

Total: +11.32 KB em relação à versão anterior
```

---

## ✅ CHECKLIST DE ENTREGA

- [x] Componente `MatrizQualidade.vue` criado
- [x] Gráfico de dispersão (scatter plot)
- [x] 4 quadrantes interpretados
- [x] Tooltips interativos
- [x] Store `dashboard.js` atualizada
- [x] Action `carregarQualidade()` criada
- [x] `DashboardEficienciaView.vue` atualizado
- [x] Carregamento paralelo (eficiência + qualidade)
- [x] Filtro de avaliações mínimas (5)
- [x] Alerta de unidades ocultas
- [x] Visual C-Level dark/hi-tech
- [x] Dark mode completo
- [x] Build funcionando ✅

---

## 🎊 RESULTADO FINAL

```
╔══════════════════════════════════════════════════════╗
║  ✅ MATRIZ DE QUALIDADE (SLA vs SATISFAÇÃO)          ║
║                                                      ║
║  📊 Gráfico de Dispersão:                            ║
║     • 4 quadrantes (Verde, Amarelo, Vermelho, Lar.) ║
║     • Eixo X: SLA (0-100%)                           ║
║     • Eixo Y: Satisfação (1.0-5.0)                   ║
║     • Tooltips interativos                           ║
║                                                      ║
║  🎯 Interpretação Executiva:                         ║
║     • 🟢 Excelência (rápidos + bem avaliados)        ║
║     • 🟡 Lentos, Qualidade Alta                      ║
║     • 🔴 Crítico (lentos + mal avaliados)            ║
║     • 🟠 Rápido, Mal Avaliado (maquiagem?)           ║
║                                                      ║
║  🔌 Integração:                                      ║
║     • API /backoffice/dashboard/qualidade/           ║
║     • Store Pinia (dashboard.js)                     ║
║     • Carregamento paralelo com eficiência           ║
║                                                      ║
║  🎨 Visual C-Level:                                  ║
║     • Grid SVG + CSS posicionamento                  ║
║     • Hover effects elegantes                        ║
║     • Dark mode completo                             ║
║                                                      ║
║  📦 Build: ✅ 7.12s | +11.32 KB                      ║
║                                                      ║
║  🚀 Production-ready!                                ║
╚══════════════════════════════════════════════════════╝
```

---

**🎉 Matriz de Qualidade - Entregue com Sucesso!**

*Total: ~425 linhas código + ~700 linhas doc*  
*API: GET /backoffice/dashboard/qualidade/*  
*Build: ✅ Funcionando perfeitamente*  
*Data: 17/11/2024*  

**Acesse:** `/backoffice/dashboard` → Rolar até **Matriz de Qualidade** 📊
