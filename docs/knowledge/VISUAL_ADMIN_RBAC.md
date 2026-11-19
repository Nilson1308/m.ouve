# 🎨 Guia Visual - Administração e RBAC

## Módulo de Governança - Interfaces Detalhadas

---

## 1️⃣ LAYOUT PRINCIPAL - ConfiguracoesView

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  ⚙️ Configurações & Administração        [🛡️ Acesso Administrativo]    ║
║  Gestão de unidades administrativas, usuários, acessos e configurações  ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ┌───────────────┬──────────────────┬─────────────────┬──────────────┐ ║
║  │ Unidades      │ Usuários e       │ Catálogo de     │ Textos       │ ║
║  │ Administrativas│ Acessos          │ Serviços        │ Padrão       │ ║
║  │      8        │     10           │                 │              │ ║
║  └───────────────┴──────────────────┴─────────────────┴──────────────┘ ║
║  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                                       ║
║                                                                          ║
║  ┌────────────────────────────────────────────────────────────────────┐ ║
║  │                                                                    │ ║
║  │                    CONTEÚDO DA ABA ATIVA                           │ ║
║  │                    (GestaoUnidades ou                              │ ║
║  │                     GestaoUsuarios)                                │ ║
║  │                                                                    │ ║
║  └────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Navegação:**
- Tabs horizontais
- Badge com contador dinâmico
- Fade transition entre abas (300ms)

---

## 2️⃣ ABA UNIDADES - Tabela Completa

```
╔═════════════════════════════════════════════════════════════════════════════════════╗
║  Unidades Administrativas                           [➕ Nova Unidade]               ║
║  Secretarias e órgãos executivos da prefeitura                                      ║
╠═════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                     ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐  ║
║  │ UNIDADE                          │ SIGLA       │ STATUS  │ USUÁRIOS │ AÇÕES   │  ║
║  ├──────────────────────────────────┼─────────────┼─────────┼──────────┼─────────┤  ║
║  │ 🏛️ Secretaria Municipal de       │ [SINFRA-   │ ● Ativo │    8     │[✏️Editar]│  ║
║  │    Infraestrutura e Obras        │  OBRAS]    │         │          │         │  ║
║  │    Obras públicas, manutenção    │            │         │          │         │  ║
║  ├──────────────────────────────────┼─────────────┼─────────┼──────────┼─────────┤  ║
║  │ 🏛️ Secretaria Municipal de       │ [ SMTT ]   │ ● Ativo │   12     │[✏️Editar]│  ║
║  │    Transporte e Trânsito         │            │         │          │         │  ║
║  │    Gestão do transporte público  │            │         │          │         │  ║
║  ├──────────────────────────────────┼─────────────┼─────────┼──────────┼─────────┤  ║
║  │ 🏛️ Secretaria Municipal de       │ [ SEMMA ]  │ ● Ativo │    6     │[✏️Editar]│  ║
║  │    Meio Ambiente                 │            │         │          │         │  ║
║  │    Preservação ambiental...      │            │         │          │         │  ║
║  ├──────────────────────────────────┼─────────────┼─────────┼──────────┼─────────┤  ║
║  │ 🏛️ Defesa Civil Municipal        │ [DEFESA-   │ ● Ativo │    5     │[✏️Editar]│  ║
║  │                                  │  CIVIL]    │         │          │         │  ║
║  │    Prevenção e resposta...       │            │         │          │         │  ║
║  ├──────────────────────────────────┼─────────────┼─────────┼──────────┼─────────┤  ║
║  │ 🏛️ Secretaria Municipal de Saúde │ [  SMS  ]  │ ● Ativo │   15     │[✏️Editar]│  ║
║  │                                  │            │         │          │         │  ║
║  │    Gestão da rede de saúde       │            │         │          │         │  ║
║  ├──────────────────────────────────┼─────────────┼─────────┼──────────┼─────────┤  ║
║  │ 🏛️ Guarda Municipal              │ [   GM  ]  │ ○ Inativo│    0     │[✏️Editar]│  ║
║  │                                  │            │         │          │         │  ║
║  │    Segurança patrimonial...      │            │         │          │         │  ║
║  └──────────────────────────────────┴─────────────┴─────────┴──────────┴─────────┘  ║
║                                                                                     ║
╚═════════════════════════════════════════════════════════════════════════════════════╝
```

**Elementos:**
- Ícone 🏛️ em box colorido
- Sigla em badge mono-font
- Status com dot animado (● verde | ○ cinza)
- Contador de usuários com ícone
- Hover: fundo cinza claro

---

## 3️⃣ MODAL UNIDADE - Criar/Editar

