# 🚀 GUIA RÁPIDO - Detalhes do Protocolo Interno

## ⚡ Acesso Rápido

```
/backoffice/protocolo/:id
```

**Exemplo:**
```
http://localhost:3002/backoffice/protocolo/PROT-2024-042
```

---

## 📐 Estrutura da Tela

```
┌─────────────────────────────────────────┐
│ [←] PROT-2024-042 [Status] [SLA]       │ ← Header
├──────────────────────┬──────────────────┤
│ ESQUERDA: CONTEXTO   │ DIREITA: AÇÃO    │
│                      │                  │
│ 📊 Dados IA          │ ✅ Validação     │
│ 📍 Localização       │ 📋 Ordens        │
│ 💬 Chat              │ 📊 Resumo        │
└──────────────────────┴──────────────────┘
```

---

## 🎯 O Que Fazer?

### 1️⃣ **Analisar o Contexto** (Coluna Esquerda)

**A. Dados Coletados:**
- Revise a tabela de informações extraídas pela IA
- Verifique se os dados fazem sentido

**B. Localização:**
- Confira endereço completo
- Veja o pino no mapa

**C. Histórico do Chat:**
- Clique no accordion para expandir
- Leia a conversa completa
- Veja as fotos enviadas pelo cidadão

---

### 2️⃣ **Verificar a Execução** (Coluna Direita)

**A. Ordens de Serviço:**
- Veja quantas unidades foram envolvidas
- Verifique o status de cada uma
- Analise as fotos de execução (clique para ampliar)
- Leia as observações das equipes

**B. Resumo Executivo:**
- Confirme que todas as ordens estão concluídas
- Veja o tempo total de resolução

---

### 3️⃣ **Tomar Ação** (Card de Validação)

#### OPÇÃO A: Validar e Encerrar ✅

1. Selecione uma **resposta padrão** no select
2. Adicione **observações** (opcional)
3. Veja o **preview** da mensagem
4. Clique em **"Validar e Encerrar Protocolo"**

**Resultado:**
- Cidadão recebe a resposta
- Protocolo muda para "Concluído"
- Caso encerrado

---

#### OPÇÃO B: Devolver à Secretaria ❌

1. Clique em **"Devolver à Secretaria"**
2. Modal abre
3. Selecione o **motivo** (ex: "Foto inadequada")
4. Escreva uma **justificativa detalhada**
5. Clique em **"Confirmar Devolução"**

**Resultado:**
- Ordem volta para a secretaria
- Secretaria recebe notificação
- Precisa refazer o serviço

---

## 🎨 Respostas Padrão Disponíveis

1. **Serviço executado conforme padrão**
   - Use quando tudo está OK

2. **Reparo realizado com sucesso**
   - Use para reparos simples

3. **Intervenção concluída - Material aplicado**
   - Use quando houve aplicação de material

4. **Vistoria realizada - Situação regularizada**
   - Use quando foi vistoria técnica

---

## 🖼️ Fotos de Execução

### Como Ver:

```
┌─────┐ ┌─────┐ ┌─────┐
│ 📷  │ │ 📷  │ │ 📷  │
│Antes│ │Duran│ │Depoi│
└─────┘ └─────┘ └─────┘
  ↑       ↑       ↑
Clique para ampliar
```

**Ao clicar:**
- Abre em nova aba
- Zoom completo
- Analise os detalhes

---

## ⚠️ Motivos para Devolver

- **Foto inadequada ou incompleta**
  - Foto borrada, escura, de longe
  
- **Serviço executado de forma incompleta**
  - Faltou parte do trabalho
  
- **Execução fora do padrão técnico**
  - Qualidade insatisfatória
  
- **Intervenção no local incorreto**
  - Endereço errado
  
- **Outro motivo**
  - Descreva na justificativa

---

## 🔍 Onde Encontrar Cada Informação?

| O que procurar | Onde está |
|----------------|-----------|
| Dados do cidadão | Header (badges) |
| O que foi relatado | Coluna Esquerda > Dados IA |
| Endereço completo | Coluna Esquerda > Localização |
| Conversa original | Coluna Esquerda > Chat |
| Quem atendeu | Coluna Direita > Ordens |
| Fotos do serviço | Coluna Direita > Ordens |
| Status atual | Header + Coluna Direita |

---

## ⌨️ Atalhos e Dicas

### Navegação:
- **Voltar:** Clique na seta ← no header
- **Chat:** Clique no header do accordion
- **Fotos:** Clique direto na miniatura

### Produtividade:
- Use respostas padrão (mais rápido)
- Leia as observações das equipes
- Veja TODAS as fotos antes de validar

### Qualidade:
- Sempre confira as fotos
- Leia a conversa original
- Compare: O que foi pedido vs O que foi feito

---

## 📊 Entendendo o Status

### No Header:

**Badge de Status:**
- 🔵 Triagem IA
- 🟣 Em Validação
- 🟡 Aguardando Retorno
- 🟢 Concluído

**Badge de SLA:**
- 🟢 No prazo (> 24h)
- 🟡 Vence hoje (≤ 24h)
- 🔴 Atrasado (vencido)

---

## 🎯 Checklist de Validação

Antes de clicar em "Validar e Encerrar":

- [ ] Li todos os dados coletados
- [ ] Verifiquei o endereço no mapa
- [ ] Li o histórico do chat completo
- [ ] Vi a foto enviada pelo cidadão
- [ ] Conferi TODAS as ordens de serviço
- [ ] Analisei as fotos de execução
- [ ] Li as observações das equipes
- [ ] Selecionei a resposta adequada
- [ ] Adicionei observações (se necessário)

---

## 🔄 Fluxo Completo

```
1. Mesa de Trabalho
   ↓
2. Clica "Ver Detalhes"
   ↓
3. [Analisa Contexto]
   ↓
4. [Verifica Execução]
   ↓
5. [Toma Decisão]
   ├─→ Validar: Protocolo concluído ✅
   └─→ Devolver: Volta para secretaria ↩️
```

---

## 💡 Dicas Profissionais

### ✅ Boas Práticas:

1. **Sempre compare as fotos**
   - Antes vs Depois
   - O problema foi resolvido?

2. **Leia as observações**
   - Equipe explicou o que fez?
   - Materiais utilizados fazem sentido?

3. **Use respostas padrão**
   - Padroniza comunicação
   - Economiza tempo
   - Mantém profissionalismo

4. **Justifique devoluções**
   - Seja específico
   - Explique o que está errado
   - Diga o que precisa ser corrigido

### ❌ Evite:

- Validar sem ver as fotos
- Ignorar o histórico do chat
- Devolver sem justificativa clara
- Aprovar serviço incompleto

---

## 🆘 Resolução de Problemas

### Foto não abre?
- Clique novamente
- Tente com botão direito > "Abrir em nova aba"

### Chat muito longo?
- Use o scroll dentro do accordion
- Foque nas mensagens principais

### Dúvida sobre o serviço?
- Leia as observações da equipe
- Veja as fotos de execução
- Confira os materiais utilizados

### Não sei qual resposta escolher?
- Leia todas as opções
- Veja qual se encaixa melhor
- Adicione observações extras se necessário

---

## 📞 Suporte

**Dúvidas sobre a interface?**
- Consulte: `DETALHES_PROTOCOLO_INTERNO.md`

**Dúvidas sobre procedimentos?**
- Consulte manual operacional da Ouvidoria

---

**🎯 Objetivo: Validar com qualidade, agilidade e profissionalismo!**
