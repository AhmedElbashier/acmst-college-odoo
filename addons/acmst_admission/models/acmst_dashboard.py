# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AcmstDashboard(models.Model):
    _name = 'acmst.dashboard'
    _description = 'ACMST Dashboard'
    _auto = False

    # Dashboard Statistics
    total_applications = fields.Integer(
        string='Total Applications',
        compute='_compute_dashboard_statistics',
        help='Total number of admission applications'
    )
    pending_review = fields.Integer(
        string='Pending Review',
        compute='_compute_dashboard_statistics',
        help='Applications pending review'
    )
    health_required = fields.Integer(
        string='Health Required',
        compute='_compute_dashboard_statistics',
        help='Applications requiring health check'
    )
    coordinator_review = fields.Integer(
        string='Coordinator Review',
        compute='_compute_dashboard_statistics',
        help='Applications pending coordinator review'
    )
    manager_review = fields.Integer(
        string='Manager Review',
        compute='_compute_dashboard_statistics',
        help='Applications pending manager review'
    )
    ministry_pending = fields.Integer(
        string='Ministry Pending',
        compute='_compute_dashboard_statistics',
        help='Applications pending ministry approval'
    )
    completed = fields.Integer(
        string='Completed',
        compute='_compute_dashboard_statistics',
        help='Completed applications'
    )

    # Coordinator Statistics
    coordinator_pending_count = fields.Integer(
        string='Pending Reviews',
        compute='_compute_coordinator_statistics',
        help='Applications pending coordinator review'
    )
    coordinator_approved_count = fields.Integer(
        string='Approved',
        compute='_compute_coordinator_statistics',
        help='Applications approved by coordinator'
    )
    coordinator_conditional_count = fields.Integer(
        string='Conditional',
        compute='_compute_coordinator_statistics',
        help='Applications with conditional approval'
    )
    coordinator_rejected_count = fields.Integer(
        string='Rejected',
        compute='_compute_coordinator_statistics',
        help='Applications rejected by coordinator'
    )
    coordinator_total_reviews = fields.Integer(
        string='Total Reviews',
        compute='_compute_coordinator_statistics',
        help='Total coordinator reviews'
    )
    my_reviews_count = fields.Integer(
        string='My Reviews',
        compute='_compute_coordinator_statistics',
        help='Reviews assigned to current user'
    )
    approved = fields.Integer(
        string='Approved',
        compute='_compute_coordinator_statistics',
        help='Applications approved by manager'
    )

    # Health Check Statistics
    total_health_checks = fields.Integer(
        string='Total Health Checks',
        compute='_compute_health_statistics',
        help='Total number of health checks'
    )
    pending_health_checks_count = fields.Integer(
        string='Pending Health Checks',
        compute='_compute_health_statistics',
        help='Health checks pending review'
    )
    approved_health_checks_count = fields.Integer(
        string='Approved Health Checks',
        compute='_compute_health_statistics',
        help='Health checks approved'
    )
    rejected_health_checks_count = fields.Integer(
        string='Rejected Health Checks',
        compute='_compute_health_statistics',
        help='Health checks rejected'
    )
    my_health_checks_count = fields.Integer(
        string='My Health Checks',
        compute='_compute_health_statistics',
        help='Health checks assigned to current user'
    )

    @api.depends()
    def _compute_dashboard_statistics(self):
        """Compute dashboard statistics"""
        for record in self:
            record.total_applications = self.env['acmst.admission.file'].search_count([])
            record.pending_review = self.env['acmst.admission.file'].search_count([('state', '=', 'ministry_pending')])
            record.health_required = self.env['acmst.admission.file'].search_count([('state', '=', 'health_required')])
            record.coordinator_review = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_review')])
            record.manager_review = self.env['acmst.admission.file'].search_count([('state', '=', 'manager_review')])
            record.ministry_pending = self.env['acmst.admission.file'].search_count([('state', '=', 'ministry_pending')])
            record.completed = self.env['acmst.admission.file'].search_count([('state', '=', 'completed')])

    @api.depends()
    def _compute_coordinator_statistics(self):
        """Compute coordinator dashboard statistics"""
        for record in self:
            record.coordinator_pending_count = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_review')])
            record.coordinator_approved_count = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_approved')])
            record.coordinator_conditional_count = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_conditional')])
            record.coordinator_rejected_count = self.env['acmst.admission.file'].search_count([('state', '=', 'coordinator_rejected')])
            record.coordinator_total_reviews = self.env['acmst.admission.file'].search_count([('state', 'in', ['coordinator_review', 'coordinator_approved', 'coordinator_rejected', 'coordinator_conditional'])])
            record.my_reviews_count = self.env['acmst.admission.file'].search_count([('coordinator_id', '=', self.env.user.id)])
            record.approved = self.env['acmst.admission.file'].search_count([('state', '=', 'manager_approved')])

    @api.depends()
    def _compute_health_statistics(self):
        """Compute health check statistics"""
        for record in self:
            record.total_health_checks = self.env['acmst.health.check'].search_count([])
            record.pending_health_checks_count = self.env['acmst.health.check'].search_count([('state', '=', 'draft')])
            record.approved_health_checks_count = self.env['acmst.health.check'].search_count([('state', '=', 'approved')])
            record.rejected_health_checks_count = self.env['acmst.health.check'].search_count([('state', '=', 'rejected')])
            record.my_health_checks_count = self.env['acmst.health.check'].search_count([('examiner_id', '=', self.env.user.id)])

    def action_view_pending_review(self):
        """Open pending review applications"""
        return {
            'name': 'Pending Review',
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'ministry_pending')],
            'context': {},
        }

    def action_view_approved(self):
        """Open approved applications"""
        return {
            'name': 'Approved Applications',
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'manager_approved')],
            'context': {},
        }

    def action_view_completed(self):
        """Open completed applications"""
        return {
            'name': 'Completed Applications',
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.admission.file',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'completed')],
            'context': {},
        }
