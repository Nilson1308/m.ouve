# 📖 Guia de Uso - Form Builder No-Code

## 🚀 INÍCIO RÁPIDO (3 minutos)

### Acesse o Form Builder:

```
1. ✅ Faça login como Super Admin
2. ✅ Menu lateral → Configurações
3. ✅ Click na aba "Catálogo de Serviços"
4. ✅ Click [+ Criar Novo Serviço]
```

**URL Direta:** `/backoffice/configuracoes?aba=servicos`

---

## 🎯 TUTORIAL: Criar "Buraco na Rua"

### **PASSO 1:** Preencher Metadados (30s)

```
Nome do Serviço: Buraco na Rua
Descrição: Reportar buracos e defeitos nas vias públicas
SLA: 72 horas (3 dias)
Unidade: SEMOB (Secretaria de Mobilidade)
Categoria: Zeladoria Urbana
[✓] Serviço Ativo
```

**Dica:** O SLA é calculado automaticamente em dias na listagem (72h = 3d)

---

### **PASSO 2:** Adicionar Campo "Localização" (45s)

```
1. Click [+ Adicionar Campo]
2. Click "Localização (Mapa)" no dropdown
3. Preencha o card que apareceu:
   
   Label: Onde está o buraco?
   Name: onde_esta_o_buraco (← gerado automaticamente ao digitar)
   Placeholder: Toque no mapa para marcar o local
   [✓] Campo Obrigatório ← Ative o toggle
4. Pronto! Campo salvo
```

**Observação:** O `name` é gerado em tempo real enquanto você digita o `Label`.

---

### **PASSO 3:** Adicionar Campo "Foto" (30s)

```
1. Click [+ Adicionar Campo]
2. Click "Foto/Imagem"
3. Preencha:
   
   Label: Foto do buraco
   Name: foto_do_buraco (← auto-gerado)
   Placeholder: Tire uma foto clara do problema
   [ ] Campo Obrigatório ← Deixe desmarcado (opcional)
```

---

### **PASSO 4:** Adicionar Campo "Descrição" (30s)

```
1. Click [+ Adicionar Campo]
2. Click "Texto Longo"
3. Preencha:
   
   Label: Descreva o problema
   Name: descreva_o_problema (← auto-gerado)
   Placeholder: Conte com detalhes o que você observou
   [✓] Campo Obrigatório
```

---

### **PASSO 5:** Adicionar Campo "Tipo de Pavimento" (1min)

```
1. Click [+ Adicionar Campo]
2. Click "Seleção Múltipla"
3. Preencha:
   
   Label: Tipo de pavimento
   Name: tipo_de_pavimento (← auto-gerado)
   
   Opções (uma por linha):
   Asfalto
   Calçada
   Meio-fio
   Paralelepípedo
   Outro
   
   [ ] Campo Obrigatório ← Deixe opcional
```

**Dica:** Pressione Enter para criar uma nova linha no textarea de opções.

---

### **PASSO 6:** Reordenar Campos (15s)

**Ordem Atual:**
1. Onde está o buraco? (Localização)
2. Foto do buraco (Imagem)
3. Descreva o problema (Texto Longo)
4. Tipo de pavimento (Select)

**Queremos:**
1. Onde está o buraco? ← Manter primeiro
2. Tipo de pavimento ← Mover para cima
3. Descreva o problema
4. Foto do buraco ← Mover para baixo

**Ações:**
```
1. No card "Tipo de pavimento" (4º lugar), click [↑] 2 vezes
2. Agora ele está em 2º lugar
3. Pronto! Ordem atualizada
```

---

### **PASSO 7:** Salvar Serviço (5s)

```
1. Verifique se todos os campos estão corretos
2. Click [Criar Serviço] (botão verde no rodapé)
3. Aguarde a mensagem "Serviço criado com sucesso!"
4. Modal fecha automaticamente
5. Novo card aparece na listagem
```

---

## ✏️ EDITAR SERVIÇO EXISTENTE

```
1. Na listagem, localize o card do serviço
2. Click [✏️ Editar] no canto inferior direito
3. Modal abre com todos os dados pré-preenchidos
4. Faça as alterações:
   - Mudar nome, SLA, descrição
   - Adicionar novos campos
   - Editar campos existentes
   - Remover campos (click [🗑️])
   - Reordenar com setas [↑][↓]
5. Click [Atualizar Serviço]
6. Pronto!
```

