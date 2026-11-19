# 🎨 GUIA VISUAL - Painel Setorial

## 🚀 Acesso Rápido

```
/backoffice/setorial
```

---

## 📊 Dashboard Principal

```
╔═══════════════════════════════════════════════════════════╗
║ 🏢 Secretaria de Infraestrutura e Obras                   ║
║ Gestão de Ordens de Serviço · SINFRA-OBRAS               ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    ║
║  │ 🕒 OS   │  │ ⚠️ OS   │  │ 🚗 Aguard│  │ ✅ Concl.│    ║
║  │ Pend.   │  │ Atras.  │  │ Campo   │  │ Hoje    ║
║  │         │  │         │  │         │  │         │    ║
║  │   3     │  │   1     │  │   2     │  │   1     │    ║
║  └─────────┘  └─────────┘  └─────────┘  └─────────┘    ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║ [🔍 Buscar OS...] [Status ▼] [Prioridade ▼] [Lista][KB]║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║ ┌───────────────────────────────────────────────────┐   ║
║ │ OS-2024-001    Buraco na Via   🔴 URG   📍 0 fotos│   ║
║ │ ← PROT-2024-123  Av. Principal  ⏰ VENCIDO   [✏️] │   ║
║ ├───────────────────────────────────────────────────┤   ║
║ │ OS-2024-002    Poda de Árvore  🟠 ALTA  📍 0 fotos│   ║
║ │ ← PROT-2024-124  Rua das Flores ⏰ 2d 3h   [✏️]  │   ║
║ ├───────────────────────────────────────────────────┤   ║
║ │ OS-2024-003    Iluminação       🔵 NORM  📷 3 fotos│   ║
║ │ ← PROT-2024-125  Av. Estados    ⏰ 5d      [✏️]  │   ║
║ └───────────────────────────────────────────────────┘   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📋 Modal de Formalização (Drawer)

```
                                      ┌────────────────────────────────────────┐
                                      │ [X]  Formalizar Ordem de Serviço       │
                                      │                                         │
                                      │ OS-2024-001 ← PROT-2024-123  [Nova]    │
                                      │ 📍 Av. Principal, 500 - Centro         │
                                      │                                         │
                                      │ ┌────┐ ┌────┐ ┌────┐                  │
                                      │ │Serv│ │Prior│ │Prazo│                 │
                                      │ └────┘ └────┘ └────┘                  │
                                      ├─────────────────────────────────────────┤
                                      │ 💬 Instrução da Ouvidoria Central      │
                                      │ ┌──────────────────────────────────┐  │
                                      │ │ Executar tapa-buraco com massa  │  │
                                      │ │ asfáltica. Prioridade alta.     │  │
                                      │ └──────────────────────────────────┘  │
                                      ├─────────────────────────────────────────┤
                                      │ 🚗 EQUIPE DE RUA E EVIDÊNCIAS          │
                                      │                                         │
                                      │ 🔗 Link Mágico para Equipe de Campo    │
                                      │ ┌──────────────────────────────────┐  │
                                      │ │ Copie e envie este link para a   │  │
                                      │ │ equipe de campo. Permite envio   │  │
                                      │ │ de fotos sem login.              │  │
                                      │ │                                  │  │
                                      │ │ [🔗 Copiar Link] [📱 QR Code]   │  │
                                      │ └──────────────────────────────────┘  │
                                      │                                         │
                                      │ 📷 Galeria de Evidências (0 fotos)     │
                                      │ ┌──────────────────────────────────┐  │
                                      │ │         📷                       │  │
                                      │ │  Aguardando envio das evidências │  │
                                      │ │  de campo...                     │  │
                                      │ │                                  │  │
                                      │ │  [📤 Fazer upload manual]        │  │
                                      │ └──────────────────────────────────┘  │
                                      ├─────────────────────────────────────────┤
                                      │ 📄 FORMALIZAÇÃO E DESPACHO              │
                                      │                                         │
                                      │ Despacho Técnico Oficial *             │
                                      │ [Selecione um despacho padrão... ▼]   │
                                      │                                         │
                                      │ Observações Complementares             │
                                      │ ┌──────────────────────────────────┐  │
                                      │ │ Adicione observações técnicas... │  │
                                      │ │                                  │  │
                                      │ └──────────────────────────────────┘  │
                                      │                                         │
                                      │ 🛡️ ASSINATURA DIGITAL DO GESTOR        │
                                      │ ┌──────────────────────────────────┐  │
                                      │ │ ☐ Declaro ciência de que este   │  │
                                      │ │   despacho possui validade      │  │
                                      │ │   jurídica conforme Lei         │  │
                                      │ │   14.063/2020                   │  │
                                      │ │                                  │  │
                                      │ │ Senha: [••••••]                 │  │
                                      │ └──────────────────────────────────┘  │
                                      ├─────────────────────────────────────────┤
                                      │ ⚠️ Preencha todos os campos obrigatórios│
                                      │                                         │
                                      │ [Cancelar] [✅ Concluir OS] (disabled) │
                                      └─────────────────────────────────────────┘
