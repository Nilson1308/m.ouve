# 🤖 Integração Chat RAG - M.Ouve

## 📋 Resumo

Integração completa do frontend Vue 3 com o orquestrador LLM (OpenAI) do backend Django.

## 🔌 Endpoints Integrados

### 1. Iniciar Sessão
**POST** `/api/v1/chat/sessao`

**Request:**
```json
{
  "categoria_inicial": "Zeladoria Urbana"
}
```

**Response (201):**
```json
{
  "sessao": {
    "id": "uuid",
    "categoria_inicial": "Zeladoria Urbana",
    "status": "EM_ANDAMENTO",
    "criado_em": "2026-11-11T10:00:00Z"
  },
  "mensagem": {
    "id": "uuid",
    "autor": "ia",
    "conteudo_texto": "Olá! Como posso ajudar você com a Zeladoria Urbana hoje?",
    "tipo_acao": null,
    "criado_em": "2026-11-11T10:00:00Z"
  }
}
```

### 2. Enviar Mensagem
**POST** `/api/v1/chat/interagir`

**Request (JSON):**
```json
{
  "sessao_id": "uuid",
  "texto": "Tem um buraco na rua",
  "localizacao": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco": "Rua Exemplo, 123"
  }
}
```

**Request (Multipart - com fotos):**
```
Content-Type: multipart/form-data

sessao_id: uuid
texto: Aqui está a foto do buraco
localizacao: {"latitude": -23.5505, "longitude": -46.6333}
midia: [arquivo1.jpg, arquivo2.jpg]
```

**Response (200):**
```json
{
  "sessao": { ... },
  "mensagem_cidadao": {
    "id": "uuid",
    "autor": "cidadao",
    "conteudo_texto": "Tem um buraco na rua",
    "localizacao": null,
    "tipo_acao": null,
    "criado_em": "2026-11-11T10:01:00Z"
  },
  "mensagem_resposta": {
    "id": "uuid",
    "autor": "ia",
    "conteudo_texto": "Entendi. Você pode compartilhar a localização?",
    "localizacao": null,
    "tipo_acao": "solicitar_gps",
    "criado_em": "2026-11-11T10:01:05Z"
  },
  "midia_recebida": 0,
  "protocolo": null
}
```

**Response (200 - Fluxo Finalizado):**
```json
{
  "sessao": { "status": "FINALIZADO", ... },
  "mensagem_cidadao": { ... },
  "mensagem_resposta": {
    "autor": "ia",
    "conteudo_texto": "Protocolo registrado com sucesso!",
    "tipo_acao": "fim_conversa"
  },
  "midia_recebida": 2,
  "protocolo": {
    "codigo": "OUVIA-2026-123456",
    "id": "uuid"
  }
}
```

## 📦 Arquitetura Frontend

### Store Pinia (`src/stores/chat.js`)

**Estado:**
- `sessaoAtual`: Objeto da sessão ativa
- `mensagens`: Array de mensagens da conversa
- `loading`: Estado de carregamento inicial
- `error`: Mensagem de erro
- `iaDigitando`: Indicador de digitação da IA

**Actions:**
- `iniciarSessao(categoria)`: Cria nova sessão e recebe boas-vindas
- `enviarMensagem({ texto, localizacao, arquivos })`: Envia mensagem e recebe resposta
- `adicionarMensagemLocal(mensagem)`: Adiciona mensagem local
- `adicionarMensagemErro(texto)`: Adiciona mensagem de erro visual
- `resetar()`: Limpa estado da store

### Service API (`src/services/api.js`)

```javascript
chatService.iniciarSessao(categoriaInicial)
chatService.interagir(sessaoId, { texto, localizacao, arquivos })
```

### View (`src/views/ChatSolicitacaoView.vue`)

**Funcionalidades Implementadas:**
- ✅ Inicialização automática da sessão no `onMounted`
- ✅ Scroll automático para última mensagem
- ✅ Indicador de digitação da IA (`iaDigitando`)
- ✅ Tratamento de erros HTTP (mensagens vermelhas no chat)
- ✅ Envio de texto via input
- ✅ Envio de localização GPS (Geolocation API)
- ✅ Envio de fotos (multipart/form-data)
- ✅ Gravação de áudio (placeholder - implementação futura)
- ✅ Quick Replies (chips/botões para respostas rápidas)
- ✅ Detecção de protocolo gerado
- ✅ Redirecionamento automático após 3s para `/protocolo/:id`

