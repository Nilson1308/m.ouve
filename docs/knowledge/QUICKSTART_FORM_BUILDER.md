# ⚡ QUICK START - Form Builder No-Code

## 🚀 TESTE EM 3 MINUTOS

### ✅ Pré-requisitos:

```bash
# 1. Build já está funcionando ✅
cd /var/www/ouve
npm run build  # ✅ Passou em 7.07s

# 2. Servidor rodando
npm run dev

# 3. Login como Super Admin
```

---

## 📍 ACESSO DIRETO

### Opção 1: Via Menu
```
1. Login → Super Admin
2. Menu Lateral → Configurações (⚙️)
3. Aba → "Catálogo de Serviços"
```

### Opção 2: URL Direta
```
http://localhost:5173/backoffice/configuracoes?aba=servicos
```

---

## ⚡ TESTE RÁPIDO #1: Ver a Listagem (30s)

**O que você verá:**

```
┌─────────────────────────────────────────────────────┐
│ Catálogo de Serviços         [+ Criar Novo Serviço] │
│                                                      │
│ [Status: Todos ▼] [Busca: ___________]              │
├─────────────────────────────────────────────────────┤
│ (Cards de serviços se houver algum cadastrado)      │
│                                                      │
│ OU                                                   │
│                                                      │
│   📋 Nenhum serviço cadastrado                      │
│   Comece criando seu primeiro serviço!              │
└─────────────────────────────────────────────────────┘
```

**✅ Sucesso:** A tela carregou sem erros

---

## ⚡ TESTE RÁPIDO #2: Abrir o Form Builder (10s)

**Ação:**
```
1. Click no botão [+ Criar Novo Serviço]
```

**O que você verá:**

```
┌──────────────────────────────────────────────────────┐
│ ✨ Criar Novo Serviço                           [✕]  │
│    Configure o serviço e monte o formulário dinâmico │
├──────────────────────────────────────────────────────┤
│                                                       │
│ ⚙️  Informações Básicas                               │
│                                                       │
│ Nome do Serviço: [___________________________]       │
│ Descrição: [___________________________]             │
│ ...                                                   │
│                                                       │
│ 📐 Construtor de Formulário  [+ Adicionar Campo]     │
│                                                       │
│ (Área vazia para adicionar campos)                   │
└──────────────────────────────────────────────────────┘
```

**✅ Sucesso:** Modal abriu sem erros

---

## ⚡ TESTE RÁPIDO #3: Auto-geração de `name` (30s)

**Ação:**
```
1. No campo "Label", digite: Onde está o buraco?
2. Observe o campo "Name" abaixo
```

**Resultado esperado:**
```
Label: Onde está o buraco?
Name:  onde_esta_o_buraco  ← Gerado automaticamente!
```

**✅ Sucesso:** O `name` foi gerado em snake_case

---

## ⚡ TESTE RÁPIDO #4: Adicionar Campo (45s)

**Ação:**
```
1. Preencha os metadados básicos:
   Nome: Teste Rápido
   SLA: 24
   Unidade: (Selecione qualquer uma)

2. Click [+ Adicionar Campo]
3. Click "Localização (Mapa)"
```

**O que você verá:**

```
┌─────────────────────────────────────────────────┐
│ 📍 Campo sem título     [Obrig] [↑][↓][▼][🗑️]   │
│    Localização • name:                      [▼] │
│ ─────────────────────────────────────────────   │
│ Rótulo: [_________________]                     │
│ Name: [_________________] (auto-gerado)         │
│ Placeholder: [_________________]                │
│ [ ] Campo Obrigatório                           │
└─────────────────────────────────────────────────┘
```

**Agora preencha:**
```
Rótulo: Local do problema
Name: local_do_problema (← auto-gerado ao digitar)
[✓] Campo Obrigatório (← Ative o toggle)
```

**✅ Sucesso:** Campo foi adicionado ao canvas

---

## ⚡ TESTE RÁPIDO #5: Adicionar 2º Campo (30s)

**Ação:**
```
1. Click [+ Adicionar Campo]
2. Click "Foto/Imagem"
3. Preencha:
   Rótulo: Foto do problema
   Name: foto_do_problema (← auto-gerado)
```

**O que você verá:**

```
┌─────────────────────────────────────────────────┐
│ 📍 Local do problema    [Obrig] [↑][↓][▼][🗑️]   │
│    Localização • name: local_do_problema        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 📷 Foto do problema     [↑][↓][▼][🗑️]           │
│    Foto/Imagem • name: foto_do_problema         │
└─────────────────────────────────────────────────┘
```

**✅ Sucesso:** 2 campos no canvas

---

## ⚡ TESTE RÁPIDO #6: Reordenar (15s)

**Ação:**
```
1. No card "Foto do problema" (2º lugar)
2. Click na seta [↑]
```

