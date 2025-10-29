#!/bin/bash
# Quick Deployment Script for ecomarce_choco
# Run this script on your Droplet after initial setup

set -e  # Exit on any error

echo "🚀 Starting deployment..."

# Configuration (UPDATE THESE!)
DOMAIN="yourdomain.com"
DROPLET_IP="your-droplet-ip"
USERNAME="django"
PROJECT_DIR="/home/${USERNAME}/ecomarce_choco"

echo "Step 1: Creating logs directory"
mkdir -p ${PROJECT_DIR}/logs
chown -R ${USERNAME}:www-data ${PROJECT_DIR}/logs

echo "Step 2: Setting up Gunicorn config"
cp ${PROJECT_DIR}/deployment/gunicorn_config.py ${PROJECT_DIR}/gunicorn_config.py
chown ${USERNAME}:${USERNAME} ${PROJECT_DIR}/gunicorn_config.py

echo "Step 3: Setting up Systemd service"
sudo cp ${PROJECT_DIR}/deployment/systemd.service /etc/systemd/system/ecomarce_choco.service
sudo sed -i "s/django/${USERNAME}/g" /etc/systemd/system/ecomarce_choco.service
sudo systemctl daemon-reload
sudo systemctl enable ecomarce_choco

echo "Step 4: Setting up Nginx"
sudo cp ${PROJECT_DIR}/deployment/nginx.conf /etc/nginx/sites-available/ecomarce_choco
sudo sed -i "s/yourdomain.com/${DOMAIN}/g" /etc/nginx/sites-available/ecomarce_choco
sudo sed -i "s/your-droplet-ip/${DROPLET_IP}/g" /etc/nginx/sites-available/ecomarce_choco
sudo ln -sf /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "Step 5: Testing configurations"
sudo nginx -t

echo "Step 6: Setting permissions"
sudo chown -R ${USERNAME}:www-data ${PROJECT_DIR}
sudo chmod -R 755 ${PROJECT_DIR}
sudo chown -R ${USERNAME}:www-data ${PROJECT_DIR}/staticfiles
sudo chown -R ${USERNAME}:www-data ${PROJECT_DIR}/media

echo "Step 7: Starting services"
sudo systemctl start ecomarce_choco
sudo systemctl restart nginx

echo "✅ Deployment complete!"