## 🎯 Fluxo de Uso

1. **Usuário clica na categoria** → `NovaSolicitacaoView.vue`
2. **Navegação para chat** → `/chat/:categoriaNome`
3. **Inicialização** → POST `/chat/sessao` → Mensagem de boas-vindas da IA
4. **Conversa**:
   - Cidadão digita → POST `/chat/interagir`
   - IA responde (pode conter `tipo_acao`)
   - Cidadão compartilha GPS → POST `/chat/interagir` com `localizacao`
   - Cidadão envia fotos → POST `/chat/interagir` (multipart)
5. **Finalização**:
   - IA retorna `protocolo` no response
   - Frontend exibe mensagem de sucesso
   - Redireciona para `/protocolo/:id` após 3s

## 🔧 Comandos da IA (tipo_acao)

O campo `tipo_acao` da mensagem da IA permite controlar ações especiais no frontend:

| Valor | Ação Frontend |
|-------|---------------|
| `solicitar_gps` | Destacar botão de localização |
| `solicitar_foto` | Destacar botão de foto |
| `quick_reply:Pequeno,Médio,Grande` | Renderizar chips de resposta rápida |
| `fim_conversa` | Preparar para finalização |

## 🎨 Estados Visuais

### Tipos de Mensagem

1. **IA** (esquerda):
   - Fundo branco/cinza
   - Avatar com ícone sparkles
   - Bolha arredondada à esquerda

2. **Cidadão** (direita):
   - Fundo gradiente primary (azul)
   - Sem avatar
   - Bolha arredondada à direita

3. **Sistema/Erro** (centro):
   - Card vermelho/warning
   - Ícone de alerta
   - Usado para erros HTTP

4. **Localização** (direita):
   - Bubble especial com mini-card
   - Ícone de mapa
   - Coordenadas formatadas

### Indicadores

- **Typing Indicator**: 3 bolinhas animadas quando `iaDigitando = true`
- **Status Header**: "Online" (verde) ou "Conectando..." (amarelo)
- **Gravação Áudio**: Barra vermelha com timer
- **Obtendo GPS**: "Obtendo..." no botão de localização

## 🚨 Tratamento de Erros

### Erros HTTP

Capturados pela store e exibidos como mensagens de sistema (vermelhas) no chat:

```javascript
chatStore.adicionarMensagemErro('Falha ao conectar com o assistente')
```

### Erros de Geolocalização

Tratados localmente:
- Permissão negada
- Timeout
- Navegador não suporta

### Erros de Upload

Validados antes do envio:
- Tamanho máximo de arquivo
- Formatos aceitos

## 🔐 Autenticação

Todos os endpoints requerem:
```
Authorization: Bearer <token>
```

Gerenciado automaticamente pelo interceptor do Axios (`src/services/api.js`).

## 📱 PWA e Offline

- Service Worker precacheia assets estáticos
- Estado da conversa é mantido em memória (não persiste offline)
- Futuro: IndexedDB para rascunhos offline

## 🧪 Testando

```bash
# Dev mode
cd /var/www/ouve
npm run dev

# Acesse http://localhost:5173
# Login → Dashboard → Nova Solicitação → Categoria → Chat
```

## 📈 Próximas Melhorias

- [ ] Persistência de conversas no IndexedDB
- [ ] Gravação real de áudio com MediaRecorder API
- [ ] Preview de fotos antes do envio
- [ ] Geocoding reverso real (integrar com backend)
- [ ] Suporte a streaming de respostas da IA (SSE)
- [ ] Histórico de conversas anteriores
- [ ] Suporte a anexos diversos (PDF, vídeos)
- [ ] Notificações push quando protocolo atualiza

## 🐛 Debug

### Logs Úteis

```javascript
// Store
console.log('Sessão:', chatStore.sessaoAtual)
console.log('Mensagens:', chatStore.mensagens)

// API
console.log('Response:', data)
```

### Verificar Network

Chrome DevTools → Network → Filter: `chat/`

## 📚 Referências

- [OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat)
- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [Pinia Store](https://pinia.vuejs.org/)
- [Geolocation API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)

---

**Versão:** 1.0  
**Data:** Novembro 2026  
**Autor:** Equipe M.Ouve
