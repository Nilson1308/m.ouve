# ⚡ Quick Start - Dashboard de Eficiência

## 🚀 TESTE RÁPIDO (5 minutos)

### 1. Iniciar Servidor de Desenvolvimento

```bash
cd /var/www/ouve
npm run dev
```

**URL:** `http://localhost:3002/` (ou porta disponível)

---

### 2. Acessar Dashboard

**Navegador:**
```
http://localhost:3002/backoffice/dashboard
```

**Ou:**
1. Fazer login (se necessário)
2. Sidebar → Clicar em **"📊 Visão Executiva"**

---

### 3. Testar com Mock (Backend não pronto)

#### Opção A: Mock Inline (Mais Rápido)

Edite temporariamente:

```javascript
// src/views/backoffice/DashboardEficienciaView.vue
// Linha ~240 (função carregarDados)

async function carregarDados() {
  carregando.value = true
  
  // 🧪 MOCK: Adicione estas linhas
  await new Promise(resolve => setTimeout(resolve, 1500))
  dados.value = {
    tma_global_horas: 132.5,
    tma_variacao: -12.5,
    taxa_sla_cumprido: 87.3,
    sla_variacao: 5.2,
    total_protocolos: 6423,
    total_no_prazo: 5189,
    total_vencido: 1234,
    meta_tma_dias: 5,
    ranking_unidades: [
      {
        id: 1,
        nome: "Secretaria de Mobilidade Urbana",
        sigla: "SEMOB",
        tma_horas: 197,
        total: 850,
        no_prazo: 510,
        vencido: 340
      },
      {
        id: 2,
        nome: "Secretaria de Infraestrutura",
        sigla: "SEINFRA",
        tma_horas: 170,
        total: 1200,
        no_prazo: 960,
        vencido: 240
      },
      {
        id: 3,
        nome: "Secretaria de Educação",
        sigla: "SEDUC",
        tma_horas: 96,
        total: 450,
        no_prazo: 405,
        vencido: 45
      }
      // ... adicione mais secretarias (ver MOCK_DASHBOARD_EFICIENCIA.md)
    ]
  }
  ultimaAtualizacao.value = new Date()
  carregando.value = false
  return
  // 🧪 FIM DO MOCK
  
  // Comente a linha abaixo:
  // const resposta = await dashboardService.getEficiencia()
}
```

**Salvar arquivo** → Vite recarrega automaticamente → Testar dashboard

---

### 4. O Que Você Deve Ver

#### Estado de Loading (1-2 segundos):

```
┌────────────────────────────────────────┐
│ 📊 Dashboard de Eficiência   [↻]      │
├────────────────────────────────────────┤
│ ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒           │ ← 4 skeletons
└────────────────────────────────────────┘
```

#### Após Carregar:

```
┌─────────────────────────────────────────────────────┐
│ 📊 Dashboard de Eficiência             [↻ Atualizar]│
│ 🕐 Última atualização: 17/11/24, 09:30              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│ │TMA     │  │SLA     │  │Vencidos│  │Gargalos│   │
│ │5d 12h  │  │87.3%   │  │1,234   │  │3       │   │
│ │↓ 12%   │  │↑ 5%    │  │19.2%   │  │8 unid. │   │
│ └────────┘  └────────┘  └────────┘  └────────┘   │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ⚠️  Gargalos por Secretaria                         │
│                                                     │
│ 1  SEMOB                          TMA: 8d 5h       │
│    ████████░░░░░░░░░░ 60% | ████░░ 40%            │
│    ⚠️  Situação Crítica                             │
│                                                     │
│ 2  SEINFRA                        TMA: 7d 2h       │
│    ████████████░░ 80% | ██░ 20%                   │
│                                                     │
│ 3  SEDUC                          TMA: 4d          │
│    ██████████████░░ 90% | █░ 10%                  │
└─────────────────────────────────────────────────────┘
```

---

### 5. Testar Interações

#### ✅ Botão Atualizar:
- Click no botão "↻ Atualizar"
- Ícone gira (animate-spin)
- Skeletons aparecem
- Dados recarregam

#### ✅ Responsividade:
- Redimensionar janela
- **Desktop:** 4 colunas de KPIs
- **Tablet:** 2 colunas
- **Mobile:** 1 coluna

#### ✅ Dark Mode:
- Toggle dark mode (se disponível no layout)
- Todas as cores adaptam
- Gradientes mantêm contraste

---

### 6. Verificar Funcionalidades

#### ✅ KPIs:

- [ ] **TMA Global** mostra "5d 12h"
- [ ] Variação mostra "↓ 12%" em verde (melhora)
- [ ] **Taxa SLA** mostra "87.3%"
- [ ] Card é verde (>=80% = success)
- [ ] **Vencidos** mostra "1,234"
- [ ] Card é vermelho (danger)
- [ ] **Gargalos** mostra "3"
- [ ] Contexto mostra "8 unidades monitoradas"

#### ✅ Ranking:

- [ ] SEMOB aparece em 1º (badge vermelho)
- [ ] Barra mostra 60% verde + 40% vermelho
- [ ] Badge "⚠️  Situação Crítica" aparece (>50% vencido)
- [ ] SEINFRA em 2º (badge amarelo)
- [ ] SEDUC em 3º (badge laranja)
- [ ] TMA formatado corretamente

