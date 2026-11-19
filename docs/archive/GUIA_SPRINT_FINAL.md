# 🚀 Guia Rápido - Sprint Final Fase 1

## 📋 Resumo Executivo

Este guia documenta as implementações finais da **Fase 1** do M.Ouve.

---

## 🎯 **Funcionalidades Implementadas**

### 1. Dados Dinâmicos no Protocolo

**Local:** `DetalhesProtocoloView.vue` → Seção "Descrição"

**Como usar:**
```javascript
// Protocolo com dados dinâmicos
{
  descricao: "Buraco na rua",
  dados_dinamicos: {
    tamanho: "grande",
    profundidade: "30cm",
    fluxo_veiculos: "alto",
    possui_sinalizacao: false
  }
}
```

**Renderização:**
- Relato livre no topo
- Grid 2 colunas com chaves formatadas
- Valores com tratamento especial (boolean, arrays)

---

### 2. Timeline Scatter-Gather

**Local:** `DetalhesProtocoloView.vue` → Seção "Histórico"

**Como usar:**
```javascript
// Protocolo com ordens de serviço
{
  ordens_servico: [
    {
      id: 1,
      secretaria: "Secretaria de Obras",
      descricao: "Tapa-buraco executado",
      status: "CONCLUIDA",
      criado_em: "2026-11-12T08:30:00Z"
    }
  ]
}
```

**Ordenação:** Automática por timestamp

**Ícones:**
- 🚚 `TruckIcon`: Ordem ativa
- ✓ `CheckCircleIcon`: Ordem concluída

---

### 3. Pesquisa de Satisfação

**Componente:** `ChatSatisfacao.vue`

**Gatilho Backend:**
```json
{
  "mensagem_resposta": {
    "tipo_acao": "pesquisa_satisfacao"
  }
}
```

**Integração no Chat:**
```vue
<ChatSatisfacao
  @enviar="handleEnviarSatisfacao"
  @cancelar="handleCancelarSatisfacao"
/>
```

**Payload enviado:**
```javascript
{
  nota: 5,
  comentario: "Excelente atendimento!"
}
```

---

### 4. LGPD/Anonimização

**Local:** `PerfilUsuarioView.vue` → Aba "Segurança"

**Fluxo:**
1. Usuário clica "Solicitar Anonimização"
2. Dialog de confirmação (irreversível)
3. API call: `POST /api/v1/usuario/anonimizar`
4. Logout automático
5. Redirect para `/login`

**Prazo:** 48 horas (LGPD)

---

## 🔧 **Funções Utilitárias**

### `formatarChave(chave)`

Converte `snake_case` → `Título`

```javascript
formatarChave('fluxo_veiculos')
// Output: "Fluxo Veiculos"
```

### `formatarValor(valor)`

Formata valores dinâmicos:

```javascript
formatarValor(true)        // "Sim"
formatarValor(false)       // "Não"
formatarValor(['a', 'b'])  // "a, b"
formatarValor({x: 1})      // '{"x":1}'
```

---

## 🎨 **Estilos Aplicados**

### **Cores de Timeline**

```css
/* Evento normal */
bg-primary-600

/* Ordem de serviço */
bg-amber-500
ring-amber-200

/* Concluído */
bg-success (green-600)
ring-green-200
```

### **Cores de Satisfação**

```css
/* 1-2 estrelas (Insatisfeito) */
text-red-600

/* 3 estrelas (Neutro) */
text-amber-600

/* 4-5 estrelas (Satisfeito) */
text-green-600
```

---

## 📡 **Endpoints Backend (TODO)**

### 1. Anonimizar Usuário

```http
POST /api/v1/usuario/anonimizar
Authorization: Bearer <token>

Response 200:
{
  "mensagem": "Solicitação registrada",
  "prazo_execucao": "48h"
}
```

### 2. Registrar Avaliação

```http
POST /api/v1/avaliacoes
Authorization: Bearer <token>
Content-Type: application/json

{
  "protocolo_id": "uuid",
  "nota": 5,
  "comentario": "Ótimo atendimento"
}

Response 201:
{
  "id": 123,
  "criado_em": "2026-11-12T10:00:00Z"
}
```

---

## 🧪 **Testes Rápidos**

### **Teste 1: Dados Dinâmicos**

```javascript
// Mock no console do navegador
const protocolo = {
  descricao: "Teste",
  dados_dinamicos: {
    campo_1: "valor1",
    campo_boolean: true,
    campo_array: ["a", "b"]
  }
}
```

### **Teste 2: Scatter-Gather**

```javascript
// Adicionar ordem de serviço mock
protocolo.ordens_servico = [{
  id: 1,
  secretaria: "Obras",
  descricao: "Teste",
  status: "CONCLUIDA",
  criado_em: new Date().toISOString()
}]
```

### **Teste 3: Satisfação**

```javascript
// Backend mock
{
  mensagem_resposta: {
    tipo_acao: "pesquisa_satisfacao"
  }
}
```

---

## 🐛 **Troubleshooting**

### Dados dinâmicos não aparecem

**Causa:** `dados_dinamicos` é `null` ou vazio

**Solução:**
```javascript
// Verificar estrutura
console.log(protocolo.dados_dinamicos)

// Deve ser um objeto não-vazio
// { campo: "valor" }
```

### Ordens de serviço não aparecem

**Causa:** Array `ordens_servico` ausente

**Solução:**
```javascript
// Verificar array
console.log(protocolo.ordens_servico)

// Deve existir e ter itens
// [{ id: 1, ... }]
```

### Satisfação não renderiza

**Causa:** `tipo_acao` incorreto

**Solução:**
```javascript
// Verificar valor exato
tipo_acao === "pesquisa_satisfacao" // deve ser true
```

---

## 📦 **Estrutura de Arquivos**

```
src/
├── components/
│   └── chat/
│       ├── ChatSatisfacao.vue          (novo)
│       ├── ChatConfirmation.vue
│       ├── ChatLocationPicker.vue
│       ├── ChatReviewCard.vue
│       └── ChatPhotoPreview.vue
├── views/
│   ├── DetalhesProtocoloView.vue       (refatorado)
│   ├── ChatSolicitacaoView.vue         (+ satisfação)
│   └── PerfilUsuarioView.vue           (+ LGPD)
└── stores/
    ├── chat.js
    └── protocolos.js
```

---

## 🔑 **Palavras-chave para Busca**

- `dados_dinamicos`
- `ordens_servico`
- `scatter-gather`
- `pesquisa_satisfacao`
- `tipo_acao`
- `anonimizar`
- `formatarChave`
- `formatarValor`
- `timelineCompleta`

---

## 📚 **Referências**

- [LGPD (Lei 13.709/2018)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [Heroicons](https://heroicons.com/)

---

## ✅ **Checklist de Deploy**

Antes de enviar para produção:

- [ ] Build sem erros (`npm run build`)
- [ ] Testes manuais de todas as features
- [ ] Verificar dark mode e high contrast
- [ ] Testar responsividade (mobile/tablet)
- [ ] Validar acessibilidade (tab navigation)
- [ ] Revisar textos e labels
- [ ] Configurar variáveis de ambiente
- [ ] Documentar endpoints backend
- [ ] Configurar CORS
- [ ] Setup de monitoramento (Sentry)

---

**Última atualização:** Novembro 2026  
**Versão:** 1.0 (Fase 1 Completa)
