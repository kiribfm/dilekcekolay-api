#!/bin/bash

# Hata durumunda scripti durdur
set -e

echo "🚀 Starting production deployment..."

# 1. Environment kontrolü
if [ ! -f .env.prod ]; then
    echo "❌ Error: .env.prod file not found!"
    exit 1
fi

# 2. Production checklist kontrolü
echo "📋 Running pre-deployment checks..."

# SSL sertifikaları
if [ ! -d "./ssl" ]; then
    echo "🔒 Generating SSL certificates..."
    ./scripts/generate_ssl.sh
fi

# Gerekli dizinleri oluştur
echo "📁 Creating required directories..."
mkdir -p /var/www/dilekce/{uploads,temp,pdfs}
mkdir -p /var/log/dilekce
mkdir -p /var/backups/dilekce

# 3. Docker servisleri durdur
echo "🛑 Stopping running services..."
docker-compose down

# 4. Database backup
echo "💾 Creating database backup..."
./scripts/backup.sh

# 5. Docker image'larını yeniden build et
echo "🏗️ Building Docker images..."
docker-compose build --no-cache

# 6. Servisleri başlat
echo "🌟 Starting services..."
docker-compose up -d

# 7. Database migration
echo "📦 Running database migrations..."
docker-compose exec api alembic upgrade head

# 8. Nginx reload
echo "🔄 Reloading Nginx configuration..."
docker-compose exec nginx nginx -s reload

# 9. Health check
echo "🏥 Running health check..."
./scripts/monitor.sh

# 10. Cron job'ları ayarla
echo "⏰ Setting up cron jobs..."
./scripts/setup_cron.sh

echo "
✅ Deployment completed successfully!

Services:
- API: https://api.dilekce.com
- Database: localhost:5432
- Nginx: 80/443

Monitoring:
- Logs: /var/log/dilekce/
- Metrics: https://api.dilekce.com/metrics
- Health: https://api.dilekce.com/health

Backups:
- Location: /var/backups/dilekce/
- Schedule: Daily at 02:00
"

# Deployment log
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deployment completed successfully" >> /var/log/dilekce/deployment.log 