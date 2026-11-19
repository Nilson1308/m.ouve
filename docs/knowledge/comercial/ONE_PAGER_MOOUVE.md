# M.Ouve (Ouv.IA) — One-pager comercial

**Versão:** 1.0 · **Público-alvo:** prefeituras, consórcios, integradores GovTech · **Modelo:** licença + implantação (instância dedicada por município)

---

## Em uma frase

**Ouvidoria digital que o cidadão usa como aplicativo, que a gestão opera como sala de comando — com IA na entrada, scatter-gather entre secretarias e indicadores na saída.**

---

## O problema que resolvemos

| Dor do gestor | Como o mercado costuma responder | Como o M.Ouve responde |
|---------------|----------------------------------|-------------------------|
| Cidadão abandona formulário longo | PDF ou portal com 30+ campos | **Chat com IA** + coleta dinâmica por serviço |
| Demanda “some” entre secretarias | E-mail e planilha | **Protocolo único** + OS por setor (scatter-gather) |
| Ouvidor sem visão de prazo | Protocolo sem SLA operacional | **Kanban**, TMA/SLA e alertas internos |
| Imprensa / TCE pedem rastro | Anexos soltos | **Histórico auditável** (chat, tramitação, evidências) |
| Eventos em massa (buracos, enchentes) | Um protocolo = um ticket | **Super OS** e clusters geográficos com IA |

---

## Personas e ganho principal

| Persona | O que ela quer | O que vender |
|---------|----------------|--------------|
| **Prefeito / secretário executivo** | Menos reclamação, número para reunião | Dashboards TMA/SLA, mapa GIS, inelegibilidade IA (“escudo político”) |
| **Ouvidor(a) municipal** | Triagem rápida e resposta oficial defensável | Mesa Kanban, validação gather, textos padrão, CSAT |
| **Gestor de secretaria** | Fila clara da equipe | Painel setorial, OS, magic link para campo |
| **Servidor de campo** | Registrar serviço sem burocracia | Formalização de OS, fotos, link mágico |
| **Cidadão** | Resolver sem ir ao balcão | PWA, protocolo, notificações, avaliação pós-atendimento |

---

## Pacotes sugeridos (referência de proposta)

Valores abaixo são **faixas de referência para negociação** — ajustar por porte (IBGE), nº de servidores e escopo de catálogo.

### Bronze — “Canal digital + Mesa”

**Para:** município que quer **substituir formulário legado** e organizar a ouvidoria.

- PWA cidadão (catálogo, chat IA, protocolos, CSAT)
- Backoffice: mesa Kanban, despacho e detalhe do protocolo
- RBAC básico (perfis padrão, 1 unidade ouvidoria + N secretarias acionáveis)
- Implantação: até **15 serviços** no catálogo, treinamento remoto (8h)
- Suporte: 8×5, correções de segurança

**Indicador de preço (referência):** licença anual **R$ 48k – 72k** + setup único **R$ 25k – 40k**.

### Prata — “Operação integrada” (recomendado)

**Para:** município médio que quer **secretarias na mesma plataforma**.

- Tudo do Bronze
- Painel setorial, assinaturas, evidências, magic link
- Dashboards eficiência + mapa GIS + matriz de qualidade (CSAT real)
- Super OS e sugestões de cluster (IA governada)
- Form Builder: criação/edição de serviços pela equipe
- Web Push (VAPID) + notificações internas
- Implantação: até **40 serviços**, workshop presencial ou remoto (16h)
- Suporte: 8×5 com SLA de resposta 2 dias úteis

**Indicador de preço (referência):** licença anual **R$ 95k – 140k** + setup **R$ 55k – 85k**.

### Ouro — “Governança e expansão”

**Para:** capital regional, **consórcio** ou secretaria que exige governança forte.

- Tudo do Prata
- Ambiente homologação dedicado, plano de continuidade documentado
- Customização de integrações (webhook / API documentada)
- Pacote LGPD: orientação de políticas, retenção, relatório de tratamento
- Capacitação ampliada (gestores + ouvidoria + TI)
- Suporte: estendido com janela para releases planejadas

**Indicador de preço (referência):** licença anual **sob consulta** (a partir de **R$ 180k**) + setup **R$ 100k+**.

> **Nota comercial:** na fase atual o produto é entregue como **instância dedicada por cliente** (não multi-tenant SaaS compartilhado). Isso é **vantagem em edital** (dados no ambiente do cliente ou servidor municipal).

---

