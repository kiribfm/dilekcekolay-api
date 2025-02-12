#!/bin/bash

# Backup script'ini kopyala
sudo cp backup.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup.sh

# Crontab'a ekle (her gece 02:00'de)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup.sh") | crontab - 