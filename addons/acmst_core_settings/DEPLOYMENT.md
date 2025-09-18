# ACMST Core Settings - Deployment Guide

This guide provides step-by-step instructions for deploying the ACMST Core Settings module in various environments.

## 🚀 Pre-Deployment Checklist

### System Requirements
- [ ] Odoo 17.0 installed and configured
- [ ] PostgreSQL 12+ database
- [ ] Python 3.8+ runtime
- [ ] Minimum 4GB RAM
- [ ] 10GB free disk space
- [ ] SSL certificate (for production)

### Prerequisites
- [ ] Odoo server running
- [ ] Database created
- [ ] Admin user configured
- [ ] Required modules installed (base, mail, portal, web)
- [ ] Backup of existing data (if upgrading)

## 📦 Installation Methods

### Method 1: Direct Installation

#### Step 1: Copy Module Files
```bash
# Copy module to addons directory
cp -r acmst_core_settings /path/to/odoo/addons/

# Set proper permissions
chown -R odoo:odoo /path/to/odoo/addons/acmst_core_settings
chmod -R 755 /path/to/odoo/addons/acmst_core_settings
```

#### Step 2: Update Addons List
```bash
# Restart Odoo server
sudo systemctl restart odoo

# Or if using Docker
docker-compose restart odoo
```

#### Step 3: Install Module
1. Login to Odoo as administrator
2. Go to **Apps** menu
3. Search for "ACMST Core Settings"
4. Click **Install**

### Method 2: Docker Installation

#### Step 1: Update Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  odoo:
    image: odoo:17.0
    volumes:
      - ./addons/acmst_core_settings:/mnt/extra-addons/acmst_core_settings
      - ./config:/etc/odoo
      - ./data:/var/lib/odoo
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: acmst_college
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-db-data:
```

#### Step 2: Start Services
```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs -f odoo
```

#### Step 3: Install Module
1. Access Odoo at `http://localhost:8069`
2. Create database
3. Install ACMST Core Settings module

### Method 3: Production Deployment

#### Step 1: Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip postgresql-client

# Create odoo user
sudo useradd -m -s /bin/bash odoo
sudo usermod -aG sudo odoo
```

#### Step 2: Odoo Installation
```bash
# Download Odoo 17
wget https://nightly.odoo.com/17.0/nightly/src/odoo_17.0.latest.tar.gz
tar -xzf odoo_17.0.latest.tar.gz
sudo mv odoo-17.0 /opt/odoo
sudo chown -R odoo:odoo /opt/odoo
```

#### Step 3: Database Setup
```bash
# Create database
sudo -u postgres createdb acmst_college
sudo -u postgres createuser odoo
sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'odoo_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE acmst_college TO odoo;"
```

#### Step 4: Module Installation
```bash
# Copy module
sudo cp -r acmst_core_settings /opt/odoo/addons/
sudo chown -R odoo:odoo /opt/odoo/addons/acmst_core_settings

# Create configuration
sudo tee /etc/odoo/odoo.conf > /dev/null <<EOF
[options]
admin_passwd = admin_password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_password
db_name = acmst_college
addons_path = /opt/odoo/addons
data_dir = /var/lib/odoo
logfile = /var/log/odoo/odoo.log
log_level = info
workers = 4
max_cron_threads = 2
EOF

# Create systemd service
sudo tee /etc/systemd/system/odoo.service > /dev/null <<EOF
[Unit]
Description=Odoo ERP
After=postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo-bin -c /etc/odoo/odoo.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
```

## 🔧 Configuration

### Step 1: Initial Setup
1. Access Odoo at `http://your-server:8069`
2. Create database with demo data
3. Install ACMST Core Settings module
4. Configure basic settings

### Step 2: Security Configuration
```python
# Create security groups
# 1. Go to Settings > Users & Companies > Groups
# 2. Create groups: Admin, Manager, Coordinator, Dean, Viewer
# 3. Assign appropriate permissions
# 4. Create users and assign to groups
```

### Step 3: Data Configuration
```python
# 1. Create universities
# 2. Set up colleges
# 3. Define program types
# 4. Create academic programs
# 5. Set up academic years
# 6. Configure academic rules
```

### Step 4: Performance Tuning
```python
# Update odoo.conf for production
[options]
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
```

## 🔒 Security Hardening

### Step 1: Database Security
```sql
-- Create read-only user
CREATE USER acmst_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE acmst_college TO acmst_readonly;
GRANT USAGE ON SCHEMA public TO acmst_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO acmst_readonly;
```

### Step 2: Application Security
```bash
# Set proper file permissions
sudo chmod 600 /etc/odoo/odoo.conf
sudo chown odoo:odoo /etc/odoo/odoo.conf

# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Step 3: SSL Configuration
```nginx
# nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring

### Step 1: Log Monitoring
```bash
# Monitor Odoo logs
sudo tail -f /var/log/odoo/odoo.log

# Monitor system logs
sudo journalctl -u odoo -f
```

### Step 2: Performance Monitoring
```bash
# Monitor system resources
htop
iostat -x 1
free -h

# Monitor database
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Step 3: Backup Monitoring
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump acmst_college > /backups/acmst_college_$DATE.sql
find /backups -name "*.sql" -mtime +7 -delete

# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

## 🧪 Testing

### Step 1: Unit Tests
```bash
# Run unit tests
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --unit
```

### Step 2: Performance Tests
```bash
# Run performance tests
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --performance
```

### Step 3: Security Tests
```bash
# Run security tests
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --security
```

## 🔄 Maintenance

### Daily Tasks
- [ ] Check system logs for errors
- [ ] Monitor disk space usage
- [ ] Verify backup completion
- [ ] Check application performance

### Weekly Tasks
- [ ] Review security logs
- [ ] Update system packages
- [ ] Clean old log files
- [ ] Test backup restoration

### Monthly Tasks
- [ ] Review user access permissions
- [ ] Update security patches
- [ ] Performance optimization review
- [ ] Disaster recovery testing

## 🚨 Troubleshooting

### Common Issues

#### Module Installation Fails
```bash
# Check module dependencies
python3 -c "import odoo; print(odoo.__version__)"

# Check file permissions
ls -la /opt/odoo/addons/acmst_core_settings

# Check Odoo logs
sudo tail -f /var/log/odoo/odoo.log
```

#### Database Connection Issues
```bash
# Test database connection
sudo -u postgres psql -c "SELECT version();"

# Check Odoo configuration
sudo cat /etc/odoo/odoo.conf
```

#### Performance Issues
```bash
# Check system resources
top
df -h
free -h

# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Emergency Procedures

#### System Recovery
```bash
# Stop services
sudo systemctl stop odoo

# Restore from backup
sudo -u postgres psql -c "DROP DATABASE acmst_college;"
sudo -u postgres psql -c "CREATE DATABASE acmst_college;"
sudo -u postgres psql acmst_college < /backups/latest_backup.sql

# Start services
sudo systemctl start odoo
```

#### Data Recovery
```bash
# Restore specific table
sudo -u postgres psql acmst_college -c "DROP TABLE acmst_university CASCADE;"
sudo -u postgres psql acmst_college -c "CREATE TABLE acmst_university (...);"
sudo -u postgres psql acmst_college < /backups/university_table.sql
```

## 📞 Support

### Getting Help
- Check the troubleshooting section
- Review the README.md file
- Check Odoo documentation
- Contact the development team

### Emergency Contacts
- System Administrator: admin@acmst.edu
- Development Team: dev@acmst.edu
- Database Administrator: dba@acmst.edu

---

**Note**: Always test in a staging environment before deploying to production.
