# Git Deployment Setup (Droplet)

Use this guide to deploy the repository to your Droplet and keep it updated.

- **Repository**: [Ali-oss-cell/chocoloco](https://github.com/Ali-oss-cell/chocoloco.git)
- **Droplet IP**: 164.90.215.173
- **Linux user**: django (replace if different)

---

## Server Paths

- Project root: `/home/django/ecomarce_choco`
- Virtualenv: `/home/django/ecomarce_choco/venv`
- Gunicorn config: `/home/django/ecomarce_choco/gunicorn_config.py`
- Logs dir: `/home/django/ecomarce_choco/logs`
- Systemd service: `/etc/systemd/system/ecomarce_choco.service`
- Nginx site: `/etc/nginx/sites-available/ecomarce_choco`
- Static files: `/home/django/ecomarce_choco/staticfiles/`
- Media files: `/home/django/ecomarce_choco/media/`

---

## One-Time Setup

```bash
# 1) SSH into the Droplet
ssh django@164.90.215.173

# 2) Create project directory
mkdir -p /home/django/ecomarce_choco
cd /home/django/ecomarce_choco

# 3) Clone the repository
# If repo is public:
git clone https://github.com/Ali-oss-cell/chocoloco.git .

# 4) Create virtualenv and install dependencies
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5) Create .env (fill with your production values)
nano .env

# 6) Initialize database and static files
python manage.py migrate
python manage.py collectstatic --noinput

# 7) Copy production configs
cp deployment/gunicorn_config.py .
mkdir -p logs

sudo cp deployment/systemd.service /etc/systemd/system/ecomarce_choco.service
sudo systemctl daemon-reload
sudo systemctl enable ecomarce_choco
sudo systemctl start ecomarce_choco

# 8) Nginx (use IP now; swap to domain later)
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ecomarce_choco
sudo ln -s /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default || true
sudo nginx -t && sudo systemctl restart nginx
```

---

## Update Workflow (Pull Latest Code)

```bash
ssh django@164.90.215.173
cd /home/django/ecomarce_choco

# Pull latest changes
source venv/bin/activate
git pull

# Apply updates
pip install -r requirements.txt  # if requirements changed
python manage.py migrate
python manage.py collectstatic --noinput

# Restart app
sudo systemctl restart ecomarce_choco
```

---

## Optional: Deploy with SSH Key (Private Repo)
If the repository becomes private, add your Droplet's public key to GitHub Deploy Keys or your GitHub account.

```bash
# Generate key on Droplet (if you don't have one)
ssh-keygen -t ed25519 -C "deploy@chocoloco" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub  # add this to GitHub

# Test access (for private repo URLs)
ssh -T git@github.com

# Use the SSH URL to clone
# git clone git@github.com:Ali-oss-cell/chocoloco.git .
```

---

## Environment Checklist (.env)

```bash
SECRET_KEY=your-strong-secret
DEBUG=False
ALLOWED_HOSTS=164.90.215.173
CSRF_TRUSTED_ORIGINS=http://164.90.215.173
CORS_ALLOWED_ORIGINS=http://localhost:3000

DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
TIME_ZONE=Asia/Dubai
```

---

## Quick Verification

```bash
# App endpoints (HTTP only for now)
curl -I http://164.90.215.173/
curl -I http://164.90.215.173/admin/
curl -I http://164.90.215.173/graphql/

# Services
sudo systemctl status ecomarce_choco
sudo systemctl status nginx
```

---

## Notes
- Use the IP in `server_name` inside the Nginx config until a domain is attached.
- When you add a domain, update `server_name` and run certbot for HTTPS.
- Always keep ownership consistent:
  - `sudo chown -R django:www-data /home/django/ecomarce_choco`

---

## Reference
- Repository: [https://github.com/Ali-oss-cell/chocoloco.git](https://github.com/Ali-oss-cell/chocoloco.git)
- See also: `DEPLOYMENT_GUIDE.md` and `deployment/QUICK_START.md`
