# 🚀 QUICK START - Ouv.IA

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Instalar e Rodar

```bash
# 1. Clonar o repositório
git clone [URL_DO_REPO]
cd ouve

# 2. Instalar dependências
npm install

# 3. Rodar em desenvolvimento
npm run dev

# 4. Abrir no navegador
# http://localhost:3002
```

**Pronto!** O projeto está rodando.

---

## 🗺️ Onde Ir Agora?

### PWA (Cidadão):
```
http://localhost:3002/app/dashboard
```
- Interface mobile-first
- Bottom navigation
- 6 telas disponíveis

### Backoffice (Gestor):
```
http://localhost:3002/backoffice/mesa-trabalho
```
- Interface desktop-first
- Sidebar lateral
- 2 telas principais

---

## 📂 Estrutura Rápida

```
src/
├── layouts/
│   ├── PwaLayout.vue           ← Layout mobile (cidadão)
│   └── BackofficeLayout.vue    ← Layout desktop (gestor)
│
├── views/
│   ├── pwa/                    ← 6 views do cidadão
│   └── backoffice/             ← 2 views do gestor
│       ├── MesaTrabalhoView.vue       ← Kanban + Lista
│       └── DetalhesProtocoloInternoView.vue  ← Visão 360º
│
└── components/
    ├── pwa/                    ← Componentes cidadão
    ├── backoffice/             ← Componentes gestor
    └── shared/                 ← Componentes compartilhados
```

---

## 🎯 Rotas Principais

### PWA:
- `/login` - Login
- `/app/dashboard` - Dashboard cidadão
- `/app/nova-solicitacao` - Nova solicitação
- `/app/protocolo/:id` - Detalhes protocolo (cidadão)

### Backoffice:
- `/backoffice/mesa-trabalho` - Mesa de trabalho (Kanban/Lista)
- `/backoffice/protocolo/:id` - Detalhes protocolo (gestor)

---

## 🛠️ Scripts Úteis

```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Preview da build
npm run preview

# Lint (futuro)
npm run lint

# Testes (futuro)
npm run test
```

---

## 📚 Documentação

### Começar por:

**Para Desenvolvedores:**
1. `README.md` - Visão geral
2. `docs/knowledge/ARCHITECTURE.md` - Arquitetura
3. `docs/knowledge/MESA_TRABALHO_README.md` - Mesa de Trabalho
4. `docs/knowledge/DETALHES_PROTOCOLO_INTERNO.md` - Detalhes 360º

**Para Gestores:**
1. `docs/knowledge/GUIA_RAPIDO_PROTOCOLO_INTERNO.md` - Como usar

**Para Todos:**
1. `DOCUMENTACAO_INDEX.md` - Índice completo

---

## 🎨 Design System

### Cores Principais:
```css
primary: #3b82f6    (Azul)
success: #10b981    (Verde)
warning: #f59e0b    (Amarelo)
danger: #ef4444     (Vermelho)
```

### Dark Mode:
Ative no canto superior direito de qualquer layout.

### Componentes Compartilhados:
- `StatusBadge.vue` - Badges de status
- `ThemeToggle.vue` - Toggle dark mode
- `EmptyState.vue` - Estados vazios
- `LoadingSpinner.vue` - Loading

---

## 🔧 Configuração

### Tailwind:
```javascript
// tailwind.config.js
// Já configurado com cores customizadas
```

### Vite:
```javascript
// vite.config.js
// Já configurado com PWA e aliases
```

### Vue Router:
```javascript
// src/router/index.js
// Rotas aninhadas já configuradas
```

---

## 💡 Dicas de Desenvolvimento

### 1. Componentes:
- Mantê-los < 300 linhas
- Usar Composition API
- Props tipadas (JSDoc ou TypeScript futuro)

### 2. Imports:
```javascript
// Use alias @/ para imports absolutos
import Component from '@/components/shared/Component.vue'
```

### 3. Rotas:
```javascript
// PWA
router.push({ name: 'pwa-dashboard' })

// Backoffice
router.push({ name: 'backoffice-mesa-trabalho' })
```

### 4. Dark Mode:
```html
<!-- Use classes dark: -->
<div class="bg-white dark:bg-gray-800">
  <p class="text-gray-900 dark:text-white">
    Texto
  </p>
</div>
```

---

## 🐛 Troubleshooting

### Build Error?
```bash
# Limpar cache e reinstalar
rm -rf node_modules dist .vite
npm install
npm run build
```

### Import Error?
```javascript
// Use @ para imports absolutos
import X from '@/components/...'

// NÃO use caminhos relativos longos
import X from '../../../components/...'
```

