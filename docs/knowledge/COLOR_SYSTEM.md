# M.Ouve — Sistema de Cores

Sistema de cores semântico adaptado para Ouvidoria e Zeladoria Urbana.

---

## 🎨 Paleta Primary

Base do sistema de design, usada para elementos principais de interface.

```javascript
primary: {
  50:  '#eff6ff',  // Muito claro - Backgrounds hover
  100: '#dbeafe',  // Claro - Backgrounds suaves
  200: '#bfdbfe',  // 
  300: '#93c5fd',  // Tons médios
  400: '#60a5fa',  // 
  500: '#3b82f6',  // ⭐ Principal - Botões, links
  600: '#2563eb',  // Hover states
  700: '#1d4ed8',  // Pressed states
  800: '#1e40af',  // 
  900: '#1e3a8a',  // Escuro
  950: '#172554',  // Muito escuro
}
```

### Uso em Componentes

```vue
<!-- Botão primário -->
<button class="btn-primary">Enviar</button>
<!-- bg-primary-500 hover:bg-primary-600 -->

<!-- Background suave -->
<div class="bg-primary-50 border border-primary-200">
  Conteúdo destacado
</div>

<!-- Texto -->
<p class="text-primary-600">Link ou texto em destaque</p>
```

---

## 🚨 Cores Semânticas

### Danger (Perigo/Erro)

```javascript
danger: {
  light: '#ef4444',  // ⭐ Padrão
  dark:  '#dc2626',  // Hover/pressed
}
```

**Uso:** Erros, exclusões, denúncias graves

```vue
<button class="btn-danger">Excluir</button>
<div class="alert-danger">Erro ao processar</div>
```

### Success (Sucesso)

```javascript
success: {
  light: '#10b981',  // ⭐ Padrão
  dark:  '#059669',  // Hover/pressed
}
```

**Uso:** Confirmações, protocolos resolvidos, elogios

```vue
<button class="btn-success">Confirmar</button>
<div class="alert-success">Protocolo criado!</div>
```

### Warning (Aviso)

```javascript
warning: {
  light: '#f59e0b',  // ⭐ Padrão
  dark:  '#d97706',  // Hover/pressed
}
```

**Uso:** Alertas, reclamações, ações pendentes

```vue
<div class="alert-warning">Atenção: Prazo próximo</div>
```

### Info (Informação)

```javascript
info: {
  light: '#3b82f6',  // ⭐ Padrão (mesma que primary)
  dark:  '#2563eb',
}
```

**Uso:** Mensagens informativas neutras

```vue
<div class="alert-info">Nova funcionalidade disponível</div>
```

---

## 📋 Status de Protocolos - Ouvidoria

Estados do fluxo de manifestações da ouvidoria institucional.

```javascript
ouvidoria: {
  'triagem':     '#3b82f6',  // 🔵 Azul - Análise inicial
  'analise':     '#8b5cf6',  // 🟣 Roxo - Análise detalhada
  'encaminhado': '#f59e0b',  // 🟠 Âmbar - Encaminhado para setor
  'respondido':  '#10b981',  // 🟢 Verde - Respondido
  'arquivado':   '#6b7280',  // ⚪ Cinza - Arquivado
}
```

### Classes CSS

```vue
<!-- Badges -->
<span class="badge-ouvidoria-triagem">Em Triagem</span>
<span class="badge-ouvidoria-analise">Em Análise</span>
<span class="badge-ouvidoria-encaminhado">Encaminhado</span>
<span class="badge-ouvidoria-respondido">Respondido</span>
<span class="badge-ouvidoria-arquivado">Arquivado</span>
```

### Fluxo Visual

```
┌─────────────┐
│  Triagem    │ 🔵 Protocolo criado, aguardando triagem
└──────┬──────┘
       │
       v
┌─────────────┐
│   Análise   │ 🟣 Em análise detalhada pelo setor competente
└──────┬──────┘
       │
       v
┌─────────────┐
│ Encaminhado │ 🟠 Encaminhado para setor responsável
└──────┬──────┘
       │
       v
┌─────────────┐
│ Respondido  │ 🟢 Cidadão recebeu resposta
└──────┬──────┘
       │
       v
┌─────────────┐
│  Arquivado  │ ⚪ Protocolo finalizado e arquivado
└─────────────┘
```

---

## 🏙️ Status de Protocolos - Zeladoria Urbana

Estados do fluxo de solicitações de zeladoria com IA.

