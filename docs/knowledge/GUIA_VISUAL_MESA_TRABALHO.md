# 🎨 Guia Visual - Mesa de Trabalho

## 📐 Hierarquia Visual e Layout

### 1️⃣ Header (Sticky)

```
╔════════════════════════════════════════════════════════════════╗
║  📋 Mesa de Trabalho                    [Busca Global...]      ║
║  Gestão de Protocolos · Backoffice                             ║
║                                                                 ║
║  [🔴 SLA Vencido (3)] [⚡ Urgentes (5)] [🎛️ Mais Filtros]      ║
║                                         [Kanban] [Lista] ←Toggle║
╚════════════════════════════════════════════════════════════════╝
```

### 2️⃣ Estatísticas (4 Cards)

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 📋 Total     │ │ ⏳ Andamento │ │ 🔴 SLA       │ │ ✅ Concluídos│
│              │ │              │ │    Vencido   │ │    Hoje      │
│     42       │ │     12       │ │      3       │ │      8       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🎴 Visualização Kanban

```
╔═══════════════╗ ╔═══════════════╗ ╔═══════════════╗ ╔═══════════════╗
║ 🆕 Novos      ║ ║ ⚙️ Andamento  ║ ║ ⏳ Aguardando ║ ║ ✅ Concluídos ║
║ Triagem (8)   ║ ║           (5) ║ ║ Retorno   (3) ║ ║           (4) ║
╠═══════════════╣ ╠═══════════════╣ ╠═══════════════╣ ╠═══════════════╣
║               ║ ║               ║ ║               ║ ║               ║
║ ┌───────────┐ ║ ║ ┌───────────┐ ║ ║ ┌───────────┐ ║ ║ ┌───────────┐ ║
║ │001/2024   │ ║ ║ │002/2024   │ ║ ║ │003/2024   │ ║ ║ │006/2024   │ ║
║ │[Triagem IA]│ ║ ║ │[Execução] │ ║ ║ │[Aguard.]  │ ║ ║ │[Concluído]│ ║
║ │           │ ║ ║ │           │ ║ ║ │           │ ║ ║ │           │ ║
║ │Buraco     │ ║ ║ │Lâmpada    │ ║ ║ │Poda Árvore│ ║ ║ │Calçada    │ ║
║ │na Via     │ ║ ║ │Queimada   │ ║ ║ │           │ ║ ║ │           │ ║
║ │           │ ║ ║ │           │ ║ ║ │           │ ║ ║ │           │ ║
║ │📍Centro   │ ║ ║ │📍Jardim   │ ║ ║ │📍Vila     │ ║ ║ │📍América  │ ║
║ │👤João     │ ║ ║ │👤Maria    │ ║ ║ │👤Pedro    │ ║ ║ │👤Fernanda │ ║
║ │           │ ║ ║ │           │ ║ ║ │           │ ║ ║ │           │ ║
║ │⚡ALTA     │ ║ ║ │⚠️MÉDIA    │ ║ ║ │✅BAIXA    │ ║ ║ │✅BAIXA    │ ║
║ │           │ ║ ║ │           │ ║ ║ │           │ ║ ║ │           │ ║
║ │SLA: 48h   │ ║ ║ │SLA: 24h   │ ║ ║ │SLA: 7d    │ ║ ║ │Concluído  │ ║
║ │[████░░░]  │ ║ ║ │[█████░░]  │ ║ ║ │[██░░░░░]  │ ║ ║ │[███████]  │ ║
║ │           │ ║ ║ │           │ ║ ║ │           │ ║ ║ │           │ ║
║ │[Despachar]│ ║ ║ │[Despachar]│ ║ ║ │[Despachar]│ ║ ║ │[👁️]       │ ║
║ └───────────┘ ║ ║ └───────────┘ ║ ║ └───────────┘ ║ ║ └───────────┘ ║
║               ║ ║               ║ ║               ║ ║               ║
╚═══════════════╝ ╚═══════════════╝ ╚═══════════════╝ ╚═══════════════╝
```

---

## 📊 Visualização Lista/Tabela

