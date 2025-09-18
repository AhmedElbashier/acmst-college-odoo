#!/bin/bash

# ACMST College Odoo Backup Script
# This script creates a backup of the Odoo database and filestore

set -e

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="acmst_college"
DB_USER="odoo"
DB_PASSWORD="odoo"
DB_HOST="localhost"
DB_PORT="5432"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting backup process for ACMST College Odoo..."

# Database backup
echo "Creating database backup..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/acmst_college_db_$DATE.sql"

# Filestore backup
echo "Creating filestore backup..."
if [ -d "./data/filestore" ]; then
    tar -czf "$BACKUP_DIR/acmst_college_filestore_$DATE.tar.gz" -C ./data filestore
fi

# Configuration backup
echo "Creating configuration backup..."
tar -czf "$BACKUP_DIR/acmst_college_config_$DATE.tar.gz" -C ./config .

echo "Backup completed successfully!"
echo "Files created:"
echo "- Database: $BACKUP_DIR/acmst_college_db_$DATE.sql"
echo "- Filestore: $BACKUP_DIR/acmst_college_filestore_$DATE.tar.gz"
echo "- Config: $BACKUP_DIR/acmst_college_config_$DATE.tar.gz"

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "acmst_college_*" -type f -mtime +7 -delete

echo "Backup process completed!"
