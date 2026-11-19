# 🎨 Dashboard de Eficiência - Guia Visual

## 📐 Layout Completo (Desktop 1920x1080)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR (256px)          │ HEADER (full width)                                      │
│ ═══════════════          ├──────────────────────────────────────────────────────────┤
│                          │                                                           │
│ 🏛️ Ouv.IA                │ Dashboard de Eficiência                          [↻]     │
│ Backoffice               │                                                           │
│                          │                                                           │
│ ┌───────────────────┐    │ 📊 Dashboard de Eficiência                               │
│ │📊 Visão Executiva │◄── │ Visão executiva de desempenho operacional e SLA          │
│ └───────────────────┘    │ 🕐 Última atualização: 17/11/24, 08:45                   │
│ 📋 Mesa de Trabalho      │                                                           │
│ 🏢 Painel Setorial       ├───────────────────────────────────────────────────────────┤
│ 🔔 Notificações          │                                                           │
│                          │ ┌──────────────────┐ ┌──────────────────┐               │
│ ─────────────────        │ │ 🕐 TMA GLOBAL    │ │ ✅ TAXA SLA      │               │
│                          │ │ Tempo Médio de   │ │ Cumprido         │               │
│ 📊 Relatórios            │ │ Atendimento      │ │                  │               │
│ ⚙️  Configurações        │ │                  │ │ Protocolos no    │               │
│                          │ │ Meta: 5 dias  ↓12│ │ prazo         ↑5%│               │
│                          │ │                  │ │                  │               │
│ ┌───────────────────┐    │ │  5d 12h          │ │    87.3%         │               │
│ │ JO                │    │ │                  │ │ 5,189 de 6,423   │               │
│ │ João da Silva     │    │ │ 🏁 Meta: 5 dias  │ │ protocolos       │               │
│ │ Servidor          │    │ └──────────────────┘ └──────────────────┘               │
│ └───────────────────┘    │                                                           │
│                          │ ┌──────────────────┐ ┌──────────────────┐               │
│                          │ │ ⚠️  VENCIDOS     │ │ ⚠️  GARGALOS     │               │
│                          │ │ Acima do SLA     │ │ Unidades         │               │
│                          │ │                  │ │ Críticas         │               │
│                          │ │                  │ │                  │               │
│                          │ │                  │ │ 8 unidades       │               │
│                          │ │   1,234          │ │ monitoradas      │               │
│                          │ │                  │ │                  │               │
│                          │ │ 19.2% do total   │ │      3           │               │
│                          │ └──────────────────┘ └──────────────────┘               │
│                          │                                                           │
│                          ├───────────────────────────────────────────────────────────┤
│                          │                                                           │
│                          │ ┌──────────────┐  ┌────────────────────────────────────┐│
│                          │ │🥧 DISTRIBUIÇÃO│  │ ⚠️  Gargalos por Secretaria        ││
│                          │ ├──────────────┤  │ Unidades com maior volume SLA venc.││
│                          │ │              │  ├────────────────────────────────────┤│
│                          │ │              │  │ 1  SEMOB                  TMA: 8d 5h││
│                          │ │    6,423     │  │    Secretaria Mobilidade Urbana    ││
│                          │ │    Total     │  │    ● No prazo: 510  ● Vencido: 340 ││
│                          │ │              │  │    ████████░░ 60% | ████░ 40%      ││
│                          │ │              │  │    60.0% cumprindo | 40.0% atraso  ││
│                          │ │ ● No Prazo   │  │    ⚠️  Situação Crítica            ││
│                          │ │   5,189      │  ├────────────────────────────────────┤│
│                          │ │              │  │ 2  SEINFRA                TMA: 7d 2h││
│                          │ │ ● Vencido    │  │    Secretaria de Infraestrutura    ││
│                          │ │   1,234      │  │    ● No prazo: 960  ● Vencido: 240 ││
│                          │ │              │  │    ████████████░░ 80% | ██░ 20%    ││
│                          │ └──────────────┘  │    80.0% cumprindo | 20.0% atraso  ││
│                          │                   ├────────────────────────────────────┤│
│                          │                   │ 3  SEDUC                   TMA: 4d  ││
│                          │                   │    Secretaria de Educação          ││
│                          │                   │    ● No prazo: 405  ● Vencido: 45  ││
│                          │                   │    ██████████████░░ 90% | █░ 10%   ││
│                          │                   │    90.0% cumprindo | 10.0% atraso  ││
│                          │                   └────────────────────────────────────┘│
│                          │                                                           │
│                          ├───────────────────────────────────────────────────────────┤
│                          │ 💡 Insights Automáticos                                  │
│                          │ • TMA melhorou 12% em relação ao período anterior!       │
│                          │ • 3 secretaria(s) com mais de 30% dos protocolos atraso  │
│                          └───────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 ANATOMIA DO KPI CARD

