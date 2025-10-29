# 🚀 Complete Deployment Guide - DigitalOcean Droplet

## 📋 **Overview**

This guide will walk you through deploying your Django + GraphQL API to DigitalOcean Droplet with **nginx + gunicorn** - **done the RIGHT way** to avoid headaches!

---

## ✅ **Prerequisites**

Before starting, you should have:
- ✅ DigitalOcean Droplet created (General Purpose Premium - 8 GB / 2 CPUs recommended)
- ✅ Domain name pointed to your Droplet IP (optional but recommended)
- ✅ Managed PostgreSQL database created
- ✅ Database credentials ready

---

## 📦 **Step 1: Initial Server Setup**

### **1.1 Connect to Your Droplet**

```bash
ssh root@your-droplet-ip
```

### **1.2 Update System**

```bash
apt update
apt upgrade -y
```

### **1.3 Create Non-Root User (Security Best Practice)**

```bash
adduser django
usermod -aG sudo django
su - django
```

---

## 🐍 **Step 2: Install Python & Dependencies**

### **2.1 Install Python 3.13**

```bash
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip
sudo apt install -y postgresql-client libpq-dev
sudo apt install -y nginx supervisor
sudo apt install -y git
```

### **2.2 Install SSL Certificate Tool (Let's Encrypt)**

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

## 📁 **Step 3: Deploy Your Code**

### **3.1 Create Project Directory**

```bash
cd /home/django
mkdir -p /home/django/ecomarce_choco
cd /home/django/ecomarce_choco
```

### **3.2 Clone/Upload Your Code**

**Option A: Using Git (Recommended)**
```bash
git clone your-repo-url .
```

**Option B: Using SCP (from your local machine)**
```bash
# From your local machine, run:
scp -r /home/ali/Desktop/projects/ecomarce_choco/* django@your-droplet-ip:/home/django/ecomarce_choco/
```

### **3.3 Create Virtual Environment**

```bash
cd /home/django/ecomarce_choco
python3.13 -m venv venv
source venv/bin/activate
```

### **3.4 Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔧 **Step 4: Configure Environment Variables**

### **4.1 Create .env File**

```bash
nano /home/django/ecomarce_choco/.env
```

**Paste this (replace with your actual values):**

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-generate-new-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-droplet-ip

# Database (DigitalOcean Managed PostgreSQL)
DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=your-database-password-here
DB_HOST=your-database-host.db.ondigitalocean.com
DB_PORT=25060

# CORS - Update with your React frontend domain
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Timezone
TIME_ZONE=Asia/Dubai
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

---

## 🗄️ **Step 5: Database Setup**

### **5.1 Test Database Connection**

```bash
cd /home/django/ecomarce_choco
source venv/bin/activate
python manage.py check --database default
```

### **5.2 Run Migrations**

```bash
python manage.py migrate
```

### **5.3 Create Admin User**

```bash
python manage.py createsuperuser
```

### **5.4 Collect Static Files**

```bash
python manage.py collectstatic --noinput
```

---

## ⚙️ **Step 6: Configure Gunicorn**

### **6.1 Create Gunicorn Configuration File**

```bash
nano /home/django/ecomarce_choco/gunicorn_config.py
```

**Paste this:**

```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Optimal: (2 x CPU cores) + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/django/ecomarce_choco/logs/gunicorn_access.log"
errorlog = "/home/django/ecomarce_choco/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "ecomarce_choco"

# Server mechanics
daemon = False
pidfile = "/home/django/ecomarce_choco/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed later)
# keyfile = None
# certfile = None
```

**Save and exit**

### **6.2 Create Logs Directory**

```bash
mkdir -p /home/django/ecomarce_choco/logs
```

### **6.3 Test Gunicorn Manually**

```bash
cd /home/django/ecomarce_choco
source venv/bin/activate
gunicorn --config gunicorn_config.py ecomarce_choco.wsgi:application
```

**Test:** Open browser to `http://your-droplet-ip:8000/admin` - should work!

**Stop:** Press `Ctrl+C`

---

## 🚦 **Step 7: Configure Systemd Service (Gunicorn)**

### **7.1 Create Systemd Service File**

```bash
sudo nano /etc/systemd/system/ecomarce_choco.service
```

**Paste this (IMPORTANT: Replace `django` with your username if different):**

```ini
[Unit]
Description=ecomarce_choco Gunicorn daemon
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/ecomarce_choco
Environment="PATH=/home/django/ecomarce_choco/venv/bin"
ExecStart=/home/django/ecomarce_choco/venv/bin/gunicorn \
          --config /home/django/ecomarce_choco/gunicorn_config.py \
          ecomarce_choco.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Save and exit**

### **7.2 Enable and Start Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable ecomarce_choco
sudo systemctl start ecomarce_choco
sudo systemctl status ecomarce_choco
```

