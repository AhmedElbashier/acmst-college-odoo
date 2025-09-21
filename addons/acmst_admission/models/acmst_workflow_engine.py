# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class AcmstWorkflowEngine(models.Model):
    _name = 'acmst.workflow.engine'
    _description = 'Admission Workflow Engine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(
        string='Workflow Name',
        required=True,
        help='Name of the workflow'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering workflows'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this workflow is active'
    )
    description = fields.Text(
        string='Description',
        help='Description of the workflow'
    )
    workflow_rules = fields.One2many(
        'acmst.workflow.rule',
        'workflow_id',
        string='Workflow Rules',
        help='Rules for this workflow'
    )
    auto_transitions = fields.Boolean(
        string='Auto Transitions',
        default=True,
        help='Enable automatic state transitions'
    )
    notification_enabled = fields.Boolean(
        string='Enable Notifications',
        default=True,
        help='Enable email notifications for state changes'
    )
    timeout_hours = fields.Integer(
        string='Timeout Hours',
        default=24,
        help='Timeout in hours for automatic transitions'
    )

    def execute_workflow(self, admission_file):
        """Execute workflow for an admission file"""
        self.ensure_one()
        
        if not self.active:
            return False
        
        current_state = admission_file.state
        applicable_rules = self.workflow_rules.filtered(
            lambda r: r.from_state == current_state and r.active
        )
        
        for rule in applicable_rules:
            if rule.evaluate_conditions(admission_file):
                if rule.action_type == 'transition':
                    old_state = admission_file.state
                    admission_file.write({'state': rule.to_state})
                    _logger.info(f'Workflow transition: {current_state} -> {rule.to_state} for file {admission_file.name}')

                    # Create audit log entry for workflow transition
                    self.env['acmst.audit.log'].create({
                        'model_name': 'acmst.admission.file',
                        'record_id': admission_file.id,
                        'record_name': admission_file.name,
                        'action': 'workflow',
                        'category': 'workflow',
                        'old_values': f'State: {old_state}',
                        'new_values': f'State: {admission_file.state}',
                        'user_id': self.env.user.id,
                        'action_description': f'Workflow transition from {old_state} to {admission_file.state} via {self.name}'
                    })

                    # Post message to chatter
                    admission_file.message_post(
                        body=f'Workflow transition: Status changed from {old_state} to {admission_file.state} via workflow {self.name}',
                        message_type='comment'
                    )

                    if self.notification_enabled and rule.send_notification:
                        rule.send_notification_email(admission_file)
                
                elif rule.action_type == 'notification':
                    if self.notification_enabled:
                        rule.send_notification_email(admission_file)
                
                elif rule.action_type == 'validation':
                    if not rule.validate_conditions(admission_file):
                        raise ValidationError(_(rule.error_message))
        
        return True

    def process_timeout_transitions(self):
        """Process timeout transitions for all admission files"""
        self.ensure_one()
        
        if not self.auto_transitions:
            return
        
        timeout_rules = self.workflow_rules.filtered(
            lambda r: r.action_type == 'timeout' and r.active
        )
        
        for rule in timeout_rules:
            timeout_date = fields.Datetime.now() - timedelta(hours=rule.timeout_hours)
            admission_files = self.env['acmst.admission.file'].search([
                ('state', '=', rule.from_state),
                ('write_date', '<', timeout_date)
            ])
            
            for admission_file in admission_files:
                try:
                    admission_file.write({'state': rule.to_state})
                    _logger.info(f'Timeout transition: {rule.from_state} -> {rule.to_state} for file {admission_file.name}')
                    
                    if self.notification_enabled and rule.send_notification:
                        rule.send_notification_email(admission_file)
                except (ValidationError, UserError) as e:
                    _logger.error(f'Validation error processing timeout transition for file {admission_file.name}: {str(e)}')
                except Exception as e:
                    _logger.error(f'Unexpected error processing timeout transition for file {admission_file.name}: {str(e)}')

    @api.model
    def process_all_workflows(self):
        """Process all active workflows"""
        active_workflows = self.search([('active', '=', True)])
        
        for workflow in active_workflows:
            try:
                workflow.process_timeout_transitions()
            except (ValidationError, UserError) as e:
                _logger.error(f'Validation error processing workflow {workflow.name}: {str(e)}')
            except Exception as e:
                _logger.error(f'Unexpected error processing workflow {workflow.name}: {str(e)}')

    def test_workflow(self):
        """Test the workflow engine"""
        self.ensure_one()
        if not self.active:
            raise UserError(_('Cannot test an inactive workflow.'))
        
        # Find a test admission file to process
        test_file = self.env['acmst.admission.file'].search([
            ('state', '=', self.from_state)
        ], limit=1)
        
        if not test_file:
            raise UserError(_('No admission files found in state "%s" to test this workflow.' % self.from_state))
        
        try:
            # Test the workflow
            self.process_workflow(test_file)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Test Successful'),
                    'message': _('Workflow "%s" processed successfully for file %s.' % (self.name, test_file.name)),
                    'type': 'success',
                }
            }
        except (ValidationError, UserError) as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Test Failed'),
                    'message': _('Validation error testing workflow "%s": %s' % (self.name, str(e))),
                    'type': 'danger',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Test Failed'),
                    'message': _('Unexpected error testing workflow "%s": %s' % (self.name, str(e))),
                    'type': 'danger',
                }
            }

    def process_workflow_batch(self):
        """Process all eligible admission files with this workflow"""
        self.ensure_one()
        if not self.active:
            raise UserError(_('Cannot process an inactive workflow.'))
        
        # Find all admission files in the from_state
        eligible_files = self.env['acmst.admission.file'].search([
            ('state', '=', self.from_state)
        ])
        
        if not eligible_files:
            raise UserError(_('No admission files found in state "%s" to process.' % self.from_state))
        
        processed_count = 0
        error_count = 0
        
        for file in eligible_files:
            try:
                self.process_workflow(file)
                processed_count += 1
            except (ValidationError, UserError) as e:
                error_count += 1
                _logger.error(f'Validation error processing file {file.name} with workflow {self.name}: {str(e)}')
            except Exception as e:
                error_count += 1
                _logger.error(f'Unexpected error processing file {file.name} with workflow {self.name}: {str(e)}')
        
        message = _('Workflow "%s" processed %d files successfully.' % (self.name, processed_count))
        if error_count > 0:
            message += _(' %d files had errors.' % error_count)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Workflow Processing Complete'),
                'message': message,
                'type': 'success' if error_count == 0 else 'warning',
            }
        }

    def action_view_rules(self):
        """Open workflow rules related to this workflow"""
        self.ensure_one()
        _logger.info(f"Viewing workflow rules for workflow engine {self.name}")
        return {
            'type': 'ir.actions.act_window',
            'name': _('Workflow Rules'),
            'res_model': 'acmst.workflow.rule',
            'view_mode': 'tree,form',
            'domain': [('workflow_engine_id', '=', self.id)],
            'context': {
                'default_workflow_engine_id': self.id,
            }
        }


