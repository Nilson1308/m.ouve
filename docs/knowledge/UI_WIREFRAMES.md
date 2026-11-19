# M.Ouve — UI Wireframes

Wireframes conceituais das principais telas do sistema.

---

## 📱 1. Login View

```
┌─────────────────────────────────────┐
│                                     │
│          ┌───────────┐              │
│          │    🏛️     │              │
│          └───────────┘              │
│                                     │
│            M.Ouve                   │
│   Ouvidoria · Mogi das Cruzes       │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║                               ║  │
│  ║      Bem-vindo(a)            ║  │
│  ║                               ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │  ✓  Entrar com Gov.br   │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ║                               ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │  🏢  SSO Municipal       │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ║                               ║  │
│  ║  ─────────  ou  ─────────    ║  │
│  ║                               ║  │
│  ║  Criar conta / Login padrão  ║  │
│  ║                               ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
└─────────────────────────────────────┘
```

**Com formulário expandido:**

```
┌─────────────────────────────────────┐
│  ╔═══════════════════════════════╗  │
│  ║                               ║  │
│  ║  Nome completo *              ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │                         │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ║                               ║  │
│  ║  CPF *                        ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │ 000.000.000-00          │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ║                               ║  │
│  ║  E-mail *                     ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │                         │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ║                               ║  │
│  ║  Telefone                     ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │ (00) 00000-0000         │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ║                               ║  │
│  ║  ┌─────────────────────────┐ ║  │
│  ║  │      Entrar             │ ║  │
│  ║  └─────────────────────────┘ ║  │
│  ╚═══════════════════════════════╝  │
└─────────────────────────────────────┘
```

---

## 📱 2. Dashboard View

```
┌─────────────────────────────────────┐
│ M.Ouve                       [🚪]   │
│ Olá, João da Silva                  │
├─────────────────────────────────────┤
│                                     │
│  Resumo                             │
│                                     │
│  ╔═══════════╗  ╔═══════════╗      │
│  ║     3     ║  ║     12    ║      │
│  ║           ║  ║           ║      │
│  ║   Em      ║  ║ Resolvidos║      │
│  ║ Andamento ║  ║           ║      │
│  ╚═══════════╝  ╚═══════════╝      │
│                                     │
│  Meus Protocolos                    │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ PROT-2024-001     [Em Análise]║  │
│  ║ 💡 Iluminação Pública          ║  │
│  ║                                ║  │
│  ║ Poste de luz queimado na      ║  │
│  ║ Rua das Flores, 123           ║  │
│  ║                                ║  │
│  ║ Hoje • 📍 📎                   ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ PROT-2024-002  [🚗 Em Deslocam]║  │
│  ║ 🛣️ Via Pública                 ║  │
│  ║                                ║  │
│  ║ Buraco grande na Avenida      ║  │
│  ║ Principal                     ║  │
│  ║                                ║  │
│  ║ 2 dias atrás • 📍 📎           ║  │
│  ║ 👥 Equipe de Pavimentação      ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│                         ┌─────────┐ │
│                         │    +    │ │
│                         └─────────┘ │
│                        (Floating)   │
└─────────────────────────────────────┘
```

---

## 📱 3. Nova Solicitação View

```
┌─────────────────────────────────────┐
│ [←]  Nova Solicitação               │
├─────────────────────────────────────┤
│                                     │
│      Como podemos ajudar?           │
│                                     │
│  Escolha o tipo de solicitação      │
│                                     │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ 💬                            ║  │
│  ║                               ║  │
│  ║ Ouvidoria Institucional       ║  │
│  ║                               ║  │
│  ║ Denúncias, reclamações,       ║  │
│  ║ sugestões ou elogios sobre    ║  │
│  ║ serviços públicos             ║  │
│  ║                               ║  │
│  ║ [Denúncia][Reclamação]        ║  │
│  ║ [Sugestão][Elogio]         →  ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ 🏛️                            ║  │
│  ║                               ║  │
│  ║ Zeladoria Urbana              ║  │
│  ║                               ║  │
│  ║ Problemas com infraestrutura, ║  │
│  ║ iluminação, vias públicas e   ║  │
│  ║ serviços urbanos              ║  │
│  ║                               ║  │
│  ║ [Buracos][Iluminação]         ║  │
│  ║ [Limpeza][Calçadas]        →  ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ ℹ️  Importante                 ║  │
│  ║                               ║  │
│  ║ Todas as solicitações são     ║  │
│  ║ registradas e você receberá   ║  │
│  ║ um número de protocolo...     ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
└─────────────────────────────────────┘
```

---

## 📱 4. Formulário Ouvidoria

