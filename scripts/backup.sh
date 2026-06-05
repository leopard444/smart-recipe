#!/bin/bash
# Daily automated backup script
# Usage: ./backup.sh
# Cron: 0 3 * * * /opt/smart-recipe/scripts/backup.sh >> /var/log/recipe-backup.log 2>&1

set -e

DATE=$(date +%Y%m%d)
BACKUP_DIR="${BACKUP_DIR:-/var/backups/smart-recipe}"
UPLOADS_DIR="${UPLOADS_DIR:-/opt/smart-recipe/backend/uploads}"
MYSQL_USER="${MYSQL_USER:-recipe_user}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-recipe_pass}"
MYSQL_DATABASE="${MYSQL_DATABASE:-smart_recipe}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

mkdir -p "$BACKUP_DIR"

echo "=== Backup started at $(date) ==="

# 1. Database backup
echo "Backing up MySQL database..."
if command -v docker &> /dev/null; then
    docker exec smart-recipe-mysql mysqldump \
        -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
        | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
else
    mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
        | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
fi
echo "  -> $BACKUP_DIR/db_$DATE.sql.gz ($(du -h "$BACKUP_DIR/db_$DATE.sql.gz" | cut -f1))"

# 2. Uploads backup
echo "Backing up uploaded files..."
if [ -d "$UPLOADS_DIR" ]; then
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$(dirname "$UPLOADS_DIR")" "$(basename "$UPLOADS_DIR")"
    echo "  -> $BACKUP_DIR/uploads_$DATE.tar.gz ($(du -h "$BACKUP_DIR/uploads_$DATE.tar.gz" | cut -f1))"
else
    echo "  -> Skipped: uploads directory not found"
fi

# 3. Cleanup old backups
echo "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -type f -mtime "+$RETENTION_DAYS" -delete -print

echo "=== Backup completed at $(date) ==="
echo ""
