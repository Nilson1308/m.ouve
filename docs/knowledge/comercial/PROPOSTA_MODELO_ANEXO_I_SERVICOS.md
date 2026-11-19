# Proposta comercial — M.Ouve (Ouv.IA)

**Modelo de referência** para propostas a prefeituras. Ajustar dados do contratante, valores finais e cláusulas com o jurídico da licenciante.

| Campo | Preencher |
|-------|-----------|
| **Contratante** | Município de _____________________________ |
| **CNPJ** | _____________________________ |
| **Proponente / Licenciante** | _____________________________ |
| **Data da proposta** | ____/____/________ |
| **Validade** | 30 dias |
| **Pacote ofertado** | ☐ Bronze ☐ Prata ☐ Ouro |
| **Vigência da licença** | 12 meses, renovável |

---

## 1. Objeto

Fornecimento de **licença de uso** e **serviços de implantação** da plataforma **M.Ouve (Ouv.IA)** — ouvidoria digital com canal PWA ao cidadão, backoffice de protocolos e ordens de serviço, painéis gerenciais e módulos conforme pacote contratado — em **instância dedicada** (ambiente do contratante ou infraestrutura acordada).

---

## 2. Escopo por pacote (resumo)

| Item | Bronze | Prata | Ouro |
|------|:------:|:-----:|:----:|
| PWA cidadão (catálogo, chat IA, protocolos, CSAT) | ✓ | ✓ | ✓ |
| Mesa Kanban e despacho | ✓ | ✓ | ✓ |
| Painel setorial, OS, magic link | — | ✓ | ✓ |
| Dashboards TMA/SLA, mapa GIS, matriz qualidade | — | ✓ | ✓ |
| Super OS / clusters IA | — | ✓ | ✓ |
| Form Builder (edição de serviços) | — | ✓ | ✓ |
| Web Push (VAPID) | — | ✓ | ✓ |
| Ambiente de homologação | — | — | ✓ |
| Integrações API/webhook customizadas | — | — | ✓ |
| Apoio documental LGPD | — | — | ✓ |

Detalhamento completo: [`ONE_PAGER_MOOUVE.md`](ONE_PAGER_MOOUVE.md).

---

## 3. Investimento (referência — preencher valores fechados)

| Componente | Bronze | Prata | Ouro |
|------------|--------|-------|------|
| **Licença anual** | R$ ________ | R$ ________ | R$ ________ |
| **Setup / implantação (único)** | R$ ________ | R$ ________ | R$ ________ |
| **Treinamento incluído** | 8h remoto | 16h pres./remoto | Ampliado |
| **Suporte** | 8×5 | 8×5, SLA 2 DU | Estendido |

**Forma de pagamento sugerida:** ___% na assinatura; ___% na homologação; licença anual à vista ou parcelada conforme edital/contrato.

---

## 4. Cronograma de implantação (modelo — pacote Prata)

| Semana | Entrega |
|--------|---------|
| 1 | Kick-off, RBAC, ambientes, VAPID, importação inicial do Anexo I |
| 2 | Ajuste de formulários (Form Builder), testes PWA |
| 3 | Treinamento ouvidoria + mesa; piloto interno |
| 4 | Treinamento 1ª secretaria piloto; painel setorial |
| 5–6 | Ampliação de secretarias; dashboards |
| 7–8 | Go-live assistido, CSAT, relatório de encerramento de implantação |

Bronze: comprimir para **4 semanas**. Ouro: incluir homologação e integrações (**8–12 semanas**).

---

## 5. Critérios de aceite do piloto (90 dias pós go-live)

- Catálogo conforme **Anexo I** publicado e acessível no PWA.
- Perfis RBAC documentados e homologados pelo ouvidor.
- ≥ **1 secretaria** operando OS no painel setorial (exceto Bronze, se não contratado).
- Relatório de **TMA/SLA** exportável pelo dashboard.
- Métricas acordadas em acta de kick-off (meta sugerida: ≥ 30% CSAT em protocolos resolvidos).

---

## 6. Responsabilidades

| Contratante | Licenciante |
|-------------|-------------|
| Infraestrutura de hospedagem (se on-premise), DNS, certificados TLS | Licença, atualizações corretivas de segurança no período |
| Definição do catálogo e textos oficiais (Anexo I) | Implantação, treinamento conforme pacote |
| Usuários, unidades organizacionais e políticas internas | Suporte conforme SLA |
| Jurídico: base legal LGPD, políticas de privacidade publicadas | Documentação técnica (`API_CONTRACT`, `OPERACOES`) |