class AcmstWorkflowRule(models.Model):
    _name = 'acmst.workflow.rule'
    _description = 'Workflow Rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    workflow_id = fields.Many2one(
        'acmst.workflow.engine',
        string='Workflow',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Name of the rule'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering rules'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this rule is active'
    )
    from_state = fields.Selection([
        ('new', 'New'),
        ('ministry_pending', 'Ministry Pending'),
        ('ministry_approved', 'Ministry Approved'),
        ('health_required', 'Health Required'),
        ('health_approved', 'Health Approved'),
        ('coordinator_review', 'Coordinator Review'),
        ('coordinator_approved', 'Coordinator Approved'),
        ('coordinator_conditional', 'Coordinator Conditional'),
        ('manager_review', 'Manager Review'),
        ('manager_approved', 'Manager Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='From State', required=True, help='Source state for the rule')
    
    to_state = fields.Selection([
        ('new', 'New'),
        ('ministry_pending', 'Ministry Pending'),
        ('ministry_approved', 'Ministry Approved'),
        ('health_required', 'Health Required'),
        ('health_approved', 'Health Approved'),
        ('coordinator_review', 'Coordinator Review'),
        ('coordinator_approved', 'Coordinator Approved'),
        ('coordinator_conditional', 'Coordinator Conditional'),
        ('manager_review', 'Manager Review'),
        ('manager_approved', 'Manager Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='To State', required=True, help='Target state for the rule')
    
    action_type = fields.Selection([
        ('transition', 'State Transition'),
        ('notification', 'Send Notification'),
        ('validation', 'Validate Conditions'),
        ('timeout', 'Timeout Transition')
    ], string='Action Type', required=True, help='Type of action to perform')
    
    condition_type = fields.Selection([
        ('always', 'Always'),
        ('time_based', 'Time Based'),
        ('field_based', 'Field Based'),
        ('custom', 'Custom Python')
    ], string='Condition Type', default='always', help='Type of condition to evaluate')
    
    condition_expression = fields.Text(
        string='Condition Expression',
        help='Python expression to evaluate (for custom conditions)'
    )
    
    timeout_hours = fields.Integer(
        string='Timeout Hours',
        default=24,
        help='Timeout in hours (for timeout rules)'
    )
    
    send_notification = fields.Boolean(
        string='Send Notification',
        default=True,
        help='Send email notification when rule is triggered'
    )
    
    notification_template_id = fields.Many2one(
        'mail.template',
        string='Notification Template',
        help='Email template to send'
    )
    
    error_message = fields.Text(
        string='Error Message',
        help='Error message to display when validation fails'
    )
    
    priority = fields.Integer(
        string='Priority',
        default=10,
        help='Priority for rule execution (lower number = higher priority)'
    )

    def evaluate_conditions(self, admission_file):
        """Evaluate conditions for the rule"""
        self.ensure_one()
        
        if self.condition_type == 'always':
            return True
        
        elif self.condition_type == 'time_based':
            return self._evaluate_time_based_condition(admission_file)
        
        elif self.condition_type == 'field_based':
            return self._evaluate_field_based_condition(admission_file)
        
        elif self.condition_type == 'custom':
            return self._evaluate_custom_condition(admission_file)
        
        return False

    def _evaluate_time_based_condition(self, admission_file):
        """Evaluate time-based conditions"""
        if self.action_type == 'timeout':
            timeout_date = fields.Datetime.now() - timedelta(hours=self.timeout_hours)
            return admission_file.write_date < timeout_date
        
        return False

    def _evaluate_field_based_condition(self, admission_file):
        """Evaluate field-based conditions"""
        # This would be implemented based on specific field requirements
        return True

    def _evaluate_custom_condition(self, admission_file):
        """Evaluate custom Python conditions"""
        if not self.condition_expression:
            return True
        
        try:
            # Create a safe evaluation context
            context = {
                'admission_file': admission_file,
                'fields': fields,
                'datetime': datetime,
                'date': date,
                'timedelta': timedelta,
            }
            
            return eval(self.condition_expression, context)
        except (ValidationError, UserError) as e:
            _logger.error(f'Validation error evaluating custom condition: {str(e)}')
            return False
        except Exception as e:
            _logger.error(f'Unexpected error evaluating custom condition: {str(e)}')
            return False

    def validate_conditions(self, admission_file):
        """Validate conditions for the rule"""
        self.ensure_one()
        
        if self.action_type != 'validation':
            return True
        
        return self.evaluate_conditions(admission_file)

    def send_notification_email(self, admission_file):
        """Send notification email"""
        self.ensure_one()

        if not self.send_notification or not self.notification_template_id:
            return

        try:
            # Check if there's an active mail server before sending
            mail_server = self.env['ir.mail_server'].search([('active', '=', True)], order='sequence', limit=1)
            if mail_server:
                self.notification_template_id.send_mail(admission_file.id, force_send=True)
                _logger.info(f'Notification sent for file {admission_file.name} using rule {self.name}')
            else:
                # Create pending email instead of skipping
                _logger.warning(f'No active mail server configured. Creating pending email for workflow notification.')
                self._create_pending_email(admission_file)
        except (ValidationError, UserError) as e:
            _logger.error(f'Validation error sending notification for file {admission_file.name}: {str(e)}')
            # Create pending email for failed attempts too
            self._create_pending_email(admission_file)
        except Exception as e:
            _logger.error(f'Unexpected error sending notification for file {admission_file.name}: {str(e)}')
            # Create pending email for failed attempts too
            self._create_pending_email(admission_file)

    def _create_pending_email(self, admission_file):
        """Create a pending email record for workflow notifications"""
        try:
            if self.notification_template_id:
                # Create pending email record
                self.env['acmst.pending.email'].create({
                    'template_ref': self.notification_template_id._name,
                    'record_id': admission_file.id,
                    'model_name': 'acmst.admission.file',
                    'record_name': admission_file.name or str(admission_file.id),
                    'priority': 'medium',
                    'retry_count': 0,
                    'max_retries': 3,
                    'created_by': self.env.user.id,
                })
                _logger.info(f'Created pending email for workflow notification on file {admission_file.name}')
        except (ValidationError, UserError) as e:
            _logger.error(f'Validation error creating pending email for workflow notification: {str(e)}')
        except Exception as e:
            _logger.error(f'Unexpected error creating pending email for workflow notification: {str(e)}')

    @api.constrains('from_state', 'to_state')
    def _check_state_transition(self):
        """Validate state transition"""
        for record in self:
            if record.from_state == record.to_state:
                raise ValidationError(_('From state and to state cannot be the same.'))
            
            # Add more validation rules as needed
            if record.from_state == 'completed' and record.to_state != 'cancelled':
                raise ValidationError(_('Cannot transition from completed state except to cancelled.'))
            
            if record.from_state == 'cancelled' and record.to_state != 'new':
                raise ValidationError(_('Cannot transition from cancelled state except to new.'))

    def action_test_rule(self):
        """Test the workflow rule"""
        self.ensure_one()
        if not self.active:
            raise UserError(_('Cannot test an inactive rule.'))

        _logger.info(f"Testing workflow rule {self.name} by {self.env.user.name}")

        # Find a test admission file to process
        test_file = self.env['acmst.admission.file'].search([
            ('state', '=', self.from_state)
        ], limit=1)

        if not test_file:
            _logger.warning(f"No admission files found in state '{self.from_state}' to test rule {self.name}")
            raise UserError(_('No admission files found in state "%s" to test this rule.' % self.from_state))
        
        try:
            # Test the rule conditions
            if self.evaluate_conditions(test_file):
                if self.action_type == 'state_change':
                    # Test state change
                    test_file.write({'state': self.to_state})
                    message = _('Rule "%s" test successful. File state changed to "%s".' % (self.name, self.to_state))
                elif self.action_type == 'notification':
                    # Test notification
                    self.send_notification_email(test_file)
                    message = _('Rule "%s" test successful. Notification sent.' % self.name)
                elif self.action_type == 'validation':
                    # Test validation
                    self.validate_conditions(test_file)
                    message = _('Rule "%s" test successful. Validation passed.' % self.name)
                else:
                    message = _('Rule "%s" test successful.' % self.name)
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Rule Test Successful'),
                        'message': message,
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Rule Test Failed'),
                        'message': _('Rule "%s" conditions were not met for the test file.' % self.name),
                        'type': 'warning',
                    }
                }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Rule Test Failed'),
                    'message': _('Error testing rule "%s": %s' % (self.name, str(e))),
                    'type': 'danger',
                }
            }