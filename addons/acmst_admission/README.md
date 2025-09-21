# ACMST Admission Module

## Overview

The ACMST Admission Module is a comprehensive Odoo module designed to manage the complete admission process for ACMST College. It provides a multi-state workflow system with portal integration, health check management, coordinator approval processes, and comprehensive reporting.

## Features

### Core Functionality

- **Multi-State Workflow**: Complete admission process from application to student enrollment
- **Portal Integration**: Public-facing application forms and status tracking
- **Health Check System**: Medical assessment and fitness evaluation
- **Coordinator Approval**: Conditional requirements and academic prerequisites
- **Manager Approval**: Final approval and student record generation
- **Processing Students Management**: Students approved without university ID (من طلاب المعالجات)
- **Audit Logging**: Comprehensive tracking of all system activities
- **Performance Optimization**: Built-in performance monitoring and optimization tools

### Key Models

1. **Admission File** (`acmst.admission.file`)
   - Central model managing the complete admission process
   - Multi-state workflow with automated transitions
   - Integration with all related models

2. **Health Check** (`acmst.health.check`)
   - Medical assessment and fitness evaluation
   - Comprehensive health questionnaire
   - Medical report generation

3. **Coordinator Condition** (`acmst.coordinator.condition`)
   - Academic prerequisites and conditional requirements
   - Deadline management and completion tracking
   - Integration with admission workflow

4. **Admission Approval** (`acmst.admission.approval`)
   - Approval history and decision tracking
   - Multi-level approval process
   - Audit trail for all approvals

5. **Portal Application** (`acmst.portal.application`)
   - Public-facing application submission
   - Application status tracking
   - Integration with admission file creation

6. **Workflow Engine** (`acmst.workflow.engine`)
   - Configurable workflow states and transitions
   - Automated workflow rules and actions
   - Flexible workflow management

7. **Audit Log** (`acmst.audit.log`)
   - Comprehensive activity logging
   - Security violation tracking
   - Performance monitoring

8. **Performance Optimization** (`acmst.performance.optimization`)
   - Performance monitoring and optimization
   - Database index management
   - Caching and query optimization

## Installation

### Prerequisites

- Odoo 17.0 or later
- ACMST Core Settings module
- Required dependencies (see `__manifest__.py`)

### Installation Steps

1. Copy the module to your Odoo addons directory
2. Update the module list in Odoo
3. Install the module from the Apps menu
4. Configure the module settings
5. Set up security groups and access rights
6. Configure email templates and notifications

## Configuration

### Security Groups

The module includes several security groups:

- **Admin**: Full access to all features
- **Manager**: Management-level access with approval rights
- **Coordinator**: Academic coordinator access for conditional requirements
- **Health**: Health check management access
- **Officer**: Admission officer access for processing applications
- **Portal**: Public portal access for applicants

### Workflow Configuration

1. **States**: Configure admission workflow states
2. **Transitions**: Set up automated state transitions
3. **Rules**: Define workflow rules and actions
4. **Notifications**: Configure email notifications for each state

### Portal Configuration

1. **Application Form**: Customize the public application form
2. **File Uploads**: Configure allowed file types and sizes
3. **Validation**: Set up form validation rules
4. **Notifications**: Configure applicant notifications

## Usage

### For Administrators

1. **Dashboard**: Access the main admission dashboard
2. **Applications**: Manage all admission applications
3. **Health Checks**: Oversee medical assessments
4. **Conditions**: Manage coordinator requirements
5. **Approvals**: Process approval workflows
6. **Reports**: Generate comprehensive reports
7. **Performance**: Monitor and optimize system performance

### For Coordinators

1. **Review Applications**: Review submitted applications
2. **Set Conditions**: Create conditional requirements
3. **Monitor Progress**: Track condition completion
4. **Approve Applications**: Approve or reject applications

### For Health Staff

1. **Health Checks**: Conduct medical assessments
2. **Medical Reports**: Generate health reports
3. **Fitness Evaluation**: Evaluate medical fitness
4. **Follow-up**: Schedule follow-up appointments

### For Applicants

1. **Apply Online**: Submit applications through the portal
2. **Track Status**: Monitor application progress
3. **Upload Documents**: Submit required documents
4. **Health Check**: Complete medical assessments
5. **Meet Conditions**: Fulfill coordinator requirements

## Workflow

### Application Process

1. **Application Submission**: Applicant submits application via portal
2. **Initial Review**: Admission officer reviews application
3. **Ministry Approval**: Ministry-level approval process
4. **Health Check**: Medical assessment and fitness evaluation
5. **Coordinator Review**: Academic coordinator evaluation
6. **Conditional Requirements**: Set and fulfill academic prerequisites
7. **Manager Approval**: Final management approval
8. **Student Creation**: Generate student record and enrollment

### State Transitions

- **Draft** → **Submitted**: Application submission
- **Submitted** → **Ministry Approved**: Ministry approval
- **Ministry Approved** → **Health Required**: Health check initiation
- **Health Required** → **Health Approved**: Health check completion
- **Health Approved** → **Coordinator Review**: Coordinator evaluation
- **Coordinator Review** → **Coordinator Conditional**: Conditional requirements
- **Coordinator Conditional** → **Manager Approved**: Manager approval
- **Manager Approved** → **Completed**: Process completion

