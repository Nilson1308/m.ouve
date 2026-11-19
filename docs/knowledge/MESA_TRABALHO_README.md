# 📋 Mesa de Trabalho - Backoffice Ouv.IA

## 🎯 Visão Geral

A **Mesa de Trabalho** é o painel principal de gestão de protocolos para servidores públicos no sistema Ouv.IA. Foi desenvolvida com foco em **clareza visual**, **produtividade** e **inovação arquitetural** através do sistema Scatter-Gather.

---

## 📁 Estrutura de Arquivos Criados

```
src/
├── views/
│   └── MesaTrabalhoView.vue         # View principal da Mesa de Trabalho
│
└── components/
    └── backoffice/
        ├── BoardKanban.vue          # Visualização Kanban (colunas por status)
        ├── TabelaProtocolos.vue     # Visualização em Lista/Tabela densa
        ├── CardProtocolo.vue        # Card individual de protocolo (usado no Kanban)
        └── DespacharProtocolo.vue   # Modal Scatter-Gather (multi-setorial)
```

---

## ✨ Funcionalidades Implementadas

### 1️⃣ **Layout Principal (MesaTrabalhoView.vue)**

#### Header Sticky com:
- 🔍 **Busca global** (protocolo, endereço, cidadão)
- 🔴 **Filtros rápidos**: SLA Vencido e Urgentes (com contadores)
- 🎛️ **Toggle de visualização**: Kanban ↔️ Lista
- 📊 **Estatísticas em tempo real**: Total, Em Andamento, SLA Vencido, Concluídos Hoje

#### Recursos:
- Filtros ativos com badges removíveis
- Dados mock complexos (6 protocolos de demonstração)
- Transições suaves entre visualizações
- Responsivo (mobile-first)

---

### 2️⃣ **Visualização Kanban (BoardKanban.vue)**

#### Colunas por Status:
- 🆕 **Novos/Triagem** (triagem_ia, validacao)
- ⚙️ **Em Andamento** (em_deslocamento, em_execucao)
- ⏳ **Aguardando Retorno**
- ✅ **Concluídos**

#### Cards do Kanban (CardProtocolo.vue):
- 📌 Número do protocolo destacado
- 🏷️ Badge de status com ícone
- 📍 Endereço resumido
- 👤 Avatar/Iniciais do responsável
- 📊 **Barra de SLA** (Verde/Amarelo/Vermelho)
- ⚡ Indicador de urgência
- 🔖 Tags e anexos
- 🎯 Ações: Despachar e Ver Detalhes

#### Recursos UX:
- Borda lateral colorida por SLA
- Animação de hover (elevação suave)
- Empty states elegantes
- Scroll customizado

---

### 3️⃣ **Visualização em Lista (TabelaProtocolos.vue)**

#### Recursos:
- 📋 Tabela densa e limpa
- 🔄 **Ordenação clicável** em todos os cabeçalhos
- 📄 **Paginação** (10 itens por página)
- 🎨 Indicador visual de SLA (barra lateral)
- 👁️ Hover effect nas linhas
- 📱 Responsiva com scroll horizontal

#### Colunas:
1. Protocolo (número + data)
2. Serviço/Solicitação (ícone + descrição)
3. Cidadão (nome + telefone)
4. Status (badge)
5. Urgência (badge colorido)
6. SLA (texto + barra de progresso)
7. Responsável (avatar + nome)
8. Ações (despachar + detalhes)

---

### 4️⃣ **🌟 Interface Scatter-Gather (DespacharProtocolo.vue)**

> **A Grande Inovação Arquitetural do Sistema**

#### O que é Scatter-Gather?
Sistema que permite **fragmentar um protocolo** em múltiplas **Ordens de Serviço** para diferentes secretarias/departamentos, cada uma com:
- ✍️ Instrução específica personalizada
- 📅 Prazo independente
- 🎯 Prioridade própria

