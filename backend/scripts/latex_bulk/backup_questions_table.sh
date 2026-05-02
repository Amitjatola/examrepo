#!/usr/bin/env bash
# Snapshot the `questions` table before running fix_questions_in_db.py.
# Uses DATABASE_URL from the environment (load backend/.env first).
set -euo pipefail

BACKEND_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$BACKEND_ROOT"
if [ -f .env ]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set. Set it or create ${BACKEND_ROOT}/.env" >&2
  exit 1
fi

# libpq / pg_dump do not understand SQLAlchemy's +asyncpg driver
SYNC_URL="${DATABASE_URL//+asyncpg/}"
SYNC_URL="${SYNC_URL//+psycopg/}"

STAMP=$(date +%Y%m%d_%H%M%S)
OUT_DIR="${BACKUP_DIR:-${BACKEND_ROOT}/backups}"
mkdir -p "$OUT_DIR"
OUT_FILE="${OUT_DIR}/questions_table_${STAMP}.sql"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "ERROR: pg_dump not found. Install PostgreSQL client tools (e.g. brew install libpq)." >&2
  exit 1
fi

echo "Backing up table public.questions to ${OUT_FILE} ..."
pg_dump --no-owner --no-acl -t 'public.questions' --file="$OUT_FILE" "$SYNC_URL"
echo "OK: ${OUT_FILE}"
