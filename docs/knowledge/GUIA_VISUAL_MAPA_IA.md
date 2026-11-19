# 🎨 Guia Visual - Visão Geográfica & IA

## 🖼️ Telas e Componentes

---

## 1️⃣ VISÃO GERAL DA TELA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🏛️ Ouv.IA - Mesa de Trabalho                               👤 Admin  🌙    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Mesa de Trabalho                                      🔍 [Buscar...]      │
│  Gestão de Protocolos · Backoffice                                         │
│                                                                             │
│  [SLA Vencido 3] [Urgentes 5] [Mais filtros]    [Kanban] [Lista] [Mapa] ← │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────┬───────────┬──────────────┬────────────┬──────────────┐     │
│  │   Total   │ Andamento │ Ag. Validação│ SLA Vencido│ Concluídos   │     │
│  │    145    │     32    │      5       │      3     │      12      │     │
│  └───────────┴───────────┴──────────────┴────────────┴──────────────┘     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                       ÁREA DE VISUALIZAÇÃO (Mapa & IA)                     │
│                                                                             │
│  ┌──────────────────────┐  ┌────────────────────────────────────────────┐ │
│  │                      │  │                                            │ │
│  │   WIDGET IA (33%)    │  │         MAPA LEAFLET (67%)                │ │
│  │                      │  │                                            │ │
│  └──────────────────────┘  └────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ WIDGET IA - PAINEL LATERAL

```
┌──────────────────────────────────────┐
│  ╭─────────────────────────────────╮ │
│  │  ✨  Inteligência Artificial     │ │  ← Header com gradiente
│  │  Sugestões de agrupamento       │ │
│  ╰─────────────────────────────────╯ │
│                                      │
│  ┌──────────────┐  ┌───────────────┐│
│  │ Agrupamentos │  │  Protocolos   ││  ← KPIs
│  │      3       │  │      12       ││
│  └──────────────┘  └───────────────┘│
│                                      │
│  ┌──────────────────────────────────┤
│  │                           92% ✨ │  ← Badge confiança
│  │ 5 protocolos de Buraco na Via   │
│  │ próximos ao Centro              │
│  │                                  │
│  │ 📍 Centro · Raio: 0.5 km        │
│  │                                  │
│  │ ┌──────┐ ┌──────┐ ┌──────┐     │  ← Grid de fotos
│  │ │ 📷   │ │ 📷   │ │ 📷   │     │
│  │ │ 101  │ │ 102  │ │ 103  │     │
│  │ └──────┘ └──────┘ └──────┘     │
│  │                                  │
│  │ ╭────────────────────────────╮  │
│  │ │ 💰 Economia Estimada       │  │  ← Box economia
│  │ │                            │  │
│  │ │  4        6h      R$ 2.400 │  │
│  │ │ equipes   tempo     custo  │  │
│  │ ╰────────────────────────────╯  │
│  │                                  │
│  │ [🗺️ Ver no Mapa] [✅ Aprovar]  │  ← Ações
│  └──────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────────┤
│  │                           87% ✨ │
│  │ 3 solicitações de Poda de Árvore│
│  │ no Jardim Europa                │
│  │                                  │
│  │ 📍 Jardim Europa · Raio: 0.3 km │
│  │                                  │
│  │ ┌──────┐ ┌──────┐ ┌──────┐     │
│  │ │ 📷   │ │ 📷   │ │ 📷   │     │
│  │ │ 106  │ │ 107  │ │ 108  │     │
│  │ └──────┘ └──────┘ └──────┘     │
│  │                                  │
│  │ ╭────────────────────────────╮  │
│  │ │ 💰 Economia Estimada       │  │
│  │ │                            │  │
│  │ │  2        4h      R$ 1.600 │  │
│  │ │ equipes   tempo     custo  │  │
│  │ ╰────────────────────────────╯  │
│  │                                  │
│  │ [🗺️ Ver no Mapa] [✅ Aprovar]  │
│  └──────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────────┤
│  │                           95% ✨ │
│  │ 4 pontos de Iluminação Pública  │
│  │ na Zona Industrial              │
│  │                                  │
│  │ 📍 Industrial · Raio: 0.4 km    │
│  │                                  │
│  │ ┌──────┐ ┌──────┐ ┌──────┐     │
│  │ │ 📷   │ │ 📷   │ │ 📷   │     │
│  │ │ 109  │ │ 110  │ │ 111  │     │
│  │ └──────┘ └──────┘ └──────┘     │
│  │                                  │
│  │ ╭────────────────────────────╮  │
│  │ │ 💰 Economia Estimada       │  │
│  │ │                            │  │
│  │ │  3        5h      R$ 2.000 │  │
│  │ │ equipes   tempo     custo  │  │
│  │ ╰────────────────────────────╯  │
│  │                                  │
│  │ [🗺️ Ver no Mapa] [✅ Aprovar]  │
│  └──────────────────────────────────┤
│                                      │
│  🕐 Última atualização: há 2 min    │  ← Footer
└──────────────────────────────────────┘
```

