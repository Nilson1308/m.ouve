# Guia de Contribuição

Obrigado por considerar contribuir com o M.Ouve! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Pré-requisitos

- Node.js >= 20.x
- npm >= 10.x
- Git
- Editor de código (VS Code recomendado)

## 🚀 Configuração do Ambiente

```bash
# Clone o repositório
git clone <repository-url>
cd ouve

# Instale as dependências
npm install

# Copie o arquivo de variáveis de ambiente
cp .env.example .env

# Inicie o servidor de desenvolvimento
npm run dev
```

## 🌿 Workflow Git

### Branches

- `main` - Código em produção
- `develop` - Branch de desenvolvimento
- `feature/*` - Novas funcionalidades
- `bugfix/*` - Correções de bugs
- `hotfix/*` - Correções urgentes

### Convenção de Commits

Seguimos a convenção [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações na documentação
- `style`: Formatação (não afeta o código)
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção

**Exemplos:**
```
feat(auth): adiciona login com Gov.br

fix(protocolos): corrige ordenação da lista

docs(readme): atualiza instruções de instalação

style(dashboard): ajusta espaçamento dos cards

refactor(stores): simplifica lógica de autenticação
```

## 📝 Padrões de Código

### Vue 3 / Composition API

**✅ Faça:**
```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>
```

**❌ Não faça:**
```vue
<script>
export default {
  data() {
    return { count: 0 }
  }
}
</script>
```

### Nomenclatura

**Componentes:**
```
PascalCase para nomes de componentes
LoginView.vue
EmptyState.vue
StatusBadge.vue
```

**Props e eventos:**
```javascript
// Props: camelCase
const props = defineProps({
  userId: String,
  isActive: Boolean
})

// Eventos: kebab-case
emit('update-data')
emit('item-selected')
```

**Variáveis e funções:**
```javascript
// camelCase
const userName = ref('')
function handleSubmit() {}
```

### Tailwind CSS

**✅ Use classes utilitárias:**
```html
<div class="flex items-center gap-4 p-6 bg-white rounded-lg shadow-gov">
```

**❌ Evite CSS customizado quando possível:**
```html
<!-- Evite -->
<div class="custom-card">
<style scoped>
.custom-card { /* ... */ }
</style>
```

**⚠️ Use apenas quando necessário:**
```vue
<style scoped>
/* Apenas para animações complexas ou comportamentos
   que não podem ser feitos com Tailwind */
.special-animation {
  animation: custom 2s ease-in-out;
}
</style>
```

## 🧩 Criando Novos Componentes

### Template
```vue
<template>
  <div class="my-component">
    <!-- Conteúdo -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['update', 'close'])

// State
const loading = ref(false)

// Computed
const isReady = computed(() => !loading.value)

// Methods
function handleClick() {
  emit('update')
}

// Lifecycle
onMounted(() => {
  // Initialization
})
</script>

<style scoped>
/* Estilos específicos apenas se necessário */
</style>
```

## 🧪 Testes

```bash
# Executar testes unitários
npm run test

# Executar testes com coverage
npm run test:coverage

# Executar testes E2E
npm run test:e2e
```

### Escrevendo Testes

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    const wrapper = mount(MyComponent, {
      props: { title: 'Test' }
    })
    expect(wrapper.text()).toContain('Test')
  })

  it('emits update event', async () => {
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update')).toBeTruthy()
  })
})
```

## 📱 Design System

### Cores

```javascript
// Gov.br Colors
'gov-blue-warm': '#1351B4'
'gov-blue-vivid': '#155BCB'
'gov-blue-deep': '#0C326F'
'gov-green-cool': '#168821'
'gov-yellow-vivid': '#FFCD07'
```

### Componentes Base

Use sempre os componentes base quando disponíveis:

```vue
<!-- Loading -->
<LoadingSpinner size="md" color="primary" text="Carregando..." />

<!-- Empty State -->
<EmptyState 
  title="Nenhum resultado"
  description="Não encontramos protocolos"
  actionText="Nova Solicitação"
  @action="handleAction"
/>

<!-- Modal -->
<ModalBase v-model="showModal" title="Confirmar">
  <p>Conteúdo do modal</p>
  <template #footer>
    <button class="btn btn-primary">Confirmar</button>
  </template>
</ModalBase>

<!-- Status Badge -->
<StatusBadge status="resolvido" :show-icon="true" />
```

## 🔍 Code Review

### Checklist do PR

- [ ] Código segue os padrões do projeto
- [ ] Commits seguem a convenção
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada (se necessário)
- [ ] Build passa sem warnings
- [ ] Testado em diferentes tamanhos de tela
- [ ] Testado em Chrome, Firefox, Safari

### Processo de Review

1. Crie um PR da sua branch para `develop`
2. Descreva as mudanças detalhadamente
3. Adicione screenshots (se aplicável)
4. Aguarde aprovação de pelo menos 1 revisor
5. Resolva comentários do review
6. Merge após aprovação

## 📚 Documentação

### Documente:
- Funções complexas
- Componentes reutilizáveis
- APIs e serviços
- Decisões arquiteturais importantes

### JSDoc

```javascript
/**
 * Busca protocolos do usuário com filtros
 * @param {Object} filters - Filtros de busca
 * @param {string} [filters.status] - Status do protocolo
 * @param {string} [filters.tipo] - Tipo (ouvidoria/zeladoria)
 * @returns {Promise<Array>} Lista de protocolos
 */
async function buscarProtocolos(filters) {
  // ...
}
```

## 🐛 Reportando Bugs

### Template de Issue

```markdown
**Descrição:**
Descrição clara e concisa do bug

**Reprodução:**
1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

**Comportamento esperado:**
O que deveria acontecer

**Screenshots:**
Se aplicável, adicione screenshots

**Ambiente:**
- OS: [e.g. iOS, Android, Windows]
- Browser: [e.g. Chrome, Safari]
- Versão: [e.g. 22]

**Contexto adicional:**
Qualquer outra informação relevante
```

## 💡 Sugerindo Melhorias

### Template de Feature Request

```markdown
**Problema:**
Qual problema essa feature resolve?

**Solução proposta:**
Descreva a solução que você gostaria de ver

**Alternativas consideradas:**
Outras soluções que você considerou

**Contexto adicional:**
Qualquer outra informação, mockups, exemplos
```

## 📞 Contato

- Issues: [GitHub Issues]
- Discussões: [GitHub Discussions]
- Email: dev@sinapse.gov.br

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

**Obrigado por contribuir com o M.Ouve! 🎉**
