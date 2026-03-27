# Fleet Intelligence AI - Deployment Guide

## 🚀 Production Deployment Options

---

## Option 1: Streamlit Cloud (Easiest - Free)

### **Prerequisites**
- GitHub account
- Streamlit Cloud account (free signup at streamlit.io)

### **Step 1: Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit: Fleet Intelligence AI"
git remote add origin https://github.com/YOUR_USERNAME/fleet-ai.git
git push -u origin main
```

### **Step 2: Connect to Streamlit Cloud**
1. Go to https://streamlit.io/cloud
2. Click "Create app" → Select your GitHub repo
3. Select branch: `main`
4. Select script path: `app/main.py`
5. Click "Deploy"

### **Step 3: Configure Secrets** (for API keys, if needed)
Create `.streamlit/secrets.toml`:
```toml
database_url = "postgresql://..."
api_key = "your-api-key"
```

**Constraints**:
- 3 free apps per account
- Limited resources (but fine for <5000 vehicles)
- Good for demos and small teams

---

## Option 2: Docker Deployment (Recommended for Scale)

### **Prerequisites**
- Docker installed
- Docker Hub account (optional, for image registry)
- Linux server or Docker-enabled cloud provider

### **Step 1: Build Docker Image**
```bash
# From app directory
docker build -t fleet-ai:latest .
```

### **Step 2: Run Container Locally**
```bash
docker run -p 8501:8501 \
           -v $(pwd)/data:/app/data \
           fleet-ai:latest
```

### **Step 3: Push to Registry** (for production)
```bash
# Tag image
docker tag fleet-ai:latest YOUR_REGISTRY/fleet-ai:latest

# Push
docker push YOUR_REGISTRY/fleet-ai:latest
```

### **Step 4: Deploy to Production Server**
```bash
# On production server
docker pull YOUR_REGISTRY/fleet-ai:latest

# Run with persistent data and restart policy
docker run -d \
           -p 8501:8501 \
           -v /data/fleet:/app/data \
           --restart unless-stopped \
           --name fleet-ai \
           YOUR_REGISTRY/fleet-ai:latest
```

### **Docker Compose** (Advanced)
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  fleet-ai:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - fleet-ai
```

Then run:
```bash
docker-compose up -d
```

---

## Option 3: Linux Server (Traditional)

### **Prerequisites**
- Ubuntu 20.04+ or similar
- Python 3.9+
- git, curl, nginx

### **Step 1: Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx supervisor git

# Create app user
sudo useradd -m -s /bin/bash fleet-ai
sudo -u fleet-ai mkdir -p /home/fleet-ai/app
```

### **Step 2: Deploy Application**
```bash
# As fleet-ai user
cd /home/fleet-ai/app
git clone https://github.com/YOUR_USERNAME/fleet-ai.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt
```

### **Step 3: Supervisor Configuration** (Process Manager)
Create `/etc/supervisor/conf.d/fleet-ai.conf`:
```ini
[program:fleet-ai]
directory=/home/fleet-ai/app
command=/home/fleet-ai/app/venv/bin/streamlit run app/main.py --server.port 8501
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fleet-ai/out.log
environment=PATH="/home/fleet-ai/app/venv/bin"
user=fleet-ai
```

Start service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fleet-ai
```

### **Step 4: Nginx Setup** (Reverse Proxy)
Create `/etc/nginx/sites-available/fleet-ai`:
```nginx
server {
    listen 80;
    server_name fleet-ai.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fleet-ai.yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/fleet-ai.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fleet-ai.yourdomain.com/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/fleet-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 5: SSL Certificate** (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d fleet-ai.yourdomain.com
```

---

## Option 4: Heroku (Deprecated but still works)

### **Prerequisites**
- Heroku CLI installed
- Heroku account

### **Step 1: Create Procfile**
```
web: cd app && streamlit run main.py --server.port $PORT
```

### **Step 2: Deploy**
```bash
heroku login
heroku create fleet-ai-app
git push heroku main
heroku logs --tail
```

---

## Option 5: AWS Deployment

### **Using Elastic Beanstalk**
```yaml
# .ebextensions/python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app/main.py
```

Then:
```bash
eb init
eb create fleet-ai-env
eb deploy
```

### **Using EC2 + Auto-scaling**
1. Create EC2 instance (Ubuntu 20.04)
2. Follow "Linux Server" option above
3. Create AMI from configured instance
4. Set up Auto Scaling Group with:
   - Min: 1, Max: 5 instances
   - Load Balancer: Application Load Balancer
   - Health check: HTTP on port 80

---

## 📊 Performance Tuning

### **For 500+ Vehicles**

```python
# In config.py
PERFORMANCE_TUNING = {
    'cache_results': True,              # Cache feature calculations
    'cache_ttl_seconds': 300,           # 5-minute cache
    'parallel_processing': True,        # Use multiprocessing
    'chunk_size': 100,                  # Process in batches
    'optimize_memory': True,            # Memory-efficient pandas ops
}
```

