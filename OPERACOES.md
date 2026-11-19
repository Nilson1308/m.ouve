# M.Ouve — Guia de Operação (comandos)

Referência rápida para subir, parar, reiniciar, conferir status e ler logs no servidor de homologação (`/var/www/ouve`).

---

## Caminhos e portas padrão

| Item | Valor |
|------|--------|
| Raiz do projeto | `/var/www/ouve` |
| Backend Django | `/var/www/ouve/backend` |
| Virtualenv Python | `/var/www/ouve/backend/.venv` |
| API (homolog) | `http://127.0.0.1:8765/api/v1` |
| Admin Django | `http://127.0.0.1:8765/admin/` |
| Frontend dev (Vite) | `http://127.0.0.1:3000` |
| Build estático | `/var/www/ouve/dist` |
| Redis (broker Celery) | `127.0.0.1:6379` (DB `0`) |
| Log Celery (background) | `/var/www/ouve/logs/celery.log` |

> Neste host, a porta **8000** é do **SIGA**. Não use 8000 para o M.Ouve.

---

## Ativar ambiente Python

Sempre que for rodar Django ou Celery manualmente:

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
```

---

## Redis

### Status

```bash
redis-cli ping
# Esperado: PONG
```

### Subir (se não houver serviço systemd)

```bash
redis-server
# ou em background:
redis-server --daemonize yes
```

### Parar (cuidado: afeta outros projetos no mesmo Redis)

```bash
redis-cli shutdown
```

### Inspecionar chaves do Celery (debug)

```bash
redis-cli -n 0 DBSIZE
redis-cli -n 0 KEYS 'celery*' | head
```

---

## Django — API

### Desenvolvimento / homolog (`runserver`)

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8765
```

Recarrega sozinho ao salvar arquivos `.py`. Para forçar reload:

```bash
touch /var/www/ouve/backend/ouvia_core/wsgi.py
```

### Migrações

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
python manage.py migrate
python manage.py makemigrations   # só quando houver mudança de models
```

### Checagem do projeto

```bash
python manage.py check
```

### Shell Django

```bash
python manage.py shell
```

### Catálogo (seed)

```bash
# Recria tudo — falha se existir protocolo vinculado
python manage.py seed_catalogo

# Atualizar sem limpar
python manage.py seed_catalogo --no-clear
```

### Verificar se a API responde

```bash
curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8765/admin/login/
```

---

## Celery — chat assíncrono (LLM)

O chat usa fila Redis. Exige **worker** rodando e `CELERY_TASK_ALWAYS_EAGER=False` no `backend/.env`.

### Subir worker (terminal interativo)

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
celery -A ouvia_core worker -l info -n ouve@%h -Q ouve
```

> **Importante:** use `-n ouve@%h` **e** `-Q ouve` neste servidor. Tasks do M.Ouve vão para a fila `ouve` (`CELERY_TASK_ROUTES` em `settings.py`). Workers de outros projetos (SIGA, eventos) na fila `celery` não devem consumir essas tasks; sem fila dedicada, o turno fica “processando” para sempre no frontend.

### Subir worker em background (homolog)

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
nohup celery -A ouvia_core worker -l info -n ouve@%h -Q ouve >>/var/www/ouve/logs/celery.log 2>&1 &
echo "PID: $!"
```

**Sempre reinicie o worker após alterar `tasks.py`, `chat_services.py` ou o orquestrador** — o Celery não recarrega o código automaticamente.

### Parar workers M.Ouve

```bash
pkill -f 'celery -A ouvia_core worker'
```

### Status — processos

```bash
pgrep -af 'celery -A ouvia_core worker'
ps aux | grep '[o]uvia_core worker'
```

### Logs em tempo real

```bash
tail -f /var/www/ouve/logs/celery.log
```

### Inspecionar fila (ping ao worker)

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
celery -A ouvia_core inspect ping
celery -A ouvia_core inspect active
celery -A ouvia_core inspect registered
```

### Teste sem worker (só debug rápido)

No `backend/.env`:

```env
CELERY_TASK_ALWAYS_EAGER=True
```

Reinicie o Django. A IA roda no processo web (não use em produção).

---

## Frontend (Vue / Vite)

### Desenvolvimento

```bash
cd /var/www/ouve
npm install
npm run dev
# http://127.0.0.1:3000
```

### Build de produção

```bash
cd /var/www/ouve
npm run build
# Saída: dist/
```

### Servir o build localmente (preview)

```bash
npm run preview -- --host 127.0.0.1 --port 4173
```

Confirme `.env` na raiz:

```env
VITE_API_BASE_URL=http://127.0.0.1:8765/api/v1
```

---

## Produção (`ouvidoria.mogidascruzes.sp.gov.br`)

Substitui o stack antigo (`/var/www/ouvidoria`, Gunicorn `:8001`, `/backend/`).

| Item | Valor |
|------|--------|
| Apache | `/etc/apache2/sites-available/ouvidoria.conf` (fonte: `deploy/apache/ouvidoria.conf`) |
| SPA | `DocumentRoot` → `/var/www/ouve/dist` |
| API (proxy) | `/api/` → `127.0.0.1:8765` |
| Build | `.env.production` + `npm run build` |
| Gunicorn | `deploy/systemd/gunicorn-ouve.service` ou `logs/gunicorn.log` |

