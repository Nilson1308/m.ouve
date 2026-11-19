# 🧪 Testes de Integração - Chat RAG

## ✅ Checklist de Testes Funcionais

### 1. Inicialização da Sessão

**Passo a Passo:**
1. Faça login no sistema
2. Acesse Dashboard
3. Clique em "Nova Solicitação"
4. Clique no card "Zeladoria Urbana"

**Resultado Esperado:**
- ✅ Navegação para `/chat/Zeladoria Urbana`
- ✅ Header exibe "Zeladoria Urbana"
- ✅ Status "Assistente M.Ouve online" (bolinha verde)
- ✅ Mensagem de boas-vindas da IA aparece automaticamente
- ✅ Input de mensagem está habilitado

**Verificações Técnicas:**
```javascript
// DevTools Console
console.log(chatStore.sessaoAtual) // Deve ter 'id' e 'categoria_inicial'
console.log(chatStore.mensagens.length) // Deve ser >= 1
```

---

### 2. Envio de Mensagem de Texto

**Passo a Passo:**
1. Digite no input: "Tem um buraco na rua Exemplo"
2. Pressione Enter ou clique no botão de enviar

**Resultado Esperado:**
- ✅ Mensagem do cidadão aparece à direita (fundo azul)
- ✅ Indicador "digitando..." aparece (3 bolinhas)
- ✅ Resposta da IA aparece à esquerda (fundo branco)
- ✅ Scroll desce automaticamente
- ✅ Input limpa após envio

**Verificações Técnicas:**
```javascript
// Network tab → Filter: chat/interagir
// Status: 200
// Response deve ter: mensagem_cidadao, mensagem_resposta
```

---

### 3. Compartilhar Localização GPS

**Passo a Passo:**
1. Clique no botão de clipe (📎)
2. Clique em "Localização"
3. Permita acesso à localização no navegador

**Resultado Esperado:**
- ✅ Botão mostra "Obtendo..." enquanto busca
- ✅ Mensagem especial de localização aparece à direita
- ✅ Card com coordenadas (lat/lng) visível
- ✅ IA responde confirmando recebimento
- ✅ Menu de anexos fecha automaticamente

**Teste Alternativo (Permissão Negada):**
- ✅ Mensagem de erro vermelha aparece no chat
- ✅ Texto: "Não foi possível obter sua localização..."

**Verificações Técnicas:**
```javascript
// Request deve incluir:
{
  "sessao_id": "...",
  "texto": "📍 Localização compartilhada",
  "localizacao": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco": "Localização GPS"
  }
}
```

---

### 4. Envio de Fotos

**Passo a Passo:**
1. Clique no botão de clipe (📎)
2. Clique em "Foto"
3. Selecione 1 ou mais imagens

**Resultado Esperado:**
- ✅ Seletor de arquivos abre
- ✅ Após seleção, mensagem "📷 X foto(s) enviada(s)" aparece
- ✅ Upload é enviado via multipart/form-data
- ✅ IA responde confirmando recebimento

**Verificações Técnicas:**
```javascript
// Network tab → Request Headers
// Content-Type: multipart/form-data; boundary=...

// Response
{
  "midia_recebida": 2  // Número de arquivos recebidos
}
```

---

### 5. Quick Replies (Slot Filling)

**Teste Manual (Simulado):**
*Nota: Requer backend configurado para retornar `tipo_acao` específico*

**Cenário:**
IA pergunta: "Qual o tamanho do buraco?"
Backend retorna `tipo_acao: "quick_reply:Pequeno,Médio,Grande"`

**Resultado Esperado:**
- ✅ Chips aparecem acima do input
- ✅ Ao clicar em "Grande", mensagem é enviada automaticamente
- ✅ Chips desaparecem após seleção

---

### 6. Finalização com Protocolo

**Passo a Passo:**
1. Complete o fluxo conversacional
2. Backend retorna protocolo na última resposta

**Resultado Esperado:**
- ✅ Mensagem de sucesso aparece: "✅ Protocolo gerado com sucesso!"
- ✅ Código do protocolo é exibido (ex: OUVIA-2026-123456)
- ✅ Texto "Redirecionando..." aparece
- ✅ Após 3 segundos, navegação para `/protocolo/:id`
- ✅ Detalhes do protocolo são exibidos

**Verificações Técnicas:**
```javascript
// Response final
{
  "protocolo": {
    "codigo": "OUVIA-2026-123456",
    "id": "uuid-aqui"
  }
}

// Após 3s
window.location.pathname === "/protocolo/uuid-aqui"
```

---

### 7. Tratamento de Erros

#### 7.1 Erro de Conexão

**Teste:**
1. Desligue o backend Django
2. Tente enviar mensagem

**Resultado Esperado:**
- ✅ Mensagem de erro vermelha no chat
- ✅ Texto: "Falha ao enviar mensagem"
- ✅ Input permanece habilitado para retry

#### 7.2 Token Expirado

**Teste:**
1. Altere localStorage: `localStorage.setItem('sinapse_token', 'token-invalido')`
2. Envie mensagem

**Resultado Esperado:**
- ✅ 401 Unauthorized
- ✅ Interceptor tenta refresh token
- ✅ Se refresh falha → Redireciona para `/login`

#### 7.3 Sessão Inválida

**Teste:**
Manipule manualmente `chatStore.sessaoAtual.id` para UUID inexistente

