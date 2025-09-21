# ACMST Core Settings - User Guide

This guide provides comprehensive instructions for end users on how to use the ACMST Core Settings module effectively.

## 👤 Target Audience

This guide is designed for:
- **System Administrators**: Setting up and configuring the system
- **Academic Managers**: Managing universities, colleges, and programs
- **Department Coordinators**: Creating and managing batches
- **Deans and Department Heads**: Overseeing academic structures
- **IT Support Staff**: Troubleshooting and maintenance

## 🚀 Getting Started

### System Access
1. **Login to Odoo** using your credentials
2. **Navigate to ACMST Core Settings** in the main menu
3. **Verify your permissions** and access level

### Initial System Setup

#### Step 1: University Setup
1. Go to **ACMST Core Settings > Configuration > Universities**
2. Click **Create** to add a new university
3. Fill in the required information:
   - **University Name**: Full official name
   - **University Code**: Unique identifier (auto-generated)
   - **Address**: Complete address
   - **Contact Information**: Phone, email, website
4. Mark as **Main University** if applicable
5. Click **Save**

#### Step 2: College Setup
1. Go to **ACMST Core Settings > Configuration > Colleges**
2. Click **Create** to add a new college
3. Fill in the required information:
   - **College Name**: Department/college name
   - **College Code**: Unique code within university
   - **University**: Select parent university
   - **Dean**: Assign department dean (optional)
4. Click **Save**

#### Step 3: Program Types Setup
1. Go to **ACMST Core Settings > Programs > Program Types**
2. Click **Create** to add a new program type
3. Fill in the required information:
   - **Program Type Name**: e.g., "Bachelor's Degree"
   - **Code**: Unique identifier
   - **Description**: Program type details
4. Click **Save**

#### Step 4: Academic Programs Setup
1. Go to **ACMST Core Settings > Programs > Programs**
2. Click **Create** to add a new program
3. Fill in the required information:
   - **Program Name**: Official program name
   - **Program Code**: Unique code within college
   - **College**: Select parent college
   - **Program Type**: Select program type
   - **Program Manager**: Assign program manager
   - **Coordinator**: Assign academic coordinator
   - **Duration**: Academic duration in years
   - **Total Credits**: Credit hours required
4. Click **Save**

#### Step 5: Academic Years Setup
1. Go to **ACMST Core Settings > Configuration > Academic Years**
2. Click **Create** to add a new academic year
3. Fill in the required information:
   - **Year Name**: e.g., "2024-2025"
   - **Start Date**: Academic year start
   - **End Date**: Academic year end
   - **Current Year**: Mark as current if applicable
4. Click **Save**

#### Step 6: Academic Rules Setup
1. Go to **ACMST Core Settings > Academic Rules**
2. Click **Create** to add a new academic rule
3. Fill in the required information:
   - **Rule Name**: Descriptive rule name
   - **Rule Type**: Select rule category
   - **Level**: University, College, or Program level
   - **Priority**: Rule priority (1-10)
   - **Effective Date**: When rule takes effect
   - **Description**: Detailed rule description
4. Click **Save**

## 📚 Using Core Features

### University Management

#### Viewing University Information
1. Go to **ACMST Core Settings > Configuration > Universities**
2. Click on any university to view details
3. Review **Statistics** tab for overview
4. Check **Colleges** tab for associated colleges

#### Editing University Details
1. Open the university record
2. Click **Edit**
3. Modify required information
4. Click **Save**

#### University Statistics
- **Colleges Count**: Number of active colleges
- **Programs Count**: Total programs across all colleges
- **Batches Count**: Total batches across all programs
- **Active Students**: Total enrolled students (computed)

### College Management

#### Creating New Colleges
1. Go to **ACMST Core Settings > Configuration > Colleges**
2. Click **Create**
3. Select **University** from dropdown
4. Enter **College Name** and **Code**
5. Assign **Dean** (optional)
6. Click **Save**

#### Managing College Programs
1. Open a college record
2. Go to **Programs** tab
3. Click **Create** to add new programs
4. View existing programs and their details

#### College Dashboard
- **Programs Count**: Active programs in college
- **Batches Count**: Total batches in college
- **Active Students**: Enrolled students count

### Program Management

#### Program Overview
1. Go to **ACMST Core Settings > Programs > Programs**
2. Browse all programs by college
3. Use filters to find specific programs
4. Click on programs for detailed view

#### Program Details Management
- **Basic Information**: Name, code, description
- **Academic Details**: Duration, credits, requirements
- **Management**: Program manager and coordinator
- **Statistics**: Batches count, enrollment numbers

#### Program-Specific Actions
1. **View Batches**: See all batches for the program
2. **Create Batches**: Use batch creation wizard
3. **Manage Coordinators**: Assign or change coordinators
4. **Update Requirements**: Modify academic requirements

### Batch Management

#### Using Batch Creation Wizard
1. Go to **ACMST Core Settings > Batches**
2. Click **Create Batches** (wizard button)
3. Select **Program** and **Academic Year**
4. Set **Number of Batches** to create
5. Set **Capacity per Batch**
6. Preview batch details
7. Click **Create Batches**

#### Batch Information Management
1. **Basic Details**: Name, code, capacity, dates
2. **Enrollment Tracking**: Current vs. capacity
3. **Registration Periods**: Start and end dates
4. **Academic Association**: Program and year links

#### Batch Operations
- **View Students**: See enrolled students
- **Update Capacity**: Modify batch capacity
- **Change Dates**: Update academic calendar
- **Archive Batches**: Mark as inactive

### Academic Year Management

#### Current Year Setup
1. Go to **ACMST Core Settings > Configuration > Academic Years**
2. Find the current academic year
3. Click **Edit**
4. Check **Current Year** checkbox
5. Click **Save**

