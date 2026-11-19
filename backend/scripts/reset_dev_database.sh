#!/usr/bin/env bash
# Recria o schema PostgreSQL e aplica migrações do zero (somente desenvolvimento).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${POSTGRES_DB:=ouvia}"
: "${POSTGRES_USER:=admin_ouve}"
: "${POSTGRES_HOST:=127.0.0.1}"
: "${POSTGRES_PORT:=5432}"

echo ">> ATENÇÃO: apagando schema public do banco '${POSTGRES_DB}' em ${POSTGRES_HOST}:${POSTGRES_PORT}"
export PGPASSWORD="${POSTGRES_PASSWORD:-}"

psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<'SQL'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
SQL

echo ""
echo ">> OBRIGATÓRIO (como superusuário PostgreSQL, ex. postgres) no banco '${POSTGRES_DB}':"
echo "   psql -h ${POSTGRES_HOST} -U postgres -d ${POSTGRES_DB}"
echo "   CREATE EXTENSION IF NOT EXISTS postgis;"
echo "   CREATE EXTENSION IF NOT EXISTS vector;"
echo ""
echo "   O usuário da app (${POSTGRES_USER}) não pode criar extensões."
echo "   DROP SCHEMA remove postgis/vector do banco — recrie antes do migrate."
echo ""

if ! PGPASSWORD="${POSTGRES_PASSWORD:-}" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
  "SELECT COUNT(*) FROM pg_extension WHERE extname IN ('postgis','vector')" | grep -q '^2$'; then
  echo ">> AVISO: postgis/vector ainda ausentes. migrate vai falhar até o DBA criar as extensões."
  exit 1
fi

echo ">> migrate"
.venv/bin/python manage.py migrate --noinput

echo ">> seed catálogo padrão"
.venv/bin/python manage.py seed_catalogo

echo ">> Concluído. Crie superusuário se necessário: python manage.py createsuperuser"