### Card: TMA Global

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  ┌────┐  TMA Global                        ↓ 12% │ ← Variação (verde)
│  │ 🕐 │  Tempo Médio de Atendimento               │
│  └────┘  (subtitle)                               │
│  ╭────╮                                            │
│  │icon│                                            │
│  ╰────╯                                            │
│                                                    │
│         5d 12h                                     │ ← Valor principal (3xl, bold)
│                                                    │
│  🏁 Meta: 5 dias                                   │ ← Contexto
│                                                    │
└────────────────────────────────────────────────────┘
```

**Cores:**

```css
/* Header */
Icon Background:  bg-primary-100 dark:bg-primary-900/20
Icon:             text-primary-600 dark:text-primary-400
Título:           text-gray-600 dark:text-gray-400 (sm, medium)
Subtítulo:        text-gray-500 dark:text-gray-500 (xs)

/* Variação */
Melhora:   bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400
Piora:     bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400

/* Valor */
Principal:        text-gray-900 dark:text-white (3xl, bold)

/* Contexto */
Texto:            text-gray-600 dark:text-gray-400 (sm)
```

---

### Card: Taxa SLA Cumprido

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  ┌────┐  Taxa de SLA Cumprido              ↑ 5%  │ ← Variação (verde)
│  │ ✅ │  5,189 de 6,423 protocolos               │
│  └────┘  (slot subtitulo customizado)            │
│                                                    │
│                                                    │
│        87.3%                                       │ ← Valor (slot default)
│                                                    │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Tipo Dinâmico:**

```javascript
tipo: dados.taxa_sla_cumprido >= 80 
  ? 'success'   // ✅ Verde (excelente)
  : dados.taxa_sla_cumprido >= 60 
    ? 'warning' // ⚠️  Amarelo (atenção)
    : 'danger'  // ❌ Vermelho (crítico)
```

---

### Card: Protocolos Vencidos

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  ┌────┐  Protocolos em Atraso                     │
│  │ ⚠️  │  Acima do prazo SLA                       │
│  └────┘                                            │
│                                                    │
│                                                    │
│        1,234                                       │ ← Número formatado
│                                                    │
│  19.2% do total                                    │ ← Contexto calculado
│                                                    │
└────────────────────────────────────────────────────┘
```

**Cores (tipo: danger):**

```css
Icon BG:  bg-red-100 dark:bg-red-900/20
Icon:     text-red-600 dark:text-red-400
```

---

### Card: Unidades com Gargalos

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  ┌────┐  Unidades com Gargalos                    │
│  │ 🏢 │  Secretarias problemáticas                │
│  └────┘                                            │
│                                                    │
│                                                    │
│           3                                        │ ← Contador dinâmico
│                                                    │
│  8 unidades monitoradas                            │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Lógica:**

```javascript
contarUnidadesCriticas = unidades.filter(u => {
  const percentualVencido = (u.vencido / u.total) * 100
  return percentualVencido > 30 // Mais de 30% = crítico
}).length
```

---

## 🏆 ANATOMIA DO RANKING DE GARGALOS

### Card Completo