**Observação:** Campos já existentes aparecem **colapsados** por padrão. Click no card para expandir.

---

## 🗑️ EXCLUIR SERVIÇO

```
1. Na listagem, localize o card do serviço
2. Click [🗑️] no canto inferior direito
3. Modal de confirmação aparece:
   "Tem certeza que deseja excluir o serviço X?"
4. Click [Confirmar Exclusão]
5. Serviço removido da listagem
```

**⚠️ ATENÇÃO:** Não é possível excluir serviços que já possuem protocolos atrelados.

---

## 🔍 FILTROS E BUSCA

### Filtro por Status:

```
1. Dropdown "Status" no topo da listagem
2. Opções:
   - Todos (padrão)
   - Ativo
   - Inativo
3. Listagem atualiza automaticamente
```

### Busca por Nome/Descrição:

```
1. Campo de busca no topo
2. Digite parte do nome ou descrição
3. Resultados filtrados em tempo real
```

**Exemplo:**
- Busca: "buraco" → Mostra "Buraco na Rua"
- Busca: "lâmpada" → Mostra "Lâmpada Queimada"
- Busca: "poda" → Mostra "Poda de Árvore"

---

## 📐 TIPOS DE CAMPO DISPONÍVEIS

### 1. Texto Curto

**Uso:** Nome, CPF, telefone, endereço curto

**Aparência no app:** Input de uma linha

```
┌──────────────────────────────┐
│ Digite seu nome completo     │
└──────────────────────────────┘
```

---

### 2. Texto Longo

**Uso:** Descrições, observações, detalhes

**Aparência no app:** Textarea (múltiplas linhas)

```
┌──────────────────────────────┐
│ Conte com detalhes...        │
│                              │
│                              │
│                              │
└──────────────────────────────┘
```

---

### 3. Número

**Uso:** Quantidade, medidas, valores numéricos

**Aparência no app:** Input numérico

```
┌──────────────────────────────┐
│ 5                            │
└──────────────────────────────┘
      [−]  [+]  (teclado numérico)
```

---

### 4. Foto/Imagem

**Uso:** Upload de fotos

**Aparência no app:** Botão de câmera + preview

```
┌────────────────────┐
│   📷               │
│  Tirar Foto        │
└────────────────────┘
   ou
[📂 Escolher da Galeria]
```

---

### 5. Localização (Mapa)

**Uso:** Coordenadas GPS, marcação no mapa

**Aparência no app:** Mapa interativo

```
┌────────────────────────────┐
│      🗺️  Mapa Leaflet      │
│                            │
│      📍 ← Pin do usuário   │
│                            │
└────────────────────────────┘
  [📍 Usar Localização Atual]
```

---

### 6. Seleção Múltipla

**Uso:** Dropdown com opções pré-definidas

**Aparência no app:** Select nativo

```
┌──────────────────────────────┐
│ Selecione uma opção      [▼] │
└──────────────────────────────┘
  ↓ Click
┌──────────────────────────────┐
│ Asfalto                      │
│ Calçada                      │
│ Meio-fio                     │
│ Paralelepípedo               │
│ Outro                        │
└──────────────────────────────┘
```

---

## ⚙️ REGRAS DE VALIDAÇÃO

### Nome do Serviço:
- ✅ Obrigatório
- ✅ Mínimo 3 caracteres
- ✅ Máximo 200 caracteres

### SLA:
- ✅ Obrigatório
- ✅ Mínimo 1 hora
- ✅ Máximo 999 horas

### Unidade Responsável:
- ✅ Obrigatória
- ✅ Deve existir e estar ativa

### Campos do Formulário:
- ✅ Pelo menos 1 campo obrigatório
- ✅ Label não pode ser vazio
- ✅ Name é gerado automaticamente (não editável)
- ✅ Para type='select': pelo menos 2 opções

---

## 🧪 EXEMPLOS DE SERVIÇOS

### Exemplo 1: Lâmpada Queimada

```yaml
Nome: Lâmpada Queimada
Descrição: Reportar lâmpadas de postes queimadas ou piscando
SLA: 48 horas
Unidade: SEMOB
Categoria: Zeladoria Urbana
Ativo: Sim

Campos:
  1. Localização do Poste (Mapa) - Obrigatório
  2. Número do Poste (Texto Curto) - Opcional
  3. Foto da Lâmpada (Imagem) - Obrigatório
  4. Observações (Texto Longo) - Opcional
```

