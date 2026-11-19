# M.Ouve — Backend Django

API REST (`/api/v1`) alinhada ao `API_CONTRACT.md` na raiz do monorepo.

## Pré-requisitos

- Python 3.10+ (recomendado 3.11+)
- PostgreSQL **192.168.10.49** com banco `ouvia`, PostGIS e pgvector (homolog/prod)
- Redis local (porta **6379**) para Celery
- Docker local (**opcional**, porta **5434**) — apenas dev offline; ver `docker-compose.yml`

## Banco remoto (192.168.10.49)

Executar **como superusuário** no servidor PostgreSQL (uma vez):

```sql
CREATE ROLE admin_ouve WITH LOGIN PASSWORD '...' NOSUPERUSER NOCREATEDB NOCREATEROLE;

CREATE DATABASE ouvia OWNER admin_ouve ENCODING 'UTF8';

\c ouvia
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
```

Ajuste `backend/.env` (`POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`). Guia completo: `../QUICK_START.md`.

## Docker local (opcional)

```bash
cd /var/www/ouve/backend
cp .env.example .env
docker compose up -d db
# Ajuste POSTGRES_HOST=127.0.0.1 e POSTGRES_PORT=5434 no .env
```

## Ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # use CPF só com dígitos como "username"
python manage.py runserver 0.0.0.0:8000
```

## Celery (obrigatório para chat assíncrono)

1. Suba o Redis (`redis-server` ou `docker compose up redis`).
2. No `.env`, use `CELERY_TASK_ALWAYS_EAGER=False` (padrão) para processar o LLM em background.
3. Em outro terminal:

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
celery -A ouvia_core worker -l info
```

4. API Django em paralelo: `python manage.py runserver 0.0.0.0:8765`

Com `CELERY_TASK_ALWAYS_EAGER=True`, a task roda no processo web (útil só para testes rápidos sem worker).

### Erro ao subir o worker: `ResponseError: value is not an integer or out of range`

Ocorre no **Redis 6.0.x** (padrão Ubuntu 22.04) com **Kombu 5.7+**, que usa `ZRANGE BYSCORE` (só existe a partir do **Redis 6.2**).

**Solução recomendada no projeto:** manter `kombu<5.7` no `requirements.txt` e reinstalar:

```bash
pip install -r requirements.txt
celery -A ouvia_core worker -l info
```

**Alternativa (produção):** atualizar o Redis para **6.2+** (Snap, pacote oficial ou container) e usar Kombu/Celery recentes.

## Apps

| App | Responsabilidade |
|-----|----------------|
| `core_auth` | Usuários, JWT, endereço PostGIS, notificações |
| `catalogo` | `ServicoCatalogo` + JSON Schema |
| `atendimentos` | Protocolos, anexos, histórico, ordens de serviço, assistente/geocode |
| `ia_orchestrator` | Tarefa Celery `gerar_embedding_solicitacao` |

## Banco de dados (dev — recriar schema)

```bash
chmod +x scripts/reset_dev_database.sh
./scripts/reset_dev_database.sh
```

Garanta `postgis` e `vector` no banco antes do `migrate` (ver `QUICK_START.md`).

## Frontend

Configure `VITE_API_BASE_URL=http://localhost:8000/api/v1` no Vue.