```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️  Gargalos por Secretaria                   Ordenado por   │
│    Unidades com maior volume de SLA vencido   criticidade    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌───┐  Secretaria de Mobilidade Urbana        TMA: 8d 5h   │
│ │ 1 │  SEMOB                                               │
│ └───┘                                                        │
│      ● No prazo: 510  ● Vencido: 340         Total: 850    │
│      ████████░░░░░░░░░░░░░░░░░░ 60.0% | ████████░░ 40.0%  │
│      60.0% cumprindo SLA | 40.0% em atraso                 │
│      ⚠️  Situação Crítica                                   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌───┐  Secretaria de Infraestrutura           TMA: 7d 2h   │
│ │ 2 │  SEINFRA                                             │
│ └───┘                                                        │
│      ● No prazo: 960  ● Vencido: 240         Total: 1200   │
│      ████████████████░░░░ 80.0% | ████░ 20.0%              │
│      80.0% cumprindo SLA | 20.0% em atraso                 │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌───┐  Secretaria de Educação                 TMA: 4d      │
│ │ 3 │  SEDUC                                               │
│ └───┘                                                        │
│      ● No prazo: 405  ● Vencido: 45          Total: 450    │
│      ██████████████████░░ 90.0% | ██░ 10.0%                │
│      90.0% cumprindo SLA | 10.0% em atraso                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### Item Individual (1º Lugar)

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│ ┌───┐  Secretaria de Mobilidade Urbana        TMA: 8d 5h   │
│ │ 1 │  SEMOB                                               │ ← Badge vermelho
│ └───┘  ↑ Ranking                                            │   (mais crítico)
│                                                              │
│      ● No prazo: 510  ● Vencido: 340         Total: 850    │
│      ┌────────────────────────────────────────────────┐    │
│      │████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    │ ← Barra dupla
│      │← verde 60% →│← vermelho 40% →                  │    │
│      └────────────────────────────────────────────────┘    │
│      60.0% cumprindo SLA | 40.0% em atraso                 │
│                                                              │
│      ⚠️  Situação Crítica                                   │ ← Badge alerta
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Badges de Ranking:**

```css
1º lugar: bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400
2º lugar: bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400
3º lugar: bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400
4º+:      bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-400
```

**Badge "Situação Crítica":**

Aparece quando: `(vencido / total) * 100 > 50`

```css
bg-red-100 dark:bg-red-900/30 
text-red-700 dark:text-red-400
```

---

### Barra de Progresso Dupla

**HTML Structure:**

```html
<div class="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden flex">
  <!-- Parte verde (no prazo) -->
  <div 
    class="h-full bg-gradient-to-r from-green-500 to-green-600"
    style="width: 60%"
  ></div>
  
  <!-- Parte vermelha (vencido) -->
  <div 
    class="h-full bg-gradient-to-r from-red-500 to-red-600"
    style="width: 40%"
  ></div>
</div>
```

**Cálculo:**

```javascript
function calcularPercentual(valor, total) {
  if (!total || total === 0) return 0
  return (valor / total) * 100
}

