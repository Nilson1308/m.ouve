# 🏗️ Arquitetura do Form Builder No-Code

## 📐 Diagrama de Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                   USUÁRIO SUPER ADMIN                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Acessa
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ConfiguracoesView.vue (Vue Router)                             │
│  /backoffice/configuracoes?aba=servicos                         │
│                                                                  │
│  Tabs: [Unidades] [Usuários] [Perfis] [→Catálogo←] [Notif.]   │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Renderiza
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  GestaoCatalogo.vue                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ [Filtro: Todos ▼] [Busca: _____________] [+ Criar]    │    │
│  ├────────────────────────────────────────────────────────┤    │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │    │
│  │ │ Serviço │ │ Serviço │ │ Serviço │ ...               │    │
│  │ │ Card 1  │ │ Card 2  │ │ Card 3  │                   │    │
│  │ │ [Editar]│ │ [Editar]│ │ [Editar]│                   │    │
│  │ └─────────┘ └─────────┘ └─────────┘                   │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────┬───────────┬────────────────────────────────────────┘
             │           │
   Click [+] │           │ Click [✏️]
             ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│  FormBuilderServico.vue (Modal)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ⚙️  SEÇÃO 1: METADADOS                                    │  │
│  │                                                           │  │
│  │ Nome:         [_________________]                         │  │
│  │ Descrição:    [_________________]                         │  │
│  │ SLA:          [___] horas                                 │  │
│  │ Unidade:      [Selecione ▼]                              │  │
│  │ Categoria:    [Selecione ▼]                              │  │
│  │ Ativo:        [✓]                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📐 SEÇÃO 2: FORM BUILDER CANVAS                           │  │
│  │                                    [+ Adicionar Campo]    │  │
│  │ ┌─────────────────────────────────────────────────────┐  │  │
│  │ │ Campo 1: Localização    [Obrig] [↑][↓][▼][🗑️]       │  │  │
│  │ │ ─────────────────────────────────────────────────    │  │  │
│  │ │ Label: [Onde está?_____] Name: [onde_esta] (auto)   │  │  │
│  │ │ Placeholder: [Toque no mapa_______]                  │  │  │
│  │ └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │ ┌─────────────────────────────────────────────────────┐  │  │
│  │ │ Campo 2: Foto          [↑][↓][▼][🗑️]                │  │  │
│  │ └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │ ┌─────────────────────────────────────────────────────┐  │  │
│  │ │ Campo 3: Seleção       [↑][↓][▼][🗑️]                │  │  │
│  │ └─────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Cancelar]                            [Salvar Serviço] ✨      │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ Click [Salvar]
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROCESSAMENTO (FormBuilderServico.vue)                         │
│                                                                  │
│  1. ✅ Validar formulário (nome, unidade, pelo menos 1 campo)   │
│  2. ✅ Limpar campos internos (_id, _expandido)                 │
│  3. ✅ Montar payload JSON                                      │
│  4. ✅ Chamar store.criarServicoCatalogo() ou atualizar()       │
└────────────┬────────────────────────────────────────────────────┘
             │
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  catalogo.js (Pinia Store)                                      │
│                                                                  │
│  async function criarServicoCatalogo(form, camposUi) {          │
│    const payload = payloadServicoCatalogo(form, camposUi)       │
│    const { data } = await api.post(                             │
│      '/backoffice/servicos-catalogo',                           │
│      payload                                                    │
│    )                                                            │
│    return mapServicoCatalogo(data)                              │
│  }                                                              │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ HTTP POST
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND (Django REST Framework)                                │
│  POST /api/v1/backoffice/servicos-catalogo                      │
│                                                                  │
│  {                                                              │
│    "nome": "Buraco na Rua",                                     │
│    "descricao": "Reportar buracos nas vias",                    │
│    "slaHoras": 72,                                              │
│    "unidadeResponsavelId": 5,                                   │
│    "categoriaId": "zeladoria_urbana",                           │
│    "ativo": true,                                               │
│    "formularioSchema": [                                        │
│      {                                                          │
│        "name": "local_do_buraco",                               │
│        "label": "Onde está o buraco?",                          │
│        "type": "geo",                                           │
│        "required": true,                                        │
│        "placeholder": "Toque no mapa"                           │
│      },                                                         │
│      {                                                          │
│        "name": "foto_buraco",                                   │
│        "label": "Foto do buraco",                               │
│        "type": "image",                                         │
│        "required": false                                        │
│      }                                                          │
│    ]                                                            │
│  }                                                              │
│                                                                  │
│  ✅ Valida, salva no PostgreSQL                                 │
│  ✅ Retorna 201 Created com ID                                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Resposta
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  catalogo.js (Store)                                            │
│  • Mapeia resposta                                              │
│  • Adiciona serviço ao state.servicos[]                         │
│  • Incrementa totalServicos                                     │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Emit 'sucesso'
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  GestaoCatalogo.vue                                             │
│  • Fecha modal                                                  │
│  • Recarrega lista de serviços                                  │
│  • Mostra toast "Serviço criado com sucesso!"                   │
│  • Novo card aparece na listagem                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 COMPONENTES E RESPONSABILIDADES

