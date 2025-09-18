# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AcmstAcademicYear(models.Model):
    """Academic Year Management Model
    
    This model manages academic years including:
    - Academic year details (name, code, dates)
    - Semester management
    - Batch associations
    - Academic calendar events
    """
    _name = 'acmst.academic.year'
    _description = 'Academic Year'
    _order = 'start_date desc, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Academic Year',
        required=True,
        tracking=True,
        help="Name of the academic year (e.g., 2024-2025)"
    )
    code = fields.Char(
        string='Code',
        required=True,
        size=10,
        tracking=True,
        help="Unique code for the academic year (max 10 characters)"
    )
    short_name = fields.Char(
        string='Short Name',
        size=20,
        help="Abbreviated name for display purposes"
    )
    
    # Dates
    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
        help="Academic year start date"
    )
    end_date = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
        help="Academic year end date"
    )
    
    # Status and Settings
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Uncheck to archive this academic year"
    )
    is_current = fields.Boolean(
        string='Current Year',
        default=False,
        tracking=True,
        help="Mark as the current academic year"
    )
    is_future = fields.Boolean(
        string='Future Year',
        compute='_compute_is_future',
        store=True,
        help="Whether this is a future academic year"
    )
    is_past = fields.Boolean(
        string='Past Year',
        compute='_compute_is_past',
        store=True,
        help="Whether this is a past academic year"
    )
    
    # Academic Structure
    semester_count = fields.Integer(
        string='Number of Semesters',
        default=2,
        tracking=True,
        help="Number of semesters in this academic year"
    )
    # semester_ids = fields.One2many(
    #     'acmst.semester',
    #     'academic_year_id',
    #     string='Semesters',
    #     help="Semesters in this academic year"
    # )
    
    # Related Records
    batch_ids = fields.One2many(
        'acmst.batch',
        'academic_year_id',
        string='Batches',
        help="Batches in this academic year"
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
    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration_days',
        store=True,
        help="Academic year duration in days"
    )
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress_percentage',
        store=True,
        help="Academic year progress percentage"
    )
    
    @api.depends('start_date')
    def _compute_is_future(self):
        """Compute whether this is a future academic year"""
        today = fields.Date.today()
        for record in self:
            record.is_future = record.start_date and record.start_date > today
    
    @api.depends('end_date')
    def _compute_is_past(self):
        """Compute whether this is a past academic year"""
        today = fields.Date.today()
        for record in self:
            record.is_past = record.end_date and record.end_date < today
    
    @api.depends('batch_ids')
    def _compute_batch_count(self):
        """Compute the number of batches in this academic year"""
        for record in self:
            record.batch_count = len(record.batch_ids.filtered('active'))
    
    @api.depends('batch_ids')  # Will be updated when student module is available
    def _compute_student_count(self):
        """Compute the number of students in this academic year"""
        for record in self:
            # Placeholder - will be implemented when student module is available
            record.student_count = 0
    
    @api.depends('start_date', 'end_date')
    def _compute_duration_days(self):
        """Compute academic year duration in days"""
        for record in self:
            if record.start_date and record.end_date:
                duration = (record.end_date - record.start_date).days
                record.duration_days = max(0, duration)
            else:
                record.duration_days = 0
    
    @api.depends('start_date', 'end_date')
    def _compute_progress_percentage(self):
        """Compute academic year progress percentage"""
        for record in self:
            if record.start_date and record.end_date:
                today = fields.Date.today()
                total_days = (record.end_date - record.start_date).days
                if total_days > 0:
                    if today <= record.start_date:
                        record.progress_percentage = 0.0
                    elif today >= record.end_date:
                        record.progress_percentage = 100.0
                    else:
                        elapsed_days = (today - record.start_date).days
                        record.progress_percentage = min(100.0, (elapsed_days / total_days) * 100)
                else:
                    record.progress_percentage = 0.0
            else:
                record.progress_percentage = 0.0
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure academic year code is unique"""
        for record in self:
            if record.code:
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("Academic year code '%s' already exists. Please use a different code.") % record.code
                    )
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate date fields"""
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date >= record.end_date:
                    raise ValidationError(
                        _("Start date must be before end date.")
                    )
                # Check for overlapping academic years
                overlapping = self.search([
                    ('id', '!=', record.id),
                    ('active', '=', True),
                    '|',
                    '&', ('start_date', '<=', record.start_date), ('end_date', '>=', record.start_date),
                    '&', ('start_date', '<=', record.end_date), ('end_date', '>=', record.end_date)
                ])
                if overlapping:
                    raise ValidationError(
                        _("Academic year dates overlap with existing academic year: %s") % 
                        overlapping[0].name
                    )
    
    @api.constrains('is_current')
    def _check_current_year(self):
        """Ensure only one current academic year exists"""
        for record in self:
            if record.is_current:
                existing_current = self.search([
                    ('is_current', '=', True),
                    ('id', '!=', record.id)
                ])
                if existing_current:
                    raise ValidationError(
                        _("Only one academic year can be marked as current. "
                          "Please uncheck the current status of '%s' first.") % existing_current.name
                    )
    
    @api.constrains('semester_count')
    def _check_semester_count(self):
        """Validate semester count"""
        for record in self:
            if record.semester_count and record.semester_count <= 0:
                raise ValidationError(
                    _("Number of semesters must be greater than 0.")
                )
            if record.semester_count and record.semester_count > 12:
                raise ValidationError(
                    _("Number of semesters cannot exceed 12.")
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
        """Override write to handle current year changes"""
        if 'is_current' in vals and vals['is_current']:
            # Unset other current academic years
            self.search([('is_current', '=', True)]).write({'is_current': False})
        return super().write(vals)
    
    def name_get(self):
        """Custom name_get to show code and name"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.is_current:
                name = f"{name} (Current)"
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
    
    def action_view_batches(self):
        """Action to view batches in this academic year"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_batch')
        action['domain'] = [('academic_year_id', '=', self.id)]
        action['context'] = {
            'default_academic_year_id': self.id,
            'search_default_academic_year_id': self.id,
        }
        return action
    
    def action_view_semesters(self):
        """Action to view semesters in this academic year"""
        # This will be implemented when semester module is created
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Information'),
                'message': _('Semester management module not yet implemented.'),
                'type': 'info',
            }
        }
    
    def action_view_students(self):
        """Action to view students in this academic year"""
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
    
    def action_create_semesters(self):
        """Create semesters for this academic year"""
        # Will be implemented when semester module is available
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Information'),
                'message': _('Semester creation will be available when the semester module is implemented.'),
                'type': 'info',
            }
        }
    
    def toggle_active(self):
        """Override toggle_active to handle related records"""
        for record in self:
            if not record.active:
                # Archive related batches
                record.batch_ids.write({'active': False})
                # Archive related semesters (will be implemented when semester module is available)
                # record.semester_ids.write({'active': False})
        return super().toggle_active()
    
    def _get_related_batches(self):
        """Get all active batches in this academic year"""
        return self.batch_ids.filtered('active')
    
    def _get_related_semesters(self):
        """Get all active semesters in this academic year"""
        # Will be implemented when semester module is available
        return self.env['acmst.semester'].browse([])
    
    def _get_related_students(self):
        """Get all students in this academic year"""
        return self.env['acmst.student'].search([
            ('batch_id.academic_year_id', '=', self.id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_current_academic_year(self):
        """Get the current academic year"""
        return self.search([('is_current', '=', True)], limit=1)
    
    @api.model
    def get_academic_year_by_date(self, date=None):
        """Get academic year for a specific date"""
        if not date:
            date = fields.Date.today()
        return self.search([
            ('start_date', '<=', date),
            ('end_date', '>=', date),
            ('active', '=', True)
        ], limit=1)
    
    @api.model
    def get_future_academic_years(self):
        """Get all future academic years"""
        return self.search([
            ('is_future', '=', True),
            ('active', '=', True)
        ])
    
    @api.model
    def get_past_academic_years(self):
        """Get all past academic years"""
        return self.search([
            ('is_past', '=', True),
            ('active', '=', True)
        ])
    
    def _get_academic_calendar_events(self):
        """Get academic calendar events for this year"""
        # This will be implemented when calendar module is created
        return self.env['acmst.calendar.event'].browse([])