---

### Exemplo 2: Poda de Árvore

```yaml
Nome: Poda de Árvore
Descrição: Solicitar poda de árvores que estejam atrapalhando
SLA: 120 horas (5 dias)
Unidade: SEMA (Secretaria de Meio Ambiente)
Categoria: Meio Ambiente
Ativo: Sim

Campos:
  1. Local da Árvore (Mapa) - Obrigatório
  2. Foto da Árvore (Imagem) - Obrigatório
  3. Tipo de Árvore (Seleção)
     - Ipê
     - Palmeira
     - Mangueira
     - Não sei
  4. Motivo da Poda (Texto Longo) - Obrigatório
  5. Altura Aproximada (Número) - Opcional
```

---

### Exemplo 3: Castração (Proteção Animal) — elegibilidade IA

Serviço real no ambiente: **Agendamento de Castração de Animais**.

**Regras (sem código novo por regra):**

- Passo **idade** — interpretação: bloquear &lt; 12 meses ou &gt; 9 anos.
- Passo **doenças** — interpretação: bloquear se doente / “Sim”.
- **Protocolo completo** — condição que cruza idade + saúde após vários passos.

Documentação API: seção *Catálogo — metadados IA, conversa e elegibilidade* em `API_CONTRACT.md`.  
JSON de referência: `docs/exemplos/protecao-animal-castracao.json`.  
Aplicar no banco: `cd backend && .venv/bin/python manage.py aplicar_exemplo_protecao_animal`.

---

### Exemplo 4: Animal Abandonado

```yaml
Nome: Animal Abandonado
Descrição: Reportar animais abandonados nas ruas
SLA: 24 horas
Unidade: Defesa Civil
Categoria: Proteção Animal
Ativo: Sim

Campos:
  1. Localização (Mapa) - Obrigatório
  2. Tipo de Animal (Seleção)
     - Cão
     - Gato
     - Outro
  3. Foto do Animal (Imagem) - Obrigatório
  4. Quantidade de Animais (Número) - Obrigatório
  5. Condição do Animal (Texto Longo)
  6. Animal Ferido? (Seleção)
     - Sim
     - Não
     - Não sei
```

---

## 💡 DICAS E BOAS PRÁTICAS

### ✅ Labels Claros:

**Ruim:** "Local"  
**Bom:** "Onde está o problema?"

**Ruim:** "Descrição"  
**Bom:** "Descreva com detalhes o que você observou"

---

### ✅ Placeholders Informativos:

**Ruim:** "Digite aqui"  
**Bom:** "Ex: Buraco grande no meio da rua"

**Ruim:** "Localização"  
**Bom:** "Toque no mapa para marcar o local exato"

---

### ✅ Ordem Lógica dos Campos:

```
Ordem Recomendada:
1. Localização (sempre primeiro - contexto espacial)
2. Foto (evidência visual)
3. Descrição (detalhes textuais)
4. Campos específicos (tipo, quantidade, etc)
```

---

### ✅ Use "Obrigatório" com Moderação:

**Campos Obrigatórios:**
- Localização (99% dos casos)
- Foto (se for evidência crítica)
- Descrição mínima

**Campos Opcionais:**
- Detalhes complementares
- Informações difíceis de obter
- Campos técnicos (ex: "Número do Poste")

---

### ✅ Opções de Select Abrangentes:

**Sempre inclua uma opção "Outro":**

```
Tipo de Pavimento:
- Asfalto
- Calçada
- Meio-fio
- Paralelepípedo
- Outro ← Não se esqueça!
```

---

### ✅ SLA Realista:

**Zeladoria Urbana:** 48-72h (2-3 dias)  
**Emergências:** 24h (1 dia)  
**Obras Complexas:** 120-168h (5-7 dias)  
**Serviços Burocráticos:** 240h+ (10+ dias)

---

## 🐛 RESOLUÇÃO DE PROBLEMAS

### ❌ Botão [Salvar] desabilitado

**Causa:** Formulário inválido

**Soluções:**
1. ✅ Verifique se o nome do serviço foi preenchido
2. ✅ Verifique se a unidade foi selecionada
3. ✅ Verifique se há pelo menos 1 campo no formulário
4. ✅ Verifique se todos os campos têm label preenchido
5. ✅ Para campos Select, verifique se há pelo menos 2 opções

