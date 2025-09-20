@echo off
echo Stopping Odoo...
docker-compose down

echo Starting Odoo...
docker-compose up -d

echo Waiting for Odoo to start...
timeout /t 10 /nobreak > nul

echo Odoo restarted! Check http://localhost:8069
echo The admission module icon should now be visible.
