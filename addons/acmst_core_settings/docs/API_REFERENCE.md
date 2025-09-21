# ACMST Core Settings - API Reference

This document provides a comprehensive reference for the ACMST Core Settings module APIs, including model methods, workflow actions, and integration points.

## 📋 Core Models API

### University Management (`acmst.university`)

#### Methods
```python
# Create university with validation
@api.model
def create(self, vals)

# Update university with audit logging
def write(self, vals)

# Archive university with cascade check
def toggle_active(self)

# Get related colleges
def get_colleges(self)

# Get statistics
def get_statistics(self)
```

### College Management (`acmst.college`)

#### Key Methods
```python
# Validate college creation
@api.constrains('university_id', 'code')
def _check_unique_code(self)

# Get programs count
def get_programs_count(self)

# Get active programs
def get_active_programs(self)

# Get college statistics
def get_statistics(self)
```

### Program Management (`acmst.program`)

#### Core Methods
```python
# Validate program constraints
@api.constrains('college_id', 'program_type_id')
def _check_program_constraints(self)

# Get batches count
def get_batches_count(self)

# Get active batches
def get_active_batches(self)

# Get enrollment statistics
def get_enrollment_stats(self)
```

### Batch Management (`acmst.batch`)

#### Batch Creation Wizard Integration
```python
# Create batch via wizard
@api.model
def create_from_wizard(self, wizard_data)

# Validate batch capacity
@api.constrains('capacity', 'enrolled_count')
def _check_capacity(self)

# Get enrollment status
def get_enrollment_status(self)

# Calculate duration
def compute_duration(self)
```

## 🔧 Workflow Integration Points

### Academic Rules Engine

#### Rule Application Methods
```python
# Apply academic rules
def apply_academic_rules(self, record, rule_type)

# Validate rule compliance
def validate_rule_compliance(self, record, rules)

# Get applicable rules
def get_applicable_rules(self, record, context)
```

### Security Integration

#### Permission Checking
```python
# Check user permissions
def check_user_permissions(self, user, operation, model)

# Get user access level
def get_user_access_level(self, user, model)

# Validate record access
def validate_record_access(self, user, record)
```

## 📊 Dashboard APIs

### Statistics Collection
```python
# Collect university statistics
def collect_university_stats(self)

# Collect college statistics
def collect_college_stats(self)

# Collect program statistics
def collect_program_stats(self)

# Collect batch statistics
def collect_batch_stats(self)
```

## 🧪 Testing APIs

### Test Data Creation
```python
# Create test university
def create_test_university(self, data=None)

# Create test college
def create_test_college(self, university_id, data=None)

# Create test program
def create_test_program(self, college_id, data=None)

# Create test batch
def create_test_batch(self, program_id, data=None)
```

## 🔒 Security APIs

### Access Control Methods
```python
# Check field access
def check_field_access(self, user, field_name, operation)

# Check record access
def check_record_access(self, user, record, operation)

# Get user permissions
def get_user_permissions(self, user, model)

# Validate permissions
def validate_permissions(self, user, operation, model, record)
```

## 📈 Performance Monitoring

### Performance Tracking
```python
# Track query performance
def track_query_performance(self, query, duration)

# Monitor memory usage
def monitor_memory_usage(self, operation, usage)

# Log performance metrics
def log_performance_metrics(self, operation, metrics)
```

## 🔄 Integration Points

### External System Integration
```python
# Ministry system integration
def integrate_with_ministry(self, data)

# Student information system
def integrate_with_sis(self, data)

# HR system integration
def integrate_with_hr(self, data)

# Finance system integration
def integrate_with_finance(self, data)
```

## 📝 Event Handlers

### Model Event Integration
```python
# Pre-create event
def _pre_create_event(self, vals)

# Post-create event
def _post_create_event(self, record)

# Pre-write event
def _pre_write_event(self, vals)

# Post-write event
def _post_write_event(self, record, vals)
```

## 🗂️ Data Import/Export

### Import/Export Methods
```python
# Export university data
def export_university_data(self, university_ids, format='json')

# Import university data
def import_university_data(self, data, format='json')

# Export college data
def export_college_data(self, college_ids, format='json')

# Import college data
def import_college_data(self, data, format='json')
```

## 📋 Validation Rules

### Business Logic Validation
```python
# Validate university data
def validate_university_data(self, data)

# Validate college data
def validate_college_data(self, data)

# Validate program data
def validate_program_data(self, data)

# Validate batch data
def validate_batch_data(self, data)
```

## 🔍 Search and Filtering

### Advanced Search Methods
```python
# Search universities
def search_universities(self, criteria, limit=None)

# Search colleges
def search_colleges(self, criteria, limit=None)

# Search programs
def search_programs(self, criteria, limit=None)

# Search batches
def search_batches(self, criteria, limit=None)
```

## 📊 Reporting APIs

### Report Generation
```python
# Generate university report
def generate_university_report(self, university_id, report_type)

# Generate college report
def generate_college_report(self, college_id, report_type)

# Generate program report
def generate_program_report(self, program_id, report_type)

# Generate batch report
def generate_batch_report(self, batch_id, report_type)
```

## ⚙️ Configuration APIs

### System Configuration
```python
# Get system configuration
def get_system_config(self, config_key)

# Set system configuration
def set_system_config(self, config_key, config_value)

# Get module configuration
def get_module_config(self, module)

# Set module configuration
def set_module_config(self, module, config)
```

---

**Note**: This API reference is automatically generated and should be updated when the module APIs change. All methods include proper validation, error handling, and logging.