**400 Bad Request na API** (login/admin): o proxy municipal envia `X-Forwarded-Host` com hostname interno. Django **não** usa `USE_X_FORWARDED_HOST`; no Apache, `RequestHeader unset X-Forwarded-Host` em `deploy/apache/snippets/django-proxy.inc`. Após mudança: `sudo systemctl restart gunicorn-ouve` e `sudo systemctl reload apache2`.

```bash
# Requer sudo (copiar vhost + systemd + reload Apache):
sudo cp /var/www/ouve/deploy/apache/ouvidoria.conf /etc/apache2/sites-available/ouvidoria.conf
sudo cp /var/www/ouve/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now gunicorn-ouve celery-ouve
sudo apache2ctl configtest && sudo systemctl reload apache2

# Sem sudo (após build/collectstatic):
/var/www/ouve/scripts/deploy-prod.sh
```

---

## Deploy rápido (homolog)

Script que instala deps, migra, builda o frontend e reinicia o Celery:

```bash
chmod +x /var/www/ouve/scripts/deploy.sh
/var/www/ouve/scripts/deploy.sh
```

---

## Visão geral dos processos (status manual)

```bash
# API Django
pgrep -af 'runserver.*8765'
ss -tlnp | grep 8765

# Celery M.Ouve
pgrep -af 'celery -A ouvia_core'

# Vite
pgrep -af 'vite'
ss -tlnp | grep 3000

# Redis
ss -tlnp | grep 6379
redis-cli ping
```

---

## Produção (systemd + Gunicorn) — quando configurado

Templates em `backend/deploy/README.md`. Após criar as units com **sudo**:

```bash
# API
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-ouve
sudo systemctl status gunicorn-ouve
sudo systemctl restart gunicorn-ouve
sudo journalctl -u gunicorn-ouve -f

# Celery
sudo systemctl enable --now celery-ouve
sudo systemctl status celery-ouve
sudo systemctl restart celery-ouve
sudo journalctl -u celery-ouve -f
```

> No ambiente atual do **gabinete**, o M.Ouve costuma rodar com **runserver + Celery em background**, não com essas units (ainda não instaladas por padrão).

---

## Variáveis de ambiente importantes

### `backend/.env`

| Variável | Função |
|----------|--------|
| `POSTGRES_*` | Banco `ouvia` (ex.: `192.168.10.49`) |
| `CELERY_BROKER_URL` | Ex.: `redis://127.0.0.1:6379/0` |
| `CELERY_TASK_ALWAYS_EAGER` | `False` em homolog/prod com worker |
| `GROQ_API_KEY` / `LLM_*` | Motor de chat |

### `.env` (raiz — frontend)

| Variável | Função |
|----------|--------|
| `VITE_API_BASE_URL` | URL da API que o PWA chama |

---

## Troubleshooting

### Chat “travado” (digitando… sem resposta)

1. Ver log do Celery:
   ```bash
   tail -50 /var/www/ouve/logs/celery.log
   ```
2. Worker rodando?
   ```bash
   pgrep -af 'celery -A ouvia_core worker'
   ```
3. Redis:
   ```bash
   redis-cli ping
   ```
4. Erros comuns já corrigidos:
   - `tipo_acao` muito longo → migração `0005` (`max_length=255`)
   - Redis 6.0 + Kombu 5.7 → manter `kombu<5.7` no `requirements.txt`

### Celery não inicia: `value is not an integer or out of range`

Redis **6.0.x** (Ubuntu 22.04) é incompatível com **Kombu 5.7+**. Reinstale deps:

```bash
cd /var/www/ouve/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Porta 8765 em uso

```bash
ss -tlnp | grep 8765
# Encerrar o PID do runserver antigo ou use outra porta:
python manage.py runserver 0.0.0.0:8870
```

Atualize `VITE_API_BASE_URL` se mudar a porta.

### Reinício completo “stack mínima” (homolog)

```bash
pkill -f 'celery -A ouvia_core worker' || true
# Pare o runserver no terminal (Ctrl+C) e suba de novo:

cd /var/www/ouve/backend && source .venv/bin/activate
python manage.py runserver 0.0.0.0:8765

# Outro terminal:
cd /var/www/ouve/backend && source .venv/bin/activate
celery -A ouvia_core worker -l info -n ouve@%h -Q ouve

# Frontend (opcional):
cd /var/www/ouve && npm run dev
```

---

## Ordem recomendada para subir do zero

1. Redis (`redis-cli ping` → `PONG`)
2. `python manage.py runserver 0.0.0.0:8765`
3. `celery -A ouvia_core worker -l info -n ouve@%h -Q ouve`
4. `npm run dev` (ou sirva `dist/`)

---

## Documentos relacionados

| Arquivo | Conteúdo |
|---------|----------|
| `QUICK_START.md` | Setup inicial e banco |
| `backend/README.md` | Backend, Celery, erro Redis/Kombu |
| `backend/deploy/README.md` | systemd + Gunicorn + Apache |
| `API_CONTRACT.md` | Contrato REST `/api/v1` |
| `scripts/deploy.sh` | Deploy homolog automatizado |

---

**Última atualização:** novembro de 2026
