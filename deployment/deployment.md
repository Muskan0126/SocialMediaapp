# Django Deployment Guide

## 1. Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 2. Clone Repository

```bash
git clone <repository-url>

cd SocialMediaapp
```

---

## 3. Create Virtual Environment

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements/production.txt
```

---

## 5. Create Environment File

```bash
cp deployment/env.example .env
```

Update all environment variables.

---

## 6. Apply Migrations

```bash
python manage.py migrate
```

---

## 7. Collect Static Files

```bash
python manage.py collectstatic
```

---

## 8. Copy Gunicorn Service

```bash
sudo cp deployment/gunicorn.service \
/etc/systemd/system/
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable:

```bash
sudo systemctl enable gunicorn
```

Start:

```bash
sudo systemctl start gunicorn
```

Check:

```bash
sudo systemctl status gunicorn
```

---

## 9. Copy Nginx Configuration

```bash
sudo cp deployment/nginx.conf \
/etc/nginx/sites-available/instagram
```

Enable:

```bash
sudo ln -s \
/etc/nginx/sites-available/instagram \
/etc/nginx/sites-enabled/
```

Remove default site:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Test:

```bash
sudo nginx -t
```

Restart:

```bash
sudo systemctl restart nginx
```

---

## 10. Restart Gunicorn

```bash
sudo systemctl restart gunicorn
```

---

## 11. Verify Services

```bash
sudo systemctl status nginx

sudo systemctl status gunicorn
```

---

## 12. Visit

```
http://YOUR_SERVER_IP
```