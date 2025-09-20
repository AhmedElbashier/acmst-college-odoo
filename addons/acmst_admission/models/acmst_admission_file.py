# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstAdmissionFile(models.Model):
    _name = 'acmst.admission.file'
    _description = 'Admission File'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'File number must be unique!'),
    ]

    # Core fields
    name = fields.Char(
        string='File Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique file number for this admission application'
    )
    applicant_name = fields.Char(
        string='Applicant Name',
        required=True,
        tracking=True,
        help='Full name of the applicant'
    )
    national_id = fields.Char(
        string='National ID',
        required=True,
        tracking=True,
        help='National identification number'
    )
    phone = fields.Char(
        string='Phone',
        required=True,
        tracking=True,
        help='Contact phone number'
    )
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True,
        help='Email address'
    )
    program_id = fields.Many2one(
        'acmst.program',
        string='Program',
        required=True,
        tracking=True,
        help='Target program for admission'
    )
    batch_id = fields.Many2one(
        'acmst.batch',
        string='Batch',
        required=True,
        tracking=True,
        help='Target batch for admission'
    )
    academic_level = fields.Selection([
        ('level2', 'Level 2'),
        ('level3', 'Level 3')
    ], string='Academic Level', tracking=True, 
       help='Academic level assigned during conditional approval')
    coordinator_recommended_level = fields.Selection([
        ('level2', 'Level 2'),
        ('level3', 'Level 3')
    ], string='Coordinator Recommended Level', tracking=True, 
       help='Academic level recommended by coordinator during conditional approval')
    state = fields.Selection([
        ('new', 'New Application'),
        ('ministry_pending', 'Ministry Approval Pending'),
        ('ministry_approved', 'Ministry Approved'),
        ('ministry_rejected', 'Ministry Rejected'),
        ('health_required', 'Health Check Required'),
        ('health_approved', 'Health Approved'),
        ('health_rejected', 'Health Rejected'),
        ('coordinator_review', 'Coordinator Review'),
        ('coordinator_approved', 'Coordinator Approved'),
        ('coordinator_rejected', 'Coordinator Rejected'),
        ('coordinator_conditional', 'Coordinator Conditional'),
        ('manager_review', 'Manager Review'),
        ('manager_approved', 'Manager Approved'),
        ('manager_rejected', 'Manager Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='new', tracking=True, help='Current state of the admission file')

    # Dashboard Statistics (computed fields)
    total_applications = fields.Integer(
        string='Total Applications',
        compute='_compute_dashboard_statistics',
        help='Total number of applications'
    )
    pending_review = fields.Integer(
        string='Pending Review',
        compute='_compute_dashboard_statistics',
        help='Number of applications pending review'
    )
    health_required = fields.Integer(
        string='Health Required',
        compute='_compute_dashboard_statistics',
        help='Number of applications requiring health check'
    )
    coordinator_review = fields.Integer(
        string='Coordinator Review',
        compute='_compute_dashboard_statistics',
        help='Number of applications in coordinator review'
    )
    manager_review = fields.Integer(
        string='Manager Review',
        compute='_compute_dashboard_statistics',
        help='Number of applications in manager review'
    )
    ministry_pending_total = fields.Integer(
        string='Ministry Pending (Total)',
        compute='_compute_dashboard_statistics',
        help='Number of applications pending ministry approval'
    )
    completed = fields.Integer(
        string='Completed',
        compute='_compute_dashboard_statistics',
        help='Number of completed applications'
    )
    rejected = fields.Integer(
        string='Rejected',
        compute='_compute_admission_manager_statistics',
        help='Number of rejected applications'
    )

    # Officer Dashboard Statistics (computed fields)
    new_applications_count = fields.Integer(
        string='New Applications',
        compute='_compute_officer_statistics',
        help='Number of new applications'
    )
    ministry_pending_count = fields.Integer(
        string='Ministry Pending',
        compute='_compute_officer_statistics',
        help='Number of applications pending ministry approval'
    )
    ministry_approved_count = fields.Integer(
        string='Ministry Approved',
        compute='_compute_officer_statistics',
        help='Number of ministry approved applications'
    )
    ministry_rejected_count = fields.Integer(
        string='Ministry Rejected',
        compute='_compute_officer_statistics',
        help='Number of ministry rejected applications'
    )

    # Coordinator Dashboard Statistics (computed fields)
    total_reviews = fields.Integer(
        string='Total Reviews',
        compute='_compute_coordinator_statistics',
        help='Total number of coordinator reviews'
    )
    pending_review_count = fields.Integer(
        string='Pending Review',
        compute='_compute_coordinator_statistics',
        help='Number of applications pending coordinator review'
    )
    approved_count = fields.Integer(
        string='Approved',
        compute='_compute_coordinator_statistics',
        help='Number of applications approved by coordinator'
    )
    conditional_count = fields.Integer(
        string='Conditional',
        compute='_compute_coordinator_statistics',
        help='Number of applications with conditional approval'
    )
    my_reviews_count = fields.Integer(
        string='My Reviews',
        compute='_compute_coordinator_statistics',
        help='Number of reviews assigned to current user'
    )
    approved_total = fields.Integer(
        string='Approved (Total)',
        compute='_compute_dashboard_statistics',
        help='Number of approved applications'
    )

    application_date = fields.Datetime(
        string='Application Date',
        default=fields.Datetime.now,
        required=True,
        help='Date when the application was submitted'
    )
    submission_method = fields.Selection([
        ('portal', 'Portal'),
        ('office', 'Office')
    ], string='Submission Method', default='portal', help='How the application was submitted')

    # Personal Information
    birth_date = fields.Date(
        string='Birth Date',
        required=True,
        help='Date of birth'
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', required=True, help='Gender')
    nationality = fields.Char(
        string='Nationality',
        required=True,
        help='Nationality'
    )
    address = fields.Text(
        string='Address',
        required=True,
        help='Full address'
    )
    emergency_contact = fields.Char(
        string='Emergency Contact',
        required=True,
        help='Emergency contact person name'
    )
    emergency_phone = fields.Char(
        string='Emergency Phone',
        required=True,
        help='Emergency contact phone number'
    )

    # Academic Information
    previous_education = fields.Text(
        string='Previous Education',
        help='Previous educational background'
    )
    certificates = fields.Binary(
        string='Certificates',
        help='Attached certificate files'
    )
    certificates_filename = fields.Char(
        string='Certificates Filename',
        help='Name of the certificate file'
    )
    transcripts = fields.Binary(
        string='Transcripts',
        help='Attached transcript files'
    )
    transcripts_filename = fields.Char(
        string='Transcripts Filename',
        help='Name of the transcript file'
    )

    # Process Tracking
    ministry_approval_date = fields.Date(
        string='Ministry Approval Date',
        help='Date when ministry approval was received'
    )
    ministry_approver = fields.Many2one(
        'res.users',
        string='Ministry Approver',
        help='User who approved from ministry'
    )
    
    # University ID and Processing Status
    university_id = fields.Char(
        string='University ID',
        tracking=True,
        help='University ID provided by ministry (FRMNO)'
    )
    is_processing_student = fields.Boolean(
        string='Processing Student',
        default=False,
        tracking=True,
        help='Marked as من طلاب المعالجات - student without university ID'
    )
    university_id_updated_date = fields.Datetime(
        string='University ID Updated Date',
        help='Date when university ID was last updated'
    )
    university_id_updated_by = fields.Many2one(
        'res.users',
        string='Updated By',
        help='User who last updated the university ID'
    )
    health_check_date = fields.Date(
        string='Health Check Date',
        help='Date when health check was completed'
    )
    health_approver = fields.Many2one(
        'res.users',
        string='Health Approver',
        help='User who approved health check'
    )
    coordinator_approval_date = fields.Date(
        string='Coordinator Approval Date',
        help='Date when coordinator approval was received'
    )
    coordinator_id = fields.Many2one(
        'res.users',
        string='Coordinator',
        help='Program coordinator who reviewed the application'
    )
    manager_approval_date = fields.Date(
        string='Manager Approval Date',
        help='Date when manager approval was received'
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Manager',
        help='Admission manager who gave final approval'
    )

    # Related Records
    health_check_ids = fields.One2many(
        'acmst.health.check',
        'admission_file_id',
        string='Health Checks',
        help='Health check records for this admission file'
    )
    coordinator_conditions_ids = fields.One2many(
        'acmst.coordinator.condition',
        'admission_file_id',
        string='Coordinator Conditions',
        help='Conditions set by coordinator'
    )
    coordinator_notes = fields.Text(
        string='Coordinator Notes',
        help='Notes and comments from coordinator review'
    )
    coordinator_conditions = fields.Text(
        string='Coordinator Conditions Summary',
        help='Summary of conditions set by coordinator'
    )
    approval_ids = fields.One2many(
        'acmst.admission.approval',
        'admission_file_id',
        string='Approval History',
        help='History of all approvals for this file'
    )
    student_id = fields.Many2one(
        'res.partner',
        string='Student Record',
        help='Created student record after completion'
    )

    # Computed fields
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True,
        help='Age in years'
    )
    is_health_approved = fields.Boolean(
        string='Health Approved',
        compute='_compute_health_status',
        help='Whether health check is approved'
    )
    has_pending_conditions = fields.Boolean(
        string='Has Pending Conditions',
        compute='_compute_conditions_status',
        help='Whether there are pending coordinator conditions'
    )
    
    # Health Check Computed Fields
    health_fitness_status = fields.Char(
        string='Fitness Status',
        compute='_compute_health_check_data',
        help='Medical fitness status from health check'
    )
    health_follow_up_required = fields.Boolean(
        string='Follow-up Required',
        compute='_compute_health_check_data',
        help='Whether follow-up is required from health check'
    )

    @api.depends('birth_date')
    def _compute_age(self):
        """Compute age from birth date"""
        today = date.today()
        for record in self:
            if record.birth_date:
                age = today.year - record.birth_date.year - (
                    (today.month, today.day) < (record.birth_date.month, record.birth_date.day)
                )
                record.age = age
            else:
                record.age = 0

    @api.depends('health_check_ids.state')
    def _compute_health_status(self):
        """Compute health approval status"""
        for record in self:
            approved_checks = record.health_check_ids.filtered(
                lambda h: h.state == 'approved'
            )
            record.is_health_approved = bool(approved_checks)

    @api.depends('coordinator_conditions_ids.state')
    def _compute_conditions_status(self):
        """Compute pending conditions status"""
        for record in self:
            pending_conditions = record.coordinator_conditions_ids.filtered(
                lambda c: c.state == 'pending'
            )
            record.has_pending_conditions = bool(pending_conditions)
    
    @api.depends('health_check_ids.medical_fitness', 'health_check_ids.follow_up_required')
    def _compute_health_check_data(self):
        """Compute health check data for display"""
        for record in self:
            if record.health_check_ids:
                # Get the latest health check
                latest_health_check = record.health_check_ids[0]
                record.health_fitness_status = latest_health_check.medical_fitness or 'Not Set'
                record.health_follow_up_required = latest_health_check.follow_up_required
            else:
                record.health_fitness_status = 'No Health Check'
                record.health_follow_up_required = False

    @api.model
    def create(self, vals):
        """Override create to generate file number and validate required fields"""
        _logger.info(f"Creating new admission file with vals: {vals}")

        if vals.get('name', _('New')) == _('New'):
            # Generate unique admission file number
            sequence_code = 'acmst.admission.file'
            while True:
                sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
                if sequence_number and not self.search([('name', '=', sequence_number)], limit=1):
                    vals['name'] = sequence_number
                    break
                elif not sequence_number:
                    vals['name'] = _('New')
                    break
            _logger.info(f"Generated admission file number: {vals['name']}")

        # Validate required fields
        required_fields = ['program_id', 'batch_id', 'applicant_name', 'national_id',
                          'phone', 'email', 'birth_date', 'gender', 'nationality',
                          'address', 'emergency_contact', 'emergency_phone']

        missing_fields = []
        for field in required_fields:
            if not vals.get(field):
                field_label = self._fields[field].string
                missing_fields.append(field_label)

        if missing_fields:
            _logger.error(f"Missing required fields for admission file creation: {missing_fields}")
            raise ValidationError(
                _('The following required fields are missing: %s') % ', '.join(missing_fields)
            )

        # Create the admission file
        admission_file = super().create(vals)
        _logger.info(f"Admission file {admission_file.name} created successfully with state: {admission_file.state}")

        # If state is health_required, create health check record
        if vals.get('state') == 'health_required':
            _logger.info(f"Creating health check record for admission file {admission_file.name}")
            admission_file._create_health_check_record()

        return admission_file

    @api.constrains('national_id')
    def _check_national_id(self):
        """Validate national ID format"""
        for record in self:
            if record.national_id:
                # Basic validation for Saudi national ID (10 digits)
                if not record.national_id.isdigit() or len(record.national_id) != 10:
                    raise ValidationError(
                        _('National ID must be exactly 10 digits.')
                    )

    @api.constrains('email')
    def _check_email(self):
        """Validate email format"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(
                    _('Please enter a valid email address.')
                )

    @api.constrains('birth_date')
    def _check_birth_date(self):
        """Validate birth date"""
        for record in self:
            if record.birth_date and record.birth_date > date.today():
                raise ValidationError(
                    _('Birth date cannot be in the future.')
                )

    @api.constrains('university_id')
    def _check_university_id(self):
        """Validate university ID format"""
        for record in self:
            if record.university_id:
                # Basic validation for university ID (alphanumeric, reasonable length)
                if not record.university_id.replace('-', '').replace('_', '').isalnum():
                    raise ValidationError(
                        _('University ID must contain only letters, numbers, hyphens, and underscores.')
                    )
                if len(record.university_id) < 3 or len(record.university_id) > 20:
                    raise ValidationError(
                        _('University ID must be between 3 and 20 characters.')
                    )

    def validate_student_data(self):
        """Validate all student data for re-validation during ministry approval"""
        self.ensure_one()
        errors = []
        
        # Validate required fields
        if not self.applicant_name or len(self.applicant_name.strip()) < 2:
            errors.append(_('Applicant name must be at least 2 characters long.'))
        
        if not self.national_id or len(self.national_id) != 10:
            errors.append(_('National ID must be exactly 10 digits.'))
        
        if not self.phone or len(self.phone.strip()) < 10:
            errors.append(_('Phone number must be at least 10 characters long.'))
        
        if not self.email or '@' not in self.email:
            errors.append(_('Please enter a valid email address.'))
        
        if not self.birth_date:
            errors.append(_('Birth date is required.'))
        elif self.birth_date > date.today():
            errors.append(_('Birth date cannot be in the future.'))
        
        if not self.gender:
            errors.append(_('Gender is required.'))
        
        if not self.nationality or len(self.nationality.strip()) < 2:
            errors.append(_('Nationality must be at least 2 characters long.'))
        
        if not self.address or len(self.address.strip()) < 10:
            errors.append(_('Address must be at least 10 characters long.'))
        
        if not self.emergency_contact or len(self.emergency_contact.strip()) < 2:
            errors.append(_('Emergency contact name must be at least 2 characters long.'))
        
        if not self.emergency_phone or len(self.emergency_phone.strip()) < 10:
            errors.append(_('Emergency phone must be at least 10 characters long. Current value: "%s" (length: %d)') % (self.emergency_phone or '', len(self.emergency_phone.strip()) if self.emergency_phone else 0))
        
        if not self.program_id:
            errors.append(_('Program selection is required.'))
        
        if not self.batch_id:
            errors.append(_('Batch selection is required.'))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True

    def update_university_id(self, university_id, user_id=None):
        """Update university ID and clear processing status"""
        self.ensure_one()
        if not user_id:
            user_id = self.env.user.id
        
        self.write({
            'university_id': university_id,
            'is_processing_student': False,
            'university_id_updated_date': fields.Datetime.now(),
            'university_id_updated_by': user_id
        })
        
        # Create audit log entry
        self.env['acmst.audit.log'].create({
            'model_name': 'acmst.admission.file',
            'record_id': self.id,
            'record_name': self.name,
            'action': 'write',
            'category': 'data_modification',
            'old_values': '',
            'new_values': university_id,
            'action_description': f'University ID updated to: {university_id}'
        })
        
        return True

    def mark_as_processing_student(self, user_id=None):
        """Mark student as processing (من طلاب المعالجات)"""
        self.ensure_one()
        if not user_id:
            user_id = self.env.user.id
        
        self.write({
            'is_processing_student': True,
            'university_id_updated_date': fields.Datetime.now(),
            'university_id_updated_by': user_id
        })
        
        # Create audit log entry
        self.env['acmst.audit.log'].create({
            'model_name': 'acmst.admission.file',
            'record_id': self.id,
            'record_name': self.name,
            'action': 'write',
            'category': 'data_modification',
            'old_values': '',
            'new_values': 'من طلاب المعالجات',
            'action_description': 'Student marked as processing student (من طلاب المعالجات)'
        })
        
        return True

    def action_submit_ministry(self):
        """Submit application for ministry approval"""
        self.ensure_one()
        if self.state != 'new':
            raise UserError(_('Only new applications can be submitted for ministry approval.'))
        
        self.write({
            'state': 'ministry_pending',
            'application_date': fields.Datetime.now()
        })
        
        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Submitted for ministry approval'
        })
        
        return True

    def action_ministry_approve(self):
        """Open ministry approval wizard"""
        self.ensure_one()
        if self.state != 'ministry_pending':
            raise UserError(_('Only ministry pending applications can be approved.'))
        
        # Validate student data before opening wizard
        try:
            self.validate_student_data()
        except ValidationError as e:
            raise UserError(_('Please fix the following data validation errors before approving:\n\n%s') % str(e))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ministry Approval'),
            'res_model': 'acmst.ministry.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admission_file_id': self.id,
                'default_approver_id': self.env.user.id,
            }
        }

    def action_send_to_health_check(self):
        """Send application to health check after ministry approval"""
        self.ensure_one()
        if self.state != 'ministry_approved':
            raise UserError(_('Only ministry approved applications can be sent to health check.'))

        _logger.info(f"Sending admission file {self.name} to health check by {self.env.user.name}")
        self.write({'state': 'health_required'})
        _logger.info(f"Admission file {self.name} state changed to 'health_required'")

        # Create approval record
        _logger.info(f"Creating health approval record for admission file {self.name}")
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'health',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Sent to health check'
        })

        # Create health check record
        _logger.info(f"Creating health check record for admission file {self.name}")
        self._create_health_check_record()

        # Send health check notification
        _logger.info(f"Sending health check notification for admission file {self.name}")
        self.send_health_check_notification()

        return True

    def action_ministry_reject(self):
        """Reject application by ministry"""
        self.ensure_one()
        if self.state != 'ministry_pending':
            raise UserError(_('Only ministry pending applications can be rejected.'))
        
        self.write({
            'state': 'ministry_rejected',
            'ministry_approval_date': fields.Date.today(),
            'ministry_approver': self.env.user.id
        })
        
        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': 'Rejected by ministry'
        })
        
        return True

    def action_require_health_check(self):
        """Require health check for application"""
        self.ensure_one()
        if self.state != 'ministry_approved':
            raise UserError(_('Only ministry approved applications can require health check.'))

        self.write({'state': 'health_required'})

        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'health',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Health check required'
        })

        # Create health check record
        self._create_health_check_record()

        # Send health check notification
        self.send_health_check_notification()

        return True

    def action_health_approve(self):
        """Approve health check"""
        self.ensure_one()
        if self.state != 'health_required':
            raise UserError(_('Only health required applications can be health approved.'))

        _logger.info(f"Health check approved for admission file {self.name} by {self.env.user.name}")
        self.write({
            'state': 'health_approved',
            'health_check_date': fields.Date.today(),
            'health_approver': self.env.user.id
        })
        _logger.info(f"Admission file {self.name} state changed to 'health_approved'")

        # Create approval record
        _logger.info(f"Creating health approval record for admission file {self.name}")
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'health',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Health check approved'
        })

        # Automatically move to coordinator review
        _logger.info(f"Moving admission file {self.name} to coordinator review")
        self.action_coordinator_review()
        
        return True

    def action_health_reject(self):
        """Reject health check"""
        self.ensure_one()
        if self.state != 'health_required':
            raise UserError(_('Only health required applications can be health rejected.'))

        _logger.info(f"Health check rejected for admission file {self.name} by {self.env.user.name}")
        self.write({
            'state': 'health_rejected',
            'health_check_date': fields.Date.today(),
            'health_approver': self.env.user.id
        })
        _logger.info(f"Admission file {self.name} state changed to 'health_rejected'")

        # Create approval record
        _logger.info(f"Creating health rejection record for admission file {self.name}")
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'health',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': 'Health check rejected'
        })

        return True

    def action_coordinator_review(self):
        """Send to coordinator for review"""
        self.ensure_one()
        if self.state != 'health_approved':
            raise UserError(_('Only health approved applications can be sent to coordinator.'))

        _logger.info(f"Sending admission file {self.name} to coordinator review by {self.env.user.name}")
        self.write({'state': 'coordinator_review'})
        _logger.info(f"Admission file {self.name} state changed to 'coordinator_review'")
        return True

    def action_coordinator_approve(self):
        """Approve by coordinator"""
        self.ensure_one()
        if self.state != 'coordinator_review':
            raise UserError(_('Only coordinator review applications can be approved by coordinator.'))
        
        self.write({
            'state': 'coordinator_approved',
            'coordinator_approval_date': fields.Date.today(),
            'coordinator_id': self.env.user.id
        })
        
        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'coordinator',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Approved by coordinator'
        })

        # Execute workflow engine for automatic transitions
        workflow_engine = self.env['acmst.workflow.engine'].search([('active', '=', True)], limit=1)
        if workflow_engine:
            workflow_engine.execute_workflow(self)
        
        return True

    def action_coordinator_reject(self):
        """Reject by coordinator"""
        self.ensure_one()
        if self.state != 'coordinator_review':
            raise UserError(_('Only coordinator review applications can be rejected by coordinator.'))
        
        self.write({
            'state': 'coordinator_rejected',
            'coordinator_approval_date': fields.Date.today(),
            'coordinator_id': self.env.user.id
        })
        
        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'coordinator',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': 'Rejected by coordinator'
        })
        
        return True

    def action_coordinator_conditional(self):
        """Approve with conditions by coordinator - opens wizard"""
        self.ensure_one()
        if self.state != 'coordinator_review':
            raise UserError(_('Only coordinator review applications can be conditionally approved.'))
        
        # Create approval record first
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'coordinator',
            'approval_date': fields.Datetime.now(),
            'decision': 'conditional',
            'comments': 'Approved with conditions by coordinator'
        })
        
        # Open the condition wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Academic Conditions'),
            'res_model': 'acmst.coordinator.condition.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admission_file_id': self.id,
                'default_coordinator_id': self.env.user.id,
                'default_send_notification': True,
            }
        }

    def action_manager_review(self):
        """Send to manager for review"""
        self.ensure_one()
        if self.state not in ['coordinator_approved', 'coordinator_conditional']:
            raise UserError(_('Only coordinator approved or conditional applications can be sent to manager. Current state: %s') % self.state)

        _logger.info(f"Sending application {self.name} to manager review. Current state: {self.state}")
        self.write({'state': 'manager_review'})
        _logger.info(f"Application {self.name} state changed to manager_review")
        return True

    def action_manager_approve(self):
        """Approve by manager"""
        self.ensure_one()
        _logger.info(f"Manager approve called for application {self.name}. Current state: {self.state}")

        # Check if method was called with context (from JavaScript)
        context = self.env.context
        comments = context.get('comments', '')
        send_notification = context.get('send_notification', False)

        if self.state != 'manager_review':
            _logger.error(f"Cannot approve - application {self.name} is not in manager_review state. Current state: {self.state}")
            raise UserError(_('Only manager review applications can be approved by manager. Current state: %s') % self.state)

        _logger.info(f"Approving application {self.name} by manager {self.env.user.name}")

        # Use comments from context if provided
        approval_comments = comments if comments else 'Approved by manager'

        self.write({
            'state': 'manager_approved',
            'manager_approval_date': fields.Date.today(),
            'manager_id': self.env.user.id
        })

        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'manager',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': approval_comments
        })

        # Send notification if requested
        if send_notification:
            try:
                self.send_approval_notification()
            except Exception as e:
                _logger.warning(f"Could not send approval notification: {e}")

        # Automatically complete the process
        self.action_complete()

        return True

    def action_manager_reject(self):
        """Reject by manager"""
        self.ensure_one()

        # Check if method was called with context (from JavaScript)
        context = self.env.context
        comments = context.get('comments', '')
        send_notification = context.get('send_notification', False)

        if self.state != 'manager_review':
            raise UserError(_('Only manager review applications can be rejected by manager.'))

        # Use comments from context if provided
        rejection_comments = comments if comments else 'Rejected by manager'

        self.write({
            'state': 'manager_rejected',
            'manager_approval_date': fields.Date.today(),
            'manager_id': self.env.user.id
        })

        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'manager',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': rejection_comments
        })

        # Send notification if requested
        if send_notification:
            try:
                self.send_rejection_notification()
            except Exception as e:
                _logger.warning(f"Could not send rejection notification: {e}")

        return True

    def action_complete(self):
        """Complete the admission process and create student record"""
        self.ensure_one()
        if self.state != 'manager_approved':
            raise UserError(_('Only manager approved applications can be completed.'))
        
        # Note: Coordinator conditions are now informational only and don't block completion
        
        # Create student record
        student_vals = self._prepare_student_vals()
        student = self.env['res.partner'].create(student_vals)
        
        # Create student academic record (commented out until model is created)
        # academic_vals = self._prepare_academic_vals(student)
        # academic_record = self.env['acmst.student.academic'].create(academic_vals)
        
        self.write({
            'state': 'completed',
            'student_id': student.id
        })
        
        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.id,
            'approver_id': self.env.user.id,
            'approval_type': 'completion',
            'approval_date': fields.Datetime.now(),
            'decision': 'completed',
            'comments': 'Admission process completed, student record created'
        })
        
        # Send final approval notification
        self.send_final_approval_notification()
        
        return True

    def _prepare_student_vals(self):
        """Prepare student record values"""
        return {
            'name': self.applicant_name,
            'is_company': False,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.phone,
            'street': self.address,
            'comment': f'National ID: {self.national_id}\nEmergency Contact: {self.emergency_contact}\nEmergency Phone: {self.emergency_phone}\nAdmission File: {self.name}',
        }

    def _prepare_academic_vals(self, student):
        """Prepare academic record values"""
        return {
            'student_id': student.id,
            'program_id': self.program_id.id,
            'batch_id': self.batch_id.id,
            'admission_file_id': self.id,
            'enrollment_date': fields.Date.today(),
            'academic_year': self.batch_id.academic_year_id.id if self.batch_id.academic_year_id else False,
            'status': 'enrolled',
        }

    def action_generate_student_id(self):
        """Generate student ID for the admission file"""
        self.ensure_one()
        if not self.student_id:
            raise UserError(_('No student record found. Please complete the admission process first.'))
        
        # Generate student ID based on program and batch
        student_id = self._generate_student_id()
        
        self.student_id.write({'student_id': student_id})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Student ID generated: %s') % student_id,
                'type': 'success',
            }
        }

    def _generate_student_id(self):
        """Generate unique student ID"""
        # Format: YYYY-PROGRAM-BATCH-NUMBER
        year = fields.Date.today().year
        program_code = self.program_id.code or 'PROG'
        batch_code = self.batch_id.code or 'BATCH'
        
        # Get next sequence number
        sequence = self.env['ir.sequence'].next_by_code('acmst.student.id') or '0001'
        
        return f"{year}-{program_code}-{batch_code}-{sequence}"

    def action_send_welcome_email(self):
        """Send welcome email to new student"""
        self.ensure_one()
        if not self.student_id:
            raise UserError(_('No student record found.'))
        
        template = self.env.ref('acmst_admission.email_template_welcome_student', False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Welcome email sent to student.'),
                'type': 'success',
            }
        }

    def action_cancel(self):
        """Cancel the admission file"""
        self.ensure_one()
        if self.state in ['completed', 'cancelled']:
            raise UserError(_('Completed or cancelled files cannot be cancelled.'))
        
        self.write({'state': 'cancelled'})
        return True

    def get_portal_url(self):
        """Get portal URL for this admission file"""
        return request.httprequest.host_url.rstrip('/') + '/admission/status/' + str(self.id)

    def send_health_check_notification(self):
        """Send health check required notification"""
        self.ensure_one()
        template = self.env.ref('acmst_admission.email_template_health_check_required', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _create_health_check_record(self):
        """Create health check record for this admission file"""
        self.ensure_one()
        
        # Check if health check already exists
        existing_health_check = self.env['acmst.health.check'].search([
            ('admission_file_id', '=', self.id)
        ], limit=1)
        
        if not existing_health_check:
            # Create new health check record
            health_check_vals = {
                'admission_file_id': self.id,
                'check_date': fields.Datetime.now(),
                'examiner_id': self.env.user.id,
                'state': 'draft'
            }
            self.env['acmst.health.check'].create(health_check_vals)

    def send_conditions_notification(self):
        """Send conditions notification"""
        self.ensure_one()
        template = self.env.ref('acmst_admission.email_template_coordinator_conditions', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def send_final_approval_notification(self):
        """Send final approval notification"""
        self.ensure_one()
        template = self.env.ref('acmst_admission.email_template_final_approval', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def action_create_conditions(self):
        """Open wizard to create conditions"""
        self.ensure_one()
        if self.state not in ['coordinator_review', 'coordinator_conditional']:
            raise UserError(_('Conditions can only be created for applications in coordinator review or conditional state.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Conditions'),
            'res_model': 'acmst.coordinator.condition.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admission_file_id': self.id,
                'default_coordinator_id': self.env.user.id,
            }
        }

    def action_view_health_checks(self):
        """Open health checks related to this admission file"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Health Checks'),
            'res_model': 'acmst.health.check',
            'view_mode': 'tree,form',
            'domain': [('admission_file_id', '=', self.id)],
            'context': {
                'default_admission_file_id': self.id,
            }
        }

    def action_view_conditions(self):
        """Open coordinator conditions related to this admission file"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Coordinator Conditions'),
            'res_model': 'acmst.coordinator.condition',
            'view_mode': 'tree,form',
            'domain': [('admission_file_id', '=', self.id)],
            'context': {
                'default_admission_file_id': self.id,
            }
        }

    def action_view_approvals(self):
        """Open approvals related to this admission file"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approvals'),
            'res_model': 'acmst.admission.approval',
            'view_mode': 'tree,form',
            'domain': [('admission_file_id', '=', self.id)],
            'context': {
                'default_admission_file_id': self.id,
            }
        }

    def action_view_graph(self):
        """Open graph view for admission files"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Admission Files Graph'),
            'res_model': 'acmst.admission.file',
            'view_mode': 'graph',
            'target': 'current',
        }

    def action_view_pivot(self):
        """Open pivot view for admission files"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Admission Files Pivot'),
            'res_model': 'acmst.admission.file',
            'view_mode': 'pivot',
            'target': 'current',
        }

    def action_view_pending_review(self):
        """Open pending coordinator review"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pending Coordinator Review',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'coordinator_review')],
            'target': 'current',
        }

    def action_view_approved(self):
        """Open coordinator approved applications (historical) - only truly approved, not conditional"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Coordinator Approved',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('coordinator_id', '=', self.env.user.id), ('state', 'in', ['coordinator_approved', 'manager_review', 'manager_approved', 'manager_rejected', 'completed'])],
            'target': 'current',
        }

    def action_view_conditional(self):
        """Open conditional approvals (historical) - only conditional approvals"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Conditional Approvals',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('coordinator_id', '=', self.env.user.id), ('state', 'in', ['coordinator_conditional', 'manager_review', 'manager_approved', 'manager_rejected', 'completed'])],
            'target': 'current',
        }

    def action_view_my_reviews(self):
        """Open my reviews"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Reviews',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('coordinator_id', '=', self.env.user.id), ('state', 'in', ['coordinator_review', 'coordinator_approved', 'coordinator_rejected', 'coordinator_conditional'])],
            'target': 'current',
        }

    def action_view_health_approved(self):
        """Open health approved applications (historical)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Health Approved',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('health_approver', '=', self.env.user.id), ('state', 'in', ['health_approved', 'coordinator_review', 'coordinator_approved', 'coordinator_rejected', 'coordinator_conditional', 'manager_review', 'manager_approved', 'manager_rejected', 'completed'])],
            'target': 'current',
        }

    def action_view_health_rejected(self):
        """Open health rejected applications (historical)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Health Rejected',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('health_approver', '=', self.env.user.id), ('state', 'in', ['health_rejected'])],
            'target': 'current',
        }

    def action_view_health_pending(self):
        """Open pending health check applications"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pending Health Checks',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'health_required')],
            'target': 'current',
        }

    def action_view_health_my_reviews(self):
        """Open my health reviews (historical)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Health Reviews',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('health_approver', '=', self.env.user.id)],
            'target': 'current',
        }

    def action_view_coordinator_rejected(self):
        """Open coordinator rejected applications (historical)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Coordinator Rejected',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('coordinator_id', '=', self.env.user.id), ('state', 'in', ['coordinator_rejected'])],
            'target': 'current',
        }

    def action_view_manager_rejected(self):
        """Open manager rejected applications (historical)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manager Rejected',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('manager_id', '=', self.env.user.id), ('state', 'in', ['manager_rejected'])],
            'target': 'current',
        }

    # Officer Dashboard Methods
    def action_view_new_applications(self):
        """Open new applications for officer"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Applications',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'new')],
            'target': 'current',
        }

    def action_view_ministry_pending(self):
        """Open ministry pending applications for officer"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ministry Pending',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'ministry_pending')],
            'target': 'current',
        }

    def action_view_ministry_approved(self):
        """Open ministry approved applications for officer"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ministry Approved',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'ministry_approved')],
            'target': 'current',
        }

    def action_view_ministry_rejected(self):
        """Open ministry rejected applications for officer"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ministry Rejected',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'ministry_rejected')],
            'target': 'current',
        }

    # Admission Manager Dashboard Methods
    def action_view_all_applications(self):
        """Open all applications for admission manager"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'All Applications',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [],
            'target': 'current',
        }

    def action_view_rejected(self):
        """Open rejected applications for admission manager"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rejected Applications',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', 'in', ['ministry_rejected', 'health_rejected', 'coordinator_rejected', 'manager_rejected'])],
            'target': 'current',
        }

    def action_view_completed(self):
        """Open completed applications for admission manager"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Completed Applications',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'completed')],
            'target': 'current',
        }

    def action_view_processing_students(self):
        """Open processing students list (من طلاب المعالجات)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Processing Students (من طلاب المعالجات)',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('is_processing_student', '=', True)],
            'target': 'current',
        }

    def action_update_university_id(self):
        """Open university ID update wizard for processing students"""
        self.ensure_one()
        if not self.is_processing_student:
            raise UserError(_('This action is only available for processing students.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update University ID'),
            'res_model': 'acmst.university.id.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admission_file_id': self.id,
                'default_current_university_id': self.university_id or '',
            }
        }

    def _compute_dashboard_statistics(self):
        """Compute dashboard statistics"""
        # Get global statistics once
        total_applications = self.env['acmst.admission.file'].search_count([])
        pending_review = self.env['acmst.admission.file'].search_count([('state', '=', 'ministry_pending')])
        health_required = self.env['acmst.admission.file'].search_count([('state', '=', 'health_required')])
        coordinator_review = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_review')])
        manager_review = self.env['acmst.admission.file'].search_count([('state', '=', 'manager_review')])
        ministry_pending = self.env['acmst.admission.file'].search_count([('state', '=', 'ministry_pending')])
        completed = self.env['acmst.admission.file'].search_count([('state', '=', 'completed')])
        
        # Apply to all records
        for record in self:
            record.total_applications = total_applications
            record.pending_review = pending_review
            record.health_required = health_required
            record.coordinator_review = coordinator_review
            record.manager_review = manager_review
            record.ministry_pending_total = ministry_pending
            record.completed = completed

    def _compute_coordinator_statistics(self):
        """Compute coordinator dashboard statistics"""
        # Get global statistics once
        pending_review_count = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_review')])
        total_reviews = self.env['acmst.admission.file'].search_count([('coordinator_id', '=', self.env.user.id)])
        approved_count = self.env['acmst.admission.file'].search_count([('coordinator_id', '=', self.env.user.id), ('state', 'in', ['coordinator_approved', 'manager_review', 'manager_approved', 'manager_rejected', 'completed'])])
        conditional_count = self.env['acmst.admission.file'].search_count([('coordinator_id', '=', self.env.user.id), ('state', 'in', ['coordinator_conditional', 'manager_review', 'manager_approved', 'manager_rejected', 'completed'])])
        my_reviews_count = self.env['acmst.admission.file'].search_count([('coordinator_id', '=', self.env.user.id)])
        approved_total = self.env['acmst.admission.file'].search_count([('state', '=', 'manager_approved')])

        # Apply to all records
        for record in self:
            record.pending_review_count = pending_review_count
            record.total_reviews = total_reviews
            record.approved_count = approved_count
            record.conditional_count = conditional_count
            record.my_reviews_count = my_reviews_count
            record.approved_total = approved_total

    # Coordinator Dashboard Additional Statistics
    coordinator_review_rate = fields.Float(
        string='Review Rate',
        compute='_compute_coordinator_performance_stats',
        help='Coordinator review completion rate percentage'
    )
    active_conditions_count = fields.Integer(
        string='Active Conditions',
        compute='_compute_coordinator_performance_stats',
        help='Number of active conditions assigned to coordinator'
    )
    overdue_conditions_count = fields.Integer(
        string='Overdue Conditions',
        compute='_compute_coordinator_performance_stats',
        help='Number of overdue conditions assigned to coordinator'
    )

    def _compute_coordinator_performance_stats(self):
        """Compute coordinator performance statistics"""
        for record in self:
            # Review rate calculation
            total_my_reviews = record.my_reviews_count
            completed_reviews = record.approved_count + record.conditional_count
            if total_my_reviews > 0:
                record.coordinator_review_rate = (completed_reviews / total_my_reviews) * 100
            else:
                record.coordinator_review_rate = 0.0
            
            # Conditions statistics
            record.active_conditions_count = self.env['acmst.coordinator.condition'].search_count([
                ('coordinator_id', '=', self.env.user.id),
                ('state', 'in', ['pending', 'in_progress'])
            ])
            record.overdue_conditions_count = self.env['acmst.coordinator.condition'].search_count([
                ('coordinator_id', '=', self.env.user.id),
                ('state', '=', 'overdue')
            ])

    def _compute_officer_statistics(self):
        """Compute officer dashboard statistics"""
        for record in self:
            record.new_applications_count = self.search_count([('state', '=', 'new')])
            record.ministry_pending_count = self.search_count([('state', '=', 'ministry_pending')])
            record.ministry_approved_count = self.search_count([('state', '=', 'ministry_approved')])
            record.ministry_rejected_count = self.search_count([('state', '=', 'ministry_rejected')])

    # Officer Dashboard Additional Statistics
    officer_processing_rate = fields.Float(
        string='Processing Rate',
        compute='_compute_officer_processing_stats',
        help='Officer processing rate percentage'
    )
    today_applications_count = fields.Integer(
        string="Today's Applications",
        compute='_compute_officer_processing_stats',
        help='Number of applications received today'
    )
    week_applications_count = fields.Integer(
        string='This Week Applications',
        compute='_compute_officer_processing_stats',
        help='Number of applications received this week'
    )

    def _compute_officer_processing_stats(self):
        """Compute officer processing statistics"""
        for record in self:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            # Today's applications
            record.today_applications_count = self.env['acmst.admission.file'].search_count([
                ('create_date', '>=', today.strftime('%Y-%m-%d 00:00:00')),
                ('create_date', '<=', today.strftime('%Y-%m-%d 23:59:59'))
            ])
            
            # This week's applications
            record.week_applications_count = self.env['acmst.admission.file'].search_count([
                ('create_date', '>=', week_ago.strftime('%Y-%m-%d 00:00:00'))
            ])
            
            # Processing rate (approved + rejected / total)
            total_processed = record.ministry_approved_count + record.ministry_rejected_count
            if record.total_applications > 0:
                record.officer_processing_rate = (total_processed / record.total_applications) * 100
            else:
                record.officer_processing_rate = 0.0

    def _compute_admission_manager_statistics(self):
        """Compute admission manager dashboard statistics"""
        for record in self:
            record.rejected = self.search_count([('state', 'in', ['ministry_rejected', 'health_rejected', 'coordinator_rejected', 'manager_rejected'])])

    # Manager Dashboard Additional Statistics
    manager_pending_count = fields.Integer(
        string='Manager Pending',
        compute='_compute_manager_statistics',
        help='Number of applications pending manager review'
    )
    manager_approvals_count = fields.Integer(
        string='My Approvals',
        compute='_compute_manager_statistics',
        help='Number of applications approved by current manager'
    )
    manager_approval_rate = fields.Float(
        string='Approval Rate',
        compute='_compute_manager_statistics',
        help='Manager approval rate percentage'
    )
    processing_students_count = fields.Integer(
        string='Processing Students',
        compute='_compute_manager_statistics',
        help='Number of processing students (من طلاب المعالجات)'
    )
    student_records_count = fields.Integer(
        string='Student Records',
        compute='_compute_manager_statistics',
        help='Number of created student records'
    )

    def _compute_manager_statistics(self):
        """Compute manager dashboard statistics"""
        for record in self:
            # Manager pending reviews
            record.manager_pending_count = self.env['acmst.admission.file'].search_count([('state', '=', 'manager_review')])
            
            # Manager approvals
            record.manager_approvals_count = self.env['acmst.admission.file'].search_count([
                ('manager_id', '=', self.env.user.id),
                ('state', 'in', ['manager_approved', 'completed'])
            ])
            
            # Approval rate calculation
            total_manager_reviews = self.env['acmst.admission.file'].search_count([('manager_id', '=', self.env.user.id)])
            if total_manager_reviews > 0:
                record.manager_approval_rate = (record.manager_approvals_count / total_manager_reviews) * 100
            else:
                record.manager_approval_rate = 0.0
            
            # Processing students
            record.processing_students_count = self.env['acmst.admission.file'].search_count([('is_processing_student', '=', True)])
            
            # Student records
            record.student_records_count = self.env['res.partner'].search_count([
                ('is_company', '=', False),
                ('comment', 'ilike', 'Admission File:')
            ])

    # Reports Dashboard Statistics (computed fields)
    program_count = fields.Integer(
        string='Programs',
        compute='_compute_reports_statistics',
        help='Number of active programs'
    )
    batch_count = fields.Integer(
        string='Batches',
        compute='_compute_reports_statistics',
        help='Number of active batches'
    )
    health_checks_count = fields.Integer(
        string='Health Checks',
        compute='_compute_reports_statistics',
        help='Total number of health checks'
    )
    health_approved_count = fields.Integer(
        string='Health Approved',
        compute='_compute_reports_statistics',
        help='Number of approved health checks'
    )
    health_pending_count = fields.Integer(
        string='Health Pending',
        compute='_compute_reports_statistics',
        help='Number of pending health checks'
    )
    health_rejected_count = fields.Integer(
        string='Health Rejected',
        compute='_compute_reports_statistics',
        help='Number of rejected health checks'
    )
    conditions_count = fields.Integer(
        string='Conditions',
        compute='_compute_reports_statistics',
        help='Total number of coordinator conditions'
    )
    conditions_completed_count = fields.Integer(
        string='Conditions Completed',
        compute='_compute_reports_statistics',
        help='Number of completed conditions'
    )
    conditions_pending_count = fields.Integer(
        string='Conditions Pending',
        compute='_compute_reports_statistics',
        help='Number of pending conditions'
    )
    conditions_overdue_count = fields.Integer(
        string='Conditions Overdue',
        compute='_compute_reports_statistics',
        help='Number of overdue conditions'
    )
    level2_count = fields.Integer(
        string='Level 2 Applications',
        compute='_compute_reports_statistics',
        help='Number of Level 2 applications'
    )
    level3_count = fields.Integer(
        string='Level 3 Applications',
        compute='_compute_reports_statistics',
        help='Number of Level 3 applications'
    )

    def _compute_reports_statistics(self):
        """Compute reports dashboard statistics"""
        for record in self:
            # Program and batch counts
            record.program_count = self.env['acmst.program'].search_count([])
            record.batch_count = self.env['acmst.batch'].search_count([])
            
            # Health check statistics
            record.health_checks_count = self.env['acmst.health.check'].search_count([])
            record.health_approved_count = self.env['acmst.health.check'].search_count([('state', '=', 'approved')])
            record.health_pending_count = self.env['acmst.health.check'].search_count([('state', '=', 'draft')])
            record.health_rejected_count = self.env['acmst.health.check'].search_count([('state', '=', 'rejected')])
            
            # Coordinator conditions statistics
            record.conditions_count = self.env['acmst.coordinator.condition'].search_count([])
            record.conditions_completed_count = self.env['acmst.coordinator.condition'].search_count([('state', '=', 'completed')])
            record.conditions_pending_count = self.env['acmst.coordinator.condition'].search_count([('state', '=', 'pending')])
            record.conditions_overdue_count = self.env['acmst.coordinator.condition'].search_count([('state', '=', 'overdue')])
            
            # Academic level statistics
            record.level2_count = self.search_count([('academic_level', '=', 'level2')])
            record.level3_count = self.search_count([('academic_level', '=', 'level3')])

    # Reports Dashboard Action Methods
    def action_view_application_statistics(self):
        """Open application statistics"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Application Statistics',
            'res_model': 'acmst.admission.file',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['state', 'create_date:month']},
            'target': 'current',
        }

    def action_view_program_statistics(self):
        """Open program statistics"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Program Statistics',
            'res_model': 'acmst.admission.file',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['program_id', 'state']},
            'target': 'current',
        }

    def action_view_health_statistics(self):
        """Open health check statistics"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Health Check Statistics',
            'res_model': 'acmst.health.check',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['state', 'medical_fitness', 'examiner_id']},
            'target': 'current',
        }

    def action_view_conditions_statistics(self):
        """Open conditions statistics"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Conditions Statistics',
            'res_model': 'acmst.coordinator.condition',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['state', 'level', 'coordinator_id']},
            'target': 'current',
        }

    def action_view_reports_dashboard(self):
        """Open reports dashboard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports & Analytics Dashboard',
            'res_model': 'acmst.admission.file',
            'view_mode': 'dashboard,graph,pivot,tree',
            'context': {'group_by': ['state', 'create_date:month', 'program_id']},
            'target': 'current',
        }
