# 🧩 Guia de Componentes de Chat - M.Ouve

## 📋 Visão Geral

Este documento descreve os **componentes modulares** criados para a interface conversacional do chat RAG.

---

## 🎯 Componentes Disponíveis

### 1. **ChatConfirmation.vue**

Renderiza botões de confirmação (Quick Replies) para escolhas binárias ou múltiplas opções.

#### **Props**

```typescript
interface Props {
  opcoes: Array<{
    texto: string        // Texto do botão
    valor: string        // Valor enviado no evento
    primary?: boolean    // Se true, renderiza como btn-primary
    icone?: Component   // Ícone Heroicon (opcional)
  }>
  disabled?: boolean     // Desabilita todos os botões
}
```

#### **Eventos**

```typescript
// Emitido quando usuário clica em uma opção
@confirmar(valor: string)
```

#### **Uso**

```vue
<template>
  <ChatConfirmation
    :opcoes="[
      { texto: 'Sim', valor: 'sim', primary: true },
      { texto: 'Não', valor: 'nao' }
    ]"
    @confirmar="handleConfirmacao"
    :disabled="carregando"
  />
</template>

<script setup>
function handleConfirmacao(valor) {
  console.log('Usuário escolheu:', valor) // 'sim' ou 'nao'
}
</script>
```

#### **Exemplo Visual**

```
┌─────────────────────────────┐
│ Você confirma esta ação?    │
└─────────────────────────────┘
    [✓ Sim]  [✕ Não]
```

---

### 2. **ChatLocationPicker.vue**

Componente híbrido para captura de localização com busca de endereço, GPS e preview de mapa.

#### **Eventos**

```typescript
// Emitido quando usuário confirma localização
@confirmar(dados: {
  latitude: number
  longitude: number
  endereco_texto: string
})

// Emitido quando usuário cancela
@cancelar()
```

#### **Uso**

```vue
<template>
  <ChatLocationPicker
    @confirmar="handleLocalizacao"
    @cancelar="handleCancelar"
  />
</template>

<script setup>
function handleLocalizacao(dados) {
  console.log('Localização:', dados)
  // { latitude: -23.5505, longitude: -46.6333, endereco_texto: "..." }
}

function handleCancelar() {
  console.log('Usuário cancelou')
}
</script>
```

#### **Features**

- ✅ Input de busca de endereço (com ícone de lupa)
- ✅ Botão "Usar minha localização atual (GPS)"
- ✅ Preview de mapa placeholder com pino animado
- ✅ Exibição de coordenadas (lat/lng)
- ✅ Endereço formatado abaixo do mapa
- ✅ Tratamento de erros (permissão negada, timeout, etc.)
- ✅ Dark mode e high contrast completos

#### **Exemplo Visual**

```
┌────────────────────────────────────────┐
│ 📍 Compartilhar Localização           │
│                                        │
│ Buscar endereço:                      │
│ [Digite o endereço...          ] [🔍] │
│                                        │
│           ─── OU ───                   │
│                                        │
│ [📍 Usar minha localização atual]     │
│                                        │
│ ┌──────────────────────────────┐     │
│ │    [Preview do Mapa]         │     │
│ │         📍 (pino)             │     │
│ │                              │     │
│ │ Lat: -23.55050              │     │
│ │ Lng: -46.63330              │     │
│ └──────────────────────────────┘     │
│                                        │
│ 📍 Praça da Sé, Centro - SP           │
│                                        │
│ [Cancelar]  [✓ Confirmar Local]       │
└────────────────────────────────────────┘
```

---

### 3. **ChatPhotoPreview.vue**

Renderiza grid de miniaturas de fotos com preview, contador e opção de remoção.

#### **Props**

```typescript
interface Props {
  fotos: Array<{
    url: string          // URL da imagem (pode ser blob: ou http:)
    nome?: string        // Nome do arquivo
    tamanho?: number     // Tamanho em bytes
  }>
  editavel?: boolean     // Se true, mostra botão de remover
  mostrarContador?: boolean
  maxExibicao?: number   // Máximo de fotos a exibir (padrão: 4)
}
```

