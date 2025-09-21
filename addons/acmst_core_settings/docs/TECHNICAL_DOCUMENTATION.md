# ACMST Core Settings - Technical Documentation

This document provides comprehensive technical documentation for the ACMST Core Settings module, including architecture, data models, business logic, and implementation details.

## 🏗️ Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Odoo Core     │    │  ACMST Core     │    │  Admission      │
│   Framework     │◄──►│   Settings      │◄──►│  Management     │
│                 │    │   Module        │    │  Module         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Models &      │    │   Workflow      │
│   Database      │    │   Business      │    │   Engine        │
└─────────────────┘    │   Logic         │    └─────────────────┘
                       └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   Views &       │
                       │   Wizards       │
                       └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   Security &    │  
                       │   Access        │
                       │   Control       │
                       └─────────────────┘
```

### Module Structure
```
acmst_core_settings/
├── models/              # Business logic and data models
│   ├── acmst_university.py      # University management
│   ├── acmst_college.py         # College/department management
│   ├── acmst_program_type.py    # Program type definitions
│   ├── acmst_program.py         # Academic program management
│   ├── acmst_batch.py           # Student batch management
│   ├── acmst_academic_year.py   # Academic year configuration
│   └── acmst_academic_rules.py  # Academic rules engine
├── views/               # User interface definitions
├── wizards/             # Interactive wizard interfaces
├── security/            # Security groups and access rules
├── data/                # Initial data and sequences
├── static/              # CSS, JavaScript, and assets
└── tests/               # Comprehensive test suite
```

## 📊 Data Models

### University Model (`acmst.university`)

#### Core Fields
```python
class AcmstUniversity(models.Model):
    _name = 'acmst.university'
    _description = 'ACMST University'

    name = fields.Char(string='University Name', required=True)
    code = fields.Char(string='University Code', required=True, unique=True)
    is_main = fields.Boolean(string='Main University', default=False)
    active = fields.Boolean(default=True)

    # Contact Information
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')

    # Statistics (computed fields)
    colleges_count = fields.Integer(compute='_compute_colleges_count')
    programs_count = fields.Integer(compute='_compute_programs_count')
    batches_count = fields.Integer(compute='_compute_batches_count')
```

#### Key Methods
```python
# Computed field methods
@api.depends('college_ids')
def _compute_colleges_count(self)

@api.depends('college_ids.program_ids')
def _compute_programs_count(self)

# Business logic methods
@api.constrains('code')
def _check_unique_code(self)

def get_statistics(self)
def get_active_colleges(self)
```

### College Model (`acmst.college`)

#### Core Fields
```python
class AcmstCollege(models.Model):
    _name = 'acmst.college'
    _description = 'ACMST College'

    name = fields.Char(string='College Name', required=True)
    code = fields.Char(string='College Code', required=True)
    university_id = fields.Many2one('acmst.university', required=True)
    dean_id = fields.Many2one('res.users', string='Dean')

    # Statistics
    programs_count = fields.Integer(compute='_compute_programs_count')
    batches_count = fields.Integer(compute='_compute_batches_count')
```

#### Constraints and Methods
```python
# Unique constraint across university
@api.constrains('university_id', 'code')
def _check_unique_code_per_university(self)

# Computed statistics
@api.depends('program_ids')
def _compute_programs_count(self)

# Business methods
def get_active_programs(self)
def get_statistics(self)
```

### Program Model (`acmst.program`)

#### Core Fields
```python
class AcmstProgram(models.Model):
    _name = 'acmst.program'
    _description = 'ACMST Program'

    name = fields.Char(string='Program Name', required=True)
    code = fields.Char(string='Program Code', required=True)
    college_id = fields.Many2one('acmst.college', required=True)
    program_type_id = fields.Many2one('acmst.program.type', required=True)

    # Management
    manager_id = fields.Many2one('res.users', string='Program Manager')
    coordinator_id = fields.Many2one('res.users', string='Coordinator')

    # Academic details
    duration_years = fields.Integer(string='Duration (Years)')
    total_credits = fields.Integer(string='Total Credits')
    description = fields.Text(string='Description')
