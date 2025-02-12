#!/bin/bash

# Health check
response=$(curl -s -o /dev/null -w "%{http_code}" https://api.dilekce.com/health)
if [ $response != "200" ]; then
    echo "❌ API health check failed! Status: $response"
    exit 1
fi

# Disk usage check
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 90 ]; then
    echo "⚠️ High disk usage: $disk_usage%"
fi

# Memory usage check
free_mem=$(free | awk '/Mem:/ {print $4/$2 * 100.0}')
if [ $(echo "$free_mem < 20" | bc -l) -eq 1 ]; then
    echo "⚠️ Low memory: $free_mem% free"
fi

# Log check
log_errors=$(grep -i error /var/log/dilekce/error.log | wc -l)
if [ $log_errors -gt 0 ]; then
    echo "⚠️ Found $log_errors errors in logs"
fi

# Database connection check
db_status=$(docker exec dilekce_db pg_isready -U dilekce_user)
if [ $? -ne 0 ]; then
    echo "❌ Database connection failed!"
fi 