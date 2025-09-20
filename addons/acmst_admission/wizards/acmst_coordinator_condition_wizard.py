# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class AcmstCoordinatorConditionWizard(models.TransientModel):
    _name = 'acmst.coordinator.condition.wizard'
    _description = 'Coordinator Condition Wizard'

    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        required=True,
        help='Admission file to create conditions for'
    )
    coordinator_id = fields.Many2one(
        'res.users',
        string='Coordinator',
        required=True,
        default=lambda self: self.env.user,
        help='Coordinator who will manage these conditions'
    )
    condition_lines = fields.One2many(
        'acmst.coordinator.condition.wizard.line',
        'wizard_id',
        string='Conditions',
        help='Conditions to create'
    )
    send_notification = fields.Boolean(
        string='Send Notification',
        default=True,
        help='Send email notification to applicant'
    )
    recommended_level_by_coordinator = fields.Selection([
        ('level2', 'Level 2'),
        ('level3', 'Level 3')
    ], string='Recommended Academic Level', required=True, default='level2', 
       help='Academic level recommended by coordinator for this admission file')

    @api.model
    def default_get(self, fields_list):
        """Set default values"""
        defaults = super().default_get(fields_list)
        
        # Add default condition line
        if 'condition_lines' in fields_list:
            defaults['condition_lines'] = [(0, 0, {
                'subject_name': '',
                'subject_code': '',
                'description': '',
                'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
            })]
        
        return defaults

    def action_add_math_condition(self):
        """Add a mathematics condition"""
        self.ensure_one()
        self._add_condition_line('Mathematics', 'MATH101', 'level2', 
                               'Complete Mathematics course with grade B or higher')
        return {'type': 'ir.actions.do_nothing'}

    def action_add_physics_condition(self):
        """Add a physics condition"""
        self.ensure_one()
        self._add_condition_line('Physics', 'PHYS201', 'level2', 
                               'Complete Physics course with grade B or higher')
        return {'type': 'ir.actions.do_nothing'}

    def action_add_chemistry_condition(self):
        """Add a chemistry condition"""
        self.ensure_one()
        self._add_condition_line('Chemistry', 'CHEM101', 'level2', 
                               'Complete Chemistry course with grade B or higher')
        return {'type': 'ir.actions.do_nothing'}

    def action_add_english_condition(self):
        """Add an English condition"""
        self.ensure_one()
        self._add_condition_line('English', 'ENG101', 'level2', 
                               'Complete English language course with grade B or higher')
        return {'type': 'ir.actions.do_nothing'}

    def _add_condition_line(self, subject_name, subject_code, level, description):
        """Add a condition line to the wizard"""
        self.ensure_one()
        
        # Create new condition line
        line_vals = {
            'wizard_id': self.id,
            'subject_name': subject_name,
            'subject_code': subject_code,
            'level': level,
            'description': description,
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Auto-generated condition - please review and modify as needed'
        }
        
        self.env['acmst.coordinator.condition.wizard.line'].create(line_vals)

    def action_create_conditions(self):
        """Create conditions from wizard"""
        self.ensure_one()
        
        # Validate required fields
        if not self.admission_file_id:
            raise UserError(_('Please select an admission file.'))
        
        if not self.coordinator_id:
            raise UserError(_('Please select a coordinator.'))
        
        if not self.condition_lines:
            raise UserError(_('Please add at least one condition before creating.'))
        
        # Validate condition lines
        for line in self.condition_lines:
            if not line.subject_name or not line.description:
                raise UserError(_('Please fill in all required fields (Subject Name and Description) for all conditions.'))
            
            if not line.deadline:
                raise UserError(_('Please set a deadline for all conditions.'))
            
            if line.deadline < date.today():
                raise UserError(_('Deadline cannot be in the past. Please check the deadline for: %s') % line.subject_name)
        
        created_conditions = []
        
        try:
            for line in self.condition_lines:
                condition_vals = {
                    'admission_file_id': self.admission_file_id.id,
                    'coordinator_id': self.coordinator_id.id,
                    'subject_name': line.subject_name.strip(),
                    'subject_code': line.subject_code.strip() if line.subject_code else '',
                    'level': getattr(self, 'recommended_level_by_coordinator', 'level2') or 'level2',  # Use recommended level for all conditions
                    'description': line.description.strip(),
                    'deadline': line.deadline,
                    'notes': line.notes.strip() if line.notes else '',
                }
                
                condition = self.env['acmst.coordinator.condition'].create(condition_vals)
                created_conditions.append(condition)
            
            # Send notification if requested
            if self.send_notification and created_conditions:
                try:
                    self.admission_file_id.send_conditions_notification()
                except Exception as e:
                    _logger.warning(f'Failed to send notification: {str(e)}')
            
            # Update admission file state to coordinator_conditional and then to manager_review
            self.admission_file_id.write({
                'state': 'coordinator_conditional',
                'coordinator_approval_date': fields.Date.today(),
                'coordinator_id': self.coordinator_id.id,
                'coordinator_recommended_level': getattr(self, 'recommended_level_by_coordinator', 'level2') or 'level2'  # Store the coordinator's recommended level
            })
            
            # Automatically move to manager review
            self.admission_file_id.action_manager_review()
            
            # Show success message and close wizard
            message = _('Successfully created %d condition(s) for %s. Application moved to Manager Review.') % (
                len(created_conditions), 
                self.admission_file_id.applicant_name or self.admission_file_id.name
            )
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Admission File'),
                'res_model': 'acmst.admission.file',
                'res_id': self.admission_file_id.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_id': self.admission_file_id.id,
                }
            }
            
        except Exception as e:
            _logger.error(f'Error creating conditions: {str(e)}')
            raise UserError(_('An error occurred while creating conditions: %s') % str(e))


class AcmstCoordinatorConditionWizardLine(models.TransientModel):
    _name = 'acmst.coordinator.condition.wizard.line'
    _description = 'Coordinator Condition Wizard Line'

    wizard_id = fields.Many2one(
        'acmst.coordinator.condition.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    subject_name = fields.Char(
        string='Subject Name',
        required=True,
        help='Name of the subject to complete'
    )
    subject_code = fields.Char(
        string='Subject Code',
        help='Code of the subject'
    )
    # Level is now handled at the wizard level, not per condition line
    description = fields.Text(
        string='Description',
        required=True,
        help='Detailed description of the condition'
    )
    deadline = fields.Date(
        string='Deadline',
        required=True,
        help='Deadline for completing the condition'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the condition'
    )

    @api.constrains('deadline', 'subject_name', 'description')
    def _check_required_fields(self):
        """Validate required fields and deadline"""
        for record in self:
            if record.deadline and record.deadline < date.today():
                raise ValidationError(_('Deadline cannot be in the past.'))
            
            if record.subject_name and len(record.subject_name.strip()) < 3:
                raise ValidationError(_('Subject name must be at least 3 characters long.'))
            

    @api.onchange('subject_name')
    def _onchange_subject_name(self):
        """Auto-suggest subject code based on subject name"""
        if self.subject_name and not self.subject_code:
            # Simple auto-suggestion logic
            subject = self.subject_name.strip().lower()
            if 'math' in subject:
                self.subject_code = 'MATH101'
            elif 'physics' in subject:
                self.subject_code = 'PHYS201'
            elif 'chemistry' in subject:
                self.subject_code = 'CHEM101'
            elif 'english' in subject:
                self.subject_code = 'ENG101'
            elif 'biology' in subject:
                self.subject_code = 'BIO101'
            elif 'computer' in subject or 'programming' in subject:
                self.subject_code = 'CS101'

    # Level onchange removed - level is now handled at wizard level