**Resultado Esperado:**
- ✅ 400 Bad Request
- ✅ Mensagem de erro: "Sessão não encontrada"

---

### 8. UX e Acessibilidade

#### 8.1 Dark Mode

**Teste:**
1. No header, clique no ícone de tema
2. Alterne entre Claro / Escuro / Alto Contraste

**Resultado Esperado:**
- ✅ Balões de mensagem adaptam cores
- ✅ Bordas e sombras ajustam
- ✅ Ícones mantêm contraste
- ✅ Alto Contraste: bordas amarelas visíveis

#### 8.2 Scroll Automático

**Teste:**
1. Envie 20+ mensagens para preencher tela
2. Verifique scroll após cada nova mensagem

**Resultado Esperado:**
- ✅ Scroll desce automaticamente
- ✅ Última mensagem sempre visível

#### 8.3 Textarea Expansível

**Teste:**
1. Digite mensagem longa (5+ linhas)

**Resultado Esperado:**
- ✅ Textarea expande até máximo (max-h-32)
- ✅ Após enviar, volta para 1 linha

#### 8.4 Botão Voltar

**Teste:**
1. Durante conversa, clique em voltar (<)

**Resultado Esperado:**
- ✅ Alerta de confirmação: "Deseja sair da conversa?"
- ✅ Se confirmar → Volta para `/nova-solicitacao`
- ✅ Store é resetada

---

### 9. PWA e Responsividade

#### 9.1 Mobile

**Teste em Chrome DevTools (iPhone 14):**
- ✅ Header compacto
- ✅ Safe area insets aplicadas
- ✅ Teclado não sobrepõe input
- ✅ Scroll suave

#### 9.2 Tablet

**Teste em Chrome DevTools (iPad):**
- ✅ Balões ocupam no máx 85% da largura
- ✅ Botões grandes o suficiente para toque

---

## 🔍 Testes de Integração Backend

### Teste 1: Sessão é Criada Corretamente

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/sessao \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"categoria_inicial": "Zeladoria Urbana"}'
```

**Response Esperado (201):**
```json
{
  "sessao": {
    "id": "uuid",
    "status": "EM_ANDAMENTO"
  },
  "mensagem": {
    "autor": "ia",
    "conteudo_texto": "Olá! Como posso ajudar..."
  }
}
```

---

### Teste 2: Envio de Mensagem Simples

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/interagir \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sessao_id": "uuid-da-sessao",
    "texto": "Tem um buraco na rua"
  }'
```

**Response Esperado (200):**
```json
{
  "mensagem_cidadao": { "conteudo_texto": "Tem um buraco na rua" },
  "mensagem_resposta": { "conteudo_texto": "..." },
  "protocolo": null
}
```

---

### Teste 3: Envio com Localização

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/interagir \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sessao_id": "uuid",
    "texto": "Aqui está a localização",
    "localizacao": {
      "latitude": -23.5505,
      "longitude": -46.6333,
      "endereco": "Praça da Sé, São Paulo"
    }
  }'
```

---

### Teste 4: Upload de Foto

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/interagir \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "sessao_id=uuid" \
  -F "texto=Foto do buraco" \
  -F "midia=@foto1.jpg" \
  -F "midia=@foto2.jpg"
```

**Response Esperado:**
```json
{
  "midia_recebida": 2
}
```

---

## 📊 Métricas de Performance

### Frontend

- ✅ Tempo de inicialização: < 500ms
- ✅ Tempo de resposta da IA: < 3s (depende do LLM)
- ✅ Build size: ~580 KB (gzip)
- ✅ Lighthouse Score: > 90

### Backend

- ✅ POST /sessao: < 200ms
- ✅ POST /interagir (sem LLM): < 100ms
- ✅ POST /interagir (com LLM): < 5s

---

## 🐛 Bugs Conhecidos e Workarounds

### Bug 1: Gravação de Áudio Não Implementada

**Status:** Placeholder implementado  
**Workaround:** Botão de microfone simula áudio como texto

### Bug 2: Geocoding Reverso Mock

**Status:** Hardcoded "Localização GPS"  
**TODO:** Integrar com backend `/atendimentos/geocode/reverse`

---

## 📝 Logs para Debug

### Console do Navegador

```javascript
// Verificar estado da store
chatStore.sessaoAtual
chatStore.mensagens
chatStore.iaDigitando

// Verificar localStorage
localStorage.getItem('sinapse_token')

// Forçar erro
chatStore.enviarMensagem({ texto: 'test' }).then(console.log)
```

### Network Tab

**Filtros úteis:**
- `chat/`
- `status-code:400`
- `status-code:401`

---

## ✅ Checklist Final de QA

- [ ] Inicialização de sessão funciona
- [ ] Envio de mensagens de texto
- [ ] Compartilhamento de localização GPS
- [ ] Upload de fotos (multipart)
- [ ] Indicador de digitação aparece
- [ ] Scroll automático funciona
- [ ] Tratamento de erros HTTP
- [ ] Finalização com protocolo
- [ ] Redirecionamento após protocolo
- [ ] Dark mode e alto contraste
- [ ] Responsividade mobile/tablet
- [ ] Botão voltar com confirmação
- [ ] Token refresh automático
- [ ] PWA install funciona

---

**Data:** Novembro 2026  
**Versão:** 1.0
