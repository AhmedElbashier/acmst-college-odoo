# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestCoordinatorCondition(TransactionCase):
    """Test cases for coordinator condition model"""

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
        
        self.coordinator = self.env['res.users'].create({
            'name': 'Test Coordinator',
            'login': 'coordinator',
            'email': 'coordinator@example.com'
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
            'emergency_phone': '+966501234568',
            'coordinator_id': self.coordinator.id
        })

    def test_create_coordinator_condition(self):
        """Test creating a coordinator condition"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        self.assertEqual(condition.admission_file_id, self.admission_file)
        self.assertEqual(condition.coordinator_id, self.coordinator)
        self.assertEqual(condition.state, 'pending')

    def test_coordinator_condition_workflow(self):
        """Test coordinator condition workflow"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Complete condition
        condition.action_complete()
        self.assertEqual(condition.state, 'completed')
        self.assertEqual(condition.status, 'completed')
        self.assertTrue(condition.completion_date)

    def test_coordinator_condition_rejection(self):
        """Test coordinator condition rejection"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Reject condition
        condition.action_reject()
        self.assertEqual(condition.state, 'rejected')
        self.assertEqual(condition.status, 'rejected')

    def test_coordinator_condition_overdue(self):
        """Test coordinator condition overdue status"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create condition with past deadline
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Check overdue status
        self.assertTrue(condition.is_overdue)
        self.assertEqual(condition.status, 'overdue')
        self.assertEqual(condition.state, 'overdue')

    def test_coordinator_condition_days_remaining(self):
        """Test days remaining calculation"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create condition with future deadline
        future_date = date.today() + timedelta(days=15)
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': future_date.strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Check days remaining
        self.assertEqual(condition.days_remaining, 15)

    def test_coordinator_condition_validation(self):
        """Test coordinator condition validation"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.coordinator.condition'].create({
                'admission_file_id': self.admission_file.id,
                'coordinator_id': self.coordinator.id,
                # Missing required fields
            })

    def test_coordinator_condition_summary(self):
        """Test coordinator condition summary"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        summary = condition.get_condition_summary()
        
        self.assertEqual(summary['subject_name'], 'Mathematics')
        self.assertEqual(summary['subject_code'], 'MATH101')
        self.assertEqual(summary['level'], 'bachelor')
        self.assertEqual(summary['description'], 'Complete mathematics prerequisite')
        self.assertEqual(summary['status'], 'pending')
        self.assertEqual(summary['state'], 'pending')
        self.assertEqual(summary['applicant_name'], 'John Doe')
        self.assertEqual(summary['program_name'], 'Test Program')

    def test_coordinator_condition_statistics(self):
        """Test coordinator condition statistics"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create multiple conditions
        condition1 = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        condition2 = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Physics',
            'subject_code': 'PHYS101',
            'level': 'bachelor',
            'description': 'Complete physics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Complete one condition
        condition1.action_complete()
        
        # Get statistics
        stats = self.env['acmst.coordinator.condition'].get_condition_statistics()
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['overdue'], 0)
        self.assertEqual(stats['rejected'], 0)

    def test_coordinator_condition_by_coordinator(self):
        """Test getting conditions by coordinator"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Get conditions by coordinator
        conditions = self.env['acmst.coordinator.condition'].get_conditions_by_coordinator(self.coordinator.id)
        self.assertIn(condition, conditions)

    def test_coordinator_condition_by_admission_file(self):
        """Test getting conditions by admission file"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Get conditions by admission file
        conditions = self.env['acmst.coordinator.condition'].get_conditions_by_admission_file(self.admission_file.id)
        self.assertIn(condition, conditions)

    def test_coordinator_condition_overdue_conditions(self):
        """Test getting overdue conditions"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create overdue condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Get overdue conditions
        overdue_conditions = self.env['acmst.coordinator.condition'].get_overdue_conditions()
        self.assertIn(condition, overdue_conditions)

    def test_coordinator_condition_pending_conditions(self):
        """Test getting pending conditions"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Create pending condition
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Get pending conditions
        pending_conditions = self.env['acmst.coordinator.condition'].get_pending_conditions()
        self.assertIn(condition, pending_conditions)

    def test_coordinator_condition_invalid_state_transitions(self):
        """Test invalid state transitions"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Complete condition
        condition.action_complete()
        self.assertEqual(condition.state, 'completed')
        
        # Test invalid transitions
        with self.assertRaises(UserError):
            condition.action_complete()  # Cannot complete already completed condition
        
        with self.assertRaises(UserError):
            condition.action_reject()  # Cannot reject completed condition

    def test_coordinator_condition_creation_validation(self):
        """Test coordinator condition creation validation"""
        # Test cannot create condition for non-coordinator review state
        with self.assertRaises(UserError):
            self.env['acmst.coordinator.condition'].create({
                'admission_file_id': self.admission_file.id,
                'coordinator_id': self.coordinator.id,
                'subject_name': 'Mathematics',
                'subject_code': 'MATH101',
                'level': 'bachelor',
                'description': 'Complete mathematics prerequisite',
                'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'notes': 'Must be completed before enrollment'
            })

    def test_coordinator_condition_workflow_with_notes(self):
        """Test coordinator condition workflow with notes"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        condition = self.env['acmst.coordinator.condition'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Complete condition with notes
        condition.write({'notes': 'Completed with additional requirements'})
        condition.action_complete()
        
        self.assertEqual(condition.state, 'completed')
        self.assertEqual(condition.notes, 'Completed with additional requirements')
