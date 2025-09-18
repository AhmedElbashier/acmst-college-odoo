# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AcmstProgram(models.Model):
    """Academic Program Management Model
    
    This model manages academic programs including:
    - Program details (name, code, description)
    - College and program type association
    - Personnel management (manager, coordinator)
    - Academic requirements and structure
    - Associated batches and students
    """
    _name = 'acmst.program'
    _description = 'Academic Program'
    _order = 'sequence, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Program Name',
        required=True,
        tracking=True,
        help="Official name of the academic program"
    )
    code = fields.Char(
        string='Program Code',
        required=True,
        size=15,
        tracking=True,
        help="Unique code for the program (max 15 characters)"
    )
    short_name = fields.Char(
        string='Short Name',
        size=50,
        help="Abbreviated name for display purposes"
    )
    
    # Associations
    college_id = fields.Many2one(
        'acmst.college',
        string='College',
        required=True,
        tracking=True,
        help="College this program belongs to"
    )
    university_id = fields.Many2one(
        related='college_id.university_id',
        string='University',
        store=True,
        readonly=True
    )
    program_type_id = fields.Many2one(
        'acmst.program.type',
        string='Program Type',
        required=True,
        tracking=True,
        help="Type of academic program"
    )
    
    # Personnel Management
    manager_id = fields.Many2one(
        'res.users',
        string='Program Manager',
        tracking=True,
        help="Program manager responsible for this program"
    )
    coordinator_id = fields.Many2one(
        'res.users',
        string='Program Coordinator',
        tracking=True,
        help="Program coordinator for this program"
    )
    
    # Academic Information
    description = fields.Text(
        string='Description',
        help="Detailed description of the program"
    )
    objectives = fields.Text(
        string='Program Objectives',
        help="Learning objectives of the program"
    )
    learning_outcomes = fields.Text(
        string='Learning Outcomes',
        help="Expected learning outcomes"
    )
    admission_requirements = fields.Text(
        string='Admission Requirements',
        help="Requirements for admission to this program"
    )
    
    # Academic Structure
    credits_required = fields.Integer(
        string='Credits Required',
        tracking=True,
        help="Total credits required to complete the program"
    )
    duration_years = fields.Float(
        string='Duration (Years)',
        digits=(3, 1),
        tracking=True,
        help="Program duration in years"
    )
    max_duration_years = fields.Float(
        string='Maximum Duration (Years)',
        digits=(3, 1),
        tracking=True,
        help="Maximum time allowed to complete the program"
    )
    
    # Program Settings
    is_thesis_required = fields.Boolean(
        string='Thesis Required',
        default=False,
        tracking=True,
        help="Whether a thesis is required for this program"
    )
    is_internship_required = fields.Boolean(
        string='Internship Required',
        default=False,
        tracking=True,
        help="Whether an internship is required for this program"
    )
    internship_credits = fields.Integer(
        string='Internship Credits',
        help="Credits awarded for internship"
    )
    thesis_credits = fields.Integer(
        string='Thesis Credits',
        help="Credits awarded for thesis"
    )
    
    # Status and Settings
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Uncheck to archive this program"
    )
    is_online = fields.Boolean(
        string='Online Program',
        default=False,
        tracking=True,
        help="Whether this is an online program"
    )
    is_part_time = fields.Boolean(
        string='Part-time Program',
        default=False,
        tracking=True,
        help="Whether this is a part-time program"
    )
    
    # Related Records
    batch_ids = fields.One2many(
        'acmst.batch',
        'program_id',
        string='Batches',
        help="Batches under this program"
    )
    batch_count = fields.Integer(
        string='Number of Batches',
        compute='_compute_batch_count',
        store=True
    )
    student_count = fields.Integer(
        string='Number of Students',
        compute='_compute_student_count',
        store=True
    )
    course_count = fields.Integer(
        string='Number of Courses',
        compute='_compute_course_count',
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
    
    # Computed Fields
    full_name = fields.Char(
        string='Full Name',
        compute='_compute_full_name',
        store=True
    )
    program_level = fields.Selection(
        related='program_type_id.level',
        string='Program Level',
        store=True,
        readonly=True
    )
    
    @api.depends('name', 'college_id.name', 'program_type_id.name')
    def _compute_full_name(self):
        """Compute the full name with college and type"""
        for record in self:
            name_parts = [record.name]
            if record.college_id:
                name_parts.append(f"({record.college_id.name})")
            if record.program_type_id:
                name_parts.append(f"- {record.program_type_id.name}")
            record.full_name = ' '.join(name_parts)
    
    @api.depends('batch_ids')
    def _compute_batch_count(self):
        """Compute the number of batches under this program"""
        for record in self:
            record.batch_count = len(record.batch_ids.filtered('active'))
    
    @api.depends('batch_ids')  # Will be updated when student module is available
    def _compute_student_count(self):
        """Compute the number of students under this program"""
        for record in self:
            # Placeholder - will be implemented when student module is available
            record.student_count = 0
    
    @api.depends('college_id', 'program_type_id')
    def _compute_course_count(self):
        """Compute the number of courses under this program"""
        # This will be implemented when course module is created
        for record in self:
            record.course_count = 0
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure program code is unique within college"""
        for record in self:
            if record.code and record.college_id:
                existing = self.search([
                    ('code', '=', record.code),
                    ('college_id', '=', record.college_id.id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("Program code '%s' already exists in %s. Please use a different code.") % 
                        (record.code, record.college_id.name)
                    )
    
    @api.constrains('credits_required')
    def _check_credits_required(self):
        """Validate credits required"""
        for record in self:
            if record.credits_required and record.credits_required <= 0:
                raise ValidationError(
                    _("Credits required must be greater than 0.")
                )
            if record.program_type_id:
                if record.program_type_id.min_credits and record.credits_required < record.program_type_id.min_credits:
                    raise ValidationError(
                        _("Credits required (%d) cannot be less than minimum credits for program type (%d).") % 
                        (record.credits_required, record.program_type_id.min_credits)
                    )
                if record.program_type_id.max_credits and record.credits_required > record.program_type_id.max_credits:
                    raise ValidationError(
                        _("Credits required (%d) cannot be more than maximum credits for program type (%d).") % 
                        (record.credits_required, record.program_type_id.max_credits)
                    )
    
    @api.constrains('duration_years', 'max_duration_years')
    def _check_duration(self):
        """Validate duration fields"""
        for record in self:
            if record.duration_years and record.duration_years <= 0:
                raise ValidationError(
                    _("Duration in years must be greater than 0.")
                )
            if record.max_duration_years and record.max_duration_years <= 0:
                raise ValidationError(
                    _("Maximum duration in years must be greater than 0.")
                )
            if record.duration_years and record.max_duration_years:
                if record.duration_years > record.max_duration_years:
                    raise ValidationError(
                        _("Duration cannot be greater than maximum duration.")
                    )
    
    @api.constrains('internship_credits', 'thesis_credits')
    def _check_special_credits(self):
        """Validate special credits"""
        for record in self:
            if record.internship_credits and record.internship_credits < 0:
                raise ValidationError(
                    _("Internship credits cannot be negative.")
                )
            if record.thesis_credits and record.thesis_credits < 0:
                raise ValidationError(
                    _("Thesis credits cannot be negative.")
                )
            if record.internship_credits and record.credits_required:
                if record.internship_credits > record.credits_required:
                    raise ValidationError(
                        _("Internship credits cannot be greater than total credits required.")
                    )
            if record.thesis_credits and record.credits_required:
                if record.thesis_credits > record.credits_required:
                    raise ValidationError(
                        _("Thesis credits cannot be greater than total credits required.")
                    )
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and validate"""
        if 'sequence' not in vals:
            vals['sequence'] = self._get_next_sequence(vals.get('college_id'))
        return super().create(vals)
    
    def _get_next_sequence(self, college_id=None):
        """Get next sequence number for the college"""
        domain = []
        if college_id:
            domain.append(('college_id', '=', college_id))
        last_record = self.search(domain, order='sequence desc', limit=1)
        return (last_record.sequence or 0) + 10
    
    def name_get(self):
        """Custom name_get to show code and name"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.college_id:
                name = f"{name} - {record.college_id.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        """Custom name search to include code and college"""
        args = args or []
        if name:
            domain = [
                '|', '|', '|',
                ('name', operator, name),
                ('code', operator, name),
                ('short_name', operator, name),
                ('college_id.name', operator, name)
            ]
            return self.search(domain + args, limit=limit).name_get()
        return super()._name_search(name, args, operator, limit)
    
    def action_view_batches(self):
        """Action to view batches under this program"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_batch')
        action['domain'] = [('program_id', '=', self.id)]
        action['context'] = {
            'default_program_id': self.id,
            'search_default_program_id': self.id,
        }
        return action
    
    def action_view_students(self):
        """Action to view students under this program"""
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
    
    def action_view_courses(self):
        """Action to view courses under this program"""
        # This will be implemented when course module is created
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Information'),
                'message': _('Course management module not yet implemented.'),
                'type': 'info',
            }
        }
    
    def toggle_active(self):
        """Override toggle_active to handle related records"""
        for record in self:
            if not record.active:
                # Archive related batches
                record.batch_ids.write({'active': False})
        return super().toggle_active()
    
    def _get_related_batches(self):
        """Get all active batches under this program"""
        return self.batch_ids.filtered('active')
    
    def _get_related_students(self):
        """Get all students under this program"""
        return self.env['acmst.student'].search([
            ('batch_id.program_id', '=', self.id),
            ('active', '=', True)
        ])
    
    def _get_related_courses(self):
        """Get all courses under this program"""
        # This will be implemented when course module is created
        return self.env['acmst.course'].browse([])
    
    @api.model
    def get_programs_by_college(self, college_id):
        """Get all programs for a specific college"""
        return self.search([
            ('college_id', '=', college_id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_programs_by_type(self, program_type_id):
        """Get all programs of a specific type"""
        return self.search([
            ('program_type_id', '=', program_type_id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_programs_by_university(self, university_id):
        """Get all programs for a specific university"""
        return self.search([
            ('college_id.university_id', '=', university_id),
            ('active', '=', True)
        ])
