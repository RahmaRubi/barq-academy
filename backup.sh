#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${POSTGRES_CONTAINER:-postgres}"
DB_NAME="${POSTGRES_DB:-barq_tasks}"
DB_USER="${POSTGRES_USER:-barq_app}"
BACKUP_DIR="${BACKUP_DIR:-backups}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"

echo "[INFO] Creating PostgreSQL backup..."
echo "[INFO] Database: ${DB_NAME}"
echo "[INFO] Output: ${BACKUP_FILE}"

docker exec "$CONTAINER" \
    pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -Fc \
    > "$BACKUP_FILE"

if [[ ! -s "$BACKUP_FILE" ]]; then
    echo "[FAIL] Backup file is empty." >&2
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo "[PASS] Backup created: ${BACKUP_FILE}"