#### Academic Calendar Management
- **Year Definition**: Start and end dates
- **Semester Management**: Define academic periods
- **Holiday Configuration**: Set non-academic periods
- **Batch Association**: Link batches to academic years

### Academic Rules Configuration

#### Creating Academic Rules
1. Go to **ACMST Core Settings > Academic Rules**
2. Click **Create**
3. Select **Rule Type** (enrollment, graduation, etc.)
4. Set **Rule Level** (university, college, program)
5. Define **Priority** and **Effective Date**
6. Add detailed **Description**

#### Rule Management
- **Rule Categories**: Enrollment, graduation, transfer, etc.
- **Level Hierarchy**: University > College > Program
- **Priority System**: Higher numbers = higher priority
- **Date Ranges**: Rules active during specific periods

## 📊 Reports and Analytics

### Built-in Reports
1. **University Report**: Comprehensive university overview
2. **College Report**: Department-specific statistics
3. **Program Report**: Program performance metrics
4. **Batch Report**: Batch enrollment and capacity
5. **Academic Rules Report**: Rules compliance summary

### Generating Reports
1. Go to **ACMST Core Settings > Reports**
2. Select report type
3. Set date range and filters
4. Click **Generate Report**
5. Export to PDF or Excel

### Dashboard Access
1. **Manager Dashboard**: For management overview
2. **Coordinator Dashboard**: For academic coordination
3. **Dean Dashboard**: For departmental oversight
4. **Statistics Dashboard**: For system-wide metrics

## 👥 User Management

### Security Groups Overview

#### ACMST Core Settings Admin
- Full access to all core settings functionality
- Can create, modify, and delete all records
- Access to system configuration
- Audit trail management

#### ACMST Manager
- College and program management
- Can create and modify colleges and programs
- Batch creation and management
- Limited deletion rights

#### ACMST Coordinator
- Program coordination access
- Batch management within assigned programs
- Student enrollment oversight
- Report generation

#### ACMST Dean
- College-level access
- Program oversight within college
- Academic rule management
- Department statistics

#### ACMST Viewer
- Read-only access to all information
- Cannot modify any data
- Can generate reports
- Access to dashboards

### User Assignment
1. Go to **Settings > Users & Companies > Users**
2. Select user to modify
3. Go to **Access Rights** tab
4. Assign appropriate **Security Groups**
5. Set **Default Access Rights**

## 🔧 Advanced Features

### Data Import/Export
1. **Export Data**: Select records and export to Excel
2. **Import Data**: Use Odoo import tools for bulk data
3. **Template Download**: Get import templates
4. **Data Validation**: Check data before import

### Search and Filtering
1. **Basic Search**: Use search bar for quick lookup
2. **Advanced Filters**: Create complex filter criteria
3. **Group By**: Group records by various fields
4. **Favorites**: Save frequently used searches

### Bulk Operations
1. **Bulk Update**: Select multiple records for batch updates
2. **Bulk Archive**: Archive multiple records at once
3. **Bulk Delete**: Delete multiple records (admin only)
4. **Bulk Actions**: Custom actions on selected records

### Data Validation
1. **Field Validation**: Automatic validation on save
2. **Constraint Checking**: Business rule validation
3. **Required Fields**: Mandatory field enforcement
4. **Format Validation**: Date, email, phone format checks

## 🐛 Troubleshooting

### Common Issues

#### Cannot Create Universities
- Check user permissions
- Verify required fields are filled
- Check for duplicate codes

#### College Creation Fails
- Ensure parent university exists
- Check unique code constraints
- Verify user has manager permissions

#### Program Creation Issues
- Verify college and program type exist
- Check code uniqueness within college
- Ensure required fields are completed

#### Batch Creation Problems
- Check program and academic year exist
- Verify capacity is greater than 0
- Ensure start date is before end date

#### Permission Errors
- Check user security groups
- Verify record-level access rules
- Contact administrator for permission updates

### Getting Help
1. **Check Documentation**: Review this user guide
2. **Search Knowledge Base**: Use built-in help system
3. **Contact Support**: Reach out to IT support team
4. **Check Logs**: System administrators can check logs

### Performance Tips
1. **Use Filters**: Apply filters to limit data display
2. **Archive Old Records**: Archive completed academic years
3. **Regular Cleanup**: Remove unnecessary test data
4. **Optimize Searches**: Use specific search terms

## 📱 Mobile Access

### Responsive Design
- All interfaces are mobile-friendly
- Touch-optimized controls
- Responsive tables and forms
- Mobile navigation menu

### Offline Capabilities
- Basic viewing when offline
- Cached data access
- Synchronization on reconnection

## 🔒 Security Best Practices

### User Guidelines
1. **Use Strong Passwords**: Follow password policies
2. **Logout When Done**: Always logout from shared computers
3. **Report Issues**: Report security concerns immediately
4. **Data Privacy**: Handle sensitive data appropriately

### Administrator Guidelines
1. **Regular Audits**: Review user access regularly
2. **Permission Reviews**: Update permissions as needed
3. **Security Updates**: Keep system updated
4. **Backup Procedures**: Regular data backups

## 📞 Support Information

### Contact Information
- **IT Support**: support@acmst.edu
- **System Administrator**: admin@acmst.edu
- **Academic Affairs**: academic@acmst.edu

### Support Hours
- **Monday - Friday**: 8:00 AM - 6:00 PM
- **Saturday**: 9:00 AM - 2:00 PM
- **Sunday**: Closed

### Emergency Support
- **Phone**: +966-12-123-4567
- **Email**: emergency@acmst.edu
- **Available**: 24/7 for critical issues

---

**Note**: This user guide is regularly updated. For the latest version, please check the system documentation or contact your system administrator.
