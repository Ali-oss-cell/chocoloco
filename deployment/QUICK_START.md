# ⚡ Quick Start Deployment Checklist

## 📋 **Pre-Deployment Checklist**

- [ ] DigitalOcean Droplet created (8 GB / 2 CPUs recommended)
- [ ] Domain name pointed to Droplet IP (optional)
- [ ] Managed PostgreSQL database created
- [ ] Database credentials ready

---

## 🚀 **Step-by-Step Deployment** (30 minutes)

### **1. Initial Server Setup (5 min)**

```bash
# Connect to Droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Create user
adduser django
usermod -aG sudo django
su - django
```

### **2. Install Dependencies (5 min)**

```bash
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip
sudo apt install -y postgresql-client libpq-dev nginx certbot python3-certbot-nginx git
```

### **3. Deploy Code (5 min)**

```bash
cd /home/django
git clone your-repo-url ecomarce_choco
# OR upload via SCP from local machine

cd ecomarce_choco
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### **4. Configure Environment (3 min)**

```bash
nano .env
# Paste your .env file with production values:
# - DEBUG=False
# - ALLOWED_HOSTS=yourdomain.com,your-droplet-ip
# - Database credentials
```

### **5. Setup Database (2 min)**

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### **6. Configure Gunicorn (2 min)**

```bash
# Copy config file (already in deployment/ folder)
cp deployment/gunicorn_config.py .
mkdir -p logs
```

### **7. Setup Systemd Service (3 min)**

```bash
sudo cp deployment/systemd.service /etc/systemd/system/ecomarce_choco.service
sudo systemctl daemon-reload
sudo systemctl enable ecomarce_choco
sudo systemctl start ecomarce_choco
sudo systemctl status ecomarce_choco  # Should be running ✅
```

### **8. Configure Nginx (3 min)**

```bash
# Edit nginx.conf first - replace yourdomain.com with your domain
nano deployment/nginx.conf

# Copy to nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ecomarce_choco
sudo ln -s /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### **9. Setup SSL (2 min)**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Done!** 🎉

---

## ✅ **Verify Deployment**

```bash
# Check services
sudo systemctl status ecomarce_choco
sudo systemctl status nginx

# Test endpoints
curl https://yourdomain.com/graphql/
curl https://yourdomain.com/admin/
```

---

## 🔄 **Update Code Later**

```bash
cd /home/django/ecomarce_choco
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart ecomarce_choco
```

---

## 🐛 **Common Issues**

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | `sudo systemctl restart ecomarce_choco` |
| Static files not loading | `python manage.py collectstatic --noinput` |
| Permission denied | `sudo chown -R django:www-data /home/django/ecomarce_choco` |
| Nginx error | `sudo nginx -t` to check config |

---

## 📁 **Files Created**

All config files are in `/deployment/` folder:
- ✅ `gunicorn_config.py` - Gunicorn settings
- ✅ `nginx.conf` - Nginx configuration
- ✅ `systemd.service` - Service file
- ✅ `DEPLOYMENT_SCRIPTS.sh` - Automated setup (optional)

**That's it! Follow the guide and you're live! 🚀**

