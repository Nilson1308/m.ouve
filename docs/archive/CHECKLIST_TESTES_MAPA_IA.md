# ✅ Checklist de Testes - Visão Geográfica & IA

## 🎯 Como Usar Este Checklist

- [ ] = Não testado
- [x] = Testado e funcionando
- [!] = Bug encontrado

---

## 📋 TESTES FUNCIONAIS

### 1. Store Pinia (`super_os.js`)

#### Buscar Sugestões
- [ ] Store inicializa vazio
- [ ] `buscarSugestoes()` retorna 3 sugestões mock
- [ ] `loading` fica `true` durante busca
- [ ] `loading` fica `false` após busca
- [ ] `ultimaAtualizacao` é atualizada
- [ ] `totalSugestoes` calcula corretamente (3)
- [ ] `totalProtocolosAgrupáveis` calcula corretamente (12)

#### Aprovar Sugestão
- [ ] `aprovarSugestao(id)` remove sugestão da lista
- [ ] `loading` fica `true` durante aprovação
- [ ] Retorna `super_os_id` correto
- [ ] Erro é capturado e armazenado

#### Criar Super OS Manual
- [ ] `criarSuperOSManual(dados)` aceita título e protocolo_ids
- [ ] `loading` fica `true` durante criação
- [ ] Retorna `super_os_id` correto
- [ ] Quantidade de protocolos bate

---

### 2. Widget IA (`WidgetSugestoesIA.vue`)

#### Renderização Inicial
- [ ] Header com gradiente renderiza
- [ ] Ícone SparklesIcon aparece
- [ ] Título "Inteligência Artificial" visível
- [ ] Botão refresh (ArrowPathIcon) funciona

#### Loading State
- [ ] Spinner com gradiente aparece
- [ ] Texto "Analisando protocolos..." visível
- [ ] Animação de pulse funciona
- [ ] KPIs não aparecem durante loading

#### Empty State
- [ ] Ícone CheckCircle cinza aparece
- [ ] Título "Nenhum agrupamento identificado" visível
- [ ] Mensagem explicativa renderiza
- [ ] Footer não aparece

#### KPIs (Com Sugestões)
- [ ] Card "Agrupamentos" mostra número correto (3)
- [ ] Card "Protocolos" mostra número correto (12)
- [ ] Cores dos cards (gradiente azul/roxo) corretas

#### Cards de Sugestão
- [ ] 3 sugestões renderizam
- [ ] Badge de confiança (92%, 87%, 95%) aparece no canto
- [ ] Cores do badge corretas (verde ≥90%, azul ≥80%)
- [ ] Título resumido completo
- [ ] Ícone MapPinIcon + região + raio aparecem
- [ ] Grid de 3 fotos renderiza
- [ ] Overlay com número do protocolo (101, 102, 103...)
- [ ] Box de economia (verde) renderiza
- [ ] Economia: equipes, tempo, custo aparecem
- [ ] Botão "Ver no Mapa" (secondary) funciona
- [ ] Botão "Aprovar" (gradiente) funciona

#### Interações
- [ ] Hover no card: borda brilhante animada
- [ ] Click "Refresh": recarrega sugestões
- [ ] Click "Ver no Mapa": emite evento `visualizar-no-mapa`
- [ ] Click "Aprovar": Loading no botão
- [ ] Click "Aprovar": Sugestão desaparece após sucesso
- [ ] Click "Aprovar": Emite evento `sugestao-aprovada`
- [ ] Alert de sucesso aparece após aprovar

#### Footer
- [ ] "Última atualização: há X minutos" aparece
- [ ] Formatação de tempo relativo funciona
- [ ] Atualiza após refresh

#### Responsividade
- [ ] Desktop (lg+): Largura 33% do container
- [ ] Mobile: Largura 100%, stack vertical
- [ ] Scroll vertical funciona quando muitas sugestões
- [ ] Altura máxima respeitada

---

### 3. Mapa Leaflet (`MapaClustersView.vue`)

#### Renderização Inicial
- [ ] Container do mapa renderiza
- [ ] Mapa Leaflet inicializa
- [ ] Tiles do OpenStreetMap carregam
- [ ] Centro: São Paulo (-23.5505, -46.6333)
- [ ] Zoom inicial: 13
- [ ] Controles de zoom aparecem