```

---

## 🔗 Magic Link Panel (Estados)

### Antes de Gerar:

```
┌────────────────────────────────────────────────────┐
│ 🔗 Link Mágico para Equipe de Campo                │
│                                                    │
│ Copie e envie este link para a equipe de campo.   │
│ Permite envio de fotos sem necessidade de login.  │
│                                                    │
│ [✨ Gerar Link Mágico]                             │
└────────────────────────────────────────────────────┘
```

### Depois de Gerar:

```
┌────────────────────────────────────────────────────┐
│ 🔗 Link Mágico para Equipe de Campo                │
│                                                    │
│ URL do Link Mágico                                 │
│ ┌──────────────────────────────────────┐          │
│ │ https://mouve.gov.br/campo/ML-abc123 │ [Copiar]│
│ └──────────────────────────────────────┘          │
│                                                    │
│ [📱 Gerar QR Code]                                 │
│                                                    │
│ ┌──────┐ ┌──────┐ ┌──────┐                       │
│ │Token │ │Acess.│ │Valid.│                       │
│ │ML-..│ │  2   │ │ 6d   │                       │
│ └──────┘ └──────┘ └──────┘                       │
│                                                    │
│ 🔄 Renovar  💬 WhatsApp  ✉️ E-mail               │
└────────────────────────────────────────────────────┘
```

---

## 📷 Galeria de Evidências (Estados)

### Vazia:

```
┌────────────────────────────────────────────────────┐
│ 📷 Galeria de Evidências (0 fotos)                 │
│                                                    │
│ ┌────────────────────────────────────────────────┐ │
│ │              📷                                 │ │
│ │                                                 │ │
│ │   Aguardando envio das evidências de campo     │ │
│ │                                                 │ │
│ │   [📤 Fazer upload manual]                      │ │
│ │   JPG, PNG ou HEIC até 10MB cada               │ │
│ └────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

### Com Fotos:

```
┌────────────────────────────────────────────────────┐
│ 📷 Galeria de Evidências (3 fotos)     Ver todas →│
│                                                    │
│ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐         │
│ │ [IMG] │ │ [IMG] │ │ [IMG] │ │  📤   │         │
│ │       │ │       │ │       │ │ Add   │         │
│ └───────┘ └───────┘ └───────┘ └───────┘         │
│ Antes      Durante    Depois    Upload           │
│ 09:15      10:30      11:00                      │
│ 📍 GPS     📍 GPS     📍 GPS                     │
└────────────────────────────────────────────────────┘
```

---

## 🖼️ Lightbox (Visualização de Foto)

