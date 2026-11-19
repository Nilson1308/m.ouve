#!/usr/bin/env bash
# Deploy produção M.Ouve — Gunicorn + dist/ + Apache (ouvidoria.conf)
set -euo pipefail

ROOT="/var/www/ouve"
BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv"

echo "==> Dependências Python"
"$VENV/bin/pip" install -q -r "$BACKEND/requirements.txt"

echo "==> Migrações e estáticos Django"
cd "$BACKEND"
"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput

echo "==> Build frontend (API pública)"
cd "$ROOT"
set -a
# shellcheck disable=SC1091
source "$ROOT/.env.production"
set +a
npm run build

echo "==> Parar runserver de homolog (se existir)"
pkill -f 'manage.py runserver.*8765' 2>/dev/null || true
pkill -f 'celery -A ouvia_core worker' 2>/dev/null || true
sleep 2

if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files gunicorn-ouve.service &>/dev/null; then
  echo "==> Reiniciar systemd (gunicorn-ouve, celery-ouve)"
  sudo systemctl daemon-reload
  sudo systemctl enable --now gunicorn-ouve celery-ouve
  sudo systemctl restart gunicorn-ouve celery-ouve
else
  echo "==> systemd não configurado — subindo Gunicorn/Celery via nohup"
  cd "$BACKEND"
  nohup "$VENV/bin/gunicorn" ouvia_core.wsgi:application \
    --bind 127.0.0.1:8765 --workers 3 --timeout 120 \
    >>"$ROOT/logs/gunicorn.log" 2>&1 &
  nohup "$VENV/bin/celery" -A ouvia_core worker -l info -n ouve@%h -Q ouve --concurrency=4 \
    >>"$ROOT/logs/celery.log" 2>&1 &
fi

echo "==> Apache (se snippet instalado)"
if [ -f /etc/apache2/sites-available/ouvidoria.conf ]; then
  sudo cp "$ROOT/deploy/apache/ouvidoria.conf" /etc/apache2/sites-available/ouvidoria.conf
  sudo apache2ctl configtest
  sudo systemctl reload apache2
fi

echo "✅ Produção: https://ouvidoria.mogidascruzes.sp.gov.br"
echo "   API local: http://127.0.0.1:8765/api/v1"
echo "   dist:      $ROOT/dist"
