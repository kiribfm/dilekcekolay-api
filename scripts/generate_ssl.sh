#!/bin/bash

# SSL dizini
SSL_DIR="./ssl"
mkdir -p $SSL_DIR

# Self-signed sertifika oluştur
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $SSL_DIR/dilekce.key \
    -out $SSL_DIR/dilekce.crt \
    -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Dilekce/CN=api.dilekce.com"

# Permissions
chmod 600 $SSL_DIR/dilekce.key
chmod 644 $SSL_DIR/dilekce.crt

echo "✅ SSL certificates generated successfully!" 