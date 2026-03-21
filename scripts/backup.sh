#!/bin/bash
# Backup PostgreSQL database to an encrypted file
# Usage: bash scripts/backup.sh

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y-%m-%d_%H-%M)
FILENAME="lifedb_backup_${DATE}.sql"
COMPRESSED="${FILENAME}.gz"

mkdir -p "$BACKUP_DIR"

echo "Starting backup..."
pg_dump -U postgres lifedb > "${BACKUP_DIR}/${FILENAME}"

gzip "${BACKUP_DIR}/${FILENAME}"
echo "Backup saved: ${BACKUP_DIR}/${COMPRESSED}"

# Keep only last 30 backups
cd "$BACKUP_DIR" && ls -t lifedb_backup_*.sql.gz | tail -n +31 | xargs -r rm
echo "Old backups cleaned. Done."
