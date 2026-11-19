# 🏛️ Módulo de Administração - Guia Rápido

## ✅ O QUE FOI CRIADO

**Sprint 4:** Governança & Administração (RBAC)  
**Status:** 100% Completo | Build: ✅ OK

---

## 📦 ARQUIVOS

```
src/stores/
└── admin.js                                      430 linhas

src/components/backoffice/admin/
├── GestaoUnidades.vue                            180 linhas
├── ModalUnidade.vue                              190 linhas
├── GestaoUsuarios.vue                            350 linhas
└── ModalUsuario.vue                              380 linhas

src/views/backoffice/
└── ConfiguracoesView.vue (reescrito)             180 linhas
```

**Total:** ~1.710 linhas

---

## 🎯 FUNCIONALIDADES

### 1. **Gestão de Unidades Administrativas**
- ✅ Tabela com 8 secretarias mock
- ✅ Criar/Editar unidades
- ✅ Status Ativo/Inativo
- ✅ Contador de usuários vinculados

### 2. **Gestão de Usuários (RBAC)**
- ✅ Tabela com 10 usuários mock
- ✅ Criar/Editar usuários
- ✅ 4 perfis hierárquicos
- ✅ Vínculo condicional de unidade
- ✅ Resetar senha
- ✅ Filtros por perfil

---

## 🛡️ PERFIS RBAC

| Perfil | Cor | Vínculo | Acesso |
|--------|-----|---------|--------|
| 🟣 **Super Admin** | Purple | ❌ NÃO | Acesso total |
| 🔵 **Ouvidor** | Blue | ❌ NÃO | Mesa Geral |
| 🟢 **Gestor Setorial** | Green | ✅ SIM | Painel da Unidade |
| 🟠 **Operador Campo** | Orange | ✅ SIM | Magic Link/App |

---

## 📊 DADOS MOCK

### 8 Unidades:
1. SINFRA-OBRAS (8 usuários)
2. SMTT (12 usuários)
3. SEMMA (6 usuários)
4. DEFESA-CIVIL (5 usuários)
5. SMS (15 usuários)
6. SEMED (10 usuários)
7. SEMAS (7 usuários)
8. GM (0 usuários - inativa)

### 10 Usuários:
- 1 Super Admin
- 2 Ouvidores
- 4 Gestores Setoriais
- 3 Operadores de Campo

---

## 🎨 TELAS

### ConfiguracoesView (Layout com Abas):
```
[Unidades] [Usuários] [Serviços] [Textos]
  ▔▔▔▔▔▔▔▔
```

### GestaoUnidades (Tabela):
```
Unidade | Sigla | Status | Usuários | Ações
────────┼───────┼────────┼──────────┼──────
🏛️ SINFRA | SINFRA-OBRAS | ✓ Ativo | 8 | [Editar]
```

### GestaoUsuarios (Tabela):
```
Usuário | Perfil | Unidade | Status | Acesso | Ações
────────┼────────┼─────────┼────────┼────────┼──────
👤 MS | 🛡️ Super Admin | — | ✓ Ativo | há 2min | [Editar][🔑]
```

---

## 🔑 DIFERENCIAL: VÍNCULO CONDICIONAL

```javascript
// No modal de usuário:

if (perfil === 'super_admin' || perfil === 'ouvidor') {
  // Campo "Unidade" OCULTO
  unidade_id = null
} else {
  // Campo "Unidade" OBRIGATÓRIO
  unidade_id = [select com secretarias]
}
```

**Validação inteligente!**

---

## 🔄 FLUXOS PRINCIPAIS

### Criar Usuário Gestor:
```
1. Click "Novo Usuário"
2. Preenche dados (nome, email, CPF*)
3. Seleciona "Gestor Setorial"
4. Campo Unidade aparece automaticamente
5. Seleciona "SINFRA-OBRAS"
6. Click "Criar"
7. ✅ Usuário criado + contador atualizado
```

*CPF com formatação automática: 000.000.000-00

### Resetar Senha:
```
1. Click "🔑" na linha
2. Confirma envio de e-mail
3. ✅ "E-mail enviado para: usuario@..."
```

---

## 📍 COMO ACESSAR

```
URL: /backoffice/configuracoes

Navegação:
Sidebar → ⚙️ Configurações → Aba [Unidades] ou [Usuários]
```

---

## 🎨 DESIGN

- ✅ Layout enterprise limpo
- ✅ Abas de navegação
- ✅ Tabelas responsivas
- ✅ Modais elegantes (scale + opacity)
- ✅ Badges coloridos por perfil
- ✅ Avatar com iniciais (gradiente)
- ✅ Dark mode completo
- ✅ Empty states

---

## 🔌 APIs (Backend Futuro)

```javascript
// Unidades
GET    /api/v1/admin/unidades/
POST   /api/v1/admin/unidades/
PUT    /api/v1/admin/unidades/{id}/

// Usuários
GET    /api/v1/admin/usuarios/
POST   /api/v1/admin/usuarios/
PUT    /api/v1/admin/usuarios/{id}/
POST   /api/v1/admin/usuarios/{id}/resetar-senha/
```

---

## 📊 BUILD

```bash
npm run build
✓ built in 5.90s
✓ 121 entries precached

ConfiguracoesView.js: 46.43 kB (gzip: 11.92 kB) ✅
```

---

## 💎 DESTAQUES

1. **RBAC Hierárquico** - 4 perfis com permissões escalonadas
2. **Vínculo Inteligente** - Campo unidade aparece/oculta baseado no perfil
3. **Validação Contextual** - Regras mudam dinamicamente
4. **Formatação Auto** - CPF e sigla formatados em tempo real
5. **Filtros Rápidos** - Badges clicáveis por perfil com contador
6. **Avatar Dinâmico** - Iniciais com gradiente personalizado
7. **Info Boxes** - Explicações contextuais por perfil
8. **Dark Mode** - Totalmente suportado

---

## 🎯 RESULTADO

```
✅ Gestão de Unidades      (8 secretarias)
✅ Gestão de Usuários      (10 usuários)
✅ RBAC com 4 perfis
✅ Vínculo condicional
✅ Resetar senha
✅ Filtros inteligentes
✅ Dark mode
✅ Build OK
```

---

## 📚 DOCUMENTAÇÃO

- **Completa:** `SPRINT_4_GOVERNANCA.md` (700 linhas)
- **Resumo:** `README_ADMINISTRACAO.md` (este arquivo)

---

**🏛️ Módulo de Administração 100% Pronto!**

*Acesse: `/backoffice/configuracoes`*
