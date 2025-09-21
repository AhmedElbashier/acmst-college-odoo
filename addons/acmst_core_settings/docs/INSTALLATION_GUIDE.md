# ACMST Core Settings - Installation Guide

This guide provides detailed instructions for installing, configuring, and deploying the ACMST Core Settings module in various environments.

## 📋 Prerequisites

### System Requirements
- **Odoo Version**: 17.0 or higher
- **Python**: 3.8 or higher
- **PostgreSQL**: 12.0 or higher
- **Memory**: Minimum 4GB RAM
- **Disk Space**: 10GB free space
- **Operating System**: Linux (Ubuntu 20.04+), Windows 10+, or macOS 10.15+

### Required Dependencies
- Odoo base modules: `base`, `mail`, `portal`, `web`
- Python packages: `psycopg2`, `lxml`, `pillow`, `reportlab`
- System packages: `python3-dev`, `libxml2-dev`, `libxslt-dev`, `libjpeg-dev`

## 🚀 Installation Methods

### Method 1: Docker Installation (Recommended)

#### Step 1: Environment Setup
```bash
# Clone the repository
git clone https://github.com/AhmedElbashier/acmst-college-odoo.git
cd acmst-college-odoo

# Configure environment variables
cp env.example .env
nano .env  # Edit database credentials
```

#### Step 2: Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f odoo
```

#### Step 3: Access Odoo
1. Open browser and go to `http://localhost:8069`
2. Create a new database
3. Install ACMST Core Settings module

### Method 2: Manual Installation

#### Step 1: Odoo Setup
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip python3-dev libxml2-dev libxslt-dev libjpeg-dev

# Install Odoo 17 (if not already installed)
pip3 install odoo==17.0
```

#### Step 2: Module Installation
```bash
# Copy module to Odoo addons directory
sudo cp -r acmst_core_settings /path/to/odoo/addons/

# Set proper permissions
sudo chown -R odoo:odoo /path/to/odoo/addons/acmst_core_settings
sudo chmod -R 755 /path/to/odoo/addons/acmst_core_settings
```

#### Step 3: Database Setup
```bash
# Create database
sudo -u postgres createdb acmst_college
sudo -u postgres createuser -s odoo
sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'odoo_password';"
```

#### Step 4: Configuration
```bash
# Create Odoo configuration file
sudo tee /etc/odoo/odoo.conf > /dev/null <<EOF
[options]
admin_passwd = admin_password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_password
db_name = acmst_college
addons_path = /path/to/odoo/addons
data_dir = /var/lib/odoo
logfile = /var/log/odoo/odoo.log
log_level = info
workers = 4
max_cron_threads = 2
EOF
```

### Method 3: Production Deployment

#### Step 1: Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip postgresql postgresql-contrib nginx

# Create odoo system user
sudo useradd -m -s /bin/bash odoo
sudo usermod -aG sudo odoo
```

#### Step 2: PostgreSQL Configuration
```bash
# Configure PostgreSQL for production
sudo -u postgres createuser -s odoo
sudo -u postgres createdb acmst_college
sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'secure_odoo_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE acmst_college TO odoo;"

# Optimize PostgreSQL configuration
sudo tee /etc/postgresql/15/main/postgresql.conf > /dev/null <<EOF
# Performance settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_segments = 32
checkpoint_completion_target = 0.9
wal_buffers = 8MB
default_statistics_target = 100
EOF
```

#### Step 3: Odoo Installation
```bash
# Download and install Odoo 17
wget https://nightly.odoo.com/17.0/nightly/src/odoo_17.0.latest.tar.gz
tar -xzf odoo_17.0.latest.tar.gz
sudo mv odoo-17.0 /opt/odoo
sudo chown -R odoo:odoo /opt/odoo

# Install Python dependencies
sudo -u odoo pip3 install --user psycopg2-binary lxml pillow reportlab
```

#### Step 4: Module Deployment
```bash
# Copy modules
sudo cp -r acmst_core_settings /opt/odoo/addons/
sudo chown -R odoo:odoo /opt/odoo/addons/acmst_core_settings

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
```

## 🔧 Post-Installation Configuration

