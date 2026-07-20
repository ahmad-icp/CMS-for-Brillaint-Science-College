#!/bin/sh
set -eu

: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
FILE_PREFIX="${BACKUP_FILE_PREFIX:-${POSTGRES_DB}}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="${BACKUP_DIR}/${FILE_PREFIX}-${TIMESTAMP}.dump"
PARTIAL="${TARGET}.partial"

case "$RETENTION_DAYS" in
  ''|*[!0-9]*) echo "BACKUP_RETENTION_DAYS must be a positive integer" >&2; exit 1 ;;
esac
if [ "$RETENTION_DAYS" -le 0 ]; then
  echo "BACKUP_RETENTION_DAYS must be positive" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
export PGPASSWORD="$POSTGRES_PASSWORD"
rm -f "$PARTIAL"

pg_dump \
  --host="${POSTGRES_HOST:-postgres}" \
  --port="${POSTGRES_PORT:-5432}" \
  --username="$POSTGRES_USER" \
  --dbname="$POSTGRES_DB" \
  --format=custom \
  --compress=9 \
  --file="$PARTIAL"

mv "$PARTIAL" "$TARGET"
sha256sum "$TARGET" > "${TARGET}.sha256"
find "$BACKUP_DIR" -type f \( -name "${FILE_PREFIX}-*.dump" -o -name "${FILE_PREFIX}-*.dump.sha256" \) -mtime "+${RETENTION_DAYS}" -delete

echo "Backup completed: $TARGET"