```
╔══════════╦═══════════════════╦══════════╦═══════════╦══════════╦════════╦══════════╦════════╗
║ Protocolo║ Serviço           ║ Cidadão  ║ Status    ║ Urgência ║  SLA   ║Responsável║ Ações ║
╠══════════╬═══════════════════╬══════════╬═══════════╬══════════╬════════╬══════════╬════════╣
║│001/2024 ║ 🔧 Buraco na Via  ║ João     ║[Triagem IA]║ 🔴 Alta ║ 48h    ║ EN       ║[✈️][👁️]║
║│Há 2h    ║ 📍 Av. Principal  ║ Silva    ║           ║          ║[████░░]║ Equipe   ║        ║
╠══════════╬═══════════════════╬══════════╬═══════════╬══════════╬════════╬══════════╬════════╣
║│002/2024 ║ 💡 Lâmpada       ║ Maria    ║[Execução] ║ 🟡 Média║ 24h    ║ EI       ║[✈️][👁️]║
║│Há 1d    ║ 📍 Rua Flores    ║ Santos   ║           ║          ║[█████░]║ Iluminação║       ║
╠══════════╬═══════════════════╬══════════╬═══════════╬══════════╬════════╬══════════╬════════╣
║│003/2024 ║ 🌳 Poda Árvore   ║ Pedro    ║[Aguardando]║🟢 Baixa ║ 7d     ║ MA       ║[✈️][👁️]║
║│Há 2d    ║ 📍 Rua Verde     ║ Costa    ║           ║          ║[██░░░░]║M.Ambiente║        ║
╚══════════╩═══════════════════╩══════════╩═══════════╩══════════╩════════╩══════════╩════════╝

                    Mostrando 1 até 10 de 42 protocolos
                    
                    [<] Página 1 de 5 [>]
```

---

## 🌟 Modal Scatter-Gather (O "Uau!")

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                          [X]║
║  ✈️  Despachar Protocolo                                                  ║
║     Fragmentação Scatter-Gather · Multi-Setorial                          ║
║                                                                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  ╔═══════════════════════════════════════════════════════════════════════╗ ║
║  ║ 🔧 PROT-2024-001 | [Triagem IA]                                      ║ ║
║  ║                                                                        ║ ║
║  ║ Buraco na Via                                                         ║ ║
║  ║ 📍 Av. Principal, 500, Centro    👤 João Silva                       ║ ║
║  ╚═══════════════════════════════════════════════════════════════════════╝ ║
║                                                                             ║
║  💡 Despacho Inteligente Multi-Setorial                                   ║
║  Este protocolo pode ser fragmentado e despachado para múltiplas           ║
║  secretarias/departamentos. Cada unidade receberá uma Ordem de Serviço     ║
║  específica com instruções personalizadas e prazos independentes.          ║
║                                                                             ║
║  🏢 Ordens de Serviço                                          2 unidades  ║
║  ────────────────────────────────────────────────────────────────────────  ║
║                                                                             ║
║  ╔═══════════════════════════════════════════════════════════════════════╗ ║
║  ║ 1️⃣  Unidade / Secretaria Responsável                                 ║ ║
║  ║     [Secretaria de Obras Públicas ▼]                                  ║ ║
║  ║                                                                        ║ ║
║  ║     Instrução / Despacho Específico                                   ║ ║
║  ║     ┌────────────────────────────────────────────────────────────┐    ║ ║
║  ║     │ Realizar vistoria técnica no local e providenciar          │    ║ ║
║  ║     │ reparo emergencial da via...                               │    ║ ║
║  ║     └────────────────────────────────────────────────────────────┘    ║ ║
║  ║                                                                        ║ ║
║  ║     Prazo: [2024-11-20]     Prioridade: [Alta ▼]              [🗑️]  ║ ║
║  ╚═══════════════════════════════════════════════════════════════════════╝ ║
║                                                                             ║
║  ╔═══════════════════════════════════════════════════════════════════════╗ ║
║  ║ 2️⃣  Unidade / Secretaria Responsável                                 ║ ║
║  ║     [Defesa Civil ▼]                                                  ║ ║
║  ║                                                                        ║ ║
║  ║     Instrução / Despacho Específico                                   ║ ║
║  ║     ┌────────────────────────────────────────────────────────────┐    ║ ║
║  ║     │ Avaliar riscos estruturais e emitir parecer sobre          │    ║ ║
║  ║     │ necessidade de interdição...                               │    ║ ║
║  ║     └────────────────────────────────────────────────────────────┘    ║ ║
║  ║                                                                        ║ ║
║  ║     Prazo: [2024-11-15]     Prioridade: [Crítica ▼]           [🗑️]  ║ ║
║  ╚═══════════════════════════════════════════════════════════════════════╝ ║
║                                                                             ║
║  [➕ Adicionar Unidade / Secretaria]                                       ║
║                                                                             ║
║  Observações Gerais (Opcional)                                             ║
║  ┌───────────────────────────────────────────────────────────────────┐    ║
║  │ Caso de alta prioridade devido ao fluxo de veículos...            │    ║
║  └───────────────────────────────────────────────────────────────────┘    ║
║                                                                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  [Cancelar]                      [✈️ Despachar 2 Ordens de Serviço]      ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## 🎨 Paleta de Cores por Contexto

