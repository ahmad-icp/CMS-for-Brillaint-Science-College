#!/bin/sh
set -eu

INTERVAL="${BACKUP_INTERVAL_SECONDS:-86400}"
case "$INTERVAL" in
  ''|*[!0-9]*) echo "BACKUP_INTERVAL_SECONDS must be a positive integer" >&2; exit 1 ;;
esac
if [ "$INTERVAL" -le 0 ]; then
  echo "BACKUP_INTERVAL_SECONDS must be positive" >&2
  exit 1
fi

while true; do
  /usr/local/bin/backup-postgres
  sleep "$INTERVAL"
done