### **Streamlit-specific Optimizations**

```python
# Cache expensive operations
@st.cache_data(ttl=300)
def load_and_process_data(file_path):
    df = pd.read_csv(file_path)
    return process_pipeline(df)

# Cache visualizations
@st.cache_resource
def get_plotly_figure():
    return px.scatter(...)
```

### **Server-level Optimizations**

```bash
# Increase file limits
ulimit -n 65536

# Tune TCP settings
sysctl -w net.core.somaxconn=1024
sysctl -w net.ipv4.tcp_max_syn_backlog=1024

# Increase memory
# Edit /etc/security/limits.conf
```

---

## 🔐 Security Best Practices

### **1. Environment Variables**
```bash
# Never commit sensitive data
# Use .env files (in .gitignore)
API_KEY=your_api_key_here
DATABASE_URL=postgresql://...

# In code
import os
api_key = os.getenv('API_KEY')
```

### **2. Data Protection**
```python
# Encrypt sensitive data
from cryptography.fernet import Fernet

def encrypt_vehicle_data(df):
    # Encrypt PII columns
    cipher = Fernet(key)
    df['encrypted_id'] = df['vehicle_id'].apply(cipher.encrypt)
    return df.drop('vehicle_id', axis=1)
```

### **3. API Security**
```python
# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/v1/risk')
@limiter.limit("100 per hour")
def get_risk():
    ...

# Authentication
from flask_jwt_extended import JWTManager, jwt_required

@app.route('/api/v1/data')
@jwt_required()
def get_data():
    ...
```

### **4. Database Security**
- Use strong passwords
- Restrict network access to DB
- Enable SSL for DB connections
- Regular backups with encryption

### **5. Server Security**
```bash
# Firewall rules
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable

# Automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📈 Monitoring & Logging

### **Application Monitoring**
```python
# In utils/logger.py
import logging
from pythonjsonlogger import jsonlogger

handler = logging.FileHandler('logs/app.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
```

### **System Monitoring** (Prometheus + Grafana)
```bash
# Install Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Install Grafana
docker run -d -p 3000:3000 grafana/grafana
```

Configure Prometheus scrape targets:
```yaml
scrape_configs:
  - job_name: 'fleet-ai'
    static_configs:
      - targets: ['localhost:8501']
```

### **Error Tracking** (Sentry)
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    "https://...@sentry.io/...",
    integrations=[FlaskIntegration()]
)
```

---

## 🧪 Automated Testing & CI/CD

### **GitHub Actions Workflow**
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy Fleet AI

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r app/requirements.txt
          pip install pytest
      
      - name: Run tests
        run: pytest tests/
      
      - name: Build Docker image
        run: docker build -t fleet-ai .
      
      - name: Push to Docker Hub
        uses: docker/build-push-action@v2
        with:
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/fleet-ai:latest
      
      - name: Deploy to production
        run: |
          # SSH into production server and pull latest image
          ssh -i ${{ secrets.SSH_KEY }} user@server.com "cd /app && docker-compose pull && docker-compose up -d"
```

---

## 📊 Scaling Strategies

### **Horizontal Scaling**
- Load balance multiple instances
- Use database for session state
- CDN for static assets

### **Vertical Scaling**
- Increase server RAM
- Use faster CPU
- More powerful GPU

### **Database Scaling**
```
SQLite (dev) → PostgreSQL (prod) → PostgreSQL + Read Replicas (scale)
```

---

## 🚨 Disaster Recovery

### **Backup Strategy**
```bash
# Daily backups
0 2 * * * /usr/local/bin/backup-fleet-ai.sh > /var/log/backups.log

# Backup script
#!/bin/bash
BACKUP_DIR="/backups/fleet-ai/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Backup database
pg_dump fleet_ai_db > $BACKUP_DIR/db.sql

# Backup data files
tar -czf $BACKUP_DIR/data.tar.gz /app/data

# Upload to cloud storage
aws s3 sync $BACKUP_DIR s3://fleet-ai-backups/$(date +%Y/%m/%d)/
```

### **Disaster Recovery Plan**
1. **RTO** (Recovery Time Objective): <1 hour
2. **RPO** (Recovery Point Objective): <30 minutes
3. **Test recovery monthly**

---

## 📞 Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Port already in use | `lsof -i :8501` then `kill -9 <PID>` |
| Out of memory | Increase swap or upgrade server |
| Database connection errors | Check connection string in `.env` |
| Slow dashboard | Enable caching or add more workers |
| SSL certificate errors | Renew with `certbot renew` |

---

## ✅ Pre-launch Checklist

- [ ] All tests passing
- [ ] Documentation complete
- [ ] Secrets in environment variables
- [ ] SSL/HTTPS configured
- [ ] Database backups scheduled
- [ ] Monitoring set up
- [ ] Rate limiting enabled
- [ ] Error tracking configured
- [ ] Performance tested with 500+ vehicles
- [ ] Security audit completed

---

**Ready for production!** Choose your deployment option and get Fleet Intelligence AI live.
