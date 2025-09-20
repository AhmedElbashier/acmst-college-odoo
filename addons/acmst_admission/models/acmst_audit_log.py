# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging
import json

_logger = logging.getLogger(__name__)


class AcmstAuditLog(models.Model):
    _name = 'acmst.audit.log'
    _description = 'Admission Audit Log'
    _order = 'create_date desc'

    name = fields.Char(
        string='Log Entry',
        compute='_compute_name',
        store=True,
        help='Generated name for the log entry'
    )
    model_name = fields.Char(
        string='Model',
        required=True,
        help='Name of the model being audited'
    )
    record_id = fields.Integer(
        string='Record ID',
        required=True,
        help='ID of the record being audited'
    )
    record_name = fields.Char(
        string='Record Name',
        help='Name of the record being audited'
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        help='User who performed the action'
    )
    action = fields.Selection([
        ('create', 'Create'),
        ('read', 'Read'),
        ('write', 'Update'),
        ('unlink', 'Delete'),
        ('workflow', 'Workflow'),
        ('approval', 'Approval'),
        ('rejection', 'Rejection'),
        ('completion', 'Completion'),
        ('cancellation', 'Cancellation'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('print', 'Print'),
        ('email', 'Email'),
        ('portal_access', 'Portal Access'),
        ('security_violation', 'Security Violation'),
        ('data_breach', 'Data Breach'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('other', 'Other')
    ], string='Action', required=True, help='Type of action performed')
    
    action_description = fields.Text(
        string='Action Description',
        help='Detailed description of the action'
    )
    
    old_values = fields.Text(
        string='Old Values',
        help='Previous values before the change'
    )
    
    new_values = fields.Text(
        string='New Values',
        help='New values after the change'
    )
    
    changed_fields = fields.Text(
        string='Changed Fields',
        help='List of fields that were changed'
    )
    
    ip_address = fields.Char(
        string='IP Address',
        help='IP address of the user'
    )
    
    user_agent = fields.Text(
        string='User Agent',
        help='User agent string from the browser'
    )
    
    session_id = fields.Char(
        string='Session ID',
        help='Session ID of the user'
    )
    
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity', default='low', help='Severity level of the action')
    
    category = fields.Selection([
        ('data_access', 'Data Access'),
        ('data_modification', 'Data Modification'),
        ('workflow', 'Workflow'),
        ('security', 'Security'),
        ('system', 'System'),
        ('user', 'User'),
        ('portal', 'Portal'),
        ('report', 'Report'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('other', 'Other')
    ], string='Category', required=True, help='Category of the action')
    
    is_sensitive = fields.Boolean(
        string='Sensitive Data',
        default=False,
        help='Whether this log entry contains sensitive data'
    )
    
    is_anomaly = fields.Boolean(
        string='Anomaly',
        default=False,
        help='Whether this log entry represents an anomaly'
    )
    
    anomaly_reason = fields.Text(
        string='Anomaly Reason',
        help='Reason why this is considered an anomaly'
    )
    
    related_log_ids = fields.One2many(
        'acmst.audit.log',
        'parent_log_id',
        string='Related Logs',
        help='Related log entries'
    )
    
    parent_log_id = fields.Many2one(
        'acmst.audit.log',
        string='Parent Log',
        help='Parent log entry'
    )
    
    tags = fields.Char(
        string='Tags',
        help='Comma-separated tags for categorization'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the log entry'
    )

    @api.depends('model_name', 'record_id', 'action', 'create_date')
    def _compute_name(self):
        """Compute name for the log entry"""
        for record in self:
            record.name = f"{record.model_name}#{record.record_id} - {record.action} - {record.create_date.strftime('%Y-%m-%d %H:%M')}"

    @api.model
    def create_log(self, model_name, record_id, action, **kwargs):
        """Create a new audit log entry"""
        log_vals = {
            'model_name': model_name,
            'record_id': record_id,
            'action': action,
            'user_id': self.env.user.id,
            'ip_address': self._get_ip_address(),
            'user_agent': self._get_user_agent(),
            'session_id': self._get_session_id(),
        }
        
        # Add additional values
        for key, value in kwargs.items():
            if key in self._fields:
                log_vals[key] = value
        
        return self.create(log_vals)

    def _get_ip_address(self):
        """Get IP address from request"""
        try:
            from odoo.http import request
            return request.httprequest.environ.get('REMOTE_ADDR', '')
        except:
            return ''

    def _get_user_agent(self):
        """Get user agent from request"""
        try:
            from odoo.http import request
            return request.httprequest.environ.get('HTTP_USER_AGENT', '')
        except:
            return ''

    def _get_session_id(self):
        """Get session ID from request"""
        try:
            from odoo.http import request
            return request.session.sid if hasattr(request, 'session') else ''
        except:
            return ''

    @api.model
    def log_data_change(self, record, old_values, new_values, changed_fields):
        """Log data changes"""
        self.create_log(
            model_name=record._name,
            record_id=record.id,
            record_name=getattr(record, 'name', ''),
            action='write',
            action_description=f'Data changed in {record._name}',
            old_values=json.dumps(old_values, default=str),
            new_values=json.dumps(new_values, default=str),
            changed_fields=json.dumps(changed_fields, default=str),
            category='data_modification',
            severity='medium'
        )

    @api.model
    def log_workflow_change(self, record, old_state, new_state, action_description):
        """Log workflow state changes"""
        self.create_log(
            model_name=record._name,
            record_id=record.id,
            record_name=getattr(record, 'name', ''),
            action='workflow',
            action_description=action_description,
            old_values=json.dumps({'state': old_state}, default=str),
            new_values=json.dumps({'state': new_state}, default=str),
            changed_fields=json.dumps(['state'], default=str),
            category='workflow',
            severity='high'
        )

    @api.model
    def log_approval(self, record, approver, decision, comments):
        """Log approval actions"""
        self.create_log(
            model_name=record._name,
            record_id=record.id,
            record_name=getattr(record, 'name', ''),
            action='approval' if decision == 'approved' else 'rejection',
            action_description=f'{decision.title()} by {approver.name}',
            new_values=json.dumps({'decision': decision, 'comments': comments}, default=str),
            category='workflow',
            severity='high',
            is_sensitive=True
        )

    @api.model
    def log_security_violation(self, model_name, record_id, violation_type, description):
        """Log security violations"""
        self.create_log(
            model_name=model_name,
            record_id=record_id,
            action='security_violation',
            action_description=description,
            category='security',
            severity='critical',
            is_sensitive=True,
            is_anomaly=True,
            anomaly_reason=violation_type
        )

    @api.model
    def log_portal_access(self, record, action_description):
        """Log portal access"""
        self.create_log(
            model_name=record._name,
            record_id=record.id,
            record_name=getattr(record, 'name', ''),
            action='portal_access',
            action_description=action_description,
            category='portal',
            severity='medium'
        )

    @api.model
    def get_audit_trail(self, model_name, record_id):
        """Get audit trail for a specific record"""
        return self.search([
            ('model_name', '=', model_name),
            ('record_id', '=', record_id)
        ], order='create_date desc')

    @api.model
    def get_user_activity(self, user_id, days=30):
        """Get user activity for the last N days"""
        date_from = fields.Datetime.now() - timedelta(days=days)
        return self.search([
            ('user_id', '=', user_id),
            ('create_date', '>=', date_from)
        ], order='create_date desc')

    @api.model
    def get_security_violations(self, days=30):
        """Get security violations for the last N days"""
        date_from = fields.Datetime.now() - timedelta(days=days)
        return self.search([
            ('action', 'in', ['security_violation', 'data_breach', 'unauthorized_access']),
            ('create_date', '>=', date_from)
        ], order='create_date desc')

    @api.model
    def get_anomalies(self, days=30):
        """Get anomalies for the last N days"""
        date_from = fields.Datetime.now() - timedelta(days=days)
        return self.search([
            ('is_anomaly', '=', True),
            ('create_date', '>=', date_from)
        ], order='create_date desc')

    @api.model
    def cleanup_old_logs(self, days=365):
        """Clean up old audit logs"""
        date_before = fields.Datetime.now() - timedelta(days=days)
        old_logs = self.search([
            ('create_date', '<', date_before),
            ('severity', 'in', ['low', 'medium'])
        ])
        
        if old_logs:
            old_logs.unlink()
            _logger.info(f'Cleaned up {len(old_logs)} old audit logs')

    @api.model
    def generate_audit_report(self, date_from, date_to, user_id=None, category=None):
        """Generate audit report for a date range"""
        domain = [
            ('create_date', '>=', date_from),
            ('create_date', '<=', date_to)
        ]
        
        if user_id:
            domain.append(('user_id', '=', user_id))
        
        if category:
            domain.append(('category', '=', category))
        
        logs = self.search(domain, order='create_date desc')
        
        report_data = {
            'total_logs': len(logs),
            'by_action': {},
            'by_user': {},
            'by_category': {},
            'by_severity': {},
            'security_violations': len(logs.filtered(lambda l: l.action in ['security_violation', 'data_breach', 'unauthorized_access'])),
            'anomalies': len(logs.filtered('is_anomaly')),
            'sensitive_data': len(logs.filtered('is_sensitive'))
        }
        
        for log in logs:
            # Count by action
            if log.action not in report_data['by_action']:
                report_data['by_action'][log.action] = 0
            report_data['by_action'][log.action] += 1
            
            # Count by user
            if log.user_id.name not in report_data['by_user']:
                report_data['by_user'][log.user_id.name] = 0
            report_data['by_user'][log.user_id.name] += 1
            
            # Count by category
            if log.category not in report_data['by_category']:
                report_data['by_category'][log.category] = 0
            report_data['by_category'][log.category] += 1
            
            # Count by severity
            if log.severity not in report_data['by_severity']:
                report_data['by_severity'][log.severity] = 0
            report_data['by_severity'][log.severity] += 1
        
        return report_data

    def action_view_related_logs(self):
        """Open related logs in a new window"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related Logs'),
            'res_model': 'acmst.audit.log',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.related_log_ids.ids)],
            'context': {
                'default_model_name': self.model_name,
                'default_record_id': self.record_id,
            }
        }