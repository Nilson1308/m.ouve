# 📡 Contrato da API - Chat Conversacional M.Ouve

## 📋 Visão Geral

Este documento especifica o contrato entre o **frontend Vue 3** e o **backend Django** para a funcionalidade de chat conversacional com IA (RAG + LLM).

---

## 🔌 Endpoints

### 1. Iniciar Sessão de Chat

Cria uma nova sessão conversacional e retorna a mensagem de boas-vindas da IA.

#### **POST** `/api/v1/chat/sessao`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "categoria_inicial": "Zeladoria Urbana"
}
```

**Response (201 Created):**
```json
{
  "sessao": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "categoria_inicial": "Zeladoria Urbana",
    "status": "EM_ANDAMENTO",
    "servico_identificado": null,
    "dados_coletados": {},
    "protocolo_final_id": null,
    "criado_em": "2026-11-11T10:00:00Z",
    "atualizado_em": "2026-11-11T10:00:00Z"
  },
  "mensagem": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "autor": "ia",
    "conteudo_texto": "Olá! Como posso ajudar você com a Zeladoria Urbana hoje?",
    "localizacao": null,
    "tipo_acao": null,
    "criado_em": "2026-11-11T10:00:00Z"
  }
}
```

---

### 2. Enviar Mensagem e Receber Resposta da IA

Envia mensagem do cidadão (texto, localização e/ou arquivos) e recebe resposta da IA.

#### **POST** `/api/v1/chat/interagir`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json  (ou multipart/form-data se houver arquivos)
```

#### **Opção 1: JSON (sem arquivos)**

**Request Body:**
```json
{
  "sessao_id": "550e8400-e29b-41d4-a716-446655440000",
  "texto": "Tem um buraco gigante na minha rua",
  "localizacao": null
}
```

#### **Opção 2: JSON com Localização**

**Request Body:**
```json
{
  "sessao_id": "550e8400-e29b-41d4-a716-446655440000",
  "texto": "Aqui está a localização do problema",
  "localizacao": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco": "Praça da Sé, Centro - São Paulo, SP"
  }
}
```

#### **Opção 3: Multipart (com fotos)**

**Content-Type:** `multipart/form-data`

**Form Data:**
```
sessao_id: 550e8400-e29b-41d4-a716-446655440000
texto: Aqui estão as fotos do buraco
localizacao: {"latitude": -23.5505, "longitude": -46.6333, "endereco": "Rua Exemplo, 123"}
midia: [arquivo1.jpg, arquivo2.jpg, arquivo3.jpg]
```

**Campos:**
- `sessao_id` (string, obrigatório): UUID da sessão
- `texto` (string, opcional): Mensagem de texto do cidadão
- `localizacao` (JSON string, opcional): Objeto com latitude, longitude e endereco
- `midia` (file[], opcional): Array de arquivos (fotos, vídeos, áudio)

---

**Response (200 OK):**

```json
{
  "sessao": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "categoria_inicial": "Zeladoria Urbana",
    "status": "EM_ANDAMENTO",
    "servico_identificado": {
      "id": 42,
      "nome": "Buraco na Via",
      "categoria": "Zeladoria Urbana"
    },
    "dados_coletados": {
      "descricao": "Buraco gigante na rua",
      "tamanho": "grande",
      "localizacao": {
        "latitude": -23.5505,
        "longitude": -46.6333,
        "endereco": "Praça da Sé, Centro"
      }
    },
    "protocolo_final_id": null,
    "criado_em": "2026-11-11T10:00:00Z",
    "atualizado_em": "2026-11-11T10:05:30Z"
  },
  "mensagem_cidadao": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "autor": "cidadao",
    "conteudo_texto": "Tem um buraco gigante na minha rua",
    "localizacao": null,
    "tipo_acao": null,
    "criado_em": "2026-11-11T10:05:00Z"
  },
  "mensagem_resposta": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "autor": "ia",
    "conteudo_texto": "Entendi que se trata de um buraco na via. Vou precisar confirmar algumas informações. Você está falando sobre um buraco na rua, correto?",
    "localizacao": null,
    "tipo_acao": "confirmar_servico",
    "criado_em": "2026-11-11T10:05:10Z"
  },
  "midia_recebida": 0,
  "protocolo": null
}
```

---

**Response (200 OK - Fluxo Finalizado com Protocolo):**

```json
{
  "sessao": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "FINALIZADO",
    "protocolo_final_id": "990e8400-e29b-41d4-a716-446655440099"
  },
  "mensagem_cidadao": {
    "id": "aa0e8400-e29b-41d4-a716-446655440004",
    "autor": "cidadao",
    "conteudo_texto": "✅ Confirmo todos os dados. Pode gerar o protocolo!",
    "localizacao": null,
    "tipo_acao": null,
    "criado_em": "2026-11-11T10:15:00Z"
  },
  "mensagem_resposta": {
    "id": "bb0e8400-e29b-41d4-a716-446655440005",
    "autor": "ia",
    "conteudo_texto": "Perfeito! Seu protocolo foi gerado com sucesso. Anote o código para acompanhar: OUVIA-2026-123456",
    "localizacao": null,
    "tipo_acao": "fim_conversa",
    "criado_em": "2026-11-11T10:15:05Z"
  },
  "midia_recebida": 3,
  "protocolo": {
    "codigo": "OUVIA-2026-123456",
    "id": "990e8400-e29b-41d4-a716-446655440099"
  }
}
```

---

## 🎬 Comandos de Ação da IA (`tipo_acao`)

O campo `tipo_acao` da `mensagem_resposta` permite ao frontend renderizar componentes interativos específicos.

### Comandos Disponíveis

| Comando | Descrição | UI Frontend |
|---------|-----------|-------------|
| `confirmar_servico` | IA identificou o serviço e pede confirmação | Renderiza botões "Sim" / "Não" |
| `solicitar_localizacao` | IA precisa da localização do problema | Renderiza `ChatLocationPicker` (busca de endereço + GPS + mapa placeholder) |
| `solicitar_foto` | IA solicita fotos do problema | Destaca botão de foto no input bar |
| `quick_reply:Opção1,Opção2,Opção3` | IA oferece opções rápidas | Renderiza chips/botões com as opções separadas por vírgula |
| `revisao_final` | IA coletou todos os dados e exibe resumo | Renderiza `ChatReviewCard` com os `dados_coletados` |
| `fim_conversa` | Protocolo gerado, conversa encerrada | Frontend exibe mensagem de sucesso e redireciona para `/protocolo/:id` |
| `null` ou ausente | Mensagem de texto pura | Apenas exibe o balão de texto |

---

### Exemplo de Fluxo com Comandos

#### **1. Confirmação de Serviço**

**IA envia:**
```json
{
  "conteudo_texto": "Você está relatando um buraco na via, correto?",
  "tipo_acao": "confirmar_servico"
}
```

**Frontend renderiza:**
```
┌──────────────────────────────────────┐
│ Você está relatando um buraco na    │
│ via, correto?                        │
└──────────────────────────────────────┘
            [Sim]  [Não]
```

**Cidadão clica "Sim":**
```json
{
  "sessao_id": "...",
  "texto": "Sim, é isso mesmo!"
}
```

---

#### **2. Solicitação de Localização**

**IA envia:**
```json
{
  "conteudo_texto": "Perfeito! Onde está localizado o buraco?",
  "tipo_acao": "solicitar_localizacao"
}
```

**Frontend renderiza:**
```
┌────────────────────────────────────────────┐
│ 📍 Compartilhar Localização               │
│                                            │
│ Buscar endereço:                          │
│ [_______________________________] [🔍]    │
│                                            │
│           ─── OU ───                       │
│                                            │
│ [📍 Usar minha localização atual (GPS)]   │
│                                            │
│ [Preview do Mapa com Pino]                │
│                                            │
│ [Cancelar]  [✓ Confirmar Local]           │
└────────────────────────────────────────────┘
```

**Cidadão confirma localização:**
```json
{
  "sessao_id": "...",
  "texto": "📍 Praça da Sé, Centro - São Paulo, SP",
  "localizacao": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco": "Praça da Sé, Centro - São Paulo, SP"
  }
}
```

---

#### **3. Quick Replies**

**IA envia:**
```json
{
  "conteudo_texto": "Qual o tamanho aproximado do buraco?",
  "tipo_acao": "quick_reply:Pequeno,Médio,Grande"
}
```

**Frontend renderiza:**
```
┌──────────────────────────────────────┐
│ Qual o tamanho aproximado do buraco? │
└──────────────────────────────────────┘
        [Pequeno] [Médio] [Grande]
```

**Cidadão clica "Grande":**
```json
{
  "sessao_id": "...",
  "texto": "Grande"
}
```

---

#### **4. Revisão Final**

**IA envia:**
```json
{
  "conteudo_texto": "Ótimo! Aqui está o resumo da sua solicitação:",
  "tipo_acao": "revisao_final"
}
```

**Backend também atualiza `sessao.dados_coletados`:**
```json
{
  "dados_coletados": {
    "servico": "Buraco na Via",
    "descricao": "Buraco gigante na rua",
    "tamanho": "Grande",
    "localizacao": {
      "latitude": -23.5505,
      "longitude": -46.6333,
      "endereco": "Praça da Sé, Centro - São Paulo, SP"
    },
    "fotos": [
      { "url": "/media/anexos/foto1.jpg", "nome": "foto1.jpg", "tamanho": 524288 },
      { "url": "/media/anexos/foto2.jpg", "nome": "foto2.jpg", "tamanho": 612304 }
    ]
  }
}
```

**Frontend renderiza:**
```
┌─────────────────────────────────────────────────┐
│ ✓ Revisão da Solicitação                       │
│ ───────────────────────────────────────────────│
│                                                 │
│ Serviço Identificado:                          │
│ 🏷️ Buraco na Via                               │
│                                                 │
│ Descrição:                                     │
│ Buraco gigante na rua                          │
│                                                 │
│ Localização:                                   │
│ 📍 Praça da Sé, Centro - São Paulo, SP         │
│    -23.55050, -46.63330                        │
│                                                 │
│ Fotos Anexadas (2):                            │
│ [📷 miniatura1] [📷 miniatura2]                │
│                                                 │
│ ℹ️ Ao confirmar, um protocolo será gerado...   │
│                                                 │
│ [✏️ Editar]  [✓ Confirmar e Gerar Protocolo]  │
└─────────────────────────────────────────────────┘
```

**Cidadão clica "Confirmar":**
```json
{
  "sessao_id": "...",
  "texto": "✅ Confirmo todos os dados. Pode gerar o protocolo!"
}
```

---

#### **5. Fim da Conversa com Protocolo**

**Backend responde:**
```json
{
  "mensagem_resposta": {
    "conteudo_texto": "Protocolo gerado com sucesso! Código: OUVIA-2026-123456",
    "tipo_acao": "fim_conversa"
  },
  "protocolo": {
    "codigo": "OUVIA-2026-123456",
    "id": "990e8400-e29b-41d4-a716-446655440099"
  }
}
```

**Frontend:**
1. Exibe mensagem de sucesso no chat
2. Aguarda 3 segundos
3. Redireciona para `/protocolo/990e8400-e29b-41d4-a716-446655440099`

---

## 📦 Estrutura de Dados

### Objeto `Sessao`

```typescript
interface Sessao {
  id: string                    // UUID
  categoria_inicial: string     // Nome da categoria
  status: 'EM_ANDAMENTO' | 'FINALIZADO' | 'CANCELADO'
  servico_identificado: Servico | null
  dados_coletados: object       // Dados dinâmicos coletados durante a conversa
  protocolo_final_id: string | null
  criado_em: string            // ISO 8601
  atualizado_em: string        // ISO 8601
}
```

### Objeto `Mensagem`

```typescript
interface Mensagem {
  id: string                   // UUID
  autor: 'ia' | 'cidadao'
  conteudo_texto: string
  localizacao: {
    latitude: number
    longitude: number
  } | null
  tipo_acao: string | null     // Comando de ação (ver tabela acima)
  criado_em: string           // ISO 8601
}
```

### Objeto `Protocolo`

```typescript
interface Protocolo {
  codigo: string               // Ex: "OUVIA-2026-123456"
  id: string                   // UUID
}
```

---

## 🔐 Autenticação

Todos os endpoints requerem token JWT no header:

```
Authorization: Bearer <token>
```

**Token Expirado:**
- Retorna `401 Unauthorized`
- Frontend deve tentar refresh token automaticamente
- Se refresh falhar, redirecionar para `/login`

---

## ⚠️ Tratamento de Erros

### Erro 400 (Bad Request)

**Exemplo: Sessão não encontrada**
```json
{
  "sessao_id": ["Sessão não encontrada."]
}
```

**Exemplo: Sessão finalizada**
```json
{
  "sessao_id": ["Esta sessão não aceita novas mensagens."]
}
```

### Erro 401 (Unauthorized)

```json
{
  "detail": "Token expirado ou inválido."
}
```

### Erro 500 (Internal Server Error)

```json
{
  "detail": "Erro interno do servidor. Tente novamente mais tarde."
}
```

**Frontend:**
- Captura erro HTTP
- Exibe mensagem de erro como bubble vermelho no chat
- Não bloqueia interface (usuário pode tentar novamente)

---

## 🧪 Exemplos de Uso

### Exemplo Completo de Fluxo

```javascript
// 1. Iniciar sessão
const { sessao, mensagem } = await chatService.iniciarSessao('Zeladoria Urbana')
// IA: "Olá! Como posso ajudar você com a Zeladoria Urbana hoje?"

// 2. Cidadão relata problema
await chatService.interagir(sessao.id, {
  texto: 'Tem um buraco na minha rua'
})
// IA: "Você está relatando um buraco na via, correto?" (tipo_acao: confirmar_servico)

// 3. Cidadão confirma
await chatService.interagir(sessao.id, {
  texto: 'Sim'
})
// IA: "Perfeito! Onde está localizado o buraco?" (tipo_acao: solicitar_localizacao)

// 4. Cidadão envia localização
await chatService.interagir(sessao.id, {
  texto: '📍 Praça da Sé',
  localizacao: {
    latitude: -23.5505,
    longitude: -46.6333,
    endereco: 'Praça da Sé, Centro - São Paulo, SP'
  }
})
// IA: "Qual o tamanho aproximado?" (tipo_acao: quick_reply:Pequeno,Médio,Grande)

// 5. Cidadão escolhe opção
await chatService.interagir(sessao.id, {
  texto: 'Grande'
})
// IA: "Você pode enviar fotos?" (tipo_acao: solicitar_foto)

// 6. Cidadão envia fotos (multipart)
await chatService.interagir(sessao.id, {
  texto: 'Aqui estão as fotos',
  arquivos: [foto1, foto2, foto3]
})
// IA: "Aqui está o resumo..." (tipo_acao: revisao_final)

// 7. Cidadão confirma
const { protocolo } = await chatService.interagir(sessao.id, {
  texto: '✅ Confirmo!'
})
// protocolo: { codigo: "OUVIA-2026-123456", id: "..." }

// 8. Redirecionar para detalhes do protocolo
router.push(`/protocolo/${protocolo.id}`)
```

---

## 📱 Suporte a Multipart/Form-Data

### Quando Usar

- Sempre que houver **arquivos** (fotos, vídeos, áudio) no envio
- Backend detecta `Content-Type: multipart/form-data`

### Como Enviar (Frontend)

```javascript
// Caso 1: Sem arquivos (JSON puro)
await axios.post('/chat/interagir', {
  sessao_id: '...',
  texto: 'Mensagem de texto',
  localizacao: { ... }
})

// Caso 2: Com arquivos (FormData)
const formData = new FormData()
formData.append('sessao_id', sessaoId)
formData.append('texto', 'Aqui estão as fotos')
formData.append('localizacao', JSON.stringify({ latitude, longitude, endereco }))

arquivos.forEach(arquivo => {
  formData.append('midia', arquivo)
})

await axios.post('/chat/interagir', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

### Limites

- **Tamanho máximo por arquivo:** 10 MB
- **Número máximo de arquivos por envio:** 10
- **Formatos aceitos:** JPEG, PNG, GIF, WebP, MP4, MOV, MP3, WAV

---

## 📊 Fluxograma de Estados

```
┌──────────────┐
│ POST /sessao │
└──────┬───────┘
       │
       v
┌────────────────┐
│ EM_ANDAMENTO   │
│ (Conversando)  │
└────────┬───────┘
         │
         │ (Loop de mensagens)
         │ POST /interagir
         │
         v
   ┌─────────────┐
   │ tipo_acao?  │
   └─────┬───────┘
         │
    ┌────┴────────────┬──────────────┬────────────┐
    │                 │              │            │
    v                 v              v            v
