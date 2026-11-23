# M.Ouve (Ouv.IA)

Plataforma GovTech de ouvidoria e zeladoria urbana para o cidadão e para a gestão municipal.

> Codinome técnico do repositório: **SINAPSE** / `ouvia`.

> **Nota histórica:** para rotas, payloads e versionamento da API, consulte sempre o [`API_CONTRACT.md`](API_CONTRACT.md). Este README descreve o produto; o contrato descreve a implementação.

---

## O que é o M.Ouve

O M.Ouve é um sistema **em produção**, com PWA para o cidadão e backoffice para servidores, backend Django/PostGIS e filas Celery. O fluxo operacional segue o padrão **scatter-gather**: um protocolo do cidadão pode gerar várias ordens de serviço entre secretarias, retornar para validação da ouvidoria e encerrar com resposta oficial e pesquisa de satisfação (CSAT).

### PWA do cidadão

- Dashboard, catálogo de serviços e abertura de solicitações (ouvidoria e zeladoria).
- **Chat conversacional com IA** (processamento assíncrono via Celery), coleta dinâmica por JSON Schema e geração de protocolo.
- **Detalhe do protocolo** com andamento, anexos, localização e timeline.
- **Acessibilidade** orientada à WCAG 2.1 AA (navegação por teclado, alto contraste, landmarks, componentes acessíveis).
- **CSAT** pós-resolução (estrelas 1–5 e comentário opcional).
- **Central de notificações in-app** e **Web Push** (VAPID): sino no header, lista `/app/notificacoes`, inscrição push no navegador.

### Backoffice

- **Mesa de trabalho** com Kanban e lista, filtros por SLA, despacho scatter-gather, **sugestão de encaminhamento** (motor determinístico + IA semântica opcional) e validação ao cidadão.
- **Visão 360º** do protocolo, ordens de serviço, assinaturas hierárquicas e evidências de campo.
- **Painel setorial**, link mágico para equipes de rua e formalização de OS.
- **Super OS** e sugestões de cluster por IA (governadas por catálogo e configuração global).
- **Catálogo de serviços** com form builder, versionamento de schema e sandbox.
- **Dashboards gerenciais**: eficiência (TMA/SLA), mapa GIS, inelegibilidade da IA, **matriz de qualidade** com CSAT real.
- **Notificações internas** para servidores e central Super Admin (auditoria e broadcast).

### Governança e segurança

- **RBAC granular** (perfis dinâmicos, permissões por módulo).
- **Motor de escopo de dados** no backoffice (prevenção de IDOR por unidade).
- **Auditoria** de notificações e configuração de gatilhos operacionais.
- Contrato de API versionado e testes de regressão no backend.

---

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Frontend | Vue 3, Vite, Tailwind, Pinia, PWA (Workbox) |
| Backend | Django, DRF, PostGIS, pgvector, Celery, Redis |
| IA | Orquestrador LLM (Groq/OpenAI), chat assíncrono |

---

## Início rápido (desenvolvimento)

```bash
# Frontend
npm install
cp .env.example .env   # ajuste VITE_API_BASE_URL e VITE_VAPID_PUBLIC_KEY
npm run dev

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 127.0.0.1:8765
# Worker (chat, push, SLA):
celery -A ouvia_core worker -l info -Q ouve
```

Build de produção do frontend: `npm run build` (saída em `dist/`).

Mais detalhes: [`QUICK_START.md`](QUICK_START.md), [`OPERACOES.md`](OPERACOES.md), [`backend/README.md`](backend/README.md).

---

## Documentação

| Pilar | Onde |
|-------|------|
| **Contrato (API)** | [`API_CONTRACT.md`](API_CONTRACT.md) |
| **Operação** | [`OPERACOES.md`](OPERACOES.md), [`backend/deploy/README.md`](backend/deploy/README.md) |
| **Índice geral** | [`DOCUMENTACAO_INDEX.md`](DOCUMENTACAO_INDEX.md) |
| **Base de conhecimento** | [`docs/knowledge/`](docs/knowledge/) (fluxos, RBAC, UX, catálogo) |
| **Arquivo histórico** | [`docs/archive/`](docs/archive/) (entregas e sprints — somente referência) |

---

## Estrutura resumida

```
/var/www/ouve
├── src/                 # Vue PWA + Backoffice
├── backend/             # Django (atendimentos, catálogo, core_auth)
├── dist/                # Build estático (produção)
├── API_CONTRACT.md
├── OPERACOES.md
└── docs/
    ├── knowledge/
    └── archive/
```

---

## Licença e uso

Software desenvolvido para gestão pública municipal.