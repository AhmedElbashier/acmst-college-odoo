# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstAdmissionWizard(models.TransientModel):
    _name = 'acmst.admission.wizard'
    _description = 'Admission Wizard'

    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        required=True,
        help='Admission file to process'
    )
    action_type = fields.Selection([
        ('ministry_approve', 'Ministry Approve'),
        ('ministry_reject', 'Ministry Reject'),
        ('health_approve', 'Health Approve'),
        ('health_reject', 'Health Reject'),
        ('coordinator_approve', 'Coordinator Approve'),
        ('coordinator_reject', 'Coordinator Reject'),
        ('coordinator_conditional', 'Coordinator Conditional'),
        ('manager_approve', 'Manager Approve'),
        ('manager_reject', 'Manager Reject'),
        ('complete', 'Complete'),
        ('cancel', 'Cancel')
    ], string='Action Type', required=True, help='Type of action to perform')
    comments = fields.Text(
        string='Comments',
        help='Comments about the action'
    )
    send_notification = fields.Boolean(
        string='Send Notification',
        default=True,
        help='Send email notification to applicant'
    )

    def action_confirm(self):
        """Confirm the wizard action"""
        self.ensure_one()
        
        if not self.admission_file_id:
            raise UserError(_('Please select an admission file.'))
        
        # Perform the action based on action_type
        action_methods = {
            'ministry_approve': self.admission_file_id.action_ministry_approve,
            'ministry_reject': self.admission_file_id.action_ministry_reject,
            'health_approve': self.admission_file_id.action_health_approve,
            'health_reject': self.admission_file_id.action_health_reject,
            'coordinator_approve': self.admission_file_id.action_coordinator_approve,
            'coordinator_reject': self.admission_file_id.action_coordinator_reject,
            'coordinator_conditional': self.admission_file_id.action_coordinator_conditional,
            'manager_approve': self.admission_file_id.action_manager_approve,
            'manager_reject': self.admission_file_id.action_manager_reject,
            'complete': self.admission_file_id.action_complete,
            'cancel': self.admission_file_id.action_cancel
        }
        
        action_method = action_methods.get(self.action_type)
        if not action_method:
            raise UserError(_('Invalid action type.'))
        
        # Update comments if provided
        if self.comments:
            # Create approval record with comments
            self.env['acmst.admission.approval'].create({
                'admission_file_id': self.admission_file_id.id,
                'approver_id': self.env.user.id,
                'approval_type': self._get_approval_type(),
                'approval_date': fields.Datetime.now(),
                'decision': self._get_decision(),
                'comments': self.comments
            })
        
        # Perform the action
        action_method()
        
        # Send notification if requested
        if self.send_notification:
            self._send_notification()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Admission File'),
            'res_model': 'acmst.admission.file',
            'res_id': self.admission_file_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_approval_type(self):
        """Get approval type based on action type"""
        type_mapping = {
            'ministry_approve': 'ministry',
            'ministry_reject': 'ministry',
            'health_approve': 'health',
            'health_reject': 'health',
            'coordinator_approve': 'coordinator',
            'coordinator_reject': 'coordinator',
            'coordinator_conditional': 'coordinator',
            'manager_approve': 'manager',
            'manager_reject': 'manager',
            'complete': 'completion',
            'cancel': 'completion'
        }
        return type_mapping.get(self.action_type, 'completion')

    def _get_decision(self):
        """Get decision based on action type"""
        decision_mapping = {
            'ministry_approve': 'approved',
            'ministry_reject': 'rejected',
            'health_approve': 'approved',
            'health_reject': 'rejected',
            'coordinator_approve': 'approved',
            'coordinator_reject': 'rejected',
            'coordinator_conditional': 'conditional',
            'manager_approve': 'approved',
            'manager_reject': 'rejected',
            'complete': 'completed',
            'cancel': 'rejected'
        }
        return decision_mapping.get(self.action_type, 'pending')

    def _send_notification(self):
        """Send notification email"""
        self.ensure_one()
        
        # This would be implemented with email templates
        # For now, just log the notification
        _logger.info(f'Notification sent for admission file {self.admission_file_id.name}')
        
        return True
