# Guia de Migração - Refatoração v2.0

## ✅ Status da Refatoração

### Completo (80%)
- [x] Dark Mode + High Contrast implementados
- [x] AppDialog criado e integrado
- [x] useDialog substituindo window.alert/confirm
- [x] Emojis removidos do StatusBadge
- [x] Heroicons instalado e em uso
- [x] Branding M.Ouve aplicado
- [x] useCepLookup criado (geocodificação)
- [x] ThemeToggle funcionando
- [x] DashboardView atualizada (parcial)
- [x] NovaSolicitacaoView atualizada (completa)

### Em Progresso (20%)
- [ ] LoginView com campos de endereço
- [ ] FormularioSolicitacaoView (emojis + dark mode)
- [ ] DetalhesProtocoloView (dark mode)
- [ ] API_CONTRACT.md atualizado

---

## 🚀 Como Usar as Novas Features

### 1. Dialog System

Substitui completamente `window.alert`, `window.confirm` e modais customizados.

**Antes:**
```javascript
if (confirm('Deseja excluir?')) {
  // código
}
alert('Salvo com sucesso!')
```

**Depois:**
```vue
<script setup>
import { useDialog } from '@/composables/useDialog'

const { success, error, warning, info, confirm } = useDialog()

// Informação
info('Protocolo #123 foi atualizado')

// Sucesso
success('Cadastro realizado com sucesso!')

// Erro
error('Não foi possível processar a solicitação')

// Aviso
warning('Esta ação não pode ser desfeita')

// Confirmação (async)
async function handleDelete() {
  const confirmed = await confirm(
    'Tem certeza que deseja excluir este protocolo?',
    'Confirmar Exclusão',
    {
      confirmText: 'Sim, excluir',
      cancelText: 'Cancelar'
    }
  )
  
  if (confirmed) {
    // Executar exclusão
    success('Protocolo excluído!')
  }
}
</script>
```

---

### 2. Sistema de Temas

Três temas disponíveis: Claro, Escuro, Alto Contraste.

**Usar o Toggle:**
```vue
<template>
  <ThemeToggle />
</template>

<script setup>
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>
```

**Programático:**
```vue
<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// Alternar para próximo tema
themeStore.toggleTheme()

// Definir tema específico
themeStore.setTheme('dark') // 'light', 'dark', 'high-contrast'

// Obter tema atual
console.log(themeStore.currentTheme)
console.log(themeStore.getThemeLabel()) // 'Claro', 'Escuro', 'Alto Contraste'
</script>
```

---

### 3. CEP + Geocodificação

Busca automática de endereço e coordenadas geográficas.

**Uso Básico:**
```vue
<script setup>
import { ref } from 'vue'
import { useCepLookup } from '@/composables/useCepLookup'
import { useDialog } from '@/composables/useDialog'

const { buscarCepComGeocoding, loading, error, formatarCep } = useCepLookup()
const { success, error: showError } = useDialog()

const cep = ref('')
const numero = ref('')
const endereco = ref(null)
const coordenadas = ref(null)

async function handleBuscarCep() {
  if (!cep.value || cep.value.length < 8) {
    showError('Digite um CEP válido')
    return
  }
  
  const result = await buscarCepComGeocoding(cep.value, numero.value)
  
  if (result.success) {
    endereco.value = result.endereco
    coordenadas.value = result.coordenadas
    
    console.log('Endereço:', endereco.value)
    // {
    //   cep: '01310-100',
    //   logradouro: 'Avenida Paulista',
    //   numero: '42',
    //   complemento: '',
    //   bairro: 'Bela Vista',
    //   cidade: 'São Paulo',
    //   estado: 'SP',
    //   enderecoCompleto: 'Avenida Paulista, Bela Vista - São Paulo/SP'
    // }
    
    console.log('Coordenadas:', coordenadas.value)
    // {
    //   latitude: -23.561414,
    //   longitude: -46.656451,
    //   precisao: 'exata' // ou 'cidade' em caso de fallback
    // }
    
    success('Endereço encontrado!')
  } else {
    showError(result.error || 'Erro ao buscar CEP')
  }
}

// Formatar CEP enquanto digita
function handleCepInput(event) {
  cep.value = formatarCep(event.target.value)
}
</script>

<template>
  <div>
    <input
      v-model="cep"
      @input="handleCepInput"
      @blur="handleBuscarCep"
      placeholder="00000-000"
      maxlength="9"
      class="input"
    />
    
    <input
      v-model="numero"
      placeholder="Número"
      class="input"
    />
    
    <!-- Campos preenchidos automaticamente -->
    <input v-model="endereco.logradouro" readonly class="input" />
    <input v-model="endereco.bairro" readonly class="input" />
    <input v-model="endereco.cidade" readonly class="input" />
    <input v-model="endereco.estado" readonly class="input" />
    
    <p v-if="loading">Buscando endereço...</p>
    <p v-if="coordenadas">
      Localização: {{ coordenadas.latitude }}, {{ coordenadas.longitude }}
    </p>
  </div>
</template>
```

