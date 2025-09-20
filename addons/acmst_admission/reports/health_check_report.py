# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HealthCheckReport(models.AbstractModel):
    _name = 'report.acmst_admission.health_check_report'
    _description = 'Health Check Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values for health check report"""
        docs = self.env['acmst.health.check'].browse(docids)
        
        if not docs:
            raise UserError(_('No health check records found.'))
        
        return {
            'doc_ids': docids,
            'doc_model': 'acmst.health.check',
            'docs': docs,
            'data': data,
            'get_bmi_category': self._get_bmi_category,
            'get_health_summary': self._get_health_summary,
        }

    def _get_bmi_category(self, bmi):
        """Get BMI category based on BMI value"""
        if not bmi:
            return 'Unknown'
        
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 25:
            return 'Normal weight'
        elif 25 <= bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def _get_health_summary(self, health_check):
        """Get health check summary"""
        return {
            'applicant_name': health_check.applicant_name,
            'check_date': health_check.check_date,
            'examiner': health_check.examiner_id.name,
            'height': health_check.height,
            'weight': health_check.weight,
            'bmi': health_check.bmi,
            'bmi_category': self._get_bmi_category(health_check.bmi),
            'blood_type': health_check.blood_type,
            'medical_fitness': health_check.medical_fitness_display,
            'has_chronic_diseases': health_check.has_chronic_diseases,
            'takes_medications': health_check.takes_medications,
            'has_allergies': health_check.has_allergies,
            'has_disabilities': health_check.has_disabilities,
            'follow_up_required': health_check.follow_up_required,
            'follow_up_date': health_check.follow_up_date,
            'medical_notes': health_check.medical_notes,
            'restrictions': health_check.restrictions
        }