#### Header do Mapa
- [ ] Título "Visão Geográfica de Protocolos" visível
- [ ] Contador "X protocolos" atualiza dinamicamente
- [ ] Toggle "Seleção em Lote" funciona
- [ ] Botão "Limpar Seleção" aparece quando tem seleção
- [ ] Botão "Resetar Visualização" funciona

#### Marcadores
- [ ] 12 marcadores aparecem no mapa
- [ ] Cores corretas por urgência:
  - [ ] 🔴 Vermelho para "urgente"
  - [ ] 🟠 Laranja para "alta"
  - [ ] 🔵 Azul para "normal"
- [ ] Ícone SVG de pin renderiza
- [ ] Tamanho: 32x32px
- [ ] Hover: scale aumenta para 110%

#### Popups
- [ ] Click no marcador: popup abre
- [ ] Código do protocolo aparece
- [ ] Serviço aparece
- [ ] Endereço completo aparece
- [ ] Estilo do popup correto (border-radius, padding)

#### Modo Seleção
- [ ] Toggle "Seleção em Lote": modo ativa
- [ ] Banner azul aparece: "Clique nos pinos..."
- [ ] Banner tem animação bounce
- [ ] Click no marcador: seleção toggle
- [ ] Marcador selecionado fica roxo (🟣)
- [ ] Marcador selecionado tem ring animado (pulse)
- [ ] Badge no toggle mostra quantidade selecionada
- [ ] Click "Limpar Seleção": todos desmarcam

#### Botão Flutuante
- [ ] Aparece quando 2+ marcadores selecionados
- [ ] Texto: "Agrupar X selecionados em Super OS"
- [ ] Gradiente: Primary → Purple → Pink
- [ ] Posição: Bottom center
- [ ] Animação de entrada (translate-y + opacity)
- [ ] Hover: scale aumenta para 105%
- [ ] Hover: blur aumenta
- [ ] Click: abre modal `ModalCriarSuperOS`

#### Destacar Sugestão
- [ ] Evento `visualizar-no-mapa` recebido do widget
- [ ] Mapa faz zoom suave (animate: true, duration: 0.5s)
- [ ] Centraliza no `centro_geografico`
- [ ] Desenha círculo roxo representando raio
- [ ] Opacity do círculo: 10%
- [ ] Popups dos protocolos abrem automaticamente
- [ ] Círculo desaparece após 3 segundos

#### Legenda
- [ ] Legenda aparece no canto inferior direito
- [ ] Background: branco (dark: gray-800)
- [ ] Título "Legenda" visível
- [ ] 4 itens:
  - [ ] 🔴 Urgente
  - [ ] 🟡 Alta
  - [ ] 🔵 Normal
  - [ ] 🟣 Selecionado (com ring)
- [ ] Cores corretas

#### Resetar Mapa
- [ ] Click "Resetar": volta ao centro (-23.5505, -46.6333)
- [ ] Click "Resetar": zoom volta para 13
- [ ] Click "Resetar": seleção é limpa

#### Responsividade
- [ ] Desktop (lg+): Largura 67% do container
- [ ] Mobile: Largura 100%, stack vertical
- [ ] Altura ajustada: calc(100vh - 16rem) desktop
- [ ] Altura ajustada: calc(100vh - 24rem) mobile

---

### 4. Modal Criar Super OS (`ModalCriarSuperOS.vue`)

#### Renderização
- [ ] Backdrop (overlay escuro) aparece
- [ ] Modal centralizado na tela
- [ ] Largura máxima: 2xl (672px)
- [ ] Border-radius: 2xl (16px)
- [ ] Shadow: 2xl

#### Header
- [ ] Background: gradiente Primary → Purple → Pink
- [ ] Título: "Criar Super OS Manual"
- [ ] Subtítulo: "Agrupe X protocolos selecionados"
- [ ] Ícone SparklesIcon aparece
- [ ] Botão [X] fechar funciona

#### Formulário - Título
- [ ] Label "Título da Super OS *" visível
- [ ] Input text renderiza
- [ ] Placeholder: "Ex: Tapa-buracos na região central"
- [ ] Texto de ajuda abaixo: "Descreva brevemente..."
- [ ] Input aceita texto
- [ ] Validação: mínimo 5 caracteres