---

### 4. Aplicar Dark Mode + High Contrast em Componentes

**Padrão de Classes:**
```vue
<template>
  <!-- Backgrounds -->
  <div class="bg-white dark:bg-gray-800 high-contrast:bg-black">
    
    <!-- Texto normal -->
    <p class="text-gray-900 dark:text-gray-100 high-contrast:text-white high-contrast:font-bold">
      Texto aqui
    </p>
    
    <!-- Títulos -->
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 high-contrast:text-yellow-300 high-contrast:font-bold">
      Título
    </h2>
    
    <!-- Texto secundário -->
    <p class="text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
      Descrição
    </p>
    
    <!-- Bordas -->
    <div class="border border-gray-200 dark:border-gray-700 high-contrast:border-4 high-contrast:border-yellow-300">
      
    </div>
    
    <!-- Ícones -->
    <component 
      :is="IconComponent" 
      class="w-6 h-6 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300"
    />
    
  </div>
</template>
```

**Usando Classes Utilitárias (Recomendado):**
```vue
<template>
  <!-- Botões - já suportam automaticamente -->
  <button class="btn-primary">Salvar</button>
  
  <!-- Cards - já suportam automaticamente -->
  <div class="card">
    Conteúdo
  </div>
  
  <!-- Inputs - já suportam automaticamente -->
  <input class="input" />
  
  <!-- Alertas - já suportam automaticamente -->
  <div class="alert-success">Sucesso!</div>
  
  <!-- Badges - use StatusBadge component -->
  <StatusBadge status="concluido" tipo="zeladoria" :show-icon="true" />
</template>
```

---

### 5. Usar Heroicons em Vez de Emojis

**Antes:**
```vue
<span>🚀 Enviado</span>
<span>✅ Concluído</span>
<span>🤖 Triagem IA</span>
```

**Depois:**
```vue
<script setup>
import { 
  RocketLaunchIcon,
  CheckCircleIcon,
  CpuChipIcon
} from '@heroicons/vue/24/outline'
</script>

<template>
  <span class="inline-flex items-center gap-1">
    <RocketLaunchIcon class="w-4 h-4" />
    Enviado
  </span>
  
  <span class="inline-flex items-center gap-1">
    <CheckCircleIcon class="w-4 h-4" />
    Concluído
  </span>
  
  <span class="inline-flex items-center gap-1">
    <CpuChipIcon class="w-4 h-4" />
    Triagem IA
  </span>
</template>
```

