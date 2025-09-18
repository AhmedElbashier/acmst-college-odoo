#!/bin/bash

# ACMST College Odoo Start Script
# This script starts the Odoo services and performs initial setup

set -e

echo "Starting ACMST College Odoo Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p backups

# Set proper permissions
echo "Setting permissions..."
chmod 755 scripts/*.sh

# Start services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "=========================================="
echo "ACMST College Odoo is now running!"
echo "=========================================="
echo "Access URL: http://localhost:8069"
echo "Database: acmst_college"
echo "Admin Username: admin"
echo "Admin Password: admin"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo "=========================================="