**Cores e Efeitos:**
- Header: Gradiente `Primary → Purple`
- Badge: Verde (≥90%), Azul (≥80%)
- Box Economia: Verde claro
- Hover: Borda brilhante animada
- Ícone ✨: Pulse animation

---

## 3️⃣ MAPA LEAFLET - ÁREA PRINCIPAL

### Estado Normal (Navegação)

```
┌────────────────────────────────────────────────────────────────────┐
│  Visão Geográfica de Protocolos               12 protocolos       │
│  [🎯 Seleção em Lote] [↔ Reset]                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│          Av. Paulista         Av. Brigadeiro          Av. Ipiranga│
│              │                     │                       │       │
│              │                     │                       │       │
│         ──────────────────────────────────────────────────────    │
│              │          📍🔴       │                       │       │
│              │          101        │        📍🔵          │       │
│              │         (Urgente)   │        104           │       │
│              │                     │       (Normal)       │       │
│         ──────────────────────────────────────────────────────    │
│              │                     │                       │       │
│              │        📍🟡         │      📍🟠            │       │
│              │        102          │      105             │       │
│              │       (Alta)        │     (Alta)           │       │
│              │                     │                       │       │
│         ──────────────────────────────────────────────────────    │
│              │     📍🔵            │                       │       │
│              │     103             │       📍🟡           │       │
│              │    (Normal)         │       106            │       │
│              │                     │      (Alta)          │       │
│         ──────────────────────────────────────────────────────    │
│                                                                    │
│                                                                    │
│                                              ┌──────────────────┐ │
│                                              │ Legenda          │ │
│                                              │ 🔴 Urgente       │ │
│                                              │ 🟡 Alta          │ │
│                                              │ 🔵 Normal        │ │
│                                              │ 🟣 Selecionado   │ │
│                                              └──────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Estado: Modo Seleção Ativado

```
┌────────────────────────────────────────────────────────────────────┐
│  Visão Geográfica de Protocolos               12 protocolos       │
│  [🎯 Seleção em Lote: ON 3] [❌ Limpar] [↔ Reset]               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ╭──────────────────────────────────────────────────────────────╮ │
│  │ 🎯 Clique nos pinos para selecionar múltiplos protocolos     │ │  ← Banner
│  ╰──────────────────────────────────────────────────────────────╯ │
│                                                                    │
│          Av. Paulista         Av. Brigadeiro          Av. Ipiranga│
│              │                     │                       │       │
│              │                     │                       │       │
│         ──────────────────────────────────────────────────────    │
│              │          📍🟣       │                       │       │  ← Selecionado
│              │          ⭕ 101     │        📍🔵          │       │
│              │          ──         │        104           │       │
│              │         SELECTED    │       (Normal)       │       │
│              │                     │                       │       │
│         ──────────────────────────────────────────────────────    │
│              │                     │                       │       │
│              │        📍🟣         │      📍🟠            │       │  ← Selecionado
│              │        ⭕ 102       │      105             │       │
│              │        ──           │     (Alta)           │       │
│              │       SELECTED      │                       │       │
│              │                     │                       │       │
│         ──────────────────────────────────────────────────────    │
│              │     📍🟣            │                       │       │  ← Selecionado
│              │     ⭕ 103          │       📍🟡           │       │
│              │     ──              │       106            │       │
│              │    SELECTED         │      (Alta)          │       │
│              │                     │                       │       │
│         ──────────────────────────────────────────────────────    │
│                                                                    │
│     ╭────────────────────────────────────────────────────────╮   │
│     │ ✨ Agrupar 3 selecionados em uma Super OS  →          │   │  ← Botão flutuante
│     ╰────────────────────────────────────────────────────────╯   │
│                                                                    │
│                                              ┌──────────────────┐ │
│                                              │ Legenda          │ │
│                                              │ 🔴 Urgente       │ │
│                                              │ 🟡 Alta          │ │
│                                              │ 🔵 Normal        │ │
│                                              │ 🟣 Selecionado ← │ │
│                                              └──────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

