#!/usr/bin/env bash
# Deploy homologação M.Ouve (usuário gabinete, sem systemd).
set -euo pipefail

ROOT="/var/www/ouve"
BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv"

echo "==> Dependências Python"
"$VENV/bin/pip" install -q -r "$BACKEND/requirements.txt"

echo "==> Migrações"
cd "$BACKEND"
"$VENV/bin/python" manage.py migrate --noinput

echo "==> Build frontend (dist/)"
cd "$ROOT"
npm run build

echo "==> Reiniciar Celery worker (código assíncrono)"
pkill -f 'celery -A ouvia_core worker' 2>/dev/null || true
sleep 2
cd "$BACKEND"
nohup "$VENV/bin/celery" -A ouvia_core worker -l info -n ouve@%h -Q ouve \
  >>"$ROOT/logs/celery.log" 2>&1 &
echo "Celery PID: $!"

echo "==> Django runserver"
echo "    Se usar runserver, ele recarrega ao detectar alterações em .py."
echo "    Produção: configure gunicorn + Apache (ver backend/deploy/README.md)."

echo "✅ Deploy concluído."
echo "   API:  http://127.0.0.1:8765/api/v1"
echo "   dist: $ROOT/dist"
