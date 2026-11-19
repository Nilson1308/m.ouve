# ⚡ Catálogo Dinâmico - Quick Reference

## 🎯 Conceito Principal

**Antes:** Categorias hardcoded ("Ouvidoria", "Zeladoria")  
**Depois:** Tudo dinâmico baseado em `ServicoCatalogo` do backend

---

## 📦 Estrutura de Dados

### Backend → Frontend

```json
GET /api/v1/catalogo-servicos/
[
  {
    "id": "zel-001",
    "nome": "Buracos e Pavimentação",
    "descricao": "Reportar buracos...",
    "categoria": "Zeladoria Urbana",
    "sla_horas": 48,
    "ativo": true,
    "schema_formulario": {
      "type": "object",
      "properties": {
        "tipo_problema": {
          "type": "string",
          "title": "Tipo de Problema",
          "enum": ["buraco", "rachadura"]
        }
      },
      "required": ["tipo_problema"],
      "$metadata": {
        "exige_localizacao": true
      }
    }
  }
]
```

### Frontend → Backend

```json
POST /api/v1/protocolos/
{
  "servico_id": "zel-001",
  "dados_dinamicos": {
    "tipo_problema": "buraco",
    "tamanho_aproximado": "medio"
  },
  "endereco_texto": "Rua X, 123",
  "localizacao": {
    "latitude": -23.5505,
    "longitude": -46.6333
  }
}
```

---

## 🗂️ Arquivos Criados/Modificados

### Novos
1. ✅ `src/stores/catalogo.js` - Store do catálogo
2. ✅ `REFATORACAO_CATALOGO_DINAMICO.md` - Documentação completa

### Refatorados
3. ✅ `src/views/NovaSolicitacaoView.vue` - Cards dinâmicos
4. ✅ `src/views/FormularioSolicitacaoView.vue` - Form dinâmico
5. ✅ `src/stores/protocolos.js` - Action `criarSolicitacaoDinamica()`
6. ✅ `src/router/index.js` - Rota `/solicitacao/:servicoId`

---

## 🔧 Como Usar

### 1. Store do Catálogo

```javascript
import { useCatalogoStore } from '@/stores/catalogo'

const catalogoStore = useCatalogoStore()

// Carregar serviços
await catalogoStore.carregarCatalogo()

// Acessar agrupados por categoria
catalogoStore.servicosPorCategoria
// [
//   { nome: 'Ouvidoria', servicos: [...] },
//   { nome: 'Zeladoria Urbana', servicos: [...] }
// ]

// Buscar serviço por ID
const servico = catalogoStore.getServicoById.value('zel-001')
```

### 2. Renderizar Categorias

```vue
<template>
  <div v-for="categoria in catalogoStore.servicosPorCategoria">
    <h2>{{ categoria.nome }}</h2>
    
    <button 
      v-for="servico in categoria.servicos"
      @click="selecionarServico(servico)"
    >
      {{ servico.nome }}
    </button>
  </div>
</template>
```

### 3. Gerar Formulário Dinâmico

```vue
<template>
  <div v-for="(config, name) in servico.schema_formulario.properties">
    <!-- String -->
    <input 
      v-if="config.type === 'string' && !config.enum"
      v-model="dados[name]"
    />
    
    <!-- Select -->
    <select v-else-if="config.enum">
      <option v-for="val in config.enum">
        {{ val }}
      </option>
    </select>
    
    <!-- Checkbox -->
    <input 
      v-else-if="config.type === 'boolean'"
      type="checkbox"
      v-model="dados[name]"
    />
  </div>
</template>
```

### 4. Enviar Protocolo

```javascript
import { useProtocolosStore } from '@/stores/protocolos'

const protocolosStore = useProtocolosStore()

const payload = {
  servico_id: 'zel-001',
  dados_dinamicos: {
    tipo_problema: 'buraco',
    tamanho_aproximado: 'medio'
  },
  endereco_texto: 'Rua X, 123',
  localizacao: {
    latitude: -23.5505,
    longitude: -46.6333
  }
}

const result = await protocolosStore.criarSolicitacaoDinamica(payload)
// { success: true, protocolo: { id, codigo: "PROT-2024-042" } }
```

---

## 🎨 Mapeamento de Tipos

| JSON Schema | Input HTML | Exemplo |
|-------------|------------|---------|
| `string` | `<input type="text">` | Nome, Endereço |
| `string` + `format: "textarea"` | `<textarea>` | Descrição |
| `string` + `enum` | `<select>` | Tipo de Problema |
| `boolean` | `<input type="checkbox">` | Causa Risco? |
| `integer` | `<input type="number">` | Quantidade |

---

## 🔑 Campos Especiais

### Metadados do Schema

```json
"$metadata": {
  "exige_localizacao": true
}
```

**Uso:**
```javascript
const exige = servico.schema_formulario.$metadata?.exige_localizacao
// true → Mostra campos de GPS e endereço
// false → Esconde campos de localização
```

### Campos Obrigatórios

```json
"required": ["tipo_problema", "tamanho_aproximado"]
```

**Uso:**
```javascript
const isRequired = (fieldName) => {
  return servico.schema_formulario.required.includes(fieldName)
}
```

---

## 🚀 Fluxo Simplificado

```
1. Usuário → "Nova Solicitação"
2. Sistema carrega GET /api/v1/catalogo-servicos/
3. Sistema renderiza cards agrupados por categoria
4. Usuário clica em "Buracos e Pavimentação"
5. Sistema navega para /solicitacao/zel-001
6. Sistema lê schema_formulario do serviço
7. Sistema gera inputs dinamicamente
8. Usuário preenche e envia
9. Sistema faz POST /api/v1/protocolos/ com:
   - servico_id: "zel-001"
   - dados_dinamicos: { ... }
10. Backend valida contra schema_formulario
11. Backend cria Protocolo vinculado ao ServicoCatalogo
12. Frontend redireciona para Dashboard
```

---

## 📊 Estado Atual

### Mock Implementado (6 serviços)

**Ouvidoria:**
- Denúncia
- Solicitação de Informação

**Zeladoria Urbana:**
- Buracos e Pavimentação ← Exige GPS
- Iluminação Pública ← Exige GPS
- Limpeza Urbana ← Exige GPS
- Calçadas e Acessibilidade ← Exige GPS

### Próximos Passos

- [ ] Integrar com API real
- [ ] Validação client-side do schema
- [ ] Upload real de fotos
- [ ] Transcrição de áudio

---

## 🐛 Debug

### Catálogo não carrega?

```javascript
// Console do navegador
import { useCatalogoStore } from '@/stores/catalogo'
const store = useCatalogoStore()

console.log('Serviços:', store.servicos)
console.log('Por categoria:', store.servicosPorCategoria)
console.log('Loading:', store.loading)
console.log('Error:', store.error)
```

### Formulário não gera campos?

```javascript
const servico = catalogoStore.getServicoById.value('zel-001')
console.log('Schema:', servico?.schema_formulario)
console.log('Properties:', servico?.schema_formulario?.properties)
```

### Payload incorreto?

```javascript
// FormularioSolicitacaoView.vue
console.log('Dados Dinâmicos:', dadosDinamicos.value)
console.log('Payload:', {
  servico_id: servicoId.value,
  dados_dinamicos: dadosDinamicos.value,
  endereco_texto: enderecoTexto.value,
  localizacao: localizacao.value
})
```

---

## 📖 Documentação Completa

Ver: `REFATORACAO_CATALOGO_DINAMICO.md`

---

**Versão:** 4.0  
**Build:** ✅ Sem erros (3.5s)  
**Status:** Pronto para integração com API real
