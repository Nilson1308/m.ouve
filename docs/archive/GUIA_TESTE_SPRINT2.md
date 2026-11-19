# 🧪 GUIA DE TESTE - SPRINT 2

## ✅ Checklist Completo para Validação

---

## 🚀 PRÉ-REQUISITOS

1. ✅ **Node.js** instalado (v18+)
2. ✅ **NPM** instalado
3. ✅ Projeto rodando em: `http://localhost:3002`

### Iniciar servidor:
```bash
cd /var/www/ouve
npm run dev
```

---

## 📋 ROTEIRO DE TESTES

### 🔹 TESTE 1: Mesa de Trabalho (Visualização Kanban)

**Objetivo:** Validar o Kanban e interações básicas

#### Passos:
1. Acesse: `http://localhost:3002/backoffice/mesa-trabalho`
2. Verifique que o Kanban está visível com 4 colunas
3. Identifique os protocolos em cada coluna

#### Validações:
- [ ] Header "Mesa de Trabalho" visível
- [ ] 4 colunas renderizadas: NOVO, EM ANDAMENTO, AGUARDANDO REVISÃO, CONCLUÍDO
- [ ] Contadores nas colunas (ex: "NOVO (8)")
- [ ] Cards de protocolos renderizados
- [ ] Barra de SLA visível nos cards (verde/amarelo/vermelho)
- [ ] Badges de status coloridos
- [ ] Hover effect nos cards funciona

#### Ações:
- [ ] Clicar em um card → Abre detalhes do protocolo
- [ ] Clicar em "👁️ Ver Detalhes" → Abre detalhes
- [ ] Clicar em "📤 Despachar" → Abre modal de despacho

**Resultado esperado:** Kanban renderizado corretamente, cards clicáveis, modal abre.

---

### 🔹 TESTE 2: Mesa de Trabalho (Visualização Lista)

**Objetivo:** Validar a tabela e ordenação

#### Passos:
1. Na Mesa de Trabalho, clique no toggle "📊 Lista"
2. Verifique que a visualização mudou para tabela

#### Validações:
- [ ] Tabela renderizada com 8 colunas
- [ ] Header da tabela com títulos corretos
- [ ] Linhas de protocolos visíveis
- [ ] Badges nas células (status, urgência, SLA)
- [ ] Hover effect nas linhas

#### Ações:
- [ ] Clicar em uma linha → Abre detalhes
- [ ] Ordenar por coluna (se implementado)
- [ ] Alternar de volta para Kanban

**Resultado esperado:** Tabela densa, profissional, linhas clicáveis.

---

### 🔹 TESTE 3: Filtros e Busca

**Objetivo:** Validar os filtros rápidos

#### Passos:
1. Na Mesa de Trabalho (qualquer visualização)
2. Observe os badges de filtro no header

#### Validações:
- [ ] Badge "⚡ SLA Vencido (X)" visível
- [ ] Badge "🔴 Urgentes (X)" visível
- [ ] Campo de busca presente

#### Ações:
- [ ] Clicar em "SLA Vencido" → Filtra protocolos
- [ ] Clicar novamente → Remove filtro
- [ ] Clicar em "Urgentes" → Filtra protocolos
- [ ] Digitar no campo de busca → Filtra em tempo real
- [ ] Limpar busca → Volta ao estado original

**Resultado esperado:** Filtros funcionam, lista atualiza, badges ficam ativos.

---

### 🔹 TESTE 4: Modal de Despacho (Scatter)

**Objetivo:** Validar o modal Scatter-Gather

#### Passos:
1. Na Mesa de Trabalho, clique em "📤 Despachar" em um protocolo
2. Modal deve abrir

#### Validações:
- [ ] Modal renderizado sobre a página
- [ ] Backdrop escuro visível
- [ ] Título "Despachar Protocolo"
- [ ] Lista de unidades disponíveis
- [ ] Checkboxes funcionam
- [ ] Campos de instrução e prazo por unidade

#### Ações:
- [ ] Selecionar 2 ou mais unidades
- [ ] Preencher instruções e prazos
- [ ] Clicar "Confirmar" → Fecha modal (log no console)
- [ ] Abrir novamente e clicar "Cancelar" → Fecha sem ação
- [ ] Clicar fora do modal → Fecha