**Check status:** Should show "active (running)" ✅

---

## 🌐 **Step 8: Configure Nginx**

### **8.1 Create Nginx Configuration**

```bash
sudo nano /etc/nginx/sites-available/ecomarce_choco
```

**Paste this (replace `yourdomain.com` with your domain or use IP):**

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com your-droplet-ip;

    client_max_body_size 10M;  # Allow file uploads up to 10MB

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
```

**Save and exit**

### **8.2 Enable Site and Test Configuration**

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-enabled/

# Remove default nginx site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

**Should show "active (running)" ✅**

---

## 🔒 **Step 9: Setup SSL Certificate (HTTPS)**

### **9.1 Get SSL Certificate from Let's Encrypt**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Follow prompts:**
- Enter your email
- Agree to terms
- Choose redirect HTTP to HTTPS (option 2)

**That's it!** Certbot automatically updates nginx config.

---

## 🔍 **Step 10: Final Checks & Testing**

### **10.1 Check All Services Running**

```bash
# Check Gunicorn
sudo systemctl status ecomarce_choco

# Check Nginx
sudo systemctl status nginx

# Check both are listening
sudo netstat -tlnp | grep -E ':(80|443|8000)'
```

### **10.2 Test Your API**

```bash
# Test GraphQL endpoint
curl http://yourdomain.com/graphql/

# Test admin (should redirect to HTTPS)
curl -I http://yourdomain.com/admin/
```

---

## 📝 **Common Issues & Solutions**

### **Issue 1: 502 Bad Gateway**

**Cause:** Gunicorn not running or wrong port

**Fix:**
```bash
sudo systemctl status ecomarce_choco
sudo journalctl误 -u ecomarce_choco -f  # Check logs
sudo systemctl restart ecomarce_choco
```

### **Issue 2: Static Files Not Loading**

**Cause:** Wrong paths or permissions

**Fix:**
```bash
# Check permissions
sudo chown -R django:www-data /home/django/ecomarce_choco/staticfiles
sudo chown -R django:www-data /home/django/ecomarce_choco/media

# Recollect static files
cd /home/django/ecomarce_choco
source venv/bin/activate
python manage.py collectstatic --noinput
```

### **Issue 3: Permission Denied Errors**

**Fix:**
```bash
# Fix ownership
sudo chown -R django:django /home/django/ecomarce_choco
sudo chmod -R 755 /home/django/ecomarce_choco
```

### **Issue 4: Database Connection Error**

**Fix:**
```bash
# Test connection
cd /home/django/ecomarce_choco
source venv/bin/activate
python manage.py dbshell

# Check .env file has correct credentials
cat .env | grep DB_
```

---

## 🔄 **Deployment Workflow**

### **Update Code on Server:**

```bash
# SSH to server
ssh django@your-droplet-ip

# Go to project
cd /home/django/ecomarce_choco

# Pull latest code (if using git)
git pull

# Activate virtual environment
source venv/bin/activate

# Install new dependencies (if any)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl restart ecomarce_choco

# Check status
sudo systemctl status ecomarce_choco
```

---

## 📊 **Monitoring & Logs**

### **View Logs:**

```bash
# Gunicorn logs
tail -f /home/django/ecomarce_choco/logs/gunicorn_error.log
tail -f /home/django/ecomarce_choco/logs/gunicorn_access.log

# Systemd service logs
sudo journalctl -u ecomarce_choco -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs (if configured)
tail -f /home/django/ecomarce_choco/logs/django.log
```

---

## 🔐 **Security Checklist**

- [x] Use non-root user (django)
- [x] DEBUG=False in production
- [x] ALL=.env file (not in git)
- [x] SSL certificate installed
- [x] Firewall configured (UFW)
- [x] Strong SECRET_KEY
- [x] Database uses SSL

---

## 🎯 **Quick Reference Commands**

```bash
# Restart services
sudo systemctl restart ecomarce_choco
sudo systemctl restart nginx

# Check status
sudo systemctl status ecomarce_choco
sudo systemctl status nginx

# View logs
sudo journalctl - TU ecomarce_choco -f

# Test nginx config
sudo nginx -t

# Check ports
sudo netstat -tlnp | grep -E ':(80|443|8000)'
```

---

## ✅ **You're Done!**

Your Django application should now be live at:
- **GraphQL API**: `https://yourdomain.com/graphql/`
- **Admin**: `https://yourdomain.com/admin/`
- **Static Files**: `https://yourdomain.com/static/`
- **Media Files**: `https://yourdomain.com/media/`

**Next:** Connect your React frontend to the API! 🚀