```
                 ╔═══════════════════════════════════════════════════╗
                 ║  🏛️ Nova Unidade Administrativa            [✕]   ║
                 ║  Cadastre uma nova secretaria ou órgão executivo ║
                 ╠═══════════════════════════════════════════════════╣
                 ║                                                   ║
                 ║  Nome da Unidade *                               ║
                 ║  ┌─────────────────────────────────────────────┐ ║
                 ║  │ Secretaria Municipal de Infraestrutura__   │ ║
                 ║  └─────────────────────────────────────────────┘ ║
                 ║  Nome completo oficial da secretaria            ║
                 ║                                                   ║
                 ║  Sigla *                                         ║
                 ║  ┌─────────────────────────────────────────────┐ ║
                 ║  │ SINFRA-OBRAS                                │ ║
                 ║  └─────────────────────────────────────────────┘ ║
                 ║  Abreviação (máx. 20 chars) AUTO-MAIÚSCULA      ║
                 ║                                                   ║
                 ║  Descrição                                       ║
                 ║  ┌─────────────────────────────────────────────┐ ║
                 ║  │ Responsável por obras públicas, manutenção  │ ║
                 ║  │ urbana, pavimentação e iluminação pública   │ ║
                 ║  │                                             │ ║
                 ║  └─────────────────────────────────────────────┘ ║
                 ║  Ajuda os usuários a entender o escopo          ║
                 ║                                                   ║
                 ║  ┌─────────────────────────────────────────────┐ ║
                 ║  │ ☑ Unidade Ativa                             │ ║
                 ║  │ Unidades inativas não aparecem nos filtros  │ ║
                 ║  └─────────────────────────────────────────────┘ ║
                 ║                                                   ║
                 ║  (Se editando: Info box com dados do cadastro)  ║
                 ║                                                   ║
                 ╠═══════════════════════════════════════════════════╣
                 ║  * Campos obrigatórios  [Cancelar] [✓ Criar]    ║
                 ╚═══════════════════════════════════════════════════╝
```

**Validações:**
- Nome: min 3 chars
- Sigla: min 2 chars, max 20, auto-uppercase
- Botão desabilita se inválido (opacity 50%)

---

## 4️⃣ ABA USUÁRIOS - Filtros + Tabela

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  Usuários e Controle de Acesso                              [➕ Novo Usuário]           ║
║  Gestão de servidores, perfis e permissões (RBAC)                                       ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                          ║
║  Filtros:                                                                                ║
║  ┌──────────────┬───────────┬──────────────────┬────────────────────┬───────────────┐  ║
║  │ ● Super Admin│ ● Ouvidor │ ● Gestor Setorial│ ● Operador Campo   │ ✕ Limpar      │  ║
║  │      1       │     2     │       4          │        3           │               │  ║
║  └──────────────┴───────────┴──────────────────┴────────────────────┴───────────────┘  ║
║  🟣             🔵          🟢                 🟠                                        ║
║                                                                                          ║
║  ┌──────────────────────────────────────────────────────────────────────────────────┐  ║
║  │ USUÁRIO           │ PERFIL        │ UNIDADE         │ STATUS │ ACESSO    │ AÇÕES  │  ║
║  ├───────────────────┼───────────────┼─────────────────┼────────┼───────────┼────────┤  ║
║  │ 👤 MS             │ 🛡️ Super     │ Sem vínculo     │● Ativo │ há 2min   │✏️  🔑  │  ║
║  │ Maria da Silva    │    Admin      │                 │        │           │        │  ║
║  │ maria@prefeitura  │               │                 │        │           │        │  ║
║  ├───────────────────┼───────────────┼─────────────────┼────────┼───────────┼────────┤  ║
║  │ 👤 JO             │ 🛡️ Ouvidor   │ Sem vínculo     │● Ativo │ há 15min  │✏️  🔑  │  ║
║  │ João Pedro        │               │                 │        │           │        │  ║
║  │ joao@prefeitura   │               │                 │        │           │        │  ║
║  ├───────────────────┼───────────────┼─────────────────┼────────┼───────────┼────────┤  ║
║  │ 👤 CM             │ 🛡️ Gestor    │ 🏛️ SINFRA-OBRAS│● Ativo │ há 30min  │✏️  🔑  │  ║
║  │ Carlos Alberto    │    Setorial   │                 │        │           │        │  ║
║  │ carlos@prefeitura │               │                 │        │           │        │  ║
║  ├───────────────────┼───────────────┼─────────────────┼────────┼───────────┼────────┤  ║
║  │ 👤 AC             │ 🛡️ Gestor    │ 🏛️ SMTT        │● Ativo │ há 1h     │✏️  🔑  │  ║
║  │ Ana Paula Costa   │    Setorial   │                 │        │           │        │  ║
║  │ ana@prefeitura    │               │                 │        │           │        │  ║
║  ├───────────────────┼───────────────┼─────────────────┼────────┼───────────┼────────┤  ║
║  │ 👤 RS             │ 🛡️ Operador  │ 🏛️ SINFRA-OBRAS│● Ativo │ há 5min   │✏️  🔑  │  ║
║  │ Roberto da Silva  │    de Campo   │                 │        │           │        │  ║
║  │ roberto@prefeit   │               │                 │        │           │        │  ║
║  └───────────────────┴───────────────┴─────────────────┴────────┴───────────┴────────┘  ║
║                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