confirmar_servico  solicitar_    quick_reply  revisao_final
                   localizacao
    │                 │              │            │
    └─────────────────┴──────────────┴────────────┘
                      │
                      v
              ┌──────────────┐
              │ Cidadão      │
              │ confirma     │
              └──────┬───────┘
                     │
                     v
            ┌─────────────────┐
            │ fim_conversa    │
            │ protocolo: {...}│
            └─────────┬───────┘
                      │
                      v
              ┌──────────────┐
              │ FINALIZADO   │
              └──────────────┘
```

---

## 📝 Notas de Implementação

### Backend (Django)

- LLM deve analisar histórico da sessão e `dados_coletados` para determinar qual `tipo_acao` enviar
- `revisao_final` só deve ser enviado quando **todos** os campos obrigatórios do serviço estiverem coletados
- Protocolo só é criado quando cidadão confirmar explicitamente na revisão final

### Frontend (Vue 3)

- Store Pinia (`chat.js`) gerencia estado da sessão e mensagens
- Componentes reativos renderizam UI baseada em `tipo_acao`
- Scroll automático para última mensagem após cada interação
- Preview de fotos usando `URL.createObjectURL(file)`
- Cleanup de URLs temporárias ao desmontar componente

---

## ⏳ Chat assíncrono (Celery)

### POST `/api/v1/chat/interagir` (202 Accepted)

Enfileira o processamento do LLM. **Não** retorna `mensagem_resposta` no corpo.

```json
{
  "status": "processando",
  "task_id": "celery-task-uuid",
  "sessao": { "...": "..." },
  "mensagem_cidadao": { "...": "..." },
  "midia_recebida": 0
}
```

### GET `/api/v1/chat/sessao/<sessao_id>/mensagens`

Polling recomendado a cada **2 segundos** até `ia_processando` ser `false` e existir mensagem `ia` após a última do cidadão.

```json
{
  "sessao": { "...": "..." },
  "mensagens": [ { "autor": "cidadao", "...": "..." }, { "autor": "ia", "...": "..." } ],
  "protocolo": { "id": "uuid", "codigo": "PROT-2026-001" },
  "ia_processando": false
}
```

---

## ⭐ Avaliações (CSAT)

Modelo: `AvaliacaoProtocolo` — **OneToOne** com `Protocolo` (`related_name=avaliacao`). Espelha `nota_satisfacao` / `comentario_satisfacao` no protocolo para dashboards.

**Regras:** protocolo `status=resolvido`; pertence ao cidadão autenticado; uma única avaliação por protocolo (400 se repetir).

### POST `/api/v1/app/protocolos/<uuid>/avaliar` *(PWA — preferencial)*

**Auth:** Bearer JWT (cidadão)

```json
{
  "nota": 5,
  "comentario": "Opcional (máx. 500 caracteres)"
}
```

**Response 201 (PWA):**

```json
{
  "nota": 5,
  "comentario": "Opcional",
  "criada_em": "2026-11-19T12:00:00Z"
}
```

**Erros comuns:** `400` — protocolo não resolvido ou já avaliado (`"Este protocolo já foi avaliado."`); `404` — protocolo inexistente ou de outro usuário.

#### Detalhe do protocolo (cidadão) — `GET /api/v1/protocolos/<id>`

Campos adicionais no serializer de detalhe:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `pode_avaliar` | bool | `true` se `status=resolvido` e ainda não há `AvaliacaoProtocolo` |
| `avaliacao` | objeto \| null | `{ "nota", "comentario", "criada_em" }` quando já avaliado |

### POST `/api/v1/chat/sessao/<sessao_id>/avaliar-abertura`

Pesquisa exibida no chat logo após o registro do protocolo (`tipo_acao: pesquisa_satisfacao`). Mede a **experiência de abertura** da solicitação, **não** o CSAT de conclusão.

**Auth:** Bearer JWT (dono da sessão)

**Regras:** sessão com `status=finalizado_protocolo`, `protocolo_final` definido; uma avaliação por sessão.

```json
{
  "nota": 5,
  "comentario": "Opcional"
}
```

**Response 201:** `{ "nota", "comentario", "protocolo_id", "avaliacao_abertura_em" }`

---

### POST `/api/v1/avaliacoes` *(legado — CSAT de protocolo resolvido)*

```json
{
  "protocolo_id": "uuid",
  "nota": 5,
  "comentario": "Opcional"
}
```

- **Requer** `Protocolo.status = resolvido`. Protocolos recém-abertos devem usar `avaliar-abertura` no chat (acima) ou `POST /app/protocolos/<id>/avaliar` após conclusão.

**Response 201:** mesmo formato acima (`criada_em` no lugar de `criado_em`).

---

## 🔔 Notificações do Cidadão (PWA) — Onda 4

Modelos: `NotificacaoCidadao` (in-app) e `PushSubscription` (Web Push VAPID).  
Gatilhos assíncronos: mudança de status do protocolo (`em_andamento`, `aguardando_revisao`, `resolvido`) e nova resposta da IA no chat → `NotificacaoCidadao` + task Celery `enviar_notificacao_push_task`.

> **Rotas canônicas vs legado (cidadão):** use **`/api/v1/app/notificacoes`** no PWA atual (lista, marcar lida, push-subscribe, VAPID). A rota **`/api/v1/notificacoes`** (`core_auth`) permanece apenas por compatibilidade com integrações antigas; novos desenvolvimentos devem adotar `/app/notificacoes`.

### Variáveis de ambiente (Web Push)

| Variável | Descrição |
|----------|-----------|
| `VAPID_PUBLIC_KEY` | Chave pública VAPID (exposta ao PWA para `pushManager.subscribe`) |
| `VAPID_PRIVATE_KEY` | Chave privada VAPID (apenas backend / worker Celery) |
| `VAPID_ADMIN_EMAIL` | Claim `sub` VAPID (ex.: `mailto:ouvidoria@municipio.gov.br`) |
| `PWA_FRONTEND_BASE_URL` | Opcional — URL absoluta no campo `data.url` do push |

Se VAPID não estiver configurado, as notificações **in-app** continuam sendo gravadas; o push é ignorado com log.

### GET `/api/v1/app/notificacoes`

**Auth:** Bearer JWT (cidadão)

**Query:** `nao_lidas=true` (filtra não lidas), `limit` (máx. 200)

**Response 200:**

```json
{
  "results": [
    {
      "id": "uuid",
      "titulo": "Protocolo resolvido",
      "mensagem": "Sua solicitação PROT-… foi respondida…",
      "lida": false,
      "criada_em": "2026-11-19T15:00:00Z",
      "protocolo_id": "uuid",
      "protocolo_codigo": "PROT-2026-001"
    }
  ],
  "count": 1,
  "nao_lidas": 1
}
```

Header opcional: `X-Notificacoes-Nao-Lidas: <int>` (espelha `nao_lidas`).

### PATCH `/api/v1/app/notificacoes/<uuid>/marcar-lida`

**Response 200:**

```json
{
  "sucesso": true,
  "notificacao": { "id": "…", "lida": true, "…": "…" },
  "marcada_em": "2026-11-19T15:01:00Z"
}
```

**Erros:** `404` — notificação inexistente ou de outro usuário.

### GET `/api/v1/app/notificacoes/vapid-public-key`

**Auth:** Bearer JWT (cidadão)

Retorna a **Application Server Key** (base64url) para `pushManager.subscribe({ applicationServerKey })`, sem expor a chave privada.

**Response 200:**

```json
{
  "configurado": true,
  "vapid_public_key": "BI0rLvZvDwi8…"
}
```

**Response 503:** VAPID não configurado (`configurado: false`, `vapid_public_key: null`).

**Geração de chaves (ops):** `python manage.py generate_vapid --output-dir /caminho/seguro --email mailto:ouvidoria@municipio.gov.br`

### POST `/api/v1/app/notificacoes/push-subscribe`

Registra ou atualiza inscrição Web Push (`endpoint` é chave única global).

**Body (formato Push API do navegador):**

```json
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/…",
  "keys": {
    "p256dh": "…",
    "auth": "…"
  }
}
```

**Response 201:**

```json
{
  "id": "uuid",
  "endpoint": "https://…",
  "criada_em": "2026-11-19T14:00:00Z",
  "atualizado_em": "2026-11-19T14:00:00Z"
}
```

---

## 🔒 LGPD — Anonimização

### GET `/api/v1/usuario/me` · GET `/api/v1/auth/me`

Retorna o perfil do usuário autenticado (mesmo formato de `user` no login/registro).

**Auth:** Bearer JWT

**Response 200 (campos principais):**

```json
{
  "id": "uuid",
  "cpf": "000.000.000-00",
  "nome": "Maria Silva",
  "email": "maria@prefeitura.gov.br",
  "telefone": "(11) 98765-4321",
  "avatar": null,
  "endereco": null,
  "perfil": {
    "id": "uuid",
    "codigo": "ouvidor",
    "nome": "Ouvidor"
  },
  "unidade_administrativa": {
    "id": "uuid",
    "nome": "Secretaria de Zeladoria",
    "sigla": "SEZEL"
  },
  "is_superadmin": false,
  "permissoes": [
    "mapa_ia.criar",
    "mapa_ia.ler",
    "mesa_trabalho.criar",
    "mesa_trabalho.ler"
  ],
  "tipo_usuario": "backoffice",
  "is_backoffice": true,
  "is_cidadao": false
}
```

| Campo | Descrição |
|-------|-----------|
| `permissoes` | Lista ordenada de códigos `modulo.acao` (matriz CRUD) **ativos** no perfil. Super Admin recebe o catálogo completo. Cidadão sem perfil: `[]`. |
| `tipo_usuario` | `"backoffice"` ou `"cidadao"` — usado pelo frontend para rotear login PWA vs backoffice. |
| `is_superadmin` | `true` se `regras.super_admin` ou `is_superuser` Django. |
| `perfil` | `null` para cidadãos. |
| `unidade_administrativa` | `null` se sem vínculo. |
| `avatar` | URL absoluta da foto de perfil (`null` se não houver). Mesma convenção dos demais anexos (`PUBLIC_BASE_URL` + `/media/...` ou `request.build_absolute_uri`). |

---

### POST · PATCH · DELETE `/api/v1/usuario/me/avatar` · `/api/v1/auth/me/avatar`

Gerencia a foto de perfil do usuário autenticado (cidadão PWA e servidor backoffice).

**Auth:** Bearer JWT

#### Upload ou substituição (POST ou PATCH)

- **Content-Type:** `multipart/form-data`
- **Campo:** `avatar` (arquivo)
- **Regras:** apenas `image/jpeg`, `image/png` ou `image/webp`; tamanho máximo **2 MB**.
- **Response 200:** objeto completo do usuário (mesmo formato de `GET /auth/me`), com `avatar` atualizado.
- **Response 400:** corpo com `avatar` ou `error` descrevendo formato/tamanho inválido.

Ao substituir, o arquivo anterior é removido do storage.

#### Remoção

- **DELETE** no mesmo path, **ou**
- **PATCH** com `Content-Type: application/json` e corpo `{ "avatar": null }`.

**Response 200:** usuário com `"avatar": null`.

**Exemplo (upload):**

```http
POST /api/v1/auth/me/avatar
Authorization: Bearer …
Content-Type: multipart/form-data