```
╔══════════════════════════════════════════════════════════╗
║                         [X]                              ║
║ 2 / 3    Antes da intervenção                           ║
║                                                          ║
║                                                          ║
║  [←]         🖼️ IMAGEM EM FULLSCREEN          [→]      ║
║                                                          ║
║                                                          ║
║ 📅 13/11/2024 09:15  👤 Equipe de Campo                 ║
║ 📍 GPS: -23.5520, -46.6350                              ║
║                                        [⬇️] [🔗]         ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🎨 Paleta de Cores

### KPIs:

```css
OS Pendentes:          #3B82F6 (Azul)
OS Atrasadas:          #EF4444 (Vermelho)
Aguardando Campo:      #F59E0B (Amarelo)
Concluídas Hoje:       #10B981 (Verde)
```

### Prioridade:

```css
Urgente:  🔴  #EF4444 (Vermelho)
Alta:     🟠  #F97316 (Laranja)
Normal:   🔵  #3B82F6 (Azul)
```

### Status:

```css
Nova:               🔵  #3B82F6 (Azul)
Aguardando Campo:   🟡  #F59E0B (Amarelo)
Em Execução:        🟣  #8B5CF6 (Roxo)
Concluída:          🟢  #10B981 (Verde)
```

### SLA:

```css
Normal:    🟢  #10B981 (Verde)
Atenção:   🟡  #F59E0B (Amarelo)
Vencido:   🔴  #EF4444 (Vermelho)
```

### Especiais:

```css
Magic Link:     #3B82F6 → #6366F1 (Gradiente Primary → Indigo)
Assinatura:     #3B82F6 → #6366F1 (Gradiente Blue → Indigo)
Instrução:      #8B5CF6 (Roxo)
GPS Badge:      #10B981 (Verde)
```

---

## 🔢 Badges e Indicadores

### Badge de Prioridade:

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ ⚠️ URG  │  │ 🔥 ALTA │  │ • NORM  │
└─────────┘  └─────────┘  └─────────┘
  Vermelho     Laranja       Azul
```

### Badge de Status:

```
┌─────────────┐  ┌─────────────┐
│ • Nova      │  │ • Aguard.   │
└─────────────┘  │   Campo     │
                 └─────────────┘
┌─────────────┐  ┌─────────────┐
│ • Em Exec.  │  │ ✓ Concluída │
└─────────────┘  └─────────────┘
```

### SLA Indicator:

```
⏰ 5d restantes  (Verde)
⏰ Vence hoje    (Amarelo)
⏰ VENCIDO       (Vermelho, pulsando)
```

---

## 📐 Layout Responsivo

### Desktop (> 1024px):

```
┌─────────────────────────────────────────────────┐
│ Sidebar │ Content Area                          │
│ 256px   │                                       │
│         │  Dashboard                            │
│ [Menu]  │  ┌───────────────────────────────┐   │
│         │  │ KPIs (4 cards)                │   │
│ Links   │  └───────────────────────────────┘   │
│         │  ┌───────────────────────────────┐   │
│         │  │ Worklist                      │   │
│         │  │ (Lista ou Kanban)             │   │
│         │  └───────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Tablet (768px - 1024px):

```
┌─────────────────────────────────────────────────┐
│ [☰]  Dashboard                          [User]  │
├─────────────────────────────────────────────────┤
│ KPIs (Grid 2x2)                                 │
│ ┌──────┐ ┌──────┐                               │
│ │      │ │      │                               │
│ └──────┘ └──────┘                               │
│ ┌──────┐ ┌──────┐                               │
│ │      │ │      │                               │
│ └──────┘ └──────┘                               │
│                                                 │
│ Worklist (Lista compacta)                       │
└─────────────────────────────────────────────────┘
```

### Mobile (< 768px):

```
┌───────────────────────────┐
│ [☰] Dashboard      [User] │
├───────────────────────────┤
│ KPIs (Stack vertical)     │
│ ┌───────────────────────┐ │
│ │ OS Pendentes    3     │ │
│ └───────────────────────┘ │
│ ┌───────────────────────┐ │
│ │ OS Atrasadas    1     │ │
│ └───────────────────────┘ │
│ ┌───────────────────────┐ │
│ │ Aguardando      2     │ │
│ └───────────────────────┘ │
│ ┌───────────────────────┐ │
│ │ Concluídas      1     │ │
│ └───────────────────────┘ │
│                           │
│ Cards de OS (Stack)       │
│ ┌───────────────────────┐ │
│ │ OS-2024-001           │ │
│ │ Buraco na Via         │ │
│ │ 🔴 URG  ⏰ VENCIDO    │ │
│ └───────────────────────┘ │
└───────────────────────────┘
```

---

## 🎯 Hierarquia de Componentes

```
PainelSetorialView
├── Header
│   ├── Título da Unidade
│   ├── Botões de Ação
│   └── KPIs (4 cards)
├── Filtros
│   ├── Busca
│   ├── Select Status
│   ├── Select Prioridade
│   └── Toggle Lista/Kanban
└── WorklistOS
    ├── Lista (Tabela)
    │   └── Linhas de OS
    └── Kanban (Colunas)
        └── CardOrdemKanban (por OS)

