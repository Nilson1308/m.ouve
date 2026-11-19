# Deploy produção (systemd + Gunicorn)

Requer sudo. Ajuste domínio/porta conforme infra.

## Gunicorn (API)

```ini
# /etc/systemd/system/gunicorn-ouve.service
[Unit]
Description=M.Ouve API (Django)
After=network.target

[Service]
User=gabinete
Group=www-data
WorkingDirectory=/var/www/ouve/backend
EnvironmentFile=/var/www/ouve/backend/.env
ExecStart=/var/www/ouve/backend/.venv/bin/gunicorn ouvia_core.wsgi:application \
    --bind 127.0.0.1:8765 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-ouve
```

## Celery

```ini
# /etc/systemd/system/celery-ouve.service
[Unit]
Description=M.Ouve Celery worker
After=network.target redis-server.service

[Service]
User=gabinete
Group=www-data
WorkingDirectory=/var/www/ouve/backend
EnvironmentFile=/var/www/ouve/backend/.env
ExecStart=/var/www/ouve/backend/.venv/bin/celery -A ouvia_core worker -l info -n ouve@%h -Q ouve --concurrency=4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Frontend (Apache)

Arquivos versionados em `deploy/apache/`:

```bash
sudo cp /var/www/ouve/deploy/apache/ouvidoria.conf /etc/apache2/sites-available/ouvidoria.conf
sudo a2ensite ouvidoria.conf   # se ainda não habilitado
sudo apache2ctl configtest && sudo systemctl reload apache2
```

`DocumentRoot /var/www/ouve/dist` com `FallbackResource /index.html`.  
Proxy `/api/` → Gunicorn `127.0.0.1:8765`.

Build com `.env.production` (`VITE_API_BASE_URL=https://ouvidoria.mogidascruzes.sp.gov.br/api/v1`).

## Systemd (cópia dos units)

```bash
sudo cp /var/www/ouve/deploy/systemd/gunicorn-ouve.service /etc/systemd/system/
sudo cp /var/www/ouve/deploy/systemd/celery-ouve.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-ouve celery-ouve
```

## Script produção

```bash
chmod +x /var/www/ouve/scripts/deploy-prod.sh
/var/www/ouve/scripts/deploy-prod.sh
```

## Script rápido (homolog)

```bash
chmod +x /var/www/ouve/scripts/deploy.sh
/var/www/ouve/scripts/deploy.sh
```