**Resultado esperado:** Modal funcional, validações OK, fecha corretamente.

---

### 🔹 TESTE 5: Navegação para Detalhes

**Objetivo:** Validar a navegação

#### Passos:
1. Na Mesa de Trabalho, clique em qualquer protocolo
2. A URL deve mudar para `/backoffice/protocolo/:id`

#### Validações:
- [ ] Página de detalhes carrega
- [ ] URL mudou corretamente
- [ ] Botão "Voltar" (←) visível no header
- [ ] Informações do protocolo renderizadas

#### Ações:
- [ ] Clicar em "Voltar" → Retorna à Mesa de Trabalho
- [ ] Navegar via URL diretamente → Carrega detalhes

**Resultado esperado:** Navegação fluida, SPA sem reload.

---

### 🔹 TESTE 6: Detalhes do Protocolo (Header)

**Objetivo:** Validar o header fixo

#### Passos:
1. Estar na tela de detalhes de um protocolo
2. Observar o header superior

#### Validações:
- [ ] Número do protocolo em destaque (ex: PROT-2024-042)
- [ ] Data de abertura formatada
- [ ] Badge de Status visível e colorido
- [ ] Badge de SLA colorido (verde/amarelo/vermelho)
- [ ] Badge de Serviço visível
- [ ] Badge de Cidadão visível
- [ ] Ícones de ações (Imprimir, Compartilhar, Menu)

#### Ações:
- [ ] Scroll na página → Header deve permanecer fixo (sticky)
- [ ] Hover nos ícones → Tooltip aparece
- [ ] Clicar em ações → Log no console

**Resultado esperado:** Header informativo, sticky, ações visíveis.

---

### 🔹 TESTE 7: Coluna Esquerda (Dados Coletados)

**Objetivo:** Validar os dados extraídos pela IA

#### Passos:
1. Na tela de detalhes, observar a coluna esquerda
2. Localizar o card "Dados Coletados pela IA"

#### Validações:
- [ ] Card renderizado com ícone de CPU
- [ ] Tabela de dados visível
- [ ] Cada linha tem: Campo (esquerda) e Valor (direita)
- [ ] 9 campos renderizados (do mock)
- [ ] Background alternado (zebrado)
- [ ] Hover effect nas linhas

#### Ações:
- [ ] Hover nas linhas → Background muda sutilmente
- [ ] Scroll na tabela (se necessário)

**Resultado esperado:** Dados tabulados, legíveis, profissionais.

---

### 🔹 TESTE 8: Coluna Esquerda (Localização)

**Objetivo:** Validar o card de localização

#### Passos:
1. Na coluna esquerda, localizar "Localização"

#### Validações:
- [ ] Card renderizado com ícone de pin
- [ ] Endereço formatado corretamente
- [ ] CEP, bairro, cidade visíveis
- [ ] Ponto de referência exibido
- [ ] Mapa placeholder renderizado
- [ ] Pino animado no centro do mapa
- [ ] Coordenadas lat/lng exibidas

#### Ações:
- [ ] Observar animação do pino (pulsante)
- [ ] Verificar que o mapa é um placeholder

**Resultado esperado:** Localização clara, mapa visual.

---

### 🔹 TESTE 9: Coluna Esquerda (Chat Auditoria)

**Objetivo:** Validar o histórico de chat

#### Passos:
1. Na coluna esquerda, localizar "Histórico de Atendimento"

#### Validações:
- [ ] Card renderizado com ícone de chat
- [ ] Título "Histórico de Atendimento"
- [ ] Contador de mensagens (ex: "11 mensagens")
- [ ] Botão de expandir/colapsar (▼)
- [ ] Chat expandido por padrão

#### Ações:
- [ ] Clicar no header → Chat colapsa com animação
- [ ] Clicar novamente → Chat expande com animação
- [ ] Observar timeline de mensagens
- [ ] Diferenciar mensagens: IA (azul) vs Cidadão (verde)
- [ ] Ver anexos (fotos) nas mensagens
- [ ] Clicar em foto → Abre em nova aba

