# Deploy Checklist

Project: ecomarce_choco
Droplet IP: 164.90.215.173
Repo: https://github.com/Ali-oss-cell/chocoloco.git
Linux user: django

---

## 0) Prereqs (run as root once)
```bash
apt update
apt install -y git nginx python3-venv python3-pip build-essential libpq-dev python3-dev pkg-config
# (optional ufw)
# ufw allow OpenSSH && ufw allow 80/tcp && ufw enable
adduser --disabled-password --gecos "" django || true
usermod -aG sudo django
```

## 1) SSH and code (as django)
```bash
ssh django@164.90.215.173
mkdir -p /home/django/ecomarce_choco && cd /home/django/ecomarce_choco

git clone https://github.com/Ali-oss-cell/chocoloco.git .
```

## 2) Python env and deps
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Environment variables (.env)
```bash
cat > .env << 'EOF'
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=164.90.215.173
CSRF_TRUSTED_ORIGINS=http://164.90.215.173
CORS_ALLOWED_ORIGINS=http://localhost:3000

DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=your-database-password-here
DB_HOST=your-database-host.db.ondigitalocean.com
DB_PORT=25060
TIME_ZONE=Asia/Dubai
EOF
```

## 4) DB migrate + static
```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## 5) Gunicorn service
```bash
cp deployment/gunicorn_config.py .
mkdir -p logs
sudo cp deployment/systemd.service /etc/systemd/system/ecomarce_choco.service
sudo systemctl daemon-reload
sudo systemctl enable --now ecomarce_choco
sudo systemctl status ecomarce_choco --no-pager
```

## 6) Nginx (IP only for now)
```bash
sudo sed -i 's/server_name .*/server_name 164.90.215.173;/' deployment/nginx.conf
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ecomarce_choco
sudo ln -sf /etc/nginx/sites-available/ecomarce_choco /etc/nginx/sites-enabled/ecomarce_choco
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

## 7) Verify
```bash
curl -I http://164.90.215.173/
curl -I http://164.90.215.173/admin/
curl -I http://164.90.215.173/graphql/
sudo systemctl status ecomarce_choco nginx --no-pager
```

## 8) Update workflow
```bash
ssh django@164.90.215.173
cd /home/django/ecomarce_choco
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart ecomarce_choco
```

## Notes
- When you attach a domain, update `server_name` in nginx and run certbot for HTTPS.
- psycopg v3 is already used (binary wheels): no extra build steps needed.
- Keep ownership consistent: `sudo chown -R django:www-data /home/django/ecomarce_choco`
