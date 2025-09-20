# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestHealthCheck(TransactionCase):
    """Test cases for health check model"""

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

    def test_create_health_check(self):
        """Test creating a health check"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        self.assertEqual(health_check.admission_file_id, self.admission_file)
        self.assertEqual(health_check.examiner_id, self.user)
        self.assertEqual(health_check.state, 'draft')

    def test_bmi_calculation(self):
        """Test BMI calculation"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        # Test BMI calculation
        expected_bmi = 70.0 / (1.75 ** 2)
        self.assertAlmostEqual(health_check.bmi, expected_bmi, places=2)

    def test_bmi_category(self):
        """Test BMI category calculation"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        # Test underweight
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 50.0,
            'medical_fitness': 'fit'
        })
        self.assertEqual(health_check.get_bmi_category(), 'Underweight')
        
        # Test normal weight
        health_check.write({'weight': 70.0})
        self.assertEqual(health_check.get_bmi_category(), 'Normal weight')
        
        # Test overweight
        health_check.write({'weight': 80.0})
        self.assertEqual(health_check.get_bmi_category(), 'Overweight')
        
        # Test obese
        health_check.write({'weight': 100.0})
        self.assertEqual(health_check.get_bmi_category(), 'Obese')

    def test_health_check_workflow(self):
        """Test health check workflow"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        # Submit health check
        health_check.action_submit()
        self.assertEqual(health_check.state, 'submitted')
        
        # Approve health check
        health_check.action_approve()
        self.assertEqual(health_check.state, 'approved')
        
        # Check admission file state
        self.assertEqual(self.admission_file.state, 'health_approved')

    def test_health_check_rejection(self):
        """Test health check rejection"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'unfit'
        })
        
        # Submit health check
        health_check.action_submit()
        self.assertEqual(health_check.state, 'submitted')
        
        # Reject health check
        health_check.action_reject()
        self.assertEqual(health_check.state, 'rejected')
        
        # Check admission file state
        self.assertEqual(self.admission_file.state, 'health_rejected')

    def test_health_check_validation(self):
        """Test health check validation"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.health.check'].create({
                'admission_file_id': self.admission_file.id,
                'examiner_id': self.user.id,
                # Missing required fields
            })

    def test_health_check_medical_fitness_display(self):
        """Test medical fitness display"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        # Test medical fitness display
        self.assertEqual(health_check.medical_fitness_display, 'Medically Fit')
        
        health_check.write({'medical_fitness': 'unfit'})
        self.assertEqual(health_check.medical_fitness_display, 'Medically Unfit')
        
        health_check.write({'medical_fitness': 'conditional'})
        self.assertEqual(health_check.medical_fitness_display, 'Conditionally Fit')

    def test_health_check_summary(self):
        """Test health check summary"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
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
            'has_disabilities': False,
            'follow_up_required': True,
            'follow_up_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'medical_notes': 'Regular checkup required',
            'restrictions': 'No heavy lifting'
        })
        
        summary = health_check.get_health_summary()
        
        self.assertEqual(summary['applicant_name'], 'John Doe')
        self.assertEqual(summary['height'], 175.0)
        self.assertEqual(summary['weight'], 70.0)
        self.assertEqual(summary['blood_type'], 'O+')
        self.assertEqual(summary['medical_fitness'], 'Medically Fit')
        self.assertTrue(summary['has_chronic_diseases'])
        self.assertTrue(summary['takes_medications'])
        self.assertTrue(summary['has_allergies'])
        self.assertFalse(summary['has_disabilities'])
        self.assertTrue(summary['follow_up_required'])
        self.assertEqual(summary['medical_notes'], 'Regular checkup required')
        self.assertEqual(summary['restrictions'], 'No heavy lifting')

    def test_health_check_reset(self):
        """Test health check reset"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        # Submit and approve
        health_check.action_submit()
        health_check.action_approve()
        self.assertEqual(health_check.state, 'approved')
        
        # Reset
        health_check.action_reset()
        self.assertEqual(health_check.state, 'draft')

    def test_health_check_invalid_state_transitions(self):
        """Test invalid state transitions"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        # Test invalid transitions
        with self.assertRaises(UserError):
            health_check.action_approve()  # Cannot approve from draft
        
        with self.assertRaises(UserError):
            health_check.action_reject()  # Cannot reject from draft

    def test_health_check_creation_validation(self):
        """Test health check creation validation"""
        # Test cannot create health check for non-health required state
        with self.assertRaises(UserError):
            self.env['acmst.health.check'].create({
                'admission_file_id': self.admission_file.id,
                'examiner_id': self.user.id,
                'height': 175.0,
                'weight': 70.0,
                'medical_fitness': 'fit'
            })

    def test_health_check_attachments(self):
        """Test health check attachments"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'fit'
        })
        
        # Test attachment fields
        self.assertFalse(health_check.medical_reports)
        self.assertFalse(health_check.lab_results)
        self.assertFalse(health_check.other_documents)

    def test_health_check_workflow_with_conditions(self):
        """Test health check workflow with medical conditions"""
        # Set admission file to health required state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        
        health_check = self.env['acmst.health.check'].create({
            'admission_file_id': self.admission_file.id,
            'examiner_id': self.user.id,
            'height': 175.0,
            'weight': 70.0,
            'medical_fitness': 'conditional',
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
            'medical_notes': 'Requires special accommodations',
            'restrictions': 'No heavy lifting, requires wheelchair access'
        })
        
        # Submit health check
        health_check.action_submit()
        self.assertEqual(health_check.state, 'submitted')
        
        # Approve with conditions
        health_check.action_approve()
        self.assertEqual(health_check.state, 'approved')
        
        # Check admission file state
        self.assertEqual(self.admission_file.state, 'health_approved')