#### **Eventos**

```typescript
@visualizar(index: number)  // Clique na foto para visualizar
@remover(index: number)     // Clique no X para remover (se editável)
```

#### **Uso**

```vue
<template>
  <ChatPhotoPreview
    :fotos="fotos"
    :editavel="true"
    @visualizar="handleVisualizar"
    @remover="handleRemover"
  />
</template>

<script setup>
const fotos = [
  { url: 'blob:...', nome: 'foto1.jpg', tamanho: 524288 },
  { url: 'blob:...', nome: 'foto2.jpg', tamanho: 612304 }
]

function handleVisualizar(index) {
  // Abrir modal de visualização em tela cheia
}

function handleRemover(index) {
  fotos.splice(index, 1)
}
</script>
```

#### **Exemplo Visual**

```
┌─────────────────────────────┐
│ [📷 mini1] [📷 mini2]       │
│ [📷 mini3] [📷 mini4]       │
│                             │
│ 📷 4 fotos · 2.1 MB         │
└─────────────────────────────┘
```

**Com mais de 4 fotos:**
```
┌─────────────────────────────┐
│ [📷 mini1] [📷 mini2]       │
│ [📷 mini3] [  +3  ]         │
└─────────────────────────────┘
```

---

### 4. **ChatReviewCard.vue**

Card de revisão final que exibe todos os dados coletados antes de gerar o protocolo.

#### **Props**

```typescript
interface Props {
  dados: {
    servico?: string
    descricao?: string
    localizacao?: {
      latitude: number
      longitude: number
      endereco: string
    }
    fotos?: Array<{ url, nome, tamanho }>
    [key: string]: any  // Campos dinâmicos extras
  }
  confirmando?: boolean  // Estado de carregamento ao gerar protocolo
}
```

#### **Eventos**

```typescript
@confirmar()  // Usuário clicou em "Confirmar e Gerar Protocolo"
@editar()     // Usuário clicou em "Editar"
```

#### **Uso**

```vue
<template>
  <ChatReviewCard
    :dados="sessao.dados_coletados"
    :confirmando="gerando"
    @confirmar="gerarProtocolo"
    @editar="editarDados"
  />
</template>

<script setup>
const sessao = ref({
  dados_coletados: {
    servico: 'Buraco na Via',
    descricao: 'Buraco gigante',
    localizacao: { ... },
    fotos: [ ... ],
    tamanho: 'Grande'
  }
})

const gerando = ref(false)

async function gerarProtocolo() {
  gerando.value = true
  await chatStore.enviarMensagem({ texto: '✅ Confirmo!' })
  gerando.value = false
}

function editarDados() {
  // Permitir usuário digitar correções
}
</script>
```

#### **Exemplo Visual**

```
┌───────────────────────────────────────────┐
│ ✓ Revisão da Solicitação                 │
│ Confirme os dados antes de gerar          │
│ ─────────────────────────────────────────│
│                                           │
│ Serviço Identificado:                    │
│ 🏷️ Buraco na Via                         │
│                                           │
│ Descrição:                               │
│ Buraco gigante na rua                    │
│                                           │
│ Localização:                             │
│ 📍 Praça da Sé, Centro - São Paulo, SP   │
│    -23.55050, -46.63330                  │
│                                           │
│ Fotos Anexadas (3):                      │
│ [📷] [📷] [📷]                           │
│                                           │
│ Tamanho:                                 │
│ Grande                                    │
│                                           │
│ ℹ️ Ao confirmar, um protocolo será       │
│    gerado...                             │
│                                           │
│ [✏️ Editar] [✓ Confirmar e Gerar...]    │
└───────────────────────────────────────────┘
```

---

## 🎬 Integração com ChatSolicitacaoView.vue

### Renderização Condicional baseada em `tipo_acao`