#### Lista de Protocolos
- [ ] Label "Protocolos que serão agrupados (X)" visível
- [ ] Container scrollable renderiza
- [ ] Altura máxima: 256px (64 * 4 linhas)
- [ ] Todos os protocolos selecionados aparecem
- [ ] Cada card mostra:
  - [ ] Foto thumbnail (64x64)
  - [ ] Código do protocolo
  - [ ] Badge de urgência (cor correta)
  - [ ] Nome do serviço
  - [ ] Ícone MapPinIcon + endereço
- [ ] Scroll funciona quando > 4 protocolos

#### Info Box
- [ ] Background: gradiente azul
- [ ] Border: azul-200 (dark: azul-800)
- [ ] Ícone InformationCircleIcon aparece
- [ ] Título: "O que acontecerá:" visível
- [ ] 3 bullets com CheckCircleIcon:
  - [ ] "Os X protocolos serão agrupados..."
  - [ ] "Uma equipe poderá resolver todos..."
  - [ ] "Economia de tempo e recursos..."

#### Footer
- [ ] Background: gray-50 (dark: gray-700/50)
- [ ] Texto: "X protocolo(s) selecionado(s)" visível
- [ ] Botão "Cancelar" (secondary) funciona
- [ ] Botão "Criar Super OS" (gradiente) funciona

#### Validação
- [ ] Botão desabilitado quando título < 5 caracteres
- [ ] Opacity: 50% quando desabilitado
- [ ] Cursor: not-allowed quando desabilitado

#### Interações
- [ ] Click backdrop: fecha modal (emite `fechar`)
- [ ] Click [X]: fecha modal
- [ ] Click "Cancelar": fecha modal
- [ ] Enter no input: chama confirmar (se válido)
- [ ] Click "Criar Super OS":
  - [ ] Loading state (spinner + "Criando...")
  - [ ] Emite evento `confirmar` com dados
  - [ ] Modal NÃO fecha automaticamente (pai decide)

#### Animações
- [ ] Backdrop: fade in/out (300ms)
- [ ] Modal: scale 95% → 100% + opacity (300ms)
- [ ] Saída: inverso (200ms)

---

### 5. Integração na Mesa de Trabalho (`MesaTrabalhoView.vue`)

#### Toggle de Visualização
- [ ] 3 botões no header: [Kanban] [Lista] [Mapa & IA]
- [ ] Botão "Mapa & IA" tem ícone MapIcon
- [ ] Texto: "Mapa & IA" visível (desktop)
- [ ] Click alterna `modoVisualizacao` para 'mapa'
- [ ] Botão ativo tem fundo branco + texto primary

#### Layout Mapa & IA
- [ ] Grid 2 colunas renderiza: 1fr (33%) + 2fr (67%)
- [ ] Widget IA na coluna 1 (esquerda)
- [ ] Mapa na coluna 2 (direita)
- [ ] Altura: calc(100vh - 16rem) em desktop
- [ ] Altura: calc(100vh - 24rem) em mobile
- [ ] Mobile: stack vertical (1 coluna)

#### Carregamento Inicial
- [ ] `onMounted` chama `superOSStore.buscarSugestoes()`
- [ ] Sugestões carregam junto com protocolos
- [ ] Loading é silencioso (não bloqueia UI)

#### Callbacks
- [ ] `carregarSugestoesIA()` recarrega sugestões
- [ ] `destacarSugestaoNoMapa(sugestao)` atualiza `sugestaoDestacadaMapa`
- [ ] `onSugestaoAprovada(dados)` mostra toast + recarrega
- [ ] `onSuperOSCriada(dados)` mostra toast + recarrega
- [ ] Toast unificado funciona

#### Transições
- [ ] Fade in/out ao trocar visualização
- [ ] Duration: 300ms
- [ ] Suave e sem glitches

#### Responsividade
- [ ] Desktop: Grid 1fr 2fr
- [ ] Tablet (768-1024): Grid mantido
- [ ] Mobile (<768): Stack vertical

---

## 🎨 TESTES VISUAIS

### Design System