### Rota não encontrada?
```javascript
// Verifique se está registrada em:
src/router/index.js
```

### Dark mode não funciona?
```javascript
// Verifique se tem ThemeToggle no layout
// Verifique classes dark: nos componentes
```

---

## 🎯 Tarefas Comuns

### Criar um novo componente Backoffice:

1. Criar em `src/components/backoffice/MeuComponente.vue`
2. Usar `<script setup>`
3. Adicionar Heroicons se necessário
4. Suportar dark mode
5. Documentar props/emits

### Criar uma nova view:

1. Criar em `src/views/backoffice/MinhaView.vue`
2. Registrar rota em `src/router/index.js`
3. Adicionar link no layout
4. Testar navegação

### Adicionar um filtro na Mesa:

1. Abrir `src/views/backoffice/MesaTrabalhoView.vue`
2. Adicionar estado reativo para o filtro
3. Adicionar computed para filtrar dados
4. Adicionar UI (botão ou select)

---

## 📊 Status do Projeto

### ✅ Completo:
- PWA Cidadão (Fase 1)
- Backoffice Gestor (Fase 2 - Sprint 2)
- Arquitetura refatorada
- Documentação completa

### 🔄 Em Progresso:
- Integração com backend (Sprint 3)

### 📋 Planejado:
- Dashboard Backoffice
- Relatórios
- Notificações em tempo real

---

## 🔗 Links Importantes

### Documentação:
- [Índice Completo](DOCUMENTACAO_INDEX.md)
- [Resumo Sprint 2 (arquivo)](docs/archive/RESUMO_SPRINT2_BACKOFFICE.md)
- [Release Notes](RELEASE_NOTES_SPRINT2.md)

### Tecnologias:
- [Vue 3](https://vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Pinia](https://pinia.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Vite](https://vitejs.dev/)
- [Heroicons](https://heroicons.com/)

---

## 🆘 Precisa de Ajuda?

### Por funcionalidade:

**Mesa de Trabalho?**
→ `docs/knowledge/MESA_TRABALHO_README.md`

**Detalhes do Protocolo?**
→ `docs/knowledge/DETALHES_PROTOCOLO_INTERNO.md`

**Arquitetura?**
→ `docs/knowledge/ARCHITECTURE.md`

**Tudo?**
→ `DOCUMENTACAO_INDEX.md`

---

## 🎓 Learning Path (3 dias)

### Dia 1: Setup e Exploração
- ✅ Instalar e rodar o projeto
- ✅ Navegar pelas rotas PWA
- ✅ Navegar pelas rotas Backoffice
- ✅ Ler `README.md`
- ✅ Explorar estrutura de diretórios

### Dia 2: PWA (Cidadão)
- ✅ Estudar `PwaLayout.vue`
- ✅ Estudar views em `src/views/pwa/`
- ✅ Entender fluxo de criação de solicitação
- ✅ Analisar componentes compartilhados

### Dia 3: Backoffice (Gestor)
- ✅ Estudar `BackofficeLayout.vue`
- ✅ Estudar `MesaTrabalhoView.vue`
- ✅ Estudar `DetalhesProtocoloInternoView.vue`
- ✅ Ler `docs/knowledge/DETALHES_PROTOCOLO_INTERNO.md`
- ✅ Experimentar criar um componente

### Dia 4+: Desenvolvimento
- ✅ Pegar uma task
- ✅ Implementar
- ✅ Testar
- ✅ Documentar
- ✅ Pull request

---

## ✅ Checklist Primeiro Dia

- [ ] Node.js instalado (v18+)
- [ ] npm install sem erros
- [ ] npm run dev funcionando
- [ ] Abriu http://localhost:3002
- [ ] Navegou para `/app/dashboard`
- [ ] Navegou para `/backoffice/mesa-trabalho`
- [ ] Testou dark mode
- [ ] Leu README.md
- [ ] Leu QUICK_START.md (este arquivo)
- [ ] Escolheu próximo documento para ler

---

## 🎉 Pronto para Começar!

Você agora tem tudo para começar a desenvolver no projeto Ouv.IA.

### Próximo passo:
1. Explore as rotas no navegador
2. Leia a documentação relevante
3. Escolha uma task
4. Comece a codar!

---

**💡 Dica:** Sempre consulte `DOCUMENTACAO_INDEX.md` quando tiver dúvidas.

**📚 Documentação completa:** 9 documentos | ~3.550 linhas

**🚀 Boa sorte e bom código!**
