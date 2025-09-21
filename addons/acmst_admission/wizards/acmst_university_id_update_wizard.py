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
    applicant_name_english = fields.Char(
        string='Applicant Name (English)',
        related='admission_file_id.applicant_name_english',
        readonly=True,
        help='Student name in English'
    )
    applicant_name_arabic = fields.Char(
        string='Applicant Name (Arabic)',
        related='admission_file_id.applicant_name_arabic',
        readonly=True,
        help='Student name in Arabic'
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

    # Acknowledgment
    acknowledge_warning = fields.Boolean(
        string='I acknowledge that updating University ID is a sensitive operation',
        help='I understand that this operation is logged and requires special permissions'
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
        """Update university ID with security checks and acknowledgment"""
        self.ensure_one()

        if not self.new_university_id:
            raise UserError(_('Please enter a university ID.'))

        if not self.acknowledge_warning:
            raise UserError(_('Please acknowledge that you understand this is a sensitive operation.'))

        # Check user permissions
        if not self.env.user.has_group('acmst_admission.group_university_id_updater') and \
           not self.env.user.has_group('acmst_admission.group_admin') and \
           not self.env.user.has_group('acmst_admission.group_manager'):
            raise UserError(_('You do not have permission to update University ID. This operation requires special permissions.'))

        # Check if University ID is already assigned
        if self.admission_file_id.university_id and self.admission_file_id.university_id == self.new_university_id:
            raise UserError(_('The new University ID is the same as the current one.'))

        # Log the sensitive operation
        _logger.warning(f"Sensitive operation: University ID update by user {self.env.user.name} ({self.env.user.id}) "
                       f"for admission file {self.admission_file_id.name} from '{self.admission_file_id.university_id}' to '{self.new_university_id}'")

        # Update university ID
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
