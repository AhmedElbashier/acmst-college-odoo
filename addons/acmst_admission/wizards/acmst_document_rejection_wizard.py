# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AcmstDocumentRejectionWizard(models.TransientModel):
    _name = 'acmst.document.rejection.wizard'
    _description = 'Document Rejection Wizard'

    document_id = fields.Many2one(
        'acmst.document',
        string='Document',
        required=True,
        help='Document to be rejected'
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True,
        help='Reason for rejecting the document'
    )

    def action_reject(self):
        """Reject the document with reason"""
        self.ensure_one()

        if not self.rejection_reason or len(self.rejection_reason.strip()) < 10:
            raise ValidationError(_('Please provide a detailed rejection reason (at least 10 characters).'))

        self.document_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason
        })

        return {'type': 'ir.actions.act_window_close'}