#### Validações do Chat Expandido:
- [ ] Timeline vertical renderizada
- [ ] Indicadores coloridos (IA: azul, Cidadão: verde)
- [ ] Timestamps formatados
- [ ] Mensagens legíveis
- [ ] Estatísticas no rodapé (Total, IA, Cidadão)

**Resultado esperado:** Chat auditável, expansível, fotos clicáveis.

---

### 🔹 TESTE 10: Coluna Direita (Ações de Validação)

**Objetivo:** Validar o card de ações

#### Passos:
1. Na tela de detalhes, observar a coluna direita
2. Card de "Ações de Validação" no topo

#### Validações:
- [ ] Card sticky (acompanha scroll)
- [ ] Título "Ações de Validação"
- [ ] Select de "Resposta ao Cidadão"
- [ ] Textarea de "Observações Adicionais"
- [ ] Botão verde "✅ Validar e Encerrar Protocolo"
- [ ] Botão vermelho "↶ Devolver à Secretaria"
- [ ] Botões secundários "Editar" e "Relatório"

#### Ações:
- [ ] Abrir select → 4 opções de resposta padrão
- [ ] Selecionar uma resposta → Preview aparece
- [ ] Digitar observações → Preview atualiza
- [ ] Clicar "Validar" SEM resposta → Botão desabilitado
- [ ] Selecionar resposta e clicar "Validar" → Log no console
- [ ] Clicar "Devolver" → Modal abre

**Resultado esperado:** Ações intuitivas, validações funcionam, preview atualiza.

---

### 🔹 TESTE 11: Modal de Devolução

**Objetivo:** Validar a devolução à secretaria

#### Passos:
1. No card de ações, clicar "Devolver à Secretaria"

#### Validações:
- [ ] Modal renderizado
- [ ] Título "Devolver à Secretaria"
- [ ] Select "Motivo da Devolução" com 5 opções
- [ ] Textarea "Justificativa Detalhada"
- [ ] Botões "Cancelar" e "Confirmar Devolução"

#### Ações:
- [ ] Tentar confirmar SEM preencher → Botão desabilitado
- [ ] Selecionar motivo → Botão ainda desabilitado
- [ ] Digitar justificativa → Botão habilita
- [ ] Clicar "Confirmar" → Log no console, modal fecha
- [ ] Abrir novamente e clicar "Cancelar" → Fecha sem ação

**Resultado esperado:** Validações rigorosas, modal funcional.

---

### 🔹 TESTE 12: Coluna Direita (Timeline de Ordens)

**Objetivo:** Validar a timeline Scatter-Gather

#### Passos:
1. Na coluna direita, abaixo das ações
2. Localizar "Ordens de Serviço"

#### Validações:
- [ ] Título "Ordens de Serviço"
- [ ] Contador de unidades (ex: "2 unidades envolvidas")
- [ ] Timeline vertical renderizada
- [ ] 2 ordens de serviço visíveis (Obras + Defesa Civil)
- [ ] Indicadores coloridos na timeline (verde para concluído)

#### Validações por Ordem:
- [ ] Nome da unidade (ex: "Secretaria de Obras Públicas")
- [ ] Equipe responsável
- [ ] ID da ordem (ex: "OS-2024-042-01")
- [ ] Badge de status ("Concluído")
- [ ] Badge de prioridade ("Alta")
- [ ] Instrução original destacada
- [ ] Prazo e data de conclusão
- [ ] Observações da equipe (feedback)
- [ ] Materiais utilizados (badges)
- [ ] Galeria de fotos (3 fotos em grid)
- [ ] Timestamps de início e conclusão
- [ ] Duração calculada (ex: "6h 15min")

#### Ações:
- [ ] Hover nos cards → Sombra aumenta
- [ ] Clicar nas fotos → Abre em nova aba
- [ ] Observar cores: Verde (concluído), Laranja (DC)

**Resultado esperado:** Timeline visual, informativa, fotos clicáveis.

---

### 🔹 TESTE 13: Coluna Direita (Resumo Executivo)

**Objetivo:** Validar o card de resumo

#### Passos:
1. Na coluna direita, ao final da timeline
2. Localizar "Resumo Executivo"

