# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AcmstCollege(models.Model):
    """College/Department Management Model
    
    This model manages college/department information including:
    - Basic college details (name, code, description)
    - University association
    - Personnel management (Dean, staff)
    - Associated programs and students
    - Contact information and location
    """
    _name = 'acmst.college'
    _description = 'College/Department'
    _order = 'sequence, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string=_('College Name'),
        required=True,
        tracking=True,
        help=_("Official name of the college/department")
    )
    code = fields.Char(
        string=_('College Code'),
        required=True,
        size=10,
        tracking=True,
        help=_("Unique code for the college (max 10 characters)")
    )
    short_name = fields.Char(
        string=_('Short Name'),
        size=50,
        help=_("Abbreviated name for display purposes")
    )
    
    # University Association
    university_id = fields.Many2one(
        'acmst.university',
        string='University',
        required=True,
        tracking=True,
        help="University this college belongs to"
    )
    university_name = fields.Char(
        related='university_id.name',
        string='University Name',
        store=True,
        readonly=True
    )
    university_code = fields.Char(
        related='university_id.code',
        string='University Code',
        store=True,
        readonly=True
    )
    
    # Personnel Management
    dean_id = fields.Many2one(
        'res.users',
        string='Dean',
        tracking=True,
        help="Dean of the college"
    )
    dean_name = fields.Char(
        related='dean_id.name',
        string='Dean Name',
        store=True,
        readonly=True
    )
    dean_email = fields.Char(
        related='dean_id.email',
        string='Dean Email',
        store=True,
        readonly=True
    )
    
    # Contact Information
    address = fields.Text(
        string='Address',
        tracking=True,
        help="College address"
    )
    phone = fields.Char(
        string='Phone',
        size=20,
        tracking=True,
        help="Main contact phone number"
    )
    email = fields.Char(
        string='Email',
        size=100,
        tracking=True,
        help="Main contact email address"
    )
    website = fields.Char(
        string='Website',
        size=200,
        tracking=True,
        help="College website URL"
    )
    
    # Academic Information
    established_year = fields.Integer(
        string='Established Year',
        tracking=True,
        help="Year the college was established"
    )
    accreditation = fields.Text(
        string='Accreditation',
        help="Accreditation details and certifications"
    )
    description = fields.Text(
        string='Description',
        help="Detailed description of the college"
    )
    mission = fields.Text(
        string='Mission Statement',
        help="College mission statement"
    )
    vision = fields.Text(
        string='Vision Statement',
        help="College vision statement"
    )
    
    # Academic Structure
    program_types = fields.Selection([
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('both', 'Both Undergraduate and Graduate'),
        ('other', 'Other')
    ], string='Program Types', default='both', tracking=True)
    
    # Status and Settings
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Uncheck to archive this college"
    )
    is_main = fields.Boolean(
        string='Main College',
        default=False,
        help="Mark as the main college in the university"
    )
    
    # Related Records
    program_ids = fields.One2many(
        'acmst.program',
        'college_id',
        string='Programs',
        help="Programs under this college"
    )
    program_count = fields.Integer(
        string='Number of Programs',
        compute='_compute_program_count',
        store=True
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
    faculty_count = fields.Integer(
        string='Number of Faculty',
        compute='_compute_faculty_count',
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
    
    @api.depends('name', 'university_id.name')
    def _compute_full_name(self):
        """Compute the full name with university"""
        for record in self:
            if record.university_id:
                record.full_name = f"{record.name} - {record.university_id.name}"
            else:
                record.full_name = record.name
    
    @api.depends('program_ids')
    def _compute_program_count(self):
        """Compute the number of programs under this college"""
        for record in self:
            record.program_count = len(record.program_ids.filtered('active'))
    
    @api.depends('program_ids.batch_ids')
    def _compute_batch_count(self):
        """Compute the number of batches under this college"""
        for record in self:
            batches = self.env['acmst.batch'].search([
                ('program_id.college_id', '=', record.id),
                ('active', '=', True)
            ])
            record.batch_count = len(batches)
    
    @api.depends('program_ids.batch_ids')  # Will be updated when student module is available
    def _compute_student_count(self):
        """Compute the number of students under this college"""
        for record in self:
            # Placeholder - will be implemented when student module is available
            record.student_count = 0
    
    @api.depends('program_ids.manager_id', 'program_ids.coordinator_id')
    def _compute_faculty_count(self):
        """Compute the number of faculty under this college"""
        for record in self:
            faculty_ids = set()
            for program in record.program_ids:
                if program.manager_id:
                    faculty_ids.add(program.manager_id.id)
                if program.coordinator_id:
                    faculty_ids.add(program.coordinator_id.id)
            record.faculty_count = len(faculty_ids)
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure college code is unique within university"""
        for record in self:
            if record.code and record.university_id:
                existing = self.search([
                    ('code', '=', record.code),
                    ('university_id', '=', record.university_id.id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("College code '%s' already exists in %s. Please use a different code.") % 
                        (record.code, record.university_id.name)
                    )
    
    @api.constrains('is_main')
    def _check_main_college(self):
        """Ensure only one main college exists per university"""
        for record in self:
            if record.is_main and record.university_id:
                existing_main = self.search([
                    ('is_main', '=', True),
                    ('university_id', '=', record.university_id.id),
                    ('id', '!=', record.id)
                ])
                if existing_main:
                    raise ValidationError(
                        _("Only one college can be marked as main per university. "
                          "Please uncheck the main status of '%s' first.") % existing_main.name
                    )
    
    @api.constrains('established_year')
    def _check_established_year(self):
        """Validate established year"""
        for record in self:
            if record.established_year:
                current_year = fields.Date.today().year
                if record.established_year > current_year:
                    raise ValidationError(
                        _("Established year cannot be in the future.")
                    )
                if record.established_year < 1800:
                    raise ValidationError(
                        _("Established year seems too old. Please verify the year.")
                    )
                if record.university_id and record.university_id.established_year:
                    if record.established_year < record.university_id.established_year:
                        raise ValidationError(
                            _("College cannot be established before its university.")
                        )
    
    @api.constrains('email')
    def _check_email_format(self):
        """Validate email format"""
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(
                    _("Please enter a valid email address.")
                )
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and validate"""
        if 'sequence' not in vals:
            vals['sequence'] = self._get_next_sequence(vals.get('university_id'))
        return super().create(vals)
    
    def _get_next_sequence(self, university_id=None):
        """Get next sequence number for the university"""
        domain = []
        if university_id:
            domain.append(('university_id', '=', university_id))
        last_record = self.search(domain, order='sequence desc', limit=1)
        return (last_record.sequence or 0) + 10
    
    def write(self, vals):
        """Override write to handle main college changes"""
        if 'is_main' in vals and vals['is_main']:
            # Unset other main colleges in the same university
            for record in self:
                if record.university_id:
                    self.search([
                        ('is_main', '=', True),
                        ('university_id', '=', record.university_id.id),
                        ('id', '!=', record.id)
                    ]).write({'is_main': False})
        return super().write(vals)
    
    def name_get(self):
        """Custom name_get to show code and name"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.university_id:
                name = f"{name} - {record.university_id.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        """Custom name search to include code and university"""
        args = args or []
        if name:
            domain = [
                '|', '|', '|',
                ('name', operator, name),
                ('code', operator, name),
                ('short_name', operator, name),
                ('university_id.name', operator, name)
            ]
            return self.search(domain + args, limit=limit).name_get()
        return super()._name_search(name, args, operator, limit)
    
    def action_view_programs(self):
        """Action to view programs under this college"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_program')
        action['domain'] = [('college_id', '=', self.id)]
        action['context'] = {
            'default_college_id': self.id,
            'search_default_college_id': self.id,
        }
        return action
    
    def action_view_batches(self):
        """Action to view batches under this college"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_batch')
        action['domain'] = [('program_id.college_id', '=', self.id)]
        action['context'] = {
            'search_default_college_id': self.id,
        }
        return action
    
    def action_view_students(self):
        """Action to view students under this college"""
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
    
    def action_view_faculty(self):
        """Action to view faculty under this college"""
        # This will be implemented when faculty module is created
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Information'),
                'message': _('Faculty management module not yet implemented.'),
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
        """Get all active programs under this college"""
        return self.program_ids.filtered('active')
    
    def _get_related_batches(self):
        """Get all active batches under this college"""
        return self.env['acmst.batch'].search([
            ('program_id.college_id', '=', self.id),
            ('active', '=', True)
        ])
    
    def _get_related_students(self):
        """Get all active students under this college"""
        return self.env['acmst.student'].search([
            ('batch_id.program_id.college_id', '=', self.id),
            ('active', '=', True)
        ])
    
    def _get_related_faculty(self):
        """Get all faculty associated with this college"""
        faculty_ids = set()
        for program in self.program_ids:
            if program.manager_id:
                faculty_ids.add(program.manager_id.id)
            if program.coordinator_id:
                faculty_ids.add(program.coordinator_id.id)
        return self.env['res.users'].browse(list(faculty_ids))
    
    @api.model
    def get_colleges_by_university(self, university_id):
        """Get all colleges for a specific university"""
        return self.search([
            ('university_id', '=', university_id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_main_college(self, university_id):
        """Get the main college for a specific university"""
        return self.search([
            ('university_id', '=', university_id),
            ('is_main', '=', True),
            ('active', '=', True)
        ], limit=1)
