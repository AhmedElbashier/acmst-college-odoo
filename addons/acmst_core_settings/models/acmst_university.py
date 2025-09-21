# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AcmstUniversity(models.Model):
    """University/Institution Management Model
    
    This model manages university/institution information including:
    - Basic university details (name, code, contact info)
    - Logo and branding
    - Address and location information
    - Associated colleges and programs
    - Active status and validation
    """
    _name = 'acmst.university'
    _description = 'University/Institution'
    _order = 'name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string=_('University Name'),
        required=True,
        tracking=True,
        help=_("Official name of the university/institution")
    )
    code = fields.Char(
        string=_('University Code'),
        required=True,
        size=10,
        tracking=True,
        help=_("Unique code for the university (max 10 characters)")
    )
    short_name = fields.Char(
        string=_('Short Name'),
        size=50,
        help=_("Abbreviated name for display purposes")
    )
    
    # Contact Information
    address = fields.Text(
        string=_('Address'),
        tracking=True,
        help=_("Complete address of the university")
    )
    city = fields.Char(
        string=_('City'),
        size=100,
        tracking=True
    )
    state_id = fields.Many2one(
        'res.country.state',
        string=_('State/Province'),
        tracking=True
    )
    country_id = fields.Many2one(
        'res.country',
        string=_('Country'),
        default=lambda self: self.env.company.country_id,
        tracking=True
    )
    zip = fields.Char(
        string=_('ZIP Code'),
        size=20,
        tracking=True
    )
    
    # Contact Details
    phone = fields.Char(
        string=_('Phone'),
        size=20,
        tracking=True,
        help=_("Main contact phone number")
    )
    mobile = fields.Char(
        string=_('Mobile'),
        size=20,
        tracking=True
    )
    email = fields.Char(
        string=_('Email'),
        size=100,
        tracking=True,
        help=_("Main contact email address")
    )
    website = fields.Char(
        string=_('Website'),
        size=200,
        tracking=True,
        help=_("Official website URL")
    )
    
    # Branding
    logo = fields.Binary(
        string=_('Logo'),
        attachment=True,
        help=_("University logo image")
    )
    logo_web = fields.Binary(
        string=_('Web Logo'),
        attachment=True,
        help=_("Logo optimized for web display")
    )
    
    # Academic Information
    established_year = fields.Integer(
        string=_('Established Year'),
        tracking=True,
        help=_("Year the university was established")
    )
    accreditation = fields.Text(
        string=_('Accreditation'),
        help=_("Accreditation details and certifications")
    )
    description = fields.Text(
        string=_('Description'),
        help=_("Detailed description of the university")
    )
    
    # Status and Settings
    active = fields.Boolean(
        string=_('Active'),
        default=True,
        tracking=True,
        help=_("Uncheck to archive this university")
    )
    is_main = fields.Boolean(
        string=_('Main University'),
        default=False,
        help=_("Mark as the main university in the system")
    )
    
    # Related Records
    college_ids = fields.One2many(
        'acmst.college',
        'university_id',
        string=_('Colleges'),
        help=_("Colleges under this university")
    )
    college_count = fields.Integer(
        string=_('Number of Colleges'),
        compute='_compute_college_count',
        store=True
    )
    program_count = fields.Integer(
        string=_('Number of Programs'),
        compute='_compute_program_count',
        store=True
    )
    student_count = fields.Integer(
        string=_('Number of Students'),
        compute='_compute_student_count',
        store=True
    )
    
    # System Fields
    sequence = fields.Integer(
        string=_('Sequence'),
        default=10,
        help=_("Order of display")
    )
    color = fields.Integer(
        string=_('Color'),
        default=0,
        help=_("Color for kanban view")
    )
    
    # Computed Fields
    full_address = fields.Text(
        string=_('Full Address'),
        compute='_compute_full_address',
        store=True
    )
    
    @api.depends('college_ids')
    def _compute_college_count(self):
        """Compute the number of colleges under this university"""
        for record in self:
            record.college_count = len(record.college_ids.filtered('active'))
    
    @api.depends('college_ids.program_ids')
    def _compute_program_count(self):
        """Compute the number of programs under this university"""
        for record in self:
            programs = self.env['acmst.program'].search([
                ('college_id.university_id', '=', record.id),
                ('active', '=', True)
            ])
            record.program_count = len(programs)
    
    @api.depends('college_ids.program_ids.batch_ids')  # Will be updated when student module is available
    def _compute_student_count(self):
        """Compute the number of students under this university"""
        for record in self:
            # Placeholder - will be implemented when student module is available
            record.student_count = 0
    
    @api.depends('address', 'city', 'state_id', 'country_id', 'zip')
    def _compute_full_address(self):
        """Compute the complete address string"""
        for record in self:
            address_parts = []
            if record.address:
                address_parts.append(record.address)
            if record.city:
                address_parts.append(record.city)
            if record.state_id:
                address_parts.append(record.state_id.name)
            if record.country_id:
                address_parts.append(record.country_id.name)
            if record.zip:
                address_parts.append(record.zip)
            record.full_address = ', '.join(address_parts)
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure university code is unique"""
        for record in self:
            if record.code:
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("University code '%s' already exists. Please use a different code.") % record.code
                    )
    
    @api.constrains('is_main')
    def _check_main_university(self):
        """Ensure only one main university exists"""
        for record in self:
            if record.is_main:
                existing_main = self.search([
                    ('is_main', '=', True),
                    ('id', '!=', record.id)
                ])
                if existing_main:
                    raise ValidationError(
                        _("Only one university can be marked as main. "
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
            vals['sequence'] = self._get_next_sequence()
        return super().create(vals)
    
    def _get_next_sequence(self):
        """Get next sequence number"""
        last_record = self.search([], order='sequence desc', limit=1)
        return (last_record.sequence or 0) + 10
    
    def write(self, vals):
        """Override write to handle main university changes"""
        if 'is_main' in vals and vals['is_main']:
            # Unset other main universities
            self.search([('is_main', '=', True)]).write({'is_main': False})
        return super().write(vals)
    
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
    
    def action_view_colleges(self):
        """Action to view colleges under this university"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_college')
        action['domain'] = [('university_id', '=', self.id)]
        action['context'] = {
            'default_university_id': self.id,
            'search_default_university_id': self.id,
        }
        return action
    
    def action_view_programs(self):
        """Action to view programs under this university"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_program')
        action['domain'] = [('college_id.university_id', '=', self.id)]
        action['context'] = {
            'search_default_university_id': self.id,
        }
        return action
    
    def action_view_students(self):
        """Action to view students under this university"""
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
                # Archive related colleges
                record.college_ids.write({'active': False})
        return super().toggle_active()
    
    @api.model
    def get_main_university(self):
        """Get the main university"""
        return self.search([('is_main', '=', True)], limit=1)
    
    def _get_related_colleges(self):
        """Get all active colleges under this university"""
        return self.college_ids.filtered('active')
    
    def _get_related_programs(self):
        """Get all active programs under this university"""
        return self.env['acmst.program'].search([
            ('college_id.university_id', '=', self.id),
            ('active', '=', True)
        ])
    
    def _get_related_batches(self):
        """Get all active batches under this university"""
        return self.env['acmst.batch'].search([
            ('program_id.college_id.university_id', '=', self.id),
            ('active', '=', True)
        ])