**Interações:**
1. **Click Normal:** Abre popup com detalhes
2. **Click em Modo Seleção:** Toggle seleção (roxo)
3. **Hover:** Marcador escala 110%

### Estado: Destacar Sugestão (Ver no Mapa)

```
┌────────────────────────────────────────────────────────────────────┐
│  Visão Geográfica de Protocolos               12 protocolos       │
│  [🎯 Seleção em Lote] [↔ Reset]                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│                    ╭────────────────────╮                         │
│                    │   Zoom Animation   │                         │
│                    │   Centro: -23.550  │                         │
│                    ╰────────────────────╯                         │
│                                                                    │
│                         ◉◉◉◉◉◉◉◉◉                                │
│                      ◉◉             ◉◉                            │
│                   ◉◉                   ◉◉                         │
│                 ◉◉        📍🔴          ◉◉                        │
│                ◉◉         101            ◉◉                       │
│                ◉◉    ┌──────────────┐    ◉◉  ← Círculo roxo      │
│                ◉◉    │ PROT-2024-101│    ◉◉     representando    │
│                ◉◉    │ Buraco na Via│    ◉◉     o raio (500m)    │
│                ◉◉    │ Av. Principal│    ◉◉                       │
│                 ◉◉   └──────────────┘   ◉◉                        │
│                   ◉◉        📍🟡        ◉◉                         │
│                     ◉◉      102       ◉◉                          │
│                       ◉◉             ◉◉                           │
│                         ◉◉◉◉◉◉◉◉◉◉                               │
│                                                                    │
│                          📍🔵                                      │
│                          103                                      │
│                                                                    │
│                                              ┌──────────────────┐ │
│                                              │ Legenda          │ │
│                                              │ 🔴 Urgente       │ │
│                                              │ 🟡 Alta          │ │
│                                              │ 🔵 Normal        │ │
│                                              └──────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

**Animação:**
1. Mapa faz zoom suave (0.5s)
2. Desenha círculo roxo com opacity 10%
3. Abre popups dos protocolos no cluster
4. Após 3s: remove círculo automaticamente

---

## 4️⃣ MODAL CRIAR SUPER OS

```
                    ╔═══════════════════════════════════════════╗
                    ║                                           ║
                    ║  ✨ Criar Super OS Manual                 ║
                    ║  Agrupe 3 protocolos selecionados         ║
                    ║                                    [✕]    ║
    Header          ╠═══════════════════════════════════════════╣
    Gradiente →     ║                                           ║
                    ║  Título da Super OS *                     ║
                    ║  ┌─────────────────────────────────────┐ ║
    Input           ║  │ Tapa-buracos região central____     │ ║
    obrigatório →   ║  └─────────────────────────────────────┘ ║
                    ║  Descreva brevemente o que será executado║
                    ║                                           ║
                    ║  Protocolos que serão agrupados (3)       ║
                    ║  ╭─────────────────────────────────────╮ ║
                    ║  │                                     │ ║
    Lista           ║  │ ┌───────────────────────────────┐  │ ║
    scrollable →    ║  │ │ 📷  PROT-2024-101  [ALTA]    │  │ ║
                    ║  │ │     Buraco na Via            │  │ ║
                    ║  │ │     📍 Av. Principal, 500    │  │ ║
                    ║  │ └───────────────────────────────┘  │ ║
                    ║  │                                     │ ║
                    ║  │ ┌───────────────────────────────┐  │ ║
                    ║  │ │ 📷  PROT-2024-102  [ALTA]    │  │ ║
                    ║  │ │     Buraco na Via            │  │ ║
                    ║  │ │     📍 Rua São Paulo, 230    │  │ ║
                    ║  │ └───────────────────────────────┘  │ ║
                    ║  │                                     │ ║
                    ║  │ ┌───────────────────────────────┐  │ ║
                    ║  │ │ 📷  PROT-2024-103  [NORMAL]  │  │ ║
                    ║  │ │     Buraco na Via            │  │ ║
                    ║  │ │     📍 Av. Brasil, 780       │  │ ║
                    ║  │ └───────────────────────────────┘  │ ║
                    ║  │                                     │ ║
                    ║  ╰─────────────────────────────────────╯ ║
                    ║                                           ║
    Info box        ║  ╭─────────────────────────────────────╮ ║
    azul →          ║  │ ℹ️  O que acontecerá:                │ ║
                    ║  │                                       │ ║
                    ║  │ ✓ Os 3 protocolos serão agrupados    │ ║
                    ║  │   em uma única Ordem de Serviço      │ ║
                    ║  │                                       │ ║
                    ║  │ ✓ Uma equipe poderá resolver todos   │ ║
                    ║  │   de uma vez                          │ ║
                    ║  │                                       │ ║
                    ║  │ ✓ Economia de tempo e recursos       │ ║
                    ║  │   operacionais                        │ ║
                    ║  ╰─────────────────────────────────────╯ ║
                    ║                                           ║
    Footer →        ╠═══════════════════════════════════════════╣
                    ║ 3 protocolo(s) selecionado(s)            ║
                    ║                                           ║
                    ║      [Cancelar]  [✨ Criar Super OS]     ║
                    ╚═══════════════════════════════════════════╝
