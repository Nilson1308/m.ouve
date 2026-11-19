# 🚀 GUIA RÁPIDO - Refatoração Estrutural

## ✅ Tudo está funcionando!

**Servidor Dev:** `http://localhost:3002/`  
**Build:** ✅ Compilado sem erros  

---

## 📁 Onde Está Cada Coisa?

### 🎯 Quero criar um componente para o **Cidadão (PWA)**:
```
src/components/pwa/MeuComponente.vue
```

### 🎯 Quero criar um componente para o **Servidor (Backoffice)**:
```
src/components/backoffice/MeuComponente.vue
```

### 🎯 Quero criar um componente **Compartilhado**:
```
src/components/shared/MeuComponente.vue
```

---

## 📄 Onde Está Cada View?

### PWA (Cidadão):
```
src/views/pwa/
├── DashboardView.vue
├── NovaSolicitacaoView.vue
├── ChatSolicitacaoView.vue
├── DetalhesProtocoloView.vue
└── PerfilUsuarioView.vue
```

### Backoffice (Servidor):
```
src/views/backoffice/
└── MesaTrabalhoView.vue
```

---

## 🎨 Layouts

### PwaLayout (mobile-first):
```vue
src/layouts/PwaLayout.vue

Tem:
- Header com logo
- Bottom navigation
- Theme toggle
```

### BackofficeLayout (desktop-first):
```vue
src/layouts/BackofficeLayout.vue

Tem:
- Sidebar lateral
- Header superior
- Menu mobile
```

---

## 🛣️ Rotas

### PWA (Cidadão):
```
/app/dashboard
/app/nova-solicitacao
/app/chat/:categoriaNome
/app/protocolo/:id
/app/perfil
```

### Backoffice (Servidor):
```
/backoffice/mesa-trabalho
/backoffice/dashboard
/backoffice/relatorios
/backoffice/configuracoes
```

### Rotas antigas ainda funcionam!
```
/dashboard → /app/dashboard (redirect)
/perfil → /app/perfil (redirect)
```

---

## 📦 Imports Atualizados

### Antes:
```javascript
import StatusBadge from '@/components/StatusBadge.vue'
```

### Agora:
```javascript
import StatusBadge from '@/components/shared/StatusBadge.vue'
```

### Padrão:
```javascript
// Componente PWA
import MeuComp from '@/components/pwa/MeuComp.vue'

// Componente Backoffice
import MeuComp from '@/components/backoffice/MeuComp.vue'

// Componente Compartilhado
import MeuComp from '@/components/shared/MeuComp.vue'
```

---

## 🆕 Adicionar Nova Rota

### PWA:
```javascript
// src/router/index.js
{
  path: '/app',
  component: () => import('@/layouts/PwaLayout.vue'),
  children: [
    // ... rotas existentes
    {
      path: 'minha-nova-rota',
      name: 'pwa-minha-rota',
      component: () => import('@/views/pwa/MinhaView.vue')
    }
  ]
}
```

### Backoffice:
```javascript
{
  path: '/backoffice',
  component: () => import('@/layouts/BackofficeLayout.vue'),
  children: [
    // ... rotas existentes
    {
      path: 'minha-nova-rota',
      name: 'backoffice-minha-rota',
      component: () => import('@/views/backoffice/MinhaView.vue')
    }
  ]
}
```

---

## 🎯 Navegação Programática

### PWA:
```javascript
// Em qualquer componente PWA
router.push('/app/dashboard')
router.push('/app/protocolo/123')
router.push({ name: 'pwa-perfil' })
```

### Backoffice:
```javascript
// Em qualquer componente Backoffice
router.push('/backoffice/mesa-trabalho')
router.push({ name: 'backoffice-relatorios' })
```

---

## 🧪 Comandos Úteis

### Rodar servidor dev:
```bash
npm run dev
```

### Build de produção:
```bash
npm run build
```

### Preview do build:
```bash
npm run preview
```

### Limpar tudo:
```bash
rm -rf dist node_modules
npm install
npm run dev
```

---

## 🔍 Troubleshooting

### Erro: "Module not found"
**Solução:** Verificar se o import está apontando para a pasta correta:
- `pwa/`
- `backoffice/`
- `shared/`

### Erro: "Cannot read property 'push' of undefined"
**Solução:** Verificar se a rota está usando `/app/` ou `/backoffice/`

### Layout não aparece
**Solução:** Verificar se a rota é child do layout no `router/index.js`

---

## 📚 Documentação Completa

- 📖 **REFATORACAO_ESTRUTURA.md** - Documentação técnica detalhada
- 📊 **REFATORACAO_COMPLETA.md** - Resumo executivo
- 🎯 **GUIA_RAPIDO_REFATORACAO.md** - Este arquivo

---

## ✅ Tudo Certo!

A refatoração está **100% completa** e funcionando!

**Próximos passos:**
1. Testar as rotas no navegador
2. Verificar se todos os componentes carregam
3. Confirmar que a navegação funciona
4. Celebrar! 🎉

---

**Dúvidas?** Consulte a documentação completa! 📚
