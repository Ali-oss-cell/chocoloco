# 🚀 Quick HTTPS Setup - Step by Step

## **Option 1: Automated Script (Easiest)**

### **Step 1: SSH into your server**
```bash
ssh django@164.90.215.173
# Enter your password when prompted
```

### **Step 2: Go to project directory**
```bash
cd /home/django/ecomarce_choco
```

### **Step 3: Pull latest code (to get the script)**
```bash
git pull origin main
```

### **Step 4: Run the setup script**
```bash
sudo bash QUICK_HTTPS_SETUP.sh
```

The script will:
- ✅ Generate SSL certificate
- ✅ Update nginx configuration
- ✅ Restart services
- ✅ Test HTTPS

**Follow the prompts** - it will ask you to update `.env` file when needed.

---

## **Option 2: Manual Setup (Step by Step)**

### **Step 1: SSH into your server**
```bash
ssh django@164.90.215.173
```

### **Step 2: Install OpenSSL**
```bash
sudo apt update
sudo apt install -y openssl
```

### **Step 3: Create SSL directory**
```bash
sudo mkdir -p /etc/nginx/ssl
```

### **Step 4: Generate self-signed certificate**
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/C=AE/ST=Dubai/L=Dubai/O=ChocoEcommerce/CN=164.90.215.173"
```

### **Step 5: Set permissions**
```bash
sudo chmod 600 /etc/nginx/ssl/selfsigned.key
sudo chmod 644 /etc/nginx/ssl/selfsigned.crt
```

### **Step 6: Backup existing nginx config**
```bash
sudo cp /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-available/ecomarce_choco.backup
```

### **Step 7: Update nginx configuration**

Edit the nginx config:
```bash
sudo nano /etc/nginx/sites-available/ecomarce_choco
```

**Replace the entire file with this:**

```nginx
upstream django {
    server 127.0.0.1:8000;
}

# HTTP Server - Redirect to HTTPS
server {
    listen 80;
    server_name 164.90.215.173;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name 164.90.215.173;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 10M;

    location /static/ {
        alias /home/django/ecomarce_choco/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/django/ecomarce_choco/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

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

    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~ /\. {
        deny all;
    }
}
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### **Step 8: Test nginx configuration**
```bash
sudo nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### **Step 9: Restart nginx**
```bash
sudo systemctl restart nginx
```

### **Step 10: Update Django .env file**
```bash
nano /home/django/ecomarce_choco/.env
```

**Add or update these lines:**
```env
USE_HTTPS=True
FRONTEND_URL=https://clownfish-app-2ehbt.ondigitalocean.app
BACKEND_URL=https://164.90.215.173
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### **Step 11: Restart Django service**
```bash
sudo systemctl restart ecomarce_choco
```

### **Step 12: Test HTTPS**
```bash
curl -k https://164.90.215.173/graphql/
```

**Expected:** Should return a response (even if it's an error, that means HTTPS is working)

---

## **Step 13: Update Frontend**

Change your frontend API URL from:
```
http://164.90.215.173/graphql/
```

To:
```
https://164.90.215.173/graphql/
```

---

## **✅ Verify Everything Works**

### **Test from browser:**
1. Open: `https://164.90.215.173/graphql/`
2. You'll see a security warning (this is normal for self-signed certificates)
3. Click "Advanced" → "Proceed to 164.90.215.173 (unsafe)"
4. You should see the GraphiQL interface

### **Test from frontend:**
- Your frontend should now be able to connect without mixed content errors

---

## **🔧 Troubleshooting**

### **If nginx test fails:**
```bash
# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Check your config syntax
sudo nginx -t
```

### **If Django service won't start:**
```bash
# Check service status
sudo systemctl status ecomarce_choco

# Check logs
sudo journalctl -u ecomarce_choco -n 50
```

### **If HTTPS doesn't work:**
```bash
# Check if nginx is listening on port 443
sudo netstat -tlnp | grep 443

# Check nginx status
sudo systemctl status nginx
```

---

## **📝 Summary**

After completing these steps:
- ✅ HTTPS is enabled on your backend
- ✅ HTTP automatically redirects to HTTPS
- ✅ Frontend can connect without mixed content errors
- ⚠️ Browsers will show security warning (normal for self-signed certificates)

**Next:** When you get a domain, follow the guide in `HTTPS_SETUP_GUIDE.md` to migrate to Let's Encrypt!

