# 🎨 Guia Visual - Matriz de Permissões RBAC

## A Interface Mais Impressionante do Sistema 🔐✨

---

## 1️⃣ MODAL DA MATRIZ - Visão Completa

```
                    ╔═════════════════════════════════════════════════════════════╗
                    ║ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ║
   Header           ║ ▓▓ 🛡️ Novo Perfil de Acesso  ✨              [✕]  ▓▓ ║
   Gradiente →      ║ ▓▓ Matriz de Permissões Granulares — Padrão GLPI  ▓▓ ║
   Purple→Pink      ║ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ║
   com Shimmer      ╠═════════════════════════════════════════════════════════════╣
                    ║                                                             ║
                    ║  ℹ️ Informações do Perfil                                   ║
                    ║  ─────────────────────────                                  ║
                    ║                                                             ║
                    ║  Nome do Perfil *                   Slug (identificador)   ║
                    ║  ┌───────────────────────────┐     ┌────────────────────┐ ║
   Dados básicos    ║  │ Operador de Máquinas      │     │ operador_maquinas  │ ║
                    ║  └───────────────────────────┘     └────────────────────┘ ║
                    ║                                                             ║
                    ║  Descrição                                                  ║
                    ║  ┌───────────────────────────────────────────────────────┐ ║
                    ║  │ Acesso apenas para visualizar ordens de serviço       │ ║
                    ║  └───────────────────────────────────────────────────────┘ ║
                    ║                                                             ║
                    ║  ☑ Requer Vínculo de Unidade Administrativa                ║
                    ║  ☑ Perfil Ativo                                            ║
                    ║                                                             ║
                    ║  ─────────────────────────────────────────────────────────  ║
                    ║                                                             ║
                    ║  🎯 Matriz de Permissões por Módulo  [Marcar][Desmarcar]  ║
                    ║                                                             ║
                    ║  ╔═══════════════════════════════════════════════════════╗ ║
   A MATRIZ! →      ║  ║ MÓDULO             │ 👁️ LER│➕ CRIAR│✏️ EDITAR│🗑️ EXCLUIR║ ║
                    ║  ╠════════════════════╪═══════╪════════╪════════╪═══════╣ ║
                    ║  ║ 📋 Mesa Trabalho   │  🟢  │   ⚪   │   ⚪   │   ⚪  ║ ║
                    ║  ║ Gerenciar protoc.  │       │        │        │       ║ ║
                    ║  ╠════════════════════╪═══════╪════════╪════════╪═══════╣ ║
                    ║  ║ 🏛️ Painel Setorial │  🟢  │   🟢   │   🟢   │   ⚪  ║ ║
                    ║  ║ Gestão de OS       │       │        │        │       ║ ║
                    ║  ╠════════════════════╪═══════╪════════╪════════╪═══════╣ ║
                    ║  ║ 🗺️ Mapa & IA       │  🟢  │   ⚪   │   ⚪   │   ⚪  ║ ║
                    ║  ║ Visão geográfica   │       │        │        │       ║ ║
                    ║  ╠════════════════════╪═══════╪════════╪════════╪═══════╣ ║
                    ║  ║ ⚙️ Configurações   │  ⚪  │   ⚪   │   ⚪   │   ⚪  ║ ║
                    ║  ║ Administração      │       │        │        │       ║ ║
                    ║  ╠════════════════════╪═══════╪════════╪════════╪═══════╣ ║
                    ║  ║ 📝 Textos Padrão   │  🟢  │   🟢   │   🟢   │   🟢  ║ ║
                    ║  ║ Modelos despacho   │       │        │        │       ║ ║
                    ║  ╠════════════════════╪═══════╪════════╪════════╪═══════╣ ║
                    ║  ║ 👥 Gestão Usuários │  ⚪  │   ⚪   │   ⚪   │   ⚪  ║ ║
                    ║  ║ Criar e editar     │       │        │        │       ║ ║
                    ║  ╚═══════════════════════════════════════════════════════╝ ║
                    ║                                                             ║
                    ║  💡 Ative apenas as permissões necessárias para cada perfil║
                    ║                                                             ║
                    ╠═════════════════════════════════════════════════════════════╣
   Footer           ║  * Campos obrigatórios      [Cancelar] [✨ Criar Perfil]  ║
                    ║  As permissões serão salvas no formato JSON (Padrão GLPI)  ║
                    ╚═════════════════════════════════════════════════════════════╝
```

**Legenda:**
- 🟢 = **ATIVADO** (gradient purple→pink + shadow)
- ⚪ = **DESATIVADO** (cinza)

---

## 2️⃣ TOGGLES (SWITCHES) - Anatomia

### Desligado (OFF):

```
┌─────────────┐
│ ⚪────────  │  ← Bolinha à esquerda
│             │     Background: gray-200
│             │     Border: gray-300
└─────────────┘
```

### Ligado (ON):

