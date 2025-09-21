# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstMinistryApprovalWizard(models.TransientModel):
    _name = 'acmst.ministry.approval.wizard'
    _description = 'Ministry Approval Wizard'

    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        ondelete='cascade',
        help='Admission file to approve'
    )
    portal_application_id = fields.Many2one(
        'acmst.portal.application',
        string='Portal Application',
        ondelete='cascade',
        help='Portal application to approve'
    )
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True,
        default=lambda self: self.env.user,
        help='User approving the application'
    )
    
    # Student Data Re-validation Fields
    applicant_name = fields.Char(
        string='Applicant Name',
        compute='_compute_applicant_data',
        readonly=True,
        help='Student name for verification'
    )
    national_id = fields.Char(
        string='National ID',
        compute='_compute_applicant_data',
        readonly=True,
        help='National ID for verification'
    )
    phone = fields.Char(
        string='Phone',
        compute='_compute_applicant_data',
        readonly=True,
        help='Phone number for verification'
    )
    email = fields.Char(
        string='Email',
        compute='_compute_applicant_data',
        readonly=True,
        help='Email for verification'
    )
    program_id = fields.Many2one(
        'acmst.program',
        string='Program',
        compute='_compute_applicant_data',
        readonly=True,
        help='Program for verification'
    )
    batch_id = fields.Many2one(
        'acmst.batch',
        string='Batch',
        compute='_compute_applicant_data',
        readonly=True,
        help='Batch for verification'
    )
    
    # University ID Entry
    university_id = fields.Char(
        string='University ID',
        help='University ID provided by ministry (FRMNO) - Leave empty if not available'
    )
    has_university_id = fields.Boolean(
        string='Has University ID',
        default=False,
        help='Check if university ID is available from ministry'
    )
    
    # Approval Decision
    decision = fields.Selection([
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ], string='Decision', required=True, default='approve', help='Approval decision')
    
    comments = fields.Text(
        string='Comments',
        help='Comments about the approval decision'
    )
    
    # Data Validation Status
    data_validated = fields.Boolean(
        string='Data Validated',
        default=False,
        help='Whether student data has been validated'
    )

    # Sensitive Data Acknowledgment
    acknowledge_sensitive_data = fields.Boolean(
        string='I acknowledge that I have reviewed all sensitive data',
        default=False,
        help='I confirm that I have carefully reviewed all sensitive personal information including National ID, contact details, and academic records'
    )

    # Additional Sensitive Data Fields
    birth_date = fields.Date(
        string='Birth Date',
        compute='_compute_applicant_data',
        readonly=True,
        help='Date of birth for verification'
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender',
        compute='_compute_applicant_data',
        readonly=True,
        help='Gender for verification'
    )
    nationality = fields.Char(
        string='Nationality',
        compute='_compute_applicant_data',
        readonly=True,
        help='Nationality for verification'
    )
    address = fields.Text(
        string='Address',
        compute='_compute_applicant_data',
        readonly=True,
        help='Residential address for verification'
    )
    emergency_contact = fields.Char(
        string='Emergency Contact',
        compute='_compute_applicant_data',
        readonly=True,
        help='Emergency contact name for verification'
    )
    emergency_phone = fields.Char(
        string='Emergency Phone',
        compute='_compute_applicant_data',
        readonly=True,
        help='Emergency contact phone for verification'
    )

    # Educational Data
    education_institution = fields.Char(
        string='Previous Institution',
        compute='_compute_applicant_data',
        readonly=True,
        help='Previous educational institution'
    )
    education_program = fields.Char(
        string='Previous Program',
        compute='_compute_applicant_data',
        readonly=True,
        help='Previous program studied'
    )
    education_completion_year = fields.Integer(
        string='Completion Year',
        compute='_compute_applicant_data',
        readonly=True,
        help='Year of completion of previous education'
    )
    certificate_type = fields.Selection([
        ('high_school', 'High School'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
        ('diploma', 'Diploma'),
        ('other', 'Other')
    ], string='Certificate Type',
        compute='_compute_applicant_data',
        readonly=True,
        help='Type of previous certificate'
    )

    @api.onchange('has_university_id')
    def _onchange_has_university_id(self):
        """Clear university ID when unchecked"""
        if not self.has_university_id:
            self.university_id = False

    @api.onchange('university_id')
    def _onchange_university_id(self):
        """Update has_university_id based on university_id value"""
        if self.university_id:
            self.has_university_id = True
        else:
            self.has_university_id = False

    @api.depends('admission_file_id', 'portal_application_id')
    def _compute_applicant_data(self):
        """Compute applicant data from admission file or portal application"""
        for record in self:
            if record.portal_application_id:
                # Get data from portal application
                record.applicant_name = record.portal_application_id.applicant_name_english
                record.national_id = record.portal_application_id.national_id
                record.phone = record.portal_application_id.phone
                record.email = record.portal_application_id.email
                record.program_id = record.portal_application_id.program_id
                record.batch_id = record.portal_application_id.batch_id
                record.birth_date = record.portal_application_id.birth_date
                record.gender = record.portal_application_id.gender
                record.nationality = record.portal_application_id.nationality
                record.address = record.portal_application_id.address
                record.emergency_contact = record.portal_application_id.emergency_contact
                record.emergency_phone = record.portal_application_id.emergency_phone
                record.education_institution = record.portal_application_id.education_institution
                record.education_program = record.portal_application_id.education_program
                record.education_completion_year = record.portal_application_id.education_completion_year
                record.certificate_type = record.portal_application_id.certificate_type
            elif record.admission_file_id:
                # Get data from admission file
                record.applicant_name = record.admission_file_id.applicant_name_english
                record.national_id = record.admission_file_id.national_id
                record.phone = record.admission_file_id.phone
                record.email = record.admission_file_id.email
                record.program_id = record.admission_file_id.program_id
                record.batch_id = record.admission_file_id.batch_id
                record.birth_date = record.admission_file_id.birth_date
                record.gender = record.admission_file_id.gender
                record.nationality = record.admission_file_id.nationality
                record.address = record.admission_file_id.address
                record.emergency_contact = record.admission_file_id.emergency_contact
                record.emergency_phone = record.admission_file_id.emergency_phone
                record.education_institution = record.admission_file_id.education_institution
                record.education_program = record.admission_file_id.education_program
                record.education_completion_year = record.admission_file_id.education_completion_year
                record.certificate_type = record.admission_file_id.certificate_type
            else:
                # Clear data if no source
                record.applicant_name = False
                record.national_id = False
                record.phone = False
                record.email = False
                record.program_id = False
                record.batch_id = False
                record.birth_date = False
                record.gender = False
                record.nationality = False
                record.address = False
                record.emergency_contact = False
                record.emergency_phone = False
                record.education_institution = False
                record.education_program = False
                record.education_completion_year = False
                record.certificate_type = False

    def action_validate_data(self):
        """Validate student data"""
        self.ensure_one()
        try:
            # Validate data based on source (portal application or admission file)
            if self.portal_application_id:
                # For portal applications, validate the portal application data
                self.portal_application_id.validate_student_data()
            elif self.admission_file_id:
                # For admission files, validate the admission file data
                self.admission_file_id.validate_student_data()
            else:
                raise ValidationError(_('No source data found to validate.'))

            self.data_validated = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Student data validation completed successfully.'),
                    'type': 'success',
                }
            }
        except ValidationError as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Validation Error'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def action_approve(self):
        """Approve application with university ID handling"""
        self.ensure_one()

        if not self.data_validated:
            raise UserError(_('Please validate student data first before approving.'))

        if not self.acknowledge_sensitive_data:
            raise UserError(_('Please acknowledge that you have reviewed all sensitive data before approving.'))

        if self.decision != 'approve':
            raise UserError(_('This action is only for approval.'))

        # Log the acknowledgment of sensitive data
        _logger.info(f"User {self.approver_id.name} acknowledged sensitive data review for applicant {self.applicant_name}")

        # Create audit log entry for data acknowledgment
        audit_vals = {
            'model_name': 'acmst.admission.file' if self.admission_file_id else 'acmst.portal.application',
            'record_id': self.admission_file_id.id if self.admission_file_id else self.portal_application_id.id,
            'record_name': self.admission_file_id.name if self.admission_file_id else self.portal_application_id.name,
            'action': 'approval',
            'category': 'data_access',
            'old_values': '',
            'new_values': 'Sensitive data reviewed and acknowledged',
            'user_id': self.approver_id.id,
            'action_description': f'Sensitive data acknowledgment by {self.approver_id.name} for ministry approval',
            'is_sensitive': True,
            'severity': 'high'
        }
        self.env['acmst.audit.log'].create(audit_vals)

        if self.portal_application_id:
            # Handle portal application approval
            return self._approve_portal_application()
        else:
            # Handle regular admission file approval
            return self._approve_admission_file()

    def _approve_portal_application(self):
        """Approve portal application and create admission file"""
        self.ensure_one()

        _logger.info(f"Starting approval process for portal application {self.portal_application_id.name}")

        # Create admission file from portal application
        admission_vals = {
            'applicant_name_english': self.portal_application_id.applicant_name_english,
            'applicant_name_arabic': self.portal_application_id.applicant_name_arabic,
            'national_id': self.portal_application_id.national_id,
            'phone': self.portal_application_id.phone,
            'email': self.portal_application_id.email,
            'program_id': self.portal_application_id.program_id.id,
            'batch_id': self.portal_application_id.batch_id.id,
            'birth_date': self.portal_application_id.birth_date,
            'gender': self.portal_application_id.gender,
            'nationality': self.portal_application_id.nationality,
            'address': self.portal_application_id.address,
            'emergency_contact': self.portal_application_id.emergency_contact,
            'emergency_phone': self.portal_application_id.emergency_phone,
            'previous_education': self.portal_application_id.previous_education,
            'education_institution': self.portal_application_id.education_institution,
            'education_program': self.portal_application_id.education_program,
            'education_college': self.portal_application_id.education_college,
            'education_major': self.portal_application_id.education_major,
            'education_start_year': self.portal_application_id.education_start_year,
            'education_completion_year': self.portal_application_id.education_completion_year,
            'certificate_type': self.portal_application_id.certificate_type,
            'education_duration_years': self.portal_application_id.education_duration_years,
            'submission_method': 'portal',
            'state': 'health_required',  # Set to health_required for health check
            'profile_picture': self.portal_application_id.profile_picture,
            'profile_picture_filename': self.portal_application_id.profile_picture_filename,
            'id_type': self.portal_application_id.id_type,
            'admission_type': self.portal_application_id.admission_type,
            'place_of_birth': self.portal_application_id.place_of_birth,
            'religion': self.portal_application_id.religion,
            # Don't set name - let admission file generate its own ADM000xxx ID
        }

        _logger.info(f"Creating admission file from portal application {self.portal_application_id.name}")
        admission_file = self.env['acmst.admission.file'].create(admission_vals)

        # Create guardian records for the admission file
        for guardian in self.portal_application_id.guardian_ids:
            self.env['acmst.guardian'].create({
                'name': guardian.name,
                'relationship': guardian.relationship,
                'phone': guardian.phone,
                'email': guardian.email,
                'is_default': guardian.is_default,
                'is_active': guardian.is_active,
                'admission_file_id': admission_file.id
            })

        # Handle university ID
        if self.has_university_id and self.university_id:
            _logger.info(f"Updating university ID for admission file {admission_file.name}: {self.university_id}")
            # Update university ID
            admission_file.update_university_id(
                self.university_id,
                self.approver_id.id
            )
        else:
            _logger.info(f"No university ID provided for admission file {admission_file.name} - marking as processing student")
            # Mark as processing student
            admission_file.mark_as_processing_student(self.approver_id.id)

        # Create health check record automatically
        _logger.info(f"Creating health check record for admission file {admission_file.name}")
        admission_file._create_health_check_record()

        # Create approval record for ministry approval
        _logger.info(f"Creating ministry approval record for admission file {admission_file.name}")
        self.env['acmst.admission.approval'].create({
            'admission_file_id': admission_file.id,
            'approver_id': self.approver_id.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': self.comments or f'Portal application approved by ministry. University ID: {self.university_id or "Not provided"}'
        })

        # Update portal application state
        _logger.info(f"Updating portal application {self.portal_application_id.name} state to 'approved'")
        self.portal_application_id.write({
            'state': 'approved',
            'admission_file_id': admission_file.id
        })

        # Send notifications
        _logger.info(f"Sending approval notification for portal application {self.portal_application_id.name}")
        self._send_approval_notification()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Admission File Created'),
            'res_model': 'acmst.admission.file',
            'view_mode': 'form',
            'res_id': admission_file.id,
            'target': 'current',
        }

    def _send_approval_notification(self):
        """Send approval notification"""
        # TODO: Implement notification logic
        _logger.info(f"Portal application {self.portal_application_id.name} approved by ministry")

    def _approve_admission_file(self):
        """Approve regular admission file"""
        self.ensure_one()

        # Update admission file state
        self.admission_file_id.write({
            'state': 'ministry_approved',
            'ministry_approval_date': fields.Date.today(),
            'ministry_approver': self.approver_id.id
        })

        # Handle university ID
        if self.has_university_id and self.university_id:
            # Update university ID and clear processing status
            self.admission_file_id.update_university_id(
                self.university_id,
                self.approver_id.id
            )
        else:
            # Mark as processing student
            self.admission_file_id.mark_as_processing_student(
                self.approver_id.id
            )

        # Move to health check after ministry approval
        self.admission_file_id.action_send_to_health_check()

        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file_id.id,
            'approver_id': self.approver_id.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': self.comments or f'Approved by ministry. University ID: {self.university_id or "Not provided - marked as processing student"}'
        })

        # Update portal application state if it exists
        portal_app = self.env['acmst.portal.application'].search([
            ('admission_file_id', '=', self.admission_file_id.id)
        ], limit=1)
        if portal_app:
            portal_app.write({'state': 'approved'})
            # Send approval notification
            portal_app._send_approval_notification()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.portal.application',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {'create': False}
        }

    def action_reject(self):
        """Reject application"""
        self.ensure_one()
        
        if self.decision != 'reject':
            raise UserError(_('This action is only for rejection.'))
        
        # Update admission file state
        self.admission_file_id.write({
            'state': 'ministry_rejected',
            'ministry_approval_date': fields.Date.today(),
            'ministry_approver': self.approver_id.id
        })
        
        # Create approval record
        self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file_id.id,
            'approver_id': self.approver_id.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': self.comments or 'Rejected by ministry'
        })
        
        # Update portal application state if it exists
        portal_app = self.env['acmst.portal.application'].search([
            ('admission_file_id', '=', self.admission_file_id.id)
        ], limit=1)
        if portal_app:
            portal_app.write({'state': 'rejected'})
            # Send rejection notification
            portal_app._send_rejection_notification()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.portal.application',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {'create': False}
        }
