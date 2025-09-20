# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestReports(TransactionCase):
    """Test cases for admission reports"""

    def setUp(self):
        super().setUp()
        
        # Create test data
        self.program = self.env['acmst.program'].create({
            'name': 'Test Program',
            'code': 'TEST001',
            'description': 'Test program for testing'
        })
        
        self.batch = self.env['acmst.batch'].create({
            'name': 'Test Batch 2024',
            'code': 'BATCH2024',
            'academic_year_id': self.env.ref('base.main_company').id
        })
        
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'test@example.com'
        })
        
        self.admission_file = self.env['acmst.admission.file'].create({
            'applicant_name': 'John Doe',
            'national_id': '1234567890',
            'phone': '+966501234567',
            'email': 'john.doe@example.com',
            'program_id': self.program.id,
            'batch_id': self.batch.id,
            'birth_date': '1990-01-01',
            'gender': 'male',
            'nationality': 'Saudi',
            'address': '123 Test Street, Riyadh',
            'emergency_contact': 'Jane Doe',
            'emergency_phone': '+966501234568'
        })

    def test_health_check_report(self):
        """Test health check report"""
        # Create health check
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit',
            'blood_type': 'O+',
            'has_chronic_diseases': False,
            'takes_medications': False,
            'has_allergies': False,
            'has_disabilities': False,
            'follow_up_required': False,
            'medical_notes': 'No issues found',
            'restrictions': 'None'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.health_check_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(health_check.ids)
        self.assertTrue(report_html)
        self.assertIn('John Doe', report_html[0])
        self.assertIn('175.0', report_html[0])
        self.assertIn('70.0', report_html[0])

    def test_admission_file_report(self):
        """Test admission file report"""
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(self.admission_file.ids)
        self.assertTrue(report_html)
        self.assertIn('John Doe', report_html[0])
        self.assertIn('1234567890', report_html[0])

    def test_coordinator_condition_report(self):
        """Test coordinator condition report"""
        # Create coordinator condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.user.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.coordinator_condition_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(condition.ids)
        self.assertTrue(report_html)
        self.assertIn('Mathematics', report_html[0])
        self.assertIn('MATH101', report_html[0])

    def test_admission_approval_report(self):
        """Test admission approval report"""
        # Create admission approval
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.user.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_approval_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(approval.ids)
        self.assertTrue(report_html)
        self.assertIn('ministry', report_html[0])
        self.assertIn('approved', report_html[0])

    def test_portal_application_report(self):
        """Test portal application report"""
        # Create portal application
        application = self.env['acmst.portal.application'].create({
            'applicant_name': 'John Doe',
            'national_id': '1234567890',
            'phone': '+966501234567',
            'email': 'john.doe@example.com',
            'program_id': self.program.id,
            'batch_id': self.batch.id,
            'birth_date': '1990-01-01',
            'gender': 'male',
            'nationality': 'Saudi',
            'address': '123 Test Street, Riyadh',
            'emergency_contact': 'Jane Doe',
            'emergency_phone': '+966501234568'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.portal_application_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(application.ids)
        self.assertTrue(report_html)
        self.assertIn('John Doe', report_html[0])
        self.assertIn('1234567890', report_html[0])

    def test_workflow_engine_report(self):
        """Test workflow engine report"""
        # Create workflow engine
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.workflow_engine_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(workflow.ids)
        self.assertTrue(report_html)
        self.assertIn('Test Workflow', report_html[0])

    def test_audit_log_report(self):
        """Test audit log report"""
        # Create audit log
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.audit_log_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(audit_log.ids)
        self.assertTrue(report_html)
        self.assertIn('Test Action', report_html[0])

    def test_health_check_report_with_data(self):
        """Test health check report with data"""
        # Create health check with comprehensive data
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit',
            'blood_type': 'O+',
            'has_chronic_diseases': True,
            'chronic_diseases_details': 'Diabetes',
            'takes_medications': True,
            'medications_details': 'Insulin',
            'has_allergies': True,
            'allergies_details': 'Peanuts',
            'has_disabilities': True,
            'disabilities_details': 'Mobility impairment',
            'follow_up_required': True,
            'follow_up_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'medical_notes': 'Regular checkup required',
            'restrictions': 'No heavy lifting'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.health_check_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(health_check.ids)
        self.assertTrue(report_html)
        self.assertIn('John Doe', report_html[0])
        self.assertIn('175.0', report_html[0])
        self.assertIn('70.0', report_html[0])
        self.assertIn('O+', report_html[0])
        self.assertIn('Diabetes', report_html[0])
        self.assertIn('Insulin', report_html[0])
        self.assertIn('Peanuts', report_html[0])
        self.assertIn('Mobility impairment', report_html[0])

    def test_admission_file_report_with_data(self):
        """Test admission file report with data"""
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(self.admission_file.ids)
        self.assertTrue(report_html)
        self.assertIn('John Doe', report_html[0])
        self.assertIn('1234567890', report_html[0])
        self.assertIn('+966501234567', report_html[0])
        self.assertIn('john.doe@example.com', report_html[0])
        self.assertIn('Test Program', report_html[0])
        self.assertIn('Test Batch 2024', report_html[0])

    def test_coordinator_condition_report_with_data(self):
        """Test coordinator condition report with data"""
        # Create coordinator condition with comprehensive data
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.user.id,
            'subject_name': 'Advanced Mathematics',
            'subject_code': 'MATH201',
            'level': 'bachelor',
            'description': 'Complete advanced mathematics prerequisite with minimum grade of B',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment. Additional requirements may apply.'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.coordinator_condition_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(condition.ids)
        self.assertTrue(report_html)
        self.assertIn('Advanced Mathematics', report_html[0])
        self.assertIn('MATH201', report_html[0])
        self.assertIn('bachelor', report_html[0])
        self.assertIn('Complete advanced mathematics prerequisite', report_html[0])

    def test_admission_approval_report_with_data(self):
        """Test admission approval report with data"""
        # Create admission approval with comprehensive data
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.user.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry after thorough review',
            'conditions': 'Complete health check, Submit additional documents',
            'rejection_reason': '',
            'attachments': 'Approval letter, Ministry certificate'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_approval_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(approval.ids)
        self.assertTrue(report_html)
        self.assertIn('ministry', report_html[0])
        self.assertIn('approved', report_html[0])
        self.assertIn('Application approved by ministry', report_html[0])

    def test_portal_application_report_with_data(self):
        """Test portal application report with data"""
        # Create portal application with comprehensive data
        application = self.env['acmst.portal.application'].create({
            'applicant_name': 'John Doe',
            'national_id': '1234567890',
            'phone': '+966501234567',
            'email': 'john.doe@example.com',
            'program_id': self.program.id,
            'batch_id': self.batch.id,
            'birth_date': '1990-01-01',
            'gender': 'male',
            'nationality': 'Saudi',
            'address': '123 Test Street, Riyadh',
            'emergency_contact': 'Jane Doe',
            'emergency_phone': '+966501234568',
            'notes': 'Application submitted with additional documents',
            'attachments': 'Transcript, Recommendation letter, Health certificate'
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.portal_application_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(application.ids)
        self.assertTrue(report_html)
        self.assertIn('John Doe', report_html[0])
        self.assertIn('1234567890', report_html[0])
        self.assertIn('Application submitted with additional documents', report_html[0])

    def test_workflow_engine_report_with_data(self):
        """Test workflow engine report with data"""
        # Create workflow engine with comprehensive data
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Advanced Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Advanced test workflow for admission files with comprehensive rules',
            'active': True
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.workflow_engine_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(workflow.ids)
        self.assertTrue(report_html)
        self.assertIn('Advanced Test Workflow', report_html[0])
        self.assertIn('Advanced test workflow for admission files', report_html[0])

    def test_audit_log_report_with_data(self):
        """Test audit log report with data"""
        # Create audit log with comprehensive data
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Advanced Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Advanced test audit log entry with comprehensive details',
            'old_value': 'old_value',
            'new_value': 'new_value',
            'ip_address': '192.168.1.1',
            'session_id': 'test_session_123',
            'is_security_violation': False,
            'is_anomaly': False
        })
        
        # Test report generation
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.audit_log_report')
        self.assertTrue(report)
        
        # Test report rendering
        report_html = report._render_qweb_html(audit_log.ids)
        self.assertTrue(report_html)
        self.assertIn('Advanced Test Action', report_html[0])
        self.assertIn('Advanced test audit log entry', report_html[0])
        self.assertIn('192.168.1.1', report_html[0])
        self.assertIn('test_session_123', report_html[0])

    def test_health_check_report_without_data(self):
        """Test health check report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.health_check_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)

    def test_admission_file_report_without_data(self):
        """Test admission file report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)

    def test_coordinator_condition_report_without_data(self):
        """Test coordinator condition report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.coordinator_condition_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)

    def test_admission_approval_report_without_data(self):
        """Test admission approval report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_approval_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)

    def test_portal_application_report_without_data(self):
        """Test portal application report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.portal_application_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)

    def test_workflow_engine_report_without_data(self):
        """Test workflow engine report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.workflow_engine_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)

    def test_audit_log_report_without_data(self):
        """Test audit log report without data"""
        # Test report generation with empty recordset
        report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.audit_log_report')
        self.assertTrue(report)
        
        # Test report rendering with empty recordset
        report_html = report._render_qweb_html([])
        self.assertTrue(report_html)