```

### Batch Model (`acmst.batch`)

#### Core Fields
```python
class AcmstBatch(models.Model):
    _name = 'acmst.batch'
    _description = 'ACMST Batch'

    name = fields.Char(string='Batch Name', required=True)
    code = fields.Char(string='Batch Code', required=True, unique=True)
    program_id = fields.Many2one('acmst.program', required=True)
    academic_year_id = fields.Many2one('acmst.academic.year', required=True)

    # Batch details
    capacity = fields.Integer(string='Student Capacity', required=True)
    enrolled_count = fields.Integer(compute='_compute_enrolled_count')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    registration_start = fields.Date(string='Registration Start')
    registration_end = fields.Date(string='Registration End')
```

## 🔐 Security Implementation

### Security Groups
```python
# Access Control List
class SecurityGroups:
    ADMIN = 'acmst_core_settings.group_admin'
    MANAGER = 'acmst_core_settings.group_manager'
    COORDINATOR = 'acmst_core_settings.group_coordinator'
    DEAN = 'acmst_core_settings.group_dean'
    VIEWER = 'acmst_core_settings.group_viewer'
```

### Record Rules
```xml
<!-- University access rules -->
<record id="university_admin_rule" model="ir.rule">
    <field name="name">University Admin Access</field>
    <field name="model_id" ref="model_acmst_university"/>
    <field name="groups" eval="[(4, ref('group_admin'))]"/>
    <field name="domain_force">[('active', '=', True)]</field>
    <field name="perm_read">1</field>
    <field name="perm_write">1</field>
    <field name="perm_create">1</field>
    <field name="perm_unlink">1</field>
</record>
```

### Field-Level Security
```python
# Sensitive field access control
class AcmstUniversity(models.Model):
    _name = 'acmst.university'

    # Internal fields with restricted access
    internal_notes = fields.Text(
        groups='acmst_core_settings.group_admin,acmst_core_settings.group_manager'
    )

    confidential_data = fields.Binary(
        groups='acmst_core_settings.group_admin'
    )
```

## 🧠 Business Logic Implementation

### Code Generation System
```python
class CodeGenerator:
    @staticmethod
    def generate_university_code(university_name):
        """Generate unique university code"""
        # Implementation: UNIV + timestamp + hash
        pass

    @staticmethod
    def generate_college_code(college_name, university_code):
        """Generate college code within university"""
        # Implementation: UNIV_COL + sequence
        pass

    @staticmethod
    def generate_program_code(program_name, college_code):
        """Generate program code"""
        # Implementation: COL_PROG + sequence
        pass

    @staticmethod
    def generate_batch_code(program_code, academic_year):
        """Generate batch code"""
        # Implementation: PROG_YEAR_SEMESTER + sequence
        pass
```

### Validation Rules
```python
class ValidationEngine:
    @api.constrains('capacity')
    def _validate_capacity(self):
        """Ensure capacity is positive"""
        if self.capacity <= 0:
            raise ValidationError("Capacity must be greater than 0")

    @api.constrains('start_date', 'end_date')
    def _validate_dates(self):
        """Ensure end date is after start date"""
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")

    @api.constrains('university_id', 'code')
    def _validate_unique_code(self):
        """Ensure unique codes within university"""
        existing = self.search([
            ('university_id', '=', self.university_id.id),
            ('code', '=', self.code),
            ('id', '!=', self.id)
        ])
        if existing:
            raise ValidationError("Code must be unique within university")