### 1. **ConfiguracoesView.vue**
**Papel:** Container principal com sistema de abas

```javascript
// Responsabilidades:
✅ Renderizar tabs (Unidades, Usuários, Perfis, Catálogo, etc)
✅ Sincronizar aba ativa com query string (?aba=servicos)
✅ Exibir badges com contadores (totalServicos)
✅ Gerenciar toasts de sucesso/erro
✅ Layout consistente (header, tabs, conteúdo)
```

**Dependências:**
- `catalogo.js` store (totalServicos)
- `admin.js` store (totalUnidades, totalUsuarios, etc)
- GestaoCatalogo.vue
- GestaoUnidades.vue
- GestaoUsuarios.vue
- GestaoPerfis.vue

---

### 2. **GestaoCatalogo.vue**
**Papel:** Listagem e CRUD básico de serviços

```javascript
// Responsabilidades:
✅ Carregar lista de serviços (onMounted)
✅ Filtrar por status (todos/ativo/inativo)
✅ Buscar por nome/descrição
✅ Renderizar cards de serviços (grid)
✅ Abrir modal de criação/edição
✅ Confirmar e executar exclusão
✅ Calcular SLA em dias (ex: 72h = 3d)
✅ Contar campos do formulário (formularioSchema.length)
```

**State Interno:**
```javascript
const servicoEmEdicao = ref(null)        // Serviço sendo editado
const mostrarFormBuilder = ref(false)    // Modal aberto?
const buscaNome = ref('')                // Busca textual
const filtroStatus = ref('todos')        // Filtro dropdown
const confirmarExclusao = ref(false)     // Modal confirmação
const servicoParaExcluir = ref(null)     // Serviço a excluir
```

**Dependências:**
- `catalogo.js` store (servicos, carregarServicosCatalogo(), excluirServicoCatalogo())
- FormBuilderServico.vue

---

### 3. **FormBuilderServico.vue** ⭐
**Papel:** Construtor visual no-code (CORE DA FEATURE)

```javascript
// Responsabilidades:
✅ Renderizar formulário de metadados do serviço
✅ Carregar unidades do admin.js para select
✅ Gerenciar lista reativa de campos (campos.value)
✅ Dropdown de tipos de campo (6 opções)
✅ Adicionar campo ao canvas (adicionarCampo)
✅ Remover campo (removerCampo)
✅ Expandir/colapsar card (toggleExpandir)
✅ Reordenar campos (moverCampo com setas)
✅ Auto-gerar name snake_case (atualizarName)
✅ Validar formulário
✅ Limpar campos internos (_id, _expandido)
✅ Salvar (POST/PUT via store)
✅ Modo criação vs edição
```

**State Interno:**
```javascript
const formulario = ref({
  nome: '',
  descricao: '',
  slaHoras: 48,
  unidadeResponsavelId: null,
  categoriaId: '',
  ativo: true
})

const campos = ref([
  {
    _id: 'campo-1',           // Gerado internamente (nanoid())
    _expandido: true,         // Estado UI
    name: 'local_problema',   // Auto-gerado
    label: 'Onde está o problema?',
    type: 'geo',
    required: true,
    placeholder: 'Toque no mapa',
    options: []               // Apenas para type='select'
  }
])

const mostrarDropdown = ref(false)
const salvando = ref(false)
```

**Funções Críticas:**

#### `adicionarCampo(tipo)`
```javascript
// Cria novo campo com valores padrão
function adicionarCampo(tipo) {
  const novoCampo = {
    _id: nanoid(),
    _expandido: true,
    name: '',
    label: '',
    type: tipo,
    required: false,
    placeholder: '',
    options: tipo === 'select' ? [] : undefined
  }
  campos.value.push(novoCampo)
  mostrarDropdown.value = false
}
```