```javascript
zeladoria: {
  'triagem-ia':        '#3b82f6',  // 🔵 Azul - Triagem automática (IA)
  'validacao':         '#8b5cf6',  // 🟣 Roxo - Validação humana
  'aguardando-equipe': '#f59e0b',  // 🟠 Âmbar - Aguardando designação
  'em-deslocamento':   '#f59e0b',  // 🟠 Âmbar - Equipe a caminho
  'em-execucao':       '#14b8a6',  // 🟦 Teal - Trabalho em andamento
  'concluido':         '#10b981',  // 🟢 Verde - Concluído
  'nao-procedente':    '#6b7280',  // ⚪ Cinza - Não procedente
}
```

### Classes CSS

```vue
<!-- Badges -->
<span class="badge-zeladoria-triagem-ia">Triagem IA</span>
<span class="badge-zeladoria-validacao">Em Validação</span>
<span class="badge-zeladoria-aguardando-equipe">Aguardando Equipe</span>
<span class="badge-zeladoria-em-deslocamento">Equipe em Deslocamento</span>
<span class="badge-zeladoria-em-execucao">Em Execução</span>
<span class="badge-zeladoria-concluido">Concluído</span>
<span class="badge-zeladoria-nao-procedente">Não Procedente</span>
```

### Fluxo Visual

```
┌─────────────────┐
│   Triagem IA    │ 🔵 IA analisa e categoriza automaticamente
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Validação     │ 🟣 Gestor valida análise da IA
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Aguardando      │ 🟠 Aguarda designação de equipe
│ Equipe          │
└────────┬────────┘
         │
         v
┌─────────────────┐
│      Em         │ 🟠 Equipe foi designada e está indo ao local
│ Deslocamento    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│      Em         │ 🟦 Equipe está executando o serviço
│   Execução      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Concluído     │ 🟢 Serviço executado com sucesso
└─────────────────┘

         OU

┌─────────────────┐
│      Não        │ ⚪ Solicitação não procede
│   Procedente    │
└─────────────────┘
```

---

## 💬 Tipos de Manifestação (Ouvidoria)

Cores por tipo de manifestação do cidadão.

```javascript
manifestacao: {
  'denuncia':   '#ef4444',  // 🔴 Vermelho
  'reclamacao': '#f59e0b',  // 🟠 Âmbar
  'sugestao':   '#3b82f6',  // 🔵 Azul
  'elogio':     '#10b981',  // 🟢 Verde
}
```

### Classes CSS

```vue
<span class="badge-manifestacao-denuncia">🚨 Denúncia</span>
<span class="badge-manifestacao-reclamacao">😤 Reclamação</span>
<span class="badge-manifestacao-sugestao">💡 Sugestão</span>
<span class="badge-manifestacao-elogio">👏 Elogio</span>
```

### Uso em Cards

```vue
<div class="card" :class="{
  'border-l-4 border-red-500': tipo === 'denuncia',
  'border-l-4 border-amber-500': tipo === 'reclamacao',
  'border-l-4 border-blue-500': tipo === 'sugestao',
  'border-l-4 border-green-500': tipo === 'elogio',
}">
  <!-- Conteúdo -->
</div>
```

---

## 🏗️ Categorias de Zeladoria

Cores por categoria de problema urbano.

```javascript
categoria: {
  'via-publica':  '#3b82f6',  // 🔵 Azul
  'iluminacao':   '#f59e0b',  // 🟠 Âmbar
  'limpeza':      '#10b981',  // 🟢 Verde
  'calcada':      '#8b5cf6',  // 🟣 Roxo
  'arborizacao':  '#059669',  // 🌲 Verde escuro
  'sinalizacao':  '#dc2626',  // 🔴 Vermelho
}
```

### Uso em Ícones

```vue
<!-- Via Pública -->
<div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
  <svg class="w-6 h-6 text-white">🛣️</svg>
</div>

<!-- Iluminação -->
<div class="w-12 h-12 bg-amber-500 rounded-lg flex items-center justify-center">
  <svg class="w-6 h-6 text-white">💡</svg>
</div>
```

---

## ⚡ Níveis de Urgência (IA)

Cores para classificação automática de urgência pela IA.

```javascript
urgencia: {
  'baixa':    '#10b981',  // 🟢 Verde
  'media':    '#f59e0b',  // 🟠 Âmbar
  'alta':     '#ef4444',  // 🔴 Vermelho
  'critica':  '#dc2626',  // 🔴 Vermelho escuro + negrito
}
```

### Classes CSS

```vue
<span class="badge-urgencia-baixa">Urgência Baixa</span>
<span class="badge-urgencia-media">Urgência Média</span>
<span class="badge-urgencia-alta">Urgência Alta</span>
<span class="badge-urgencia-critica">🚨 Urgência Crítica</span>
```

### Uso em Alertas

