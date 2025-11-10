#!/bin/bash
# Quick HTTPS Setup Script for ecomarce_choco
# Run this script on your server: 164.90.215.173
# 
# Usage: 
#   1. SSH into your server: ssh django@164.90.215.173
#   2. cd /home/django/ecomarce_choco
#   3. sudo bash QUICK_HTTPS_SETUP.sh

set -e  # Exit on any error

echo "🔒 Starting HTTPS Setup with Self-Signed Certificate..."
echo ""

# Step 1: Install OpenSSL (if needed)
echo "Step 1: Installing OpenSSL..."
sudo apt update
sudo apt install -y openssl

# Step 2: Create SSL directory
echo "Step 2: Creating SSL directory..."
sudo mkdir -p /etc/nginx/ssl

# Step 3: Generate self-signed certificate
echo "Step 3: Generating self-signed certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/C=AE/ST=Dubai/L=Dubai/O=ChocoEcommerce/CN=164.90.215.173"

# Step 4: Set permissions
echo "Step 4: Setting certificate permissions..."
sudo chmod 600 /etc/nginx/ssl/selfsigned.key
sudo chmod 644 /etc/nginx/ssl/selfsigned.crt

# Step 5: Backup existing nginx config
echo "Step 5: Backing up existing nginx configuration..."
if [ -f /etc/nginx/sites-available/ecomarce_choco ]; then
    sudo cp /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-available/ecomarce_choco.backup.$(date +%Y%m%d_%H%M%S)
    echo "   ✅ Backup created"
else
    echo "   ⚠️  No existing config found, will create new one"
fi

# Step 6: Create new nginx config with HTTPS
echo "Step 6: Creating HTTPS nginx configuration..."
sudo tee /etc/nginx/sites-available/ecomarce_choco > /dev/null <<'EOF'
upstream django {
    server 127.0.0.1:8000;
}

# HTTP Server - Redirect to HTTPS
server {
    listen 80;
    server_name 164.90.215.173;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name 164.90.215.173;

    # SSL Certificate
    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /home/django/ecomarce_choco/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/django/ecomarce_choco/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # GraphQL API
    location /graphql/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Default - proxy to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
EOF

# Step 7: Enable site (create symlink)
echo "Step 7: Enabling nginx site..."
sudo ln -sf /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-enabled/

# Step 8: Test nginx configuration
echo "Step 8: Testing nginx configuration..."
if sudo nginx -t; then
    echo "   ✅ Nginx configuration is valid"
else
    echo "   ❌ Nginx configuration has errors!"
    echo "   Please check the configuration manually"
    exit 1
fi

# Step 9: Restart nginx
echo "Step 9: Restarting nginx..."
sudo systemctl restart nginx
echo "   ✅ Nginx restarted"

# Step 10: Update Django settings
echo ""
echo "Step 10: Updating Django environment..."
echo ""
echo "⚠️  IMPORTANT: You need to update your .env file manually!"
echo ""
echo "Add or update these lines in /home/django/ecomarce_choco/.env:"
echo "   USE_HTTPS=True"
echo "   FRONTEND_URL=https://clownfish-app-2ehbt.ondigitalocean.app"
echo "   BACKEND_URL=https://164.90.215.173"
echo ""
read -p "Press Enter after you've updated the .env file..."

# Step 11: Restart Django service
echo "Step 11: Restarting Django service..."
sudo systemctl restart ecomarce_choco
echo "   ✅ Django service restarted"

# Step 12: Test HTTPS endpoint
echo ""
echo "Step 12: Testing HTTPS endpoint..."
if curl -k -s -o /dev/null -w "%{http_code}" https://164.90.215.173/graphql/ | grep -q "200\|405"; then
    echo "   ✅ HTTPS is working!"
else
    echo "   ⚠️  HTTPS test returned unexpected result"
fi

echo ""
echo "✅ HTTPS Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Update your frontend to use: https://164.90.215.173/graphql/"
echo "   2. Test the connection from your frontend"
echo "   3. Note: Browsers will show a security warning (this is normal for self-signed certificates)"
echo "   4. Users need to click 'Advanced' → 'Proceed to 164.90.215.173' the first time"
echo ""
echo "🔗 Test URLs:"
echo "   - HTTPS GraphQL: https://164.90.215.173/graphql/"
echo "   - HTTPS Admin: https://164.90.215.173/admin/"
echo ""