```

## 🎨 User Interface Implementation

### Views Structure
```xml
<!-- University form view -->
<record id="acmst_university_form" model="ir.ui.view">
    <field name="name">acmst.university.form</field>
    <field name="model">acmst.university</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="code"/>
                    <field name="is_main"/>
                </group>
                <notebook>
                    <page string="Contact Information">
                        <field name="address"/>
                        <field name="phone"/>
                        <field name="email"/>
                        <field name="website"/>
                    </page>
                    <page string="Statistics">
                        <field name="colleges_count"/>
                        <field name="programs_count"/>
                        <field name="batches_count"/>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

### Wizards Implementation
```python
class AcmstBatchCreationWizard(models.TransientModel):
    _name = 'acmst.batch.creation.wizard'
    _description = 'Batch Creation Wizard'

    program_id = fields.Many2one('acmst.program', required=True)
    academic_year_id = fields.Many2one('acmst.academic.year', required=True)
    batch_count = fields.Integer(string='Number of Batches', default=1)
    capacity_per_batch = fields.Integer(string='Capacity per Batch', default=50)

    def create_batches(self):
        """Create multiple batches based on wizard input"""
        # Implementation details
        pass
```

## 🗄️ Database Design

### Table Structure
```sql
-- Universities table
CREATE TABLE acmst_university (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_main BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id)
);

-- Colleges table
CREATE TABLE acmst_college (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    university_id INTEGER NOT NULL REFERENCES acmst_university(id),
    dean_id INTEGER REFERENCES res_users(id),
    active BOOLEAN DEFAULT TRUE,
    UNIQUE(university_id, code)
);
```

### Indexes and Performance
```sql
-- Performance indexes
CREATE INDEX idx_acmst_university_active ON acmst_university(active);
CREATE INDEX idx_acmst_college_university_active ON acmst_college(university_id, active);
CREATE INDEX idx_acmst_program_college_active ON acmst_program(college_id, active);
CREATE INDEX idx_acmst_batch_program_active ON acmst_batch(program_id, active);

-- Partial indexes for common queries
CREATE INDEX idx_acmst_batch_start_date_active
ON acmst_batch(start_date) WHERE active = TRUE;
```

## 🧪 Testing Framework

### Unit Tests Structure
```python
class TestAcmstUniversity(unittest.TestCase):
    def setUp(self):
        self.university = self.env['acmst.university']

    def test_create_university(self):
        """Test university creation with valid data"""
        vals = {
            'name': 'Test University',
            'code': 'TEST_UNIV_001'
        }
        university = self.university.create(vals)
        self.assertEqual(university.name, 'Test University')

    def test_unique_code_constraint(self):
        """Test unique code constraint"""
        # Test implementation
        pass

    def test_computed_fields(self):
        """Test computed statistics fields"""
        # Test implementation
        pass
```

### Integration Tests
```python
class TestUniversityIntegration(unittest.TestCase):
    def test_university_college_hierarchy(self):
        """Test university to college relationship"""
        # Integration test implementation
        pass

    def test_batch_creation_workflow(self):
        """Test complete batch creation workflow"""
        # Workflow test implementation
        pass
```

## 🔧 Configuration and Customization

### System Parameters
```python
# Module configuration parameters
class SystemConfig:
    MAX_BATCH_CAPACITY = 1000
    DEFAULT_ACADEMIC_YEAR_DURATION = 365
    CODE_GENERATION_PATTERN = 'UNIV_COL_PROG_BATCH'
    AUDIT_LOG_ENABLED = True
    PERFORMANCE_MONITORING = True
```

### Customization Points
```python
# Customizable methods for extension
class AcmstUniversity(models.Model):
    def customize_code_generation(self):
        """Override for custom code generation logic"""
        pass

    def customize_validation_rules(self):
        """Override for custom validation rules"""
        pass

    def customize_statistics_calculation(self):
        """Override for custom statistics"""
        pass
```

## 📈 Performance Optimization