#### `atualizarName(campo)`
```javascript
// Auto-geração de snake_case
function atualizarName(campo) {
  if (campo.label) {
    campo.name = campo.label
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9\s]/g, '')
      .trim()
      .replace(/\s+/g, '_')
  }
}
```

#### `moverCampo(index, direcao)`
```javascript
// Reordenar com setas (-1 = ↑, +1 = ↓)
function moverCampo(index, direcao) {
  const novoIndex = index + direcao
  if (novoIndex < 0 || novoIndex >= campos.value.length) return
  
  const campo = campos.value.splice(index, 1)[0]
  campos.value.splice(novoIndex, 0, campo)
}
```

#### `salvar()`
```javascript
// Limpa campos internos e envia para API
async function salvar() {
  if (!formularioValido.value) return
  
  salvando.value = true
  
  const payload = {
    ...formulario.value,
    formularioSchema: campos.value.map(campo => {
      const { _id, _expandido, ...campoLimpo } = campo
      return campoLimpo
    })
  }
  
  try {
    if (modoEdicao.value) {
      await catalogoStore.atualizarServicoCatalogo(
        props.servico.id,
        payload,
        campos.value
      )
    } else {
      await catalogoStore.criarServicoCatalogo(payload, campos.value)
    }
    emit('sucesso')
  } catch (erro) {
    console.error('Erro ao salvar serviço:', erro)
  } finally {
    salvando.value = false
  }
}
```

**Dependências:**
- `catalogo.js` store (criarServicoCatalogo, atualizarServicoCatalogo)
- `admin.js` store (unidadesAtivas para select)
- Heroicons (ícones)
- nanoid (IDs únicos)

---

### 4. **catalogo.js (Pinia Store)**
**Papel:** Gerenciamento de estado e comunicação com API

```javascript
// State
const state = {
  servicos: [],              // Lista de serviços
  totalServicos: 0,          // Contador
  carregando: false,         // Loading state
  erro: null                 // Mensagens de erro
}

// Actions
async function carregarServicosCatalogo() {
  carregando.value = true
  try {
    const { data } = await api.get('/backoffice/servicos-catalogo')
    servicos.value = data.map(mapServicoCatalogo)
    totalServicos.value = servicos.value.length
  } finally {
    carregando.value = false
  }
}

async function criarServicoCatalogo(form, camposUi) {
  const payload = payloadServicoCatalogo(form, camposUi)
  const { data } = await api.post('/backoffice/servicos-catalogo', payload)
  const novoServico = mapServicoCatalogo(data)
  servicos.value.push(novoServico)
  totalServicos.value++
  return novoServico
}

async function atualizarServicoCatalogo(id, form, camposUi) {
  const payload = payloadServicoCatalogo(form, camposUi)
  const { data } = await api.put(`/backoffice/servicos-catalogo/${id}`, payload)
  const servicoAtualizado = mapServicoCatalogo(data)
  const index = servicos.value.findIndex(s => s.id === id)
  if (index !== -1) {
    servicos.value[index] = servicoAtualizado
  }
  return servicoAtualizado
}

async function excluirServicoCatalogo(id) {
  await api.delete(`/backoffice/servicos-catalogo/${id}`)
  servicos.value = servicos.value.filter(s => s.id !== id)
  totalServicos.value--
}
```

**Helpers:**

#### `payloadServicoCatalogo(form, camposUi)`
```javascript
// Converte state interno para formato da API
function payloadServicoCatalogo(form, camposUi) {
  return {
    nome: form.nome,
    descricao: form.descricao,
    sla_horas: form.slaHoras,
    unidade_responsavel_id: form.unidadeResponsavelId,
    categoria_id: form.categoriaId,
    ativo: form.ativo,
    formulario_schema: camposUi.map(campo => {
      const { _id, _expandido, ...campoLimpo } = campo
      return campoLimpo
    })
  }
}
```

#### `mapServicoCatalogo(data)`
```javascript
// Converte resposta da API para formato Vue
function mapServicoCatalogo(data) {
  return {
    id: data.id,
    nome: data.nome,
    descricao: data.descricao,
    slaHoras: data.sla_horas,
    unidadeResponsavelId: data.unidade_responsavel_id,
    categoriaId: data.categoria_id,
    ativo: data.ativo,
    formularioSchema: data.formulario_schema || []
  }
}
```

