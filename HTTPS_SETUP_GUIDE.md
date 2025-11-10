# 🔒 HTTPS Setup Guide

## 📋 **Your Options**

### **Option 1: Self-Signed Certificate (IP Address) - NOW**
- ✅ Works immediately
- ✅ Fixes mixed content errors
- ⚠️ Browser shows security warning (users must accept)
- ⚠️ Not trusted by browsers automatically
- **Best for:** Development/testing, temporary solution

### **Option 2: Let's Encrypt (Domain) - LATER**
- ✅ Free SSL certificate
- ✅ Trusted by all browsers
- ✅ No security warnings
- ⚠️ Requires a domain name
- **Best for:** Production

---

## 🚀 **Step 1: Set Up HTTPS on IP (Self-Signed Certificate)**

### **On Your Server (SSH into 164.90.215.173):**

```bash
# 1. Install OpenSSL (if not already installed)
sudo apt update
sudo apt install -y openssl

# 2. Create directory for certificates
sudo mkdir -p /etc/nginx/ssl

# 3. Generate self-signed certificate (valid for 1 year)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/selfsigned.key \
  -out /etc/nginx/ssl/selfsigned.crt \
  -subj "/C=AE/ST=Dubai/L=Dubai/O=ChocoEcommerce/CN=164.90.215.173"

# 4. Set proper permissions
sudo chmod 600 /etc/nginx/ssl/selfsigned.key
sudo chmod 644 /etc/nginx/ssl/selfsigned.crt
```

### **Update Nginx Configuration:**

Create/update `/etc/nginx/sites-available/ecomarce_choco`:

```nginx
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
```

### **Apply Configuration:**

```bash
# Test nginx configuration
sudo nginx -t

# If test passes, restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### **Update Django Settings:**

Update your `.env` file on the server:

```env
USE_HTTPS=True
FRONTEND_URL=https://clownfish-app-2ehbt.ondigitalocean.app
BACKEND_URL=https://164.90.215.173
```

Then restart your Django service:

```bash
sudo systemctl restart ecomarce_choco
```

### **Update Frontend:**

Change your frontend API URL from:
```
http://164.90.215.173/graphql/
```

To:
```
https://164.90.215.173/graphql/
```

### **Test:**

```bash
# Test HTTPS endpoint
curl -k https://164.90.215.173/graphql/

# The -k flag ignores self-signed certificate warnings
```

**Note:** Browsers will show a security warning. Users need to click "Advanced" → "Proceed to 164.90.215.173 (unsafe)" the first time.

---

## 🌐 **Step 2: Migrate to Domain with Let's Encrypt (LATER)**

When you're ready to use a domain:

### **Prerequisites:**
1. Domain name (e.g., `api.yourdomain.com`)
2. DNS A record pointing to `164.90.215.173`

### **Install Certbot:**

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### **Get Let's Encrypt Certificate:**

```bash
# Replace 'api.yourdomain.com' with your actual domain
sudo certbot --nginx -d api.yourdomain.com

# Follow the prompts:
# - Enter your email
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)
```

Certbot will automatically:
- ✅ Get a free SSL certificate
- ✅ Update nginx configuration
- ✅ Set up auto-renewal
- ✅ Redirect HTTP to HTTPS

### **Update Nginx Configuration:**

Certbot will automatically update your nginx config. It will look like:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # ... rest of your config
}
```

### **Update Django Settings:**

```env
USE_HTTPS=True
ALLOWED_HOSTS=api.yourdomain.com,164.90.215.173
FRONTEND_URL=https://clownfish-app-2ehbt.ondigitalocean.app
BACKEND_URL=https://api.yourdomain.com
```

### **Update CORS Settings:**

In `settings.py`, add your domain:

```python
CORS_ALLOWED_ORIGINS = [
    "https://clownfish-app-2ehbt.ondigitalocean.app",
    # Add other origins as needed
]

CSRF_TRUSTED_ORIGINS = [
    "https://clownfish-app-2ehbt.ondigitalocean.app",
    "https://api.yourdomain.com",
]
```

### **Update Frontend:**

Change API URL to:
```
https://api.yourdomain.com/graphql/
```

### **Verify Auto-Renewal:**

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Check renewal status
sudo systemctl status certbot.timer
```

---

## 🔄 **Migration Checklist**

When moving from IP to domain:

- [ ] Domain DNS A record points to `164.90.215.173`
- [ ] Certbot certificate obtained
- [ ] Nginx configuration updated
- [ ] Django `ALLOWED_HOSTS` updated
- [ ] Django `BACKEND_URL` updated
- [ ] Frontend API URL updated
- [ ] CORS settings updated
- [ ] Test HTTPS endpoint
- [ ] Test frontend connection
- [ ] Remove old self-signed certificate (optional)

---

## ⚠️ **Important Notes**

### **Self-Signed Certificate:**
- Users will see a security warning in browsers
- Not suitable for production with real customers
- Good for development/testing
- Works for API calls from your frontend (with proper configuration)

### **Let's Encrypt Certificate:**
- Free and trusted by all browsers
- Auto-renews every 90 days
- Requires domain name
- Best for production

### **Mixed Content:**
- HTTPS frontend → HTTPS backend ✅ Works
- HTTPS frontend → HTTP backend ❌ Blocked by browsers
- HTTP frontend → HTTPS backend ✅ Works (but not recommended)

---

## 🧪 **Testing**

### **Test HTTPS Endpoint:**

```bash
# With self-signed (ignore warning)
curl -k https://164.90.215.173/graphql/

# With Let's Encrypt (no warning)
curl https://api.yourdomain.com/graphql/
```

### **Test from Frontend:**

In browser console:
```javascript
fetch('https://164.90.215.173/graphql/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: '{ __typename }'})
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

---

## 📚 **Quick Reference**

### **Current Setup (IP with Self-Signed):**
- Backend: `https://164.90.215.173/graphql/`
- Certificate: `/etc/nginx/ssl/selfsigned.crt`
- Browser warning: Yes (users must accept)

### **Future Setup (Domain with Let's Encrypt):**
- Backend: `https://api.yourdomain.com/graphql/`
- Certificate: `/etc/letsencrypt/live/api.yourdomain.com/fullchain.pem`
- Browser warning: No (trusted certificate)

---

**That's it! You can start with self-signed on IP, then migrate to domain later! 🚀**

