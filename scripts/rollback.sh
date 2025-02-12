#!/bin/bash

echo "⚠️ Starting rollback process..."

# 1. Son backup'ı bul
LATEST_BACKUP=$(ls -t /var/backups/dilekce/database/db_*.sql | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backup found!"
    exit 1
fi

# 2. Servisleri durdur
docker-compose down

# 3. Database'i geri yükle
echo "🔄 Restoring database from $LATEST_BACKUP..."
docker-compose up -d db
sleep 5  # Database'in başlamasını bekle
cat $LATEST_BACKUP | docker exec -i dilekce_db psql -U dilekce_user dilekce

# 4. Eski versiyona dön
if [ -n "$1" ]; then
    echo "⏮️ Rolling back to version $1..."
    git checkout $1
    docker-compose build --no-cache
fi

# 5. Servisleri yeniden başlat
echo "🔄 Restarting services..."
docker-compose up -d

# 6. Health check
echo "🏥 Running health check..."
./scripts/monitor.sh

echo "✅ Rollback completed!" 