### Status do Protocolo:

```
┌─────────────────┬─────────────┬──────────────┐
│ Status          │ Cor         │ Badge        │
├─────────────────┼─────────────┼──────────────┤
│ Triagem IA      │ 🔵 #3b82f6 │ [Triagem IA] │
│ Validação       │ 🟣 #8b5cf6 │ [Validação]  │
│ Aguard. Equipe  │ 🟡 #f59e0b │ [Aguard.]    │
│ Deslocamento    │ 🟠 #f59e0b │ [Desloc.]    │
│ Em Execução     │ 🟢 #14b8a6 │ [Execução]   │
│ Concluído       │ ✅ #10b981 │ [Concluído]  │
│ Não Procedente  │ ⚪ #6b7280 │ [Não Proc.]  │
└─────────────────┴─────────────┴──────────────┘
```

### Urgência:

```
┌──────────┬─────────────┬──────────┐
│ Urgência │ Cor         │ Badge    │
├──────────┼─────────────┼──────────┤
│ Baixa    │ 🟢 #10b981 │ [Baixa]  │
│ Média    │ 🟡 #f59e0b │ [Média]  │
│ Alta     │ 🔴 #ef4444 │ [Alta]   │
│ Crítica  │ 🔴 #dc2626 │ [Crítica]│
└──────────┴─────────────┴──────────┘
```

### SLA:

```
┌────────────────┬─────────────┬────────────────┐
│ Situação       │ Cor         │ Barra          │
├────────────────┼─────────────┼────────────────┤
│ No Prazo (>24h)│ 🟢 #10b981 │ [████████░░]   │
│ Vence Hoje     │ 🟡 #f59e0b │ [███████░░░]   │
│ Vencido        │ 🔴 #ef4444 │ [██████████]   │
└────────────────┴─────────────┴────────────────┘
```

---

## 📱 Responsividade Visual

### Desktop (> 1024px):
```
┌────────────────────────────────────────────────────────────────┐
│ [Busca........] [Filtros] [Kanban] [Lista]                     │
│                                                                 │
│ [Card][Card][Card][Card]  ← 4 Estatísticas                     │
│                                                                 │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                           │
│ │Novos │ │Andam.│ │Aguard│ │Concl.│  ← 4 Colunas Kanban       │
│ │      │ │      │ │      │ │      │                            │
│ │ Card │ │ Card │ │ Card │ │ Card │                            │
│ │ Card │ │ Card │ │ Card │ │ Card │                            │
│ └──────┘ └──────┘ └──────┘ └──────┘                           │
└────────────────────────────────────────────────────────────────┘
```

### Tablet (640px - 1024px):
```
┌────────────────────────────────────┐
│ [Busca................]            │
│ [Filtros] [Kanban] [Lista]         │
│                                     │
│ [Card] [Card]  ← 2 Estatísticas    │
│ [Card] [Card]                      │
│                                     │
│ ┌──────────┐ ┌──────────┐          │
│ │  Novos   │ │Andamento │          │
│ │          │ │          │          │
│ │  Card    │ │  Card    │          │
│ └──────────┘ └──────────┘          │
│                                     │
│ ┌──────────┐ ┌──────────┐          │
│ │Aguardando│ │Concluídos│          │
│ └──────────┘ └──────────┘          │
└────────────────────────────────────┘
```

### Mobile (< 640px):
```
┌──────────────────┐
│ [Busca.........]  │
│ [🔴] [⚡] [🎛️]    │
│ [☰] [⚏]  ← Toggle │
│                   │
│ [Card]            │
│ [Card]            │
│ [Card]            │
│ [Card]            │
│                   │
│ ┌──────────────┐  │
│ │   Novos      │  │
│ │              │  │
│ │   Card       │  │
│ │   Card       │  │
│ └──────────────┘  │
│                   │
│ ┌──────────────┐  │
│ │  Andamento   │  │
│ └──────────────┘  │
└──────────────────┘
```