// Uso
const percentualNoPrazo = calcularPercentual(510, 850)  // 60%
const percentualVencido = calcularPercentual(340, 850)  // 40%
```

**Cores:**

```css
/* Verde (no prazo) */
background: linear-gradient(to right, #10b981, #059669);

/* Vermelho (vencido) */
background: linear-gradient(to right, #ef4444, #dc2626);

/* Container */
background: #e5e7eb (light) / #374151 (dark);
height: 12px;
border-radius: 9999px;
```

---

## 📱 RESPONSIVIDADE

### Desktop (≥1024px)

```
┌─────────────────────────────────────────────────────────────┐
│ [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]                          │ ← 4 colunas
├─────────────────────────────────────────────────────────────┤
│ [Distribuição]  [Ranking de Gargalos...........]            │ ← 1 + 2 colunas
└─────────────────────────────────────────────────────────────┘
```

**CSS:**

```css
grid-cols-1 lg:grid-cols-4       /* KPIs */
grid-cols-1 lg:grid-cols-3       /* Gráficos + Ranking */
```

---

### Tablet (768px - 1023px)

```
┌───────────────────────────────────┐
│ [KPI 1]         [KPI 2]           │ ← 2 colunas
│ [KPI 3]         [KPI 4]           │
├───────────────────────────────────┤
│ [Distribuição]                    │ ← 1 coluna
│ [Ranking de Gargalos]             │
└───────────────────────────────────┘
```

**CSS:**

```css
md:grid-cols-2
```

---

### Mobile (<768px)

```
┌──────────────────┐
│ [KPI 1]          │ ← 1 coluna
│ [KPI 2]          │
│ [KPI 3]          │
│ [KPI 4]          │
├──────────────────┤
│ [Distribuição]   │
│ [Ranking]        │
└──────────────────┘
```

**CSS:**

```css
grid-cols-1
```

---

## 🌓 DARK MODE

### Light Mode

```
┌─────────────────────────────────┐
│ bg-white                        │
│ border-gray-200                 │
│                                 │
│ text-gray-900 (títulos)         │
│ text-gray-600 (secundário)      │
│                                 │
│ hover:shadow-lg                 │
└─────────────────────────────────┘
```

### Dark Mode

```
┌─────────────────────────────────┐
│ dark:bg-gray-800                │
│ dark:border-gray-700            │
│                                 │
│ dark:text-white (títulos)       │
│ dark:text-gray-400 (secundário) │
│                                 │
│ dark:hover:shadow-xl            │
└─────────────────────────────────┘
```

---

## 🎭 ESTADOS VISUAIS

### 1. Loading (Skeleton)

```
┌────────────────────────────┐
│ ▒▒▒▒                       │ ← Shimmer animation
│ ▒▒▒▒▒▒ ▒▒▒▒▒▒▒             │
│        ▒▒▒▒▒               │
│                            │
│ ▒▒▒▒▒▒▒▒▒▒                 │
│                            │
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒             │
└────────────────────────────┘
```

**CSS:**

```css
animate-pulse
bg-gray-200 dark:bg-gray-700
rounded
```

---

### 2. Carregado (Dados)

```
┌────────────────────────────┐
│ 🕐  TMA Global       ↓ 12% │
│     Tempo Médio...         │
│                            │
│     5d 12h                 │
│                            │
│ 🏁  Meta: 5 dias           │
└────────────────────────────┘
```

---

### 3. Erro

```
┌─────────────────────────────────────┐
│ ⚠️  Dados Indisponíveis             │
│                                     │
│ Não foi possível carregar os dados  │
│ do dashboard. Tente novamente em    │
│ alguns instantes.                   │
└─────────────────────────────────────┘
```

**CSS:**

```css
bg-amber-50 dark:bg-amber-900/20
border-amber-200 dark:border-amber-800
text-amber-900 dark:text-amber-200
```

---

### 4. Vazio (Sem Gargalos)

```
┌─────────────────────────────────────┐
│            ✅                        │
│         (ícone grande)              │
│                                     │
│    Nenhum Gargalo Identificado      │
│                                     │
│ Todas as unidades estão cumprindo   │
│ os prazos estabelecidos.            │
└─────────────────────────────────────┘
```

---

## 🎨 PALETA DE CORES COMPLETA

### Cores Principais

```css
/* Primary (Roxo) */
primary-50:   #f5f3ff
primary-100:  #ede9fe
primary-500:  #8b5cf6
primary-600:  #7c3aed
primary-900:  #4c1d95

/* Success (Verde) */
green-50:     #f0fdf4
green-100:    #dcfce7
green-400:    #4ade80
green-500:    #22c55e
green-600:    #16a34a
green-700:    #15803d
green-900:    #14532d

/* Danger (Vermelho) */
red-50:       #fef2f2
red-100:      #fee2e2
red-400:      #f87171
red-500:      #ef4444
red-600:      #dc2626
red-700:      #b91c1c
red-900:      #7f1d1d

/* Warning (Amarelo) */
amber-50:     #fffbeb
amber-100:    #fef3c7
amber-500:    #f59e0b
amber-600:    #d97706
amber-700:    #b45309
amber-900:    #78350f

/* Orange */
orange-100:   #ffedd5
orange-700:   #c2410c
orange-900:   #7c2d12

/* Neutrals */
gray-50:      #f9fafb
gray-100:     #f3f4f6
gray-200:     #e5e7eb
gray-400:     #9ca3af
gray-500:     #6b7280
gray-600:     #4b5563
gray-700:     #374151
gray-800:     #1f2937
gray-900:     #111827
white:        #ffffff
```

---

## 💫 ANIMAÇÕES

### 1. Fade In (Entrada)

```css
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}
```

---

### 2. Pulse (Skeleton)

```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

### 3. Spin (Botão Atualizar)

```css
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
```

**Uso:**

```vue
<ArrowPathIcon 
  class="w-5 h-5" 
  :class="{ 'animate-spin': carregando }"
/>
```

---

### 4. Barra de Progresso (Preenchimento)

```css
.progress-bar {
  transition: width 500ms ease-in-out;
}
```

**Efeito:**

```
Início:  |                    |  0%
500ms:   |████████           |  60%
```

---

## 📊 HIERARQUIA TIPOGRÁFICA

```css
/* Título principal da página */
h1: text-3xl font-bold
    (30px, 700)

/* Valor dos KPIs */
.kpi-value: text-3xl font-bold
            (30px, 700)

/* Título do card */
h3: text-lg font-semibold
    (18px, 600)

/* Título do KPI */
.kpi-title: text-sm font-medium
            (14px, 500)

/* Descrição */
p: text-sm text-gray-600
   (14px, 400)

/* Subtítulo / Contexto */
.subtitle: text-xs text-gray-500
           (12px, 400)

/* Badge / Tag */
.badge: text-xs font-semibold
        (12px, 600)
```

---

## 🎯 GRID SYSTEM

### Container Principal

```css
max-w-7xl        /* 1280px */
mx-auto          /* Centralizado */
px-4 sm:px-6 lg:px-8  /* Padding responsivo */
py-8             /* Padding vertical */
```

---

### Grid de KPIs

```css
/* Mobile */
grid-cols-1      /* 1 coluna */

/* Tablet */
md:grid-cols-2   /* 2 colunas */

/* Desktop */
lg:grid-cols-4   /* 4 colunas */

/* Gap */
gap-6            /* 24px entre cards */
```

---

### Grid Gráficos + Ranking

```css
/* Mobile */
grid-cols-1            /* 1 coluna */

/* Desktop */
lg:grid-cols-3         /* 3 colunas */
lg:col-span-1          /* Distribuição: 1 coluna */
lg:col-span-2          /* Ranking: 2 colunas */
```

---

## 🎁 COMPONENTES REUTILIZÁVEIS

### Badge de Status

```vue
<!-- SLA Excelente (≥90%) -->
<span class="badge-success">✅ Excelente</span>

<!-- SLA Bom (80-89%) -->
<span class="badge-success">✅ Bom</span>

<!-- SLA Atenção (60-79%) -->
<span class="badge-warning">⚠️  Atenção</span>

<!-- SLA Crítico (<60%) -->
<span class="badge-danger">❌ Crítico</span>
```

**CSS:**

```css
.badge-success {
  @apply px-2.5 py-1 rounded-full text-xs font-semibold;
  @apply bg-green-100 dark:bg-green-900/30;
  @apply text-green-700 dark:text-green-400;
}

.badge-warning {
  @apply px-2.5 py-1 rounded-full text-xs font-semibold;
  @apply bg-amber-100 dark:bg-amber-900/30;
  @apply text-amber-700 dark:text-amber-400;
}

.badge-danger {
  @apply px-2.5 py-1 rounded-full text-xs font-semibold;
  @apply bg-red-100 dark:bg-red-900/30;
  @apply text-red-700 dark:text-red-400;
}
```

---

**🎨 Guia Visual Completo do Dashboard de Eficiência!**

*Este documento serve como referência para designers, desenvolvedores e stakeholders entenderem a anatomia visual do dashboard executivo.*
