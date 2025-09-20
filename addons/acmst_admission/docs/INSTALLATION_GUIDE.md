# ACMST Admission Module - Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Post-Installation Setup](#post-installation-setup)
5. [Troubleshooting](#troubleshooting)
6. [Upgrade Instructions](#upgrade-instructions)

## Prerequisites

### System Requirements
- **Odoo Version**: 17.0 or later
- **Python Version**: 3.8 or later
- **Database**: PostgreSQL 12 or later
- **Memory**: Minimum 4GB RAM (8GB recommended for production)
- **Storage**: Minimum 10GB free space

### Dependencies
The module automatically installs the following Odoo modules:
- `base` (Core Odoo functionality)
- `mail` (Email notifications)
- `portal` (Portal access)
- `web` (Web interface)
- `website` (Website functionality)

## Installation Steps

### 1. Download the Module
```bash
# Clone the repository or download the module files
git clone <repository-url>
cd acmst-college-odoo
```

### 2. Copy Module to Addons Directory
```bash
# Copy the module to your Odoo addons directory
cp -r addons/acmst_admission /path/to/odoo/addons/
```

### 3. Update Module List
1. Log in to your Odoo instance as an administrator
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Search for "ACMST Admission"

### 4. Install the Module
1. Click on the **ACMST Admission** module
2. Click **Install**
3. Wait for the installation to complete

## Configuration

### 1. Security Groups Setup
After installation, configure the following security groups:

#### Admin Group
- **Name**: `acmst_admission.group_admin`
- **Users**: System administrators
- **Permissions**: Full access to all admission features

#### Manager Group
- **Name**: `acmst_admission.group_manager`
- **Users**: Admission managers
- **Permissions**: View and approve admission files

#### Coordinator Group
- **Name**: `acmst_admission.group_coordinator`
- **Users**: Program coordinators
- **Permissions**: Set conditions and review applications

#### Health Group
- **Name**: `acmst_admission.group_health`
- **Users**: Health department staff
- **Permissions**: Manage health checks and medical assessments

#### Officer Group
- **Name**: `acmst_admission.group_officer`
- **Users**: Admission officers
- **Permissions**: Process applications and manage files

#### Portal Group
- **Name**: `acmst_admission.group_portal`
- **Users**: Students and applicants
- **Permissions**: Submit applications and view status

### 2. Portal Configuration
1. Go to **Settings** > **Users & Companies** > **Portal**
2. Enable portal access for the admission module
3. Configure portal settings:
   - **Portal URL**: Set the base URL for the portal
   - **Email Templates**: Configure notification templates
   - **File Upload Limits**: Set maximum file sizes

### 3. Email Configuration
1. Go to **Settings** > **Technical** > **Email** > **Outgoing Mail Servers**
2. Configure your SMTP server
3. Test email delivery

### 4. Workflow Configuration
1. Go to **Admission** > **Configuration** > **Workflow Engine**
2. Configure workflow states and transitions
3. Set up approval chains
4. Configure automated notifications

## Post-Installation Setup

### 1. Create Initial Data
1. Go to **Admission** > **Configuration** > **Admission Rules**
2. Create admission rules for different programs
3. Set up program coordinators
4. Configure health check requirements

### 2. Portal Setup
1. Go to **Admission** > **Configuration** > **Portal Settings**
2. Configure portal appearance and functionality
3. Set up application forms
4. Configure file upload settings

### 3. Performance Optimization
1. Go to **Admission** > **Performance** > **Optimizations**
2. Review and activate performance optimizations
3. Configure caching settings
4. Set up monitoring alerts

### 4. Testing
1. Create test admission files
2. Test portal functionality
3. Verify email notifications
4. Test workflow transitions

## Troubleshooting

### Common Issues

#### Module Installation Fails
**Problem**: Module fails to install with dependency errors
**Solution**: 
1. Ensure all required Odoo modules are installed
2. Check Python dependencies
3. Verify database permissions

#### Portal Access Issues
**Problem**: Users cannot access the portal
**Solution**:
1. Check portal group assignments
2. Verify portal configuration
3. Check URL routing

#### Email Notifications Not Working
**Problem**: Email notifications are not being sent
**Solution**:
1. Check SMTP configuration
2. Verify email templates
3. Check mail queue status

#### Performance Issues
**Problem**: Slow response times or high memory usage
**Solution**:
1. Check performance optimizations
2. Review database indexes
3. Monitor system resources

### Debug Mode
Enable debug mode for troubleshooting:
1. Go to **Settings** > **Technical** > **Activate the developer mode**
2. Check logs in **Settings** > **Technical** > **Logging**
3. Use the browser developer tools for frontend issues

### Log Files
Check the following log files:
- **Odoo Server Log**: `/var/log/odoo/odoo-server.log`
- **Database Log**: Check PostgreSQL logs
- **Web Server Log**: Check Apache/Nginx logs

## Upgrade Instructions

### 1. Backup
Before upgrading, create a backup:
```bash
# Database backup
pg_dump -h localhost -U odoo -d odoo_db > backup_$(date +%Y%m%d_%H%M%S).sql

# File system backup
tar -czf odoo_files_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/odoo/
```

### 2. Update Module
1. Download the new version
2. Replace the module files
3. Update the module list
4. Upgrade the module

### 3. Post-Upgrade
1. Check for any new configuration options
2. Update customizations if needed
3. Test all functionality
4. Monitor performance

## Support

### Documentation
- **Technical Documentation**: `docs/TECHNICAL_DOCUMENTATION.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **User Guide**: `docs/USER_GUIDE.md`

### Contact
- **Email**: support@acmst.edu
- **Phone**: +1-555-0123
- **Website**: https://www.acmst.edu

### Bug Reports
Report bugs through:
1. Odoo Community Forum
2. GitHub Issues
3. Direct email to support

## License

This module is licensed under the AGPL-3.0 License. See the LICENSE file for details.

---

**Note**: This installation guide is for ACMST Admission Module v1.0.0. For other versions, please refer to the specific version documentation.
