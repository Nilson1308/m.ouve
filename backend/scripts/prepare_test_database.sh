#!/usr/bin/env bash
# Provisiona o banco de testes quando o usuário da aplicação não tem CREATEDB (ex.: 192.168.10.49).
# Execute como superusuário Postgres no servidor correto:
#
#   psql -h 192.168.10.49 -U postgres -f - <<'SQL'
#   CREATE DATABASE ouvia_test OWNER admin_ouve;
#   \c ouvia_test
#   CREATE EXTENSION IF NOT EXISTS postgis;
#   CREATE EXTENSION IF NOT EXISTS vector;
#   SQL
#
# Depois: POSTGRES_TEST_DB=ouvia_test python manage.py test --keepdb

set -euo pipefail
cd "$(dirname "$0")/.."
DB="${POSTGRES_TEST_DB:-ouvia_test}"
echo "Banco de testes esperado: $DB (defina POSTGRES_TEST_DB no .env)"
echo "Rode os testes com: python manage.py test --keepdb"