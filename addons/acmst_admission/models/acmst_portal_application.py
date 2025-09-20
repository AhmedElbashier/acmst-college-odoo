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

    # Application Data
    name = fields.Char(
        string='Application Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique application number'
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
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('admission_created', 'Admission File Created'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', tracking=True, help='Current state of the application')
    submitted_to_ministry = fields.Boolean(
        string='Submitted to Ministry',
        default=False,
        help='Whether this application has been submitted to ministry'
    )
    submission_date = fields.Datetime(
        string='Submission Date',
        help='Date when the application was submitted'
    )
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        help='Created admission file after approval'
    )

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
    documents = fields.Binary(
        string='Documents',
        help='Attached documents'
    )
    documents_filename = fields.Char(
        string='Documents Filename',
        help='Name of the documents file'
    )

    # Portal specific fields
    portal_user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        help='Portal user who submitted the application'
    )
    ip_address = fields.Char(
        string='IP Address',
        help='IP address of the submitter'
    )
    user_agent = fields.Char(
        string='User Agent',
        help='Browser user agent'
    )

    # Computed fields
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True,
        help='Age in years'
    )
    program_name = fields.Char(
        string='Program Name',
        related='program_id.name',
        store=True,
        help='Program name'
    )
    batch_name = fields.Char(
        string='Batch Name',
        related='batch_id.name',
        store=True,
        help='Batch name'
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
        """Override create to generate application number"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'acmst.portal.application'
            ) or _('New')
        
        # Set portal user if not provided
        if 'portal_user_id' not in vals:
            vals['portal_user_id'] = self.env.user.id
        
        return super().create(vals)

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
            'applicant_name', 'national_id', 'phone', 'email',
            'program_id', 'batch_id', 'birth_date', 'gender',
            'nationality', 'address', 'emergency_contact', 'emergency_phone'
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                field_label = self._fields[field].string
                raise UserError(_('Please fill in the required field: %s') % field_label)
        
        self.write({
            'state': 'submitted',
            'submission_date': fields.Datetime.now()
        })
        
        # Send notification email
        self._send_submission_notification()
        
        return True

    def action_review(self):
        """Mark application for review"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted applications can be marked for review.'))

        self.write({'state': 'under_review'})
        return True

    def action_submit_to_ministry(self):
        """Submit application to ministry for approval"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted applications can be sent to ministry.'))
        
        # Create admission file with ministry_pending state
        admission_vals = {
            'applicant_name': self.applicant_name,
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
            'submission_method': 'portal',
            'state': 'ministry_pending'
        }
        
        admission_file = self.env['acmst.admission.file'].create(admission_vals)
        
        # Create initial approval record for ministry pending
        self.env['acmst.admission.approval'].create({
            'admission_file_id': admission_file.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Submitted for ministry approval'
        })
        
        self.write({
            'state': 'under_review',
            'admission_file_id': admission_file.id,
            'submitted_to_ministry': True
        })
        
        # Send notification
        self._send_ministry_submission_notification()
        
        return True

    def action_approve(self):
        """Open ministry approval wizard for portal application"""
        self.ensure_one()
        if self.state not in ['submitted', 'under_review']:
            raise UserError(_('Only submitted or under review applications can be approved.'))
        
        # Create or get admission file first
        if not self.admission_file_id:
            # Create new admission file in ministry_pending state
            admission_vals = {
                'applicant_name': self.applicant_name,
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
                'submission_method': 'portal',
                'state': 'ministry_pending',
                'name': self.name  # Use the same name as portal application
            }
            
            admission_file = self.env['acmst.admission.file'].create(admission_vals)
            self.write({'admission_file_id': admission_file.id})
        else:
            # Update existing admission file with current portal data and set to ministry_pending state
            self.admission_file_id.write({
                'applicant_name': self.applicant_name,
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
                'state': 'ministry_pending'
            })
        
        # Reload the admission file to get the latest data
        admission_file = self.env['acmst.admission.file'].browse(self.admission_file_id.id)
        
        # Validate student data before opening wizard
        try:
            admission_file.validate_student_data()
        except ValidationError as e:
            raise UserError(_('Please fix the following data validation errors before approving:\n\n%s') % str(e))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Ministry Approval - Portal Application'),
            'res_model': 'acmst.ministry.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admission_file_id': self.admission_file_id.id,
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

    def _send_submission_notification(self):
        """Send notification email when application is submitted"""
        self.ensure_one()
        
        template = self.env.ref('acmst_admission.email_template_application_submitted', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_approval_notification(self):
        """Send notification email when application is approved"""
        self.ensure_one()
        
        template = self.env.ref('acmst_admission.email_template_application_approved', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_rejection_notification(self):
        """Send notification email when application is rejected"""
        self.ensure_one()
        
        template = self.env.ref('acmst_admission.email_template_application_rejected', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _send_ministry_submission_notification(self):
        """Send notification email when application is submitted to ministry"""
        self.ensure_one()
        
        template = self.env.ref('acmst_admission.email_template_application_submitted', False)
        if template:
            template.send_mail(self.id, force_send=True)

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

        # Create or get admission file
        if not self.admission_file_id:
            # Create new admission file in ministry_pending state
            admission_vals = {
                'applicant_name': self.applicant_name,
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
                'submission_method': 'portal',
                'state': 'ministry_pending',
                'name': self.name  # Use the same name as portal application
            }

            admission_file = self.env['acmst.admission.file'].create(admission_vals)
            self.write({'admission_file_id': admission_file.id})
        else:
            # Update existing admission file with current portal data and set to ministry_pending state
            self.admission_file_id.write({
                'applicant_name': self.applicant_name,
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
