#!/bin/bash

# Backup dizini
BACKUP_DIR="/var/backups/dilekce"
DATE=$(date +%Y%m%d_%H%M%S)

# Dizinleri oluştur
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/files"
mkdir -p "$BACKUP_DIR/logs"

# Database backup
echo "📦 Creating database backup..."
docker exec dilekce_db pg_dump -U dilekce_user dilekce > "$BACKUP_DIR/database/db_$DATE.sql"

# Dosya backup
echo "📂 Creating file backups..."
tar -czf "$BACKUP_DIR/files/uploads_$DATE.tar.gz" /var/www/dilekce/uploads
tar -czf "$BACKUP_DIR/files/pdfs_$DATE.tar.gz" /var/www/dilekce/pdfs

# Log backup
echo "📝 Creating log backup..."
tar -czf "$BACKUP_DIR/logs/logs_$DATE.tar.gz" /var/log/dilekce

# Eski backup'ları temizle (30 günden eski)
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "✅ Backup completed successfully!" 