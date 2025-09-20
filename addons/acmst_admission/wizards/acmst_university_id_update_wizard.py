# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstUniversityIdUpdateWizard(models.TransientModel):
    _name = 'acmst.university.id.update.wizard'
    _description = 'University ID Update Wizard'

    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        required=True,
        ondelete='cascade',
        help='Admission file to update'
    )
    
    # Student Information (readonly)
    applicant_name = fields.Char(
        string='Applicant Name',
        related='admission_file_id.applicant_name',
        readonly=True,
        help='Student name'
    )
    national_id = fields.Char(
        string='National ID',
        related='admission_file_id.national_id',
        readonly=True,
        help='National ID'
    )
    current_university_id = fields.Char(
        string='Current University ID',
        readonly=True,
        help='Current university ID (if any)'
    )
    
    # New University ID
    new_university_id = fields.Char(
        string='New University ID',
        required=True,
        help='New university ID provided by ministry'
    )
    
    # Comments
    comments = fields.Text(
        string='Comments',
        help='Comments about the university ID update'
    )

    @api.constrains('new_university_id')
    def _check_university_id(self):
        """Validate university ID format"""
        for record in self:
            if record.new_university_id:
                # Basic validation for university ID (alphanumeric, reasonable length)
                if not record.new_university_id.replace('-', '').replace('_', '').isalnum():
                    raise ValidationError(
                        _('University ID must contain only letters, numbers, hyphens, and underscores.')
                    )
                if len(record.new_university_id) < 3 or len(record.new_university_id) > 20:
                    raise ValidationError(
                        _('University ID must be between 3 and 20 characters.')
                    )

    def action_update_university_id(self):
        """Update university ID and clear processing status"""
        self.ensure_one()
        
        if not self.new_university_id:
            raise UserError(_('Please enter a university ID.'))
        
        # Update university ID and clear processing status
        self.admission_file_id.update_university_id(
            self.new_university_id, 
            self.env.user.id
        )
        
        # Update comments if provided
        if self.comments:
            self.admission_file_id.message_post(
                body=f'University ID updated: {self.comments}',
                message_type='comment'
            )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.admission.file',
            'view_mode': 'form',
            'res_id': self.admission_file_id.id,
            'target': 'current',
        }

    def action_cancel(self):
        """Cancel the update"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.admission.file',
            'view_mode': 'form',
            'res_id': self.admission_file_id.id,
            'target': 'current',
        }