**Detalhes:**
- **Avatar:** Círculo com gradiente Primary→Purple, iniciais brancas
- **Badges de perfil:** Cores específicas (Purple, Blue, Green, Orange)
- **Último acesso:** Relativo (há Xmin, há Xh, DD/MM)
- **Filtros:** Clicáveis, com ring-2 quando ativo
- **Ações:** ✏️ Editar | 🔑 Resetar Senha (hover orange)

---

## 5️⃣ MODAL USUÁRIO - RBAC Completo

```
        ╔════════════════════════════════════════════════════════════════════╗
        ║  👤 Novo Usuário do Sistema                                  [✕]   ║
        ║  Cadastre um novo servidor com controle de acesso                 ║
        ╠════════════════════════════════════════════════════════════════════╣
        ║                                                                    ║
        ║  📋 Dados Pessoais                                                ║
        ║  ───────────────                                                  ║
        ║                                                                    ║
        ║  Nome Completo *                                                  ║
        ║  ┌──────────────────────────────────────────────────────────────┐ ║
        ║  │ José da Silva Santos                                         │ ║
        ║  └──────────────────────────────────────────────────────────────┘ ║
        ║                                                                    ║
        ║  E-mail Corporativo *           CPF *                             ║
        ║  ┌────────────────────────────┐  ┌────────────────────────────┐ ║
        ║  │ jose@prefeitura.gov.br     │  │ 123.456.789-00             │ ║
        ║  └────────────────────────────┘  └────────────────────────────┘ ║
        ║  Usado para login               Formatação automática           ║
        ║                                                                    ║
        ║  🛡️ Controle de Acesso (RBAC)                                    ║
        ║  ─────────────────────────                                        ║
        ║                                                                    ║
        ║  Perfil de Acesso *                                               ║
        ║  ┌──────────────────────────────────────────────────────────────┐ ║
        ║  │ ▼ Selecione um perfil...                                     │ ║
        ║  │                                                              │ ║
        ║  │   Super Admin — Acesso total ao sistema                     │ ║
        ║  │   Ouvidor — Mesa de Trabalho Geral                          │ ║
        ║  │ → Gestor Setorial — Painel da sua Unidade    ✓ SELECIONADO │ ║
        ║  │   Operador de Campo — Acesso via Magic Link/App             │ ║
        ║  └──────────────────────────────────────────────────────────────┘ ║
        ║                                                                    ║
        ║  ╭────────────────────────────────────────────────────────────╮  ║
        ║  │ 🛡️ Gestor Setorial                                          │  ║
        ║  │ Painel da sua Unidade, gerencia equipe setorial             │  ║
        ║  ╰────────────────────────────────────────────────────────────╯  ║
        ║                                                                    ║
        ║  Unidade Administrativa *   ← APARECE PORQUE PERFIL REQUER       ║
        ║  ┌──────────────────────────────────────────────────────────────┐ ║
        ║  │ ▼ Selecione uma unidade...                                   │ ║
        ║  │                                                              │ ║
        ║  │   SINFRA-OBRAS — Secretaria Mun. de Infraestrutura         │ ║
        ║  │ → SMTT — Secretaria Mun. de Transporte e Trânsito   ✓      │ ║
        ║  │   SEMMA — Secretaria Mun. de Meio Ambiente                  │ ║
        ║  │   DEFESA-CIVIL — Defesa Civil Municipal                     │ ║
        ║  └──────────────────────────────────────────────────────────────┘ ║
        ║  Usuário terá acesso apenas aos protocolos desta unidade         ║
        ║                                                                    ║
        ║  ┌──────────────────────────────────────────────────────────────┐ ║
        ║  │ ☑ Usuário Ativo                                              │ ║
        ║  │ Usuários inativos não podem fazer login                      │ ║
        ║  └──────────────────────────────────────────────────────────────┘ ║
        ║                                                                    ║
        ╠════════════════════════════════════════════════════════════════════╣
        ║  * Campos obrigatórios              [Cancelar] [✓ Criar Usuário] ║
        ║  O usuário receberá e-mail para definir sua senha                 ║
        ╚════════════════════════════════════════════════════════════════════╝
```

