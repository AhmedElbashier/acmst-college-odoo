# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AcmstBatchCreationWizard(models.TransientModel):
    """Batch Creation Wizard
    
    This wizard helps in creating multiple batches for programs
    with predefined templates and settings.
    """
    _name = 'acmst.batch.creation.wizard'
    _description = 'Batch Creation Wizard'

    # Program Selection
    program_id = fields.Many2one(
        'acmst.program',
        string=_('Program'),
        required=True,
        help=_("Program to create batches for")
    )
    college_id = fields.Many2one(
        related='program_id.college_id',
        string=_('College'),
        readonly=True
    )
    university_id = fields.Many2one(
        related='program_id.university_id',
        string=_('University'),
        readonly=True
    )
    
    # Academic Year Selection
    academic_year_id = fields.Many2one(
        'acmst.academic.year',
        string=_('Academic Year'),
        required=True,
        help=_("Academic year for the batches")
    )
    
    # Batch Configuration
    batch_count = fields.Integer(
        string='Number of Batches',
        default=1,
        required=True,
        help="Number of batches to create"
    )
    batch_prefix = fields.Char(
        string='Batch Prefix',
        default='Batch',
        required=True,
        help="Prefix for batch names"
    )
    start_number = fields.Integer(
        string='Start Number',
        default=1,
        required=True,
        help="Starting number for batch codes"
    )
    
    # Date Configuration
    start_date = fields.Date(
        string='Start Date',
        required=True,
        help="Start date for the batches"
    )
    duration_months = fields.Integer(
        string='Duration (Months)',
        default=12,
        required=True,
        help="Duration of each batch in months"
    )
    registration_days_before = fields.Integer(
        string='Registration Days Before',
        default=30,
        required=True,
        help="Days before start date to open registration"
    )
    
    # Student Configuration
    max_students = fields.Integer(
        string='Maximum Students per Batch',
        default=50,
        required=True,
        help="Maximum students allowed in each batch"
    )
    
    # Advanced Options
    create_sequentially = fields.Boolean(
        string='Create Sequentially',
        default=True,
        help="Create batches with sequential start dates"
    )
    gap_days = fields.Integer(
        string='Gap Between Batches (Days)',
        default=0,
        help="Days gap between consecutive batches"
    )
    
    # Results
    created_batch_ids = fields.Many2many(
        'acmst.batch',
        string='Created Batches',
        readonly=True,
        help="Batches created by this wizard"
    )
    
    @api.constrains('batch_count')
    def _check_batch_count(self):
        """Validate batch count"""
        for record in self:
            if record.batch_count <= 0:
                raise ValidationError(
                    _("Number of batches must be greater than 0.")
                )
            if record.batch_count > 50:
                raise ValidationError(
                    _("Cannot create more than 50 batches at once.")
                )
    
    @api.constrains('start_number')
    def _check_start_number(self):
        """Validate start number"""
        for record in self:
            if record.start_number < 1:
                raise ValidationError(
                    _("Start number must be greater than 0.")
                )
    
    @api.constrains('duration_months')
    def _check_duration(self):
        """Validate duration"""
        for record in self:
            if record.duration_months <= 0:
                raise ValidationError(
                    _("Duration must be greater than 0.")
                )
            if record.duration_months > 60:
                raise ValidationError(
                    _("Duration cannot exceed 60 months.")
                )
    
    @api.constrains('max_students')
    def _check_max_students(self):
        """Validate maximum students"""
        for record in self:
            if record.max_students <= 0:
                raise ValidationError(
                    _("Maximum students must be greater than 0.")
                )
            if record.max_students > 1000:
                raise ValidationError(
                    _("Maximum students cannot exceed 1000.")
                )
    
    @api.constrains('registration_days_before')
    def _check_registration_days(self):
        """Validate registration days"""
        for record in self:
            if record.registration_days_before < 0:
                raise ValidationError(
                    _("Registration days before cannot be negative.")
                )
            if record.registration_days_before > 365:
                raise ValidationError(
                    _("Registration days before cannot exceed 365.")
                )
    
    @api.onchange('program_id')
    def _onchange_program_id(self):
        """Update related fields when program changes"""
        if self.program_id:
            # Set default academic year to current year
            current_year = self.env['acmst.academic.year'].get_current_academic_year()
            if current_year:
                self.academic_year_id = current_year.id
            
            # Set default start date to academic year start date
            if self.academic_year_id and self.academic_year_id.start_date:
                self.start_date = self.academic_year_id.start_date
    
    @api.onchange('academic_year_id')
    def _onchange_academic_year_id(self):
        """Update start date when academic year changes"""
        if self.academic_year_id and self.academic_year_id.start_date:
            self.start_date = self.academic_year_id.start_date
    
    def action_create_batches(self):
        """Create the batches based on wizard configuration"""
        self.ensure_one()
        
        if not self.program_id:
            raise UserError(_("Please select a program."))
        
        if not self.academic_year_id:
            raise UserError(_("Please select an academic year."))
        
        if not self.start_date:
            raise UserError(_("Please specify a start date."))
        
        # Create batches
        created_batches = self.env['acmst.batch']
        current_date = self.start_date
        
        for i in range(self.batch_count):
            batch_number = self.start_number + i
            batch_name = f"{self.batch_prefix} {batch_number}"
            batch_code = f"{self.program_id.code}-{self.academic_year_id.code}-B{batch_number:02d}"
            
            # Calculate dates
            from datetime import timedelta
            end_date = current_date + timedelta(days=self.duration_months * 30)
            registration_start = current_date - timedelta(days=self.registration_days_before)
            registration_end = current_date - timedelta(days=1)
            
            # Create batch
            batch_vals = {
                'name': batch_name,
                'code': batch_code,
                'program_id': self.program_id.id,
                'academic_year_id': self.academic_year_id.id,
                'start_date': current_date,
                'end_date': end_date,
                'registration_start_date': registration_start,
                'registration_end_date': registration_end,
                'max_students': self.max_students,
                'state': 'draft',
                'description': f"Batch created via wizard for {self.program_id.name}",
            }
            
            batch = self.env['acmst.batch'].create(batch_vals)
            created_batches |= batch
            
            # Calculate next batch start date
            if self.create_sequentially and i < self.batch_count - 1:
                current_date = end_date + timedelta(days=self.gap_days)
        
        # Update wizard with created batches
        self.created_batch_ids = created_batches
        
        # Return action to view created batches
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Batches'),
            'res_model': 'acmst.batch',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_batches.ids)],
            'context': {
                'search_default_program_id': self.program_id.id,
                'search_default_academic_year_id': self.academic_year_id.id,
            },
            'target': 'current',
        }
    
    def action_preview_batches(self):
        """Preview the batches that will be created"""
        self.ensure_one()
        
        if not self.program_id or not self.academic_year_id or not self.start_date:
            raise UserError(_("Please fill in all required fields."))
        
        # Generate preview data
        preview_data = []
        current_date = self.start_date
        
        for i in range(self.batch_count):
            batch_number = self.start_number + i
            batch_name = f"{self.batch_prefix} {batch_number}"
            batch_code = f"{self.program_id.code}-{self.academic_year_id.code}-B{batch_number:02d}"
            
            from datetime import timedelta
            end_date = current_date + timedelta(days=self.duration_months * 30)
            registration_start = current_date - timedelta(days=self.registration_days_before)
            registration_end = current_date - timedelta(days=1)
            
            preview_data.append({
                'name': batch_name,
                'code': batch_code,
                'start_date': current_date,
                'end_date': end_date,
                'registration_start_date': registration_start,
                'registration_end_date': registration_end,
                'max_students': self.max_students,
            })
            
            if self.create_sequentially and i < self.batch_count - 1:
                current_date = end_date + timedelta(days=self.gap_days)
        
        # Return preview action
        return {
            'type': 'ir.actions.act_window',
            'name': _('Batch Preview'),
            'res_model': 'acmst.batch.creation.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'preview_data': preview_data,
                'show_preview': True,
            },
        }
    
    def action_cancel(self):
        """Cancel the wizard"""
        return {'type': 'ir.actions.act_window_close'}
    
    @api.model
    def get_program_batches_count(self, program_id):
        """Get count of existing batches for a program"""
        return self.env['acmst.batch'].search_count([
            ('program_id', '=', program_id),
            ('active', '=', True)
        ])
    
    @api.model
    def get_next_batch_number(self, program_id, academic_year_id):
        """Get next available batch number for a program and academic year"""
        existing_batches = self.env['acmst.batch'].search([
            ('program_id', '=', program_id),
            ('academic_year_id', '=', academic_year_id),
            ('active', '=', True)
        ])
        
        if not existing_batches:
            return 1
        
        # Extract numbers from existing batch codes
        numbers = []
        for batch in existing_batches:
            if batch.code and '-' in batch.code:
                try:
                    number_part = batch.code.split('-')[-1]
                    numbers.append(int(number_part))
                except ValueError:
                    continue
        
        return max(numbers) + 1 if numbers else 1