```
┌─────────────────────────────────────┐
│ [←]  Ouvidoria Institucional        │
│      Registrar manifestação         │
├─────────────────────────────────────┤
│                                     │
│  Tipo de Manifestação *             │
│                                     │
│  ┌─────────┐  ┌─────────┐          │
│  │   🚨    │  │   😤    │          │
│  │ Denúncia│  │Reclamação│         │
│  └─────────┘  └─────────┘          │
│                                     │
│  ┌─────────┐  ┌─────────┐          │
│  │   💡    │  │   👏    │          │
│  │ Sugestão│  │  Elogio │          │
│  └─────────┘  └─────────┘          │
│                                     │
│  Categoria *                        │
│  ┌─────────────────────────────┐   │
│  │ Saúde                    ▼ │   │
│  └─────────────────────────────┘   │
│                                     │
│  Descrição detalhada *              │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │                             │   │
│  │                             │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│  0 / 1000 caracteres                │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Enviar Manifestação         │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

---

## 📱 5. Formulário Zeladoria (Assistente)

```
┌─────────────────────────────────────┐
│ [←]  Zeladoria Urbana               │
│      Relatar problema urbano        │
├─────────────────────────────────────┤
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Conte-nos o que aconteceu     ║  │
│  ║                               ║  │
│  ║ ┌─────────────────────────┐  ║  │
│  ║ │ Há um buraco grande na  │  ║  │
│  ║ │ Rua das Flores...       │  ║  │
│  ║ │                         │  ║  │
│  ║ │                      🎙️  │  ║  │
│  ║ └─────────────────────────┘  ║  │
│  ║                               ║  │
│  ║ ┌─────────────────────────┐  ║  │
│  ║ │ 💡 Assistente IA detectou:│  ║  │
│  ║ │                          │  ║  │
│  ║ │ ✓ Categoria: Via Pública │  ║  │
│  ║ │ ✓ Endereço: Rua das...   │  ║  │
│  ║ └─────────────────────────┘  ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Categoria do Problema         ║  │
│  ║ ┌─────────────────────────┐  ║  │
│  ║ │ 🛣️ Via Pública         ▼│  ║  │
│  ║ └─────────────────────────┘  ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Localização      [📍 Usar GPS]║  │
│  ║ ┌─────────────────────────┐  ║  │
│  ║ │ Rua das Flores, 123     │  ║  │
│  ║ └─────────────────────────┘  ║  │
│  ║                               ║  │
│  ║ ┌─────────────────────────┐  ║  │
│  ║ │      [ Mapa ]           │  ║  │
│  ║ │         📍              │  ║  │
│  ║ │   Lat: -23.5505         │  ║  │
│  ║ │   Lng: -46.6333         │  ║  │
│  ║ └─────────────────────────┘  ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Fotos do Problema             ║  │
│  ║                               ║  │
│  ║ ┌──────┐ ┌──────┐ ┌──────┐   ║  │
│  ║ │ 📷 1 │ │ 📷 2 │ │      │   ║  │
│  ║ └──────┘ └──────┘ └──────┘   ║  │
│  ║                               ║  │
│  ║ ┌───────┐  ┌───────┐         ║  │
│  ║ │📷 Foto│  │🖼️ Galeria│       ║  │
│  ║ └───────┘  └───────┘         ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
├─────────────────────────────────────┤
│ ┌───────────────────────────────┐   │
│ │   Enviar Solicitação          │   │
│ └───────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 📱 6. Modal de Sucesso

```
┌─────────────────────────────────────┐
│                                     │
│  ╔═════════════════════════════╗   │
│  ║                             ║   │
│  ║        ┌─────────┐          ║   │
│  ║        │    ✓    │          ║   │
│  ║        └─────────┘          ║   │
│  ║                             ║   │
│  ║  Solicitação Enviada!       ║   │
│  ║                             ║   │
│  ║  Seu protocolo foi          ║   │
│  ║  registrado com sucesso     ║   │
│  ║                             ║   │
│  ║  ┌─────────────────────┐   ║   │
│  ║  │ Número do Protocolo │   ║   │
│  ║  │                     │   ║   │
│  ║  │   PROT-2024-042     │   ║   │
│  ║  └─────────────────────┘   ║   │
│  ║                             ║   │
│  ║  ┌─────────────────────┐   ║   │
│  ║  │ Voltar ao Dashboard │   ║   │
│  ║  └─────────────────────┘   ║   │
│  ║                             ║   │
│  ╚═════════════════════════════╝   │
│                                     │
└─────────────────────────────────────┘
```

---

## 📱 7. Detalhes do Protocolo