```
┌─────────────┐
│  ────────🟢 │  ← Bolinha à direita
│             │     Background: gradient purple→pink
│             │     Shadow: glow purple
└─────────────┘
```

**Animação:**
- Transição suave (300ms)
- Bolinha desliza com easing
- Shadow aparece no hover

---

## 3️⃣ LISTAGEM DE PERFIS - Grid

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  Perfis de Acesso (RBAC)                         [➕ Novo Perfil]            ║
║  Gestão granular de permissões por módulo — Padrão GLPI                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌────────────────────────┬────────────────────────┬────────────────────────┐║
║  │ ┌────────────────────┐ │ ┌────────────────────┐ │ ┌────────────────────┐││
║  │ │ 🛡️ Chefe Gabinete  │ │ │ 🛡️ Operador Máq.  │ │ │ 🛡️ Secretário      │││
║  │ │ ID: 1      ● Ativo │ │ │ ID: 2      ● Ativo │ │ │ ID: 3      ● Ativo │││
║  │ │                    │ │ │                    │ │ │                    │││
║  │ │ Acesso gerencial   │ │ │ Apenas visualizar  │ │ │ Acesso estratégico │││
║  │ │ com permissões...  │ │ │ ordens de serviço  │ │ │ ao seu setor       │││
║  │ │                    │ │ │                    │ │ │                    │││
║  │ │ ┌────────────────┐ │ │ │ ┌────────────────┐ │ │ │ ┌────────────────┐ │││
║  │ │ │ Módulos: 5     │ │ │ │ │ Módulos: 2     │ │ │ │ │ Módulos: 4     │ │││
║  │ │ └────────────────┘ │ │ │ └────────────────┘ │ │ │ └────────────────┘ │││
║  │ │                    │ │ │                    │ │ │                    │││
║  │ │ 👥 12  🏛️ Vínculo │ │ │ 👥 3   🏛️ Vínculo │ │ │ 👥 8   🏛️ Vínculo │││
║  │ │                    │ │ │                    │ │ │                    │││
║  │ │ [Editar] [🗑️]     │ │ │ [Editar] [🗑️]     │ │ │ [Editar] [🗑️]     │││
║  │ └────────────────────┘ │ └────────────────────┘ │ └────────────────────┘││
║  └────────────────────────┴────────────────────────┴────────────────────────┘║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Responsivo:**
- Desktop: 3 colunas
- Tablet: 2 colunas
- Mobile: 1 coluna

---

## 4️⃣ HEADER COM SHIMMER ANIMATION

```
Frame 1:
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓ 🛡️ Novo Perfil de Acesso ✨   [✕] ▓▓
│←── Brilho se move da esquerda


Frame 2:
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓ 🛡️ Novo Perfil de Acesso ✨   [✕] ▓▓
         │←── Brilho no centro


Frame 3:
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓ 🛡️ Novo Perfil de Acesso ✨   [✕] ▓▓
                             Brilho →│


Loop: 3 segundos infinito
```

**CSS:**
```css
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

---

## 5️⃣ SELECT DINÂMICO EM USUÁRIOS

### Antes (Hardcoded):

```
Perfil de Acesso *
┌────────────────────────────────────────┐
│ ▼ Selecione um perfil...              │
│   Super Admin — Acesso total          │ ← Fixo no código
│   Ouvidor — Mesa Geral                │ ← Fixo no código
│   Gestor Setorial — Painel Unidade    │ ← Fixo no código
│   Operador Campo — Magic Link/App     │ ← Fixo no código
└────────────────────────────────────────┘
```

### Depois (Dinâmico):

```
Perfil de Acesso *
┌────────────────────────────────────────┐
│ ▼ Selecione um perfil...              │
│   Chefe de Gabinete — Acesso gerencial│ ← Da API!
│   Operador de Máquinas — Visualizar OS│ ← Da API!
│   Secretário — Gestão estratégica     │ ← Da API!
│   Prefeito — Acesso total             │ ← Da API!
│   ...                                  │
└────────────────────────────────────────┘
```

**Fonte:** `GET /backoffice/perfis-acesso`

---

## 6️⃣ FILTROS DINÂMICOS EM GESTÃO USUÁRIOS

### Filtros renderizados dinamicamente:

```
[● Chefe Gabinete 12] [● Operador Máq. 3] [● Secretário 8] [● Prefeito 1]
 🟣                    🟣                   🟣               🟣
 
 ← Carregado da API, não hardcoded!
```

**Hover:**
```
[● Chefe Gabinete 12]  →  Destaca com ring-2 purple
```

**Ativo:**
```
[◉ Chefe Gabinete 12]  →  Background purple + ring-2 + shadow
```

---

## 7️⃣ DEPENDÊNCIAS AUTOMÁTICAS

### Exemplo Visual:

```
Cenário: Usuário marca "Editar" em Mesa de Trabalho

