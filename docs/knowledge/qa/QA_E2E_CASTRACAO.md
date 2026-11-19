# Prova de fogo E2E — Castração de Animais (Sandbox + Elegibilidade + Repescagem)

| Item | Valor |
|------|--------|
| **Produto** | M.Ouve — Chat IA + Form Builder |
| **Versão alvo** | Confiança Operacional (Sandbox v3.9+, Repescagem, Saúde do Chat) |
| **Público** | Product Owners, QA, TI municipal |
| **Objetivo** | Demonstrar que a máquina de estados conversacional trata **caminho feliz**, **repescagem configurada** e **inelegibilidade com bloqueio** sem publicar o serviço no PWA |

---

## Pré-requisitos de execução

1. **Permissão:** Super Admin ou `configuracoes.editar` (catálogo).
2. **Infraestrutura:** Na aba **Configurações → Saúde do Sistema**, `chat_operacional` = verdadeiro (Redis + worker Celery na fila `ouve`). Sem isso, o PWA pode travar em “digitando…”; o **Sandbox** no backoffice ainda roda, mas a extração LLM depende da stack de IA estar configurada.
3. **Ferramenta:** Backoffice → **Configurações** → **Catálogo de Serviços** → editar serviço salvo → **Testar fluxo (Sandbox)**.
4. **Alternativa rápida de seed (opcional):** comando Django `aplicar_exemplo_protecao_animal` (exemplo canônico no repositório). Os cenários abaixo usam o roteiro **documentado neste QA**; se usar o seed, ajuste textos de repescagem conforme a tabela da Seção 1.

---

## Seção 1 — Configuração do serviço no Mapeador IA (Setup)

Crie (ou confira) o serviço **Castração de Animais** com governança mínima: categoria **Proteção Animal**, SLA, unidade responsável, serviço **ativo** e **salvo** (o Sandbox exige `id` persistido).

### 1.1 Cards no Form Builder (Mapeador IA)

Configure **exatamente** os campos abaixo. A ordem recomendada reflete o fluxo do orquestrador (slots vazios → próximo campo obrigatório).

| # | Nome interno | Tipo no Builder | Obrigatório | Pergunta UI (exemplo) | Instrução de extração (`ia_instrucao`) | Repescagem (`ia_repescagem`) |
|---|--------------|-----------------|-------------|------------------------|----------------------------------------|-------------------------------|
| 1 | `tipo` | Seleção (Cão / Gato) | Sim | Qual é o seu animal? | Identificar se é cão ou gato. | — |
| 2 | `idade` | **Número** (ou texto aceitando “anos/meses”) | Sim | Qual a idade dele? | Pergunte a idade do animal. Se for menor que 1 ano ou maior que 8 anos, explique que não é elegível. | Pode informar em anos ou meses (ex.: 2 anos, 8 meses). |
| 3 | `doencas` | **Texto** (ou seleção Sim/Não, se preferir enum) | Sim | Ele possui doenças crônicas? | Pergunte se possui doenças crônicas. | **Por favor, responda apenas se o animal possui alguma doença grave.** |
| 4 | `porte` | Seleção (Pequeno / Médio / Grande) | Sim | Qual o porte? | Registrar porte do animal. | — |
| 5 | `localizacao` | Geolocalização | Sim | Informe sua localização | O slot é preenchido via mapa (não por texto livre). | — |

> **Nota para PO:** O exemplo de referência no código (`protecao_animal_castracao.py`) usa faixa **12 meses a 9 anos** nas regras automáticas. Neste roteiro de QA usamos a narrativa **&lt; 1 ano ou &gt; 8 anos** nas instruções do gestor; o bloqueio efetivo depende das **Regras de elegibilidade** configuradas na etapa seguinte.

### 1.2 Regras de elegibilidade (Bloco “Regras de Protocolo”)

Cadastre ao menos duas regras ativas (tipo **interpretação**), alinhadas às instruções:

| Regra | Campo / Escopo | Condição (linguagem natural para a IA) | Mensagem ao cidadão (bloqueio) |
|-------|----------------|----------------------------------------|--------------------------------|
| **R1 — Idade** | `idade` | Bloquear se idade &lt; 1 ano ou &gt; 8 anos (aceitar “12 anos”, “6 meses”, etc.). | Para castração, o animal precisa ter entre 1 e 8 anos. Para outros casos, procure a Proteção Animal. |
| **R2 — Doença** | `doencas` | Bloquear se indicar doença grave, sintomas ou resposta afirmativa explícita. | Não é possível agendar castração para animal doente neste canal. Procure veterinário ou Proteção Animal. |
| **R3 — Protocolo (opcional)** | Escopo **protocolo** | Bloquear se idade fora da faixa **e/ou** doença grave, avaliando slots já preenchidos. | Pelas informações informadas, este agendamento não pode seguir aqui. |

### 1.3 Como o bloqueio funciona na máquina de estados (comportamento esperado)

1. A cada turno, o orquestrador extrai slots → mescla em `dados_parciais` → chama `passo_deterministico_preenchimento`.
2. **Antes** de avançar para revisão ou protocolo, o módulo `catalogo.eligibility` avalia as regras (determinístico + interpretação LLM quando configurado).
3. Se uma regra dispara:
   - `fluxo_bloqueado` = **true**
   - `resposta_cidadao` = mensagem da regra (sem criar protocolo)
   - No Sandbox: painel **Dados extraídos** mostra os slots já capturados; o chat **não** deve oferecer `acao_ui: revisao_final` nem confirmação de protocolo.
4. Na repescagem: se o cidadão envia texto que **não** preenche o slot em foco, o orquestrador marca repescagem e envia o texto **literal** de `ia_repescagem` (sem nova pergunta genérica gerada por LLM).

**Salvar o serviço** após configurar cards e regras. Só então abrir **Testar fluxo (Sandbox)**.

---

## Seção 2 — Roteiros de teste no Sandbox (casos de uso)

Em todos os cenários:

- Observe o painel **Dados extraídos** (JSON) à direita do celular virtual.
- Registre `acao_ui`, `fluxo_bloqueado` e a última mensagem da IA.
- Após cada passo, use **Reiniciar simulação** antes do próximo cenário.

---

### Cenário A — Caminho feliz (elegível → revisão)

**Objetivo:** Animal elegível preenche todos os slots e chega à **revisão final** simulada.

| Passo | Ação do “cidadão” (Sandbox) | Resultado esperado |
|-------|-----------------------------|-------------------|
| 0 | Abrir Sandbox (primeiro turno automático) | IA cumprimenta / pergunta primeiro slot (`tipo` ou equivalente). `dados_parciais` vazio ou parcial. |
| 1 | Escolher chip **Cão** (se `escolha_campo`) ou escrever “É um cão”. | `tipo` preenchido no JSON. |
| 2 | “Ele tem 3 anos.” | `idade` contém valor interpretável (ex.: `3` ou `3 anos`). Sem `fluxo_bloqueado`. |
| 3 | “Não, ele é saudável.” / chip **Não** | `doencas` preenchido (ex.: “Não”). |
| 4 | Escolher **Médio** (porte). | `porte` preenchido. |
| 5 | Clicar **📍 Abrir mapa (simulado)** | Localização simulada; campo `localizacao` / metadado de GPS tratado pelo backend. |
| 6 | — | `acao_ui` = **`revisao_final`**. Mensagem de resumo. Badge **“Tela de revisão final (simulada)”**. `fluxo_bloqueado` = **false**. |

**Critérios de aprovação**

- [ ] Todos os campos obrigatórios aparecem em **Dados extraídos**.
- [ ] Nenhuma mensagem de inelegibilidade antes da revisão.
- [ ] Estado final compatível com abertura de protocolo no PWA (no Sandbox não há persistência de protocolo).

---

### Cenário B — Repescagem (resposta fora do escopo)