avatar=<arquivo imagem>
```

---

### PATCH `/api/v1/usuario/me` · PATCH `/api/v1/auth/me`

Atualização parcial **somente** dos campos: `nome`, `email`, `telefone`, `endereco` (mesma estrutura do cadastro).

**Bloqueado (400):** `perfil_acesso`, `unidade`, `is_staff`, `is_superuser`, `permissoes` e quaisquer campos de privilégio.

**Auth:** Bearer JWT

---

### POST `/api/v1/usuario/alterar-senha` · POST `/api/v1/auth/me/alterar-senha`

```json
{
  "senha_atual": "...",
  "nova_senha": "...",
  "confirmar_nova_senha": "..."
}
```

- Valida senha atual com `check_password`.
- `nova_senha` passa pelos validadores Django (`AUTH_PASSWORD_VALIDATORS`).
- `confirmar_nova_senha` deve ser idêntica a `nova_senha`.

**Response 200:** `{ "mensagem": "Senha alterada com sucesso." }`

---

### DELETE `/api/v1/usuario/desativar`

Desativa a conta e remove PII (mesmo fluxo técnico da anonimização). Body opcional: `{ "refresh_token": "..." }`.

---

### POST `/api/v1/usuario/anonimizar`

```json
{ "refresh_token": "opcional — invalida refresh JWT" }
```

**Response 200:**

```json
{
  "mensagem": "Solicitação de anonimização registrada...",
  "prazo_execucao": "48h"
}
```

---

## 🏛️ Backoffice — Mesa de Trabalho (`/api/v1/backoffice/*`)

Endpoints para o **Backoffice (Vue 3)**: Kanban, tabela densa e despacho **Scatter-Gather**.

**Auth:** `Authorization: Bearer <token>`  
**Permissão:** RBAC granular — ver tabela de códigos abaixo (ex.: `mesa_trabalho.ler` para consultas GET no módulo Mesa).

### GET `/api/v1/backoffice/mesa/unidades`

Lista unidades administrativas **ativas** para popular o modal de despacho (Mesa / Scatter-Gather).

**Permissão:** `is_staff=true` (qualquer servidor com acesso à mesa).

**Query params:** nenhum (lista completa, sem paginação).

**Response 200:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nome": "Secretaria de Obras Públicas",
    "sigla": "SOP",
    "ativo": true
  }
]
```

> **Nota:** O CRUD completo de unidades para o painel **Configurações** está em `/api/v1/backoffice/unidades` (somente Super Admin). Ver seção [Governança e RBAC (v3.0)](#-governança-e-rbac-sprint-4-v30).

---

### GET `/api/v1/backoffice/protocolos`

Lista protocolos otimizada para Kanban / tabela, com ordens de serviço aninhadas e SLA calculado.

**Query params (filtros):**

| Parâmetro     | Tipo    | Descrição                                              |
|---------------|---------|--------------------------------------------------------|
| `status`      | string  | `em_analise`, `em_andamento`, `aguardando_revisao`, `resolvido`, `rejeitado` |
| `busca`       | string  | Busca em `codigo` e `descricao`                        |
| `urgencia`    | string  | Valor em `dados_dinamicos` (urgencia/prioridade)       |
| `sla_vencido` | boolean | `true` = fora do prazo do catálogo (`sla_horas`)       |
| `page`        | int     | Página (padrão 1)                                      |
| `per_page`    | int     | Itens por página (máx. 100)                            |
| `ordering`    | string  | Ex.: `-data_criacao`, `codigo`, `status`               |

**Response 200 (paginado):**

```json
{
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "codigo": "PROT-2026-014",
      "status": "em_analise",
      "descricao": "Buraco profundo na via...",
      "data_criacao": "2026-11-13T12:00:00Z",
      "servico": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "nome": "Buraco na via",
        "sla_horas": 72,
        "categoria_nome": "Zeladoria Urbana",
        "categoria_slug": "zeladoria_urbana"
      },
      "dados_dinamicos": {
        "urgencia": "alta",
        "categoria_problema": "via_publica"
      },
      "sla": {
        "sla_horas": 72,
        "prazo_em": "2026-11-16T12:00:00Z",
        "vencido": false,
        "horas_restantes": 48.0
      },
      "urgencia": "alta",
      "cidadao": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "nome": "João Silva",
        "telefone": "11987654321"
      },
      "endereco": "Av. Principal, 500",
      "tem_anexos": true,
      "tem_localizacao": true,
      "ordens_servico": [
        {
          "id": "990e8400-e29b-41d4-a716-446655440004",
          "unidade_id": "550e8400-e29b-41d4-a716-446655440000",
          "unidade": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "nome": "Secretaria de Obras Públicas",
            "sigla": "SOP",
            "ativa": true
          },
          "nome_equipe": "SOP",
          "descricao": "Tapar buraco",
          "instrucao": "Tapar buraco",
          "prazo_horas": 48,
          "status": "pendente",
          "criado_em": "2026-11-13T14:00:00Z",
          "atualizado_em": "2026-11-13T14:00:00Z"
        }
      ]
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_items": 42,
    "total_pages": 3
  }
}
```

**Notas:**

- `dados_dinamicos` retorna apenas chaves resumidas (`urgencia`, `prioridade`, `categoria_problema`, `tema`, `tipo_manifestacao`, `bairro`).
- `sla` usa `servico.sla_horas` a partir de `data_criacao`.

---

### POST `/api/v1/backoffice/protocolos/<uuid:protocolo_id>/despachar`

Cria múltiplas **Ordens de Serviço** (scatter-gather), move o protocolo para `em_andamento` e registra histórico.

**Request body:**

```json
{
  "ordens": [
    {
      "unidade_id": "550e8400-e29b-41d4-a716-446655440000",
      "instrucao": "Tapar buraco",
      "prazo_horas": 48
    },
    {
      "unidade_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "instrucao": "Sinalizar via",
      "prazo_horas": 12
    }
  ],
  "observacao_geral": "Despacho em lote"
}
```

**Validações:**

- Pelo menos uma ordem em `ordens`.
- `unidade_id` deve existir e estar `ativa=true`.
- Cada unidade só pode aparecer uma vez no mesmo despacho.
- `prazo_horas`: inteiro entre 1 e 8760.

**Response 201:**

```json
{
  "protocolo": { "...": "mesmo formato do item em GET /backoffice/protocolos" },
  "ordens_servico": [ "..." ],
  "despachado_em": "2026-11-13T15:30:00Z",
  "urgencia": "alta"
}
```

**Efeito colateral (v1.5):** cada OS criada registra `despachado_por` e dispara **notificação interna** para os servidores `is_staff` da unidade recebedora.

**Erros comuns:**

- `400` — payload inválido, unidade duplicada ou inativa.
- `403` — usuário sem `is_staff`.
- `404` — protocolo não encontrado.

---

### GET `/api/v1/backoffice/protocolos/<protocolo_id>`

Detalhamento **360º** para a tela interna: dados coletados pela IA, histórico de chat, ordens de serviço (com anexos/evidências) e histórico administrativo.

**`protocolo_id`:** UUID do protocolo **ou** código legível (`codigo`, ex.: `PROT-2026-001`), sem diferenciar maiúsculas/minúsculas.

**Response 200:** objeto plano (mesmos campos do item da listagem Kanban, mais os abaixo):

| Campo extra | Descrição |
|-------------|-----------|
| `dados_coletados` | Merge de `dados_dinamicos` do protocolo + slots da sessão de chat (sem chaves `_meta`) |
| `historico_chat` | Lista cronológica `{ id, tipo, mensagem, timestamp, anexo? }` (`tipo`: `cidadao`, `bot` [IA], `sistema`) |
| `historico_protocolo` | Eventos administrativos (`ProtocoloHistorico`) |
| `localizacao` | `{ endereco, latitude?, longitude? }` |
| `resposta_cidadao` / `observacoes_internas` | Preenchidos após validação |
| `triagem_sugerida` | Objeto do motor determinístico (v4.9); `{}` se não aplicável |
| `ordens_servico[]` | Inclui `observacoes_execucao`, `concluido_em`, `anexos[]`, `fotos_execucao[]`, `prazo_em` |

**Erros:** `403`, `404`.

---

### POST `/api/v1/backoffice/ordens/<uuid:ordem_id>/concluir`

**Gather** — secretaria/equipe conclui a ordem com evidências fotográficas.

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `observacoes_execucao` | string | Não | Relato da execução em campo |
| `anexos` | file[] | Não* | Fotos antes/depois (também aceita `arquivos` ou `midia`) |
| `tipo_evidencia` | string[] | Não | Paralelo a cada arquivo: `antes`, `depois`, `durante`, `outro` (padrão: `depois`) |

\* Recomendado enviar ao menos um anexo de evidência.

**Efeitos:**

- OS → `concluida`, `concluido_em` preenchido.
- Se **todas** as ordens ativas do protocolo pai estiverem `concluida`, protocolo → `aguardando_revisao`.

**Response 200:**

```json
{
  "ordem_servico": { "...": "detalhe com anexos" },
  "protocolo_status": "aguardando_revisao",
  "protocolo_em_revisao": true,
  "concluido_em": "2026-11-13T18:00:00Z"
}
```

---

### POST `/api/v1/backoffice/protocolos/<uuid:protocolo_id>/validar`

Gestor da ouvidoria valida o trabalho das secretarias e encerra o protocolo.

**Request body (JSON):**

```json
{
  "resposta_cidadao": "Prezado(a) cidadão(ã), informamos que...",
  "observacoes_internas": "Conferido in loco via fotos."
}
```

**Efeitos:** `status` → `resolvido`; dispara notificação push/e-mail (Celery) com `habilitar_avaliacao: true` nos metadados.

**Response 200:** `{ "sucesso": true, "protocolo": { ... }, "mensagem_enviada": true }`

**Erros:**

- `400` se o protocolo **não** estiver em `aguardando_revisao` (retorno do setor concluído).
- `400` se o protocolo já estiver `resolvido` ou `rejeitado` (encerrado — não é possível validar de novo).

**Nota:** A formalização setorial (`POST .../formalizar`) nunca define `resolvido`; apenas a validação da Ouvidoria encerra o protocolo ao cidadão.

---

### POST `/api/v1/backoffice/ordens/<uuid:ordem_id>/devolver`

Devolve uma ordem específica para correção pela secretaria.

**Request body (JSON):**

```json
{
  "motivo": "foto_inadequada",
  "justificativa": "As imagens não mostram o serviço concluído."
}
```

**Efeitos:**

- OS → `em_andamento`, `concluido_em` limpo.
- Se o protocolo estava em `aguardando_revisao` → `em_andamento`.
- Registro em `historico_protocolo`.

**Response 200:** `{ "sucesso": true, "ordem_servico": { ... }, "protocolo_status": "em_andamento" }`

---

## 🏗️ Painel Setorial & Link Mágico

Fluxo: gestor setorial gera link → equipe de rua envia fotos **sem login** → gestor **formaliza** com senha (assinatura digital base) → gather no protocolo pai.

**Auth setorial:** JWT + `is_staff=true` + usuário com `unidade` vinculada (superusuário sem unidade vê todas as OS).

### GET `/api/v1/backoffice/setorial/ordens`

Lista ordens da unidade do servidor logado (sem dados sensíveis completos do cidadão — CPF mascarado).

**Response 200:** array de objetos compatíveis com o Painel Setorial (`magic_link`, `evidencias`, `status` UI: `nova`, `aguardando_campo`, `concluida`, etc.).

**Erros:** `403` sem unidade vinculada (não superuser).

---

### POST `/api/v1/backoffice/ordens/<uuid:ordem_id>/gerar-link`

Gera/renova token UUID com validade de **48 horas**.

**Response 201:**

```json
{
  "magic_link": {
    "token": "uuid",
    "url": "https://ouvidoria.mogidascruzes.sp.gov.br/campo/<uuid>",
    "gerado_em": "...",
    "expira_em": "...",
    "acessos": 0
  },
  "url": "...",
  "ordem_servico": { "...": "item setorial" }
}
```

---

### POST `/api/v1/backoffice/ordens/<uuid:ordem_id>/formalizar`

Formalização com assinatura por senha do gestor.

**Request body (JSON):**

```json
{
  "despacho_tecnico": "Serviço executado conforme norma...",
  "observacoes_extras": "Opcional",
  "senha_assinatura": "senha-do-usuario"
}
```

**Validações:**

- `403` se a senha não confere.
- Evidências fotográficas são **opcionais** (despachos de impossibilidade técnica podem formalizar sem anexos).
- `400` se a OS estiver em `aguardando_assinatura` (use o fluxo hierárquico abaixo).
- OS → `concluida`; se todas as OS do protocolo concluírem → protocolo `aguardando_revisao`.

**Status operacionais da ordem de serviço (`OrdemServico.status`):**

| Valor | Descrição |
|-------|-----------|
| `pendente` | Criada no despacho, ainda não em execução |
| `em_andamento` | Em execução pela secretaria / equipe |
| `aguardando_formalizacao` | Evidências recebidas via link mágico |
| `aguardando_assinatura` | Despacho elaborado; aguarda assinatura do superior (fluxo hierárquico) |
| `concluida` | Formalizada (autoassinatura ou assinatura hierárquica) |
| `cancelada` | Encerrada sem conclusão |

**Assinatura eletrônica simples:**

Após validação de `senha_assinatura`, o servidor gera **SHA-256** sobre a concatenação (sem separadores):

`{usuario_id}{ordem_id}{despacho_tecnico}{timestamp_iso8601}`

O digest é persistido em `assinatura_digital_hash` e o instante exato em `data_formalizacao`.

**Response 200:**

```json
{
  "sucesso": true,
  "ordem_servico": { "...": "inclui data_formalizacao quando formalizada" },
  "protocolo_status": "aguardando_revisao",
  "protocolo_em_revisao": true,
  "assinatura_digital_hash": "a1b2c3..."
}
```

---

### Assinatura eletrônica hierárquica — `/api/v1/backoffice/assinaturas/`

Fluxo alternativo à formalização direta: o **operador** (servidor da unidade) redige o despacho e solicita a **assinatura** de um superior (`Secretário`, `Diretor`, etc.). O superior assina com **senha do usuário**; o sistema gera hash **SHA-256** com validade jurídica (rastreabilidade).

**Permissão:** JWT + `is_staff` + unidade vinculada (`IsSetorialStaff`), salvo superusuário.

#### POST `/api/v1/backoffice/assinaturas/solicitar`

**Request body (JSON):**

```json
{
  "ordem_servico_id": "uuid-da-os",
  "despacho_tecnico": "Texto integral do despacho a ser assinado..."
}
```

`assinante_destino_id` (UUID) é **opcional**. Se omitido, o backend designa automaticamente: (1) gestor/outro staff da unidade da OS; (2) se a secretaria só tiver o operador, gestor da Mesa/Ouvidoria central (`is_staff` sem `unidade_id`).

**Regras:**

- Cria `SolicitacaoAssinatura` com `status=pendente`.
- OS → `aguardando_assinatura`; persiste `despacho_tecnico` na OS.
- Notificação interna para o assinante resolvido via `criar_notificacao_interna` (`atendimentos/servicos_notificacao.py`).
- `400` se já houver solicitação pendente para a mesma OS.
- `400` se `assinante_destino_id` for o próprio solicitante (quando informado manualmente).
- `400` se não houver gestor elegível na unidade quando `assinante_destino_id` for omitido.

**Response 201:**

```json
{
  "sucesso": true,
  "solicitacao_assinatura": {
    "id": "uuid",
    "ordem_servico_id": "uuid",
    "solicitante_id": 10,
    "assinante_destino_id": 42,
    "despacho_tecnico": "...",
    "status": "pendente",
    "hash_assinatura": null,
    "assinada_em": null,
    "criado_em": "...",
    "atualizado_em": "..."
  },
  "ordem_servico_status": "aguardando_assinatura"
}
```

#### POST `/api/v1/backoffice/assinaturas/<uuid:solicitacao_id>/assinar`

Somente o **assinante designado** (usuário logado = `assinante_destino`).

**Request body (JSON):**

```json
{
  "senha_assinatura": "senha-do-assinante"
}
```

**Transação (`transaction.atomic`):**

1. Valida senha do assinante (`403` se inválida).
2. Gera **SHA-256** sobre: `{usuario_id}{despacho_tecnico}{timestamp_iso8601}` (conteúdo exato da solicitação).
3. Persiste em `SolicitacaoAssinatura.hash_assinatura`; `status=assinada`.
4. OS → `concluida`; copia hash para `OrdemServico.assinatura_digital_hash` e `data_formalizacao`.
5. Gather: histórico do protocolo (parecer técnico), `tentar_aguardando_revisao` → `aguardando_revisao`; notifica o ouvidor (`despachado_por`). **Não** encerra ao cidadão (push de conclusão só na validação).

**Response 200:**

```json
{
  "sucesso": true,
  "solicitacao_assinatura": { "...": "status assinada, hash preenchido" },
  "hash_assinatura": "a1b2c3...",
  "ordem_servico_status": "concluida",
  "protocolo_status": "aguardando_revisao"
}
```

#### GET `/api/v1/backoffice/assinaturas/pendentes`

Inbox do **assinante**: solicitações `pendente` em que `assinante_destino` = usuário logado.

**Permissão:** `IsSetorialStaff` (JWT + staff com unidade, ou superusuário).

**Deep fetch:** cada item inclui `ordem_servico` no mesmo formato do Painel Setorial (`SetorialOrdemServicoSerializer`: protocolo, evidências, magic link, SLA, etc.).

**Response 200:**

```json
{
  "results": [
    {
      "id": "uuid-solicitacao",
      "ordem_servico_id": "uuid-os",
      "solicitante_id": 10,
      "assinante_destino_id": 42,
      "solicitante_nome": "Maria Operadora",
      "assinante_destino_nome": "João Secretário",
      "despacho_tecnico": "...",
      "status": "pendente",
      "hash_assinatura": null,
      "assinada_em": null,
      "motivo_rejeicao": "",
      "rejeitada_em": null,
      "criado_em": "...",
      "atualizado_em": "...",
      "ordem_servico": { "...": "objeto completo setorial" }
    }
  ],
  "count": 1
}
```

---

#### POST `/api/v1/backoffice/assinaturas/<uuid:solicitacao_id>/rejeitar`

Somente o **assinante designado** pode recusar uma solicitação ainda `pendente`.

**Request body (JSON):**

```json
{
  "motivo_rejeicao": "Despacho incompleto — falta referência à norma técnica aplicável."
}
```

**Validações:**

- `motivo_rejeicao` obrigatório (mín. 10 caracteres após trim).
- `403` se o usuário logado não for o `assinante_destino`.
- `400` se a solicitação não estiver `pendente` ou a OS não estiver em `aguardando_assinatura`.

**Efeitos (`transaction.atomic`):**

1. `SolicitacaoAssinatura` → `rejeitada`; persiste `motivo_rejeicao` e `rejeitada_em`.
2. `OrdemServico` → `aguardando_formalizacao` (operador pode revisar despacho e solicitar novamente).
3. Notificação interna ao **solicitante** com o motivo informado.

**Response 200:**

```json
{
  "sucesso": true,
  "solicitacao_assinatura": {
    "id": "uuid",
    "status": "rejeitada",
    "motivo_rejeicao": "...",
    "rejeitada_em": "2026-11-16T12:00:00Z"
  },
  "ordem_servico_status": "aguardando_formalizacao"
}
```

**Modelo `SolicitacaoAssinatura.status`:** `pendente` | `assinada` | `rejeitada`.

---

### Serviço `criar_notificacao_interna`

Módulo: `atendimentos/servicos_notificacao.py`

```python
criar_notificacao_interna(usuario_id, titulo, mensagem, link_acao=None) -> NotificacaoInterna | None
```

Usado pelos gatilhos automáticos (scatter/gather) e pelo fluxo de assinatura.

---

### CRUD `/api/v1/backoffice/textos-padrao/`

Textos de despacho técnico **por secretaria** (`UnidadeAdministrativa`).

**Permissão:** `is_staff` com `unidade` vinculada (ou superusuário).

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/backoffice/textos-padrao` | Lista textos da unidade do usuário (`results`, `count`) |
| `POST` | `/backoffice/textos-padrao` | Cria texto (`titulo`, `texto`, `ativo?`); `unidade` inferida do usuário |
| `GET` | `/backoffice/textos-padrao/<uuid>` | Detalhe (somente da própria unidade) |
| `PUT` | `/backoffice/textos-padrao/<uuid>` | Atualiza `titulo`, `texto`, `ativo` |
| `DELETE` | `/backoffice/textos-padrao/<uuid>` | Remove registro (`204`) |

**Item (exemplo):**

```json
{
  "id": "uuid",
  "unidade": "uuid-unidade",
  "unidade_nome": "Zeladoria Urbana",
  "unidade_sigla": "ZEL",
  "titulo": "Asfalto Frio",
  "texto": "Serviço de tapa-buraco executado com asfalto frio CBUQ...",
  "ativo": true,
  "criado_em": "2026-11-13T18:00:00Z",
  "atualizado_em": "2026-11-13T18:00:00Z"
}
```

---

### Notificações internas — `/api/v1/backoffice/notificacoes/`

Canal in-app para **servidores** (`is_staff`), distinto de `GET /notificacoes` (cidadão).

**Gatilhos automáticos (backend):**

1. **Scatter** — ao despachar protocolo: notifica todos os usuários `is_staff=True` da unidade recebedora (`ConfiguracaoSistema.notificar_novos_despachos`, default `true`).
2. **Super OS** — ao despachar Super OS: mesmo scatter por unidade (`ConfiguracaoSistema.notificar_novas_super_os`, default `true`).
3. **SLA vencido** — job Celery `notificar_sla_vencido_task` (agendar no Beat); respeita `ConfiguracaoSistema.notificar_sla_vencido`.
4. **Gather** — ao formalizar OS: notifica o `despachado_por` (ouvidor que criou a OS).
5. **Assinatura** — ao solicitar: notifica o `assinante_destino`; ao assinar: notifica o `solicitante`; ao **rejeitar**: notifica o `solicitante` com o motivo.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/backoffice/notificacoes` | Lista do usuário logado (`results`, `count`, `nao_lidas`). Query: `nao_lidas=true` (filtra não lidas), `limit` (máx. 200) |
| `POST` | `/backoffice/notificacoes/<uuid>/marcar-lida` | Marca como lida (canônico) |
| `POST` | `/backoffice/notificacoes/<uuid>/lida` | Alias compatível com o contrato Sprint 2 |

**Item:**

```json
{
  "id": "uuid",
  "titulo": "Nova OS — PROT-2026-005",
  "mensagem": "Nova ordem de serviço atribuída à Zeladoria Urbana...",
  "lida": false,
  "link_acao": "https://ouvidoria.../backoffice/setorial",
  "data_criacao": "2026-11-13T18:05:00Z"
}
```

#### Central de Gestão (Super Admin) — `/api/v1/backoffice/admin/notificacoes/`

Somente **Super Admin** (`IsSuperAdmin` / `regras.super_admin` no RBAC GLPI).

##### GET/PATCH `/backoffice/admin/configuracao-sistema`

Singleton de parâmetros globais. **PATCH** aceita parcial: `notificar_novos_despachos`, `notificar_sla_vencido`, `notificar_novas_super_os`, `dias_busca_cluster_ia`.

##### GET `/backoffice/admin/saude-infra`

**Saúde do Chat** — monitoramento em tempo real de Redis (broker) e workers Celery que processam filas da IA. O `inspect.ping()` pode levar vários segundos quando há múltiplos workers no broker; o endpoint usa timeout de até **~8s** na camada HTTP para evitar falso OFFLINE.

**Permissão:** Super Admin (`IsSuperAdmin`).

**Resposta (200):**

```json
{
  "chat_operacional": true,
  "redis": {
    "status": "ONLINE",
    "ok": true,
    "detalhe": null
  },
  "celery": {
    "status": "ONLINE",
    "ok": true,
    "workers_vivos": 1,
    "workers": ["celery@servidor"],
    "filas_detectadas": ["ouve"],
    "fila_padrao": "ouve",
    "detalhe": null
  },
  "verificado_em": "2026-11-17T21:12:00+00:00"
}
```

| Campo | Descrição |
|-------|-----------|
| `chat_operacional` | `true` somente se `redis.ok` e `celery.ok` |
| `redis.status` | `ONLINE` ou `OFFLINE` (ping em `CELERY_BROKER_URL`) |
| `celery.workers_vivos` | Quantidade de workers que responderam ao `inspect.ping()` |
| `celery.filas_detectadas` | Filas reportadas em `active_queues` (pode estar vazio se o broker falhar) |
| `verificado_em` | ISO 8601 UTC do instante da checagem |

Em falha de broker ou timeout, `detalhe` traz mensagem resumida; `chat_operacional` fica `false`.

##### GET `/backoffice/admin/notificacoes/auditoria`

Lista **todas** as notificações internas do sistema (paginado).

| Query | Tipo | Descrição |
|-------|------|-----------|
| `usuario_destino_id` | UUID | Filtra destinatário |
| `unidade_destino_id` | UUID | Filtra pela unidade vinculada ao usuário destino |
| `lida` | boolean | `true` / `false` |
| `data_criacao_inicio` | ISO date/datetime | Início do intervalo (inclusivo) |
| `data_criacao_fim` | ISO date/datetime | Fim do intervalo (inclusivo; datas `YYYY-MM-DD` usam fim do dia) |
| `busca` | string | Título, mensagem, nome ou e-mail do destinatário |
| `page` / `page_size` | int | Paginação (default 50, máx. 200) |

**Resposta (200):** padrão DRF `count`, `next`, `previous`, `results[]` com campos do item acima mais `usuario_destino_id`, `usuario_destino_nome`, `usuario_destino_email`, `unidade_destino_id`, `unidade_destino_nome`.

##### POST `/backoffice/admin/notificacoes/broadcast`

Disparo em massa via `criar_notificacao_interna` (transação atômica). Destinatários: usuários **`is_staff=True` e ativos**; se `unidade_alvo_id` for omitido/nulo, broadcast global; se informado, apenas servidores da unidade.

**Body:**

```json
{
  "titulo": "Manutenção programada",
  "mensagem": "O sistema ficará indisponível das 22h às 23h.",
  "unidade_alvo_id": "uuid-opcional",
  "nivel_urgencia": "normal",
  "link_acao": "/backoffice/mesa"
}
```

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `titulo` | sim | Até 255 caracteres; urgência `alta` prefixa `[Urgência alta]` |
| `mensagem` | sim | Corpo da notificação |
| `unidade_alvo_id` | não | UUID da unidade alvo |
| `nivel_urgencia` | não | `normal` (default) \| `alta` |
| `link_acao` | não | Caminho ou URL absoluta |

**Resposta (201):**

```json
{
  "sucesso": true,
  "criadas": 42,
  "destinatarios_elegiveis": 42,
  "unidade_alvo_id": null,
  "nivel_urgencia": "normal"
}
```

**Configuração de gatilhos** — modelo singleton `ConfiguracaoSistema` (Django Admin): `notificar_novos_despachos`, `notificar_sla_vencido`, `notificar_novas_super_os` (boolean, default `true`).

---

### POST `/api/v1/publico/evidencias/<uuid:token_magic_link>` (público)

**Sem JWT.** Upload multipart de evidências fotográficas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `anexos` / `arquivos` / `midia` | file[] | Fotos (obrigatório ≥ 1) |
| `tipo_evidencia` | string[] | `antes`, `depois`, `durante`, `outro` |

**Efeitos:** cria `AnexoOrdemServico`; incrementa `magic_link_acessos`; OS → `aguardando_formalizacao`.

**Response 201 (mínima — sem dados do cidadão):**

```json
{
  "sucesso": true,
  "anexos_recebidos": 3,
  "status": "aguardando_formalizacao",
  "mensagem": "Evidências enviadas com sucesso."
}
```

**Erros:** `404` token inválido; `410` link expirado ou OS encerrada.

---

### Super OS — Incidente Mestre (`/api/v1/backoffice/super-os/`)

Agrupamento operacional de protocolos duplicados/similares (Sprint 3 — clusterização).

**Modelo de domínio**

| Campo | Descrição |
|-------|-----------|
| `SuperOS.codigo` | Ex.: `SOS-2026-001` (sequencial anual) |
| `Protocolo.super_os` | FK opcional; cada protocolo pertence a no máximo uma Super OS |
| `OrdemServico.super_os` | FK opcional; OS criada pelo despacho da Super OS |

**Status da Super OS** — mesmos valores de `Protocolo.status`:

`em_analise` · `em_andamento` · `aguardando_revisao` · `resolvido` · `rejeitado`

**Sincronização em massa:** ao alterar o `status` de uma `SuperOS` (via Django Admin ou futuras APIs de despacho), um `post_save` propaga o status para todos os `protocolos_filhos`. Em `resolvido`, preenche `resposta_cidadao` padrão quando vazio e dispara push (sinal existente em `Protocolo`).

---

#### GET `/api/v1/backoffice/super-os/sugestoes`

**Auth:** Bearer JWT · `is_staff=True`

**Query (opcional):**

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `raio_metros` | `300` | Raio Haversine entre coordenadas (50–5000) |
| `min_protocolos` | `2` | Tamanho mínimo do cluster (2–50) |

**Configuração global (Django Admin):** modelo singleton `ConfiguracaoSistema.dias_busca_cluster_ia` (padrão **30** dias). Somente protocolos com `data_criacao` dentro dessa janela entram no motor.

**Heurística:**

- Protocolos: `em_analise` ou `em_andamento` (equipe ainda em atuação), sem `super_os`, com `localizacao`, mesmo `servico_id` no cluster, distância ≤ `raio_metros`.
- **Excluídos:** `aguardando_revisao`, `resolvido`, `rejeitado` (serviço de campo concluído ou encerrado).
- Super OS elegível à anexação: mesmo conjunto de status abertos (`em_analise`, `em_andamento`).

**Tipos de sugestão (`tipo_acao`):**

| Valor | Significado |
|-------|-------------|
| `criar` | Novo incidente mestre a partir de ≥ `min_protocolos` protocolos próximos **sem OS ativa no cluster** |
| `anexar` | Protocolo(s) próximo(s) a **Super OS** (com OS ativa em campo, quando aplicável) — `POST .../anexar` |
| `criar_retroativa` | Âncora: protocolo **já despachado** (OS ativa no setorial). Novos relatos no mesmo cluster — `POST .../retroativa` |

**Âncora operacional:** o motor prioriza Super OS ou protocolo com `OrdemServico` em `pendente`, `em_andamento`, `aguardando_formalizacao` ou `aguardando_assinatura`. Sugestões `criar` são **suprimidas** quando o cluster tem OS ativa (use retroativa ou anexar).

**Campos extras em `criar_retroativa`:**

| Campo | Descrição |
|-------|-----------|
| `protocolo_ancora_id` | UUID do protocolo já no Painel Setorial |
| `protocolo_ancora_codigo` | Código legível da âncora |
| `protocolos_envolvidos_ids` | Todos os UUID do cluster (âncora + novos), para mapa/UI |

**Response 200:**

```json
{
  "raio_metros": 300,
  "min_protocolos": 2,
  "dias_busca_cluster_ia": 30,
  "count": 2,
  "sugestoes": [
    {
      "tipo_acao": "anexar",
      "titulo": "Anexar 1 protocolo(s) de Buraco na Via à Super OS SOS-2026-003 — …",
      "super_os_id": "uuid",
      "super_os_codigo": "SOS-2026-003",
      "super_os_titulo": "Buracos — trecho central",
      "servico_id": "uuid",
      "servico_nome": "Buraco na Via",
      "protocolo_ids": ["uuid"],
      "quantidade": 1,
      "latitude_centro": -23.5501,
      "longitude_centro": -46.6332,
      "raio_metros": 300
    },
    {
      "tipo_acao": "criar",
      "titulo": "5 protocolos de Buraco na Via próximos à Av. Paulista",
      "servico_id": "uuid",
      "servico_nome": "Buraco na Via",
      "protocolo_ids": ["uuid", "uuid"],
      "quantidade": 5,
      "latitude_centro": -23.5501,
      "longitude_centro": -46.6332,
      "raio_metros": 300
    }
  ]
}
```

---

#### POST `/api/v1/backoffice/super-os/retroativa`

Agrupamento **retroativo** — cria Super OS em `em_andamento` em torno do protocolo âncora, migra OS ativas da âncora para `OrdemServico.super_os` e sincroniza filhos.

**Auth:** Bearer JWT · `is_staff=True`

**Request:**

```json
{
  "protocolo_ancora_id": "550e8400-e29b-41d4-a716-446655440000",
  "protocolos_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ],
  "titulo_resumo": "Buracos — quadra central",
  "descricao_geral": "Opcional"
}
```

**Response 201:** `super_os`, `protocolo_ancora_id`, `quantidade_protocolos`.

**Erros:** `400` — âncora sem OS ativa, protocolo já em Super OS, serviço incompatível.

**Bloqueio (C):** `POST .../agrupar-mapa` rejeita criação em `em_analise` se qualquer protocolo do lote tiver OS ativa; use esta rota.

---

#### POST `/api/v1/backoffice/super-os/<uuid>/anexar`

Anexação em 1 clique — vincula protocolo a incidente mestre existente **sem** novo despacho scatter individual (herda OS da Super OS).

**Auth:** Bearer JWT · `is_staff=True`

**Request:**

```json
{
  "protocolo_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Regras:**

- Super OS e protocolo em `em_analise` ou `em_andamento`.
- Protocolo com `localizacao`, sem `super_os` prévio.
- Serviço do protocolo compatível com os filhos já agrupados (quando houver filhos).
- Atualiza `protocolo.status` para o **mesmo status da Super OS** (espelhamento operacional).

**Response 200:**

```json
{
  "sucesso": true,
  "super_os": {
    "id": "uuid",
    "codigo": "SOS-2026-003",
    "status": "em_andamento",
    "titulo_resumo": "…",
    "protocolos_filhos_ids": ["…"],
    "quantidade_protocolos": 4
  },
  "protocolo": {
    "id": "uuid",
    "codigo": "PROT-2026-042",
    "status": "em_andamento",
    "super_os_id": "uuid"
  }
}
```

**Erros:** `400` com `detail` (status inválido, sem geo, já agrupado, serviço incompatível).

---

#### GET `/api/v1/backoffice/kanban`

Kanban unificado da Mesa de Trabalho — **não lista protocolos já agrupados** (`super_os` preenchido); exibe incidentes `SuperOS` como cards próprios.

**Auth:** Bearer JWT · `is_staff=True`

**Query (opcional):** `status`, `busca`, `sla_vencido`, `urgencia`, `page`, `per_page` (padrão 50, máx. 200).

**Ordenação:** SLA vencido primeiro → menor `horas_restantes` → urgência (crítica/alta antes) → data de criação.

**Response 200:**

```json
{
  "data": [
    {
      "id": "uuid",
      "tipo": "protocolo",
      "codigo": "PROT-2026-007",
      "titulo": "Buracos e Pavimentação · PROT-2026-007",
      "status": "em_analise",
      "prazo_horas": 72,
      "urgencia": "media",
      "qtd_filhos": 0,
      "sla": {
        "sla_horas": 72,
        "prazo_em": "2026-11-19T12:00:00Z",
        "vencido": false,
        "horas_restantes": 48.2
      },
      "criado_em": "2026-11-16T12:00:00Z",
      "endereco": "Rua Exemplo, 100",
      "servico_nome": "Buracos e Pavimentação",
      "cidadao": { "id": "uuid", "nome": "Maria Silva", "telefone": "11999990000" },
      "triagem_sugerida": {}
    },
    {
      "id": "uuid",
      "tipo": "super_os",
      "codigo": "SOS-2026-001",
      "titulo": "Buracos — trecho central",
      "status": "em_andamento",
      "prazo_horas": 48,
      "urgencia": "alta",
      "qtd_filhos": 5,
      "sla": { "vencido": true, "horas_restantes": -12.0 },
      "criado_em": "2026-11-15T10:00:00Z",
      "endereco": "…",
      "servico_nome": "Buracos e Pavimentação"
    }
  ],
  "count": 12,
  "pagination": {
    "current_page": 1,
    "per_page": 50,
    "total_items": 12,
    "total_pages": 1
  }
}
```

---

#### GET `/api/v1/backoffice/super-os/<uuid>`

Dossiê profundo do incidente mestre (Visão 360º consolidada).

**Auth:** Bearer JWT · `is_staff=True`

**Response 200:** objeto `SuperOS` + `centroide` + `protocolos_filhos[]` com `cidadao`, `dados_coletados`, `historico_chat`, `historico_protocolo`, `sla`, `urgencia`, `localizacao` por filho; `ordens_servico_ids`, `sla` e `urgencia` agregados.

```json
{
  "id": "uuid",
  "codigo": "SOS-2026-001",
  "titulo_resumo": "…",
  "descricao_geral": "…",
  "status": "em_andamento",
  "centroide": { "latitude": -23.52, "longitude": -46.19 },
  "quantidade_protocolos": 3,
  "protocolos_filhos": [
    {
      "id": "uuid",
      "codigo": "PROT-2026-006",
      "cidadao": { "nome": "…", "telefone": "…", "email": "…" },
      "dados_coletados": { "tipo_problema": ["buraco"] },
      "historico_chat": [{ "tipo": "cidadao", "mensagem": "…", "timestamp": "…" }]
    }
  ],
  "ordens_servico_ids": ["uuid"]
}
```

**Erros:** `404` — Super OS inexistente.

---

#### Painel Setorial — incidente múltiplo

Em `GET /api/v1/backoffice/setorial/ordens` e em respostas que incluem `ordem_servico` (ex.: formalização, link mágico, upload de evidências):

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `is_super_os` | boolean | `true` quando a OS foi despachada via Super OS (`OrdemServico.super_os_id` preenchido) |
| `qtd_chamados_vinculados` | int | Número de protocolos filhos na Super OS; `1` para OS unitária |

O mesmo par de campos aparece em `BackofficeOrdemServicoSerializer` (mesa / detalhe de protocolo).

---

#### POST `/api/v1/backoffice/super-os/agrupar-mapa`

Criação manual a partir da seleção no mapa (raio desenhado na UI).

**Auth:** Bearer JWT · `is_staff=True`

**Request:**

```json
{
  "protocolos_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ],
  "titulo_resumo": "Buracos — quadra 12 ao mercado",
  "descricao_geral": "Opcional; se vazio, concatena trechos das descrições dos protocolos."
}
```

**Regras:** todos os IDs devem existir; cada protocolo precisa de `localizacao`; nenhum pode já ter `super_os`.

**Response 201:**

```json
{
  "sucesso": true,
  "super_os": {
    "id": "uuid",
    "codigo": "SOS-2026-001",
    "titulo_resumo": "Buracos — quadra 12 ao mercado",
    "descricao_geral": "…",
    "status": "em_analise",
    "latitude_centro": -23.5501,
    "longitude_centro": -46.6332,
    "criado_em": "2026-11-16T15:00:00Z",
    "atualizado_em": "2026-11-16T15:00:00Z",
    "protocolos_filhos_ids": ["uuid", "uuid"],
    "quantidade_protocolos": 2
  }
}
```

**Erros:** `400` com `detail` (protocolo inexistente, sem geo, já agrupado, título vazio).

---

#### POST `/api/v1/backoffice/super-os/<uuid>/despachar`

Scatter-gather da Super OS — mesmo contrato do despacho de protocolo.

**Auth:** Bearer JWT · `is_staff=True`

**Pré-condições:** Super OS em `em_analise`, com protocolos filhos, sem OS ativa prévia.

**Request** (igual a `POST .../protocolos/<id>/despachar`):

```json
{
  "ordens": [
    {
      "unidade_id": "uuid",
      "instrucao": "Equipe de zeladoria: intervenção consolidada no trecho.",
      "prazo_horas": 72
    }
  ],
  "observacao_geral": "Opcional — registrada na descrição da Super OS e no histórico dos filhos."
}
```

**Efeitos:**

1. Cria `OrdemServico` por unidade com `super_os_id` preenchido (protocolo de referência = filho mais antigo, para compatibilidade setorial).
2. `SuperOS.status` → `em_andamento` → signal propaga `em_andamento` a **todos** os `protocolos_filhos`.
3. Notifica servidores staff das unidades recebedoras (mesmo motor do scatter).

**Response 201:**

```json
{
  "super_os": {
    "id": "uuid",
    "codigo": "SOS-2026-001",
    "status": "em_andamento",
    "titulo_resumo": "…",
    "protocolos_filhos_ids": ["…"],
    "quantidade_protocolos": 5
  },
  "ordens_servico": [
    {
      "id": "uuid",
      "super_os_id": "uuid",
      "super_os_codigo": "SOS-2026-001",
      "unidade_id": "uuid",
      "instrucao": "…",
      "prazo_horas": 72,
      "status": "pendente"
    }
  ],
  "despachado_em": "2026-11-16T15:30:00Z",
  "quantidade_protocolos_filhos": 5
}
```

**Erros:** `400` — status inválido, sem filhos, unidade duplicada/inativa, Super OS já despachada.

---

## 🚀 Versionamento

**Versão:** 2.2  
**Data:** Novembro 2026  
**Última Atualização:** Nov 17, 2026  
**Versão do contrato:** 3.3

---

## ⚙️ Governança e RBAC (Sprint 4, v3.0)

Painel **Configurações** (`/backoffice/configuracoes`): gerenciamento de **Unidades Administrativas** e **Usuários internos** com controle de acesso por perfil.

**Base URL:** `/api/v1/backoffice/`  
**Auth:** `Authorization: Bearer <JWT>`  
**Permissão global desta seção (CRUD de governança):** classe `IsSuperAdmin` — usuário com `regras.super_admin = true` no JSON do `PerfilAcesso` (ou `is_superuser=true` no Django Admin para bootstrap).

### RBAC dinâmico (padrão GLPI, v3.1)

Perfis **não são mais enums fixos** no código. O Super Admin cria/edita perfis com permissões granulares por **módulo** e **ação**, persistidas em `PerfilAcesso.permissoes` (JSONField).

#### `PerfilAcesso` (`core_auth.PerfilAcesso`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave primária |
| `codigo` | slug | Identificador estável (`super_admin`, `ouvidor`, … ou slug customizado) |
| `nome` | string | Rótulo exibido (“Triagem Central”, “Visualizador”) |
| `descricao` | text | Descrição do perfil |
| `permissoes` | object | Mapa módulo → ações booleanas (ver abaixo) |
| `sistema` | boolean | `true` = perfil seed da migração (não pode ser excluído) |
| `qtd_usuarios` | int | (somente leitura na listagem) usuários ativos com este perfil |

#### Estrutura canônica do JSON `permissoes` (matriz CRUD v3.2)

Chaves ausentes são interpretadas como `false`. O backend **normaliza** legados (`despachar` → `criar`, etc.) e expõe ao frontend códigos planos `modulo.acao`.

```json
{
  "mesa_trabalho": { "ler": false, "criar": false, "editar": false, "excluir": false },
  "painel_setorial": { "ler": false, "criar": false, "editar": false, "excluir": false },
  "mapa_ia": { "ler": false, "criar": false, "editar": false, "excluir": false },
  "configuracoes": { "ler": false, "criar": false, "editar": false, "excluir": false },
  "textos_padrao": { "ler": false, "criar": false, "editar": false, "excluir": false },
  "gestao_usuarios": { "ler": false, "criar": false, "editar": false, "excluir": false },
  "regras": {
    "exige_unidade": false,
    "acesso_staff": false,
    "super_admin": false
  }
}
```

#### Catálogo de códigos `permissoes[]` (GET `/auth/me`)

Formato: **`{modulo}.{acao}`**. Apenas combinações com valor `true` no perfil (Super Admin: todos).

| Código | Módulo / tela |
|--------|----------------|
| `mesa_trabalho.ler` | Mesa de trabalho, kanban, protocolos — leitura (GET) |
| `mesa_trabalho.criar` | Despacho, criação de nós/OS — escrita (POST) |
| `mesa_trabalho.editar` | Atualizações de protocolo/OS — PUT/PATCH |
| `mesa_trabalho.excluir` | Exclusões administrativas — DELETE |
| `painel_setorial.ler` | Painel setorial — listagem (GET) |
| `painel_setorial.criar` | Formalização / upload — POST |
| `painel_setorial.editar` | Edição de OS — PUT/PATCH |
| `painel_setorial.excluir` | Remoção de recursos setoriais — DELETE |
| `mapa_ia.ler` | Visão territorial, mapa de calor, bairros — GET |
| `mapa_ia.criar` | Agrupamento Super OS / clusters — POST |
| `mapa_ia.editar` | Ajustes em camadas IA — PUT/PATCH |
| `mapa_ia.excluir` | Remoções em mapa/clusters — DELETE |
| `configuracoes.ler` | Configurações / unidades — leitura |
| `configuracoes.criar` | Criar unidades, itens de catálogo — POST |
| `configuracoes.editar` | Editar catálogo, unidades, sistema — PUT/PATCH |
| `configuracoes.excluir` | Excluir/inativar recursos de config — DELETE |
| `textos_padrao.ler` | Textos padrão de despacho — GET |
| `textos_padrao.criar` | Novo texto padrão — POST |
| `textos_padrao.editar` | Editar texto — PUT/PATCH |
| `textos_padrao.excluir` | Excluir texto — DELETE |
| `gestao_usuarios.ler` | Listar usuários internos — GET |
| `gestao_usuarios.criar` | Criar usuário servidor — POST |
| `gestao_usuarios.editar` | Editar usuário — PUT/PATCH |
| `gestao_usuarios.excluir` | Desativar usuário — DELETE |

**Aliases legados aceitos na checagem:** `mesa_trabalho.despachar` → `criar`; `painel_setorial.assinar` → `editar`; `mapa_ia.acessar` → `ler`; `mapa_ia.agrupar` → `criar` (somente persistência JSON antiga; o `/me` retorna só CRUD canônico).

| Módulo JSON | Ações CRUD | Uso previsto |
|-------------|------------|----------------|
| `mesa_trabalho` | ler, criar, editar, excluir | Mesa / triagem / Super OS |
| `painel_setorial` | ler, criar, editar, excluir | OS da unidade |
| `mapa_ia` | ler, criar, editar, excluir | Visão territorial e clusters |
| `configuracoes` | ler, criar, editar, excluir | Unidades, catálogo, sistema |
| `textos_padrao` | ler, criar, editar, excluir | Textos padrão de despacho |
| `gestao_usuarios` | ler, criar, editar, excluir | Usuários internos |
| `regras` | (metadados) | `exige_unidade`, `acesso_staff`, `super_admin` |

**`regras` (comportamento):**

- `exige_unidade`: se `true`, o usuário **deve** ter `unidade_id`; se `false`, `unidade_id` deve ser `null`.
- `acesso_staff`: sincroniza `Usuario.is_staff` no `save()`.
- `super_admin`: sincroniza `is_staff` + `is_superuser` e libera CRUD de governança.

**Perfis seed (migração `0006`):** `super_admin`, `ouvidor`, `gestor_setorial`, `operador_campo` — equivalentes aos perfis estáticos da v3.0, agora editáveis exceto exclusão (`sistema=true`).

#### Enforcement nas APIs (v3.2 — Onda 2)

| Área | Classe DRF / regra |
|------|---------------------|
| Mesa, kanban, Super OS, notificações internas | `PermissaoMesaTrabalho` (`IsBackofficeStaff`) — HTTP → ação CRUD |
| Painel setorial / assinaturas setoriais | `PermissaoPainelSetorial` (`IsSetorialStaff`) + unidade quando `regras.exige_unidade` |
| Dashboards executivos (eficiência, qualidade, inelegibilidade) | `PermissaoMesaTrabalho` (GET → `ler`) |
| Mapa territorial / bairros | `PermissaoMapaIA` |
| Textos padrão | `PermissaoTextosPadrao` |
| Unidades + catálogo governança | `PermissaoConfiguracoes` |
| Usuários internos (CRUD) | `PermissaoGestaoUsuarios` |
| Perfis de acesso + NOC (saúde infra) | `IsSuperAdmin` |

Factory por código:

```python
from core_auth.permissions import require_permission

permission_classes = [IsAuthenticated, require_permission("mesa_trabalho.criar")]
```

Helper Python: `usuario_tem_permissao(request.user, "mapa_ia", "ler")`.

Resposta **403 Forbidden** com `detail` / mensagem indicando o código exigido (ex.: `Permissão necessária: mesa_trabalho.ler`).

Super Admin (`regras.super_admin`) e `is_superuser` Django **sempre** passam.

---

### CRUD — Perfis de Acesso

**Resource:** `/api/v1/backoffice/perfis-acesso`  
**Permissão:** `IsSuperAdmin`

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/backoffice/perfis-acesso` | Lista perfis (`?busca=` em nome/código) |
| `POST` | `/api/v1/backoffice/perfis-acesso` | Cria perfil (`codigo` opcional — gerado do nome) |
| `GET` | `/api/v1/backoffice/perfis-acesso/<uuid>` | Detalhe |
| `PUT` / `PATCH` | `.../<uuid>` | Atualiza nome, descrição e `permissoes` |
| `DELETE` | `.../<uuid>` | Exclui** |

\*\* `400` se `sistema=true` ou houver usuários ativos vinculados.

**Exemplo `POST` — perfil “Visualizador”:**

```json
{
  "nome": "Visualizador",
  "descricao": "Somente leitura na mesa",
  "permissoes": {
    "mesa_trabalho": { "ler": true },
    "regras": { "acesso_staff": true }
  }
}
```

**Resposta 200 (trecho):**

```json
{
  "id": "…",
  "codigo": "visualizador",
  "nome": "Visualizador",
  "permissoes": { "mesa_trabalho": { "ler": true, "editar": false, … }, "regras": { … } },
  "sistema": false,
  "qtd_usuarios": 0
}
```

### Modelo de dados (resumo)

#### `UnidadeAdministrativa` (`catalogo.UnidadeAdministrativa`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave primária |
| `nome` | string | Nome completo da secretaria/equipe |
| `sigla` | string | Sigla curta (opcional) |
| `descricao` | text | Descrição institucional |
| `tom_ia` | string | Tom do assistente virtual para serviços com `unidade_responsavel` desta unidade (ver valores abaixo). Padrão: `institucional` |
| `tom_ia_display` | string | Somente leitura — rótulo legível de `tom_ia` |
| `diretrizes_tom_ia` | string | Instruções extras de vocabulário/estilo (máx. **500** caracteres na API; influencia o system prompt do chat) |
| `ativo` | boolean | `true` = disponível para despacho e vínculos |
| `criado_em` / `atualizado_em` | datetime | Timestamps automáticos |

**Valores aceitos em `tom_ia`:**

| Valor | Uso sugerido |
|-------|----------------|
| `institucional` | Cordial, claro e padronizado (padrão) |
| `acolhedor` | Empático e paciente (Saúde, Assistência Social, Proteção Animal) |
| `objetivo` | Direto e conciso (Zeladoria, Trânsito, Iluminação) |
| `tecnico` | Preciso na coleta de evidências (Fiscalização, Obras) |

> **Runtime (chat / sandbox):** o orquestrador LLM lê `servico.unidade_responsavel` e injeta o tom nas redações conversacionais (perguntas via `ia_instrucao`, classificação e avaliação interpretativa de elegibilidade). A **repescagem literal** (`ia_repescagem` com `repescagem=true`) permanece inalterada — sem chamada LLM.

#### `Usuario` (`core_auth.Usuario` — Custom User)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `perfil_acesso` | FK opcional | Perfil GLPI; `null` = cidadão |
| `unidade` | FK opcional | Obrigatória se `regras.exige_unidade=true`; caso contrário deve ser `null` |

**Regra de negócio:** derivada do JSON `regras.exige_unidade` do perfil vinculado (não mais enum estático).

### Convenção na API de usuários (compatibilidade Vue)

| Campo API | Significado |
|-----------|-------------|
| `perfil` | **Somente leitura** — espelha `perfil_acesso.codigo` (ex.: `gestor_setorial`) |
| `perfil_acesso_id` | UUID do `PerfilAcesso` (preferencial na escrita) |
| `perfil` / `perfil_codigo` na escrita | Aceito como alias do `codigo` do perfil (legado Sprint 4) |

---

### CRUD — Unidades Administrativas

**Resource:** `/api/v1/backoffice/unidades`

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/backoffice/unidades` | Lista todas as unidades (ativas e inativas) |
| `POST` | `/api/v1/backoffice/unidades` | Cria unidade |
| `GET` | `/api/v1/backoffice/unidades/<uuid>` | Detalhe |
| `PUT` | `/api/v1/backoffice/unidades/<uuid>` | Atualização completa |
| `PATCH` | `/api/v1/backoffice/unidades/<uuid>` | Atualização parcial (suportado pelo ViewSet) |
| `DELETE` | `/api/v1/backoffice/unidades/<uuid>` | Remove ou desativa* |

\*Se houver usuários ativos vinculados, o `DELETE` apenas define `ativo=false` (desativação suave). Sem vínculos, o registro é excluído.

**Query params (`GET` lista):**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `ativo` | boolean | Filtra por status |
| `busca` | string | Busca em `nome` ou `sigla` |

**Campo anotado na listagem:** `qtd_usuarios` — contagem de usuários com `is_active=true` vinculados à unidade. Alias espelhado: `usuarios_count` (compatível com o frontend Vue).

**Exemplo `GET` 200:**

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "nome": "Secretaria Municipal de Infraestrutura e Obras",
    "sigla": "SINFRA-OBRAS",
    "descricao": "Obras, pavimentação e manutenção urbana",
    "tom_ia": "objetivo",
    "tom_ia_display": "Direto ao ponto, ágil e conciso",
    "diretrizes_tom_ia": "Priorize prazos e localização exata da obra.",
    "ativo": true,
    "qtd_usuarios": 8,
    "usuarios_count": 8,
    "criado_em": "2024-01-15T10:30:00Z",
    "atualizado_em": "2024-11-10T14:20:00Z"
  }
]
```

**Exemplo `POST` request:**

```json
{
  "nome": "Guarda Municipal",
  "sigla": "GM",
  "descricao": "Segurança patrimonial e zeladoria",
  "tom_ia": "institucional",
  "diretrizes_tom_ia": "",
  "ativo": true
}
```

**Erros comuns:**

| HTTP | Motivo |
|------|--------|
| `401` | Token ausente ou inválido |
| `403` | Usuário autenticado sem perfil `SUPER_ADMIN` |
| `400` | Validação de campos |

---

### CRUD — Usuários internos

**Resource:** `/api/v1/backoffice/usuarios`

Lista apenas registros com `perfil` preenchido (servidores; exclui cidadãos).

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/backoffice/usuarios` | Lista usuários |
| `POST` | `/api/v1/backoffice/usuarios` | Cadastra servidor |
| `GET` | `/api/v1/backoffice/usuarios/<uuid>` | Detalhe |
| `PUT` | `/api/v1/backoffice/usuarios/<uuid>` | Atualização completa |
| `PATCH` | `/api/v1/backoffice/usuarios/<uuid>` | Atualização parcial |
| `DELETE` | `/api/v1/backoffice/usuarios/<uuid>` | Desativa (`is_active=false`) |

**Query params (`GET` lista):**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `perfil` | string | Filtra por `perfil_acesso.codigo` |
| `perfil_acesso_id` | UUID | Filtra por perfil |
| `unidade_id` | UUID | Filtra servidores da unidade |

**Exemplo `GET` 200:**

```json
[
  {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "nome": "Maria da Silva Santos",
    "email": "maria.santos@prefeitura.gov.br",
    "cpf": "123.456.789-00",
    "perfil": "super_admin",
    "perfil_acesso_id": "f47ac10b-58cc-4372-a567-0e02b2c3d480",
    "perfil_acesso_nome": "Super Admin",
    "unidade_id": null,
    "unidade_nome": null,
    "ativo": true,
    "ultimo_acesso": "2026-11-16T11:30:00Z",
    "criado_em": "2024-01-10T09:00:00Z",
    "atualizado_em": "2026-11-16T11:30:00Z"
  }
]
```

**Exemplo `POST` request (gestor setorial):**

```json
{
  "nome": "Carlos Mendes",
  "email": "carlos.mendes@prefeitura.gov.br",
  "cpf": "34567890122",
  "perfil": "gestor_setorial",
  "unidade_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "ativo": true,
  "senha": "SenhaTemporaria123"
}
```

- Campo `senha` é **opcional**. Se omitido, o backend gera senha aleatória e retorna em `senha_inicial` **uma única vez** na resposta `201`.

**Exemplo `POST` 201 (senha gerada):**

```json
{
  "id": "...",
  "nome": "Carlos Mendes",
  "perfil": "gestor_setorial",
  "unidade_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "senha_inicial": "k9Px2mNqR4vW8sL"
}
```

**Validações `400`:**

```json
{
  "unidade_id": ["Unidade é obrigatória para este perfil."]
}
```

```json
{
  "unidade_id": ["Este perfil não aceita vínculo com unidade."]
}
```

---

### POST — Resetar senha (Super Admin)

**POST** `/api/v1/backoffice/usuarios/<uuid>/resetar-senha`

Gera senha aleatória, persiste o hash no banco e devolve a senha em texto claro para o administrador repassar ao servidor (não envia e-mail nesta iteração).

**Request body:** vazio `{}` ou sem body.

**Response 200:**

```json
{
  "sucesso": true,
  "mensagem": "Senha redefinida. Entregue a senha temporária ao servidor.",
  "usuario_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "senha": "aB3cD9eF2gH6kL",
  "email": "carlos.mendes@prefeitura.gov.br"
}
```

**Permissão:** `IsSuperAdmin` (igual ao CRUD).

---

### Matriz RBAC (visão geral)

| Recurso | Quem acessa |
|---------|-------------|
| `/backoffice/perfis-acesso` | `regras.super_admin` |
| `/backoffice/unidades`, `/backoffice/usuarios` | `regras.super_admin` |
| Mesa / Kanban | `mesa_trabalho.ler` (+ ações específicas por rota) |
| Painel Setorial | `painel_setorial.ler` (+ `editar` / `assinar`) |
| Mapa IA | `mapa_ia.acessar` / `agrupar` |
| Configurações | `configuracoes.ler` / `editar` |

Perfis customizados combinam módulos livremente (padrão GLPI).

---

### CRUD — Catálogo de Serviços (Form Builder)

**Resource:** `/api/v1/backoffice/servicos-catalogo`  
**Modelo:** `catalogo.ServicoCatalogo` (já vinculado a `Protocolo.servico` via FK — sem migração de protocolo).

**Permissão:** Super Admin **ou** `configuracoes.editar` (RBAC dinâmico).

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/backoffice/servicos-catalogo` | Lista serviços (filtros: `ativo`, `busca`, `categoria_id`, `unidade_responsavel_id`) |
| `POST` | `/api/v1/backoffice/servicos-catalogo` | Cria serviço |
| `GET` | `/api/v1/backoffice/servicos-catalogo/<uuid>` | Detalhe |
| `PUT` / `PATCH` | `.../<uuid>` | Atualiza |
| `DELETE` | `.../<uuid>` | Exclui* ou desativa se houver protocolos |

\* Com protocolos vinculados: `ativo=false` (desativação suave).

#### Campos principais

| Campo API | Campo modelo | Descrição |
|-----------|--------------|-----------|
| `nome` | `nome` | Ex.: "Tapa Buraco" |
| `descricao` | `descricao` | Texto para o cidadão |
| `icone` | `icone` | Nome lógico do ícone ou URL |
| `sla_padrao_horas` | `sla_horas` | SLA padrão (int, ex. 48, 72) |
| `fluxo_tramitacao` | `fluxo_tramitacao` | `direto_secretaria` (default), `ouvidoria_encaminha`, `hibrido` — ver § Fluxo de tramitação |
| `unidade_responsavel_id` | `unidade_responsavel` | Papel depende do fluxo: executor padrão **ou** unidade do **canal** (`SET_NULL`) |
| `categoria_id` | `categoria` | Agrupamento no app (obrigatório na criação se não houver categoria padrão) |
| `formulario_schema` | `formulario_schema` | **Publicado** — Form Builder (PWA / chat em produção) |
| `schema_formulario` | `schema_formulario` | **Publicado** — JSON Schema (chat/IA) |
| `formulario_schema_rascunho` | `formulario_schema_rascunho` | Rascunho do Form Builder (`null` = sem rascunho) |
| `schema_formulario_rascunho` | `schema_formulario_rascunho` | Rascunho do JSON Schema |
| `versao_publicada` | `versao_publicada` | Contador da última versão publicada (default `1`) |
| `publicado_em` | `publicado_em` | Timestamp da última publicação dos schemas (`null` até a primeira publicação explícita) |
| `tem_rascunho_pendente` | *(property)* | `true` se há `*_rascunho` preenchido |
| `salvar_como_rascunho` | — | **Somente escrita** no `POST`/`PUT`/`PATCH` do serviço (ver abaixo) |
| `ativo` | `ativo` | Disponível ao cidadão |
| `permite_cluster` | `permite_cluster` | Default `true`. Se `false`, demandas deste serviço **não entram** no motor de cluster/Super OS do mapa IA (mesmo geográficamente próximas). Preservado em `POST .../clonar` e duplicação municipal. |
| `is_template` | `is_template` | **Somente leitura** na API de governança. Modelos globais (`true`) não aparecem no catálogo público nem na listagem CRUD padrão. |

#### Versionamento (rascunho / publicado) — v4.4

- **`GET /catalogo-servicos` e sessões ativas no PWA** continuam lendo apenas `formulario_schema` + `schema_formulario` **publicados** (retrocompatibilidade total).
- Edições com `"salvar_como_rascunho": true` no corpo do CRUD gravam schemas apenas em `*_rascunho`; metadados do serviço (`nome`, `sla`, `unidade`, etc.) seguem atualizando normalmente.
- Sem o flag (ou `false`), `PUT`/`PATCH` mantém o comportamento anterior: schemas vão direto para os campos publicados.
- Fluxo recomendado: **rascunho → sandbox (`usar_rascunho`) → publicar → histórico**.

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `.../servicos-catalogo/<uuid>/publicar` | Promove rascunho → produção; body opcional `{ "nota_versao": "..." }` |
| `POST` | `.../servicos-catalogo/<uuid>/descartar-rascunho` | Descarta `*_rascunho` sem publicar |
| `GET` | `.../servicos-catalogo/<uuid>/versoes` | Lista snapshots (`numero_versao`, `nota_versao`, `publicado_em`, `publicado_por_nome`) |
| `POST` | `.../servicos-catalogo/<uuid>/versoes/<int>/restaurar` | Copia snapshot para `*_rascunho` (testar no sandbox antes de republicar) |

**Nota:** o router de governança usa `trailing_slash=False` — **não** acrescente `/` ao final dessas rotas (URL com barra final retorna 404).

Modelo de auditoria: `catalogo.ServicoCatalogoVersao` — um registro por publicação (schemas completos + nota + autor).

**Visibilidade pública:** `GET /api/v1/catalogo-servicos` e contagem por categoria **sempre excluem** `is_template=true`.

#### Biblioteca de modelos (templates)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/backoffice/servicos-catalogo/templates` | Lista modelos globais (`is_template=true`) — mesmos campos do serviço (nome, ícone, categoria, schemas, SLA). |
| `POST` | `/api/v1/backoffice/servicos-catalogo/<uuid>/clonar` | Clona **template** ou **duplica** serviço municipal existente (mesma rota). |

**Body `POST .../clonar` (201):**

```json
{
  "unidade_responsavel_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

| Origem (`id` na URL) | `unidade_responsavel_id` | Comportamento |
|----------------------|--------------------------|---------------|
| `is_template=true` | **Obrigatório** | Novo serviço com mesmo nome, `ativo=true`, schemas copiados (deep copy). |
| `is_template=false` | Opcional | Duplicata com nome `«original» (Cópia)` (ou `… (Cópia 2)` se já existir), `ativo=false`, `is_template=false`. Sem unidade no body → mantém a unidade do serviço de origem. |

Sempre copia `descricao`, `icone`, `categoria`, `sla_horas`, `formulario_schema`, `schema_formulario`. Resposta = objeto completo do serviço criado (201).

**Seed operacional:** `python manage.py seed_templates` — cria/atualiza modelos «Zeladoria: Tapa Buraco», «Iluminação: Lâmpada Queimada», «Saúde: Foco de Dengue».

#### Fluxo de tramitação (`fluxo_tramitacao`) — v4.5

| Valor | `unidade_responsavel` | Comportamento operacional |
|-------|------------------------|---------------------------|
| `direto_secretaria` | **Executor padrão** (secretaria de campo) | Zeladoria e serviços setoriais: encaminhamento direto; scatter opcional. |
| `ouvidoria_encaminha` | **Unidade do canal** (Ouvidoria / E-SIC) | Protocolo titulado na ouvidoria; executores via despacho scatter + triagem (matriz/IA — ondas futuras). |
| `hibrido` | **Canal titular** com executor sugerido | Recepção centralizada com destino padrão editável na mesa. |

Retrocompatibilidade: serviços existentes permanecem `direto_secretaria`.

#### Matriz de roteamento temático (triagem determinística) — v4.9

**RBAC:** `IsAuthenticated` + permissões do módulo `configuracoes` (mesmo padrão de `servicos-catalogo`).

| Método | Rota | Ação |
|--------|------|------|
| `GET` | `/api/v1/backoffice/catalogo/servicos/<uuid:servico_id>/roteamento` | Lista regras do serviço |
| `POST` | idem | Cria regra |
| `PATCH` | `.../roteamento/<uuid:regra_id>` | Atualiza regra |
| `DELETE` | idem | Remove regra |

Rotas com barra final são aceitas. Serviço deve existir e `is_template=false`.

**Payload escrita (POST/PATCH):**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `chave_schema` | string | Campo em `schema_formulario.properties` (ex.: `categoria`) |
| `valor_condicao` | string | Igualdade exata com `dados_dinamicos[chave_schema]` |
| `unidade_sugerida` | UUID | Unidade executora sugerida (**deve estar ativa**) |
| `ativo` | bool | Default `true` |

**Resposta leitura:** inclui `id`, `unidade_sugerida_nome`, `criado_em`, `atualizado_em`.

**Erros:** `400` — duplicidade `(servico, chave_schema, valor_condicao)` com mensagem clara; unidade inativa ou inexistente. `403` — sem permissão. `404` — serviço ou regra inexistente.

Constraint: único por `(servico, chave_schema, valor_condicao)`.

#### Triagem sugerida no protocolo (`triagem_sugerida`) — v4.9

Gerada automaticamente na **criação do protocolo** (PWA ou chat) quando `servico.fluxo_tramitacao` é `ouvidoria_encaminha` ou `hibrido`. Motor determinístico (`deterministico_v1`); **não despacha** — protocolo permanece `em_analise`.

Ordem de evidências: (1) lookup `unidades_administrativas` preenchido pelo cidadão (`confianca` 1.0, `fonte` `lookup_cidadao`); (2) regras ativas da matriz (`confianca` 0.85, `fonte` `matriz_eixo`). Unidades deduplicadas (prevalece maior confiança).

**Formato persistido:**

```json
{
  "unidades_sugeridas": [
    {
      "id": "uuid",
      "nome": "Secretaria de Saúde",
      "confianca": 0.85,
      "fonte": "matriz_eixo",
      "motivo": "Regra categoria=saude"
    }
  ],
  "gerada_em": "2026-11-23T10:30:00Z",
  "versao_motor": "deterministico_v1"
}
```

`fluxo_tramitacao=direto_secretaria` → `{}` (sem sugestão de encaminhamento).

**Backoffice — dados:** campo `triagem_sugerida` em `GET /api/v1/backoffice/kanban` (fonte da Mesa), `GET /api/v1/backoffice/protocolos` e `GET /api/v1/backoffice/protocolos/<protocolo_id>` (detalhe; respeita `escopo_dados` / IDOR).

**Backoffice — UI (Mesa v4.10.1):** Kanban e lista exibem resumo compacto (“Sugere: …” + confiança); modal **Despachar** e detalhe do protocolo permitem **aplicar** a sugestão nas ordens de serviço (confirmação manual do servidor).

**Despacho scatter:** quando há triagem, `ProtocoloHistorico` registra se as unidades despachadas **confirmaram** ou **divergiram** da sugestão (auditoria de acurácia).

#### Triagem semântica (LLM) — v4.10

**Governança (`ServicoCatalogo`):**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `triagem_ia_ativa` | bool | Default `true`. Habilita enfileiramento da triagem semântica após a triagem determinística em `ouvidoria_encaminha` e `hibrido`. |

Exposto em `GET/PATCH/POST` do CRUD `backoffice/servicos-catalogo`. Clonagem/duplicação de serviços **preserva** a flag.

**Execução:** task Celery `executar_triagem_semantica_task(protocolo_id)` via `transaction.on_commit` após `executar_triagem_protocolo`. Sem chave LLM ou em erro de rede/parse → **mantém** `triagem_sugerida` determinística (apenas log).

**Payload enriquecido (`versao_motor: hibrido_llm_v1`):**

| Campo extra | Descrição |
|-------------|-----------|
| `resumo_motivo` | Síntese em 1 frase do encaminhamento sugerido pela IA |
| `versao_modelo` | Identificador do modelo LLM usado (ex.: Groq) |
| `unidades_sugeridas[].fonte` | `llm` (além de `lookup_cidadao`, `matriz_eixo`) |

Regras de merge: UUID deve existir em unidade ativa; `confianca` mínima 0.50; até 3 unidades; duplicatas unificadas (fonte determinística preservada, maior confiança, motivo complementado).

#### Lookup dinâmico — datasource de formulário

**Endpoint público (PWA / chat):**

| Método | Rota | Auth |
|--------|------|------|
| `GET` | `/api/v1/catalogo/lookup/unidades` | Nenhuma (`AllowAny`, como `catalogo-servicos`) |

Query: `busca` (filtra nome/sigla), `limit` (1–500, default 200).

**Resposta 200:**

```json
{
  "datasource": "unidades_administrativas",
  "items": [
    { "id": "uuid", "nome": "Secretaria Municipal de Saúde" }
  ]
}
```

Rota com barra final (`.../unidades/`) é aceita. Apenas unidades **ativas**; retorno mínimo (`id`, `nome`) por privacidade.

**`formulario_schema` — tipo `lookup`:**

```json
{
  "name": "unidade_referencia",
  "type": "lookup",
  "label": "Secretaria relacionada",
  "datasource": "unidades_administrativas",
  "ui_widget": "searchable_select",
  "required": false
}
```

Datasources suportados: `unidades_administrativas`. Widgets: `searchable_select`, `select`.

**Espelho em `schema_formulario.properties.<name>`:**

```json
{
  "type": "string",
  "format": "uuid",
  "title": "Secretaria relacionada",
  "x-ouvia-datasource": "unidades_administrativas",
  "x-ouvia-ui-widget": "searchable_select",
  "x-ouvia-tipo-campo": "lookup"
}
```

Validação de protocolo: valores devem ser **UUID** válido referenciando unidade existente (extensão em `catalogo.validators`).

Governança: `validate_schema_formulario` rejeita `x-ouvia-datasource` desconhecido.

#### Estrutura `formulario_schema` (array)

Cada item define um campo renderizado no app:

```json
[
  {
    "name": "foto_local",
    "type": "image",
    "label": "Foto do Local",
    "required": true
  },
  {
    "name": "ponto_referencia",
    "type": "text",
    "label": "Ponto de Referência",
    "required": false,
    "placeholder": "Ex.: em frente ao mercado"
  },
  {
    "name": "urgencia",
    "type": "select",
    "label": "Urgência",
    "required": true,
    "options": [
      { "value": "baixa", "label": "Baixa" },
      { "value": "alta", "label": "Alta" }
    ]
  }
]
```

**Tipos suportados:** `text`, `textarea`, `number`, `select`, `image`, `date`, `boolean`, `email`, `tel`.

**Validação backend:** `name` único por serviço; tipos na lista acima; `options` obrigatório para `select`.

**Resposta do cidadão:** valores preenchidos continuam em `Protocolo.dados_dinamicos` (chave = `name` de cada campo).

#### Exemplo `POST` 201

```json
{
  "nome": "Poda de Árvore",
  "descricao": "Solicitação de poda ou remoção de árvore em via pública.",
  "icone": "tree",
  "sla_padrao_horas": 72,
  "unidade_responsavel_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "categoria_id": "550e8400-e29b-41d4-a716-446655440000",
  "ativo": true,
  "formulario_schema": [
    { "name": "foto_local", "type": "image", "label": "Foto", "required": true }
  ]
}
```

#### API pública (cidadão)

`GET /api/v1/catalogo-servicos` inclui `formulario_schema`, `schema_formulario`, `icone` e `fluxo_tramitacao` para o PWA montar o formulário e rotular o fluxo.

---

### Catálogo — metadados IA, conversa e elegibilidade (chat PWA)

O assistente conversacional usa **`schema_formulario`** (JSON Schema + `$metadata`) para ordem dos passos, instruções de extração e **regras de elegibilidade**. O array paralelo **`formulario_schema`** é o que o backoffice edita no Form Builder; na gravação governança, ambos são persistidos (o front monta `schema_formulario` a partir do roteiro).

#### Propriedades por campo (`schema_formulario.properties.<name>`)

| Chave | Uso |
|-------|-----|
| `title` / `description` | Texto base do passo (legado) |
| `x-ouvia-ui-pergunta` | Pergunta humanizada exibida no chat |
| `x-ouvia-ia-extract` | Instrução de extração (equiv. `ia_instrucao` no Form Builder) |
| `x-ouvia-ia-reprompt` | Repescagem quando a IA não entende (equiv. `ia_repescagem`) |
| `x-ouvia-tipo-campo` | `geolocation`, `image`, `lookup`, etc. |
| `x-ouvia-datasource` | `unidades_administrativas` (listas do sistema — ver § Lookup dinâmico) |
| `x-ouvia-ui-widget` | `searchable_select` \| `select` (com datasource) |

#### `$metadata` (nível serviço)

| Chave | Tipo | Descrição |
|-------|------|-----------|
| `ordem_campos` | `string[]` | Ordem do roteiro conversacional |
| `ia_conversacional` | `boolean` | Chat por passos (PWA) |
| `exige_localizacao` | `boolean` | Há campo geo no roteiro |
| `exige_foto` | `boolean` | Há campo imagem no roteiro |
| `regras_elegibilidade` | `object[]` | Lista única de regras (por campo + protocolo) |

#### Regras de elegibilidade — modelo de dados

Cada item em `regras_elegibilidade` (e espelhado em `formulario_schema[].regra_elegibilidade` quando escopo = campo):

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `ativo` | sim | `false` ignora a regra |
| `tipo` | sim | `interpretacao` (NL + LLM), `texto` (match exato), `idade_faixa` **(legado)** |
| `mensagem` | sim | Texto ao cidadão ao bloquear (`fluxo_bloqueado`) |
| `campo` | escopo campo | `name` do passo avaliado |
| `condicao` | `interpretacao` | Frase em português: “Bloquear quando…” |
| `valores` | `texto` | Lista de strings que disparam bloqueio |
| `escopo` | protocolo | Valor fixo `"protocolo"` — avalia **vários campos** já preenchidos |

**Escopos:**

1. **Por campo** — dispara assim que aquele passo tem valor (bloqueio cedo, ex.: idade fora da faixa).
2. **Por protocolo** — condição em NL sobre o snapshot do que já foi coletado (ex.: idade + doença juntos). Sem `campo`. Avaliado após regras por campo, a cada turno do chat.

**Runtime** (`catalogo.eligibility` + `llm_orchestrator`):

- Ordem: regras com `campo` na ordem da lista; depois regras `escopo: protocolo`.
- `interpretacao`: LLM retorna `deve_bloquear`; em dúvida ou LLM indisponível → **não bloqueia**.
- `texto`: match normalizado, sem LLM.
- `idade_faixa`: apenas schemas antigos; no backoffice legado é convertido para condição em NL.

**Resposta do chat ao bloquear:** `fluxo_bloqueado: true`, fase `INELEGIVEL`, `resposta_cidadao` = `mensagem` da regra.

#### Exemplo concreto — Proteção Animal (castração)

Serviço de referência: **`Agendamento de Castração de Animais`**.

- Regra no passo `idade` (`interpretacao`) — faixa 12 meses a 9 anos.
- Regra no passo `doencas` (`interpretacao`) — animal doente / “Sim”.
- Regra de **protocolo** — cruzamento idade + saúde quando ambas já constam no protocolo.

Arquivos:

- `docs/exemplos/protecao-animal-castracao.json` — resumo JSON.
- `backend/catalogo/exemplos/protecao_animal_castracao.py` — payload completo.
- Comando: `python manage.py aplicar_exemplo_protecao_animal` (opcional `--dry-run`).

Trecho de `regras_elegibilidade`:

```json
[
  {
    "ativo": true,
    "tipo": "interpretacao",
    "campo": "idade",
    "condicao": "Bloquear se a idade informada for menor que 12 meses ou maior que 9 anos.",
    "mensagem": "Para castração, o animal precisa ter entre 12 meses e 9 anos..."
  },
  {
    "ativo": true,
    "escopo": "protocolo",
    "tipo": "interpretacao",
    "condicao": "Bloquear se idade e saúde, juntos, indicarem inelegibilidade para castração.",
    "mensagem": "Pelas informações que você passou, este agendamento não pode seguir aqui..."
  }
]
```

#### Roadmap — fluxograma visual (v2 UX, não implementado)

Motor atual cobre condições em NL sem novos `if` no código. A **v2** prevista no backoffice:

- Árvore **se / senão** entre passos (ramificações condicionais).
- Ordem explícita de avaliação e regras “somente se campo X preenchido”.
- Persistência provável em `$metadata.fluxo_elegibilidade` (versão + nós), mantendo compatibilidade com `regras_elegibilidade` v1.

Até lá, combinar **regra por passo** + **regra de protocolo** cobre a maioria dos casos municipais.

---

### Catálogo — Sandbox de chat (simulador backoffice, dry-run)

**Rota:** `POST /api/v1/backoffice/servicos-catalogo/<uuid>/sandbox`  
**Permissão:** mesma do CRUD de catálogo — Super Admin ou `configuracoes.editar`.

**Objetivo:** testar roteiro, extração e elegibilidade **sem** criar `SessaoChat`, `Protocolo` ou mensagens persistidas. O estado do turno vive em memória (`SessaoSandbox`) apenas na requisição.

#### Request body

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `usar_rascunho` | boolean \| omitido | Default: `true` se `tem_rascunho_pendente`, senão `false`. Simula rascunho ou versão publicada |
| `mensagem` | string | Última fala simulada do cidadão (opcional no 1º turno) |
| `dados_parciais` | object | Slots já preenchidos (`idade`, `tipo`, …) |
| `dados_slot` | object | Escolha de UI (`escolha_campo`), normalizada como no PWA |
| `anexos_novos` | int | Simula fotos enviadas no turno |
| `localizacao_ok` | bool | Marca GPS como confirmado |
| `localizacao` | object | `{ latitude, longitude, endereco? }` |
| `historico` | array | `[{ "role": "user"\|"assistant", "content": "..." }]` para contexto de redação |

#### Response `200`

| Campo | Descrição |
|-------|-----------|
| `modo` | Sempre `"sandbox"` |
| `origem_schema` | `"rascunho"` ou `"publicado"` — schemas usados no turno |
| `resposta_cidadao` | Texto que o PWA mostraria no balão |
| `acao_ui` | `escolha_campo`, `solicitar_localizacao`, `solicitar_foto`, `revisao_final`, ou `null` |
| `payload_ui` | Config de escolha (`opcoes`, `titulo`, `modo`, …) quando `acao_ui=escolha_campo` |
| `dados_parciais` | Estado acumulado dos slots após o turno |
| `dados_extraidos_turno` | O que a extração LLM inferiu neste turno |
| `fluxo_bloqueado` / `mensagem_bloqueio` | Regra de elegibilidade ativada |
| `ir_para_revisao` | Campos obrigatórios satisfeitos |
| `historico_sugerido` | Histórico para o próximo POST do simulador |
| `servico_id` / `servico_nome` | Metadados do serviço testado |

#### Slot filling na abertura (PWA — após confirmar serviço)

Quando o cidadão confirma o `ServicoCatalogo` sugerido e já existe uma **mensagem inicial substantiva** (≥ 20 caracteres, não sendo só “oi”/“sim”), o motor tenta **uma única extração estruturada** dos campos elegíveis do `schema_formulario` publicado (exclui lookup, imagem, geo).

| Aspecto | Comportamento |
|---------|----------------|
| **Idempotência** | Cache Redis `slot_filling:<sessao_id>:<sha256_16>` TTL 3600s — evita re-chamar o LLM no reenvio/reload |
| **Confiança** | Só persiste campos com `confianca ≥ 0.80` após validação estrita (enum, tipos, `minLength`) |
| **Persistência** | Merge em `dados_coletados` **sem sobrescrever** valores já preenchidos |
| **Elegibilidade** | Regras de passo/protocolo rodam no turno seguinte (determinístico), podendo bloquear já na abertura |
| **UX** | Prefixo opcional na próxima fala da IA: “Entendi! Já identifiquei …” (rótulos `title` / `enumNames`) |
| **Fallback** | Sem API key, timeout ou nenhum campo válido → fluxo pergunta campo a campo (sem erro ao cidadão) |
| **Diagnóstico** | Opcional em `dados_coletados._meta`: `slot_filling_hash`, `slot_filling_campos` (não altera contrato REST do PWA) |

Endpoints e payloads do PWA (`POST /chat/interagir`, polling de mensagens) **não mudam**.

#### Produção vs Sandbox

| | Produção (PWA) | Sandbox |
|---|----------------|---------|
| Contexto | `SessaoChat` + Celery | `SessaoSandbox` em RAM |
| Persistência | Mensagens, anexos, protocolo | Nenhuma escrita |
| Motor | `LLMOrchestrator.processar_turno` | `simular_turno_catalogo_sandbox` → mesmo `passo_deterministico_preenchimento` |

#### Onda 1 — redação de perguntas (no-code)

No preenchimento, o orquestrador usa metadados do gestor:

1. **Repescagem** (`x-ouvia-ia-reprompt` / `ia_repescagem`) — quando a extração falha no campo corrente, o texto de repescagem é usado literalmente.
2. **Instrução** (`x-ouvia-ia-extract` / `ia_instrucao`) — chamada LLM curta para redigir pergunta acolhedora (sem template fixo “Ótimo. Agora, qual é o…”).
3. **Fallback** — `x-ouvia-ui-pergunta` / `title`.
4. **UI** — `acao_ui` e `payload_ui` derivados do schema (`enum` → `escolha_campo`, `geolocation` → `solicitar_localizacao`, `image` → `solicitar_foto`).

#### Exemplo

```http
POST /api/v1/backoffice/servicos-catalogo/ce0c1a4c-cfd6-421d-8301-898c3655fd20/sandbox
Content-Type: application/json

{
  "mensagem": "tenho um cão",
  "dados_parciais": {}
}
```

---

### Sprint 5 — Dashboard de Eficiência (Process Mining)

#### GET `/api/v1/backoffice/dashboard/eficiencia`

Métricas agregadas no banco (ORM) para o painel de eficiência: **TMA**, **funil por status** e **ranking de SLA por secretaria**.

**Permissão:** usuário `is_staff` com `mesa_trabalho.ler` ou Super Admin.

**Escopo (RBAC):**

| Perfil | Escopo |
|--------|--------|
| Super Admin / `super_admin` / `ouvidor` | Município inteiro |
| `gestor_setorial` (com `unidade` vinculada) | Protocolos da secretaria (`servico.unidade_responsavel` ou OS com mesma `unidade`) |

**Query params opcionais:**

| Parâmetro | Descrição |
|-----------|-----------|
| `bairro` | Filtra por `Protocolo.dados_dinamicos.bairro` (JSON); `iexact` + fallback `icontains` |

**Definições:**

- **TMA (geral e por unidade):** média de `data_atualizacao - data_criacao` **apenas** para protocolos `resolvido`. `rejeitado` entra no funil, mas **não** entra na média de tempo (evita distorcer a eficiência).
- **SLA (Mesa e KPIs do dashboard):** prazo = `data_criacao + servico.sla_horas`; **vencido** se `now() > prazo` — mesma regra de `calcular_sla` / filtro `sla_vencido` do Kanban (inclui concluídos ainda “atrasados” no relógio operacional).
- **KPIs de cumprimento (`resumo_sla_mesa`):** contagem por **itens do Kanban** (protocolos sem Super OS + um cartão por Super OS), não por `COUNT(*)` bruto de protocolos (filhos agregados não viram cartão).
- **Ranking (`ranking_sla_unidades`):** base = **cartões da Mesa**; agrupa por secretaria (`servico.unidade_responsavel` ou unidade da OS ativa). Itens sem vínculo vão para o bucket `sem-secretaria-vinculada` (`sem_vinculo_catalogo: true`), ordenado por maior `% vencidos`.

**Resposta (200):**

```json
{
  "escopo": "municipio",
  "unidade_id": null,
  "gerado_em": "2026-11-17T14:30:00+00:00",
  "tma_geral": {
    "horas": 52.75,
    "protocolos_concluidos": 318
  },
  "funil_status": [
    { "status": "em_analise", "label": "Em análise", "total": 42 },
    { "status": "em_andamento", "label": "Em andamento", "total": 88 },
    { "status": "aguardando_revisao", "label": "Aguardando revisão", "total": 12 },
    { "status": "resolvido", "label": "Resolvido", "total": 1205 },
    { "status": "rejeitado", "label": "Rejeitado", "total": 7 }
  ],
  "ranking_sla_unidades": [
    {
      "unidade_id": "uuid",
      "nome": "Secretaria de Zeladoria",
      "sigla": "ZEL",
      "total_protocolos": 890,
      "pct_no_prazo": 61.5,
      "pct_vencidos": 38.5,
      "tma_horas": 71.2,
      "protocolos_concluidos": 640
    }
  ],
  "resumo_sla_mesa": {
    "total_itens": 412,
    "vencidos": 148,
    "no_prazo": 264,
    "taxa_cumprimento": 64.08
  },
  "totais": {
    "protocolos": 1354,
    "itens_mesa": 412
  }
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `escopo` | `municipio` \| `unidade` | Visão aplicada ao usuário |
| `unidade_id` | UUID \| null | Preenchido quando `escopo=unidade` |
| `tma_geral.horas` | number \| null | TMA médio em horas (2 casas); base = só `resolvido` |
| `tma_geral.protocolos_concluidos` | int | Quantidade de `resolvido` na base do TMA (exclui `rejeitado`) |
| `resumo_sla_mesa` | object | Alinhado aos contadores da Mesa de Trabalho (Kanban) |
| `resumo_sla_mesa.total_itens` | int | Cartões no Kanban (escopo RBAC) |
| `resumo_sla_mesa.taxa_cumprimento` | number | `%` itens com SLA não vencido (regra Mesa) |
| `totais.protocolos` | int | Todos os protocolos no escopo (inclui filhos de Super OS) |
| `totais.itens_mesa` | int | Igual a `resumo_sla_mesa.total_itens` |
| `ranking_sla_unidades[].pct_vencidos` | number | Percentual de protocolos com SLA estourado |

---

### Sprint 5 — Mapa GIS Executivo (Heatmap)

#### GET `/api/v1/backoffice/dashboard/mapa-calor`

Coordenadas puras **\[lat, lng\]** para plotagem em Leaflet (heatmap executivo). Consulta enxuta — **sem instanciar** objetos `Protocolo` completos; extrai `ST_Y` / `ST_X` do `localizacao` (PostGIS `PointField`, SRID 4326).

**Permissão:** `is_staff` + `mesa_trabalho.ler` ou Super Admin (mesma regra do dashboard de eficiência).

**Escopo (RBAC):**

| Perfil | Escopo |
|--------|--------|
| Super Admin / `ouvidor` | Município inteiro |
| `gestor_setorial` | Somente protocolos da unidade (`servico.unidade_responsavel` ou OS com a mesma `unidade`); **não** pode passar `unidade_responsavel_id` de outra secretaria (403). |

**Query params (filtros macro):**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `data_inicio` | ISO date/datetime | `data_criacao >=` |
| `data_fim` | ISO date/datetime | `data_criacao <=` (fim do dia se for só data) |
| `categoria_id` | UUID | Filtra `servico.categoria_id` |
| `servico_id` | UUID | Filtra serviço do catálogo |
| `unidade_responsavel_id` | UUID | Secretaria (`servico.unidade_responsavel` ou OS vinculada); omitido no gestor setorial (escopo já fixo) |
| `status` | string | Lista vírgula: `em_analise`, `em_andamento`, `aguardando_revisao`, `resolvido`, `rejeitado` |
| `bairro` | string | Bairro em `dados_dinamicos.bairro` (valor da listagem `/dashboard/bairros`) |
| `limite` | int | Máx. pontos retornados (padrão **5000**, teto 5000) |
| `agregar_pesos` | `1` \| `true` | Agrega coordenadas arredondadas (4 casas) e devolve `pontos_ponderados` `\[lat, lng, peso\]` |
| `incluir_demandas` | `0` \| `false` | Omite `demandas` (só heat). Padrão: **incluir** resumo clicável por protocolo |

**Resposta (200):**

```json
{
  "gerado_em": "2026-11-17T12:55:00+00:00",
  "filtros_aplicados": { "escopo": "municipio" },
  "pontos": [
    [-23.5507, -46.1826],
    [-23.5506, -46.1809]
  ],
  "total": 6,
  "retornados": 2,
  "limite": 5000,
  "truncado": false,
  "demandas": [
    {
      "id": "uuid",
      "codigo": "PROT-2026-001",
      "status": "em_analise",
      "descricao_resumo": "Buraco na via…",
      "endereco": "Rua X, Vila da Prata, Mogi das Cruzes",
      "bairro": "Vila da Prata",
      "latitude": -23.5507,
      "longitude": -46.1826,
      "data_criacao": "2026-11-15T10:00:00+00:00",
      "cidadao": { "nome": "Maria Silva" },
      "servico": { "id": "uuid", "nome": "Zeladoria urbana" },
      "sla": { "sla_horas": 72, "vencido": true, "horas_restantes": -12.5, "prazo_em": "..." }
    }
  ]
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `pontos` | `number[][]` | Pares **\[latitude, longitude\]** para Leaflet (`[lat, lng]`) |
| `demandas` | `object[]` | Resumo por protocolo (marcadores clicáveis no GIS). Omitido se `agregar_pesos=true` ou `incluir_demandas=false` |
| `pontos_ponderados` | `number[][]` | Presente se `agregar_pesos=true` — `[lat, lng, peso]` |
| `total` | int | Protocolos **com geo** que atendem aos filtros (antes do `limite`) |
| `retornados` | int | Quantidade de entradas em `pontos` |
| `truncado` | bool | `true` se `total > retornados` por causa do `limite` |

**Erros:** `403` se gestor setorial tentar outra `unidade_responsavel_id`.

**Notas de performance:** `values_list` + funções PostGIS; apenas registros com `localizacao IS NOT NULL`; ordenação por `-data_criacao` no modo pontual.

#### GET `/api/v1/backoffice/dashboard/bairros`

Lista leve de **bairros distintos** onde há protocolos no escopo RBAC do usuário (para filtros do mapa e do painel de eficiência).

**Permissão:** igual aos demais endpoints do dashboard analítico.

**Fonte (protocolos com `localizacao` no escopo RBAC):** inferência em `protocolo_localidade` — ordem `dados_dinamicos.bairro` → parsing de `endereco_texto` (ex. Nominatim: “Vila da Prata”) → `usuario.endereco.bairro` (`EnderecoCidadao`). Filtro `bairro` no mapa/eficiência usa as mesmas fontes (`icontains`/`iexact` em texto e JSON).

**Filtro eficiência:** `GET /backoffice/dashboard/eficiencia?bairro=...` (opcional).

**Resposta (200):**

```json
{
  "bairros": ["Braz Cubas", "Centro", "Vila Augusta"],
  "total": 3
}
```

---

#### GET `/api/v1/backoffice/dashboard/inelegibilidade`

Métricas do **Escudo Político** — sessões de chat barradas por regras de elegibilidade (IA).

**Permissão:** `is_staff` + `mesa_trabalho.ler` ou Super Admin (mesmo RBAC dos demais dashboards).

**Modelo:** `SessaoChat.motivo_inelegibilidade` preenchido quando `fluxo_bloqueado` / fase `INELEGIVEL`.

**Query params (opcionais):**

| Parâmetro | Descrição |
|-----------|-----------|
| `data_inicio` / `data_fim` | Intervalo em `criado_em` da sessão (ISO date/datetime) |
| `unidade_responsavel_id` | Filtra por secretaria do serviço (`servico_identificado.unidade_responsavel`) |
| `servico_id` | UUID do serviço |
| `categoria_id` | UUID da categoria do catálogo |

**Resposta (200):**

```json
{
  "escopo": "municipio",
  "unidade_id": null,
  "gerado_em": "2026-11-18T12:00:00-03:00",
  "filtros_aplicados": {},
  "total_sessoes_inelegiveis": 42,
  "ranking_por_servico": [
    {
      "servico_id": "uuid",
      "servico_nome": "Agendamento de Castração de Animais",
      "total": 15,
      "rotulo": "Agendamento de Castração de Animais: 15 bloqueio(s)"
    }
  ],
  "ranking_por_motivo": [
    { "motivo": "Qual a idade dele · regra interpretacao", "total": 12 },
    { "motivo": "Protocolo · Bloquear se idade fora da faixa…", "total": 8 }
  ]
}
```

`ranking_por_motivo` ordenado por volume (nuvem de inelegibilidade). Gestor setorial: escopo restrito à própria unidade; **403** se `unidade_responsavel_id` for de outra secretaria.

---

### Sprint 5 — Matriz de Qualidade Executiva (SLA × Satisfação)

#### Modelo `AvaliacaoProtocolo` (fonte canônica CSAT)

OneToOne com `Protocolo`. Dashboards usam esta tabela; `Protocolo.nota_satisfacao` é espelho legado para notificações/demo.

Preenchimento: `POST /api/v1/app/protocolos/<uuid>/avaliar`.

#### GET `/api/v1/backoffice/dashboard/qualidade`

Cruzamento **taxa de SLA cumprido** vs **média de satisfação** por secretaria (`servico.unidade_responsavel`).

**Permissão:** `is_staff` + `mesa_trabalho.ler` ou Super Admin (igual aos demais dashboards).

**Escopo (RBAC):**

| Perfil | Escopo |
|--------|--------|
| Super Admin / `ouvidor` | Todas as secretarias |
| `gestor_setorial` | Apenas protocolos da unidade (`servico.unidade_responsavel` ou OS); **403** se `unidade_responsavel_id` for de outra secretaria |

**Query params (opcionais):**

| Parâmetro | Descrição |
|-----------|-----------|
| `bairro` | Mesmo filtro territorial dos demais painéis |
| `unidade_responsavel_id` | UUID — restringe a uma secretaria (município) |

**Métricas por unidade (`matriz_unidades[]`):**

| Campo | Descrição |
|-------|-----------|
| `unidade_id`, `nome`, `sigla` | Secretaria; bucket `sem-secretaria-vinculada` se catálogo sem vínculo |
| `taxa_sla_cumprido` | % dos protocolos **resolvidos** com `data_atualizacao` ≤ prazo SLA |
| `media_satisfacao` | Média `AvaliacaoProtocolo.nota` (1 casa decimal) ou `null` |
| `total_avaliacoes` | Protocolos resolvidos com avaliação no escopo |
| `percentual_satisfeitos` | % notas 4 ou 5 sobre `total_avaliacoes` |
| `total_resolvidos` | Denominador do SLA (status `resolvido` no escopo) |

**Resposta (200):**

```json
{
  "escopo": "municipio",
  "unidade_id": null,
  "gerado_em": "2026-11-17T14:00:00+00:00",
  "filtros_aplicados": {},
  "resumo_geral": {
    "total_resolvidos": 42,
    "taxa_sla_cumprido": 71.43,
    "media_satisfacao": 4.1,
    "total_avaliacoes": 38,
    "percentual_satisfeitos": 82.5
  },
  "matriz_unidades": [
    {
      "unidade_id": "uuid",
      "nome": "Secretaria de Obras",
      "sigla": "OBR",
      "taxa_sla_cumprido": 85.0,
      "media_satisfacao": 4.5,
      "total_avaliacoes": 12,
      "total_resolvidos": 20,
      "resolvidos_no_prazo": 17,
      "sem_vinculo_catalogo": false
    }
  ]
}
```

**Agregação:** Django `Avg`, `Count`, `Sum`, `Case`/`When` sobre prazo SLA (mesma regra de `calcular_sla` / `analytics_service`).

---

### Changelog

- **v4.10.1** (Nov 23, 2026): Mesa — `triagem_sugerida` no `GET /backoffice/kanban`; indicadores no kanban/lista e painel no modal de despacho; slot filling na abertura do chat (Redis + schema)
- **v4.10** (Nov 23, 2026): Onda 4 — `triagem_ia_ativa` no catálogo; triagem semântica assíncrona (Celery + LLM) com merge em `triagem_sugerida` (`hibrido_llm_v1`, `resumo_motivo`, `versao_modelo`, fonte `llm`)
- **v4.9** (Nov 23, 2026): Onda 3 — CRUD `/backoffice/catalogo/servicos/<id>/roteamento`; motor `triagem_sugerida` determinístico em `Protocolo`; auditoria de despacho vs sugestão; exposição no detalhe backoffice
- **v4.8** (Nov 19, 2026): Catálogo — `fluxo_tramitacao`, `MatrizRoteamentoTematico`, tipo `lookup` + `GET /catalogo/lookup/unidades`; semântica de `unidade_responsavel` por fluxo
- **v4.7.1** (Nov 19, 2026): `GET /app/notificacoes/vapid-public-key`; comando `manage.py generate_vapid`; derivação da chave pública a partir de PEM quando só `VAPID_PRIVATE_KEY` (caminho) está definido
- **v4.7** (Nov 19, 2026): Onda 4 — `NotificacaoCidadao`, `PushSubscription`; `GET/PATCH /app/notificacoes`, `POST /app/notificacoes/push-subscribe`; Celery `enviar_notificacao_push_task` (pywebpush + VAPID); gatilhos status protocolo e resposta IA
- **v4.6** (Nov 19, 2026): CSAT Onda 3B — `pode_avaliar`/`avaliacao` no detalhe PWA; dashboard qualidade com `AvaliacaoProtocolo` + `percentual_satisfeitos`; escopo `escopo_dados`
- **v4.5** (Nov 19, 2026): Onda 3 — Escopo de dados em `get_protocolo_backoffice` (404 IDOR setorial); `ServicoCatalogo.permite_cluster` (governança + filtro no motor de cluster IA); CSAT `AvaliacaoProtocolo` OneToOne; `POST /app/protocolos/<id>/avaliar`
- **v4.4** (Nov 18, 2026): Versionamento de schema — rascunho/publicado em `ServicoCatalogo`, `ServicoCatalogoVersao`, `salvar_como_rascunho`, rotas publicar/descartar/versoes/restaurar; sandbox `usar_rascunho` + `origem_schema`
- **v4.3** (Nov 18, 2026): Governo Digital — `UnidadeAdministrativa.tom_ia` + `diretrizes_tom_ia`; persona injetada no `llm_orchestrator` (produção e sandbox)
- **v4.2** (Nov 18, 2026): `SessaoChat.motivo_inelegibilidade`; `GET /backoffice/dashboard/inelegibilidade` (ranking serviço/motivo)
- **v4.1** (Nov 18, 2026): `POST .../clonar` também duplica serviços municipais (sufixo «(Cópia)», inativo por padrão, unidade opcional)
- **v4.0** (Nov 17, 2026): Biblioteca de modelos — `ServicoCatalogo.is_template`; `GET .../templates`; `POST .../clonar`; seed `seed_templates`
- **v3.9** (Nov 17, 2026): Sandbox `POST .../servicos-catalogo/<id>/sandbox` (dry-run); Onda 1 — perguntas via `ia_instrucao`/`ia_repescagem` no `llm_orchestrator`
- **v3.8** (Nov 17, 2026): Catálogo — documentação de elegibilidade (`interpretacao`, `texto`, `escopo: protocolo`), metadados `x-ouvia-ia-*`, exemplo Proteção Animal/castração (`docs/exemplos/protecao-animal-castracao.json`, comando `aplicar_exemplo_protecao_animal`)
- **v3.7** (Nov 17, 2026): Matriz de Qualidade — campos `nota_satisfacao`/`comentario_satisfacao` em `Protocolo`; `GET /backoffice/dashboard/qualidade`
- **v3.6.4** (Nov 17, 2026): Mapa GIS — `demandas[]` com resumo clicável (visão 360º no backoffice); query `incluir_demandas`
- **v3.6.3** (Nov 17, 2026): Na criação do protocolo (API + chat), preenche `dados_dinamicos.bairro/cidade`; comando `sincronizar_bairro_protocolos`
- **v3.6.2** (Nov 17, 2026): Bairros GIS via `endereco_texto` + `EnderecoCidadao` (`protocolo_localidade`), não só JSON
- **v3.6.1** (Nov 17, 2026): Filtro `bairro` em eficiência e mapa-calor; `GET /backoffice/dashboard/bairros`
- **v3.6** (Nov 17, 2026): `GET /backoffice/dashboard/mapa-calor` — heatmap GIS executivo; serviço `mapa_calor_service`
- **v3.5.2** (Nov 17, 2026): SLA do dashboard alinhado à Mesa (`resumo_sla_mesa`, `totais.itens_mesa`); regra `now() > prazo` em ranking e KPIs
- **v3.5.1** (Nov 17, 2026): TMA do dashboard considera somente status `resolvido` (rejeitados permanecem no funil)
- **v3.5** (Nov 17, 2026): Sprint 5 — `GET /backoffice/dashboard/eficiencia` (TMA, funil, ranking SLA); serviço `analytics_service`; escopo RBAC ouvidor/município vs gestor setorial
- **v3.4** (Nov 17, 2026): Central de Notificações Super Admin — `GET .../admin/notificacoes/auditoria`, `POST .../admin/notificacoes/broadcast`; gatilhos em `ConfiguracaoSistema` (`notificar_novos_despachos`, `notificar_sla_vencido`, `notificar_novas_super_os`); task Celery `notificar_sla_vencido_task`
- **v3.3** (Nov 17, 2026): Catálogo de Serviços governança — `formulario_schema`, `icone`, `unidade_responsavel`; CRUD `/backoffice/servicos-catalogo`; permissão Super Admin ou `configuracoes.editar`
- **v3.2** (Nov 17, 2026): Matriz Vue 6×4 — módulos `textos_padrao`, `gestao_usuarios`; ações uniformes `ler|criar|editar|excluir`; aliases legados (`despachar`→`criar`, `assinar`→`editar`, `acessar`→`ler`); campos API `slug`, `requer_vinculo`, `ativo`, `usuarios_count`; payload usuário com `perfil_acesso_id` (UUID)
- **v3.1** (Nov 17, 2026): RBAC dinâmico — modelo `PerfilAcesso` + JSON `permissoes`; `Usuario.perfil_acesso` (remove enum `perfil`); CRUD `/backoffice/perfis-acesso`; `HasModulePermission` / `usuario_tem_permissao`; seeds `super_admin`, `ouvidor`, `gestor_setorial`, `operador_campo`
- **v3.0** (Nov 17, 2026): Governança Sprint 4 — CRUD unidades/usuários, `resetar-senha`, `IsSuperAdmin`, `GET /backoffice/mesa/unidades`
- **v2.2** (Nov 16, 2026): âncora operacional na IA (`criar_retroativa`), `POST .../super-os/retroativa`, bloqueio de `agrupar-mapa` com OS ativa
- **v2.1** (Nov 16, 2026): `GET .../backoffice/kanban`, `GET .../super-os/<uuid>` (dossiê), flags `is_super_os` e `qtd_chamados_vinculados` no setorial
- **v2.0** (Nov 16, 2026): `ConfiguracaoSistema.dias_busca_cluster_ia` (Admin), sugestões `tipo_acao` (`criar` \| `anexar`), `POST .../super-os/<uuid>/anexar`, exclusão de status pós-campo na IA
- **v1.9** (Nov 16, 2026): `POST .../super-os/<uuid>/despachar`, FK `OrdemServico.super_os`, scatter-gather com propagação de status
- **v1.8** (Nov 16, 2026): Super OS — modelo `SuperOS`, `GET/POST backoffice/super-os/*`, cluster Haversine + mesmo serviço, propagação de status para protocolos filhos
- **v1.7** (Nov 16, 2026): `GET .../assinaturas/pendentes` (deep fetch da OS), `POST .../assinaturas/<id>/rejeitar`, campos `motivo_rejeicao` e `rejeitada_em` em `SolicitacaoAssinatura`
- **v1.6** (Nov 16, 2026): Status OS `aguardando_assinatura`, modelo e APIs de solicitação/assinatura hierárquica (SHA-256), serviço `criar_notificacao_interna`, alias `POST .../notificacoes/<id>/lida`
- **v1.5** (Nov 13, 2026): CRUD textos padrão por unidade, hash SHA-256 de assinatura + `data_formalizacao`, notificações internas (scatter/gather)
- **v1.4** (Nov 13, 2026): Painel setorial, link mágico, upload público de evidências, formalização com assinatura por senha
- **v1.3** (Nov 13, 2026): Backoffice visão 360º, conclusão multipart de OS, validação e devolução (scatter-gather completo)
- **v1.2** (Nov 13, 2026): API Backoffice — unidades administrativas, listagem Kanban, despacho scatter-gather
- **v1.1** (Nov 12, 2026): Chat assíncrono (202 + polling), avaliações, anonimização LGPD, push simulado em mudança de status do protocolo
- **v1.0** (Nov 11, 2026): Versão inicial com suporte a multipart e comandos `acao_ui`

---

**Desenvolvido pela Equipe M.Ouve** 🤖