## Diferenciais vs. “prateleira”

1. **Scatter-gather nativo** — um protocolo, várias secretarias, validação única ao cidadão.  
2. **IA conversacional + inelegibilidade** — menos triagem humana em demanda inválida.  
3. **PWA instalável + Web Push** — engajamento sem depender de app nas stores.  
4. **Catálogo versionado (Form Builder)** — secretaria adapta serviço sem desenvolvedor.  
5. **RBAC + escopo por unidade** — adequado a ambiente multi-secretaria.  
6. **Manuais e FAQs embutidos** — reduz custo de suporte no 1º ano.

---

## Objeções frequentes (e respostas)

| Objeção | Resposta curta |
|---------|----------------|
| “Já temos ouvidoria / 156.” | O M.Ouve **não substitui o ERP**; é o **canal cidadão + orquestração** entre secretarias. Integra via API ou exportação. |
| “IA é moda / dá erro.” | IA na **entrada** (chat e elegibilidade); decisão oficial continua **humana** na validação gather. Sandbox e auditoria de chat. |
| “Cidadão não usa tecnologia.” | PWA leve, linguagem natural, notificações; CSAT mede adoção real. |
| “E a LGPD?” | Dados em instância dedicada, RBAC, logs; pacote Ouro inclui apoio documental (DPA/RIPD com jurídico do cliente). |
| “E se o Groq/LLM cair?” | Fila Celery, retry e possibilidade de provedor alternativo; operação manual do protocolo permanece no backoffice. |
| “Preço de software global.” | Comparar **custo de equipe** evitando retrabalho entre secretarias + tempo de resposta (SLA). Licença menor que um analista. |
| “Precisamos de licitação.” | Produto com **documentação, API e operação** prontos para anexo técnico; implantação como serviço licitável separado. |

---

## Roteiro de demonstração (15 minutos)

| Min | Ator | Roteiro |
|-----|------|---------|
| 0–2 | Vendas | **Contexto:** “Uma solicitação entra pelo celular e sai com protocolo, prazo e secretaria certa.” |
| 2–5 | PWA | **Nova solicitação** → chat IA → foto/local → **protocolo gerado**. Destacar indicador “IA analisando”. |
| 5–7 | PWA | **Dashboard** → detalhe do protocolo → **ativar notificações** (nudge). Mencionar ajuda `/app/ajuda`. |
| 7–10 | Backoffice | **Mesa Kanban** → despachar para 2 setores → mostrar coluna **Aguardando validação** (tooltips). |
| 10–12 | Backoffice | **Detalhe 360º** — cidadão + demanda abertos; expandir OS / histórico se perguntarem. |
| 12–14 | Backoffice | **Visão Executiva** — TMA, SLA; opcional: mapa GIS ou Super OS se público técnico. |
| 14–15 | Fechamento | Repetir pacote **Prata** + próximo passo: piloto 90 dias, catálogo inicial, métricas CSAT/SLA. |

**Dica:** usar protocolo real de homologação (Mogi das Cruzes) para credibilidade; evitar login Gov.br na demo se ainda não estiver no escopo do cliente.

---

## Critérios de sucesso do piloto (90 dias)

- ≥ **70%** dos novos atendimentos via PWA/chat (meta negociável).  
- **TMA** documentado antes/depois no dashboard.  
- ≥ **1 secretaria** operando painel setorial com OS formalizadas.  
- **CSAT** medido em ≥ **30%** dos protocolos resolvidos.  
- Ouvidor treinado com **manual in-app** (`/backoffice/manual`) sem suporte diário.

---

## Próximos passos comerciais

1. Alinhar **pacote** (Bronze/Prata/Ouro) e população alvo.  
2. Definir **catálogo inicial** (lista de serviços no Anexo I da proposta).  
3. Proposta comercial + **cronograma de implantação** (4–8 semanas típico Prata).  
4. Contrato: licença anual + setup + SLA de suporte.  
5. Kick-off: RBAC, VAPID, importação de serviços, treinamento mesa.

---

## Contato e materiais de apoio

- Produto: [`README.md`](../../../README.md)  
- Operação técnica: [`OPERACOES.md`](../../../OPERACOES.md)  
- Contrato de integração: [`API_CONTRACT.md`](../../../API_CONTRACT.md)  
- Repositório: https://github.com/Nilson1308/m.ouve.git  

**Elaborado para:** equipe comercial e integradores parceiros do M.Ouve · Revisar valores e SLAs conforme política comercial da empresa licenciante.