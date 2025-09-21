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
    name = fields.Char(
        string=_('Health Check Name'),
        compute='_compute_name',
        store=True,
        help=_('Unique name for this health check')
    )
    admission_file_id = fields.Many2one(
        'acmst.admission.file',
        string=_('Admission File'),
        required=True,
        ondelete='cascade',
        help=_('Related admission file')
    )
    check_date = fields.Datetime(
        string=_('Check Date'),
        default=fields.Datetime.now,
        required=True,
        help=_('Date and time of the health check')
    )
    examiner_id = fields.Many2one(
        'res.users',
        string=_('Examiner'),
        required=True,
        default=lambda self: self.env.user,
        help=_('Medical examiner who performed the check')
    )
    state = fields.Selection([
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected'))
    ], string=_('State'), default='draft', tracking=True, help=_('Current state of the health check'))

    # Health Questionnaire
    has_chronic_diseases = fields.Boolean(
        string=_('Has Chronic Diseases'),
        help=_('Does the applicant have any chronic diseases?')
    )
    chronic_diseases_details = fields.Text(
        string=_('Chronic Diseases Details'),
        help=_('Details about chronic diseases')
    )
    takes_medications = fields.Boolean(
        string=_('Takes Medications'),
        help=_('Does the applicant take any medications?')
    )
    medications_details = fields.Text(
        string=_('Medications Details'),
        help=_('Details about medications being taken')
    )
    has_allergies = fields.Boolean(
        string=_('Has Allergies'),
        help=_('Does the applicant have any allergies?')
    )
    allergies_details = fields.Text(
        string=_('Allergies Details'),
        help=_('Details about allergies')
    )
    has_disabilities = fields.Boolean(
        string=_('Has Disabilities'),
        help=_('Does the applicant have any disabilities?')
    )
    disabilities_details = fields.Text(
        string=_('Disabilities Details'),
        help=_('Details about disabilities')
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
        ('unknown', _('Unknown'))
    ], string=_('Blood Type'), help=_('Blood type'))
    height = fields.Float(
        string=_('Height (cm)'),
        digits=(5, 2),
        help=_('Height in centimeters')
    )
    weight = fields.Float(
        string=_('Weight (kg)'),
        digits=(5, 2),
        help=_('Weight in kilograms')
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

    # Attachments - Multiple files support
    medical_reports = fields.Many2many(
        'ir.attachment',
        'acmst_health_check_medical_reports_rel',
        'health_check_id',
        'attachment_id',
        string='Medical Reports',
        help='Medical examination reports (multiple files allowed)'
    )
    lab_results = fields.Many2many(
        'ir.attachment',
        'acmst_health_check_lab_results_rel',
        'health_check_id',
        'attachment_id',
        string='Lab Results',
        help='Laboratory test results (multiple files allowed)'
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
    other_documents = fields.Many2many(
        'ir.attachment',
        'acmst_health_check_other_documents_rel',
        'health_check_id',
        'attachment_id',
        string='Other Documents',
        help='Other medical documents (multiple files allowed)'
    )

    # Computed fields
    applicant_name = fields.Char(
        string='Applicant Name',
        related='admission_file_id.applicant_name_english',
        store=True,
        help='Name of the applicant'
    )
    program_name = fields.Char(
        string='Program',
        related='admission_file_id.program_id.name',
        store=True,
        help='Program name'
    )

    # Student Information for Examiners
    applicant_name_arabic = fields.Char(
        string='Applicant Name (Arabic)',
        related='admission_file_id.applicant_name_arabic',
        store=True,
        help='Name of the applicant in Arabic'
    )

    # Student Profile Picture
    profile_picture = fields.Binary(
        string='Profile Picture',
        related='admission_file_id.profile_picture',
        store=True,
        help='Student profile picture'
    )
    profile_picture_filename = fields.Char(
        string='Profile Picture Filename',
        related='admission_file_id.profile_picture_filename',
        store=True,
        help='Name of the profile picture file'
    )
    national_id = fields.Char(
        string='National ID / Passport',
        related='admission_file_id.national_id',
        store=True,
        help='National ID or passport number'
    )
    id_type = fields.Selection([
        ('national_id', 'National ID'),
        ('passport', 'Passport')
    ], string='ID Type', related='admission_file_id.id_type', store=True, help='Type of identification document')
    university_id = fields.Char(
        string='University ID',
        related='admission_file_id.university_id',
        store=True,
        help='University ID provided by ministry'
    )
    is_processing_student = fields.Boolean(
        string='Processing Student',
        related='admission_file_id.is_processing_student',
        store=True,
        help='Marked as processing student without university ID'
    )
    phone = fields.Char(
        string='Phone',
        related='admission_file_id.phone',
        store=True,
        help='Contact phone number'
    )
    email = fields.Char(
        string='Email',
        related='admission_file_id.email',
        store=True,
        help='Email address'
    )
    birth_date = fields.Date(
        string='Birth Date',
        related='admission_file_id.birth_date',
        store=True,
        help='Date of birth'
    )
    age = fields.Integer(
        string='Age',
        related='admission_file_id.age',
        store=True,
        help='Age in years'
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', related='admission_file_id.gender', store=True, help='Gender')
    nationality = fields.Selection([
        ('sudanese', 'Sudanese'),
        ('foreign', 'Foreign')
    ], string='Nationality', related='admission_file_id.nationality', store=True, help='Nationality')
    address = fields.Text(
        string='Address',
        related='admission_file_id.address',
        store=True,
        help='Full address'
    )
    emergency_contact = fields.Char(
        string='Emergency Contact',
        related='admission_file_id.emergency_contact',
        store=True,
        help='Emergency contact person'
    )
    emergency_phone = fields.Char(
        string='Emergency Phone',
        related='admission_file_id.emergency_phone',
        store=True,
        help='Emergency contact phone number'
    )
    # Guardian information (from default guardian)
    @api.depends('admission_file_id.guardian_ids', 'admission_file_id.guardian_ids.is_default')
    def _compute_guardian_info(self):
        for record in self:
            default_guardian = record.admission_file_id.guardian_ids.filtered(lambda g: g.is_default) if record.admission_file_id.guardian_ids else False
            if default_guardian:
                record.guardian_name = default_guardian[0].name
                record.guardian_relationship = default_guardian[0].relationship
                record.guardian_phone = default_guardian[0].phone
            else:
                record.guardian_name = ''
                record.guardian_relationship = ''
                record.guardian_phone = ''

    guardian_name = fields.Char(
        string='Guardian Name',
        compute='_compute_guardian_info',
        store=True,
        help='Guardian name'
    )
    guardian_relationship = fields.Selection([
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('legal_guardian', 'Legal Guardian'),
        ('other', 'Other')
    ], string='Guardian Relationship', compute='_compute_guardian_info', store=True, help='Relationship to guardian')
    guardian_phone = fields.Char(
        string='Guardian Phone',
        compute='_compute_guardian_info',
        store=True,
        help='Guardian phone number'
    )
    religion = fields.Selection([
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('other', 'Other')
    ], string='Religion', related='admission_file_id.religion', store=True, help='Religious affiliation')
    batch_id = fields.Many2one(
        'acmst.batch',
        string='Batch',
        related='admission_file_id.batch_id',
        store=True,
        help='Target batch'
    )
    batch_name = fields.Char(
        string='Batch Name',
        related='admission_file_id.batch_id.name',
        store=True,
        help='Batch name'
    )
    admission_type = fields.Selection([
        ('direct', 'Direct Admission'),
        ('regular', 'Regular Admission'),
        ('private', 'Private Admission'),
        ('transfer', 'Transfer'),
        ('bridging', 'Bridging'),
        ('degree_holder', 'Degree Holder'),
        ('private_education_grant', 'Private Education Grant')
    ], string='Admission Type', related='admission_file_id.admission_type', store=True, help='Type of admission')

    @api.depends('admission_file_id', 'check_date')
    def _compute_name(self):
        """Compute name for health check"""
        for record in self:
            if record.admission_file_id and record.check_date:
                # Format: "Health Check - FILE001 - 2024-01-15"
                date_str = record.check_date.strftime('%Y-%m-%d')
                record.name = f"Health Check - {record.admission_file_id.name} - {date_str}"
            elif record.admission_file_id:
                record.name = f"Health Check - {record.admission_file_id.name}"
            else:
                record.name = "Health Check"

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

        _logger.info(f"Health check {self.name} submitted for review by {self.env.user.name}")
        self.write({'state': 'submitted'})
        _logger.info(f"Health check {self.name} state changed to 'submitted'")
        return True

    def action_approve(self):
        """Approve health check"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted health checks can be approved.'))

        _logger.info(f"Health check {self.name} approved by {self.env.user.name}")
        self.write({'state': 'approved'})
        _logger.info(f"Health check {self.name} state changed to 'approved'")

        # Update admission file state
        _logger.info(f"Updating admission file {self.admission_file_id.name} to health approved")
        if self.admission_file_id.state == 'health_required':
            self.admission_file_id.action_health_approve()

        return True

    def action_reject(self):
        """Reject health check"""
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Only submitted health checks can be rejected.'))

        _logger.info(f"Health check {self.name} rejected by {self.env.user.name}")
        self.write({'state': 'rejected'})
        _logger.info(f"Health check {self.name} state changed to 'rejected'")

        # Update admission file state
        _logger.info(f"Updating admission file {self.admission_file_id.name} to health rejected")
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

    def write(self, vals):
        """Override write to log all changes"""
        _logger.info(f"Updating health check {self.name} with vals: {vals}")

        # Get old values before update
        old_values = {}
        if 'state' in vals:
            old_values['state'] = self.state
        if 'medical_fitness' in vals:
            old_values['medical_fitness'] = self.medical_fitness

        result = super(AcmstHealthCheck, self).write(vals)

        # Log state changes
        if 'state' in vals and old_values.get('state') != self.state:
            _logger.info(f"Health check {self.name} state changed from {old_values.get('state')} to {self.state}")

            # Create audit log entry for state change
            self.env['acmst.audit.log'].create({
                'model_name': 'acmst.health.check',
                'record_id': self.id,
                'record_name': self.name,
                'action': 'write',
                'category': 'workflow',
                'old_values': f"State: {old_values.get('state')}",
                'new_values': f"State: {self.state}",
                'user_id': self.env.user.id,
                'action_description': f'State changed from {old_values.get("state")} to {self.state}'
            })

            # Post message to chatter
            self.message_post(
                body=f'Status changed from {old_values.get("state")} to {self.state}',
                message_type='comment'
            )

        # Log medical fitness changes
        if 'medical_fitness' in vals:
            _logger.info(f"Health check {self.name} medical fitness changed")

            self.env['acmst.audit.log'].create({
                'model_name': 'acmst.health.check',
                'record_id': self.id,
                'record_name': self.name,
                'action': 'write',
                'category': 'data_modification',
                'old_values': f"Medical Fitness: {old_values.get('medical_fitness', 'None')}",
                'new_values': f"Medical Fitness: {self.medical_fitness}",
                'user_id': self.env.user.id,
                'action_description': 'Medical fitness updated'
            })

            self.message_post(
                body=f'Medical fitness updated to {self.medical_fitness}',
                message_type='comment'
            )

        return result

    def unlink(self):
        """Override unlink to log deletions"""
        for record in self:
            _logger.warning(f"Deleting health check {record.name} for admission file {record.admission_file_id.name}")

            # Create audit log entry for deletion
            self.env['acmst.audit.log'].create({
                'model_name': 'acmst.health.check',
                'record_id': record.id,
                'record_name': record.name,
                'action': 'unlink',
                'category': 'data_deletion',
                'old_values': f'Health check: {record.name} for {record.admission_file_id.name}',
                'new_values': '',
                'user_id': self.env.user.id,
                'action_description': f'Health check deleted: {record.name}'
            })

            # Post message to chatter before deletion
            record.message_post(
                body=f'Health check {record.name} has been deleted',
                message_type='comment'
            )

        return super(AcmstHealthCheck, self).unlink()