#### ✅ Insights:

- [ ] Seção "💡 Insights Automáticos" aparece
- [ ] Mostra "TMA melhorou 12%..."
- [ ] Mostra "3 secretaria(s) com mais de 30%..."

---

### 7. Testar Estados de Erro

#### Forçar Erro:

```javascript
// DashboardEficienciaView.vue
async function carregarDados() {
  carregando.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // Simular erro
  dados.value = null
  erro.value = 'Erro ao carregar dados'
  
  carregando.value = false
}
```

**Deve mostrar:**
```
┌───────────────────────────────────────────┐
│ ⚠️  Dados Indisponíveis                   │
│                                           │
│ Não foi possível carregar os dados do    │
│ dashboard. Tente novamente em alguns      │
│ instantes.                                │
└───────────────────────────────────────────┘
```

---

### 8. Testar Estado Vazio

#### Forçar Ranking Vazio:

```javascript
dados.value = {
  // ... outros dados
  ranking_unidades: []  // Lista vazia
}
```

**Deve mostrar:**
```
┌───────────────────────────────────────────┐
│            ✅                              │
│      (ícone grande verde)                 │
│                                           │
│   Nenhum Gargalo Identificado             │
│                                           │
│ Todas as unidades estão cumprindo         │
│ os prazos estabelecidos.                  │
└───────────────────────────────────────────┘
```

---

### 9. Build de Produção

```bash
npm run build
```

**Deve mostrar:**
```
✓ built in 6.18s
DashboardEficienciaView.js: 17.73 kB (gzip: 5.45 kB) ✅
```

**Sem erros!**

---

### 10. Remover Mock e Usar API Real

Quando o backend estiver pronto:

1. **Remover mock inline:**
   ```javascript
   // src/views/backoffice/DashboardEficienciaView.vue
   async function carregarDados() {
     carregando.value = true
     erro.value = null
     
     try {
       // ✅ Usar API real
       const resposta = await dashboardService.getEficiencia()
       dados.value = resposta
       ultimaAtualizacao.value = new Date()
     } catch (err) {
       erro.value = 'Erro ao carregar dados do dashboard'
       console.error('Erro:', err)
     } finally {
       carregando.value = false
     }
   }
   ```

2. **Configurar backend URL:**
   ```bash
   # .env.local
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

3. **Testar endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/backoffice/dashboard/eficiencia/
   ```

---

## ✅ CHECKLIST DE TESTE

### Funcional:
- [ ] Dashboard carrega sem erros
- [ ] Skeletons aparecem durante loading
- [ ] 4 KPIs exibidos corretamente
- [ ] Variações mostram setas (verde/vermelho)
- [ ] Ranking ordenado por criticidade
- [ ] Barras duplas (verde + vermelho) funcionam
- [ ] TMA formatado (dias/horas)
- [ ] Badge "Situação Crítica" para >50% vencido
- [ ] Insights automáticos aparecem
- [ ] Botão atualizar funciona
- [ ] Timestamp da última atualização

### Visual:
- [ ] Layout limpo (C-Level)
- [ ] Cores apropriadas (verde/vermelho/amarelo)
- [ ] Hover effects nos cards
- [ ] Transições suaves
- [ ] Dark mode funciona
- [ ] Responsivo (mobile, tablet, desktop)

### Estados:
- [ ] Loading (skeletons)
- [ ] Carregado (dados)
- [ ] Erro (alerta amarelo)
- [ ] Vazio (sem gargalos)

### Performance:
- [ ] Build sem erros
- [ ] Tamanho aceitável (~17 KB)
- [ ] Carregamento rápido
- [ ] Sem memory leaks

---

## 🐛 TROUBLESHOOTING

### Problema: Dashboard não aparece

**Solução:**
1. Verificar rota: `/backoffice/dashboard`
2. Verificar menu lateral
3. Console do navegador (F12)

### Problema: API retorna erro

**Solução:**
1. Usar mock inline (ver passo 3)
2. Verificar CORS no backend
3. Verificar URL da API (.env)

### Problema: Skeletons ficam para sempre

**Solução:**
1. Verificar console (F12)
2. Verificar se `carregando.value = false` é chamado
3. Verificar try/catch na função

### Problema: Cores estranhas em dark mode

**Solução:**
1. Verificar classes `dark:`
2. Limpar cache do navegador
3. Rebuild: `npm run build`

---

## 📚 DOCUMENTAÇÃO COMPLETA

- **Técnica:** `DASHBOARD_EFICIENCIA.md`
- **Visual:** `VISUAL_DASHBOARD_EFICIENCIA.md`
- **Mocks:** `MOCK_DASHBOARD_EFICIENCIA.md`
- **Entrega:** `ENTREGA_SPRINT_5_DASHBOARD.md`
- **API:** `EXEMPLO_API_DASHBOARD.json`

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Testar com dados mockados
2. ✅ Validar visual com stakeholders
3. ✅ Integrar com backend real
4. ✅ Testar performance com dados reais
5. ✅ Deploy em produção

---

**⚡ Dashboard pronto para teste em 5 minutos!**

*Qualquer dúvida, consulte a documentação completa.*
