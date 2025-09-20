# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class AcmstCoordinatorCondition(models.Model):
    _name = 'acmst.coordinator.condition'
    _description = 'Coordinator Condition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'condition_date desc, deadline asc'

    # Basic Information
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        required=True,
        ondelete='cascade',
        help='Related admission file'
    )
    coordinator_id = fields.Many2one(
        'res.users',
        string='Coordinator',
        required=True,
        default=lambda self: self.env.user,
        help='Program coordinator who set the condition'
    )
    condition_date = fields.Date(
        string='Condition Date',
        default=fields.Date.today,
        required=True,
        help='Date when the condition was set'
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('overdue', 'Overdue')
    ], string='State', default='pending', tracking=True, help='Current state of the condition')

    # Dashboard Statistics (computed fields)
    total_conditions = fields.Integer(
        string='Total Conditions',
        compute='_compute_dashboard_statistics',
        help='Total number of conditions'
    )
    pending_conditions = fields.Integer(
        string='Pending Conditions',
        compute='_compute_dashboard_statistics',
        help='Number of pending conditions'
    )
    completed_conditions = fields.Integer(
        string='Completed Conditions',
        compute='_compute_dashboard_statistics',
        help='Number of completed conditions'
    )
    overdue_conditions = fields.Integer(
        string='Overdue Conditions',
        compute='_compute_dashboard_statistics',
        help='Number of overdue conditions'
    )

    # Condition Details
    subject_name = fields.Char(
        string='Subject Name',
        required=True,
        help='Name of the subject to complete'
    )
    subject_code = fields.Char(
        string='Subject Code',
        help='Code of the subject'
    )
    level = fields.Selection([
        ('level2', 'Level 2'),
        ('level3', 'Level 3')
    ], string='Level', required=True, help='Academic level of the subject')
    description = fields.Text(
        string='Description',
        required=True,
        help='Detailed description of the condition'
    )
    deadline = fields.Date(
        string='Deadline',
        required=False,
        help='Deadline for completing the condition (optional)'
    )
    completion_date = fields.Date(
        string='Completion Date',
        help='Date when the condition was completed'
    )
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue')
    ], string='Status', compute='_compute_status', store=True, help='Current status of the condition')
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the condition'
    )

    # Related fields
    applicant_name = fields.Char(
        string='Applicant Name',
        related='admission_file_id.applicant_name',
        store=True,
        help='Name of the applicant'
    )
    program_name = fields.Char(
        string='Program',
        related='admission_file_id.program_id.name',
        store=True,
        help='Program name'
    )

    # Computed fields
    days_remaining = fields.Integer(
        string='Days Remaining',
        compute='_compute_days_remaining',
        help='Number of days remaining until deadline'
    )
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        help='Whether the condition is overdue'
    )

    @api.depends('deadline', 'state')
    def _compute_status(self):
        """Compute status based on deadline and state"""
        today = date.today()
        for record in self:
            if record.state == 'completed':
                record.status = 'completed'
            elif record.state == 'rejected':
                record.status = 'rejected'
            elif record.deadline and record.deadline < today and record.state == 'pending':
                record.status = 'overdue'
            else:
                record.status = 'pending'

    @api.depends('deadline')
    def _compute_days_remaining(self):
        """Compute days remaining until deadline"""
        today = date.today()
        for record in self:
            if record.deadline and record.state == 'pending':
                delta = record.deadline - today
                record.days_remaining = delta.days
            else:
                record.days_remaining = 0

    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        """Compute if condition is overdue"""
        today = date.today()
        for record in self:
            record.is_overdue = (
                record.deadline and 
                record.deadline < today and 
                record.state == 'pending'
            )

    @api.constrains('deadline')
    def _check_deadline(self):
        """Validate deadline date"""
        for record in self:
            if record.deadline and record.deadline < record.condition_date:
                raise ValidationError(_('Deadline cannot be before condition date.'))

    @api.constrains('completion_date')
    def _check_completion_date(self):
        """Validate completion date"""
        for record in self:
            if record.completion_date and record.completion_date < record.condition_date:
                raise ValidationError(_('Completion date cannot be before condition date.'))

    def action_complete(self):
        """Mark condition as completed"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending conditions can be completed.'))

        _logger.info(f"Coordinator condition {self.name} completed by {self.env.user.name}")
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today()
        })
        _logger.info(f"Coordinator condition {self.name} state changed to 'completed'")

        # Check if all conditions are completed
        _logger.info(f"Checking if all conditions are completed for admission file {self.admission_file_id.name}")
        self._check_all_conditions_completed()

        return True

    def action_reject(self):
        """Mark condition as rejected"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending conditions can be rejected.'))

        _logger.info(f"Coordinator condition {self.name} rejected by {self.env.user.name}")
        self.write({'state': 'rejected'})
        _logger.info(f"Coordinator condition {self.name} state changed to 'rejected'")
        return True

    def action_reset_to_pending(self):
        """Reset condition to pending"""
        self.ensure_one()
        if self.state not in ['completed', 'rejected']:
            raise UserError(_('Only completed or rejected conditions can be reset to pending.'))
        
        self.write({
            'state': 'pending',
            'completion_date': False
        })
        return True

    @api.depends()
    def _compute_dashboard_statistics(self):
        """Compute dashboard statistics"""
        for record in self:
            stats = self.get_condition_statistics()
            record.total_conditions = stats['total']
            record.pending_conditions = stats['pending']
            record.completed_conditions = stats['completed']
            record.overdue_conditions = stats['overdue']

    def _check_all_conditions_completed(self):
        """Check if all conditions for the admission file are completed"""
        self.ensure_one()
        
        # Get all pending conditions for this admission file
        pending_conditions = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file_id.id),
            ('state', '=', 'pending')
        ])
        
        # If no pending conditions, update admission file state
        if not pending_conditions:
            if self.admission_file_id.state == 'coordinator_conditional':
                self.admission_file_id.action_coordinator_approve()

    @api.model
    def _cron_check_overdue_conditions(self):
        """Cron job to check for overdue conditions"""
        today = date.today()
        overdue_conditions = self.search([
            ('state', '=', 'pending'),
            ('deadline', '!=', False),
            ('deadline', '<', today)
        ])
        
        for condition in overdue_conditions:
            condition.write({'state': 'overdue'})
            _logger.info(f'Marked condition {condition.id} as overdue')

    @api.model
    def create(self, vals):
        """Override create method"""
        return super().create(vals)

    def get_portal_url(self):
        """Get portal URL for this condition"""
        return request.httprequest.host_url.rstrip('/') + '/admission/conditions/' + str(self.admission_file_id.id)

    def send_completion_notification(self):
        """Send condition completion notification"""
        self.ensure_one()
        if self.state == 'completed':
            # Send notification to admission file
            self.admission_file_id.send_conditions_notification()

    def send_overdue_notification(self):
        """Send condition overdue notification"""
        self.ensure_one()
        if self.state == 'overdue':
            # Send notification to admission file
            template = self.env.ref('acmst_admission.email_template_condition_overdue', False)
            if template:
                template.send_mail(self.id, force_send=True)

    def get_condition_summary(self):
        """Get condition summary for reporting"""
        self.ensure_one()
        return {
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'level': self.level,
            'description': self.description,
            'deadline': self.deadline,
            'completion_date': self.completion_date,
            'status': self.status,
            'state': self.state,
            'days_remaining': self.days_remaining,
            'is_overdue': self.is_overdue,
            'notes': self.notes,
            'applicant_name': self.applicant_name,
            'program_name': self.program_name
        }

    def get_conditions_by_coordinator(self, coordinator_id):
        """Get all conditions for a specific coordinator"""
        return self.search([
            ('coordinator_id', '=', coordinator_id)
        ])

    def get_overdue_conditions(self):
        """Get all overdue conditions"""
        return self.search([
            ('state', '=', 'overdue')
        ])

    def get_pending_conditions(self):
        """Get all pending conditions"""
        return self.search([
            ('state', '=', 'pending')
        ])

    def get_conditions_by_admission_file(self, admission_file_id):
        """Get all conditions for a specific admission file"""
        return self.search([
            ('admission_file_id', '=', admission_file_id)
        ])

    def get_condition_statistics(self):
        """Get condition statistics for dashboard"""
        # Get conditions for the specific admission file
        conditions = self.search([('admission_file_id', '=', self.admission_file_id.id)])
        
        return {
            'total': len(conditions),
            'pending': len(conditions.filtered(lambda c: c.state == 'pending')),
            'completed': len(conditions.filtered(lambda c: c.state == 'completed')),
            'overdue': len(conditions.filtered(lambda c: c.state == 'overdue')),
            'rejected': len(conditions.filtered(lambda c: c.state == 'rejected'))
        }

    def action_view_graph(self):
        """Open graph view for coordinator conditions"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Coordinator Conditions Graph'),
            'res_model': 'acmst.coordinator.condition',
            'view_mode': 'graph',
            'target': 'current',
        }

    def action_view_pivot(self):
        """Open pivot view for coordinator conditions"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Coordinator Conditions Pivot'),
            'res_model': 'acmst.coordinator.condition',
            'view_mode': 'pivot',
            'target': 'current',
        }