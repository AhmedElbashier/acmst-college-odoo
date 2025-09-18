#!/bin/bash

# ACMST College Odoo Stop Script
# This script stops the Odoo services

set -e

echo "Stopping ACMST College Odoo Services..."

# Stop services
docker-compose down

echo "Services stopped successfully!"

# Optional: Remove containers and volumes (uncomment if needed)
# echo "Removing containers and volumes..."
# docker-compose down -v
# docker system prune -f

echo "All services have been stopped."