### Processing Students Workflow

Students approved without university ID are marked as "Processing Students" (من طلاب المعالجات) and:
- Appear in the Processing Students menu with muted styling
- Have `is_processing_student = True` field set
- Can be filtered using the "⏳ Processing Students" filter
- Are tracked with update date and user information

## API Reference

### Models

#### Admission File

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

# Submit application
admission_file.action_submit()

# Approve application
admission_file.action_ministry_approve()
```

#### Health Check

```python
# Create health check
health_check = env['acmst.health.check'].create({
    'admission_file_id': admission_file.id,
    'examiner_id': user.id,
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

# Submit health check
health_check.action_submit()

# Approve health check
health_check.action_approve()
```

#### Coordinator Condition

```python
# Create coordinator condition
condition = env['acmst.coordinator.condition'].create({
    'admission_file_id': admission_file.id,
    'coordinator_id': coordinator.id,
    'subject_name': 'Mathematics',
    'subject_code': 'MATH101',
    'level': 'bachelor',
    'description': 'Complete mathematics prerequisite',
    'deadline': '2024-12-31',
    'notes': 'Must be completed before enrollment'
})

# Complete condition
condition.action_complete()
```

### Controllers

#### Portal Application

```python
# Submit application
@http.route('/admission/submit', type='http', auth='public', methods=['POST'])
def submit_application(self, **kwargs):
    # Process application submission
    pass

# Check application status
@http.route('/admission/status/<int:application_id>', type='http', auth='public')
def check_status(self, application_id, **kwargs):
    # Return application status
    pass
```

## Reporting

### Available Reports

1. **Admission File Report**: Complete admission file details
2. **Health Check Report**: Medical assessment summary
3. **Coordinator Condition Report**: Academic requirements status
4. **Admission Approval Report**: Approval history and decisions
5. **Portal Application Report**: Application submission details
6. **Workflow Engine Report**: Workflow configuration and status
7. **Audit Log Report**: System activity and security logs

### Report Generation

```python
# Generate admission file report
report = env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
report_html = report._render_qweb_html(admission_file.ids)
```

## Security

### Access Control

- **Record Rules**: Model-level access control
- **Field Security**: Field-level access restrictions
- **Group-based Access**: Role-based permissions
- **Audit Logging**: Comprehensive activity tracking

### Security Groups

- **Admin**: Full system access
- **Manager**: Management and approval access
- **Coordinator**: Academic coordination access
- **Health**: Medical assessment access
- **Officer**: Application processing access
- **Portal**: Public portal access

## Performance

### Optimization Features

- **Database Indexes**: Optimized database queries
- **Caching**: Response caching for improved performance
- **Query Optimization**: Efficient database operations
- **View Optimization**: Optimized user interface rendering
- **Report Optimization**: Fast report generation
- **Workflow Optimization**: Efficient workflow processing

### Performance Monitoring

- **Performance Metrics**: Real-time performance monitoring
- **Optimization Tracking**: Track optimization implementations
- **Audit Performance**: Monitor system performance
- **Resource Usage**: Track resource consumption

## Troubleshooting

### Common Issues

1. **Permission Errors**: Check user group assignments
2. **Workflow Errors**: Verify workflow configuration
3. **Portal Issues**: Check portal access settings
4. **Email Notifications**: Verify email template configuration
5. **Performance Issues**: Run performance optimization

### Debug Mode

Enable debug mode for detailed error information:

```python
# In Odoo configuration
debug = True
```

### Logging

Check Odoo logs for detailed error information:

```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo.log
```

## Support

### Documentation

- **User Manual**: Complete user guide
- **API Documentation**: Technical API reference
- **Configuration Guide**: Setup and configuration instructions
- **Troubleshooting Guide**: Common issues and solutions

### Contact

- **Technical Support**: support@acmst.edu.sa
- **Documentation**: docs@acmst.edu.sa
- **Issues**: issues@acmst.edu.sa

## License

This module is licensed under the AGPL-3.0 License. See the LICENSE file for details.

## Changelog

### Version 1.1.0 (Latest)
- **Processing Students Management**: Students approved without university ID are marked as "من طلاب المعالجات"
- **Manager Dashboard Views**: Enabled manager-specific dashboard and menu items
- **Enhanced University ID Tracking**: Improved tracking of university ID updates and processing student status
- **Fixed Workflow Logic**: Corrected ministry approval wizard to properly handle processing students
- **Updated Documentation**: Comprehensive documentation for all features

### Version 1.0.0
- Initial release
- Complete admission workflow
- Portal integration
- Health check system
- Coordinator approval process
- Manager approval workflow
- Audit logging
- Performance optimization
- Comprehensive reporting
- Security implementation
- Testing suite

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Roadmap

### Future Enhancements

- **Mobile App**: Mobile application for applicants
- **Advanced Analytics**: Enhanced reporting and analytics
- **Integration APIs**: Third-party system integration
- **Automated Workflows**: More automated workflow processes
- **Advanced Security**: Enhanced security features
- **Performance Improvements**: Continuous performance optimization