```vue
<template>
  <div v-if="mensagem.tipoAcao" class="mt-3">
    <!-- Confirmação de Serviço -->
    <ChatConfirmation
      v-if="mensagem.tipoAcao === 'confirmar_servico'"
      @confirmar="handleConfirmarServico"
    />

    <!-- Seletor de Localização -->
    <ChatLocationPicker
      v-else-if="mensagem.tipoAcao === 'solicitar_localizacao'"
      @confirmar="handleLocalizacao"
      @cancelar="handleCancelar"
    />

    <!-- Card de Revisão -->
    <ChatReviewCard
      v-else-if="mensagem.tipoAcao === 'revisao_final'"
      :dados="chatStore.sessaoAtual.dados_coletados"
      @confirmar="handleGerarProtocolo"
      @editar="handleEditar"
    />

    <!-- Quick Replies Genéricos -->
    <ChatConfirmation
      v-else-if="mensagem.tipoAcao?.startsWith('quick_reply:')"
      :opcoes="parseQuickReplies(mensagem.tipoAcao)"
      @confirmar="handleQuickReply"
    />
  </div>
</template>
```

---

## 🎨 Suporte a Design System

Todos os componentes seguem o Design System do M.Ouve:

### ✅ **Temas**
- Light Mode
- Dark Mode
- High Contrast (WCAG AAA)

### ✅ **Tokens**
- Cores: `primary`, `gray`, `red`, `green`, `blue`, `yellow`
- Tipografia: Inter (300-900)
- Bordas: `rounded-card`, `rounded-button`, `rounded-avatar`
- Sombras: `shadow-soft`, `shadow-button`, `shadow-elevation-3`

### ✅ **Animações**
- `animate-fade-in`
- `animate-scale-in`
- `animate-slide-up`
- `animate-bounce`
- `animate-pulse`

### ✅ **Responsividade**
- Mobile-first
- Safe area insets (PWA)
- Grids adaptativos

---

## 🧪 Testes dos Componentes

### ChatConfirmation

```bash
✅ Renderiza botões corretamente
✅ Emite evento ao clicar
✅ Desabilita quando disabled=true
✅ Aplica estilo primary corretamente
✅ Renderiza ícones quando fornecidos
```

### ChatLocationPicker

```bash
✅ Busca de endereço funciona (mock)
✅ GPS obtém coordenadas reais
✅ Exibe erro quando permissão negada
✅ Preview do mapa é exibido
✅ Confirmar emite dados corretos
✅ Cancelar emite evento
```

### ChatPhotoPreview

```bash
✅ Renderiza grid de miniaturas
✅ Exibe contador de fotos
✅ Formata tamanho de arquivo
✅ Botão remover funciona (se editável)
✅ Badge +N aparece com mais de 4 fotos
✅ Evento visualizar é emitido
```

### ChatReviewCard

```bash
✅ Exibe todos os campos dos dados
✅ Renderiza preview de fotos
✅ Formata localização corretamente
✅ Botão confirmar emite evento
✅ Botão editar emite evento
✅ Estado confirmando desabilita botões
```

---

## 📦 Estrutura de Arquivos

```
src/
├── components/
│   └── chat/
│       ├── ChatConfirmation.vue
│       ├── ChatLocationPicker.vue
│       ├── ChatPhotoPreview.vue
│       └── ChatReviewCard.vue
├── views/
│   └── ChatSolicitacaoView.vue
└── stores/
    └── chat.js
```

---

## 🔧 Extensões Futuras

### ChatLocationPicker
- [ ] Integrar Leaflet/Google Maps real
- [ ] Geocoding reverso via backend
- [ ] Arrastar pino no mapa
- [ ] Histórico de locais recentes

### ChatPhotoPreview
- [ ] Modal de visualização em tela cheia
- [ ] Zoom e pan nas fotos
- [ ] Edição básica (crop, rotação)
- [ ] Compressão automática

### ChatReviewCard
- [ ] Edição inline de campos
- [ ] Validação de campos obrigatórios
- [ ] Preview de protocolo antes de gerar

### ChatConfirmation
- [ ] Suporte a mais de 2 opções (horizontal scroll)
- [ ] Ícones dinâmicos por contexto

---

## 📚 Referências

- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [Heroicons](https://heroicons.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Geolocation API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)

---

**Versão:** 1.0  
**Data:** Novembro 2026  
**Equipe:** M.Ouve Frontend