#### Cores
- [ ] Primary: `#2563EB` (#2563EB)
- [ ] Purple: `#9333EA` (#9333EA)
- [ ] Pink: `#EC4899` (#EC4899)
- [ ] Verde economia: `#10B981` (#10B981)
- [ ] Vermelho urgente: `#EF4444` (#EF4444)
- [ ] Laranja alta: `#F97316` (#F97316)
- [ ] Azul normal: `#3B82F6` (#3B82F6)
- [ ] Roxo selecionado: `#8B5CF6` (#8B5CF6)

#### Gradientes
- [ ] Primary → Purple no ícone IA
- [ ] Primary → Purple no botão "Aprovar"
- [ ] Primary → Purple → Pink no botão flutuante
- [ ] Primary → Purple → Pink no header do modal

#### Animações
- [ ] Pulse no ícone IA (2s)
- [ ] Bounce no banner seleção (1s)
- [ ] Shimmer no hover do card (2s)
- [ ] Scale no hover do botão (scale-105)
- [ ] Spin nos loaders

#### Tipografia
- [ ] Títulos: font-bold
- [ ] Corpo: font-medium / font-normal
- [ ] Textos pequenos: text-sm / text-xs
- [ ] Hierarquia clara

#### Espaçamento
- [ ] Padding consistente (p-4, p-6)
- [ ] Gap entre elementos (gap-2, gap-3, gap-4)
- [ ] Margens apropriadas

#### Bordas e Sombras
- [ ] Border-radius: rounded-lg / rounded-xl
- [ ] Shadows: shadow-lg / shadow-2xl
- [ ] Borders: 1px / 2px

### Dark Mode

#### Widget IA
- [ ] Background: gray-900
- [ ] Cards: gray-800
- [ ] Borders: gray-700
- [ ] Texto: white / gray-200
- [ ] Badges mantêm cores com opacity

#### Mapa
- [ ] Leaflet tiles funcionam no dark
- [ ] Controles visíveis
- [ ] Legenda: background gray-800

#### Modal
- [ ] Backdrop: black/50
- [ ] Modal background: gray-800
- [ ] Inputs: gray-700
- [ ] Texto: white / gray-200

#### Geral
- [ ] Transição suave ao trocar modo
- [ ] Contraste WCAG AA ✓
- [ ] Sem elementos invisíveis

---

## ♿ TESTES DE ACESSIBILIDADE

### Navegação por Teclado
- [ ] Tab navega entre botões do header
- [ ] Tab navega pelos cards de sugestão
- [ ] Tab navega pelos botões dos cards
- [ ] Tab entra no mapa (focus nos controles)
- [ ] Tab navega pelos inputs do modal
- [ ] Enter no input do modal: submit
- [ ] Escape fecha modal

### Focus Visible
- [ ] Botões têm outline azul no focus
- [ ] Inputs têm ring-2 no focus
- [ ] Cards têm borda destacada no focus

### ARIA e Semântica
- [ ] Botões têm `aria-label` quando só ícone
- [ ] Imagens têm `alt` text
- [ ] Formulário tem labels associados
- [ ] Role="status" nos loading states
- [ ] Popups do mapa são acessíveis

### Contraste
- [ ] Texto branco em fundo escuro: 7:1 (AAA)
- [ ] Texto colorido em fundo branco: 4.5:1 (AA)
- [ ] Badges têm contraste suficiente

---

## 📱 TESTES DE RESPONSIVIDADE

### Desktop (> 1024px)
- [ ] Grid 1/3 + 2/3 funciona
- [ ] Widget: 400px largura
- [ ] Mapa: 800px largura
- [ ] Altura: calc(100vh - 16rem)
- [ ] Toggle mostra texto completo

### Tablet (768px - 1024px)
- [ ] Grid mantido (40% / 60%)
- [ ] Elementos redimensionam proporcionalmente
- [ ] Scroll vertical funciona
- [ ] Toggle ainda mostra texto

### Mobile (< 768px)
- [ ] Stack vertical (100% largura)
- [ ] Widget primeiro, mapa depois
- [ ] Altura: calc(100vh - 24rem)
- [ ] Cards de sugestão: 1 coluna
- [ ] Grid de fotos mantém 3 colunas
- [ ] Modal: largura 95vw
- [ ] Toggle mostra apenas ícones

### Orientação
- [ ] Portrait: layout vertical
- [ ] Landscape: tenta manter grid horizontal

---

## 🔌 TESTES DE INTEGRAÇÃO

### Widget ↔ Mapa
- [ ] Click "Ver no Mapa" destaca no mapa
- [ ] Destaque aparece e desaparece (3s)
- [ ] Zoom funciona corretamente

### Mapa → Modal
- [ ] Seleção 2+ abre botão flutuante
- [ ] Click botão abre modal
- [ ] Protocolos corretos no modal

### Modal → Store
- [ ] Formulário envia dados corretos
- [ ] Store recebe `titulo` e `protocolo_ids`
- [ ] Resposta retorna `super_os_id`

### Store → UI
- [ ] Sugestão aprovada some da lista
- [ ] KPIs atualizam após aprovação
- [ ] Toast aparece após sucesso

### Mesa de Trabalho ↔ Todos
- [ ] Toggle muda visualização
- [ ] Loading não bloqueia UI
- [ ] Protocolos recarregam após ação
- [ ] Toast unificado funciona

---

## 🐛 TESTES DE ERRO

### Network
- [ ] API falha: erro é capturado
- [ ] Erro aparece em `superOSStore.erro`
- [ ] Toast de erro aparece
- [ ] UI não quebra

### Validação
- [ ] Título < 5 caracteres: botão desabilitado
- [ ] Protocolo sem coordenadas: não plota no mapa
- [ ] Sugestão sem protocolos: não renderiza card

### Edge Cases
- [ ] 0 sugestões: empty state aparece
- [ ] 100+ protocolos: scroll funciona
- [ ] Mapa sem tiles: fallback funciona
- [ ] Dark mode no meio da sessão: transição suave

---

## ⚡ TESTES DE PERFORMANCE

### Renderização
- [ ] 3 sugestões renderizam < 100ms
- [ ] 12 marcadores no mapa < 200ms
- [ ] Modal abre instantaneamente
- [ ] Scroll é suave (60fps)

### Animações
- [ ] Pulse não degrada performance
- [ ] Hover effects são fluidos
- [ ] Transições não causam lag

### Memória
- [ ] Componentes desmontam corretamente
- [ ] Leaflet é destruído no unmount
- [ ] Sem memory leaks nos watchers

---

## 🎯 TESTES FINAIS

### Build
- [x] `npm run build` sem erros
- [x] Bundle size razoável
  - Mesa: 89.08 kB (gzip: 23.01 kB) ✅
  - Leaflet: 149.76 kB (gzip: 43.41 kB) ✅
- [x] 111 entries precached
- [ ] Service Worker funciona

### Smoke Test
- [ ] Abrir `/backoffice/mesa-trabalho`
- [ ] Clicar [Mapa & IA]
- [ ] Ver 3 sugestões no widget
- [ ] Ver 12 marcadores no mapa
- [ ] Clicar "Ver no Mapa" em uma sugestão
- [ ] Ativar "Seleção em Lote"
- [ ] Selecionar 3 marcadores
- [ ] Clicar "Agrupar 3 selecionados"
- [ ] Digitar título
- [ ] Criar Super OS
- [ ] Ver toast de sucesso

### E2E Completo
- [ ] Aprovar 1 sugestão da IA (fluxo completo)
- [ ] Criar 1 Super OS manual (fluxo completo)
- [ ] Testar em dark mode
- [ ] Testar em mobile (Chrome DevTools)
- [ ] Recarregar página (estado persiste?)

---

## 📊 RESUMO DE TESTES

| Categoria | Total | Testados | Bugs |
|-----------|-------|----------|------|
| Store | 8 | 0 | 0 |
| Widget IA | 35 | 0 | 0 |
| Mapa Leaflet | 40 | 0 | 0 |
| Modal | 30 | 0 | 0 |
| Integração | 15 | 0 | 0 |
| Visual | 25 | 0 | 0 |
| Acessibilidade | 15 | 0 | 0 |
| Responsividade | 20 | 0 | 0 |
| Performance | 8 | 0 | 0 |
| Build | 3 | 3 | 0 |
| **TOTAL** | **199** | **3** | **0** |

---

## 🚀 PRONTO PARA TESTES

**Status do Build:** ✅ Funcionando  
**Mock Data:** ✅ 3 sugestões, 12 protocolos  
**Integração:** ✅ Completa  

**Próximo passo:** Começar testes manuais seguindo este checklist!

---

*Checklist criado em 16/11/2024*  
*Para a feature: Visão Geográfica & IA*
