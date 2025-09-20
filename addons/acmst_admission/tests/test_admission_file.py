# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestAdmissionFile(TransactionCase):
    """Test cases for admission file model"""

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

    def test_create_admission_file(self):
        """Test creating an admission file"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        self.assertEqual(admission_file.applicant_name, 'John Doe')
        self.assertEqual(admission_file.state, 'new')
        self.assertTrue(admission_file.name)  # Should have generated name

    def test_admission_file_validation(self):
        """Test admission file validation"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.admission.file'].create({
                'applicant_name': 'John Doe',
                # Missing required fields
            })

    def test_state_transitions(self):
        """Test state transitions"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Test valid transitions
        admission_file.action_ministry_approve()
        self.assertEqual(admission_file.state, 'ministry_approved')
        
        admission_file.action_health_required()
        self.assertEqual(admission_file.state, 'health_required')

    def test_invalid_state_transitions(self):
        """Test invalid state transitions"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Test invalid transition
        with self.assertRaises(UserError):
            admission_file.action_complete()  # Cannot complete from new state

    def test_health_check_creation(self):
        """Test health check creation"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        admission_file.action_ministry_approve()
        admission_file.action_health_required()
        
        # Create health check
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        self.assertEqual(health_check.admission_file_id, admission_file)
        self.assertEqual(health_check.bmi, 22.86)  # 70 / (1.75^2)

    def test_coordinator_conditions(self):
        """Test coordinator conditions"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        admission_file.action_ministry_approve()
        admission_file.action_health_required()
        admission_file.action_health_approve()
        admission_file.action_coordinator_review()
        
        # Create condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': admission_file.id,
            'coordinator_id': self.user.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'level2',
            'description': 'Complete mathematics course',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        })
        
        self.assertEqual(condition.admission_file_id, admission_file)
        self.assertEqual(condition.state, 'pending')

    def test_approval_workflow(self):
        """Test complete approval workflow"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Complete workflow
        admission_file.action_ministry_approve()
        self.assertEqual(admission_file.state, 'ministry_approved')
        
        admission_file.action_health_required()
        self.assertEqual(admission_file.state, 'health_required')
        
        admission_file.action_health_approve()
        self.assertEqual(admission_file.state, 'health_approved')
        
        admission_file.action_coordinator_review()
        self.assertEqual(admission_file.state, 'coordinator_review')
        
        admission_file.action_coordinator_approve()
        self.assertEqual(admission_file.state, 'coordinator_approved')
        
        admission_file.action_manager_review()
        self.assertEqual(admission_file.state, 'manager_review')
        
        admission_file.action_manager_approve()
        self.assertEqual(admission_file.state, 'manager_approved')
        
        admission_file.action_complete()
        self.assertEqual(admission_file.state, 'completed')

    def test_student_record_creation(self):
        """Test student record creation"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Complete workflow
        admission_file.action_ministry_approve()
        admission_file.action_health_required()
        admission_file.action_health_approve()
        admission_file.action_coordinator_review()
        admission_file.action_coordinator_approve()
        admission_file.action_manager_review()
        admission_file.action_manager_approve()
        
        # Complete admission
        admission_file.action_complete()
        
        # Check student record creation
        self.assertTrue(admission_file.student_id)
        self.assertEqual(admission_file.student_id.name, 'John Doe')
        self.assertEqual(admission_file.student_id.email, 'john.doe@example.com')

    def test_conditional_approval(self):
        """Test conditional approval workflow"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Complete workflow to coordinator review
        admission_file.action_ministry_approve()
        admission_file.action_health_required()
        admission_file.action_health_approve()
        admission_file.action_coordinator_review()
        
        # Conditional approval
        admission_file.action_coordinator_conditional()
        self.assertEqual(admission_file.state, 'coordinator_conditional')
        
        # Create condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': admission_file.id,
            'coordinator_id': self.user.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'level2',
            'description': 'Complete mathematics course',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        })
        
        # Complete condition
        condition.action_complete()
        self.assertEqual(condition.state, 'completed')
        
        # Send to manager
        admission_file.action_manager_review()
        self.assertEqual(admission_file.state, 'manager_review')

    def test_rejection_workflow(self):
        """Test rejection workflow"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Reject at ministry level
        admission_file.action_ministry_reject()
        self.assertEqual(admission_file.state, 'ministry_rejected')
        
        # Reset and test other rejections
        admission_file.action_reset()
        admission_file.action_ministry_approve()
        admission_file.action_health_required()
        
        admission_file.action_health_reject()
        self.assertEqual(admission_file.state, 'health_rejected')

    def test_cancellation(self):
        """Test cancellation workflow"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Cancel
        admission_file.action_cancel()
        self.assertEqual(admission_file.state, 'cancelled')
        
        # Test cannot cancel completed
        admission_file.action_reset()
        admission_file.action_ministry_approve()
        admission_file.action_health_required()
        admission_file.action_health_approve()
        admission_file.action_coordinator_review()
        admission_file.action_coordinator_approve()
        admission_file.action_manager_review()
        admission_file.action_manager_approve()
        admission_file.action_complete()
        
        with self.assertRaises(UserError):
            admission_file.action_cancel()

    def test_validation_rules(self):
        """Test validation rules"""
        # Test national ID validation
        with self.assertRaises(ValidationError):
            self.env['acmst.admission.file'].create({
                'applicant_name': 'John Doe',
                'national_id': '123',  # Invalid length
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

    def test_computed_fields(self):
        """Test computed fields"""
        admission_file = self.env['acmst.admission.file'].create({
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
        
        # Test computed fields
        self.assertTrue(admission_file.name)
        self.assertEqual(admission_file.program_name, self.program.name)
        self.assertEqual(admission_file.batch_name, self.batch.name)
