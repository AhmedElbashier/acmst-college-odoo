# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AcmstProgramType(models.Model):
    """Program Type Management Model
    
    This model manages different types of academic programs including:
    - Diploma programs
    - Bachelor's degree programs
    - Master's degree programs
    - PhD programs
    - Certificate programs
    """
    _name = 'acmst.program.type'
    _description = 'Program Type'
    _order = 'sequence, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Program Type',
        required=True,
        tracking=True,
        help="Name of the program type (e.g., Bachelor's Degree, Master's Degree)"
    )
    code = fields.Char(
        string='Code',
        required=True,
        size=10,
        tracking=True,
        help="Unique code for the program type (max 10 characters)"
    )
    short_name = fields.Char(
        string='Short Name',
        size=20,
        help="Abbreviated name for display purposes"
    )
    
    # Academic Information
    level = fields.Selection([
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD/Doctorate'),
        ('postgraduate', 'Postgraduate Diploma'),
        ('other', 'Other')
    ], string='Academic Level', required=True, default='bachelor', tracking=True)
    
    duration_years = fields.Float(
        string='Duration (Years)',
        digits=(3, 1),
        tracking=True,
        help="Typical duration of programs of this type in years"
    )
    duration_months = fields.Integer(
        string='Duration (Months)',
        tracking=True,
        help="Typical duration of programs of this type in months"
    )
    min_credits = fields.Integer(
        string='Minimum Credits',
        tracking=True,
        help="Minimum credits required for programs of this type"
    )
    max_credits = fields.Integer(
        string='Maximum Credits',
        tracking=True,
        help="Maximum credits allowed for programs of this type"
    )
    
    # Description and Requirements
    description = fields.Text(
        string='Description',
        help="Detailed description of this program type"
    )
    requirements = fields.Text(
        string='General Requirements',
        help="General requirements for programs of this type"
    )
    learning_outcomes = fields.Text(
        string='Learning Outcomes',
        help="Expected learning outcomes for programs of this type"
    )
    
    # Status and Settings
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Uncheck to archive this program type"
    )
    is_degree = fields.Boolean(
        string='Degree Program',
        default=True,
        help="Whether this program type awards a degree"
    )
    requires_thesis = fields.Boolean(
        string='Requires Thesis',
        default=False,
        help="Whether programs of this type typically require a thesis"
    )
    requires_internship = fields.Boolean(
        string='Requires Internship',
        default=False,
        help="Whether programs of this type typically require an internship"
    )
    
    # Related Records
    program_ids = fields.One2many(
        'acmst.program',
        'program_type_id',
        string='Programs',
        help="Programs of this type"
    )
    program_count = fields.Integer(
        string='Number of Programs',
        compute='_compute_program_count',
        store=True
    )
    student_count = fields.Integer(
        string='Number of Students',
        compute='_compute_student_count',
        store=True
    )
    
    # System Fields
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of display"
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help="Color for kanban view"
    )
    
    @api.depends('program_ids')
    def _compute_program_count(self):
        """Compute the number of programs of this type"""
        for record in self:
            record.program_count = len(record.program_ids.filtered('active'))
    
    @api.depends('program_ids.batch_ids')  # Will be updated when student module is available
    def _compute_student_count(self):
        """Compute the number of students in programs of this type"""
        for record in self:
            # Placeholder - will be implemented when student module is available
            record.student_count = 0
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure program type code is unique"""
        for record in self:
            if record.code:
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("Program type code '%s' already exists. Please use a different code.") % record.code
                    )
    
    @api.constrains('duration_years', 'duration_months')
    def _check_duration(self):
        """Validate duration fields"""
        for record in self:
            if record.duration_years and record.duration_years <= 0:
                raise ValidationError(
                    _("Duration in years must be greater than 0.")
                )
            if record.duration_months and record.duration_months <= 0:
                raise ValidationError(
                    _("Duration in months must be greater than 0.")
                )
            if record.duration_years and record.duration_months:
                # Check if they are consistent (within 10% tolerance)
                years_to_months = record.duration_years * 12
                if abs(years_to_months - record.duration_months) > years_to_months * 0.1:
                    raise ValidationError(
                        _("Duration in years and months should be consistent.")
                    )
    
    @api.constrains('min_credits', 'max_credits')
    def _check_credits(self):
        """Validate credit requirements"""
        for record in self:
            if record.min_credits and record.min_credits <= 0:
                raise ValidationError(
                    _("Minimum credits must be greater than 0.")
                )
            if record.max_credits and record.max_credits <= 0:
                raise ValidationError(
                    _("Maximum credits must be greater than 0.")
                )
            if record.min_credits and record.max_credits:
                if record.min_credits > record.max_credits:
                    raise ValidationError(
                        _("Minimum credits cannot be greater than maximum credits.")
                    )
    
    @api.model
    def create(self, vals):
        """Override create to set sequence"""
        if 'sequence' not in vals:
            vals['sequence'] = self._get_next_sequence()
        return super().create(vals)
    
    def _get_next_sequence(self):
        """Get next sequence number"""
        last_record = self.search([], order='sequence desc', limit=1)
        return (last_record.sequence or 0) + 10
    
    def name_get(self):
        """Custom name_get to show code and name"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        """Custom name search to include code"""
        args = args or []
        if name:
            domain = [
                '|', '|',
                ('name', operator, name),
                ('code', operator, name),
                ('short_name', operator, name)
            ]
            return self.search(domain + args, limit=limit).name_get()
        return super()._name_search(name, args, operator, limit)
    
    def action_view_programs(self):
        """Action to view programs of this type"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_program')
        action['domain'] = [('program_type_id', '=', self.id)]
        action['context'] = {
            'default_program_type_id': self.id,
            'search_default_program_type_id': self.id,
        }
        return action
    
    def action_view_students(self):
        """Action to view students in programs of this type"""
        # This will be implemented when student module is created
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Information'),
                'message': _('Student management module not yet implemented.'),
                'type': 'info',
            }
        }
    
    def toggle_active(self):
        """Override toggle_active to handle related records"""
        for record in self:
            if not record.active:
                # Archive related programs
                record.program_ids.write({'active': False})
        return super().toggle_active()
    
    def _get_related_programs(self):
        """Get all active programs of this type"""
        return self.program_ids.filtered('active')
    
    def _get_related_students(self):
        """Get all students in programs of this type"""
        return self.env['acmst.student'].search([
            ('batch_id.program_id.program_type_id', '=', self.id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_program_types_by_level(self, level):
        """Get all program types for a specific academic level"""
        return self.search([
            ('level', '=', level),
            ('active', '=', True)
        ])
    
    @api.model
    def get_degree_program_types(self):
        """Get all degree program types"""
        return self.search([
            ('is_degree', '=', True),
            ('active', '=', True)
        ])
    
    @api.model
    def get_certificate_program_types(self):
        """Get all certificate program types"""
        return self.search([
            ('is_degree', '=', False),
            ('active', '=', True)
        ])