#### UX Destacada:
1. **Modal amplo e elegante** com header gradiente
2. **Card do Protocolo Pai** sempre visível no topo
3. **Alert informativo** explicando o conceito Scatter-Gather
4. **Lista dinâmica de Ordens**:
   - Adicionar/remover unidades
   - Numeração visual clara
   - Validação de duplicatas
   - Animações de entrada/saída
5. **Formulário inteligente**:
   - Select de unidades (não permite repetição)
   - Textarea para instruções específicas
   - Date picker (prazo mínimo = hoje)
   - Select de prioridade
6. **Validação em tempo real**
7. **Observações gerais** (opcional, compartilhadas)

#### Unidades Disponíveis (Mock):
- Secretaria de Obras Públicas
- Obras - Equipe de Pavimentação
- Defesa Civil
- Departamento de Trânsito
- Iluminação Pública
- Secretaria de Limpeza Urbana
- Secretaria do Meio Ambiente
- Vigilância Sanitária
- Zeladoria Urbana

---

## 🎨 Design System Utilizado

### Cores Semânticas:
- ✅ **Verde** (success): SLA OK, concluído
- ⚠️ **Amarelo** (warning): SLA próximo, urgência média
- 🔴 **Vermelho** (danger): SLA vencido, urgência alta
- 🔵 **Azul** (primary): ações principais, triagem
- 🟣 **Roxo**: validação, análise

### Componentes Reutilizados:
- `StatusBadge.vue` - Badges de status
- `useStatusColors.js` - Composable de cores

### Tailwind Classes:
- `.card` - Cards com sombra e arredondamento
- `.btn-primary` / `.btn-secondary` - Botões estilizados
- `.badge` - Badges diversos
- `.alert-info` - Alertas informativos
- `.rounded-card`, `.rounded-button`, `.rounded-modal` - Bordas personalizadas
- `.shadow-card-hover` - Sombra de elevação

---

## 🚀 Como Acessar

### Rota Criada:
```
/backoffice/mesa-trabalho
```

### Navegação:
Para adicionar um link de navegação, edite o menu/sidebar e inclua:

```vue
<router-link 
  to="/backoffice/mesa-trabalho"
  class="nav-item"
>
  <ClipboardDocumentListIcon class="w-5 h-5" />
  Mesa de Trabalho
</router-link>
```

---

## 📊 Dados Mock

### Estrutura de um Protocolo:
```javascript
{
  id: 'PROT-2024-001',
  numero: '001/2024',
  servico: 'Buraco na Via',
  categoria: 'via_publica',
  endereco: 'Av. Principal, 500',
  bairro: 'Centro',
  cidadao: {
    nome: 'João Silva',
    telefone: '(11) 98765-4321'
  },
  status: 'triagem_ia',
  urgencia: 'alta',
  sla: {
    prazo: '2024-11-15T18:00:00',
    vencido: false,
    horasRestantes: 48
  },
  criadoEm: '2024-11-13T09:00:00',
  responsavel: {
    nome: 'Equipe Norte',
    iniciais: 'EN'
  },
  departamento: 'Obras',
  tags: ['via', 'risco'],
  temAnexos: true,
  temLocalizacao: true
}
```

---

## 🎭 Animações e Transições

### Implementadas:
- ✨ Fade entre Kanban ↔️ Lista
- 🎬 Slide-up no modal
- 📦 Animação de lista (ordens de serviço)
- 🎯 Hover effects nos cards
- 📈 Transição da barra de SLA

### Duração:
- Fade: 300ms
- Slide: 300-400ms
- Hover: 200ms

---

## 🔄 Próximos Passos (Integração Backend)

### APIs Necessárias:
1. **GET /api/backoffice/protocolos**
   - Listar protocolos com filtros
   - Paginação server-side

2. **GET /api/backoffice/protocolos/:id**
   - Detalhes de um protocolo

3. **POST /api/backoffice/protocolos/:id/despachar**
   - Criar scatter-gather
   - Body: array de ordens de serviço

4. **GET /api/backoffice/unidades**
   - Listar secretarias/departamentos disponíveis