### Step 1: Initial Setup
1. Access Odoo at `http://your-server:8069`
2. Login with admin credentials
3. Go to **Apps** menu
4. Search for "ACMST Core Settings"
5. Click **Install**

### Step 2: Security Configuration
```bash
# Create security groups via interface
1. Go to Settings > Users & Companies > Groups
2. Create the following groups:
   - ACMST Core Settings Admin
   - ACMST Manager
   - ACMST Coordinator
   - ACMST Dean
   - ACMST Viewer
3. Assign appropriate permissions
4. Create users and assign to groups
```

### Step 3: Data Configuration
```python
# Initial data setup sequence:
1. Create Universities
2. Create Colleges under universities
3. Define Program Types
4. Create Academic Programs
5. Set up Academic Years
6. Configure Academic Rules
7. Create initial Batches using the wizard
```

### Step 4: Performance Tuning
```bash
# Database optimization
sudo -u postgres psql acmst_college -c "VACUUM ANALYZE;"

# Create indexes (already handled by module)
# The module automatically creates necessary indexes

# Configure cron jobs for maintenance
sudo crontab -e
# Add: 0 2 * * * /usr/bin/vacuumdb -d acmst_college
```

## 🔒 Security Hardening

### Database Security
```sql
-- Create read-only user for reporting
CREATE USER acmst_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE acmst_college TO acmst_readonly;
GRANT USAGE ON SCHEMA public TO acmst_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO acmst_readonly;
```

### Application Security
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

### SSL Configuration (Nginx)
```nginx
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

## 📊 Monitoring and Maintenance

### Log Monitoring
```bash
# Monitor Odoo logs
sudo tail -f /var/log/odoo/odoo.log

# Monitor system performance
htop
iostat -x 1
free -h
```

### Database Maintenance
```bash
# Weekly maintenance script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump acmst_college > /backups/acmst_college_$DATE.sql

# Clean old backups (keep 7 days)
find /backups -name "*.sql" -mtime +7 -delete

# Vacuum and analyze
vacuumdb -d acmst_college -f -v

# Reindex if needed
reindexdb -d acmst_college
```

### Performance Monitoring
```bash
# Monitor database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check table sizes
sudo -u postgres psql -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"

# Monitor slow queries
sudo -u postgres psql -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## 🧪 Testing Installation

### Unit Tests
```bash
# Run unit tests
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --unit

# Run with verbose output
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --all --verbose
```

### Integration Tests
```bash
# Run integration tests
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --integration

# Test with sample data
python3 /opt/odoo/addons/acmst_core_settings/tests/test_runner.py --demo-data
```

## 🚨 Troubleshooting

### Common Issues

#### Module Installation Fails
```bash
# Check Python path
python3 -c "import sys; print(sys.path)"

# Check module dependencies
python3 -c "import odoo; print(odoo.__version__)"

# Check file permissions
ls -la /opt/odoo/addons/acmst_core_settings/
```

#### Database Connection Issues
```bash
# Test database connection
sudo -u postgres psql -c "SELECT version();"

# Check Odoo configuration
sudo cat /etc/odoo/odoo.conf

# Test connection from Odoo user
sudo -u odoo psql -h localhost -d acmst_college -c "SELECT 1;"
```

#### Performance Issues
```bash
# Check system resources
top
df -h
free -h

# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Analyze query performance
sudo -u postgres psql -c "EXPLAIN ANALYZE SELECT * FROM acmst_university;"
```

## 📞 Support and Maintenance

### Getting Help
- Check the troubleshooting section above
- Review the README.md file for common solutions
- Check Odoo documentation for general issues
- Contact the development team for module-specific issues

### Emergency Contacts
- **System Administrator**: admin@acmst.edu
- **Database Administrator**: dba@acmst.edu
- **Development Team**: dev@acmst.edu

### Maintenance Schedule
- **Daily**: Log monitoring, backup verification
- **Weekly**: Security updates, performance review
- **Monthly**: Full system maintenance, user access review
- **Quarterly**: Security audit, disaster recovery testing

---

**Note**: Always test in a staging environment before deploying to production. Keep regular backups and monitor system performance continuously.
