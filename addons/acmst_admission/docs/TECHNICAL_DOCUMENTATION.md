# ACMST Admission Module - Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Model Specifications](#model-specifications)
4. [API Reference](#api-reference)
5. [Security Implementation](#security-implementation)
6. [Performance Optimization](#performance-optimization)
7. [Testing Framework](#testing-framework)
8. [Deployment Guide](#deployment-guide)
9. [Maintenance](#maintenance)

## Architecture Overview

### System Architecture

The ACMST Admission Module follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Portal Templates  │  Backend Views  │  Reports  │  APIs   │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Models  │  Workflows  │  Controllers  │  Wizards  │  Rules │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ORM  │  Database  │  Caching  │  File Storage  │  Email  │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Odoo Framework  │  PostgreSQL  │  Redis  │  Nginx  │  SSL  │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
acmst_admission/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── acmst_admission_file.py
│   ├── acmst_health_check.py
│   ├── acmst_coordinator_condition.py
│   ├── acmst_admission_approval.py
│   ├── acmst_portal_application.py
│   ├── acmst_workflow_engine.py
│   ├── acmst_audit_log.py
│   └── acmst_performance.py
├── views/
│   ├── acmst_admission_file_views.xml
│   ├── acmst_health_check_views.xml
│   ├── acmst_coordinator_condition_views.xml
│   ├── acmst_admission_approval_views.xml
│   ├── acmst_portal_application_views.xml
│   ├── acmst_workflow_engine_views.xml
│   ├── acmst_audit_log_views.xml
│   ├── acmst_performance_views.xml
│   └── acmst_admission_menus.xml
├── controllers/
│   └── main.py
├── wizards/
│   ├── __init__.py
│   ├── acmst_admission_wizard.py
│   └── acmst_coordinator_condition_wizard.py
├── security/
│   ├── ir.model.access.csv
│   └── ir.rule.xml
├── data/
│   └── acmst_admission_data.xml
├── demo/
│   └── acmst_admission_demo.xml
├── reports/
│   └── health_check_report_template.xml
├── static/
│   ├── src/
│   │   ├── css/
│   │   │   ├── acmst_admission.css
│   │   │   └── acmst_admission_portal.css
│   │   ├── js/
│   │   │   ├── acmst_admission.js
│   │   │   └── acmst_admission_portal.js
│   │   └── xml/
│   │       ├── acmst_admission_portal_templates.xml
│   │       ├── acmst_admission_portal_dashboard.xml
│   │       ├── acmst_admission_form_wizard.xml
│   │       ├── acmst_admission_dashboard.xml
│   │       └── acmst_admission_progress_tracking.xml
├── tests/
│   ├── __init__.py
│   ├── test_admission_file.py
│   ├── test_health_check.py
│   ├── test_coordinator_condition.py
│   ├── test_admission_approval.py
│   ├── test_portal_application.py
│   ├── test_workflow_engine.py
│   ├── test_audit_log.py
│   ├── test_controllers.py
│   ├── test_reports.py
│   ├── test_security.py
│   ├── test_wizards.py
│   ├── test_performance.py
│   └── test_integration.py
└── docs/
    ├── README.md
    ├── TECHNICAL_DOCUMENTATION.md
    └── API_REFERENCE.md
```

## Database Schema

### Core Tables

#### acmst_admission_file
```sql
CREATE TABLE acmst_admission_file (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    applicant_name VARCHAR(255) NOT NULL,
    national_id VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    program_id INTEGER REFERENCES acmst_program(id),
    batch_id INTEGER REFERENCES acmst_batch(id),
    birth_date DATE,
    gender VARCHAR(10),
    nationality VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(255),
    emergency_phone VARCHAR(20),
    state VARCHAR(50) DEFAULT 'draft',
    coordinator_id INTEGER REFERENCES res_users(id),
    student_id INTEGER REFERENCES res_partner(id),
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id)
);
```

#### acmst_health_check
```sql
CREATE TABLE acmst_health_check (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    admission_file_id INTEGER REFERENCES acmst_admission_file(id),
    examiner_id INTEGER REFERENCES res_users(id),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    bmi DECIMAL(5,2),
    blood_type VARCHAR(10),
    medical_fitness VARCHAR(20),
    has_chronic_diseases BOOLEAN DEFAULT FALSE,
    chronic_diseases_details TEXT,
    takes_medications BOOLEAN DEFAULT FALSE,
    medications_details TEXT,
    has_allergies BOOLEAN DEFAULT FALSE,
    allergies_details TEXT,
    has_disabilities BOOLEAN DEFAULT FALSE,
    disabilities_details TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    medical_notes TEXT,
    restrictions TEXT,
    state VARCHAR(50) DEFAULT 'draft',
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id)
);
```

#### acmst_coordinator_condition
```sql
CREATE TABLE acmst_coordinator_condition (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    admission_file_id INTEGER REFERENCES acmst_admission_file(id),
    coordinator_id INTEGER REFERENCES res_users(id),
    subject_name VARCHAR(255) NOT NULL,
    subject_code VARCHAR(50),
    level VARCHAR(20),
    description TEXT,
    deadline DATE,
    completion_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    state VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    create_date TIMESTAMP DEFAULT NOW(),
    write_date TIMESTAMP DEFAULT NOW(),
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id)
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX acmst_admission_file_state_date_idx ON acmst_admission_file(state, create_date);
CREATE INDEX acmst_admission_file_name_id_idx ON acmst_admission_file(applicant_name, national_id);
CREATE INDEX acmst_health_check_file_state_idx ON acmst_health_check(admission_file_id, state);
CREATE INDEX acmst_coordinator_condition_file_state_idx ON acmst_coordinator_condition(admission_file_id, state);
CREATE INDEX acmst_admission_approval_file_type_idx ON acmst_admission_approval(admission_file_id, approval_type);
CREATE INDEX acmst_portal_application_state_date_idx ON acmst_portal_application(state, create_date);
CREATE INDEX acmst_audit_log_model_id_date_idx ON acmst_audit_log(res_model_id, res_id, create_date);
```

## Model Specifications

### AcmstAdmissionFile

**Purpose**: Central model managing the complete admission process

**Key Fields**:
- `applicant_name`: Full name of the applicant
- `national_id`: Unique national identification number
- `state`: Current workflow state
- `program_id`: Reference to academic program
- `batch_id`: Reference to academic batch

**Key Methods**:
- `action_submit()`: Submit application for review
- `action_ministry_approve()`: Approve at ministry level
- `action_health_required()`: Require health check
- `action_health_approved()`: Approve health check
- `action_coordinator_review()`: Send for coordinator review
- `action_manager_approve()`: Approve at manager level
- `action_complete()`: Complete admission process

**State Machine**:
```
draft → submitted → ministry_approved → health_required → health_approved → 
coordinator_review → coordinator_conditional → manager_approved → completed
```

### AcmstHealthCheck

**Purpose**: Medical assessment and fitness evaluation

**Key Fields**:
- `height`: Applicant height in cm
- `weight`: Applicant weight in kg
- `bmi`: Calculated BMI value
- `medical_fitness`: Fitness assessment result
- `blood_type`: Blood type information

**Key Methods**:
- `action_submit()`: Submit health check for review
- `action_approve()`: Approve health check
- `action_reject()`: Reject health check
- `get_bmi_category()`: Get BMI category
- `get_health_summary()`: Get comprehensive health summary

### AcmstCoordinatorCondition

**Purpose**: Academic prerequisites and conditional requirements

**Key Fields**:
- `subject_name`: Name of the subject
- `subject_code`: Subject code
- `level`: Academic level
- `deadline`: Completion deadline
- `status`: Completion status

**Key Methods**:
- `action_complete()`: Mark condition as completed
- `action_reject()`: Reject condition
- `get_condition_summary()`: Get condition summary
- `get_condition_statistics()`: Get statistics

### AcmstWorkflowEngine

**Purpose**: Configurable workflow management

**Key Fields**:
- `name`: Workflow name
- `model_id`: Target model
- `active`: Workflow status

**Key Methods**:
- `_run_workflow_rules()`: Execute workflow rules
- `action_view_states()`: View workflow states
- `action_view_rules()`: View workflow rules

## API Reference

### REST API Endpoints

#### Portal Application

```python
# Submit application
POST /admission/submit
Content-Type: application/x-www-form-urlencoded

Parameters:
- applicant_name: string (required)
- national_id: string (required)
- phone: string (required)
- email: string (required)
- program_id: integer (required)
- batch_id: integer (required)
- birth_date: date (required)
- gender: string (required)
- nationality: string (required)
- address: string (required)
- emergency_contact: string (required)
- emergency_phone: string (required)

Response:
{
    "success": true,
    "application_id": 123,
    "message": "Application submitted successfully"
}
```

#### Application Status

```python
# Check application status
GET /admission/status/<int:application_id>

Response:
{
    "application_id": 123,
    "status": "submitted",
    "current_state": "Ministry Review",
    "progress": 25,
    "next_steps": ["Health Check", "Coordinator Review", "Manager Approval"]
}
```

#### Health Check

```python
# Submit health check
POST /admission/health-check/<int:admission_file_id>
Content-Type: application/x-www-form-urlencoded

Parameters:
- height: float (required)
- weight: float (required)
- blood_type: string (required)
- medical_fitness: string (required)
- has_chronic_diseases: boolean
- chronic_diseases_details: string
- takes_medications: boolean
- medications_details: string
- has_allergies: boolean
- allergies_details: string
- has_disabilities: boolean
- disabilities_details: string
- follow_up_required: boolean
- follow_up_date: date
- medical_notes: string
- restrictions: string

Response:
{
    "success": true,
    "health_check_id": 456,
    "message": "Health check submitted successfully"
}
```

### Python API

#### Model Operations

```python
# Create admission file
admission_file = env['acmst.admission.file'].create({
    'applicant_name': 'John Doe',
    'national_id': '1234567890',
    'phone': '+966501234567',
    'email': 'john.doe@example.com',
    'program_id': program.id,
    'batch_id': batch.id,
    'birth_date': '1990-01-01',
    'gender': 'male',
    'nationality': 'Saudi',
    'address': '123 Test Street, Riyadh',
    'emergency_contact': 'Jane Doe',
    'emergency_phone': '+966501234568'
})

# Workflow transitions
admission_file.action_submit()
admission_file.action_ministry_approve()
admission_file.action_health_required()
admission_file.action_health_approved()
admission_file.action_coordinator_review()
admission_file.action_manager_approve()
admission_file.action_complete()

# Search and filtering
admission_files = env['acmst.admission.file'].search([
    ('state', '=', 'submitted'),
    ('program_id', '=', program.id)
])

# Read operations
admission_file.read(['name', 'state', 'applicant_name'])

# Update operations
admission_file.write({'notes': 'Updated notes'})

# Delete operations
admission_file.unlink()
```

#### Workflow Operations

```python
# Create workflow engine
workflow = env['acmst.workflow.engine'].create({
    'name': 'Admission Workflow',
    'model_id': env['ir.model']._get('acmst.admission.file').id,
    'description': 'Complete admission workflow'
})

# Create workflow states
state1 = env['acmst.workflow.state'].create({
    'name': 'draft',
    'workflow_id': workflow.id,
    'is_initial': True,
    'description': 'Initial state'
})

# Create workflow rules
rule1 = env['acmst.workflow.rule'].create({
    'name': 'Auto Submit',
    'workflow_id': workflow.id,
    'trigger_event': 'on_create',
    'action_type': 'update_field',
    'action_value': 'submitted'
})
```

## Security Implementation

### Access Control

#### Model Access Rights

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_acmst_admission_file_admin,acmst.admission.file.admin,model_acmst_admission_file,acmst_admission.group_admin,1,1,1,1
access_acmst_admission_file_manager,acmst.admission.file.manager,model_acmst_admission_file,acmst_admission.group_manager,1,1,1,0
access_acmst_admission_file_coordinator,acmst.admission.file.coordinator,model_acmst_admission_file,acmst_admission.group_coordinator,1,1,0,0
access_acmst_admission_file_health,acmst.admission.file.health,model_acmst_admission_file,acmst_admission.group_health,1,0,0,0
access_acmst_admission_file_officer,acmst.admission.file.officer,model_acmst_admission_file,acmst_admission.group_officer,1,1,1,0
access_acmst_admission_file_portal,acmst.admission.file.portal,model_acmst_admission_file,acmst_admission.group_portal,1,0,0,0
```

#### Record Rules

```xml
<record id="acmst_admission_file_rule_admin" model="ir.rule">
    <field name="name">Admission File: Admin Access</field>
    <field name="model_id" ref="model_acmst_admission_file"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('acmst_admission.group_admin'))]"/>
</record>

<record id="acmst_admission_file_rule_coordinator" model="ir.rule">
    <field name="name">Admission File: Coordinator Access</field>
    <field name="model_id" ref="model_acmst_admission_file"/>
    <field name="domain_force">[('coordinator_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('acmst_admission.group_coordinator'))]"/>
</record>
```

### Security Groups

#### Group Hierarchy

```
acmst_admission.group_admin
├── Full access to all models
├── Can create, read, update, delete
└── Can manage system configuration

acmst_admission.group_manager
├── Management-level access
├── Can approve applications
├── Can read, update (limited delete)
└── Cannot manage system configuration

acmst_admission.group_coordinator
├── Academic coordination access
├── Can set conditions
├── Can read, update (no delete)
└── Limited to assigned applications

acmst_admission.group_health
├── Health check management
├── Can manage health checks
├── Can read admission files
└── Cannot modify other data

acmst_admission.group_officer
├── Application processing
├── Can create, read, update
├── Cannot delete
└── Limited to assigned applications

acmst_admission.group_portal
├── Public portal access
├── Can read own applications
├── Cannot modify data
└── Limited to portal operations
```

### Audit Logging

#### Security Events

```python
# Log security events
env['acmst.audit.log'].log_action(
    action_type='access_denied',
    res_model='acmst.admission.file',
    res_id=admission_file.id,
    description='Unauthorized access attempt',
    is_security_violation=True
)

# Log workflow transitions
env['acmst.audit.log'].log_action(
    action_type='workflow',
    res_model='acmst.admission.file',
    res_id=admission_file.id,
    description='State transition from draft to submitted',
    old_value='draft',
    new_value='submitted'
)
```

## Performance Optimization

### Database Optimization

#### Indexes

```sql
-- Primary indexes for performance
CREATE INDEX acmst_admission_file_state_date_idx ON acmst_admission_file(state, create_date);
CREATE INDEX acmst_admission_file_name_id_idx ON acmst_admission_file(applicant_name, national_id);
CREATE INDEX acmst_health_check_file_state_idx ON acmst_health_check(admission_file_id, state);
CREATE INDEX acmst_coordinator_condition_file_state_idx ON acmst_coordinator_condition(admission_file_id, state);
CREATE INDEX acmst_admission_approval_file_type_idx ON acmst_admission_approval(admission_file_id, approval_type);
CREATE INDEX acmst_portal_application_state_date_idx ON acmst_portal_application(state, create_date);
CREATE INDEX acmst_audit_log_model_id_date_idx ON acmst_audit_log(res_model_id, res_id, create_date);
```

#### Query Optimization

```python
# Optimized search queries
def search_admission_files(self, domain):
    """Optimized search with proper indexing"""
    return self.search(domain, order='create_date desc')

# Batch operations
def batch_update_state(self, record_ids, new_state):
    """Batch update for better performance"""
    self.browse(record_ids).write({'state': new_state})

# Lazy loading
def get_related_records(self):
    """Lazy load related records"""
    return self.mapped('health_check_ids')
```

### Caching

#### Response Caching

```python
# Cache frequently accessed data
@api.model
def get_admission_stats(self):
    """Get admission statistics with caching"""
    cache_key = 'admission_stats'
    cached_data = self.env.cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # Calculate statistics
    stats = {
        'total': self.search_count([]),
        'submitted': self.search_count([('state', '=', 'submitted')]),
        'approved': self.search_count([('state', '=', 'completed')])
    }
    
    # Cache for 1 hour
    self.env.cache.set(cache_key, stats, 3600)
    return stats
```

#### Database Caching

```python
# Use database-level caching
@api.model
def get_program_list(self):
    """Get program list with database caching"""
    return self.env['acmst.program'].search([])
```

### View Optimization

#### Lazy Loading

```xml
<!-- Lazy load tree view -->
<tree string="Admission Files" lazy="true">
    <field name="name"/>
    <field name="applicant_name"/>
    <field name="state"/>
</tree>
```

#### Conditional Fields

```xml
<!-- Show fields based on state -->
<field name="health_check_required" invisible="1"/>
<field name="health_check_ids" attrs="{'invisible': [('health_check_required', '=', False)]}"/>
```

## Testing Framework

### Unit Tests

#### Test Structure

```python
class TestAdmissionFile(TransactionCase):
    """Test cases for admission file model"""
    
    def setUp(self):
        super().setUp()
        # Create test data
        
    def test_create_admission_file(self):
        """Test creating admission file"""
        # Test implementation
        
    def test_workflow_transitions(self):
        """Test workflow transitions"""
        # Test implementation
```

#### Test Coverage

- **Model Tests**: All model methods and properties
- **Workflow Tests**: State transitions and validations
- **Security Tests**: Access control and permissions
- **Integration Tests**: Model interactions
- **Performance Tests**: Query performance and optimization
- **API Tests**: Controller endpoints and responses

### Test Data

#### Demo Data

```xml
<!-- Demo data for testing -->
<record id="demo_admission_file_1" model="acmst.admission.file">
    <field name="applicant_name">John Doe</field>
    <field name="national_id">1234567890</field>
    <field name="phone">+966501234567</field>
    <field name="email">john.doe@example.com</field>
    <field name="program_id" ref="demo_program_1"/>
    <field name="batch_id" ref="demo_batch_1"/>
    <field name="birth_date">1990-01-01</field>
    <field name="gender">male</field>
    <field name="nationality">Saudi</field>
    <field name="address">123 Test Street, Riyadh</field>
    <field name="emergency_contact">Jane Doe</field>
    <field name="emergency_phone">+966501234568</field>
</record>
```

### Test Execution

#### Running Tests

```bash
# Run all tests
python odoo-bin -d test_db -i acmst_admission --test-enable

# Run specific test
python odoo-bin -d test_db -i acmst_admission --test-enable --test-tags=acmst_admission

# Run with coverage
coverage run --source=addons/acmst_admission odoo-bin -d test_db -i acmst_admission --test-enable
```

## Deployment Guide

### Prerequisites

- Odoo 17.0 or later
- PostgreSQL 12 or later
- Python 3.8 or later
- Redis (optional, for caching)
- Nginx (optional, for reverse proxy)

### Installation Steps

1. **Download Module**
   ```bash
   git clone https://github.com/acmst-college/acmst-admission.git
   cp -r acmst-admission /opt/odoo/addons/
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Update Module List**
   ```bash
   python odoo-bin -d your_database --update-module-list
   ```

4. **Install Module**
   ```bash
   python odoo-bin -d your_database -i acmst_admission
   ```

5. **Configure Settings**
   - Set up security groups
   - Configure email templates
   - Set up workflow rules
   - Configure portal settings

### Production Configuration

#### Database Configuration

```ini
# odoo.conf
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_password
db_name = acmst_production
```

#### Performance Configuration

```ini
# odoo.conf
[options]
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
```

#### Security Configuration

```ini
# odoo.conf
[options]
admin_passwd = your_admin_password
list_db = False
proxy_mode = True
```

### Monitoring

#### Log Configuration

```ini
# odoo.conf
[options]
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log
```

#### Performance Monitoring

```python
# Monitor performance
performance = env['acmst.performance.optimization']
metrics = performance.get_performance_metrics()
audit_results = performance.run_performance_audit()
```

## Maintenance

### Regular Maintenance

#### Database Maintenance

```sql
-- Analyze tables for query optimization
ANALYZE acmst_admission_file;
ANALYZE acmst_health_check;
ANALYZE acmst_coordinator_condition;

-- Reindex for performance
REINDEX TABLE acmst_admission_file;
REINDEX TABLE acmst_health_check;
REINDEX TABLE acmst_coordinator_condition;
```

#### Log Rotation

```bash
# Rotate logs
logrotate /etc/logrotate.d/odoo
```

#### Backup

```bash
# Database backup
pg_dump -h localhost -U odoo acmst_production > backup_$(date +%Y%m%d).sql

# File backup
tar -czf files_backup_$(date +%Y%m%d).tar.gz /opt/odoo/filestore/
```

### Troubleshooting

#### Common Issues

1. **Permission Errors**
   - Check user group assignments
   - Verify access rights configuration
   - Review record rules

2. **Workflow Errors**
   - Check workflow configuration
   - Verify state transitions
   - Review workflow rules

3. **Performance Issues**
   - Run performance audit
   - Check database indexes
   - Monitor query performance

4. **Portal Issues**
   - Check portal access settings
   - Verify email configuration
   - Review portal templates

#### Debug Mode

```ini
# odoo.conf
[options]
debug = True
log_level = debug
```

#### Log Analysis

```bash
# Check error logs
grep "ERROR" /var/log/odoo/odoo.log

# Check performance logs
grep "PERFORMANCE" /var/log/odoo/odoo.log

# Check security logs
grep "SECURITY" /var/log/odoo/odoo.log
```

### Updates

#### Module Updates

```bash
# Update module
python odoo-bin -d your_database -u acmst_admission

# Update all modules
python odoo-bin -d your_database -u all
```

#### Data Migration

```python
# Migrate data if needed
def migrate_data(self):
    """Migrate data from old version"""
    # Migration logic here
    pass
```

### Support

#### Documentation

- **User Manual**: Complete user guide
- **API Reference**: Technical API documentation
- **Configuration Guide**: Setup and configuration
- **Troubleshooting Guide**: Common issues and solutions

#### Contact Information

- **Technical Support**: support@acmst.edu.sa
- **Documentation**: docs@acmst.edu.sa
- **Issues**: issues@acmst.edu.sa

#### Community

- **GitHub Repository**: https://github.com/acmst-college/acmst-admission
- **Issue Tracker**: https://github.com/acmst-college/acmst-admission/issues
- **Discussions**: https://github.com/acmst-college/acmst-admission/discussions
