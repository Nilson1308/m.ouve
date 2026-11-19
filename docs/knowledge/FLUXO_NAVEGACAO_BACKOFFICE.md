# 🗺️ FLUXO DE NAVEGAÇÃO - BACKOFFICE

## 📍 Navegação Completa (Sprint 2)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🏛️ OUVIA - BACKOFFICE                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 🔐 LOGIN DO SERVIDOR                                                │
│    /backoffice                                                      │
│                                                                     │
│    [CPF] ________________                                           │
│    [Senha] ____________                                             │
│    [Entrar no Sistema] ────────────────────────────────────┐        │
└─────────────────────────────────────────────────────────────────────┘
                                                             │
                                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 DASHBOARD (Home)                                                 │
│    /backoffice/dashboard                                            │
│                                                                     │
│    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│    │ 📈 Total    │ │ ⏱️ Em And.  │ │ ✅ Concluíd.│                │
│    │    250      │ │    45        │ │    150      │                │
│    └─────────────┘ └─────────────┘ └─────────────┘                │
│                                                                     │
│    [Ver Mesa de Trabalho] ──────────────────────────────┐          │
└─────────────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 📋 MESA DE TRABALHO (Gestão de Protocolos)                         │
│    /backoffice/mesa-trabalho                                        │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ [🔍 Buscar] [⚡ SLA Vencido (5)] [🔴 Urgentes (12)]        │   │
│ │ [👁️ Kanban] [📊 Lista]                                      │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│ ╔═════════════════════════════════════════════════════════════╗   │
│ ║ VISUALIZAÇÃO KANBAN                                         ║   │
│ ╠═════════════════════════════════════════════════════════════╣   │
│ ║                                                             ║   │
│ ║ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       ║   │
│ ║ │ NOVO     │ │ EM AND.  │ │ AGUARD.  │ │ CONCLUÍD.│       ║   │
│ ║ │   (8)    │ │   (12)   │ │   (5)    │ │   (10)   │       ║   │
│ ║ ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤       ║   │
│ ║ │┌────────┐│ │┌────────┐│ │┌────────┐│ │┌────────┐│       ║   │
│ ║ ││PROT-042││ ││PROT-039││ ││PROT-035││ ││PROT-030││       ║   │
│ ║ ││Buraco  ││ ││Ilum.   ││ ││Calçada ││ ││Árvore  ││       ║   │
│ ║ ││[SLA OK]││ ││[VENCIDO││ ││[6h rest││ ││[✓]     ││       ║   │
│ ║ ││[Clique]││◄┼┤[Clique]││ ││[Clique]││ ││[Clique]││       ║   │
│ ║ │└────────┘│ │└────────┘│ │└────────┘│ │└────────┘│       ║   │
│ ║ └──────────┘ └──────────┘ └──────────┘ └──────────┘       ║   │
│ ╚═════════════════════════════════════════════════════════════╝   │
│                                                                     │
│ Ações:                                                              │
│ • Clicar no card ─────────────────────────────┐                    │
│ • Clicar em "👁️ Ver Detalhes" ───────────────┼────┐               │
│ • Clicar na linha da tabela ──────────────────┘    │               │
└─────────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 🔍 DETALHES DO PROTOCOLO (Visão 360º)                              │
│    /backoffice/protocolo/:id                                        │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ ← PROT-2024-042  [Aguard. Revisão] [36h] [Buraco] [João]   │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│ ┌──────────────────────────┬────────────────────────────────────┐ │
│ │  COLUNA ESQUERDA         │  COLUNA DIREITA                    │ │
│ │  (O Problema)            │  (A Solução)                       │ │
│ ├──────────────────────────┼────────────────────────────────────┤ │
│ │                          │                                    │ │
│ │ 🤖 Dados Coletados IA    │ ✅ AÇÕES DE VALIDAÇÃO             │ │
│ │ ┌──────────────────────┐ │ ┌────────────────────────────────┐ │
│ │ │ Descrição: Buraco... │ │ │ Resposta ao Cidadão:           │ │
│ │ │ Tamanho: 1 metro     │ │ │ [Selecione...]▼               │ │
│ │ │ Profundidade: 20cm   │ │ │                                │ │
│ │ │ Sinalização: Não     │ │ │ Observações:                  │ │
│ │ │ ...                  │ │ │ [_____________]                │ │
│ │ └──────────────────────┘ │ │                                │ │
│ │                          │ │ PREVIEW:                       │ │
│ │ 📍 Localização           │ │ "Prezado cidadão..."           │ │
│ │ ┌──────────────────────┐ │ │                                │ │
│ │ │ Av. Principal, 500   │ │ │ [✅ Validar e Encerrar]       │ │
│ │ │ Centro - São Paulo   │ │ │ [↶ Devolver à Secretaria]     │ │
│ │ │ [MAPA com PINO 📍]   │ │ │ [✏️ Editar] [📄 Relatório]     │ │
│ │ └──────────────────────┘ │ └────────────────────────────────┘ │
│ │                          │                                    │ │
│ │ 💬 Histórico Chat [▼]   │ 📋 Ordens de Serviço              │ │
│ │ ┌──────────────────────┐ │ ┌────────────────────────────────┐ │
│ │ │ 🤖 IA: Olá! Sou a... │ │ │ ⚫ Secretaria de Obras         │ │
│ │ │ 👤 Cidadão: Tem um...│ │ │    [✅ Concluído]              │ │
│ │ │ 🤖 IA: Entendo...    │ │ │    📅 Prazo: 14/11             │ │
│ │ │ 👤 Cidadão: Avenida..│ │ │    ✓ Concluído: 13/11          │ │
│ │ │ ...                  │ │ │                                │ │
│ │ │ [11 mensagens]       │ │ │    OBSERVAÇÕES:               │ │
│ │ └──────────────────────┘ │ │    "Serviço executado..."      │ │
│ │                          │ │                                │ │
│ │                          │ │    FOTOS (3):                  │ │
│ │                          │ │    [📷 Antes] [📷 Durante]     │ │
│ │                          │ │    [📷 Depois]                 │ │
│ │                          │ │                                │ │
│ │                          │ │    Duração: 6h 15min           │ │
│ │                          │ ├────────────────────────────────┤ │
│ │                          │ │ ⚫ Defesa Civil                │ │
│ │                          │ │    [✅ Concluído]              │ │
│ │                          │ │    "Vistoria realizada..."     │ │
│ │                          │ │    [📷 Vistoria]               │ │
│ │                          │ └────────────────────────────────┘ │
│ │                          │                                    │ │
│ └──────────────────────────┴────────────────────────────────────┘ │
│                                                                     │
│ Ações Principais:                                                   │
│ 1. ✅ Validar e Encerrar ─────────────┐                            │
│ 2. ↶ Devolver à Secretaria ───────────┼─────────────┐              │
└─────────────────────────────────────────────────────────────────────┘
                                         │            │
                   ┌─────────────────────┘            │
                   ▼                                  ▼
┌──────────────────────────────────┐  ┌──────────────────────────────┐
│ ✅ VALIDAR E ENCERRAR            │  │ ↶ DEVOLVER À SECRETARIA      │
│                                  │  │                              │
│ Confirmação:                     │  │ ╔══════════════════════════╗ │
│ ✓ Resposta selecionada           │  │ ║ Modal de Devolução       ║ │
│ ✓ Cidadão será notificado        │  │ ╠══════════════════════════╣ │
│                                  │  │ ║ Motivo:                  ║ │
│ [Confirmar Encerramento]         │  │ ║ [Selecione...]▼          ║ │
│ [Cancelar]                       │  │ ║                          ║ │
└──────────────────────────────────┘  │ ║ • Foto inadequada        ║ │
         │                            │ ║ • Serviço incompleto     ║ │
         ▼                            │ ║ • Fora do padrão         ║ │
┌──────────────────────────────────┐  │ ║ • Local errado           ║ │
│ 🎉 PROTOCOLO ENCERRADO!          │  │ ║ • Outro                  ║ │
│                                  │  │ ║                          ║ │
│ ✓ Status atualizado              │  │ ║ Justificativa:           ║ │
│ ✓ Cidadão notificado             │  │ ║ [___________________]    ║ │
│ ✓ Métricas atualizadas           │  │ ║                          ║ │
│                                  │  │ ║ [Cancelar] [Confirmar]   ║ │
│ [Voltar à Mesa]                  │  │ ╚══════════════════════════╝ │
└──────────────────────────────────┘  └──────────────────────────────┘
         │                                         │
         └─────────────────┬───────────────────────┘
                           ▼
          ┌────────────────────────────────┐
          │ 📋 VOLTA À MESA DE TRABALHO    │
          │    (Atualizada)                │
          └────────────────────────────────┘
```

---

## 🎯 FLUXO DE DESPACHO (Scatter-Gather)

```
┌─────────────────────────────────────────────────────────────────┐
│ MESA DE TRABALHO                                                │
│                                                                 │
│ ┌─────────────────────┐                                         │
│ │ PROT-2024-050       │                                         │
│ │ Buraco na Via       │                                         │
│ │ [Status: NOVO]      │                                         │
│ └─────────────────────┘                                         │
│         │                                                       │
│         │ [Botão: 📤 Despachar]                                 │
│         ▼                                                       │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🔀 MODAL: DESPACHAR PROTOCOLO (Scatter)                         │
│                                                                 │
│ Unidades Selecionadas:                                          │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ ✅ Secretaria de Obras                                     │  │
│ │    Instrução: "Realizar reparo emergencial..."            │  │
│ │    Prazo: [14/11/2024 18:00]                              │  │
│ │    Prioridade: [Alta ▼]                                   │  │
│ ├───────────────────────────────────────────────────────────┤  │
│ │ ✅ Defesa Civil                                            │  │
│ │    Instrução: "Avaliar riscos estruturais..."            │  │
│ │    Prazo: [13/11/2024 14:00]                              │  │
│ │    Prioridade: [Crítica ▼]                                │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│ [+ Adicionar Unidade] [Confirmar Despacho]                     │
└─────────────────────────────────────────────────────────────────┘
         │
         │ [Confirmar]
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 📤 PROTOCOLO DESPACHADO (Scatter)                               │
│                                                                 │
│ PROT-2024-050 fragmentado em:                                   │
│                                                                 │
│ ┌─────────────────┐  ┌─────────────────┐                       │
│ │ OS-2024-050-01  │  │ OS-2024-050-02  │                       │
│ │ → Obras         │  │ → Defesa Civil  │                       │
│ │ Status: Pendente│  │ Status: Pendente│                       │
│ └─────────────────┘  └─────────────────┘                       │
│         │                     │                                 │
│         │                     │                                 │
│         ▼                     ▼                                 │
│ [Equipe trabalha...]  [Equipe trabalha...]                      │
│         │                     │                                 │
│         ▼                     ▼                                 │
│ [Obras: Concluído]    [DC: Concluído]                           │
│         │                     │                                 │
│         └──────────┬──────────┘                                 │
│                    │                                            │
│                    ▼                                            │
│         ┌──────────────────────┐                                │
│         │ GATHER (Consolidação)│                                │
│         │ Status: Aguardando   │                                │
│         │ Revisão da Ouvidoria │                                │
│         └──────────────────────┘                                │
│                    │                                            │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 DETALHES DO PROTOCOLO                                        │
│    (Visão 360º)                                                 │
│                                                                 │
│ Timeline de Ordens:                                             │
│ ✅ Secretaria de Obras - Concluído                              │
│ ✅ Defesa Civil - Concluído                                     │
│                                                                 │
│ Ações:                                                          │
│ [✅ Validar e Encerrar] ← Gestor da Ouvidoria decide aqui      │
│ [↶ Devolver]                                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 CICLO COMPLETO DE UM PROTOCOLO

```
    ┌──────────────┐
    │   CIDADÃO    │
    │  Abre Chamado│
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Chat com IA │
    │ Coleta Dados │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────┐
    │ PROTOCOLO CRIADO│
    │ Status: NOVO    │
    └──────┬──────────┘
           │
           ▼
    ┌──────────────────────┐
    │ MESA DE TRABALHO     │ ← Gestor visualiza
    │ (Kanban/Lista)       │
    └──────┬───────────────┘
           │
           │ [Despachar]
           ▼
    ┌──────────────────────┐
    │ SCATTER (Fragmentar) │
    │ → Obras              │
    │ → Defesa Civil       │
    │ → Iluminação         │
    └──────┬───────────────┘
           │
           │ [Equipes trabalham]
           ▼
    ┌──────────────────────┐
    │ GATHER (Consolidar)  │
    │ Status: Aguardando   │
    │ Revisão              │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ DETALHES 360º        │
    │ Gestor Analisa:      │
    │ • Chat auditoria     │
    │ • Dados coletados    │
    │ • Fotos execução     │
    │ • Timeline ordens    │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ DECISÃO DO GESTOR    │
    ├──────────┬───────────┤
    │ Validar? │ Devolver? │
    └──────────┴───────────┘
           │         │
           │         └──> [Volta para Secretaria]
           │
           ▼
    ┌──────────────────────┐
    │ PROTOCOLO ENCERRADO  │
    │ Cidadão notificado   │
    └──────────────────────┘
```

---

## 🎮 ATALHOS E DICAS DE USO

### Mesa de Trabalho:

**Teclado:**
- `K` → Alterna para Kanban
- `L` → Alterna para Lista
- `/` → Foca na busca
- `ESC` → Limpa filtros

**Mouse:**
- Clicar em card → Abre detalhes
- Arrastar card → Muda status (Kanban)
- Duplo-clique → Edição rápida

### Detalhes do Protocolo:

**Teclado:**
- `←` → Volta para Mesa
- `V` → Validar e encerrar
- `D` → Devolver
- `E` → Editar
- `R` → Relatório

**Mouse:**
- Clicar em foto → Abre em nova aba
- Scroll → Header sticky acompanha
- Hover em ordem → Destaca na timeline

---

## 📱 NAVEGAÇÃO MOBILE (Futura)

```
┌─────────────────┐
│ ☰ Menu          │
├─────────────────┤
│ 🏠 Dashboard    │
│ 📋 Protocolos   │
│ 📊 Relatórios   │
│ ⚙️ Config       │
│ 👤 Perfil       │
│ 🚪 Sair         │
└─────────────────┘
```

---

## 🎯 CONCLUSÃO

O fluxo de navegação está **completo** e **intuitivo**:

1. ✅ Login simples e direto
2. ✅ Dashboard com visão geral
3. ✅ Mesa de Trabalho (hub central)
4. ✅ Detalhes 360º (auditoria completa)
5. ✅ Scatter-Gather visível
6. ✅ Validação inteligente
7. ✅ Feedback imediato

**Navegação Clara:** Máximo 3 cliques para qualquer ação!

---

*Fluxo projetado para produtividade máxima do servidor público*