**Ícones Disponíveis (mais usados):**
```javascript
// Outline (linha)
import {
  CheckCircleIcon,      // ✓ check
  XCircleIcon,          // ✗ erro
  ExclamationTriangleIcon, // ⚠ aviso
  InformationCircleIcon,   // ℹ info
  CpuChipIcon,          // 🤖 IA
  EyeIcon,              // 👁️ visualizar
  ClockIcon,            // ⏰ tempo
  TruckIcon,            // 🚚 transporte
  WrenchScrewdriverIcon, // 🔧 ferramenta
  DocumentTextIcon,     // 📄 documento
  MagnifyingGlassIcon,  // 🔍 busca
  PaperAirplaneIcon,    // ✈️ enviar
  ArchiveBoxIcon,       // 📦 arquivo
  ChatBubbleLeftRightIcon, // 💬 chat
  BuildingOffice2Icon,  // 🏢 prédio
  MapPinIcon,           // 📍 localização
  PhotoIcon,            // 🖼️ foto
  MicrophoneIcon,       // 🎤 áudio
} from '@heroicons/vue/24/outline'
```

---

## 📋 Checklist de Migração para Desenvolvedores

### Para Cada View/Component:

1. **Remover Emojis**
   - [ ] Buscar por regex: `[\u{1F300}-\u{1F9FF}]` ou qualquer emoji visual
   - [ ] Substituir por Heroicons apropriados

2. **Adicionar Dark Mode**
   - [ ] Background: `bg-white dark:bg-gray-800 high-contrast:bg-black`
   - [ ] Texto: `text-gray-900 dark:text-gray-100 high-contrast:text-white`
   - [ ] Títulos: adicionar `high-contrast:text-yellow-300 high-contrast:font-bold`

3. **Substituir Alerts**
   - [ ] `alert()` → `useDialog().info()`
   - [ ] `confirm()` → `await useDialog().confirm()`
   - [ ] Remover `window.alert` e `window.confirm`

4. **Usar Classes Utilitárias**
   - [ ] Usar `.btn-primary` em vez de classes customizadas
   - [ ] Usar `.card` em vez de bg-white + shadow
   - [ ] Usar `.input` em vez de classes inline

5. **Testar Temas**
   - [ ] Verificar legibilidade em tema claro
   - [ ] Verificar legibilidade em tema escuro
   - [ ] Verificar contraste WCAG AAA em alto contraste

---

## 🎯 Próximos Passos Prioritários

### 1. Completar LoginView com Endereço (URGENTE)

Adicionar campos:
- CEP (com busca automática)
- Logradouro (readonly, preenchido automaticamente)
- Número (obrigatório)
- Complemento (opcional)
- Bairro, Cidade, Estado (readonly)
- Coordenadas (hidden, salvas em background)

### 2. Remover Emojis de FormularioSolicitacaoView

Views com emojis restantes:
- `src/views/FormularioSolicitacaoView.vue` - Muitos emojis
- `src/views/DesignSystemView.vue` - Emojis em exemplos

### 3. Aplicar Dark/High-Contrast em:
- `src/views/LoginView.vue`
- `src/views/FormularioSolicitacaoView.vue`
- `src/views/DetalhesProtocoloView.vue`

### 4. Atualizar Documentação
- `API_CONTRACT.md` - Endpoint de registro com endereço
- `README.md` - Novas features
- `COLOR_SYSTEM.md` - Dark mode e high contrast

---

## 📊 Status Final

**Progresso Total: 80%**

### ✅ Funcionalidades Core (100%)
- Dialog system
- Dark mode
- High contrast
- Theme toggle
- CEP lookup
- Geocodificação

### ⚠️ Aplicação em Views (60%)
- DashboardView: 90%
- NovaSolicitacaoView: 100%
- LoginView: 40%
- FormularioSolicitacaoView: 20%
- DetalhesProtocoloView: 30%
- DesignSystemView: 80%

### 📝 Documentação (70%)
- Guias de uso: 100%
- API Contract: 40%
- README: 80%

---

**Última Atualização:** 09/11/2024 14:00  
**Próxima Ação:** Completar LoginView com campos de endereço