**Lógica Condicional:**

```javascript
// Perfil selecionado: Super Admin ou Ouvidor
Campo "Unidade" → OCULTO
Info box: "Este perfil não requer vínculo a uma unidade.
          Super Admins têm acesso total ao sistema."

// Perfil selecionado: Gestor Setorial ou Operador Campo  
Campo "Unidade" → VISÍVEL + OBRIGATÓRIO
Info box: "Gestor Setorial — Painel da sua Unidade..."
```

---

## 6️⃣ CONFIRM DIALOG - Resetar Senha

```
                    ┌───────────────────────────────────────┐
                    │  ⚠️ Resetar Senha                    │
                    ├───────────────────────────────────────┤
                    │                                       │
                    │  Deseja enviar um e-mail de          │
                    │  redefinição de senha para:          │
                    │                                       │
                    │  Nome: José da Silva Santos          │
                    │  E-mail: jose@prefeitura.gov.br      │
                    │                                       │
                    │  O usuário receberá um link          │
                    │  temporário para definir nova senha. │
                    │                                       │
                    ├───────────────────────────────────────┤
                    │       [Cancelar]  [OK, Enviar]       │
                    └───────────────────────────────────────┘
```

**Após confirmação:**

```
✅ E-mail de redefinição de senha enviado com sucesso

E-mail enviado para: jose@prefeitura.gov.br
```

---

## 7️⃣ FILTRO ATIVO - Estado Visual

```
Filtros (SEM filtro ativo):

[🟣 Super Admin 1] [🔵 Ouvidor 2] [🟢 Gestor Setorial 4] [🟠 Operador Campo 3]
 ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁   ▁▁▁▁▁▁▁▁▁▁▁▁▁   ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁   ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁


Filtros (COM filtro "Gestor Setorial" ativo):

[🟣 Super Admin 1] [🔵 Ouvidor 2] [🟢 Gestor Setorial 4] [🟠 Operador Campo 3] [✕ Limpar]
                                    ◉◉◉◉◉◉◉◉◉◉◉◉◉◉◉◉◉◉◉◉
                                    ring-2 ring-green-500
                                    bg-green-100

Tabela mostra apenas 4 usuários (Carlos, Ana, Fernanda, Juliana)
```

---

## 8️⃣ EMPTY STATE - Sem Usuários

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  Usuários e Controle de Acesso                    [➕ Novo Usuário]      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║                                                                           ║
║                            👥                                             ║
║                       (ícone grande)                                      ║
║                                                                           ║
║                    Nenhum usuário cadastrado                              ║
║                                                                           ║
║              Comece criando o primeiro usuário do sistema                ║
║                                                                           ║
║                     [➕ Novo Usuário]                                     ║
║                                                                           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## 9️⃣ RESPONSIVIDADE - Mobile

### Desktop (> 1024px):
```
[Unidades 8] [Usuários 10] [Serviços] [Textos]
     ▔▔▔▔▔▔▔▔

┌────────────────────────────────────────────────────┐
│ Tabela completa visível                            │
│ 6 colunas                                          │
└────────────────────────────────────────────────────┘
```

### Mobile (< 768px):
```
[≡] Configurações

[▼] Unidades 8

┌──────────────────┐
│ Tabela scroll →  │
│ Colunas colapsam │
└──────────────────┘
```

---

## 🎨 PALETA DE CORES

### Perfis RBAC:
```
🟣 Super Admin:     #9333EA (Purple-600)
🔵 Ouvidor:         #3B82F6 (Blue-600)
🟢 Gestor Setorial: #10B981 (Green-600)
🟠 Operador Campo:  #F97316 (Orange-600)
```

### Status:
```
● Ativo:   #10B981 (Green-500)
○ Inativo: #9CA3AF (Gray-400)
```

### Avatar:
```
Gradiente: from-primary-500 to-purple-600
          (#2563EB → #9333EA)
```

---

## 🎭 ANIMAÇÕES

### Modal:
```
Entrada:
  opacity: 0 → 1 (300ms)
  scale: 0.95 → 1.0 (300ms)

Saída:
  opacity: 1 → 0 (200ms)
  scale: 1.0 → 0.95 (200ms)
```

### Abas:
```
Fade transition (200ms ease)
```

### Filtros:
```
Hover: bg-gray-200 (transition 200ms)
Ativo: ring-2 + scale (transition 300ms)
```

---

**🎨 Guia Visual Completo - Administração e RBAC**

*Todas as telas enterprise-grade com design system consistente*
