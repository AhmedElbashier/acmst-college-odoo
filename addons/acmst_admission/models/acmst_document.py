# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AcmstDocument(models.Model):
    _name = 'acmst.document'
    _description = 'Document Attachment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Document Name',
        required=True,
        help='Name of the document'
    )
    document_type = fields.Selection([
        ('id_document', 'ID Document'),
        ('academic_certificate', 'Academic Certificate'),
        ('transcript', 'Transcript'),
        ('support_document', 'Support Document'),
        ('medical_report', 'Medical Report'),
        ('other', 'Other')
    ], string='Document Type', required=True, help='Type of document')

    file = fields.Binary(
        string='File',
        required=True,
        attachment=True,
        help='Document file'
    )
    filename = fields.Char(
        string='Filename',
        help='Original filename of the document'
    )

    # Relations
    portal_application_id = fields.Many2one(
        'acmst.portal.application',
        string='Portal Application',
        help='Portal application this document belongs to'
    )
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        help='Admission file this document belongs to'
    )

    # Document metadata
    file_size = fields.Integer(
        string='File Size (KB)',
        compute='_compute_file_size',
        store=True,
        help='Size of the document file in kilobytes'
    )
    mime_type = fields.Char(
        string='MIME Type',
        compute='_compute_mime_type',
        store=True,
        help='MIME type of the document'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', help='Status of the document')

    # Approval information
    approval_date = fields.Datetime(
        string='Approval Date',
        help='Date when document was approved'
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        help='User who approved the document'
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        help='Reason for document rejection'
    )

    # Computed fields for categorization
    is_id_document = fields.Boolean(
        string='Is ID Document',
        compute='_compute_document_category',
        help='Whether this is an ID document'
    )
    is_academic_document = fields.Boolean(
        string='Is Academic Document',
        compute='_compute_document_category',
        help='Whether this is an academic document (certificate/transcript)'
    )
    is_support_document = fields.Boolean(
        string='Is Support Document',
        compute='_compute_document_category',
        help='Whether this is a support document'
    )

    @api.depends('file')
    def _compute_file_size(self):
        """Compute file size in KB"""
        for record in self:
            if record.file:
                # Convert bytes to KB
                record.file_size = len(record.file) / 1024
            else:
                record.file_size = 0

    @api.depends('filename')
    def _compute_mime_type(self):
        """Compute MIME type from filename"""
        for record in self:
            if record.filename:
                import mimetypes
                record.mime_type = mimetypes.guess_type(record.filename)[0] or 'application/octet-stream'
            else:
                record.mime_type = 'application/octet-stream'

    @api.depends('document_type')
    def _compute_document_category(self):
        """Compute document categories"""
        for record in self:
            record.is_id_document = record.document_type == 'id_document'
            record.is_academic_document = record.document_type in ['academic_certificate', 'transcript']
            record.is_support_document = record.document_type in ['support_document', 'medical_report', 'other']

    @api.model
    def create(self, vals):
        """Override create to ensure proper validation"""
        if vals.get('filename') and not vals.get('name'):
            vals['name'] = vals['filename'].split('.')[0]

        return super().create(vals)

    def action_approve(self):
        """Approve document"""
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id
        })

    def action_reject(self):
        """Reject document"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Document'),
            'res_model': 'acmst.document.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_document_id': self.id,
            }
        }

    def get_download_url(self):
        """Get download URL for the document"""
        self.ensure_one()
        return f'/web/content/acmst.document/{self.id}/file/{self.filename}'