**Objetivo:** Validar que, ao falhar a extração do slot **doenças**, a IA usa o texto **exato** de `ia_repescagem`.

| Passo | Ação do “cidadão” | Resultado esperado |
|-------|-------------------|-------------------|
| 1 | Preencher `tipo` e `idade` (ex.: Cão, 3 anos) como no Cenário A. | Slots OK. |
| 2 | Quando a IA perguntar sobre doenças, enviar: **“Ele é muito fofo.”** | Extração **não** preenche `doencas` (ou valor inválido). |
| 3 | — | Próxima mensagem da IA contém **literalmente** (ou com mínima variação de formatação): *“Por favor, responda apenas se o animal possui alguma doença grave.”* **Não** deve ser uma pergunta genérica inventada (“Conte mais…”). |
| 4 | Responder: **“Não tem doença.”** | `doencas` preenchido; fluxo segue para porte / localização. |

**Critérios de aprovação**

- [ ] Repescagem disparada após resposta evasiva.
- [ ] Texto do balão = fallback configurado no Form Builder.
- [ ] Após resposta válida, o fluxo **não** permanece preso no mesmo slot.

---

### Cenário C — Inelegibilidade e bloqueio (idade 12 anos)

**Objetivo:** Idade fora da faixa dispara regra **R1**; protocolo **não** prossegue.

| Passo | Ação do “cidadão” | Resultado esperado |
|-------|-------------------|-------------------|
| 1 | Informar tipo: “Gato”. | `tipo` OK. |
| 2 | “Ele tem **12 anos**.” | `idade` reflete 12 (ou equivalente). |
| 3 | — | `fluxo_bloqueado` = **true**. Mensagem de bloqueio (**R1**) explicando limite de idade. Sem `revisao_final`. |
| 4 | Tentar enviar nova mensagem (“Mas ele é saudável…”) | Fluxo permanece bloqueado ou reitera inelegibilidade; **não** gera revisão/protocolo. |

**Critérios de aprovação**

- [ ] `dados_parciais` mostra `idade` coletada (prova de que a extração funcionou).
- [ ] Banner / balão de bloqueio visível no Sandbox.
- [ ] Campo de entrada pode ficar desabilitado (`fluxoEncerrado`) após bloqueio.

---

## Matriz de rastreabilidade (requisito → evidência)

| Capacidade | Cenário | Evidência |
|------------|---------|-----------|
| Sandbox dry-run | A, B, C | Histórico no celular + JSON `dados_parciais` |
| Repescagem (`ia_repescagem`) | B | Print ou log da mensagem literal |
| Elegibilidade / `fluxo_bloqueado` | C | `fluxo_bloqueado: true` no comportamento do chat |
| Revisão final | A | `acao_ui: revisao_final` |
| Confiança operacional (NOC) | Pré-requisito | Aba Saúde do Sistema verde antes de testes no PWA |

---

## Registro de execução (template)

| Campo | Preenchimento |
|-------|----------------|
| **Executor** | |
| **Data** | |
| **Ambiente** | Homologação / Produção |
| **ID do serviço (UUID)** | |
| **Build / release** | |
| **Cenário A** | Aprovado / Reprovado — observações: |
| **Cenário B** | Aprovado / Reprovado — observações: |
| **Cenário C** | Aprovado / Reprovado — observações: |
| **Anexos** | Capturas do Sandbox + JSON final |

---

## Referências técnicas (somente leitura)

- `API_CONTRACT.md` — Sandbox (`POST .../sandbox`), `fluxo_bloqueado`, `revisao_final`, elegibilidade v3.x
- `backend/catalogo/exemplos/protecao_animal_castracao.py` — exemplo canônico de schema e regras
- `backend/atendimentos/llm_orchestrator.py` — repescagem estrita via `ia_repescagem`
- `src/components/backoffice/catalogo/SandboxChat.vue` — UI da Prova de Fogo no backoffice

---

*Documento de QA — Prova de Fogo Castração. Última atualização: 17/11/2026.*