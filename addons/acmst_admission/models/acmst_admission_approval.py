# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstAdmissionApproval(models.Model):
    _name = 'acmst.admission.approval'
    _description = 'Admission Approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'approval_date desc'

    # Basic Information
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        required=True,
        ondelete='cascade',
        help='Related admission file'
    )
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        help='User who made the approval decision'
    )
    approval_type = fields.Selection([
        ('ministry', 'Ministry'),
        ('health', 'Health'),
        ('coordinator', 'Coordinator'),
        ('manager', 'Manager'),
        ('completion', 'Completion')
    ], string='Approval Type', required=True, help='Type of approval')
    approval_date = fields.Datetime(
        string='Approval Date',
        default=fields.Datetime.now,
        required=True,
        help='Date and time of the approval'
    )
    decision = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('conditional', 'Conditional'),
        ('completed', 'Completed')
    ], string='Decision', required=True, help='Approval decision')
    comments = fields.Text(
        string='Comments',
        help='Comments about the approval decision'
    )
    attachments = fields.Binary(
        string='Attachments',
        help='Attached documents for this approval'
    )
    attachments_filename = fields.Char(
        string='Attachments Filename',
        help='Name of the attached file'
    )

    # Related fields
    applicant_name = fields.Char(
        string='Applicant Name',
        related='admission_file_id.applicant_name_english',
        store=True,
        help='Name of the applicant'
    )
    program_name = fields.Char(
        string='Program',
        related='admission_file_id.program_id.name',
        store=True,
        help='Program name'
    )
    file_number = fields.Char(
        string='File Number',
        related='admission_file_id.name',
        store=True,
        help='Admission file number'
    )

    # Computed fields
    approver_name = fields.Char(
        string='Approver Name',
        compute='_compute_approver_name',
        help='Name of the approver'
    )
    approval_type_display = fields.Char(
        string='Approval Type Display',
        compute='_compute_approval_type_display',
        help='Display name for approval type'
    )

    @api.depends('approver_id')
    def _compute_approver_name(self):
        """Compute approver name"""
        for record in self:
            record.approver_name = record.approver_id.name if record.approver_id else 'System'

    @api.depends('approval_type')
    def _compute_approval_type_display(self):
        """Compute approval type display name"""
        type_mapping = {
            'ministry': 'Ministry Approval',
            'health': 'Health Check',
            'coordinator': 'Coordinator Review',
            'manager': 'Manager Review',
            'completion': 'Process Completion'
        }
        for record in self:
            record.approval_type_display = type_mapping.get(record.approval_type, record.approval_type)

    @api.constrains('approval_date')
    def _check_approval_date(self):
        """Validate approval date"""
        for record in self:
            if record.approval_date and record.approval_date > fields.Datetime.now():
                raise ValidationError(_('Approval date cannot be in the future.'))

    @api.model
    def create(self, vals):
        """Override create to set approver if not provided"""
        if 'approver_id' not in vals or not vals['approver_id']:
            vals['approver_id'] = self.env.user.id
        
        return super().create(vals)

    def action_view_admission_file(self):
        """Action to view the related admission file"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Admission File'),
            'res_model': 'acmst.admission.file',
            'res_id': self.admission_file_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def get_approval_history(self, admission_file_id):
        """Get approval history for an admission file"""
        return self.search([
            ('admission_file_id', '=', admission_file_id)
        ], order='approval_date desc')

    @api.model
    def get_approval_summary(self, admission_file_id):
        """Get approval summary for an admission file"""
        approvals = self.get_approval_history(admission_file_id)
        
        summary = {
            'ministry': {'status': 'pending', 'date': None, 'approver': None},
            'health': {'status': 'pending', 'date': None, 'approver': None},
            'coordinator': {'status': 'pending', 'date': None, 'approver': None},
            'manager': {'status': 'pending', 'date': None, 'approver': None},
            'completion': {'status': 'pending', 'date': None, 'approver': None}
        }
        
        for approval in approvals:
            if approval.approval_type in summary:
                summary[approval.approval_type] = {
                    'status': approval.decision,
                    'date': approval.approval_date,
                    'approver': approval.approver_name,
                    'comments': approval.comments
                }
        
        return summary