Antes de marcar:
Mesa Trabalho:  [⚪ Ler] [⚪ Criar] [⚪ Editar] [⚪ Excluir]

Marca "Editar":
Mesa Trabalho:  [🟢 Ler] [⚪ Criar] [🟢 Editar] [⚪ Excluir]
                  ↑                    ↑
              Auto-marcado!        Marcado pelo usuário
```

**Lógica:**
- Marcar **Editar** → Auto-marca **Ler**
- Marcar **Excluir** → Auto-marca **Ler**
- Marcar **Criar** → Auto-marca **Ler**

**Motivo:** Não faz sentido editar/criar/excluir sem poder visualizar!

---

## 8️⃣ JSON GERADO PELA MATRIZ

### Visualização do que vai pro backend:

```json
{
  "nome": "Operador de Máquinas",
  "slug": "operador_maquinas",
  "descricao": "Acesso apenas para visualizar ordens de serviço",
  "requer_vinculo": true,
  "ativo": true,
  "permissoes": {
    "mesa_trabalho": {
      "ler": true,     ← 🟢
      "criar": false,  ← ⚪
      "editar": false, ← ⚪
      "excluir": false ← ⚪
    },
    "painel_setorial": {
      "ler": true,     ← 🟢
      "criar": true,   ← 🟢
      "editar": true,  ← 🟢
      "excluir": false ← ⚪
    },
    // ... outros módulos
  }
}
```

**Formato:** Padrão GLPI (JSON estruturado)

---

## 9️⃣ PALETA DE CORES

### Gradientes:

```css
Header Modal:
  from-purple-600 via-pink-600 to-purple-600
  (#9333EA → #EC4899 → #9333EA)

Toggles Ativos:
  from-purple-600 to-pink-600
  (#9333EA → #EC4899)

Glow:
  shadow-lg shadow-purple-500/50
```

### Badges:

```css
Ativo:   bg-green-100 text-green-800
         dark:bg-green-900/30 dark:text-green-300

Inativo: bg-gray-100 text-gray-600
         dark:bg-gray-700 dark:text-gray-400
```

---

## 🔟 BOTÕES DE AÇÃO

### "Novo Perfil" (Destaque):

```
┌───────────────────────────────────────┐
│ ➕ Novo Perfil                        │
│                                       │
│ Gradient: purple→pink                 │
│ Shadow: purple glow                   │
│ Hover: purple-700→pink-700            │
└───────────────────────────────────────┘
```

### "Marcar Todos" / "Desmarcar Todos":

```
[Marcar Todos]     ← texto verde
     |
[Desmarcar Todos]  ← texto vermelho
```

---

## 1️⃣1️⃣ EMPTY STATE

```
╔══════════════════════════════════════════╗
║                                          ║
║              ┌────────┐                  ║
║              │  🛡️   │  ← Icon circular  ║
║              │ Purple│     com gradiente ║
║              └────────┘                  ║
║                                          ║
║     Nenhum perfil cadastrado             ║
║                                          ║
║   Crie o primeiro perfil de acesso       ║
║   com permissões granulares              ║
║                                          ║
║      [➕ Novo Perfil]                    ║
║                                          ║
╚══════════════════════════════════════════╝
```

---

## 1️⃣2️⃣ CONFIRMAÇÃO DE EXCLUSÃO

```
┌─────────────────────────────────────────┐
│  ⚠️ Excluir Perfil                     │
├─────────────────────────────────────────┤
│                                         │
│  Deseja realmente excluir o perfil:    │
│                                         │
│  "Operador de Máquinas"                 │
│                                         │
│  Esta ação não pode ser desfeita.      │
│                                         │
├─────────────────────────────────────────┤
│       [Cancelar]  [Excluir]            │
└─────────────────────────────────────────┘
```

**Restrição:** Só aparece se `usuarios_count === 0`

---

## 🎨 RESUMO VISUAL

```
╔════════════════════════════════════════════════════════════════╗
║                  MATRIZ DE PERMISSÕES RBAC                     ║
║                                                                ║
║  ✨ Header com shimmer animation (Purple→Pink)                 ║
║  🎯 Matriz 6 módulos x 4 ações = 24 toggles                    ║
║  🟢 Toggles com gradiente quando ativo                         ║
║  🧠 Dependências automáticas (editar → auto-marca ler)         ║
║  📊 Grid de cards com estatísticas                             ║
║  🔄 Select dinâmico em usuários                                ║
║  🎨 Dark mode completo                                         ║
║  ⚡ Ações em massa (marcar/desmarcar todos)                    ║
║                                                                ║
║  🏆 INTERFACE MAIS IMPRESSIONANTE DO SISTEMA                   ║
╚════════════════════════════════════════════════════════════════╝
```

---

**🎨 Guia Visual Completo - Matriz de Permissões RBAC**

*Interface enterprise-grade para gestão granular de permissões*  
*Padrão GLPI | JSON estruturado | Visual impressionante*