```

**Estados do Botão:**
- **Desabilitado:** Título < 5 caracteres (opacity 50%)
- **Normal:** Gradiente Primary → Purple
- **Loading:** Spinner + "Criando..."

---

## 5️⃣ ESTADOS DE LOADING

### Widget IA - Carregando

```
┌──────────────────────────────────┐
│  ✨  Inteligência Artificial     │
│  Sugestões de agrupamento   🔄  │
├──────────────────────────────────┤
│                                  │
│                                  │
│            ⭕ ⭕                  │
│          ⭕     ⭕                │
│          ⭕     ⭕  ← Spinner     │
│          ⭕     ⭕     animado    │
│            ⭕ ⭕                  │
│                                  │
│      Analisando protocolos...    │
│                                  │
│                                  │
└──────────────────────────────────┘
```

### Widget IA - Empty State

```
┌──────────────────────────────────┐
│  ✨  Inteligência Artificial     │
│  Sugestões de agrupamento   🔄  │
├──────────────────────────────────┤
│                                  │
│                                  │
│              ☑️                  │
│                                  │
│   Nenhum agrupamento             │
│   identificado                   │
│                                  │
│   A IA está analisando           │
│   continuamente. Novas           │
│   sugestões aparecerão aqui.     │
│                                  │
│                                  │
└──────────────────────────────────┘
```

---

## 6️⃣ POPUP DO MAPA

```
Ao clicar em um marcador:

      📍
       │
       ▼
    ┌─────────────────────┐
    │ PROT-2024-101       │ ← Código
    │                     │
    │ Buraco na Via       │ ← Serviço
    │                     │
    │ Av. Principal, 500  │ ← Endereço
    │ Centro              │
    └─────────────────────┘
             △
             │
          Popup
```

---

## 7️⃣ NOTIFICAÇÕES (TOAST)

### Sucesso

```
                ╔═══════════════════════════════════╗
                ║ ✅ Super OS criada com sucesso!   ║
                ║                                   ║
                ║ 5 protocolos de Buraco próximos   ║
                ║ ao Centro                         ║
                ║                                   ║
                ║ 5 protocolos agrupados            ║
                ╚═══════════════════════════════════╝
```

Background: Verde (#059669)  
Posição: Bottom center  
Duração: 4.5s

### Erro

```
                ╔═══════════════════════════════════╗
                ║ ❌ Erro ao criar Super OS          ║
                ║                                   ║
                ║ Tente novamente                   ║
                ╚═══════════════════════════════════╝
```

Background: Vermelho (#DC2626)  
Posição: Bottom center  
Duração: 5.5s

---

## 8️⃣ RESPONSIVIDADE

### Desktop (> 1024px)

```
┌─────────────────────────────────────────────────┐
│ [Kanban] [Lista] [Mapa & IA]                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Widget     │  │       Mapa            │  │
│  │   IA (33%)   │  │      (67%)            │  │
│  │              │  │                       │  │
│  │   400px      │  │       800px           │  │
│  └──────────────┘  └───────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Mobile (< 768px)

```
┌──────────────────┐
│ [≡] [Mapa & IA] │
├──────────────────┤
│                  │
│ ┌──────────────┐ │
│ │   Widget IA  │ │  ← Stack
│ │   (100%)     │ │     vertical
│ │              │ │
│ │   300px h    │ │
│ └──────────────┘ │
│                  │
│ ┌──────────────┐ │
│ │    Mapa      │ │
│ │   (100%)     │ │
│ │              │ │
│ │   400px h    │ │
│ └──────────────┘ │
│                  │
└──────────────────┘
```

---

## 🎨 PALETA DE CORES