### Query Optimization
```python
# Efficient queries with proper joins
def get_university_with_colleges(self):
    """Optimized query to get university with colleges"""
    query = """
    SELECT u.*, c.*
    FROM acmst_university u
    LEFT JOIN acmst_college c ON u.id = c.university_id
    WHERE u.active = True
    """
    return self.env.cr.execute(query)

# Use of read_group for aggregations
def get_statistics_optimized(self):
    """Optimized statistics calculation"""
    result = self.env['acmst.batch'].read_group(
        domain=[('program_id.college_id.university_id', '=', self.id)],
        fields=['program_id', 'capacity'],
        groupby=['program_id']
    )
    return result
```

### Caching Strategy
```python
# Computed field caching
class AcmstUniversity(models.Model):
    @api.depends_context('force_compute')
    def _compute_colleges_count(self):
        """Cached computation of colleges count"""
        if not self.env.context.get('force_compute'):
            # Use cached value if available
            pass

# Method caching
from functools import lru_cache
class PerformanceOptimized:
    @lru_cache(maxsize=128)
    def get_university_statistics(self, university_id):
        """Cached statistics calculation"""
        pass
```

## 📋 Data Migration

### Migration Scripts
```python
class MigrationScript:
    def migrate_university_data(self):
        """Migrate university data from old structure"""
        # Migration implementation
        pass

    def migrate_college_data(self):
        """Migrate college data"""
        # Migration implementation
        pass

    def migrate_program_data(self):
        """Migrate program data"""
        # Migration implementation
        pass
```

### Version Upgrade
```python
# Version-specific migrations
def migrate_to_version_17_0_1_0_0(self):
    """Migrate to version 17.0.1.0.0"""
    # Add new fields
    # Update constraints
    # Rebuild indexes
    pass
```

## 🔍 Monitoring and Logging

### Audit Logging
```python
class AuditLogger:
    def log_university_creation(self, university, user):
        """Log university creation"""
        self.env['acmst.audit.log'].create({
            'model': 'acmst.university',
            'action': 'create',
            'record_id': university.id,
            'user_id': user.id,
            'old_values': {},
            'new_values': university.read()[0]
        })

    def log_university_update(self, university, old_values, new_values, user):
        """Log university update"""
        self.env['acmst.audit.log'].create({
            'model': 'acmst.university',
            'action': 'write',
            'record_id': university.id,
            'user_id': user.id,
            'old_values': old_values,
            'new_values': new_values
        })
```

### Performance Monitoring
```python
class PerformanceMonitor:
    def monitor_query_performance(self, query, duration):
        """Monitor query performance"""
        if duration > 1.0:  # Log slow queries
            _logger.warning(f"Slow query detected: {duration}s")

    def monitor_memory_usage(self, operation, usage):
        """Monitor memory usage"""
        if usage > 100 * 1024 * 1024:  # 100MB threshold
            _logger.warning(f"High memory usage: {usage} bytes")
```

## 📚 Integration APIs

### External System Integration
```python
class ExternalIntegration:
    def integrate_with_ministry_system(self):
        """Integrate with ministry student information system"""
        # Implementation for ministry integration
        pass

    def integrate_with_sis(self):
        """Integrate with student information system"""
        # Implementation for SIS integration
        pass

    def integrate_with_hr_system(self):
        """Integrate with HR management system"""
        # Implementation for HR integration
        pass
```

### Web Services
```python
class WebServices:
    @http.route('/api/universities', type='json', auth='user')
    def get_universities_api(self):
        """REST API endpoint for universities"""
        universities = self.env['acmst.university'].search([])
        return universities.read()

    @http.route('/api/universities/<int:university_id>', type='json', auth='user')
    def get_university_api(self, university_id):
        """REST API endpoint for single university"""
        university = self.env['acmst.university'].browse(university_id)
        return university.read()[0]
```

---

**Note**: This technical documentation provides comprehensive information for developers, system administrators, and technical stakeholders. For user-focused documentation, please refer to the USER_GUIDE.md.