```
┌─────────────────────────────────────┐
│ [←]  Detalhes do Protocolo          │
├─────────────────────────────────────┤
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Número do Protocolo           ║  │
│  ║                               ║  │
│  ║ PROT-2024-001  [Em Análise]   ║  │
│  ║                               ║  │
│  ║ Abertura: 05/11/2024 10:30    ║  │
│  ║ Atualização: 05/11/2024 10:30 ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ 💡  Zeladoria Urbana          ║  │
│  ║     Iluminação Pública        ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Descrição                     ║  │
│  ║                               ║  │
│  ║ Poste de luz queimado na      ║  │
│  ║ Rua das Flores, 123. O poste  ║  │
│  ║ está sem iluminação há 3 dias ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Localização                   ║  │
│  ║ 📍 Rua das Flores, 123        ║  │
│  ║    Lat: -23.5505              ║  │
│  ║    Lng: -46.6333              ║  │
│  ║                               ║  │
│  ║ ┌─────────────────────────┐  ║  │
│  ║ │      [ Mapa ]           │  ║  │
│  ║ │         📍              │  ║  │
│  ║ └─────────────────────────┘  ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Fotos Anexadas                ║  │
│  ║                               ║  │
│  ║ ┌──────┐ ┌──────┐            ║  │
│  ║ │ 📷 1 │ │ 📷 2 │            ║  │
│  ║ └──────┘ └──────┘            ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Histórico                     ║  │
│  ║                               ║  │
│  ║ ● Protocolo criado            ║  │
│  ║ │ 05/11/2024 10:30            ║  │
│  ║ │                             ║  │
│  ║ ○ Em andamento                ║  │
│  ║ │ (aguardando análise)        ║  │
│  ║                               ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
└─────────────────────────────────────┘
```

**Com Equipe Designada:**

```
│  ╔═══════════════════════════════╗  │
│  ║ 👥 Equipe Responsável         ║  │
│  ║                               ║  │
│  ║    Equipe de Pavimentação     ║  │
│  ║    Norte                      ║  │
│  ╚═══════════════════════════════╝  │
│                                     │
│  ╔═══════════════════════════════╗  │
│  ║ Histórico                     ║  │
│  ║                               ║  │
│  ║ ● Protocolo criado            ║  │
│  ║ │ 05/11/2024 10:30            ║  │
│  ║ │                             ║  │
│  ║ ● Em andamento                ║  │
│  ║ │ Equipe designada e em       ║  │
│  ║ │ atendimento                 ║  │
│  ║ │ 08/11/2024 09:15            ║  │
│  ║ │                             ║  │
│  ║ ● Resolvido ✓                 ║  │
│  ║   09/11/2024 16:30            ║  │
│  ║                               ║  │
│  ╚═══════════════════════════════╝  │
```

---

## 🎨 Design Tokens

### Cores
```
Gov Blue Warm:   ████ #1351B4 (Primária)
Gov Blue Vivid:  ████ #155BCB
Gov Blue Deep:   ████ #0C326F
Gov Green Cool:  ████ #168821 (Sucesso)
Gov Yellow:      ████ #FFCD07 (Aviso)
Gray Light:      ████ #F8F8F8 (Background)
Gray Medium:     ████ #E5E5E5 (Borders)
Gray Dark:       ████ #333333 (Text)
```

### Espaçamentos
```
xs:  4px
sm:  8px
md:  16px
lg:  24px
xl:  32px
2xl: 48px
```

### Fontes
```
Família: Rawline, Roboto, system-ui, sans-serif
Tamanhos:
  - xs:   12px
  - sm:   14px
  - base: 16px
  - lg:   18px
  - xl:   20px
  - 2xl:  24px
  - 3xl:  30px
```

### Sombras
```
gov:    0 2px 8px rgba(0, 0, 0, 0.15)
gov-lg: 0 4px 16px rgba(0, 0, 0, 0.2)
```

### Bordas
```
Radius:
  - sm: 4px
  - md: 8px
  - lg: 12px
  - xl: 16px
  - 2xl: 24px
  - full: 9999px
```

---

## 📐 Breakpoints

```
Mobile:  < 640px   (base, mobile-first)
Tablet:  640px+    (sm:)
Laptop:  1024px+   (lg:)
Desktop: 1280px+   (xl:)
```

---

## ♿ Acessibilidade

### Touch Targets
```
Mínimo: 44x44px (iOS), 48x48px (Android)
Implementado: 48x48px em todos os botões
```

### Contraste
```
Texto normal:  4.5:1 (WCAG AA)
Texto grande:  3:1 (WCAG AA)
UI Elements:   3:1 (WCAG AA)

Todas as cores implementadas atendem WCAG AA
```

### Navegação por Teclado
```
Tab:        Próximo elemento
Shift+Tab:  Elemento anterior
Enter:      Ativar botão/link
Esc:        Fechar modal
```

---

Estes wireframes representam a estrutura visual das telas implementadas no M.Ouve. Para visualização interativa, rode o projeto: `npm run dev`