---

## 🔄 FLUXO DE DADOS (DATA FLOW)

### Criação de Serviço:

```
1. User Click [+ Criar Novo Serviço]
   ↓
2. GestaoCatalogo emite evento → abre FormBuilderServico
   ↓
3. FormBuilderServico inicializa state:
   - formulario: valores padrão
   - campos: array vazio
   ↓
4. User preenche metadados (nome, SLA, etc)
   ↓
5. User click [+ Adicionar Campo]
   ↓
6. FormBuilderServico.adicionarCampo('geo')
   ↓
7. Novo objeto adicionado a campos.value com _id único
   ↓
8. User digita label "Onde está?"
   ↓
9. @input chama atualizarName(campo)
   ↓
10. campo.name = 'onde_esta' (auto-gerado)
    ↓
11. User toggle [Campo Obrigatório]
    ↓
12. campo.required = true
    ↓
13. User click [Salvar Serviço]
    ↓
14. FormBuilderServico.salvar()
    ↓
15. Limpa _id e _expandido de cada campo
    ↓
16. Monta payload JSON limpo
    ↓
17. Chama catalogoStore.criarServicoCatalogo(payload, campos)
    ↓
18. Store converte para snake_case (payloadServicoCatalogo)
    ↓
19. POST /api/v1/backoffice/servicos-catalogo
    ↓
20. Backend valida, salva, retorna 201
    ↓
21. Store mapeia resposta (mapServicoCatalogo)
    ↓
22. Store adiciona serviço a servicos.value[]
    ↓
23. Store incrementa totalServicos
    ↓
24. FormBuilderServico emite evento 'sucesso'
    ↓
25. GestaoCatalogo fecha modal
    ↓
26. GestaoCatalogo recarrega lista
    ↓
27. Novo card aparece na tela
    ↓
28. Toast: "Serviço criado com sucesso!" ✅
```

---

### Edição de Serviço:

```
1. User click [✏️ Editar] em card
   ↓
2. GestaoCatalogo passa servicoEmEdicao como prop
   ↓
3. FormBuilderServico detecta modoEdicao.value = true
   ↓
4. onMounted: popula formulario.value com dados existentes
   ↓
5. Carrega formularioSchema em campos.value
   ↓
6. Adiciona _id e _expandido=false a cada campo
   ↓
7. User edita, adiciona ou remove campos
   ↓
8. User usa setas ↑ ↓ para reordenar
   ↓
9. User click [Atualizar Serviço]
   ↓
10. FormBuilderServico.salvar() com PUT
    ↓
11. catalogoStore.atualizarServicoCatalogo(id, payload, campos)
    ↓
12. PUT /api/v1/backoffice/servicos-catalogo/{id}
    ↓
13. Backend atualiza, retorna 200
    ↓
14. Store substitui serviço no array (findIndex + replace)
    ↓
15. GestaoCatalogo fecha modal
    ↓
16. Card atualizado aparece com novos dados
    ↓
17. Toast: "Serviço atualizado com sucesso!" ✅
```

---

### Exclusão de Serviço:

```
1. User click [🗑️] em card
   ↓
2. GestaoCatalogo abre modal de confirmação
   ↓
3. User confirma
   ↓
4. catalogoStore.excluirServicoCatalogo(id)
   ↓
5. DELETE /api/v1/backoffice/servicos-catalogo/{id}
   ↓
6. Backend valida permissões, executa soft delete, retorna 204
   ↓
7. Store remove serviço de servicos.value (filter)
   ↓
8. Store decrementa totalServicos
   ↓
9. GestaoCatalogo fecha modal
   ↓
10. Card desaparece da listagem
    ↓
11. Toast: "Serviço excluído com sucesso!" ✅
```

---

## 🔐 CONTROLE DE ACESSO (RBAC)

### Níveis de Permissão:

```javascript
// Super Admin (perfil_id: 'super_admin')
✅ Visualizar catálogo
✅ Criar serviços
✅ Editar qualquer serviço
✅ Excluir qualquer serviço
✅ Ativar/desativar serviços
✅ Modificar formularioSchema

// Admin de Unidade (perfil_id: 'admin_unidade')
✅ Visualizar catálogo
⚠️ Criar serviços (apenas para sua unidade)
⚠️ Editar serviços (apenas da sua unidade)
⚠️ Excluir serviços (apenas da sua unidade, se não houver protocolos)
❌ Modificar unidadeResponsavelId de serviços de outras unidades

// Atendente (perfil_id: 'atendente')
✅ Visualizar catálogo (apenas serviços ativos da sua unidade)
❌ Criar, editar ou excluir
```

