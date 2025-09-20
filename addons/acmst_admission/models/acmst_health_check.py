# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class AcmstHealthCheck(models.Model):
    _name = 'acmst.health.check'
    _description = 'Health Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'check_date desc'

    # Basic Information
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string='Admission File',
        required=True,
        ondelete='cascade',
        help='Related admission file'
    )
    check_date = fields.Datetime(
        string='Check Date',
        default=fields.Datetime.now,
        required=True,
        help='Date and time of the health check'
    )
    examiner_id = fields.Many2one(
        'res.users',
        string='Examiner',
        required=True,
        default=lambda self: self.env.user,
        help='Medical examiner who performed the check'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', default='draft', tracking=True, help='Current state of the health check')

    # Health Questionnaire
    has_chronic_diseases = fields.Boolean(
        string='Has Chronic Diseases',
        help='Does the applicant have any chronic diseases?'
    )
    chronic_diseases_details = fields.Text(
        string='Chronic Diseases Details',
        help='Details about chronic diseases'
    )
    takes_medications = fields.Boolean(
        string='Takes Medications',
        help='Does the applicant take any medications?'
    )
    medications_details = fields.Text(
        string='Medications Details',
        help='Details about medications being taken'
    )
    has_allergies = fields.Boolean(
        string='Has Allergies',
        help='Does the applicant have any allergies?'
    )
    allergies_details = fields.Text(
        string='Allergies Details',
        help='Details about allergies'
    )
    has_disabilities = fields.Boolean(
        string='Has Disabilities',
        help='Does the applicant have any disabilities?'
    )
    disabilities_details = fields.Text(
        string='Disabilities Details',
        help='Details about disabilities'
    )
    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('unknown', 'Unknown')
    ], string='Blood Type', help='Blood type')
    height = fields.Float(
        string='Height (cm)',
        digits=(5, 2),
        help='Height in centimeters'
    )
    weight = fields.Float(
        string='Weight (kg)',
        digits=(5, 2),
        help='Weight in kilograms'
    )
    bmi = fields.Float(
        string='BMI',
        compute='_compute_bmi',
        store=True,
        digits=(4, 2),
        help='Body Mass Index'
    )

    # Medical Assessment
    medical_fitness = fields.Selection([
        ('fit', 'Fit'),
        ('unfit', 'Unfit'),
        ('conditional', 'Conditional')
    ], string='Medical Fitness', help='Medical fitness assessment')
    medical_notes = fields.Text(
        string='Medical Notes',
        help='Additional medical notes'
    )
    restrictions = fields.Text(
        string='Restrictions',
        help='Any medical restrictions or limitations'
    )
    follow_up_required = fields.Boolean(
        string='Follow-up Required',
        help='Whether follow-up medical examination is required'
    )
    follow_up_date = fields.Date(
        string='Follow-up Date',
        help='Date for follow-up examination'
    )

    # Attachments
    medical_reports = fields.Binary(
        string='Medical Reports',
        help='Medical examination reports'
    )
    medical_reports_filename = fields.Char(
        string='Medical Reports Filename',
        help='Name of the medical reports file'
    )
    lab_results = fields.Binary(
        string='Lab Results',
        help='Laboratory test results'
    )
    lab_results_filename = fields.Char(
        string='Lab Results Filename',
        help='Name of the lab results file'
    )

    # Dashboard fields
    total_health_checks = fields.Integer(
        string='Total Health Checks',
        compute='_compute_dashboard_counts',
        help='Total number of health checks'
    )
    pending_health_checks_count = fields.Integer(
        string='Pending Health Checks',
        compute='_compute_dashboard_counts',
        help='Number of pending health checks'
    )
    approved_health_checks_count = fields.Integer(
        string='Approved Health Checks',
        compute='_compute_dashboard_counts',
        help='Number of approved health checks'
    )
    rejected_health_checks_count = fields.Integer(
        string='Rejected Health Checks',
        compute='_compute_dashboard_counts',
        help='Number of rejected health checks'
    )
    my_health_checks_count = fields.Integer(
        string='My Health Checks',
        compute='_compute_dashboard_counts',
        help='Number of health checks assigned to current user'
    )
    health_completion_rate = fields.Float(
        string='Completion Rate',
        compute='_compute_dashboard_counts',
        help='Health check completion rate percentage'
    )
    today_health_checks_count = fields.Integer(
        string="Today's Health Checks",
        compute='_compute_dashboard_counts',
        help='Number of health checks performed today'
    )
    week_health_checks_count = fields.Integer(
        string='This Week Health Checks',
        compute='_compute_dashboard_counts',
        help='Number of health checks performed this week'
    )
    other_documents = fields.Binary(
        string='Other Documents',
        help='Other medical documents'
    )
    other_documents_filename = fields.Char(
        string='Other Documents Filename',
        help='Name of the other documents file'
    )

    # Computed fields
    applicant_name = fields.Char(
        string='Applicant Name',
        related='admission_file_id.applicant_name',
        store=True,
        help='Name of the applicant'
    )
    program_name = fields.Char(
        string='Program',
        related='admission_file_id.program_id.name',
        store=True,
        help='Program name'
    )

    @api.depends('height', 'weight')
    def _compute_bmi(self):
        """Compute BMI from height and weight"""
        for record in self:
            if record.height and record.weight and record.height > 0:
                # BMI = weight(kg) / height(m)²
                height_m = record.height / 100  # Convert cm to m
                record.bmi = record.weight / (height_m ** 2)
            else:
                record.bmi = 0.0

    def _compute_dashboard_counts(self):
        """Compute dashboard counts for health officer"""
        for record in self:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            record.total_health_checks = self.env['acmst.health.check'].search_count([])
            record.pending_health_checks_count = self.env['acmst.health.check'].search_count([('state', '=', 'draft')])
            record.approved_health_checks_count = self.env['acmst.health.check'].search_count([('state', '=', 'approved')])
            record.rejected_health_checks_count = self.env['acmst.health.check'].search_count([('state', '=', 'rejected')])
            record.my_health_checks_count = self.env['acmst.health.check'].search_count([('examiner_id', '=', self.env.user.id)])
            
            # Today's health checks
            record.today_health_checks_count = self.env['acmst.health.check'].search_count([
                ('examiner_id', '=', self.env.user.id),
                ('check_date', '>=', today.strftime('%Y-%m-%d 00:00:00')),
                ('check_date', '<=', today.strftime('%Y-%m-%d 23:59:59'))
            ])
            
            # This week's health checks
            record.week_health_checks_count = self.env['acmst.health.check'].search_count([
                ('examiner_id', '=', self.env.user.id),
                ('check_date', '>=', week_ago.strftime('%Y-%m-%d 00:00:00'))
            ])
            
            # Calculate completion rate
            total_my_checks = self.env['acmst.health.check'].search_count([('examiner_id', '=', self.env.user.id)])
            completed_my_checks = self.env['acmst.health.check'].search_count([('examiner_id', '=', self.env.user.id), ('state', 'in', ['approved', 'rejected'])])
            if total_my_checks > 0:
                record.health_completion_rate = (completed_my_checks / total_my_checks) * 100
            else:
                record.health_completion_rate = 0.0

    @api.constrains('height', 'weight')
    def _check_height_weight(self):
        """Validate height and weight values"""
        for record in self:
            if record.height and record.height <= 0:
                raise ValidationError(_('Height must be greater than 0.'))
            if record.weight and record.weight <= 0:
                raise ValidationError(_('Weight must be greater than 0.'))
            if record.height and record.height > 300:
                raise ValidationError(_('Height seems unrealistic. Please check the value.'))
            if record.weight and record.weight > 500:
                raise ValidationError(_('Weight seems unrealistic. Please check the value.'))

    @api.constrains('follow_up_date')
    def _check_follow_up_date(self):
        """Validate follow-up date"""
        for record in self:
            if record.follow_up_date and record.follow_up_date < date.today():
                raise ValidationError(_('Follow-up date cannot be in the past.'))

    def action_submit(self):
        """Submit health check for review"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft health checks can be submitted.'))
        
        if not self.medical_fitness:
            raise UserError(_('Please provide medical fitness assessment before submitting.'))
        
        self.write({'state': 'submitted'})
        return True

    def action_approve(self):
        """Approve health check"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted health checks can be approved.'))
        
        self.write({'state': 'approved'})
        
        # Update admission file state
        if self.admission_file_id.state == 'health_required':
            self.admission_file_id.action_health_approve()
        
        return True

    def action_reject(self):
        """Reject health check"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted health checks can be rejected.'))
        
        self.write({'state': 'rejected'})
        
        # Update admission file state
        if self.admission_file_id.state == 'health_required':
            self.admission_file_id.action_health_reject()
        
        return True

    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.ensure_one()
        if self.state not in ['submitted', 'rejected']:
            raise UserError(_('Only submitted or rejected health checks can be reset to draft.'))
        
        self.write({'state': 'draft'})
        return True

    @api.model
    def create(self, vals):
        """Override create to set default values"""
        if 'admission_file_id' in vals:
            admission_file = self.env['acmst.admission.file'].browse(vals['admission_file_id'])
            if admission_file.state != 'health_required':
                raise UserError(_('Health check can only be created for applications requiring health check.'))
        
        return super().create(vals)

    def get_portal_url(self):
        """Get portal URL for this health check"""
        return request.httprequest.host_url.rstrip('/') + '/admission/health-check/' + str(self.admission_file_id.id)

    def send_approval_notification(self):
        """Send health check approval notification"""
        self.ensure_one()
        if self.state == 'approved':
            # Send notification to admission file
            self.admission_file_id.send_health_check_notification()

    def send_rejection_notification(self):
        """Send health check rejection notification"""
        self.ensure_one()
        if self.state == 'rejected':
            # Send notification to admission file
            template = self.env.ref('acmst_admission.email_template_health_check_rejected', False)
            if template:
                template.send_mail(self.id, force_send=True)

    def _compute_medical_fitness_display(self):
        """Compute medical fitness display name"""
        fitness_mapping = {
            'fit': 'Medically Fit',
            'unfit': 'Medically Unfit',
            'conditional': 'Conditionally Fit'
        }
        for record in self:
            record.medical_fitness_display = fitness_mapping.get(record.medical_fitness, record.medical_fitness)

    medical_fitness_display = fields.Char(
        string='Medical Fitness Display',
        compute='_compute_medical_fitness_display',
        help='Display name for medical fitness'
    )

    def get_bmi_category(self):
        """Get BMI category based on BMI value"""
        self.ensure_one()
        if not self.bmi:
            return 'Unknown'
        
        if self.bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= self.bmi < 25:
            return 'Normal weight'
        elif 25 <= self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def get_health_summary(self):
        """Get health check summary for reporting"""
        self.ensure_one()
        return {
            'applicant_name': self.applicant_name,
            'check_date': self.check_date,
            'examiner': self.examiner_id.name,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'bmi_category': self.get_bmi_category(),
            'blood_type': self.blood_type,
            'medical_fitness': self.medical_fitness_display,
            'has_chronic_diseases': self.has_chronic_diseases,
            'takes_medications': self.takes_medications,
            'has_allergies': self.has_allergies,
            'has_disabilities': self.has_disabilities,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date,
            'medical_notes': self.medical_notes,
            'restrictions': self.restrictions
        }

    # Dashboard button actions
    def action_view_pending_health_checks(self):
        """Open pending health checks for health officer"""
        self.ensure_one()
        return {
            'name': _('Pending Health Checks'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'draft')],
            'context': {'default_examiner_id': self.env.user.id},
        }

    def action_view_approved_health_checks(self):
        """Open approved health checks for health officer"""
        self.ensure_one()
        return {
            'name': _('Approved Health Checks'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'tree,form',
            'domain': [('examiner_id', '=', self.env.user.id), ('state', '=', 'approved')],
            'context': {},
        }

    def action_view_rejected_health_checks(self):
        """Open rejected health checks for health officer"""
        self.ensure_one()
        return {
            'name': _('Rejected Health Checks'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'tree,form',
            'domain': [('examiner_id', '=', self.env.user.id), ('state', '=', 'rejected')],
            'context': {},
        }

    def action_view_my_health_checks(self):
        """Open all health checks for current health officer"""
        self.ensure_one()
        return {
            'name': _('My Health Checks'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'tree,form',
            'domain': [('examiner_id', '=', self.env.user.id)],
            'context': {},
        }

    def action_view_health_statistics(self):
        """Open health check statistics"""
        self.ensure_one()
        return {
            'name': _('Health Check Statistics'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['state', 'medical_fitness', 'examiner_id']},
        }

    def action_view_medical_fitness_stats(self):
        """Open medical fitness statistics"""
        self.ensure_one()
        return {
            'name': _('Medical Fitness Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['medical_fitness', 'blood_type']},
        }

    def action_view_examiner_performance(self):
        """Open examiner performance statistics"""
        self.ensure_one()
        return {
            'name': _('Examiner Performance'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['examiner_id', 'state']},
        }

    def action_view_health_trends(self):
        """Open health check trends"""
        self.ensure_one()
        return {
            'name': _('Health Check Trends'),
            'type': 'ir.actions.act_window',
            'res_model': 'acmst.health.check',
            'view_mode': 'graph,pivot,tree',
            'context': {'group_by': ['check_date:month', 'state']},
        }