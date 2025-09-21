# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AcmstPendingEmail(models.Model):
    _name = 'acmst.pending.email'
    _description = 'Pending Email Queue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Subject',
        compute='_compute_name',
        store=True,
        help='Generated name for the pending email'
    )

    template_ref = fields.Char(
        string='Email Template',
        required=True,
        help='Reference to the email template to send'
    )

    record_id = fields.Integer(
        string='Record ID',
        required=True,
        help='ID of the record to send email to'
    )

    model_name = fields.Char(
        string='Model',
        required=True,
        help='Model name of the record'
    )

    record_name = fields.Char(
        string='Record Name',
        help='Name of the record for reference'
    )

    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending', required=True, help='Current status of the email')

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium', required=True, help='Email priority')

    retry_count = fields.Integer(
        string='Retry Count',
        default=0,
        help='Number of times email sending has been attempted'
    )

    max_retries = fields.Integer(
        string='Max Retries',
        default=3,
        help='Maximum number of retry attempts'
    )

    last_attempt_date = fields.Datetime(
        string='Last Attempt',
        help='Date of last attempt to send this email'
    )

    next_retry_date = fields.Datetime(
        string='Next Retry',
        compute='_compute_next_retry',
        store=True,
        help='Next scheduled retry date'
    )

    ready_for_retry = fields.Boolean(
        string='Ready for Retry',
        compute='_compute_ready_for_retry',
        store=True,
        help='Whether this email is ready to be retried'
    )

    error_message = fields.Text(
        string='Error Message',
        help='Last error message if sending failed'
    )

    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        help='User who created this pending email'
    )

    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        help='User assigned to handle this pending email'
    )

    notes = fields.Text(
        string='Notes',
        help='Additional notes about this pending email'
    )

    # Computed fields
    template_display = fields.Char(
        string='Template Display',
        compute='_compute_template_display',
        help='Human-readable template name'
    )

    @api.depends('template_ref')
    def _compute_template_display(self):
        """Compute display name for template"""
        template_names = {
            'acmst_admission.email_template_application_submitted': 'Application Submitted',
            'acmst_admission.email_template_application_approved': 'Application Approved',
            'acmst_admission.email_template_application_rejected': 'Application Rejected',
            'acmst_admission.email_template_health_check_required': 'Health Check Required',
            'acmst_admission.email_template_coordinator_conditions': 'Coordinator Conditions',
            'acmst_admission.email_template_health_check_rejected': 'Health Check Rejected',
            'acmst_admission.email_template_condition_overdue': 'Condition Overdue',
            'acmst_admission.email_template_final_approval': 'Final Approval',
            'acmst_admission.email_template_welcome_student': 'Welcome Student'
        }

        for record in self:
            record.template_display = template_names.get(record.template_ref, record.template_ref)

    @api.depends('create_date', 'retry_count')
    def _compute_next_retry(self):
        """Compute next retry date based on retry count"""
        for record in self:
            if record.state == 'pending':
                # Exponential backoff: 5 min, 15 min, 30 min, 1 hour
                delays = [5, 15, 30, 60]
                delay = delays[min(record.retry_count, len(delays) - 1)]
                record.next_retry_date = record.create_date + timedelta(minutes=delay)
            else:
                record.next_retry_date = False

    @api.depends('state', 'next_retry_date')
    def _compute_ready_for_retry(self):
        """Compute if email is ready for retry"""
        now = fields.Datetime.now()
        for record in self:
            record.ready_for_retry = (
                record.state == 'pending' and
                record.next_retry_date and
                record.next_retry_date <= now
            )

    @api.depends('template_ref', 'record_id', 'model_name')
    def _compute_name(self):
        """Compute name for the pending email"""
        for record in self:
            record.name = f"{record.template_display} - {record.model_name}#{record.record_id}"

    @api.model
    def create(self, vals):
        """Override create to set initial state"""
        vals['state'] = 'pending'
        return super().create(vals)

    def action_retry_send(self):
        """Retry sending the email"""
        for record in self:
            if record.state == 'pending' and record.retry_count < record.max_retries:
                record._attempt_send()
            elif record.retry_count >= record.max_retries:
                record.state = 'failed'
                record.error_message = 'Maximum retry attempts exceeded'

    def _attempt_send(self):
        """Attempt to send the email"""
        self.ensure_one()

        try:
            # Update attempt info
            self.last_attempt_date = fields.Datetime.now()
            self.retry_count += 1

            # Get the template and record
            template = self.env.ref(self.template_ref, False)
            if not template:
                raise ValidationError(_('Email template not found'))

            # Get the record to send email to
            record = self.env[self.model_name].browse(self.record_id)
            if not record.exists():
                raise ValidationError(_('Record not found'))

            # Check if mail server is available
            mail_server = self.env['ir.mail_server'].search([('active', '=', True)], order='sequence', limit=1)
            if not mail_server:
                raise ValidationError(_('No active mail server configured'))

            # Send the email
            template.send_mail(record.id, force_send=True)

            # Mark as sent
            self.state = 'sent'
            _logger.info(f'Successfully sent pending email {self.name}')

        except Exception as e:
            error_msg = str(e)
            self.error_message = error_msg

            if self.retry_count >= self.max_retries:
                self.state = 'failed'
                _logger.error(f'Failed to send pending email {self.name} after {self.retry_count} attempts: {error_msg}')
            else:
                _logger.warning(f'Failed to send pending email {self.name} (attempt {self.retry_count}): {error_msg}')

    def action_cancel(self):
        """Cancel the pending email"""
        self.state = 'cancelled'

    def action_reset_retry(self):
        """Reset retry count and status"""
        self.retry_count = 0
        self.state = 'pending'
        self.error_message = False

    @api.model
    def cron_retry_pending_emails(self):
        """Cron job to retry pending emails"""
        # Update ready_for_retry field first
        self._compute_ready_for_retry()

        pending_emails = self.search([
            ('state', '=', 'pending'),
            ('ready_for_retry', '=', True)
        ])

        for email in pending_emails:
            email._attempt_send()

        if pending_emails:
            _logger.info(f'Retried {len(pending_emails)} pending emails')

    @api.model
    def get_pending_email_summary(self):
        """Get summary of pending emails for dashboard"""
        return {
            'pending_count': self.search_count([('state', '=', 'pending')]),
            'failed_count': self.search_count([('state', '=', 'failed')]),
            'sent_count': self.search_count([('state', '=', 'sent')]),
            'total_count': self.search_count([]),
        }
