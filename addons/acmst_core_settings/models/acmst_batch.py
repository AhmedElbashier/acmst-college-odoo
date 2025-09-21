# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AcmstBatch(models.Model):
    """Program Batch Management Model
    
    This model manages program batches including:
    - Batch details (name, code, dates)
    - Program and academic year association
    - Student management and capacity
    - Batch status and progression
    """
    _name = 'acmst.batch'
    _description = 'Program Batch'
    _order = 'start_date desc, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string=_('Batch Name'),
        required=True,
        tracking=True,
        help=_("Name of the batch (e.g., 2024-2025, Fall 2024)")
    )
    code = fields.Char(
        string=_('Batch Code'),
        required=True,
        size=20,
        tracking=True,
        help=_("Unique code for the batch (max 20 characters)")
    )
    description = fields.Text(
        string=_('Description'),
        help=_("Description of the batch")
    )
    
    # Associations
    program_id = fields.Many2one(
        'acmst.program',
        string=_('Program'),
        required=True,
        tracking=True,
        help="Program this batch belongs to"
    )
    college_id = fields.Many2one(
        related='program_id.college_id',
        string='College',
        store=True,
        readonly=True
    )
    university_id = fields.Many2one(
        related='program_id.university_id',
        string='University',
        store=True,
        readonly=True
    )
    program_type_id = fields.Many2one(
        related='program_id.program_type_id',
        string='Program Type',
        store=True,
        readonly=True
    )
    
    academic_year_id = fields.Many2one(
        'acmst.academic.year',
        string='Academic Year',
        required=True,
        tracking=True,
        help="Academic year this batch belongs to"
    )
    
    # Dates and Duration
    start_date = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
        help="Batch start date"
    )
    end_date = fields.Date(
        string='End Date',
        tracking=True,
        help="Expected batch end date"
    )
    actual_end_date = fields.Date(
        string='Actual End Date',
        tracking=True,
        help="Actual batch end date"
    )
    registration_start_date = fields.Date(
        string='Registration Start Date',
        tracking=True,
        help="Registration start date for this batch"
    )
    registration_end_date = fields.Date(
        string='Registration End Date',
        tracking=True,
        help="Registration end date for this batch"
    )
    
    # Student Management
    max_students = fields.Integer(
        string='Maximum Students',
        tracking=True,
        help="Maximum number of students allowed in this batch"
    )
    current_students = fields.Integer(
        string='Current Students',
        compute='_compute_current_students',
        store=True,
        help="Current number of students in this batch"
    )
    enrolled_students = fields.Integer(
        string='Enrolled Students',
        compute='_compute_enrolled_students',
        store=True,
        help="Number of enrolled students"
    )
    graduated_students = fields.Integer(
        string='Graduated Students',
        compute='_compute_graduated_students',
        store=True,
        help="Number of graduated students"
    )
    
    # Status and Settings
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Uncheck to archive this batch"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open for Registration'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, required=True)
    
    is_full = fields.Boolean(
        string='Full',
        compute='_compute_is_full',
        store=True,
        help="Whether the batch is full"
    )
    is_registration_open = fields.Boolean(
        string='Registration Open',
        compute='_compute_is_registration_open',
        store=True,
        help="Whether registration is currently open"
    )
    
    # Related Records (will be implemented when student module is available)
    # student_ids = fields.One2many(
    #     'acmst.student',
    #     'batch_id',
    #     string='Students',
    #     help="Students in this batch"
    # )
    
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
        help="Batch duration in days"
    )
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress_percentage',
        store=True,
        help="Batch progress percentage"
    )
    
    @api.depends('admission_file_ids', 'admission_file_ids.state')
    def _compute_current_students(self):
        """Compute the current number of students in this batch"""
        for record in self:
            # Count active admission files as current students
            record.current_students = len(record.admission_file_ids.filtered(
                lambda f: f.state in ['draft', 'submitted', 'under_review', 'approved']
            ))
    
    @api.depends('admission_file_ids', 'admission_file_ids.state')
    def _compute_enrolled_students(self):
        """Compute the number of enrolled students"""
        for record in self:
            # Count approved admission files as enrolled students
            record.enrolled_students = len(record.admission_file_ids.filtered(
                lambda f: f.state == 'approved'
            ))
    
    @api.depends('admission_file_ids', 'admission_file_ids.state')
    def _compute_graduated_students(self):
        """Compute the number of graduated students"""
        for record in self:
            # Count graduated students (when student module is available)
            # For now, use a placeholder that can be updated later
            record.graduated_students = 0
    
    @api.depends('current_students', 'max_students')
    def _compute_is_full(self):
        """Compute whether the batch is full"""
        for record in self:
            record.is_full = record.max_students > 0 and record.current_students >= record.max_students
    
    @api.depends('registration_start_date', 'registration_end_date', 'state')
    def _compute_is_registration_open(self):
        """Compute whether registration is currently open"""
        today = fields.Date.today()
        for record in self:
            if record.state != 'open':
                record.is_registration_open = False
            elif not record.registration_start_date or not record.registration_end_date:
                record.is_registration_open = False
            else:
                record.is_registration_open = (
                    record.registration_start_date <= today <= record.registration_end_date
                )
    
    @api.depends('start_date', 'end_date', 'actual_end_date')
    def _compute_duration_days(self):
        """Compute batch duration in days"""
        for record in self:
            if record.start_date:
                end_date = record.actual_end_date or record.end_date
                if end_date:
                    duration = (end_date - record.start_date).days
                    record.duration_days = max(0, duration)
                else:
                    record.duration_days = 0
            else:
                record.duration_days = 0
    
    @api.depends('start_date', 'end_date', 'actual_end_date')
    def _compute_progress_percentage(self):
        """Compute batch progress percentage"""
        for record in self:
            if record.start_date and record.end_date:
                today = fields.Date.today()
                total_days = (record.end_date - record.start_date).days
                if total_days > 0:
                    if today <= record.start_date:
                        record.progress_percentage = 0.0
                    elif today >= record.end_date or record.actual_end_date:
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
        """Ensure batch code is unique within program"""
        for record in self:
            if record.code and record.program_id:
                existing = self.search([
                    ('code', '=', record.code),
                    ('program_id', '=', record.program_id.id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("Batch code '%s' already exists in %s. Please use a different code.") % 
                        (record.code, record.program_id.name)
                    )
    
    @api.constrains('start_date', 'end_date', 'actual_end_date')
    def _check_dates(self):
        """Validate date fields"""
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date >= record.end_date:
                    raise ValidationError(
                        _("Start date must be before end date.")
                    )
            if record.actual_end_date and record.start_date:
                if record.actual_end_date < record.start_date:
                    raise ValidationError(
                        _("Actual end date cannot be before start date.")
                    )
            if record.actual_end_date and record.end_date:
                if record.actual_end_date > record.end_date:
                    # Allow actual end date to be after expected end date
                    pass
    
    @api.constrains('registration_start_date', 'registration_end_date')
    def _check_registration_dates(self):
        """Validate registration date fields"""
        for record in self:
            if record.registration_start_date and record.registration_end_date:
                if record.registration_start_date >= record.registration_end_date:
                    raise ValidationError(
                        _("Registration start date must be before registration end date.")
                    )
            if record.registration_start_date and record.start_date:
                if record.registration_start_date > record.start_date:
                    raise ValidationError(
                        _("Registration start date cannot be after batch start date.")
                    )
    
    @api.constrains('max_students', 'current_students')
    def _check_student_capacity(self):
        """Validate student capacity"""
        for record in self:
            if record.max_students and record.max_students <= 0:
                raise ValidationError(
                    _("Maximum students must be greater than 0.")
                )
            if record.max_students and record.current_students > record.max_students:
                raise ValidationError(
                    _("Current students (%d) cannot exceed maximum students (%d).") % 
                    (record.current_students, record.max_students)
                )
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and validate"""
        if 'sequence' not in vals:
            vals['sequence'] = self._get_next_sequence(vals.get('program_id'))
        return super().create(vals)
    
    def _get_next_sequence(self, program_id=None):
        """Get next sequence number for the program"""
        domain = []
        if program_id:
            domain.append(('program_id', '=', program_id))
        last_record = self.search(domain, order='sequence desc', limit=1)
        return (last_record.sequence or 0) + 10
    
    def name_get(self):
        """Custom name_get to show code and name"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.program_id:
                name = f"{name} - {record.program_id.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        """Custom name search to include code and program"""
        args = args or []
        if name:
            domain = [
                '|', '|', '|',
                ('name', operator, name),
                ('code', operator, name),
                ('program_id.name', operator, name),
                ('academic_year_id.name', operator, name)
            ]
            return self.search(domain + args, limit=limit).name_get()
        return super()._name_search(name, args, operator, limit)
    
    def action_view_students(self):
        """Action to view students in this batch"""
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
    
    def action_open_registration(self):
        """Open registration for this batch"""
        for record in self:
            if record.state == 'draft':
                record.write({'state': 'open'})
    
    def action_start_batch(self):
        """Start the batch"""
        for record in self:
            if record.state == 'open':
                record.write({'state': 'in_progress'})
    
    def action_complete_batch(self):
        """Complete the batch"""
        for record in self:
            if record.state == 'in_progress':
                record.write({
                    'state': 'completed',
                    'actual_end_date': fields.Date.today()
                })
    
    def action_cancel_batch(self):
        """Cancel the batch"""
        for record in self:
            if record.state in ['draft', 'open']:
                record.write({'state': 'cancelled'})
    
    def toggle_active(self):
        """Override toggle_active to handle related records"""
        for record in self:
            if not record.active:
                # Archive related students (will be implemented when student module is available)
                # record.student_ids.write({'active': False})
                pass
        return super().toggle_active()
    
    def _get_related_students(self):
        """Get all students in this batch"""
        # Will be implemented when student module is available
        return self.env['acmst.student']  # Empty recordset for now
    
    @api.model
    def get_batches_by_program(self, program_id):
        """Get all batches for a specific program"""
        return self.search([
            ('program_id', '=', program_id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_batches_by_academic_year(self, academic_year_id):
        """Get all batches for a specific academic year"""
        return self.search([
            ('academic_year_id', '=', academic_year_id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_open_batches(self):
        """Get all batches open for registration"""
        return self.search([
            ('state', '=', 'open'),
            ('active', '=', True)
        ])
    
    @api.model
    def get_in_progress_batches(self):
        """Get all batches currently in progress"""
        return self.search([
            ('state', '=', 'in_progress'),
            ('active', '=', True)
        ])
    
    def _get_available_capacity(self):
        """Get available capacity for this batch"""
        if self.max_students:
            return max(0, self.max_students - self.current_students)
        return None
