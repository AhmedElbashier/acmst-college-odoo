#!/bin/bash

# ACMST College Odoo Restore Script
# This script restores the Odoo database and filestore from backup

set -e

# Configuration
BACKUP_DIR="./backups"
DB_NAME="acmst_college"
DB_USER="odoo"
DB_PASSWORD="odoo"
DB_HOST="localhost"
DB_PORT="5432"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: Backup directory '$BACKUP_DIR' does not exist!"
    exit 1
fi

# List available backups
echo "Available backups:"
ls -la "$BACKUP_DIR" | grep "acmst_college_db_"

# Get backup date from user
read -p "Enter the backup date (YYYYMMDD_HHMMSS): " BACKUP_DATE

if [ -z "$BACKUP_DATE" ]; then
    echo "Error: No backup date provided!"
    exit 1
fi

# Check if backup files exist
DB_BACKUP="$BACKUP_DIR/acmst_college_db_$BACKUP_DATE.sql"
FILESTORE_BACKUP="$BACKUP_DIR/acmst_college_filestore_$BACKUP_DATE.tar.gz"
CONFIG_BACKUP="$BACKUP_DIR/acmst_college_config_$BACKUP_DATE.tar.gz"

if [ ! -f "$DB_BACKUP" ]; then
    echo "Error: Database backup file '$DB_BACKUP' not found!"
    exit 1
fi

echo "Starting restore process for ACMST College Odoo..."
echo "WARNING: This will overwrite the current database and filestore!"

read -p "Are you sure you want to continue? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop Odoo service
echo "Stopping Odoo service..."
docker-compose stop odoo

# Drop and recreate database
echo "Recreating database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# Restore database
echo "Restoring database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < "$DB_BACKUP"

# Restore filestore
if [ -f "$FILESTORE_BACKUP" ]; then
    echo "Restoring filestore..."
    mkdir -p ./data
    tar -xzf "$FILESTORE_BACKUP" -C ./data
fi

# Restore configuration
if [ -f "$CONFIG_BACKUP" ]; then
    echo "Restoring configuration..."
    tar -xzf "$CONFIG_BACKUP" -C ./config
fi

# Start Odoo service
echo "Starting Odoo service..."
docker-compose up -d

echo "Restore completed successfully!"
echo "You can now access Odoo at http://localhost:8069"