### Validação no Backend:

```python
# Django - views.py
class ServicoCatalogoViewSet(viewsets.ModelViewSet):
    queryset = ServicoCatalogo.objects.all()
    serializer_class = ServicoCatalogoSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.perfil.id == 'super_admin':
            return self.queryset.all()
        elif user.perfil.id == 'admin_unidade':
            return self.queryset.filter(
                unidade_responsavel=user.unidade_administrativa
            )
        else:
            return self.queryset.filter(
                ativo=True,
                unidade_responsavel=user.unidade_administrativa
            )
    
    def perform_destroy(self, instance):
        # Impedir exclusão se houver protocolos atrelados
        if instance.protocolos.exists():
            raise ValidationError(
                "Não é possível excluir um serviço com protocolos existentes."
            )
        instance.delete()
```

---

## 📊 PERFORMANCE E OTIMIZAÇÕES

### Bundle Size:

```
ConfiguracoesView.js: 110.34 KB (gzip: 27.25 KB)
  - GestaoCatalogo: ~8 KB
  - FormBuilderServico: ~15 KB
  - Heroicons (compartilhados): ~5 KB
  - Outros (GestaoUnidades, GestaoUsuarios, etc): ~82 KB
```

### Lazy Loading:

```javascript
// router/index.js
{
  path: '/backoffice/configuracoes',
  component: () => import('@/views/backoffice/ConfiguracoesView.vue'),
  meta: { requiresAuth: true, perfilPermitido: ['super_admin'] }
}
```

### Computed Reactivity:

```javascript
// GestaoCatalogo.vue
const servicosFiltrados = computed(() => {
  let resultado = servicos.value
  
  // Filtro por status (O(n))
  if (filtroStatus.value === 'ativo') {
    resultado = resultado.filter(s => s.ativo)
  }
  
  // Busca textual (O(n))
  if (buscaNome.value.trim()) {
    const busca = buscaNome.value.toLowerCase()
    resultado = resultado.filter(s =>
      s.nome.toLowerCase().includes(busca) ||
      s.descricao?.toLowerCase().includes(busca)
    )
  }
  
  return resultado
})
// ✅ Atualiza automaticamente quando servicos, filtroStatus ou buscaNome mudam
```

### V-Key Optimization:

```vue
<!-- GestaoCatalogo.vue -->
<div
  v-for="servico in servicosFiltrados"
  :key="servico.id"
  class="service-card"
>
  <!-- Vue reutiliza componentes corretamente -->
</div>
```

---

## 🧪 CASOS DE TESTE

### Teste 1: Criar Serviço Simples

```javascript
// Input
formulario = {
  nome: "Teste Básico",
  descricao: "Descrição teste",
  slaHoras: 24,
  unidadeResponsavelId: 1,
  categoriaId: "teste",
  ativo: true
}
campos = [
  { label: "Campo Texto", type: "text", required: true }
]

// Esperado
POST /api/v1/backoffice/servicos-catalogo
{
  "nome": "Teste Básico",
  "formulario_schema": [
    {
      "name": "campo_texto",
      "label": "Campo Texto",
      "type": "text",
      "required": true
    }
  ]
}
```

### Teste 2: Auto-geração de Name

```javascript
// Casos
"Foto do Buraco"       → "foto_do_buraco"
"Localização GPS"      → "localizacao_gps"
"CPF (obrigatório)"    → "cpf_obrigatorio"
"Nº do Poste"          → "n_do_poste"
"Descrição com Ações!" → "descricao_com_acoes"
```

### Teste 3: Reordenação

```javascript
// Estado Inicial
campos = [
  { name: "campo_1" },
  { name: "campo_2" },
  { name: "campo_3" }
]

// Ação: moverCampo(2, -1) // Move campo_3 para cima
// Estado Final
campos = [
  { name: "campo_1" },
  { name: "campo_3" }, // ← Movido
  { name: "campo_2" }
]
```

### Teste 4: Validação