---

### ❌ "Name" não está sendo gerado

**Causa:** Label vazio

**Solução:**
1. ✅ Digite o Label do campo
2. ✅ O Name será gerado automaticamente ao digitar

---

### ❌ Não consigo excluir um serviço

**Causa:** Serviço possui protocolos atrelados

**Solução:**
1. ⚠️ Não é possível excluir serviços com protocolos existentes
2. ✅ Alternativa: desative o serviço (toggle "Serviço Ativo")
3. ✅ Serviços inativos não aparecem para os cidadãos

---

### ❌ Unidades não aparecem no dropdown

**Causa:** Nenhuma unidade está ativa

**Solução:**
1. ✅ Vá para a aba "Unidades Administrativas"
2. ✅ Ative pelo menos uma unidade
3. ✅ Volte para "Catálogo de Serviços"
4. ✅ Recarregue a página se necessário

---

### ❌ Campos aparecem em ordem errada após salvar

**Causa:** Bug no backend (improvável)

**Solução:**
1. ✅ Edite o serviço novamente
2. ✅ Use as setas [↑][↓] para reordenar
3. ✅ Salve novamente
4. ✅ A ordem será preservada

---

## 🔒 PERMISSÕES

### Super Admin:
- ✅ Acessa todas as abas de Configurações
- ✅ Cria, edita, exclui qualquer serviço
- ✅ Gerencia unidades, usuários, perfis

### Admin de Unidade:
- ⚠️ Não tem acesso à aba "Catálogo de Serviços"
- ⚠️ Pode solicitar à TI para criar serviços específicos

### Atendente:
- ❌ Não tem acesso ao Backoffice
- ✅ Visualiza serviços apenas no app de atendimento

---

## 📱 COMO OS CIDADÃOS VERÃO O FORMULÁRIO

Quando um cidadão abrir o app e selecionar "Buraco na Rua", verá:

```
┌─────────────────────────────────────────┐
│ 🏛️  Buraco na Rua                       │
│                                         │
│ Reportar buracos e defeitos nas vias    │
│ públicas                                │
├─────────────────────────────────────────┤
│                                         │
│ Onde está o buraco? *                   │
│ ┌─────────────────────────────────────┐ │
│ │        🗺️  Mapa Interativo         │ │
│ │                                     │ │
│ │         📍 Marcador                 │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Tipo de pavimento                       │
│ ┌─────────────────────────────────┐   │
│ │ Selecione                    [▼]│   │
│ └─────────────────────────────────┘   │
│                                         │
│ Descreva o problema *                   │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Foto do buraco                          │
│ ┌────────────┐                         │
│ │ 📷 Tirar   │                         │
│ │   Foto     │                         │
│ └────────────┘                         │
│                                         │
│ [           Enviar Solicitação        ]│
└─────────────────────────────────────────┘
```

---

## ✅ CHECKLIST ANTES DE SALVAR

Antes de clicar em [Criar Serviço], verifique:

- [ ] Nome do serviço está claro e objetivo
- [ ] Descrição explica o propósito do serviço
- [ ] SLA é realista e alinhado com a capacidade da unidade
- [ ] Unidade correta foi selecionada
- [ ] Categoria está correta
- [ ] Pelo menos 1 campo foi adicionado
- [ ] Todos os campos têm labels claros
- [ ] Campos essenciais estão marcados como obrigatórios
- [ ] Campos Select têm pelo menos 2 opções (incluindo "Outro")
- [ ] Ordem dos campos é lógica (Localização → Foto → Descrição → Outros)
- [ ] Serviço está marcado como "Ativo"

---

## 🎊 PRONTO PARA USAR!

Você agora sabe como:

✅ Criar serviços do zero  
✅ Adicionar campos de 6 tipos diferentes  
✅ Reordenar campos visualmente  
✅ Editar serviços existentes  
✅ Excluir serviços  
✅ Filtrar e buscar na listagem  
✅ Definir campos obrigatórios  
✅ Criar opções para Select  

**Acesse agora:** `/backoffice/configuracoes?aba=servicos`

---

*Guia criado em 17/11/2024*  
*Form Builder No-Code - Ouv.IA* 🎨

**Dúvidas?** Contate o suporte técnico ou consulte:
- FORM_BUILDER_NO_CODE.md (documentação completa)
- ARQUITETURA_FORM_BUILDER.md (detalhes técnicos)