### Store Pinia (Futuro):
```javascript
// stores/backoffice.js
export const useBackofficeStore = defineStore('backoffice', {
  state: () => ({
    protocolos: [],
    filtros: {},
    loading: false
  }),
  actions: {
    async buscarProtocolos() { },
    async despacharScatterGather(protocoloId, ordens) { }
  }
})
```

---

## 📱 Responsividade

### Breakpoints:
- **Mobile** (< 640px): Cards empilhados, header simplificado
- **Tablet** (640px - 1024px): 2 colunas no Kanban
- **Desktop** (> 1024px): 4 colunas completas

### Funciona em:
- ✅ Smartphones
- ✅ Tablets
- ✅ Desktops
- ✅ Ultrawide monitors

---

## ♿ Acessibilidade

### Recursos:
- 🌓 **Dark Mode** completo
- 🔆 **High Contrast Mode** (Gov.br)
- ⌨️ Navegação por teclado
- 📢 ARIA labels
- 🎨 Contraste WCAG AA

---

## 🎯 Status e Urgência

### Status do Protocolo:
- `triagem_ia` - Triagem IA 🤖
- `validacao` - Em Validação 👁️
- `aguardando_equipe` - Aguardando Equipe ⏳
- `em_deslocamento` - Equipe em Deslocamento 🚚
- `em_execucao` - Em Execução 🔧
- `aguardando_retorno` - Aguardando Retorno 📬
- `concluido` - Concluído ✅
- `nao_procedente` - Não Procedente ❌

### Níveis de Urgência:
- `baixa` 🟢
- `media` 🟡
- `alta` 🔴
- `critica` 🔴💥 (pulsante)

---

## 🐛 Debugging

### Console Logs:
- `Mesa de Trabalho carregada` - ao montar view
- `Despachar protocolo:` - ao confirmar scatter-gather

### Erros Comuns:
1. **Componente não encontrado**: Verifique imports
2. **Ícones não aparecem**: Importe do `@heroicons/vue/24/outline`
3. **Estilos quebrados**: Rode `npm run dev` novamente

---

## 📚 Referências Técnicas

### Tecnologias:
- **Vue 3** (Composition API)
- **Pinia** (gerenciamento de estado - futuro)
- **Vue Router** (navegação)
- **Tailwind CSS** (estilização)
- **Heroicons** (ícones)

### Padrões:
- Componentes modulares
- Separation of Concerns
- Mobile-first design
- Acessibilidade em primeiro lugar

---

## 💡 Dicas de Desenvolvimento

### Para adicionar novos filtros:
1. Adicione estado em `filtros.ref()`
2. Crie lógica em `protocolosFiltrados.computed()`
3. Adicione botão no header

### Para adicionar novas colunas no Kanban:
1. Edite `BoardKanban.vue`
2. Ajuste grid: `grid-cols-5` (exemplo)
3. Adicione nova chamada `protocolosPorStatus()`

### Para customizar o Scatter-Gather:
1. Edite `DespacharProtocolo.vue`
2. Ajuste `unidadesDisponiveis.ref()`
3. Modifique estrutura de `ordem` conforme necessário

---

## ✅ Checklist de Qualidade

- [x] Componentes modulares e reutilizáveis
- [x] Design system seguido à risca
- [x] Responsivo (mobile, tablet, desktop)
- [x] Dark mode completo
- [x] Transições suaves
- [x] Código comentado e limpo
- [x] Dados mock realistas
- [x] UX intuitiva e clara
- [x] Acessibilidade (ARIA, contraste)
- [x] Performance otimizada

---

## 🎉 Resultado Final

A **Mesa de Trabalho** entrega uma experiência de gestão de protocolos **profissional**, **moderna** e **inovadora**, com destaque especial para o **sistema Scatter-Gather** que permite fragmentação inteligente de tarefas entre múltiplos departamentos.

### O "Uau" da Interface:
> *"Quando um servidor clica em 'Despachar', ele vê visualmente como pode dividir uma demanda complexa em múltiplas ordens de serviço específicas, cada uma com seu próprio prazo e instrução. É a materialização do conceito scatter-gather em uma UX elegante."*

---

**Desenvolvido com ❤️ para a Fase 2 do Ouv.IA**
