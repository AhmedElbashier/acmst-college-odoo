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
                record.applicant_name = record.portal_application_id.applicant_name
                record.national_id = record.portal_application_id.national_id
                record.phone = record.portal_application_id.phone
                record.email = record.portal_application_id.email
                record.program_id = record.portal_application_id.program_id
                record.batch_id = record.portal_application_id.batch_id
            elif record.admission_file_id:
                # Get data from admission file
                record.applicant_name = record.admission_file_id.applicant_name
                record.national_id = record.admission_file_id.national_id
                record.phone = record.admission_file_id.phone
                record.email = record.admission_file_id.email
                record.program_id = record.admission_file_id.program_id
                record.batch_id = record.admission_file_id.batch_id
            else:
                # Clear data if no source
                record.applicant_name = False
                record.national_id = False
                record.phone = False
                record.email = False
                record.program_id = False
                record.batch_id = False

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

        if self.decision != 'approve':
            raise UserError(_('This action is only for approval.'))

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
            'applicant_name': self.portal_application_id.applicant_name,
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
            'submission_method': 'portal',
            'state': 'health_required',  # Set to health_required for health check
            # Don't set name - let admission file generate its own ADM000xxx ID
        }

        _logger.info(f"Creating admission file from portal application {self.portal_application_id.name}")
        admission_file = self.env['acmst.admission.file'].create(admission_vals)

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
