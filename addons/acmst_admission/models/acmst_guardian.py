# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _


class AcmstGuardian(models.Model):
    _name = 'acmst.guardian'
    _description = 'Guardian Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Guardian Name', required=True)
    relationship = fields.Selection([
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('legal_guardian', 'Legal Guardian'),
        ('other', 'Other'),
    ], string='Relationship', required=True)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email')
    is_default = fields.Boolean(string='Default Guardian', default=False, help='Only one guardian can be marked as default')
    is_active = fields.Boolean(string='Active', default=True)

    # Relationships
    portal_application_id = fields.Many2one('acmst.portal.application', string='Portal Application', ondelete='cascade')
    admission_file_id = fields.Many2one('acmst.admission.file', string='Admission File', ondelete='cascade')

    @api.constrains('is_default')
    def _check_default_guardian(self):
        """Ensure only one guardian is marked as default per application/file"""
        # Group records by application/file to avoid multiple checks
        app_records = {}
        file_records = {}

        for record in self:
            if record.portal_application_id:
                if record.portal_application_id.id not in app_records:
                    app_records[record.portal_application_id.id] = []
                app_records[record.portal_application_id.id].append(record)
            elif record.admission_file_id:
                if record.admission_file_id.id not in file_records:
                    file_records[record.admission_file_id.id] = []
                file_records[record.admission_file_id.id].append(record)

        # Check portal application guardians
        for app_id, records in app_records.items():
            default_count = sum(1 for r in records if r.is_default)
            if default_count > 1:
                raise ValidationError('Only one guardian can be marked as default.')

        # Check admission file guardians
        for file_id, records in file_records.items():
            default_count = sum(1 for r in records if r.is_default)
            if default_count > 1:
                raise ValidationError('Only one guardian can be marked as default.')

    @api.model
    def create(self, vals):
        """Override create to handle default guardian logic"""
        # If this is the first guardian, automatically set as default
        if not vals.get('is_default', False):
            domain = []
            if vals.get('portal_application_id'):
                domain = [('portal_application_id', '=', vals['portal_application_id'])]
            elif vals.get('admission_file_id'):
                domain = [('admission_file_id', '=', vals['admission_file_id'])]

            if domain:
                existing_guardians = self.search(domain)
                if not existing_guardians:
                    vals['is_default'] = True

        if vals.get('is_default', False):
            # If this is set as default, remove default flag from other guardians
            domain = []
            if vals.get('portal_application_id'):
                domain = [('portal_application_id', '=', vals['portal_application_id'])]
            elif vals.get('admission_file_id'):
                domain = [('admission_file_id', '=', vals['admission_file_id'])]

            if domain:
                other_guardians = self.search(domain + [('is_default', '=', True)])
                other_guardians.write({'is_default': False})

        return super(AcmstGuardian, self).create(vals)

    def write(self, vals):
        """Override write to handle default guardian logic"""
        if vals.get('is_default', False):
            # If this is set as default, remove default flag from other guardians
            for record in self:
                domain = []
                if record.portal_application_id:
                    domain = [('portal_application_id', '=', record.portal_application_id.id)]
                elif record.admission_file_id:
                    domain = [('admission_file_id', '=', record.admission_file_id.id)]

                if domain:
                    other_guardians = self.search(domain + [('id', '!=', record.id), ('is_default', '=', True)])
                    other_guardians.write({'is_default': False})

        return super(AcmstGuardian, self).write(vals)

    def action_set_default(self):
        """Set this guardian as the default guardian"""
        self.ensure_one()

        # Remove default flag from other guardians for the same application/file
        domain = []
        if self.portal_application_id:
            domain = [('portal_application_id', '=', self.portal_application_id.id)]
        elif self.admission_file_id:
            domain = [('admission_file_id', '=', self.admission_file_id.id)]

        if domain:
            other_guardians = self.search(domain + [('is_default', '=', True)])
            other_guardians.write({'is_default': False})

        # Set this guardian as default
        self.write({'is_default': True})

        return True

    def action_remove_default(self):
        """Remove default status from this guardian"""
        self.ensure_one()

        # Only allow removal if there are other guardians to become default
        domain = []
        if self.portal_application_id:
            domain = [('portal_application_id', '=', self.portal_application_id.id)]
        elif self.admission_file_id:
            domain = [('admission_file_id', '=', self.admission_file_id.id)]

        if domain:
            other_guardians = self.search(domain + [('id', '!=', self.id)])

            if not other_guardians:
                # If this is the only guardian, don't allow removal of default status
                return False

        self.write({'is_default': False})

        # If this was the only guardian, set the first other guardian as default
        if domain and not self.search(domain + [('is_default', '=', True)]):
            first_guardian = other_guardians[0]
            first_guardian.write({'is_default': True})

        return True