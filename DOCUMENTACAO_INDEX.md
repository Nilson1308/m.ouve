# Índice da documentação — M.Ouve

Documentação ativa do repositório organizada em **três pilares**. Use este arquivo como ponto de entrada.

---

## 1. Contrato (integração e API)

Documentação normativa para frontend, mobile e integrações externas.

| Documento | Conteúdo |
|-----------|----------|
| [**API_CONTRACT.md**](API_CONTRACT.md) | Endpoints, autenticação JWT, modelos, versionamento (v4.x), chat, backoffice, CSAT, notificações `/app/notificacoes`, dashboards |

**Regra:** qualquer dúvida sobre rota ou payload → **API_CONTRACT** prevalece sobre guias antigos em `docs/archive/`.

---

## 2. Operação (produção e servidor)

Runbooks para deploy, filas e manutenção.

| Documento | Conteúdo |
|-----------|----------|
| [**OPERACOES.md**](OPERACOES.md) | Portas, Redis, Celery, Gunicorn, logs, comandos no host |
| [**backend/deploy/README.md**](backend/deploy/README.md) | Systemd, workers, checklist de produção |
| [**backend/README.md**](backend/README.md) | Setup Django, migrações, ambiente Python |
| [**backend/.env.example**](backend/.env.example) | Variáveis (DB, Celery, LLM, **VAPID**) |
| [**.env.example**](.env.example) | Variáveis do frontend (`VITE_API_BASE_URL`, `VITE_VAPID_PUBLIC_KEY`) |
| [**QUICK_START.md**](QUICK_START.md) | Passos rápidos de desenvolvimento local |
| [**CONTRIBUTING.md**](CONTRIBUTING.md) | Contribuição e convenções do time |

---

## 3. Base de conhecimento (negócio, UX e arquitetura)

Materiais de apoio que **não substituem** o contrato da API. Úteis para onboarding, treinamento e decisões de produto.

**Pasta:** [`docs/knowledge/`](docs/knowledge/)

| Tema | Exemplos de arquivos |
|------|----------------------|
| Design e acessibilidade | `DESIGN_SYSTEM_GOLD_STANDARD.md`, `COLOR_SYSTEM.md`, `UI_WIREFRAMES.md`, `MELHORIAS_UX.md` |
| Mesa e protocolo (backoffice) | `MESA_TRABALHO_README.md`, `DETALHES_PROTOCOLO_INTERNO.md`, `GUIA_RAPIDO_PROTOCOLO_INTERNO.md`, `FLUXO_NAVEGACAO_BACKOFFICE.md` |
| Scatter-gather e setorial | `PAINEL_SETORIAL_README.md`, `GUIA_VISUAL_PAINEL_SETORIAL.md` |
| RBAC e administração | `RBAC_DINAMICO_GLPI.md`, `README_ADMINISTRACAO.md`, `VISUAL_MATRIZ_PERMISSOES.md` |
| Catálogo e Form Builder | `FORM_BUILDER_NO_CODE.md`, `GUIA_USO_FORM_BUILDER.md`, `CATALOGO_QUICK_REFERENCE.md` |
| Dashboards | `DASHBOARD_EFICIENCIA.md`, `DASHBOARD_MAPA_GIS.md`, `MATRIZ_QUALIDADE.md` |
| Chat e IA | `INTEGRACAO_CHAT.md`, `COMPONENTES_CHAT.md`, `MAPA_IA_README.md` |
| Arquitetura | `ARCHITECTURE.md`, `BACKEND_INTEGRATION.md` |
| Comercial / vendas | [`docs/knowledge/comercial/`](docs/knowledge/comercial/) — one-pager, slides PDF, proposta modelo e Anexo I |
| QA | [`docs/knowledge/qa/`](docs/knowledge/qa/) (cenários E2E documentados) |

Índice da pasta knowledge: [`docs/knowledge/README.md`](docs/knowledge/README.md).

---

## Arquivo histórico

Entregas de sprint, mocks e resumos de iterações **anteriores à maturidade atual** foram movidos para:

**[`docs/archive/`](docs/archive/)** — leitura contextual apenas; podem citar telas ou TODOs já implementados.

Índice: [`docs/archive/README.md`](docs/archive/README.md).

---

## Mapa mental

```
README.md (visão do produto)
    │
    ├── Contrato ──► API_CONTRACT.md
    ├── Operação ──► OPERACOES.md + backend/deploy/
    └── Conhecimento ──► docs/knowledge/
                              └── docs/archive/ (histórico)
```

**Última reorganização da documentação:** governança pós-Onda 4 (notificações cidadão + Web Push).