# Deployment Guide

Complete guide for deploying the AI Product Search & Chatbot to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Platforms](#cloud-platforms)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Security Checklist](#security-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Disk Space**: 500MB minimum
- **OS**: Windows, Linux, or macOS

### Required Tools

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# Install virtualenv (if not present)
pip install virtualenv
```

---

## Local Development

### 1. Clone Repository

```powershell
git clone <repository-url>
cd "AI PBL"
```

### 2. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env file with your settings
notepad .env
```

**Minimum Configuration (.env)**:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### 5. Run Development Server

```powershell
python run.py
```

Application will be available at: `http://localhost:5000`

---

## Production Deployment

### Option 1: Gunicorn (Linux/Mac)

#### 1. Install Gunicorn

```bash
pip install gunicorn
```

#### 2. Create systemd Service

Create file: `/etc/systemd/system/ai-chatbot.service`

```ini
[Unit]
Description=AI Product Search Chatbot
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-chatbot
Environment="PATH=/var/www/ai-chatbot/.venv/bin"
ExecStart=/var/www/ai-chatbot/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "app.main:app"

[Install]
WantedBy=multi-user.target
```

#### 3. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl start ai-chatbot
sudo systemctl enable ai-chatbot
sudo systemctl status ai-chatbot
```

#### 4. Configure Nginx Reverse Proxy

Create file: `/etc/nginx/sites-available/ai-chatbot`

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/ai-chatbot/static;
        expires 30d;
    }
}
```

#### 5. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/ai-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Waitress (Windows)

#### 1. Install Waitress

```powershell
pip install waitress
```

#### 2. Create run_production.py

```python
from waitress import serve
from app.main import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=4)
```

#### 3. Run Production Server

```powershell
python run_production.py
```

#### 4. Create Windows Service (Optional)

Use NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM
# https://nssm.cc/download

# Install service
nssm install AIProductChatbot "C:\Path\To\Python\python.exe" "C:\Path\To\Project\run_production.py"

# Start service
nssm start AIProductChatbot
```

---

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p persist data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app.main:app"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./persist:/app/persist
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_TOKEN=${ADMIN_TOKEN}
    restart: unless-stopped
```

### 3. Create .dockerignore

```
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.git/
.gitignore
.env
*.log
archive/
tests/
```

### 4. Build and Run

```powershell
# Build image
docker build -t ai-chatbot .

# Run container
docker run -d -p 5000:5000 --name ai-chatbot ai-chatbot

# Or use docker-compose
docker-compose up -d
```

### 5. Docker Commands

```powershell
# View logs
docker logs ai-chatbot

# Stop container
docker stop ai-chatbot

# Restart container
docker restart ai-chatbot

# Remove container
docker rm ai-chatbot
```

---

## Cloud Platforms

### Heroku

#### 1. Create Procfile

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT "app.main:app"
```

#### 2. Create runtime.txt

```
python-3.9.16
```

#### 3. Deploy

```powershell
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Open app
heroku open
```

### AWS EC2

#### 1. Launch EC2 Instance

- AMI: Ubuntu 22.04 LTS
- Instance Type: t2.micro (free tier) or t2.small
- Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

#### 2. Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Clone repository
git clone <repository-url>
cd ai-chatbot

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Follow Gunicorn + Nginx steps from above
```

### Google Cloud Platform (Cloud Run)

#### 1. Create cloudbuild.yaml

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-chatbot', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-chatbot']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'ai-chatbot'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ai-chatbot'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
```

#### 2. Deploy

```bash
gcloud builds submit --config cloudbuild.yaml
```

### DigitalOcean App Platform

#### 1. Create app.yaml

```yaml
name: ai-chatbot
services:
  - name: web
    github:
      repo: your-username/your-repo
      branch: main
    build_command: pip install -r requirements.txt
    run_command: gunicorn -w 4 -b 0.0.0.0:8080 "app.main:app"
    envs:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        value: ${SECRET_KEY}
    http_port: 8080
```

---

## Monitoring & Maintenance

### Logging

#### 1. Configure Python Logging

Create `app/logging_config.py`:

```python
import logging
import os

def setup_logging():
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
```

#### 2. Use in Application

```python
from app.logging_config import setup_logging
setup_logging()
```

### Health Checks

Add to `app/main.py`:

```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
```

### Monitoring Tools

**Free Options**:
- **UptimeRobot**: Simple uptime monitoring
- **Pingdom**: Free tier available
- **StatusCake**: Basic monitoring

**Paid Options**:
- **New Relic**: Application performance monitoring
- **Datadog**: Comprehensive monitoring
- **Sentry**: Error tracking

### Backup Strategy

```powershell
# Backup script (backup.ps1)
$date = Get-Date -Format "yyyy-MM-dd"
$backupDir = "backups\$date"

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force

# Backup persist directory
Copy-Item -Path "persist\*" -Destination "$backupDir\persist\" -Recurse -Force

# Backup data directory
Copy-Item -Path "data\*" -Destination "$backupDir\data\" -Recurse -Force

Write-Host "Backup completed: $backupDir"
```

Schedule with Windows Task Scheduler or cron (Linux).

---

## Security Checklist

### Before Production

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Disable `DEBUG` mode
- [ ] Set strong admin credentials
- [ ] Rotate admin token
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Update all dependencies
- [ ] Remove test/debug endpoints
- [ ] Implement rate limiting
- [ ] Set up CORS properly
- [ ] Review error messages (no sensitive data)
- [ ] Enable security headers

### Security Headers (Nginx)

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run
```

---

## Troubleshooting

### Issue: Application won't start

**Check**:
```powershell
# Python version
python --version

# Dependencies installed
pip list

# Environment variables
Get-Content .env
```

**Solution**:
```powershell
pip install -r requirements.txt --upgrade
```

### Issue: "Module not found" errors

**Solution**:
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port already in use

**Windows**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

**Linux**:
```bash
# Find and kill process
sudo lsof -ti:5000 | xargs kill -9
```

### Issue: Permission denied errors

**Linux**:
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/project

# Fix permissions
chmod -R 755 /path/to/project
```

### Issue: Slow index building

**Optimize**:
- Reduce `max_features` in TF-IDF config
- Use smaller dataset for testing
- Increase available RAM
- Use SSD storage

### Issue: Out of memory

**Solutions**:
- Reduce worker count in Gunicorn
- Increase swap space
- Upgrade server RAM
- Optimize TF-IDF parameters

---

## Performance Optimization

### 1. Enable Gzip Compression (Nginx)

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 2. Cache Static Files

```nginx
location /static {
    alias /var/www/ai-chatbot/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 3. Optimize Gunicorn Workers

```bash
# Formula: (2 x CPU cores) + 1
gunicorn -w 5 -b 0.0.0.0:5000 "app.main:app"
```

### 4. Use Redis for Caching (Future)

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/search')
@cache.cached(timeout=300, query_string=True)
def search():
    # ...
```

---

## Rollback Procedure

### Git-based Rollback

```bash
# View recent commits
git log --oneline -n 10

# Rollback to specific commit
git checkout <commit-hash>

# Restart application
sudo systemctl restart ai-chatbot
```

### Docker Rollback

```powershell
# List images
docker images

# Run previous version
docker run -d -p 5000:5000 --name ai-chatbot ai-chatbot:previous-tag
```

---

**Last Updated**: November 2025  
**Deployment Version**: 1.0.0
