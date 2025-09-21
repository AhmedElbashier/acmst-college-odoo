# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstPortalApplication(models.Model):
    _name = 'acmst.portal.application'
    _description = 'Portal Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'submission_date desc'

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Application number must be unique!'),
    ]

    # Application Data
    name = fields.Char(
        string=_('Application Number'),
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help=_('Unique application number')
    )
    national_id = fields.Char(
        string=_('National ID / Passport Number'),
        required=True,
        tracking=True,
        help=_('National identification number')
    )
    phone = fields.Char(
        string=_('Phone'),
        required=True,
        tracking=True,
        help=_('Contact phone number')
    )
    email = fields.Char(
        string=_('Email'),
        required=True,
        tracking=True,
        help=_('Email address')
    )
    program_id = fields.Many2one(
        'acmst.program',
        string=_('Program'),
        required=True,
        tracking=True,
        help=_('Target program for admission')
    )
    batch_id = fields.Many2one(
        'acmst.batch',
        string=_('Batch'),
        required=True,
        tracking=True,
        help=_('Target batch for admission')
    )
    state = fields.Selection([
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('under_review', _('Under Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled'))
    ], string=_('State'), default='draft', tracking=True, help=_('Current state of the application'))
    submitted_to_ministry = fields.Boolean(
        string=_('Submitted to Ministry'),
        default=False,
        help=_('Whether this application has been submitted to ministry')
    )
    submission_date = fields.Datetime(
        string=_('Submission Date'),
        help=_('Date when the application was submitted')
    )
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string=_('Admission File'),
        help=_('Created admission file after approval')
    )

    # Personal Information
    birth_date = fields.Date(
        string=_('Birth Date'),
        required=True,
        help=_('Date of birth')
    )
    gender = fields.Selection([
        ('male', _('Male')),
        ('female', _('Female'))
    ], string=_('Gender'), required=True, help=_('Gender'))
    nationality = fields.Selection([
        ('sudanese', _('Sudanese')),
        ('foreign', _('Foreign'))
    ], string=_('Nationality'), required=True, help=_('Nationality'))
    applicant_name_english = fields.Char(
        string=_('Full Name (English)'),
        required=True,
        tracking=True,
        help=_('Full name in English')
    )
    applicant_name_arabic = fields.Char(
        string=_('Full Name (Arabic)'),
        required=True,
        tracking=True,
        help=_('Full name in Arabic')
    )

    applicant_name = fields.Char(
        string=_('Full Name'),
        compute='_compute_applicant_name',
        help=_('Full name (uses English name as primary)')
    )
    religion = fields.Selection([
        ('muslim', _('Muslim')),
        ('christian', _('Christian')),
        ('other', _('Other'))
    ], string=_('Religion'), help=_('Religious affiliation'))
    address = fields.Text(
        string=_('Address'),
        required=True,
        help=_('Full address')
    )
    emergency_contact = fields.Char(
        string=_('Emergency Contact'),
        required=True,
        help=_('Emergency contact person name')
    )
    emergency_phone = fields.Char(
        string=_('Emergency Phone'),
        required=True,
        help=_('Emergency contact phone number')
    )

    # Guardian Information
    guardian_ids = fields.One2many(
        'acmst.guardian',
        'portal_application_id',
        string=_('Guardians'),
        help=_('List of guardians for this application')
    )

    # Identification Information
    id_type = fields.Selection([
        ('national_id', _('National ID')),
        ('passport', _('Passport'))
    ], string=_('ID Type'), required=True, help=_('Type of identification document'))
    national_id = fields.Char(
        string=_('National ID / Passport Number'),
        required=True,
        tracking=True,
        help=_('National ID or passport number')
    )

    # Admission Information
    admission_type = fields.Selection([
        ('direct', _('Direct Admission')),
        ('regular', _('Regular Admission')),
        ('private', _('Private Admission')),
        ('transfer', _('Transfer')),
        ('bridging', _('Bridging')),
        ('degree_holder', _('Degree Holder')),
        ('private_education_grant', _('Private Education Grant'))
    ], string=_('Type of Admission'), required=True, help=_('Type of admission'));

    # Additional Personal Information
    place_of_birth = fields.Char(
        string=_('Place of Birth'),
        help=_('City/Country of birth')
    )

    # Academic Information
    previous_education = fields.Text(
        string=_('Previous Education'),
        help=_('Previous educational background')
    )

    # Detailed Education Information
    education_institution = fields.Char(
        string=_('Education Institution'),
        help=_('Name of previous educational institution')
    )
    education_program = fields.Char(
        string=_('Education Program'),
        help=_('Program/degree obtained')
    )
    education_college = fields.Char(
        string=_('Education College'),
        help=_('College/School attended')
    )
    education_major = fields.Char(
        string=_('Education Major'),
        help=_('Major field of study')
    )
    education_start_year = fields.Integer(
        string=_('Education Start Year'),
        help=_('Year when education started')
    )
    education_completion_year = fields.Integer(
        string=_('Education Completion Year'),
        help=_('Year when education was completed')
    )
    certificate_type = fields.Selection([
        ('diploma', _('Diploma')),
        ('bachelor', _('Bachelor')),
        ('master', _('Master')),
        ('phd', _('PhD')),
        ('certificate', _('Certificate')),
        ('other', _('Other'))
    ], string=_('Certificate Type'), help=_('Type of certificate obtained'))
    education_duration_years = fields.Integer(
        string=_('Education Duration (Years)'),
        help=_('Duration of education in years')
    )

    # Document Attachments - One2many relations for multiple documents
    document_ids = fields.One2many(
        'acmst.document',
        'portal_application_id',
        string=_('Documents'),
        help=_('All documents attached to this application')
    )

    # Specific document categories
    id_document_ids = fields.One2many(
        'acmst.document',
        'portal_application_id',
        domain=[('document_type', '=', 'id_document')],
        string=_('ID Documents'),
        help=_('Identification documents (National ID/Passport)')
    )
    academic_document_ids = fields.One2many(
        'acmst.document',
        'portal_application_id',
        domain=[('document_type', 'in', ['academic_certificate', 'transcript'])],
        string=_('Academic Documents'),
        help=_('Academic certificates and transcripts')
    )
    support_document_ids = fields.One2many(
        'acmst.document',
        'portal_application_id',
        domain=[('document_type', 'in', ['support_document', 'medical_report', 'other'])],
        string=_('Support Documents'),
        help=_('Other supporting documents')
    )

    # Legacy fields for backward compatibility (single file support)
    documents = fields.Binary(
        string=_('Legacy Documents'),
        help=_('Legacy field - use document_ids instead')
    )
    documents_filename = fields.Char(
        string=_('Legacy Documents Filename'),
        help=_('Legacy field - use document_ids instead')
    )

    # ID Document Upload
    id_document = fields.Binary(
        string=_('ID Document'),
        help=_('Upload your National ID or Passport copy'),
        required=False,
        tracking=True
    )
    id_document_filename = fields.Char(
        string=_('ID Document Filename'),
        help=_('Filename of the uploaded ID document')
    )

    # Portal specific fields
    portal_user_id = fields.Many2one(
        'res.users',
        string=_('Portal User'),
        help=_('Portal user who submitted the application')
    )
    ip_address = fields.Char(
        string=_('IP Address'),
        help=_('IP address of the submitter')
    )
    user_agent = fields.Char(
        string=_('User Agent'),
        help=_('Browser user agent')
    )

    # Computed fields
    age = fields.Integer(
        string=_('Age'),
        compute='_compute_age',
        store=True,
        help=_('Age in years')
    )
    program_name = fields.Char(
        string=_('Program Name'),
        related='program_id.name',
        store=True,
        help=_('Program name')
    )
    batch_name = fields.Char(
        string='Batch Name',
        related='batch_id.name',
        store=True,
        help='Batch name'
    )

    # University ID Information
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

    # Student Profile Picture
    profile_picture = fields.Binary(
        string='Profile Picture',
        attachment=True,
        help='Student profile picture'
    )
    profile_picture_filename = fields.Char(
        string='Profile Picture Filename',
        help='Name of the profile picture file'
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

    @api.model
    def create(self, vals):
        """Override create to generate application number and validate required fields"""
        if vals.get('name', _('New')) == _('New'):
            # Generate unique application number
            sequence_code = 'acmst.portal.application'
            while True:
                sequence_number = self.env['ir.sequence'].next_by_code(sequence_code)
                if sequence_number and not self.search([('name', '=', sequence_number)], limit=1):
                    vals['name'] = sequence_number
                    break
                elif not sequence_number:
                    vals['name'] = _('New')
                    break

        # Set portal user if not provided
        if 'portal_user_id' not in vals:
            vals['portal_user_id'] = self.env.user.id

        # Validate required fields for portal applications
        required_fields = ['program_id', 'batch_id', 'applicant_name_english', 'applicant_name_arabic',
                          'phone', 'email', 'birth_date', 'gender', 'nationality', 'id_type',
                          'national_id', 'address', 'emergency_contact', 'emergency_phone',
                          'admission_type', 'place_of_birth', 'religion']

        missing_fields = []
        for field in required_fields:
            if not vals.get(field):
                field_label = self._fields[field].string
                missing_fields.append(field_label)

        if missing_fields:
            raise ValidationError(
                _('The following required fields are missing: %s') % ', '.join(missing_fields)
            )

        return super().create(vals)

    def validate_student_data(self):
        """Validate all student data for re-validation during approval"""
        self.ensure_one()
        errors = []

        # Validate required fields
        if not self.applicant_name_english or len(self.applicant_name_english.strip()) < 2:
            errors.append(_('English name must be at least 2 characters long.'))

        if not self.applicant_name_arabic or len(self.applicant_name_arabic.strip()) < 2:
            errors.append(_('Arabic name must be at least 2 characters long.'))

        if not self.national_id or len(self.national_id.strip()) < 5:
            errors.append(_('National ID / Passport number is required.'))

        if not self.phone or len(self.phone.strip()) < 10:
            errors.append(_('Phone number must be at least 10 characters long.'))

    @api.depends('applicant_name_english')
    def _compute_applicant_name(self):
        """Compute the applicant name (uses English name as primary)"""
        for record in self:
            record.applicant_name = record.applicant_name_english or ''

        if not self.email or '@' not in self.email:
            errors.append(_('Please enter a valid email address.'))

        if not self.birth_date:
            errors.append(_('Birth date is required.'))
        elif self.birth_date > date.today():
            errors.append(_('Birth date cannot be in the future.'))

        if not self.place_of_birth or len(self.place_of_birth.strip()) < 2:
            errors.append(_('Place of birth must be at least 2 characters long.'))

        if not self.religion:
            errors.append(_('Religion is required.'))

        if not self.gender:
            errors.append(_('Gender is required.'))

        if not self.nationality:
            errors.append(_('Nationality selection is required.'))

        if not self.id_type:
            errors.append(_('ID type selection is required.'))

        if not self.admission_type:
            errors.append(_('Admission type selection is required.'))

        if not self.address or len(self.address.strip()) < 10:
            errors.append(_('Address must be at least 10 characters long.'))

        if not self.emergency_contact or len(self.emergency_contact.strip()) < 2:
            errors.append(_('Emergency contact name must be at least 2 characters long.'))

        if not self.emergency_phone or len(self.emergency_phone.strip()) < 10:
            errors.append(_('Emergency phone must be at least 10 characters long.'))

        # Validate guardian information
        if not self.guardian_ids:
            errors.append(_('At least one guardian is required.'))
        else:
            default_guardian_found = False
            for guardian in self.guardian_ids:
                if not guardian.name or len(guardian.name.strip()) < 2:
                    errors.append(_('Guardian name must be at least 2 characters long.'))
                if not guardian.relationship:
                    errors.append(_('Guardian relationship is required.'))
                if not guardian.phone or len(guardian.phone.strip()) < 10:
                    errors.append(_('Guardian phone must be at least 10 characters long.'))
                if guardian.is_default:
                    default_guardian_found = True
            if not default_guardian_found:
                errors.append(_('At least one guardian must be marked as default.'))

        if not self.program_id:
            errors.append(_('Program selection is required.'))

        if not self.batch_id:
            errors.append(_('Batch selection is required.'))

        if errors:
            raise ValidationError('\n'.join(errors))

        return True

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

    def action_submit(self):
        """Submit application for review"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft applications can be submitted.'))
        
        # Validate required fields
        required_fields = [
            'applicant_name_english', 'applicant_name_arabic', 'national_id', 'phone', 'email',
            'program_id', 'batch_id', 'birth_date', 'gender', 'nationality', 'id_type',
            'address', 'emergency_contact', 'emergency_phone', 'admission_type', 'place_of_birth', 'religion'
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                field_label = self._fields[field].string
                raise UserError(_('Please fill in the required field: %s') % field_label)
        
        _logger.info(f"Portal application {self.name} submitted by {self.portal_user_id.name}")
        self.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now()
        })
        _logger.info(f"Portal application {self.name} state changed to 'submitted'")

        # Send notification email
        self._send_submission_notification()

        return True

    def action_review(self):
        """Mark application for review"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted applications can be marked for review.'))

        _logger.info(f"Portal application {self.name} marked for review by {self.env.user.name}")
        self.write({'state': 'under_review'})
        _logger.info(f"Portal application {self.name} state changed to 'under_review'")
        return True

    def action_submit_to_ministry(self):
        """Submit application to ministry for approval"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted applications can be sent to ministry.'))

        # Validate all required fields are set
        required_fields = ['program_id', 'batch_id', 'applicant_name_english', 'applicant_name_arabic',
                          'phone', 'email', 'birth_date', 'gender', 'nationality', 'id_type',
                          'national_id', 'address', 'emergency_contact', 'emergency_phone',
                          'admission_type', 'place_of_birth', 'religion']

        missing_fields = []
        for field in required_fields:
            value = getattr(self, field)
            if not value:
                field_label = self._fields[field].string
                missing_fields.append(field_label)

        if missing_fields:
            raise UserError(
                _('Please complete the following required fields before submitting: %s') %
                ', '.join(missing_fields)
            )

        # Just change state to under review - don't create admission file yet
        _logger.info(f"Portal application {self.name} submitted to ministry by {self.env.user.name}")
        self.write({
            'state': 'under_review',
            'submitted_to_ministry': True
        })
        _logger.info(f"Portal application {self.name} state changed to 'under_review' (submitted to ministry)")

        # Send notification
        self._send_ministry_submission_notification()

        return True

    def action_approve(self):
        """Approve portal application and create admission file"""
        self.ensure_one()
        if self.state not in ['submitted', 'under_review']:
            raise UserError(_('Only submitted or under review applications can be approved.'))

        # Validate all required fields are set
        required_fields = ['program_id', 'batch_id', 'applicant_name_english', 'applicant_name_arabic',
                          'phone', 'email', 'birth_date', 'gender', 'nationality', 'id_type',
                          'national_id', 'address', 'emergency_contact', 'emergency_phone',
                          'admission_type', 'place_of_birth', 'religion']

        missing_fields = []
        for field in required_fields:
            value = getattr(self, field)
            if not value:
                field_label = self._fields[field].string
                missing_fields.append(field_label)

        if missing_fields:
            raise UserError(
                _('Please complete the following required fields before approving: %s') %
                ', '.join(missing_fields)
            )

        # Open ministry approval wizard to handle university ID and create admission file
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ministry Approval'),
            'res_model': 'acmst.ministry.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_portal_application_id': self.id,
                'default_applicant_name_english': self.applicant_name_english,
                'default_applicant_name_arabic': self.applicant_name_arabic,
                'default_national_id': self.national_id,
                'default_phone': self.phone,
                'default_email': self.email,
                'default_program_id': self.program_id.id,
                'default_batch_id': self.batch_id.id,
                'default_birth_date': self.birth_date,
                'default_gender': self.gender,
                'default_nationality': self.nationality,
                'default_address': self.address,
                'default_emergency_contact': self.emergency_contact,
                'default_emergency_phone': self.emergency_phone,
                'default_previous_education': self.previous_education,
                'default_submission_method': 'portal',
                'default_approver_id': self.env.user.id,
            }
        }

    def action_reject(self):
        """Reject application"""
        self.ensure_one()
        if self.state not in ['submitted', 'under_review']:
            raise UserError(_('Only submitted or under review applications can be rejected.'))
        
        self.write({'state': 'rejected'})
        
        # Send rejection notification
        self._send_rejection_notification()
        
        return True

    def action_cancel(self):
        """Cancel application"""
        self.ensure_one()
        if self.state in ['approved', 'cancelled']:
            raise UserError(_('Approved or cancelled applications cannot be cancelled.'))
        
        self.write({'state': 'cancelled'})
        return True

    def action_reset_to_draft(self):
        """Reset application to draft"""
        self.ensure_one()
        if self.state not in ['submitted', 'rejected']:
            raise UserError(_('Only submitted or rejected applications can be reset to draft.'))

        self.write({
            'state': 'draft',
            'submission_date': False
        })
        return True

    def action_reset(self):
        """Reset application to draft (alias for action_reset_to_draft)"""
        return self.action_reset_to_draft()

    def action_reopen(self):
        """Reopen application (alias for action_reset_to_draft)"""
        return self.action_reset_to_draft()

    def _safe_send_mail(self, template_ref, record_id=None, force_send=True):
        """Safely send email with proper error handling"""
        try:
            template = self.env.ref(template_ref, False)
            if template:
                # Check if there's an active mail server before sending
                mail_server = self.env['ir.mail_server'].search([('active', '=', True)], order='sequence', limit=1)
                if mail_server:
                    template.send_mail(record_id or self.id, force_send=force_send)
                    _logger.info(f'Successfully sent email using template {template_ref}')
                    return True
                else:
                    # Create pending email instead of skipping
                    _logger.warning(f'No active mail server configured. Creating pending email for template {template_ref}.')
                    self._create_pending_email(template_ref, record_id or self.id)
                    return False
            else:
                _logger.warning(f'Template {template_ref} not found.')
                return False
        except Exception as e:
            _logger.warning(f'Failed to send email using template {template_ref}: {str(e)}')
            # Create pending email for failed attempts too
            self._create_pending_email(template_ref, record_id or self.id)
            return False

    def _create_pending_email(self, template_ref, record_id):
        """Create a pending email record"""
        try:
            template = self.env.ref(template_ref, False)
            if template:
                # Create pending email record
                self.env['acmst.pending.email'].create({
                    'template_ref': template_ref,
                    'record_id': record_id,
                    'model_name': self._name,
                    'record_name': self.name or str(self.id),
                    'priority': 'medium',
                    'retry_count': 0,
                    'max_retries': 3,
                    'created_by': self.env.user.id,
                })
                _logger.info(f'Created pending email for template {template_ref} on record {record_id}')
        except Exception as e:
            _logger.error(f'Failed to create pending email for template {template_ref}: {str(e)}')

    def _send_submission_notification(self):
        """Send notification email when application is submitted"""
        self.ensure_one()
        return self._safe_send_mail('acmst_admission.email_template_application_submitted')

    def _send_approval_notification(self):
        """Send notification email when application is approved"""
        self.ensure_one()
        return self._safe_send_mail('acmst_admission.email_template_application_approved')

    def _send_rejection_notification(self):
        """Send notification email when application is rejected"""
        self.ensure_one()
        return self._safe_send_mail('acmst_admission.email_template_application_rejected')

    def _send_ministry_submission_notification(self):
        """Send notification email when application is submitted to ministry"""
        self.ensure_one()
        return self._safe_send_mail('acmst_admission.email_template_application_submitted')

    @api.model
    def get_portal_applications(self, user_id=None):
        """Get portal applications for a user"""
        domain = []
        if user_id:
            domain.append(('portal_user_id', '=', user_id))
        
        return self.search(domain)

    def action_create_admission_file(self):
        """Create admission file from portal application"""
        self.ensure_one()
        if self.state not in ['submitted', 'under_review', 'approved']:
            raise UserError(_('Only submitted, under review, or approved applications can create admission files.'))

        # Validate all required fields are set
        required_fields = ['program_id', 'batch_id', 'applicant_name_english', 'applicant_name_arabic',
                          'phone', 'email', 'birth_date', 'gender', 'nationality', 'id_type',
                          'national_id', 'address', 'emergency_contact', 'emergency_phone',
                          'admission_type', 'place_of_birth', 'religion']

        missing_fields = []
        for field in required_fields:
            value = getattr(self, field)
            if not value:
                field_label = self._fields[field].string
                missing_fields.append(field_label)

        if missing_fields:
            raise UserError(
                _('Please complete the following required fields before creating admission file: %s') %
                ', '.join(missing_fields)
            )

        # Create or get admission file
        if not self.admission_file_id:
            # Create new admission file in ministry_pending state
            admission_vals = {
                'applicant_name_english': self.applicant_name_english,
                'applicant_name_arabic': self.applicant_name_arabic,
                'national_id': self.national_id,
                'phone': self.phone,
                'email': self.email,
                'program_id': self.program_id.id,
                'batch_id': self.batch_id.id,
                'birth_date': self.birth_date,
                'gender': self.gender,
                'nationality': self.nationality,
                'address': self.address,
                'emergency_contact': self.emergency_contact,
                'emergency_phone': self.emergency_phone,
                'previous_education': self.previous_education,
                'education_institution': self.education_institution,
                'education_program': self.education_program,
                'education_college': self.education_college,
                'education_major': self.education_major,
                'education_start_year': self.education_start_year,
                'education_completion_year': self.education_completion_year,
                'certificate_type': self.certificate_type,
                'education_duration_years': self.education_duration_years,
                'submission_method': 'portal',
                'state': 'ministry_pending',
                'name': self.name,  # Use the same name as portal application
                'religion': self.religion,
                'id_type': self.id_type,
                'admission_type': self.admission_type,
                'place_of_birth': self.place_of_birth,
                'profile_picture': self.profile_picture,
                'profile_picture_filename': self.profile_picture_filename
            }

            admission_file = self.env['acmst.admission.file'].create(admission_vals)

            # Create guardian records for the admission file
            for guardian in self.guardian_ids:
                self.env['acmst.guardian'].create({
                    'name': guardian.name,
                    'relationship': guardian.relationship,
                    'phone': guardian.phone,
                    'email': guardian.email,
                    'is_default': guardian.is_default,
                    'is_active': guardian.is_active,
                    'admission_file_id': admission_file.id
                })
            self.write({'admission_file_id': admission_file.id})
        else:
            # Update existing admission file with current portal data and set to ministry_pending state
            self.admission_file_id.write({
                'applicant_name_english': self.applicant_name_english,
                'applicant_name_arabic': self.applicant_name_arabic,
                'national_id': self.national_id,
                'phone': self.phone,
                'email': self.email,
                'program_id': self.program_id.id,
                'batch_id': self.batch_id.id,
                'birth_date': self.birth_date,
                'gender': self.gender,
                'nationality': self.nationality,
                'religion': self.religion,
                'address': self.address,
                'emergency_contact': self.emergency_contact,
                'emergency_phone': self.emergency_phone,
                'previous_education': self.previous_education,
                'education_institution': self.education_institution,
                'education_program': self.education_program,
                'education_college': self.education_college,
                'education_major': self.education_major,
                'education_start_year': self.education_start_year,
                'education_completion_year': self.education_completion_year,
                'certificate_type': self.certificate_type,
                'education_duration_years': self.education_duration_years,
                'id_type': self.id_type,
                'admission_type': self.admission_type,
                'place_of_birth': self.place_of_birth,
                'profile_picture': self.profile_picture,
                'profile_picture_filename': self.profile_picture_filename,
                'state': 'ministry_pending'
            })

        # Update portal application state
        self.write({'state': 'admission_created'})

        # Create initial approval record for ministry pending
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file_id.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Admission file created from portal application'
        })

        return True

    @api.model
    def get_application_status(self, application_id):
        """Get application status for portal display"""
        application = self.browse(application_id)
        if not application.exists():
            return None

        status_info = {
            'state': application.state,
            'state_display': dict(application._fields['state'].selection)[application.state],
            'submission_date': application.submission_date,
            'admission_file_id': application.admission_file_id.id if application.admission_file_id else None,
            'file_number': application.admission_file_id.name if application.admission_file_id else None
        }

        return status_info

    def write(self, vals):
        """Override write to log all changes"""
        _logger.info(f"Updating portal application {self.name} with vals: {vals}")

        # Get old values before update
        old_values = {}
        if 'state' in vals:
            old_values['state'] = self.state

        result = super(AcmstPortalApplication, self).write(vals)

        # Log state changes
        if 'state' in vals and old_values.get('state') != self.state:
            _logger.info(f"Portal application {self.name} state changed from {old_values.get('state')} to {self.state}")

            # Create audit log entry for state change
            self.env['acmst.audit.log'].create({
                'model_name': 'acmst.portal.application',
                'record_id': self.id,
                'record_name': self.name,
                'action': 'write',
                'category': 'workflow',
                'old_values': f"State: {old_values.get('state')}",
                'new_values': f"State: {self.state}",
                'user_id': self.env.user.id,
                'action_description': f'State changed from {old_values.get("state")} to {self.state}'
            })

            # Post message to chatter
            self.message_post(
                body=f'Status changed from {old_values.get("state")} to {self.state}',
                message_type='comment'
            )

        return result

    def unlink(self):
        """Override unlink to log deletions"""
        for record in self:
            _logger.warning(f"Deleting portal application {record.name} for applicant {record.applicant_name_english}")

            # Create audit log entry for deletion
            self.env['acmst.audit.log'].create({
                'model_name': 'acmst.portal.application',
                'record_id': record.id,
                'record_name': record.name,
                'action': 'unlink',
                'category': 'data_deletion',
                'old_values': f'Portal application: {record.name} for {record.applicant_name_english}',
                'new_values': '',
                'user_id': self.env.user.id,
                'action_description': f'Portal application deleted: {record.name}'
            })

            # Post message to chatter before deletion
            record.message_post(
                body=f'Portal application {record.name} has been deleted',
                message_type='comment'
            )

        return super(AcmstPortalApplication, self).unlink()