**Resultado esperado:**

```
ANTES:
1. Local do problema
2. Foto do problema  ← Aqui

DEPOIS:
1. Foto do problema  ← Moveu para cima!
2. Local do problema
```

**✅ Sucesso:** Ordem foi invertida

---

## ⚡ TESTE RÁPIDO #7: Validação (15s)

**Ação:**
```
1. Sem preencher nome do serviço, tente clicar [Criar Serviço]
```

**Resultado esperado:**
```
Botão [Criar Serviço] está DESABILITADO (opacity-50, não clicável)
```

**Agora preencha:**
```
Nome do Serviço: Teste Rápido
```

**Resultado esperado:**
```
Botão [Criar Serviço] agora está HABILITADO (verde, clicável)
```

**✅ Sucesso:** Validação está funcionando

---

## ⚡ TESTE RÁPIDO #8: Salvar (POST) (30s)

**Ação:**
```
1. Preencha os campos obrigatórios:
   Nome: Teste Completo
   SLA: 48
   Unidade: (Selecione)
   Campos: 2 campos já adicionados

2. Click [Criar Serviço]
```

**Resultado esperado:**

```
1. Botão muda para "Salvando..." (loading)
2. Modal fecha após 1-2 segundos
3. Toast aparece: "Serviço criado com sucesso!" ✅
4. Novo card aparece na listagem
```

**✅ Sucesso:** POST funcionou!

---

## ⚡ TESTE RÁPIDO #9: Editar (30s)

**Ação:**
```
1. No card do serviço recém-criado, click [✏️ Editar]
```

**Resultado esperado:**

```
Modal abre com:
✅ Nome pré-preenchido: "Teste Completo"
✅ SLA pré-preenchido: 48
✅ Campos pré-carregados (2 cards colapsados)
```

**Faça uma mudança:**
```
1. Mude o nome para: Teste Editado
2. Click [Atualizar Serviço]
```

**Resultado esperado:**
```
1. Modal fecha
2. Toast: "Serviço atualizado com sucesso!" ✅
3. Card na listagem mostra "Teste Editado"
```

**✅ Sucesso:** PUT funcionou!

---

## ⚡ TESTE RÁPIDO #10: Excluir (20s)

**Ação:**
```
1. No card do serviço, click [🗑️]
2. Modal de confirmação aparece
3. Click [Confirmar Exclusão]
```

**Resultado esperado:**

```
1. Modal fecha
2. Toast: "Serviço excluído com sucesso!" ✅
3. Card desaparece da listagem
```

**✅ Sucesso:** DELETE funcionou!

---

## ✅ CHECKLIST DE TESTES

Marque conforme testa:

- [ ] Acessei `/backoffice/configuracoes?aba=servicos`
- [ ] Listagem carregou sem erros
- [ ] Abri o modal [+ Criar Novo Serviço]
- [ ] Auto-geração de `name` funciona ao digitar label
- [ ] Consegui adicionar campo "Localização"
- [ ] Consegui adicionar campo "Foto"
- [ ] Reordenação com setas ↑ ↓ funciona
- [ ] Validação impede salvar com dados incompletos
- [ ] POST criou serviço com sucesso
- [ ] Edição abre modal pré-preenchido
- [ ] PUT atualizou serviço com sucesso
- [ ] DELETE excluiu serviço com sucesso

**Se todos os 12 itens funcionaram: 🎉 FEATURE 100% FUNCIONAL**

---

## 🧪 TESTES AVANÇADOS (OPCIONAL)

### Teste 1: Select com Opções

```
1. Crie novo serviço
2. Adicione campo tipo "Seleção Múltipla"
3. No textarea "Opções", digite (uma por linha):
   Opção 1
   Opção 2
   Opção 3
4. Salve
5. Edite e verifique se as opções foram salvas
```

**✅ Sucesso:** Opções foram salvas e carregadas corretamente

---

### Teste 2: Campo Obrigatório

```
1. Adicione 2 campos:
   - Campo A: [✓] Obrigatório
   - Campo B: [ ] Opcional
2. Salve
3. Verifique no JSON (console ou API):
   Campo A: required: true
   Campo B: required: false
```

**✅ Sucesso:** Flag `required` foi salva corretamente

---

### Teste 3: Expandir/Colapsar Cards

```
1. Adicione 3 campos
2. Todos aparecem EXPANDIDOS inicialmente
3. Click no ícone [▼] de um card
4. Card COLAPSA (mostra apenas título e ícone)
5. Click no ícone [▶] novamente
6. Card EXPANDE novamente
```

**✅ Sucesso:** Expansão/colapso funciona

---

### Teste 4: Excluir Campo

```
1. Adicione 3 campos
2. No card do 2º campo, click [🗑️]
3. Card desaparece imediatamente
4. Ordem dos campos restantes é ajustada
```