---

## 7. Anexos desta proposta

| Anexo | Documento |
|-------|-----------|
| **I** | Catálogo inicial de serviços (este arquivo, seção abaixo) |
| **II** | [`ONE_PAGER_MOOUVE.md`](ONE_PAGER_MOOUVE.md) ou PDF exportado |
| **III** | Roteiro de demonstração (15 min) — seção no one-pager |
| **IV** | Especificação técnica resumida — [`API_CONTRACT.md`](../../../API_CONTRACT.md) (referência) |

---

# ANEXO I — Catálogo inicial de serviços

**Instruções:** listar cada serviço que será publicado no PWA na data de go-live. Para cada linha, a equipe de implantação configura categoria, secretaria responsável, SLA alvo, formulário (campos) e regras de elegibilidade/IA quando aplicável.

**Limite contratual:** Bronze até **15** linhas marcadas “Go-live”; Prata até **40**; Ouro conforme plano de expansão.

| # | Nome do serviço (cidadão) | Categoria / ícone | Secretaria / unidade destino | SLA alvo (dias úteis) | Exige geolocalização | Exige foto | Go-live fase 1 |
|---|---------------------------|-------------------|------------------------------|----------------------:|:--------------------:|:----------:|:--------------:|
| 1 | Denúncia anônima | Ouvidoria | Ouvidoria Municipal | 10 | — | Opcional | ☐ |
| 2 | Pedido de informação (LAI) | Ouvidoria | Ouvidoria Municipal | 20 | — | — | ☐ |
| 3 | Reclamação geral | Ouvidoria | Ouvidoria Municipal | 15 | — | Opcional | ☐ |
| 4 | Buraco / pavimentação | Zeladoria urbana | Secretaria de Obras | 5 | ✓ | ✓ | ☐ |
| 5 | Iluminação pública | Zeladoria urbana | Secretaria de Obras / Energia | 7 | ✓ | Opcional | ☐ |
| 6 | Limpeza urbana / entulho | Zeladoria urbana | Serviços Urbanos | 3 | ✓ | ✓ | ☐ |
| 7 | Calçada / acessibilidade | Zeladoria urbana | Secretaria de Obras | 10 | ✓ | Opcional | ☐ |
| 8 | Poda / árvore em via pública | Meio ambiente | Secretaria de Meio Ambiente | 7 | ✓ | ✓ | ☐ |
| 9 | Coleta irregular de lixo | Meio ambiente | Serviços Urbanos | 3 | ✓ | ✓ | ☐ |
| 10 | Alagamento / bueiro | Obras / drenagem | Defesa Civil / Obras | 2 | ✓ | ✓ | ☐ |
| 11 | Sinalização viária | Trânsito | CET / Trânsito | 10 | ✓ | ✓ | ☐ |
| 12 | Fiscalização de barulho | Fiscalização | Postura / Fiscalização | 15 | ✓ | — | ☐ |
| 13 | Matrícula escolar (orientação) | Educação | SME — ouvidoria educação | 5 | — | — | ☐ |
| 14 | Agendamento UBS (encaminhamento) | Saúde | SMS — ouvidoria saúde | 5 | — | — | ☐ |
| 15 | Iluminação em praça / parque | Zeladoria urbana | Serviços Urbanos | 7 | ✓ | Opcional | ☐ |
| 16 | *Reserva — adicionar linhas* | | | | | | ☐ |
| … | *(até limite do pacote)* | | | | | | |

### Campos adicionais (por serviço — usar folha extra se necessário)

Para serviços com formulário customizado, anexar folha com:

- **Perguntas obrigatórias** (texto, seleção, data, anexo).
- **Texto de inelegibilidade** (quando a IA deve orientar outro canal).
- **Modelo de resposta oficial** (template gather).
- **Integração externa** (sim/não; sistema destino).

---

## Assinaturas (modelo)

| Pela proponente | Pelo contratante |
|-----------------|------------------|
| Nome: _________________________ | Nome: _________________________ |
| Cargo: _________________________ | Cargo: _________________________ |
| Data: ____/____/________ | Data: ____/____/________ |

---

*Documento modelo — não constitui contrato vinculante sem revisão jurídica e aceite formal.*