# ACMST Admission Module - API Reference

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Models](#models)
4. [Controllers](#controllers)
5. [Workflows](#workflows)
6. [Reports](#reports)
7. [Security](#security)
8. [Performance](#performance)
9. [Error Handling](#error-handling)
10. [Examples](#examples)

## Overview

The ACMST Admission Module provides a comprehensive API for managing the complete admission process. The API is built on top of Odoo's ORM and follows RESTful principles.

### Base URL

```
https://your-domain.com
```

### API Version

```
v1.0.0
```

## Authentication

### Session Authentication

For backend operations, use Odoo's session authentication:

```python
# Login
response = requests.post('https://your-domain.com/web/session/authenticate', {
    'jsonrpc': '2.0',
    'method': 'call',
    'params': {
        'db': 'your_database',
        'login': 'your_username',
        'password': 'your_password'
    }
})

# Use session cookie for subsequent requests
cookies = response.cookies
```

### API Key Authentication

For external integrations, use API key authentication:

```python
headers = {
    'Authorization': 'Bearer your_api_key',
    'Content-Type': 'application/json'
}
```

## Models

### AcmstAdmissionFile

#### Model Information

- **Model Name**: `acmst.admission.file`
- **Table Name**: `acmst_admission_file`
- **Description**: Central model managing the complete admission process

#### Fields

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `name` | Char | No | Record name |
| `applicant_name` | Char | Yes | Full name of the applicant |
| `national_id` | Char | Yes | Unique national identification number |
| `phone` | Char | No | Phone number |
| `email` | Char | No | Email address |
| `program_id` | Many2one | Yes | Reference to academic program |
| `batch_id` | Many2one | Yes | Reference to academic batch |
| `birth_date` | Date | No | Date of birth |
| `gender` | Selection | No | Gender (male, female) |
| `nationality` | Char | No | Nationality |
| `address` | Text | No | Address |
| `emergency_contact` | Char | No | Emergency contact name |
| `emergency_phone` | Char | No | Emergency contact phone |
| `state` | Selection | No | Workflow state |
| `coordinator_id` | Many2one | No | Assigned coordinator |
| `student_id` | Many2one | No | Generated student record |
| `university_id` | Char | No | University ID provided by ministry |
| `is_processing_student` | Boolean | No | Flag for processing students (من طلاب المعالجات) |
| `university_id_updated_date` | Datetime | No | Date when university ID was last updated |
| `university_id_updated_by` | Many2one | No | User who last updated the university ID |
| `notes` | Text | No | Additional notes |

#### Methods

##### `action_submit()`

Submit application for review.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_submit()
```

##### `action_ministry_approve()`

Approve application at ministry level.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_ministry_approve()
```

##### `action_health_required()`

Require health check for the application.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_health_required()
```

##### `action_health_approved()`

Approve health check.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_health_approved()
```

##### `action_coordinator_review()`

Send application for coordinator review.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_coordinator_review()
```

##### `action_manager_approve()`

Approve application at manager level.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_manager_approve()
```

##### `action_complete()`

Complete the admission process.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
admission_file.action_complete()
```

##### `mark_as_processing_student()`

Mark student as processing (من طلاب المعالجات) when no university ID is provided.

**Parameters**:
- `user_id` (Integer): User ID who marked the student as processing

**Returns**: Boolean

**Example**:
```python
admission_file.mark_as_processing_student(user.id)
```

##### `update_university_id()`

Update university ID and clear processing student status.

**Parameters**:
- `university_id` (String): New university ID
- `user_id` (Integer): User ID who updated the ID

**Returns**: Boolean

**Example**:
```python
admission_file.update_university_id('UNIV12345', user.id)
```

##### `get_portal_url()`

Get portal URL for the admission file.

**Parameters**: None

**Returns**: String

**Example**:
```python
url = admission_file.get_portal_url()
```

#### CRUD Operations

##### Create

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
```

##### Read

```python
# Read admission file
admission_file = env['acmst.admission.file'].browse(admission_file_id)
data = admission_file.read(['name', 'applicant_name', 'state'])

# Search admission files
admission_files = env['acmst.admission.file'].search([
    ('state', '=', 'submitted'),
    ('program_id', '=', program.id)
])

# Search count
count = env['acmst.admission.file'].search_count([
    ('state', '=', 'submitted')
])
```

##### Update

```python
# Update admission file
admission_file.write({
    'notes': 'Updated notes',
    'state': 'submitted'
})
```

##### Delete

```python
# Delete admission file
admission_file.unlink()
```

### AcmstHealthCheck

#### Model Information

- **Model Name**: `acmst.health.check`
- **Table Name**: `acmst_health_check`
- **Description**: Medical assessment and fitness evaluation

#### Fields

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `name` | Char | No | Record name |
| `admission_file_id` | Many2one | Yes | Reference to admission file |
| `examiner_id` | Many2one | Yes | Health examiner |
| `height` | Float | No | Height in cm |
| `weight` | Float | No | Weight in kg |
| `bmi` | Float | No | Calculated BMI |
| `blood_type` | Selection | No | Blood type |
| `medical_fitness` | Selection | Yes | Fitness assessment |
| `has_chronic_diseases` | Boolean | No | Has chronic diseases |
| `chronic_diseases_details` | Text | No | Chronic diseases details |
| `takes_medications` | Boolean | No | Takes medications |
| `medications_details` | Text | No | Medications details |
| `has_allergies` | Boolean | No | Has allergies |
| `allergies_details` | Text | No | Allergies details |
| `has_disabilities` | Boolean | No | Has disabilities |
| `disabilities_details` | Text | No | Disabilities details |
| `follow_up_required` | Boolean | No | Follow-up required |
| `follow_up_date` | Date | No | Follow-up date |
| `medical_notes` | Text | No | Medical notes |
| `restrictions` | Text | No | Medical restrictions |
| `state` | Selection | No | Workflow state |

#### Methods

##### `action_submit()`

Submit health check for review.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
health_check.action_submit()
```

##### `action_approve()`

Approve health check.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
health_check.action_approve()
```

##### `action_reject()`

Reject health check.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
health_check.action_reject()
```

##### `get_bmi_category()`

Get BMI category.

**Parameters**: None

**Returns**: String

**Example**:
```python
category = health_check.get_bmi_category()
```

##### `get_health_summary()`

Get comprehensive health summary.

**Parameters**: None

**Returns**: Dictionary

**Example**:
```python
summary = health_check.get_health_summary()
```

### AcmstCoordinatorCondition

#### Model Information

- **Model Name**: `acmst.coordinator.condition`
- **Table Name**: `acmst_coordinator_condition`
- **Description**: Academic prerequisites and conditional requirements

#### Fields

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `name` | Char | No | Record name |
| `admission_file_id` | Many2one | Yes | Reference to admission file |
| `coordinator_id` | Many2one | Yes | Assigned coordinator |
| `subject_name` | Char | Yes | Subject name |
| `subject_code` | Char | No | Subject code |
| `level` | Selection | No | Academic level |
| `description` | Text | No | Condition description |
| `deadline` | Date | No | Completion deadline |
| `completion_date` | Date | No | Completion date |
| `status` | Selection | No | Completion status |
| `state` | Selection | No | Workflow state |
| `notes` | Text | No | Additional notes |

#### Methods

##### `action_complete()`

Mark condition as completed.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
condition.action_complete()
```

##### `action_reject()`

Reject condition.

**Parameters**: None

**Returns**: Boolean

**Example**:
```python
condition.action_reject()
```

##### `get_condition_summary()`

Get condition summary.

**Parameters**: None

**Returns**: Dictionary

**Example**:
```python
summary = condition.get_condition_summary()
```

##### `get_condition_statistics()`

Get condition statistics.

**Parameters**: None

**Returns**: Dictionary

**Example**:
```python
stats = condition.get_condition_statistics()
```

## Controllers

### Portal Application Controller

#### Submit Application

**Endpoint**: `POST /admission/submit`

**Description**: Submit a new admission application

**Parameters**:
- `applicant_name` (string, required): Full name of the applicant
- `national_id` (string, required): National identification number
- `phone` (string, required): Phone number
- `email` (string, required): Email address
- `program_id` (integer, required): Program ID
- `batch_id` (integer, required): Batch ID
- `birth_date` (date, required): Date of birth
- `gender` (string, required): Gender
- `nationality` (string, required): Nationality
- `address` (string, required): Address
- `emergency_contact` (string, required): Emergency contact name
- `emergency_phone` (string, required): Emergency contact phone

**Response**:
```json
{
    "success": true,
    "application_id": 123,
    "message": "Application submitted successfully"
}
```

**Example**:
```python
import requests

data = {
    'applicant_name': 'John Doe',
    'national_id': '1234567890',
    'phone': '+966501234567',
    'email': 'john.doe@example.com',
    'program_id': 1,
    'batch_id': 1,
    'birth_date': '1990-01-01',
    'gender': 'male',
    'nationality': 'Saudi',
    'address': '123 Test Street, Riyadh',
    'emergency_contact': 'Jane Doe',
    'emergency_phone': '+966501234568'
}

response = requests.post('https://your-domain.com/admission/submit', data=data)
result = response.json()
```

#### Check Application Status

**Endpoint**: `GET /admission/status/<int:application_id>`

**Description**: Check the status of an application

**Parameters**:
- `application_id` (integer, required): Application ID

**Response**:
```json
{
    "application_id": 123,
    "status": "submitted",
    "current_state": "Ministry Review",
    "progress": 25,
    "next_steps": ["Health Check", "Coordinator Review", "Manager Approval"]
}
```

**Example**:
```python
import requests

response = requests.get('https://your-domain.com/admission/status/123')
result = response.json()
```

#### Health Check Form

**Endpoint**: `GET /admission/health-check/<int:admission_file_id>`

**Description**: Get health check form for an admission file

**Parameters**:
- `admission_file_id` (integer, required): Admission file ID

**Response**: HTML form

**Example**:
```python
import requests

response = requests.get('https://your-domain.com/admission/health-check/123')
html = response.text
```

#### Submit Health Check

**Endpoint**: `POST /admission/health-check/<int:admission_file_id>`

**Description**: Submit health check for an admission file

**Parameters**:
- `height` (float, required): Height in cm
- `weight` (float, required): Weight in kg
- `blood_type` (string, required): Blood type
- `medical_fitness` (string, required): Medical fitness assessment
- `has_chronic_diseases` (boolean, optional): Has chronic diseases
- `chronic_diseases_details` (string, optional): Chronic diseases details
- `takes_medications` (boolean, optional): Takes medications
- `medications_details` (string, optional): Medications details
- `has_allergies` (boolean, optional): Has allergies
- `allergies_details` (string, optional): Allergies details
- `has_disabilities` (boolean, optional): Has disabilities
- `disabilities_details` (string, optional): Disabilities details
- `follow_up_required` (boolean, optional): Follow-up required
- `follow_up_date` (date, optional): Follow-up date
- `medical_notes` (string, optional): Medical notes
- `restrictions` (string, optional): Medical restrictions

**Response**:
```json
{
    "success": true,
    "health_check_id": 456,
    "message": "Health check submitted successfully"
}
```

**Example**:
```python
import requests

data = {
    'height': 175.0,
    'weight': 70.0,
    'blood_type': 'O+',
    'medical_fitness': 'fit',
    'has_chronic_diseases': False,
    'takes_medications': False,
    'has_allergies': False,
    'has_disabilities': False,
    'follow_up_required': False,
    'medical_notes': 'No issues found',
    'restrictions': 'None'
}

response = requests.post('https://your-domain.com/admission/health-check/123', data=data)
result = response.json()
```

#### Conditions Form

**Endpoint**: `GET /admission/conditions/<int:admission_file_id>`

**Description**: Get conditions form for an admission file

**Parameters**:
- `admission_file_id` (integer, required): Admission file ID

**Response**: HTML form

**Example**:
```python
import requests

response = requests.get('https://your-domain.com/admission/conditions/123')
html = response.text
```

#### Dashboard

**Endpoint**: `GET /admission/dashboard`

**Description**: Get admission dashboard

**Parameters**: None

**Response**: HTML dashboard

**Example**:
```python
import requests

response = requests.get('https://your-domain.com/admission/dashboard')
html = response.text
```

## Workflows

### Admission Workflow

#### State Machine

```
draft → submitted → ministry_approved → health_required → health_approved → 
coordinator_review → coordinator_conditional → manager_approved → completed
```

#### State Transitions

| From State | To State | Method | Description |
|------------|----------|--------|-------------|
| `draft` | `submitted` | `action_submit()` | Submit application |
| `submitted` | `ministry_approved` | `action_ministry_approve()` | Ministry approval |
| `ministry_approved` | `health_required` | `action_health_required()` | Require health check |
| `health_required` | `health_approved` | `action_health_approved()` | Approve health check |
| `health_approved` | `coordinator_review` | `action_coordinator_review()` | Coordinator review |
| `coordinator_review` | `coordinator_conditional` | Set conditions | Set conditional requirements |
| `coordinator_conditional` | `manager_approved` | `action_manager_approve()` | Manager approval |
| `manager_approved` | `completed` | `action_complete()` | Complete process |

#### Workflow Rules

```python
# Create workflow engine
workflow = env['acmst.workflow.engine'].create({
    'name': 'Admission Workflow',
    'model_id': env['ir.model']._get('acmst.admission.file').id,
    'description': 'Complete admission workflow'
})

# Create workflow states
states = [
    {'name': 'draft', 'is_initial': True, 'description': 'Initial state'},
    {'name': 'submitted', 'description': 'Application submitted'},
    {'name': 'ministry_approved', 'description': 'Ministry approved'},
    {'name': 'health_required', 'description': 'Health check required'},
    {'name': 'health_approved', 'description': 'Health check approved'},
    {'name': 'coordinator_review', 'description': 'Coordinator review'},
    {'name': 'coordinator_conditional', 'description': 'Conditional requirements'},
    {'name': 'manager_approved', 'description': 'Manager approved'},
    {'name': 'completed', 'is_final': True, 'description': 'Process completed'}
]

for state_data in states:
    env['acmst.workflow.state'].create({
        'workflow_id': workflow.id,
        **state_data
    })

# Create workflow rules
rules = [
    {
        'name': 'Auto Submit',
        'trigger_event': 'on_create',
        'action_type': 'update_field',
        'action_value': 'submitted'
    },
    {
        'name': 'Ministry Approval',
        'trigger_event': 'on_button_click',
        'action_type': 'transition_state',
        'transition_to_state_id': state_id
    }
]

for rule_data in rules:
    env['acmst.workflow.rule'].create({
        'workflow_id': workflow.id,
        **rule_data
    })
```

## Reports

### Available Reports

#### Admission File Report

**Report Name**: `acmst_admission.admission_file_report`

**Description**: Complete admission file details

**Parameters**:
- `admission_file_ids` (list): List of admission file IDs

**Example**:
```python
# Generate report
report = env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
report_html = report._render_qweb_html(admission_file_ids)
```

#### Health Check Report

**Report Name**: `acmst_admission.health_check_report`

**Description**: Medical assessment summary

**Parameters**:
- `health_check_ids` (list): List of health check IDs

**Example**:
```python
# Generate report
report = env['ir.actions.report']._get_report_from_name('acmst_admission.health_check_report')
report_html = report._render_qweb_html(health_check_ids)
```

#### Coordinator Condition Report

**Report Name**: `acmst_admission.coordinator_condition_report`

**Description**: Academic requirements status

**Parameters**:
- `condition_ids` (list): List of condition IDs

**Example**:
```python
# Generate report
report = env['ir.actions.report']._get_report_from_name('acmst_admission.coordinator_condition_report')
report_html = report._render_qweb_html(condition_ids)
```

### Report Generation

#### Programmatic Report Generation

```python
# Generate report programmatically
def generate_report(self, report_name, record_ids):
    """Generate report for given record IDs"""
    report = self.env['ir.actions.report']._get_report_from_name(report_name)
    if report:
        return report._render_qweb_html(record_ids)
    return None

# Usage
admission_file_ids = [1, 2, 3]
report_html = self.generate_report('acmst_admission.admission_file_report', admission_file_ids)
```

#### Report with Parameters

```python
# Generate report with parameters
def generate_report_with_params(self, report_name, record_ids, params=None):
    """Generate report with additional parameters"""
    report = self.env['ir.actions.report']._get_report_from_name(report_name)
    if report:
        context = self.env.context.copy()
        if params:
            context.update(params)
        return report.with_context(context)._render_qweb_html(record_ids)
    return None

# Usage
params = {'include_notes': True, 'format': 'pdf'}
report_html = self.generate_report_with_params('acmst_admission.admission_file_report', admission_file_ids, params)
```

## Security

### Access Control

#### Model Access Rights

```python
# Check access rights
def check_access_rights(self, model_name, operation):
    """Check if user has access rights for model operation"""
    model = self.env[model_name]
    return model.check_access_rights(operation, raise_exception=False)

# Usage
can_read = self.check_access_rights('acmst.admission.file', 'read')
can_write = self.check_access_rights('acmst.admission.file', 'write')
can_create = self.check_access_rights('acmst.admission.file', 'create')
can_unlink = self.check_access_rights('acmst.admission.file', 'unlink')
```

#### Record Rules

```python
# Check record access
def check_record_access(self, model_name, record_id, operation):
    """Check if user has access to specific record"""
    model = self.env[model_name]
    record = model.browse(record_id)
    return record.check_access_rights(operation, raise_exception=False)

# Usage
can_read_record = self.check_record_access('acmst.admission.file', 123, 'read')
can_write_record = self.check_record_access('acmst.admission.file', 123, 'write')
```

### Security Groups

#### Group Assignment

```python
# Assign user to group
def assign_user_to_group(self, user_id, group_name):
    """Assign user to security group"""
    group = self.env.ref(group_name)
    user = self.env['res.users'].browse(user_id)
    user.write({'groups_id': [(4, group.id)]})

# Usage
self.assign_user_to_group(123, 'acmst_admission.group_manager')
```

#### Group Check

```python
# Check if user belongs to group
def user_has_group(self, user_id, group_name):
    """Check if user belongs to security group"""
    group = self.env.ref(group_name)
    user = self.env['res.users'].browse(user_id)
    return group in user.groups_id

# Usage
is_manager = self.user_has_group(123, 'acmst_admission.group_manager')
```

### Audit Logging

#### Log Actions

```python
# Log user actions
def log_action(self, action_type, res_model, res_id, description, **kwargs):
    """Log user action for audit purposes"""
    return self.env['acmst.audit.log'].log_action(
        action_type=action_type,
        res_model=res_model,
        res_id=res_id,
        description=description,
        **kwargs
    )

# Usage
self.log_action('create', 'acmst.admission.file', 123, 'Admission file created')
self.log_action('write', 'acmst.admission.file', 123, 'Admission file updated', 
                old_value='draft', new_value='submitted')
```

#### Security Violations

```python
# Log security violations
def log_security_violation(self, res_model, res_id, description):
    """Log security violation"""
    return self.log_action('access_denied', res_model, res_id, description, 
                          is_security_violation=True)

# Usage
self.log_security_violation('acmst.admission.file', 123, 'Unauthorized access attempt')
```

## Performance

### Query Optimization

#### Optimized Searches

```python
# Optimized search with proper indexing
def search_admission_files_optimized(self, domain):
    """Search admission files with optimization"""
    return self.env['acmst.admission.file'].search(domain, order='create_date desc')

# Usage
admission_files = self.search_admission_files_optimized([
    ('state', '=', 'submitted'),
    ('program_id', '=', program.id)
])
```

#### Batch Operations

```python
# Batch update for better performance
def batch_update_state(self, record_ids, new_state):
    """Batch update state for multiple records"""
    records = self.env['acmst.admission.file'].browse(record_ids)
    return records.write({'state': new_state})

# Usage
record_ids = [1, 2, 3, 4, 5]
self.batch_update_state(record_ids, 'submitted')
```

### Caching

#### Response Caching

```python
# Cache frequently accessed data
@api.model
def get_admission_stats_cached(self):
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
def get_program_list_cached(self):
    """Get program list with database caching"""
    return self.env['acmst.program'].search([])
```

### Performance Monitoring

#### Performance Metrics

```python
# Get performance metrics
def get_performance_metrics(self):
    """Get performance metrics for optimizations"""
    performance = self.env['acmst.performance.optimization']
    return performance.get_performance_metrics()

# Usage
metrics = self.get_performance_metrics()
```

#### Performance Audit

```python
# Run performance audit
def run_performance_audit(self):
    """Run performance audit for all models"""
    performance = self.env['acmst.performance.optimization']
    return performance.run_performance_audit()

# Usage
audit_results = self.run_performance_audit()
```

## Error Handling

### Exception Types

#### ValidationError

```python
from odoo.exceptions import ValidationError

try:
    admission_file.action_submit()
except ValidationError as e:
    # Handle validation error
    print(f"Validation error: {e}")
```

#### UserError

```python
from odoo.exceptions import UserError

try:
    admission_file.action_complete()
except UserError as e:
    # Handle user error
    print(f"User error: {e}")
```

#### AccessError

```python
from odoo.exceptions import AccessError

try:
    admission_file.write({'state': 'submitted'})
except AccessError as e:
    # Handle access error
    print(f"Access error: {e}")
```

### Error Response Format

#### API Error Response

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed",
        "details": {
            "field": "applicant_name",
            "value": "",
            "constraint": "required"
        }
    }
}
```

#### Python Exception

```python
try:
    # API call
    result = api_call()
except Exception as e:
    # Handle exception
    error_response = {
        'error': {
            'code': type(e).__name__,
            'message': str(e),
            'details': getattr(e, 'details', {})
        }
    }
```

## Examples

### Complete Application Workflow

```python
# Complete application workflow example
def complete_application_workflow(self, application_data):
    """Complete application workflow from start to finish"""
    try:
        # 1. Create admission file
        admission_file = self.env['acmst.admission.file'].create(application_data)
        
        # 2. Submit application
        admission_file.action_submit()
        
        # 3. Ministry approval
        admission_file.action_ministry_approve()
        
        # 4. Health check required
        admission_file.action_health_required()
        
        # 5. Create health check
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': admission_file.id,
            'examiner_id': self.env.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit',
            'blood_type': 'O+',
            'has_chronic_diseases': False,
            'takes_medications': False,
            'has_allergies': False,
            'has_disabilities': False,
            'follow_up_required': False,
            'medical_notes': 'No issues found',
            'restrictions': 'None'
        })
        
        # 6. Submit and approve health check
        health_check.action_submit()
        health_check.action_approve()
        
        # 7. Coordinator review
        admission_file.action_coordinator_review()
        
        # 8. Create coordinator conditions
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': admission_file.id,
            'coordinator_id': self.env.user.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': '2024-12-31',
            'notes': 'Must be completed before enrollment'
        })
        
        # 9. Complete condition
        condition.action_complete()
        
        # 10. Manager approval
        admission_file.action_manager_approve()
        
        # 11. Complete admission
        admission_file.action_complete()
        
        return {
            'success': True,
            'admission_file_id': admission_file.id,
            'student_id': admission_file.student_id.id,
            'message': 'Application completed successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Application workflow failed'
        }
```

### Portal Integration

```python
# Portal integration example
def portal_application_submission(self, form_data):
    """Handle portal application submission"""
    try:
        # Validate form data
        if not self.validate_form_data(form_data):
            return {'success': False, 'message': 'Invalid form data'}
        
        # Create portal application
        application = self.env['acmst.portal.application'].create(form_data)
        
        # Submit application
        application.action_submit()
        
        # Send confirmation email
        self.send_confirmation_email(application)
        
        return {
            'success': True,
            'application_id': application.id,
            'message': 'Application submitted successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Application submission failed'
        }
```

### Report Generation

```python
# Report generation example
def generate_comprehensive_report(self, admission_file_ids):
    """Generate comprehensive report for admission files"""
    try:
        # Get admission files
        admission_files = self.env['acmst.admission.file'].browse(admission_file_ids)
        
        # Generate admission file report
        admission_report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
        admission_html = admission_report._render_qweb_html(admission_file_ids)
        
        # Generate health check reports
        health_check_ids = admission_files.mapped('health_check_ids.id')
        if health_check_ids:
            health_report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.health_check_report')
            health_html = health_report._render_qweb_html(health_check_ids)
        
        # Generate coordinator condition reports
        condition_ids = admission_files.mapped('coordinator_conditions_ids.id')
        if condition_ids:
            condition_report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.coordinator_condition_report')
            condition_html = condition_report._render_qweb_html(condition_ids)
        
        return {
            'success': True,
            'reports': {
                'admission': admission_html,
                'health': health_html if health_check_ids else None,
                'conditions': condition_html if condition_ids else None
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Report generation failed'
        }
```

### Performance Optimization

```python
# Performance optimization example
def optimize_admission_module(self):
    """Run comprehensive optimization for admission module"""
    try:
        # Get performance optimization model
        performance = self.env['acmst.performance.optimization']
        
        # Run comprehensive optimization
        optimizations = performance.optimize_admission_module()
        
        # Get performance metrics
        metrics = performance.get_performance_metrics()
        
        # Run performance audit
        audit_results = performance.run_performance_audit()
        
        return {
            'success': True,
            'optimizations': len(optimizations),
            'metrics': metrics,
            'audit_results': audit_results
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Performance optimization failed'
        }
```
