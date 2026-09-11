#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${POSTGRES_CONTAINER:-postgres}"
DB_NAME="${POSTGRES_DB:-barq_tasks}"
DB_USER="${POSTGRES_USER:-barq_app}"

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <backup-file>" >&2
    exit 1
fi

BACKUP_FILE="$1"

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "[FAIL] Backup file not found: $BACKUP_FILE" >&2
    exit 1
fi

if [[ ! -s "$BACKUP_FILE" ]]; then
    echo "[FAIL] Backup file is empty: $BACKUP_FILE" >&2
    exit 1
fi

echo "[INFO] Restoring PostgreSQL database..."
echo "[INFO] Backup: ${BACKUP_FILE}"

docker exec -i "$CONTAINER" \
    pg_restore \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --clean \
    --if-exists \
    --no-owner \
    < "$BACKUP_FILE"

echo "[PASS] Database restored successfully."