#### Validações:
- [ ] Card com gradiente de fundo
- [ ] Badge de "Status Geral"
- [ ] "Ordens Concluídas: 2 de 2"
- [ ] "Tempo Total: Xd Xh"

#### Ações:
- [ ] Verificar que os dados estão corretos
- [ ] Badge de status corresponde ao protocolo

**Resultado esperado:** Resumo claro e preciso.

---

### 🔹 TESTE 14: Dark Mode

**Objetivo:** Validar o tema escuro

#### Passos:
1. Ativar o Dark Mode (botão no header)
2. Navegar por todas as telas

#### Validações:
- [ ] Mesa de Trabalho em dark mode
- [ ] Detalhes do protocolo em dark mode
- [ ] Cards com fundo escuro
- [ ] Texto legível (contraste adequado)
- [ ] Badges adaptados
- [ ] Timeline visível
- [ ] Fotos com borda adaptada
- [ ] Modais em dark mode

#### Ações:
- [ ] Alternar entre light/dark → Transição suave
- [ ] Verificar todos os componentes

**Resultado esperado:** Dark mode completo e legível.

---

### 🔹 TESTE 15: Responsividade (Desktop)

**Objetivo:** Validar em diferentes resoluções

#### Passos:
1. Redimensionar a janela do navegador
2. Testar em: 1920px, 1440px, 1024px

#### Validações:
- [ ] Layout split view mantém proporções
- [ ] Header sticky funciona
- [ ] Cards não quebram
- [ ] Timeline legível
- [ ] Fotos em grid adaptam

**Resultado esperado:** Layout fluido, nada quebrado.

---

### 🔹 TESTE 16: Performance

**Objetivo:** Validar a velocidade

#### Passos:
1. Abrir DevTools (F12)
2. Aba "Network"
3. Recarregar a página

#### Validações:
- [ ] Tempo de carregamento < 2s
- [ ] Lazy loading funcionando
- [ ] Imagens carregam progressivamente
- [ ] Sem erros no console

#### Ações:
- [ ] Navegar entre páginas → Transições rápidas
- [ ] Abrir modais → Renderização imediata

**Resultado esperado:** App rápido e responsivo.

---

### 🔹 TESTE 17: Console (Erros)

**Objetivo:** Validar ausência de erros

#### Passos:
1. Abrir DevTools (F12)
2. Aba "Console"
3. Navegar por todas as telas

#### Validações:
- [ ] Nenhum erro vermelho
- [ ] Nenhum warning crítico
- [ ] Logs informativos OK (de eventos)

**Resultado esperado:** Console limpo, sem erros.

---

## ✅ CHECKLIST FINAL

### Funcionalidades:
- [ ] Mesa de Trabalho (Kanban)
- [ ] Mesa de Trabalho (Lista)
- [ ] Filtros e Busca
- [ ] Modal de Despacho
- [ ] Navegação para Detalhes
- [ ] Header Fixo
- [ ] Dados Coletados IA
- [ ] Localização com Mapa
- [ ] Chat Auditoria
- [ ] Ações de Validação
- [ ] Modal de Devolução
- [ ] Timeline de Ordens
- [ ] Galeria de Fotos
- [ ] Resumo Executivo

### Qualidade:
- [ ] Dark Mode
- [ ] Responsivo
- [ ] Performance
- [ ] Sem erros no console
- [ ] Build compilado

---

## 🎯 BUGS CONHECIDOS (Nenhum!)

✅ Nenhum bug identificado até o momento.

---

## 🐛 COMO REPORTAR BUGS

Se encontrar algum problema:

1. **Console:** Tire um print do console (F12)
2. **Tela:** Tire um screenshot da tela
3. **Passos:** Descreva como reproduzir
4. **Navegador:** Informe (Chrome, Firefox, etc.)

---

## 🎉 CONCLUSÃO

Se todos os testes passarem, a **Sprint 2 está 100% funcional**!

### Próximos passos:
1. Integração com backend
2. Testes de usuário reais
3. Ajustes de UX baseados em feedback

---

**🎊 Boa sorte nos testes!**

*Guia criado em 13/11/2024*