```javascript
// Inválido: nome vazio
formulario.nome = ''
→ formularioValido.value = false
→ Botão [Salvar] desabilitado

// Inválido: sem campos
campos.value = []
→ formularioValido.value = false
→ Botão [Salvar] desabilitado

// Válido
formulario.nome = 'Buraco na Rua'
campos.value = [{ label: 'Local', type: 'geo', required: true }]
→ formularioValido.value = true
→ Botão [Salvar] habilitado
```

---

## 🎨 DETALHES DE UX

### Animações:

```css
/* Dropdown Menu */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Expansão de Card */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
  opacity: 1;
}

/* Lista (Reordenação) */
.list-move {
  transition: transform 0.3s ease;
}
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
```

### Estados Interativos:

```css
/* Card Hover */
.service-card {
  @apply transition-all duration-300;
}
.service-card:hover {
  @apply shadow-md scale-[1.02];
}

/* Botão Adicionar Campo */
.add-field-button {
  @apply transition-all duration-200;
}
.add-field-button:hover {
  @apply bg-primary-600 shadow-lg scale-105;
}

/* Setas de Reordenação */
.arrow-button {
  @apply transition-all duration-150;
}
.arrow-button:hover:not(:disabled) {
  @apply bg-gray-200 scale-110;
}
.arrow-button:disabled {
  @apply opacity-30 cursor-not-allowed;
}
```

### Ícones por Tipo de Campo:

| Tipo | Ícone | Cor |
|------|-------|-----|
| `text` | `Bars3BottomLeftIcon` | Azul |
| `textarea` | `DocumentTextIcon` | Verde |
| `number` | `HashtagIcon` | Roxo |
| `image` | `CameraIcon` | Rosa |
| `geo` | `MapPinIcon` | Vermelho |
| `select` | `ListBulletIcon` | Amarelo |

---

## 🚀 PRÓXIMOS PASSOS (OPCIONAL)

### 1. Preview em Tempo Real

Adicionar uma seção "Preview" que renderiza o formulário exatamente como o cidadão verá:

```vue
<!-- FormBuilderServico.vue -->
<div class="preview-section">
  <h3>Preview do Formulário</h3>
  <form class="simulated-form">
    <div v-for="campo in campos" :key="campo._id">
      <InputText v-if="campo.type === 'text'" :label="campo.label" />
      <InputTextarea v-else-if="campo.type === 'textarea'" :label="campo.label" />
      <!-- ... outros tipos -->
    </div>
  </form>
</div>
```

### 2. Validação de Campos Customizada

Adicionar regras de validação por campo:

```json
{
  "name": "cpf",
  "label": "CPF",
  "type": "text",
  "required": true,
  "validation": {
    "pattern": "\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}",
    "message": "CPF inválido. Use o formato 000.000.000-00"
  }
}
```

### 3. Campos Condicionais

Mostrar/ocultar campos com base em respostas anteriores:

```json
{
  "name": "outro_tipo",
  "label": "Especifique o tipo",
  "type": "text",
  "required": true,
  "conditional": {
    "field": "tipo_pavimento",
    "operator": "equals",
    "value": "Outro"
  }
}
```

### 4. Import/Export de Templates

Permitir salvar configurações de formulário como templates reutilizáveis:

```javascript
// Exportar
const template = {
  nome: "Template Zeladoria",
  campos: [...campos.value]
}
downloadJSON(template, 'template-zeladoria.json')

// Importar
function importarTemplate(file) {
  const template = JSON.parse(file)
  campos.value = template.campos
}
```

### 5. Arrastar e Soltar (Drag & Drop)

Substituir setas por drag & drop usando Sortable.js:

```javascript
import Sortable from 'sortablejs'

onMounted(() => {
  const el = document.querySelector('.campos-list')
  Sortable.create(el, {
    animation: 150,
    onEnd: (evt) => {
      // Atualizar ordem em campos.value
    }
  })
})
```

---

## 📚 REFERÊNCIAS

- **Vue 3 Documentation:** https://vuejs.org/guide/introduction.html
- **Pinia Documentation:** https://pinia.vuejs.org/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Heroicons:** https://heroicons.com/
- **Leaflet (Mapas):** https://leafletjs.com/
- **Django REST Framework:** https://www.django-rest-framework.org/

---

**🎉 Arquitetura Completa do Form Builder No-Code - Documentada com Excelência!**

*Entrega: 17/11/2024*  
*Build: ✅ Funcionando*  
*Acesse: `/backoffice/configuracoes?aba=servicos`* 🎨