### Marcadores do Mapa:
```
🔴 Urgente       #EF4444  rgb(239, 68, 68)
🟠 Alta          #F97316  rgb(249, 115, 22)
🔵 Normal        #3B82F6  rgb(59, 130, 246)
🟣 Selecionado   #8B5CF6  rgb(139, 92, 246)
```

### Gradientes Hi-Tech:
```
Primary → Purple
  from: #2563EB  (Primary-600)
  to:   #9333EA  (Purple-600)

Primary → Purple → Pink
  from: #2563EB  (Primary-600)
  via:  #9333EA  (Purple-600)
  to:   #EC4899  (Pink-600)
```

### Economia (Verde):
```
Background:  #DCFCE7  (Green-100)
Border:      #86EFAC  (Green-300)
Text:        #15803D  (Green-700)
Icon BG:     #BBF7D0  (Green-200)
```

### Confiança IA:
```
Alta (≥90%):    #DCFCE7 / #166534  (Verde)
Média (≥80%):   #DBEAFE / #1E40AF  (Azul)
Baixa (<80%):   #FEF3C7 / #92400E  (Amarelo)
```

---

## 🌙 DARK MODE

### Widget IA

```
┌──────────────────────────────────┐
│ ╔════════════════════════════╗   │
│ ║ ✨ Inteligência Artificial ║   │  ← Background: gray-900
│ ╚════════════════════════════╝   │     Text: white
│                                  │
│  ┌──────────────┐ ┌────────────┐│
│  │ Agrupamentos │ │ Protocolos ││  ← Background: gray-800
│  │      3       │ │     12     ││     Border: gray-700
│  └──────────────┘ └────────────┘│
│                                  │
│  ╔═══════════════════════════╗  │
│  ║              92% ✨        ║  │  ← Background: gray-800
│  ║ 5 protocolos de Buraco    ║  │     Text: white
│  ║ próximos ao Centro        ║  │     Border: gray-700
│  ║                           ║  │
│  ║ [Ver Mapa] [Aprovar]      ║  │
│  ╚═══════════════════════════╝  │
└──────────────────────────────────┘
```

**Esquema:**
- Background base: `gray-900`
- Cards: `gray-800`
- Bordas: `gray-700`
- Texto: `white` / `gray-200`
- Badges mantêm cores originais com opacity

---

## ✨ ANIMAÇÕES

### 1. Pulse (Ícone IA)

```
Frame 1: ✨ (opacity: 1.0, scale: 1.0)
Frame 2: ✨ (opacity: 0.7, scale: 1.05)
Frame 3: ✨ (opacity: 1.0, scale: 1.0)

Duration: 2s
Timing: ease-in-out
Infinite
```

### 2. Bounce (Banner Seleção)

```
╔════════════════════════════╗
║ 🎯 Clique nos pinos...     ║
╚════════════════════════════╝
   ↓ ↑ ↓ ↑ ↓ ↑  (movimento vertical)

Duration: 1s
Timing: ease-in-out
Infinite
```

### 3. Scale (Hover Botão)

```
Normal:      [✨ Agrupar 3 selecionados]  scale(1.0)
Hover:       [✨ Agrupar 3 selecionados]  scale(1.05)

Transition: 200ms ease
```

### 4. Shimmer (Card Hover)

```
┌─────────────────────────────┐
│                             │  ← Brilho se move
│      Sugestão 1             │     da esquerda
│                             │     para direita
└─────────────────────────────┘

Linear gradient moving from -1000px to +1000px
Animation: shimmer 2s infinite linear
Trigger: hover
```

---

## 📱 GUIA DE USO RÁPIDO

### Para Aprovar Sugestão da IA:

```
1. [Widget IA] → Veja sugestão
                    ↓
2. [Ver no Mapa] → (opcional) visualize no mapa
                    ↓
3. [Aprovar] → Cria Super OS automaticamente
                    ↓
4. [Toast] → "✅ Super OS criada!"
```

### Para Criar Super OS Manual:

```
1. [Mapa] → Ative "Seleção em Lote"
                ↓
2. [Mapa] → Clique em 2+ marcadores (ficam roxos)
                ↓
3. [Botão Flutuante] → "Agrupar X selecionados"
                ↓
4. [Modal] → Digite título da Super OS
                ↓
5. [Criar Super OS] → Confirme
                ↓
6. [Toast] → "✅ Super OS criada!"
```

---

**🎨 Guia Visual Completo - Visão Geográfica & IA**

*Desenvolvido em 16/11/2024*  
*Biblioteca: Leaflet.js real*  
*Framework: Vue 3 + Tailwind CSS*