ModalFormalizacaoOS
├── Header
│   ├── Título
│   ├── Badges
│   └── Info Cards
├── Instrução Ouvidoria (Box roxo)
├── Seção: Equipe de Rua
│   ├── MagicLinkPanel
│   │   ├── Gerar Link
│   │   ├── Copiar URL
│   │   ├── QR Code
│   │   └── Compartilhar
│   └── GaleriaEvidencias
│       ├── Empty State
│       ├── Grid de Fotos
│       └── Upload Manual
├── Seção: Formalização
│   ├── Select Despacho
│   ├── Textarea Observações
│   └── Assinatura Digital
│       ├── Checkbox
│       └── Campo Senha
└── Footer
    ├── Status Validação
    └── Botões Ação

ModalVisualizacaoFoto
├── Backdrop
├── Header (Contador + Legenda)
├── Imagem Central
│   ├── Botão Anterior
│   └── Botão Próxima
└── Footer
    ├── Metadata
    └── Ações (Baixar, Abrir)
```

---

## ⚡ Animações e Transições

### Drawer:
```css
Entrada:  translateX(100%) → translateX(0)
Saída:    translateX(0) → translateX(100%)
Duração:  300ms ease-out
```

### Cards Hover:
```css
Transform: scale(1) → scale(1.02)
Shadow:    card → card-hover
Duração:   200ms ease
```

### Loading State:
```css
Spin:      rotate(0) → rotate(360deg)
Duração:   1s linear infinite
```

### Fade In:
```css
Opacity:   0 → 1
Duração:   300ms ease
```

---

## 🎨 Tipografia

```css
Títulos H1:   text-2xl font-bold
Títulos H2:   text-xl font-bold
Títulos H3:   text-lg font-semibold
Corpo:        text-sm
Legenda:      text-xs
Mono (IDs):   font-mono font-semibold
```

---

## 📦 Ícones Utilizados

```javascript
// Heroicons Outline
BuildingOffice2Icon   // Secretaria
TruckIcon             // Equipe de rua
LinkIcon              // Magic Link
PhotoIcon             // Evidências
ShieldCheckIcon       // Assinatura
DocumentTextIcon      // Despacho
ClockIcon             // Prazo
ExclamationTriangleIcon // Alerta
CheckCircleIcon       // Sucesso
MapPinIcon            // Localização
SparklesIcon          // Gerar (magia)
QrCodeIcon            // QR Code
ArrowPathIcon         // Atualizar/Renovar
ChatBubbleLeftRightIcon // Instrução
```

---

## 🎯 Estados do Formulário

### Inválido (Incompleto):

```
⚠️ Preencha todos os campos obrigatórios para concluir

[Cancelar] [✅ Concluir OS] (disabled/opaco)
```

### Válido (Completo):

```
✅ Formulário completo e pronto para conclusão

[Cancelar] [✅ Concluir OS] (enabled/verde)
```

---

## 🔒 Requisitos de Validação

Para habilitar botão "Concluir":

```
☑ Despacho técnico selecionado
☑ Pelo menos 1 evidência na galeria
☑ Checkbox de assinatura marcado
☑ Senha preenchida
```

---

## 📊 Feedback Visual

### Copiar Link:
```
[📋 Copiar] → [✓ Copiado!] (2s) → [📋 Copiar]
```

### Gerar Link:
```
[✨ Gerar Link] → [⏳ Gerando...] → [URL aparece]
```

### Upload:
```
[📤 Upload] → [⏳ Enviando...] → [Foto na galeria]
```

### Concluir OS:
```
[✅ Concluir] → [⏳ Processando...] → [Modal fecha + Lista atualiza]
```

---

## 🎉 Conclusão Visual

Interface profissional, densa e eficiente para gestores setoriais formalizarem ordens de serviço com segurança institucional e rastreabilidade completa.

**Acesso:** `/backoffice/setorial`