```vue
<div v-if="protocolo.urgencia === 'critica'" class="alert-danger">
  <svg class="w-5 h-5">⚠️</svg>
  <div>
    <strong>Protocolo Crítico</strong>
    <p>Requer atenção imediata</p>
  </div>
</div>
```

---

## 🎭 Compatibilidade Gov.br

Mantidas para componentes específicos do governo.

```javascript
'gov-blue': {
  'warm':  '#1351B4',  // Azul Gov.br oficial
  'vivid': '#155BCB',
  'deep':  '#0C326F',
},
'gov-green': {
  'cool':  '#168821',
  'vivid': '#1B7D28',
},
'gov-yellow': {
  'vivid': '#FFCD07',
},
'gov-gray': {
  'light':  '#F8F8F8',
  'medium': '#E5E5E5',
  'dark':   '#333333',
}
```

**Uso:** Headers governamentais, logos, elementos institucionais.

---

## 📊 Exemplos de Uso Completos

### Dashboard com Status

```vue
<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">
        Protocolo #{{ protocolo.id }}
      </h3>
      <span :class="getStatusBadge(protocolo.status)">
        {{ getStatusLabel(protocolo.status) }}
      </span>
    </div>

    <div v-if="protocolo.urgencia" class="mb-3">
      <span :class="getUrgenciaBadge(protocolo.urgencia)">
        {{ protocolo.urgencia.toUpperCase() }}
      </span>
    </div>

    <p class="text-gray-600">{{ protocolo.descricao }}</p>
  </div>
</template>

<script setup>
function getStatusBadge(status) {
  const badges = {
    'triagem_ia': 'badge-zeladoria-triagem-ia',
    'em_deslocamento': 'badge-zeladoria-em-deslocamento',
    'concluido': 'badge-zeladoria-concluido',
  }
  return badges[status] || 'badge-zeladoria-triagem-ia'
}

function getUrgenciaBadge(nivel) {
  return `badge-urgencia-${nivel}`
}
</script>
```

### Botões de Ação

```vue
<!-- Confirmar ação -->
<button class="btn-success">
  ✓ Confirmar Resolução
</button>

<!-- Ação destrutiva -->
<button class="btn-danger">
  × Rejeitar Protocolo
</button>

<!-- Ação secundária -->
<button class="btn-secondary">
  Solicitar Informações
</button>
```

### Alertas Contextuais

```vue
<!-- Alerta de IA -->
<div class="alert-info">
  <svg class="w-5 h-5">🤖</svg>
  <div>
    <strong>Análise Automática</strong>
    <p>A IA detectou que este protocolo pode ser similar a #PROT-2024-015</p>
  </div>
</div>

<!-- Alerta de sucesso -->
<div class="alert-success">
  <svg class="w-5 h-5">✓</svg>
  <div>
    <strong>Protocolo Criado</strong>
    <p>Número: PROT-2024-042</p>
  </div>
</div>
```

---

## 🔧 Utilitários Tailwind

### Backgrounds

```html
<div class="bg-primary-500">Primary</div>
<div class="bg-success">Sucesso</div>
<div class="bg-danger">Perigo</div>
<div class="bg-zeladoria-em-execucao">Status Zeladoria</div>
```

### Texto

```html
<p class="text-primary-600">Texto primário</p>
<p class="text-success-dark">Texto de sucesso</p>
<p class="text-danger">Texto de erro</p>
```

### Bordas

```html
<div class="border-2 border-primary-500">Borda primária</div>
<div class="ring-2 ring-success">Ring de sucesso</div>
```

---

## 📋 Migration Guide

### Atualizando Código Existente

**Antes:**
```vue
<button class="bg-gov-blue-warm hover:bg-gov-blue-deep">
  Botão
</button>
```

**Depois:**
```vue
<button class="btn-primary">
  Botão
</button>
```

**Antes:**
```vue
<span class="badge-pending">Em análise</span>
```

**Depois:**
```vue
<span class="badge-zeladoria-triagem-ia">Em Triagem IA</span>
```

---

## 🎨 Paleta Completa (Quick Reference)

```
Primary:        ████████████ #3b82f6
Success:        ████████████ #10b981
Warning:        ████████████ #f59e0b
Danger:         ████████████ #ef4444

Triagem IA:     ████████████ #3b82f6
Validação:      ████████████ #8b5cf6
Aguardando:     ████████████ #f59e0b
Em Execução:    ████████████ #14b8a6
Concluído:      ████████████ #10b981

Denúncia:       ████████████ #ef4444
Reclamação:     ████████████ #f59e0b
Sugestão:       ████████████ #3b82f6
Elogio:         ████████████ #10b981
```

---

**Sistema de cores atualizado em:** 09/11/2024  
**Versão:** 2.0  
**Baseado em:** JSON fornecido pelo cliente