**✅ Sucesso:** Exclusão de campo funciona

---

### Teste 5: Placeholder

```
1. Adicione campo "Texto Curto"
2. Preencha:
   Label: Nome completo
   Placeholder: Ex: João da Silva
3. Salve e edite
4. Verifique se placeholder foi salvo
```

**✅ Sucesso:** Placeholder foi salvo corretamente

---

### Teste 6: Dark Mode

```
1. Abra o menu de usuário
2. Alterne o tema (Light/Dark)
3. Verifique se o Form Builder adapta cores
```

**✅ Sucesso:** Dark mode funciona

---

### Teste 7: Mobile (Responsivo)

```
1. Abra DevTools (F12)
2. Alterne para modo mobile (Ctrl+Shift+M)
3. Teste o Form Builder no celular simulado
```

**✅ Sucesso:** Layout é responsivo

---

### Teste 8: Filtros

```
1. Crie 2 serviços:
   - Serviço A: [✓] Ativo
   - Serviço B: [ ] Inativo
2. Na listagem, selecione "Ativo" no dropdown
3. Apenas Serviço A aparece
4. Selecione "Inativo"
5. Apenas Serviço B aparece
```

**✅ Sucesso:** Filtros funcionam

---

### Teste 9: Busca

```
1. Crie 2 serviços:
   - "Buraco na Rua"
   - "Lâmpada Queimada"
2. No campo de busca, digite: "buraco"
3. Apenas "Buraco na Rua" aparece
4. Digite: "lâmpada"
5. Apenas "Lâmpada Queimada" aparece
```

**✅ Sucesso:** Busca funciona

---

### Teste 10: Todos os Tipos de Campo

```
1. Crie serviço com 1 campo de cada tipo:
   - Texto Curto
   - Texto Longo
   - Número
   - Foto/Imagem
   - Localização (Mapa)
   - Seleção Múltipla
2. Salve
3. Edite e verifique se todos foram salvos corretamente
```

**✅ Sucesso:** Todos os 6 tipos funcionam

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### Erro: "Unidades não aparecem no dropdown"

**Causa:** Nenhuma unidade ativa

**Solução:**
```
1. Vá para a aba "Unidades Administrativas"
2. Crie ou ative pelo menos uma unidade
3. Volte para "Catálogo de Serviços"
```

---

### Erro: "Botão [Salvar] está desabilitado"

**Causa:** Formulário inválido

**Solução:**
```
Verifique se preencheu:
✅ Nome do Serviço
✅ Unidade Responsável
✅ Pelo menos 1 campo no canvas
✅ Todos os campos têm label preenchido
```

---

### Erro: "Modal não fecha após salvar"

**Causa:** Erro na API (verificar console)

**Solução:**
```
1. Abra DevTools (F12) → Console
2. Procure por erros vermelhos
3. Verifique se o backend está rodando
4. Verifique se o endpoint existe
```

---

### Erro: "Name não está sendo gerado"

**Causa:** Label vazio

**Solução:**
```
1. Digite algo no campo "Label"
2. O "Name" será gerado automaticamente
```

---

## 📊 ESPERADO vs REAL

| Teste | Esperado | Real |
|-------|----------|------|
| Build | ✅ 7.07s | ? |
| Acesso | ✅ Sem erros | ? |
| Auto-geração | ✅ snake_case | ? |
| Adicionar campo | ✅ Card aparece | ? |
| Reordenar | ✅ Ordem muda | ? |
| Validação | ✅ Botão desabilita | ? |
| POST | ✅ Cria serviço | ? |
| PUT | ✅ Atualiza serviço | ? |
| DELETE | ✅ Exclui serviço | ? |

**Preencha "Real" conforme testa!**

---

## 🎯 RESULTADO ESPERADO

Após completar todos os testes, você deve ter:

✅ Criado 2-3 serviços  
✅ Editado pelo menos 1  
✅ Excluído pelo menos 1  
✅ Testado todos os 6 tipos de campo  
✅ Reordenado campos  
✅ Validado auto-geração de `name`  
✅ Testado filtros e busca  
✅ Confirmado que dark mode funciona  

---

## 🎊 TUDO FUNCIONOU?

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║   ✅  FORM BUILDER NO-CODE ESTÁ FUNCIONANDO!     ║
║                                                  ║
║   Próximo passo: Usar em produção! 🚀           ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

**Documentação completa:**
- FORM_BUILDER_NO_CODE.md (overview)
- ARQUITETURA_FORM_BUILDER.md (detalhes técnicos)
- GUIA_USO_FORM_BUILDER.md (tutorial completo)
- ENTREGA_FORM_BUILDER_RESUMO_EXECUTIVO.md (resumo executivo)

---

**⚡ Quick Start - Form Builder No-Code**  
*Tempo total de testes: 10-15 minutos*  
*Status esperado: 100% funcional* ✨
