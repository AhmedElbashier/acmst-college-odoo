# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestAuditLog(TransactionCase):
    """Test cases for audit log model"""

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

    def test_create_audit_log(self):
        """Test creating an audit log"""
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry',
            'old_value': 'old_value',
            'new_value': 'new_value'
        })
        
        self.assertEqual(audit_log.name, 'Test Action')
        self.assertEqual(audit_log.res_model_id.model, 'acmst.admission.file')
        self.assertEqual(audit_log.res_id, self.admission_file.id)
        self.assertEqual(audit_log.user_id, self.user)
        self.assertEqual(audit_log.action_type, 'create')
        self.assertEqual(audit_log.description, 'Test audit log entry')
        self.assertEqual(audit_log.old_value, 'old_value')
        self.assertEqual(audit_log.new_value, 'new_value')

    def test_audit_log_validation(self):
        """Test audit log validation"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.audit.log'].create({
                'name': 'Test Action',
                # Missing required fields
            })

    def test_audit_log_action_types(self):
        """Test audit log action types"""
        # Test valid action types
        valid_action_types = ['create', 'write', 'unlink', 'workflow', 'login', 'logout', 'access_denied', 'other']
        for action_type in valid_action_types:
            audit_log = self.env['acmst.audit.log'].create({
                'name': 'Test Action',
                'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
                'res_id': self.admission_file.id,
                'user_id': self.user.id,
                'action_type': action_type,
                'description': f'Test {action_type} action'
            })
            self.assertEqual(audit_log.action_type, action_type)

    def test_audit_log_log_action(self):
        """Test audit log log_action method"""
        # Test log_action method
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Test log action',
            old_value='old_value',
            new_value='new_value',
            is_security_violation=False,
            is_anomaly=False
        )
        
        self.assertEqual(audit_log.name, 'Create')
        self.assertEqual(audit_log.action_type, 'create')
        self.assertEqual(audit_log.res_model_id.model, 'acmst.admission.file')
        self.assertEqual(audit_log.res_id, self.admission_file.id)
        self.assertEqual(audit_log.user_id, self.env.user)
        self.assertEqual(audit_log.description, 'Test log action')
        self.assertEqual(audit_log.old_value, 'old_value')
        self.assertEqual(audit_log.new_value, 'new_value')
        self.assertFalse(audit_log.is_security_violation)
        self.assertFalse(audit_log.is_anomaly)

    def test_audit_log_security_violation(self):
        """Test audit log security violation"""
        # Test security violation
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='access_denied',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Unauthorized access attempt',
            is_security_violation=True,
            is_anomaly=False
        )
        
        self.assertEqual(audit_log.action_type, 'access_denied')
        self.assertTrue(audit_log.is_security_violation)
        self.assertFalse(audit_log.is_anomaly)

    def test_audit_log_anomaly(self):
        """Test audit log anomaly"""
        # Test anomaly
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Unusual activity detected',
            is_security_violation=False,
            is_anomaly=True
        )
        
        self.assertEqual(audit_log.action_type, 'write')
        self.assertFalse(audit_log.is_security_violation)
        self.assertTrue(audit_log.is_anomaly)

    def test_audit_log_workflow_action(self):
        """Test audit log workflow action"""
        # Test workflow action
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='workflow',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='State transition from draft to submitted',
            old_value='draft',
            new_value='submitted'
        )
        
        self.assertEqual(audit_log.action_type, 'workflow')
        self.assertEqual(audit_log.description, 'State transition from draft to submitted')
        self.assertEqual(audit_log.old_value, 'draft')
        self.assertEqual(audit_log.new_value, 'submitted')

    def test_audit_log_login_action(self):
        """Test audit log login action"""
        # Test login action
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='login',
            res_model='res.users',
            res_id=self.user.id,
            description='User logged in'
        )
        
        self.assertEqual(audit_log.action_type, 'login')
        self.assertEqual(audit_log.res_model_id.model, 'res.users')
        self.assertEqual(audit_log.res_id, self.user.id)
        self.assertEqual(audit_log.description, 'User logged in')

    def test_audit_log_logout_action(self):
        """Test audit log logout action"""
        # Test logout action
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='logout',
            res_model='res.users',
            res_id=self.user.id,
            description='User logged out'
        )
        
        self.assertEqual(audit_log.action_type, 'logout')
        self.assertEqual(audit_log.res_model_id.model, 'res.users')
        self.assertEqual(audit_log.res_id, self.user.id)
        self.assertEqual(audit_log.description, 'User logged out')

    def test_audit_log_other_action(self):
        """Test audit log other action"""
        # Test other action
        audit_log = self.env['acmst.audit.log'].log_action(
            action_type='other',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Custom action performed'
        )
        
        self.assertEqual(audit_log.action_type, 'other')
        self.assertEqual(audit_log.description, 'Custom action performed')

    def test_audit_log_action_view_related_record(self):
        """Test audit log action view related record"""
        # Create audit log
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry'
        })
        
        # Test action view related record
        action = audit_log.action_view_related_record()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'acmst.admission.file')
        self.assertEqual(action['res_id'], self.admission_file.id)

    def test_audit_log_action_view_related_record_no_record(self):
        """Test audit log action view related record with no record"""
        # Create audit log without related record
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry'
        })
        
        # Test action view related record
        action = audit_log.action_view_related_record()
        self.assertEqual(action['type'], 'ir.actions.act_window_close')

    def test_audit_log_workflow_with_multiple_actions(self):
        """Test audit log workflow with multiple actions"""
        # Create multiple audit logs
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file created'
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file updated',
            old_value='draft',
            new_value='submitted'
        )
        
        audit_log3 = self.env['acmst.audit.log'].log_action(
            action_type='workflow',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='State transition',
            old_value='draft',
            new_value='submitted'
        )
        
        # Check audit logs
        self.assertEqual(len(self.env['acmst.audit.log'].search([])), 3)
        self.assertIn(audit_log1, self.env['acmst.audit.log'].search([]))
        self.assertIn(audit_log2, self.env['acmst.audit.log'].search([]))
        self.assertIn(audit_log3, self.env['acmst.audit.log'].search([]))

    def test_audit_log_workflow_with_security_violations(self):
        """Test audit log workflow with security violations"""
        # Create security violation audit logs
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='access_denied',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Unauthorized access attempt',
            is_security_violation=True
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='access_denied',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Another unauthorized access attempt',
            is_security_violation=True
        )
        
        # Check security violations
        security_violations = self.env['acmst.audit.log'].search([('is_security_violation', '=', True)])
        self.assertEqual(len(security_violations), 2)
        self.assertIn(audit_log1, security_violations)
        self.assertIn(audit_log2, security_violations)

    def test_audit_log_workflow_with_anomalies(self):
        """Test audit log workflow with anomalies"""
        # Create anomaly audit logs
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Unusual activity detected',
            is_anomaly=True
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Another unusual activity detected',
            is_anomaly=True
        )
        
        # Check anomalies
        anomalies = self.env['acmst.audit.log'].search([('is_anomaly', '=', True)])
        self.assertEqual(len(anomalies), 2)
        self.assertIn(audit_log1, anomalies)
        self.assertIn(audit_log2, anomalies)

    def test_audit_log_workflow_with_dates(self):
        """Test audit log workflow with dates"""
        # Create audit log with specific date
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry',
            'create_date': fields.Datetime.now()
        })
        
        # Check date
        self.assertTrue(audit_log.create_date)

    def test_audit_log_workflow_with_ip_address(self):
        """Test audit log workflow with IP address"""
        # Create audit log with IP address
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry',
            'ip_address': '192.168.1.1'
        })
        
        # Check IP address
        self.assertEqual(audit_log.ip_address, '192.168.1.1')

    def test_audit_log_workflow_with_session_id(self):
        """Test audit log workflow with session ID"""
        # Create audit log with session ID
        audit_log = self.env['acmst.audit.log'].create({
            'name': 'Test Action',
            'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'res_id': self.admission_file.id,
            'user_id': self.user.id,
            'action_type': 'create',
            'description': 'Test audit log entry',
            'session_id': 'test_session_123'
        })
        
        # Check session ID
        self.assertEqual(audit_log.session_id, 'test_session_123')

    def test_audit_log_workflow_with_multiple_users(self):
        """Test audit log workflow with multiple users"""
        # Create second user
        user2 = self.env['res.users'].create({
            'name': 'Test User 2',
            'login': 'testuser2',
            'email': 'test2@example.com'
        })
        
        # Create audit logs with different users
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file created by user 1'
        )
        
        # Switch to user2
        self.env = self.env(user=user2)
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file updated by user 2'
        )
        
        # Check users
        self.assertEqual(audit_log1.user_id, self.user)
        self.assertEqual(audit_log2.user_id, user2)

    def test_audit_log_workflow_with_multiple_models(self):
        """Test audit log workflow with multiple models"""
        # Create audit logs for different models
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file created'
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.program',
            res_id=self.program.id,
            description='Program created'
        )
        
        audit_log3 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.batch',
            res_id=self.batch.id,
            description='Batch created'
        )
        
        # Check models
        self.assertEqual(audit_log1.res_model_id.model, 'acmst.admission.file')
        self.assertEqual(audit_log2.res_model_id.model, 'acmst.program')
        self.assertEqual(audit_log3.res_model_id.model, 'acmst.batch')

    def test_audit_log_workflow_with_multiple_action_types(self):
        """Test audit log workflow with multiple action types"""
        # Create audit logs for different action types
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file created'
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file updated'
        )
        
        audit_log3 = self.env['acmst.audit.log'].log_action(
            action_type='workflow',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='State transition'
        )
        
        # Check action types
        self.assertEqual(audit_log1.action_type, 'create')
        self.assertEqual(audit_log2.action_type, 'write')
        self.assertEqual(audit_log3.action_type, 'workflow')

    def test_audit_log_workflow_with_descriptions(self):
        """Test audit log workflow with descriptions"""
        # Create audit logs with different descriptions
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='create',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file created successfully'
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file updated with new information'
        )
        
        audit_log3 = self.env['acmst.audit.log'].log_action(
            action_type='workflow',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='State transition from draft to submitted'
        )
        
        # Check descriptions
        self.assertEqual(audit_log1.description, 'Admission file created successfully')
        self.assertEqual(audit_log2.description, 'Admission file updated with new information')
        self.assertEqual(audit_log3.description, 'State transition from draft to submitted')

    def test_audit_log_workflow_with_values(self):
        """Test audit log workflow with values"""
        # Create audit logs with old and new values
        audit_log1 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file updated',
            old_value='draft',
            new_value='submitted'
        )
        
        audit_log2 = self.env['acmst.audit.log'].log_action(
            action_type='write',
            res_model='acmst.admission.file',
            res_id=self.admission_file.id,
            description='Admission file updated again',
            old_value='submitted',
            new_value='approved'
        )
        
        # Check values
        self.assertEqual(audit_log1.old_value, 'draft')
        self.assertEqual(audit_log1.new_value, 'submitted')
        self.assertEqual(audit_log2.old_value, 'submitted')
        self.assertEqual(audit_log2.new_value, 'approved')
