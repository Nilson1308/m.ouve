# 🚀 Início Rápido - Mesa de Trabalho

## ⚡ Como Começar (3 Passos)

### 1️⃣ Acesse a Rota
```
http://localhost:5173/backoffice/mesa-trabalho
```

### 2️⃣ Adicione Link no Menu
Edite seu menu/sidebar e adicione:

```vue
<router-link to="/backoffice/mesa-trabalho" class="nav-item">
  <ClipboardDocumentListIcon class="w-5 h-5" />
  <span>Mesa de Trabalho</span>
</router-link>
```

### 3️⃣ Importe o Ícone
```vue
<script setup>
import { ClipboardDocumentListIcon } from '@heroicons/vue/24/outline'
</script>
```

---

## 🎯 Testando a Interface

### ✅ Checklist de Testes:
1. [ ] Abrir a rota `/backoffice/mesa-trabalho`
2. [ ] Alternar entre visualização Kanban e Lista
3. [ ] Usar a busca global
4. [ ] Ativar filtro "SLA Vencido"
5. [ ] Ativar filtro "Urgentes"
6. [ ] Clicar em "Despachar" em um protocolo
7. [ ] Adicionar 2 ou mais unidades no Scatter-Gather
8. [ ] Preencher instruções e prazos
9. [ ] Confirmar o despacho (verá console.log)
10. [ ] Testar ordenação na tabela (clicar nos headers)
11. [ ] Navegar entre páginas da tabela
12. [ ] Testar no mobile (F12 → Device Toolbar)
13. [ ] Alternar para Dark Mode
14. [ ] Verificar animações e transições

---

## 🎨 Personalizações Rápidas

### Alterar Cores:
Edite `tailwind.config.js` nas seções:
- `colors.primary` - Cor principal
- `colors.success` - Verde de sucesso
- `colors.danger` - Vermelho de alerta

### Adicionar Nova Coluna no Kanban:
`src/components/backoffice/BoardKanban.vue`:
```vue
<!-- Adicione após as 4 colunas existentes -->
<div class="kanban-column">
  <div class="kanban-header">
    <h3>Nova Coluna</h3>
    <span class="badge">0</span>
  </div>
  <div class="kanban-cards">
    <!-- Seus cards aqui -->
  </div>
</div>
```

E ajuste o grid:
```vue
<div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
```

### Adicionar Novo Filtro:
`src/views/MesaTrabalhoView.vue`:

1. Adicione no estado:
```javascript
const filtros = ref({
  busca: '',
  slaVencido: false,
  urgentes: false,
  meuNovoFiltro: false // NOVO
})
```

2. Adicione a lógica de filtro:
```javascript
const protocolosFiltrados = computed(() => {
  let resultado = protocolos.value
  
  // Seu novo filtro
  if (filtros.value.meuNovoFiltro) {
    resultado = resultado.filter(p => /* sua lógica */)
  }
  
  return resultado
})
```

3. Adicione o botão no header:
```vue
<button @click="toggleFiltro('meuNovoFiltro')">
  Meu Filtro
</button>
```

---

## 🔌 Conectando ao Backend

### Substituir Dados Mock:

#### Antes (Mock):
```javascript
const protocolos = ref([
  { id: 'PROT-001', /* dados mock */ }
])
```

#### Depois (API):
```javascript
import { onMounted } from 'vue'

const protocolos = ref([])
const loading = ref(false)

async function carregarProtocolos() {
  loading.value = true
  try {
    const response = await fetch('/api/backoffice/protocolos')
    const data = await response.json()
    protocolos.value = data.protocolos
  } catch (error) {
    console.error('Erro ao carregar protocolos:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  carregarProtocolos()
})
```

### Implementar Despacho Real:

#### Antes (Console.log):
```javascript
function confirmarDespacho(dados) {
  console.log('Despachar protocolo:', dados)
  fecharDespacho()
}
```

#### Depois (API):
```javascript
async function confirmarDespacho(dados) {
  try {
    const response = await fetch(
      `/api/backoffice/protocolos/${dados.protocoloId}/despachar`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      }
    )
    
    if (response.ok) {
      // Sucesso - atualizar lista
      await carregarProtocolos()
      fecharDespacho()
      // Mostrar toast de sucesso
    }
  } catch (error) {
    console.error('Erro ao despachar:', error)
    // Mostrar toast de erro
  }
}
```

---

## 🎨 Configurando Temas

### Forçar Dark Mode:
No `<html>` tag, adicione class `dark`:
```html
<html class="dark">
```

### Forçar High Contrast:
```html
<html class="high-contrast">
```

### Toggle Programático:
```javascript
// Light → Dark
document.documentElement.classList.add('dark')

// Dark → Light
document.documentElement.classList.remove('dark')
```

---

## 📱 PWA e Performance

### Service Worker (Já configurado):
A aplicação já tem suporte PWA via `vite-plugin-pwa`.

### Otimizações Aplicadas:
- ✅ Lazy loading de componentes
- ✅ Tree shaking automático (Vite)
- ✅ CSS purging (Tailwind)
- ✅ Imagens otimizadas
- ✅ Code splitting por rota

---

## 🐛 Troubleshooting

### Componente não aparece:
1. Verifique se a rota está correta
2. Abra o console (F12) e veja erros
3. Confirme que todos os imports estão corretos

### Ícones não aparecem:
```bash
npm install @heroicons/vue
```

### Estilos quebrados:
```bash
npm run dev
```

### Erro no build:
```bash
npm run build
```
Se houver erro, verifique o log e corrija imports.

---

## 📚 Documentação Completa

Para detalhes completos, consulte:
- 📖 `MESA_TRABALHO_README.md` - Documentação técnica
- 🎨 `GUIA_VISUAL_MESA_TRABALHO.md` - Guia visual
- 🧭 `EXEMPLO_NAVEGACAO.md` - Como adicionar navegação
- 📊 `RESUMO_MESA_TRABALHO.md` - Resumo executivo

---

## 🎉 Pronto!

Sua Mesa de Trabalho está funcionando! 🚀

### Próximos Passos Recomendados:
1. Conectar ao backend real
2. Adicionar toasts de feedback
3. Implementar drag & drop no Kanban
4. Adicionar filtros avançados
5. Criar testes automatizados

---

**Desenvolvido com ❤️ para o Ouv.IA - Fase 2**