---

## 🎭 Estados de Interação

### Card Normal:
```
┌─────────────────┐
│ 001/2024        │ ← Sem hover
│ Buraco na Via   │
│ Centro          │
│ [Despachar]     │
└─────────────────┘
```

### Card Hover:
```
  ┌─────────────────┐
  │ 001/2024        │ ← Elevação + Sombra
  │ Buraco na Via   │
  │ Centro          │
  │ [Despachar]     │
  └─────────────────┘
```

### Card SLA Vencido:
```
┃┌─────────────────┐
┃│ 004/2024 [ATRAS]│ ← Borda vermelha + Badge
┃│ Limpeza Terreno │
┃│ [████████████]  │ ← Barra 100% vermelha
┃│ [Despachar]     │
┃└─────────────────┘
```

---

## 🎨 Dark Mode

### Header (Dark):
```
╔════════════════════════════════════════╗  
║  📋 Mesa de Trabalho    [Busca...]     ║  bg-gray-800
║  Gestão de Protocolos                  ║  text-white
╚════════════════════════════════════════╝
```

### Card (Dark):
```
┌─────────────────┐
│ 001/2024        │  bg-gray-800
│ Buraco na Via   │  text-white
│ Centro          │  border-gray-700
│ [Despachar]     │
└─────────────────┘
```

---

## ♿ High Contrast Mode

### Header (High Contrast):
```
╔════════════════════════════════════════╗  
║  📋 Mesa de Trabalho    [Busca...]     ║  bg-black
║  Gestão de Protocolos                  ║  text-white
╚════════════════════════════════════════╝  border-yellow-300 (4px)
```

### Badge (High Contrast):
```
[Triagem IA]  →  [Triagem IA]
bg-blue-100       bg-transparent
text-blue-700     text-yellow-300
                  border-yellow-300
                  font-bold
```

---

## 🎯 Fluxo de Interação (User Flow)

```
1. Usuário acessa Mesa de Trabalho
   ↓
2. Visualiza estatísticas e protocolos (Kanban ou Lista)
   ↓
3. Aplica filtros (opcional)
   ├── Busca global
   ├── SLA Vencido
   └── Urgentes
   ↓
4. Clica em "Despachar" em um protocolo
   ↓
5. Modal Scatter-Gather abre
   ↓
6. Adiciona uma ou mais Unidades
   ├── Seleciona Secretaria
   ├── Escreve instrução específica
   ├── Define prazo
   └── Escolhe prioridade
   ↓
7. Adiciona observações gerais (opcional)
   ↓
8. Clica em "Despachar N Ordens de Serviço"
   ↓
9. Sistema fragmenta o protocolo
   ↓
10. Cada unidade recebe sua Ordem de Serviço
   ↓
11. Protocolo muda de status
   ↓
12. Kanban/Lista atualiza visualmente
```

---

## 🎬 Animações Frame-by-Frame

### Transição Kanban → Lista:

```
Frame 1 (0ms):
[Kanban visível]  opacity: 1

Frame 2 (100ms):
[Kanban]  opacity: 0.7

Frame 3 (200ms):
[Kanban]  opacity: 0.3

Frame 4 (300ms):
[Kanban]  opacity: 0
[Lista]   opacity: 0

Frame 5 (400ms):
[Lista]   opacity: 0.5

Frame 6 (500ms):
[Lista]   opacity: 1  ← Completo
```

### Modal Slide-Up:

```
Frame 1 (0ms):
[Modal]  opacity: 0, translateY: 20px

Frame 2 (150ms):
[Modal]  opacity: 0.5, translateY: 10px

Frame 3 (300ms):
[Modal]  opacity: 1, translateY: 0  ← Completo
```

---

## 📏 Espaçamento e Grid

### Espacejamento Tailwind:
```
gap-2   = 0.5rem  = 8px
gap-3   = 0.75rem = 12px
gap-4   = 1rem    = 16px
gap-6   = 1.5rem  = 24px
gap-8   = 2rem    = 32px
```

### Padding dos Cards:
```
p-4 = 1rem = 16px (mobile)
p-5 = 1.25rem = 20px (tablet)
p-6 = 1.5rem = 24px (desktop)
```

### Grid Kanban:
```
grid-cols-1       (mobile)
grid-cols-2       (tablet)
grid-cols-4       (desktop)
```

---

**🎨 Interface projetada para "brilhar os olhos" e proporcionar produtividade máxima!**
