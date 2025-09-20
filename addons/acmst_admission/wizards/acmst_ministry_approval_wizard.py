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
        required=True,
        ondelete='cascade',
        help='Admission file to approve'
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
        related='admission_file_id.applicant_name',
        readonly=True,
        help='Student name for verification'
    )
    national_id = fields.Char(
        string='National ID',
        related='admission_file_id.national_id',
        readonly=True,
        help='National ID for verification'
    )
    phone = fields.Char(
        string='Phone',
        related='admission_file_id.phone',
        readonly=True,
        help='Phone number for verification'
    )
    email = fields.Char(
        string='Email',
        related='admission_file_id.email',
        readonly=True,
        help='Email for verification'
    )
    program_id = fields.Many2one(
        'acmst.program',
        string='Program',
        related='admission_file_id.program_id',
        readonly=True,
        help='Program for verification'
    )
    batch_id = fields.Many2one(
        'acmst.batch',
        string='Batch',
        related='admission_file_id.batch_id',
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

    def action_validate_data(self):
        """Validate student data"""
        self.ensure_one()
        try:
            self.admission_file_id.validate_student_data()
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
