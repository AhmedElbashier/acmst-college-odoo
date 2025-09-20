# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestWizards(TransactionCase):
    """Test cases for admission wizards"""

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

    def test_admission_wizard_creation(self):
        """Test admission wizard creation"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing'
        })
        
        self.assertEqual(wizard.name, 'Test Wizard')
        self.assertEqual(wizard.description, 'Test wizard for testing')

    def test_admission_wizard_validation(self):
        """Test admission wizard validation"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.admission.wizard'].create({
                'name': 'Test Wizard',
                # Missing required fields
            })

    def test_coordinator_condition_wizard_creation(self):
        """Test coordinator condition wizard creation"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        self.assertEqual(wizard.admission_file_id, self.admission_file)
        self.assertEqual(wizard.coordinator_id, self.coordinator)

    def test_coordinator_condition_wizard_default_get(self):
        """Test coordinator condition wizard default_get"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Test default_get with context
        wizard = self.env['acmst.coordinator.condition.wizard'].with_context({
            'active_id': self.admission_file.id,
            'active_model': 'acmst.admission.file'
        }).create({})
        
        self.assertEqual(wizard.admission_file_id, self.admission_file)
        self.assertEqual(wizard.coordinator_id, self.coordinator)

    def test_coordinator_condition_wizard_line_creation(self):
        """Test coordinator condition wizard line creation"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard line
        wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        self.assertEqual(wizard_line.wizard_id, wizard)
        self.assertEqual(wizard_line.subject_name, 'Mathematics')
        self.assertEqual(wizard_line.subject_code, 'MATH101')
        self.assertEqual(wizard_line.level, 'bachelor')
        self.assertEqual(wizard_line.description, 'Complete mathematics prerequisite')
        self.assertEqual(wizard_line.notes, 'Must be completed before enrollment')

    def test_coordinator_condition_wizard_action_create_conditions(self):
        """Test coordinator condition wizard action_create_conditions"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard lines
        wizard_line1 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line2 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Physics',
            'subject_code': 'PHYS101',
            'level': 'bachelor',
            'description': 'Complete physics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        result = wizard.action_create_conditions()
        
        # Check conditions were created
        conditions = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(conditions), 2)
        
        # Check admission file state
        self.assertEqual(self.admission_file.state, 'coordinator_conditional')
        
        # Check result
        self.assertEqual(result['type'], 'ir.actions.act_window_close')

    def test_coordinator_condition_wizard_action_create_conditions_no_lines(self):
        """Test coordinator condition wizard action_create_conditions with no lines"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Test action_create_conditions with no lines
        with self.assertRaises(UserError):
            wizard.action_create_conditions()

    def test_coordinator_condition_wizard_validation(self):
        """Test coordinator condition wizard validation"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.coordinator.condition.wizard'].create({
                'admission_file_id': self.admission_file.id,
                # Missing required fields
            })

    def test_coordinator_condition_wizard_line_validation(self):
        """Test coordinator condition wizard line validation"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.coordinator.condition.wizard.line'].create({
                'wizard_id': wizard.id,
                # Missing required fields
            })

    def test_coordinator_condition_wizard_line_levels(self):
        """Test coordinator condition wizard line levels"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Test valid levels
        valid_levels = ['high_school', 'diploma', 'bachelor', 'master', 'phd', 'other']
        for level in valid_levels:
            wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
                'wizard_id': wizard.id,
                'subject_name': f'Test Subject {level}',
                'subject_code': f'TEST{level.upper()}',
                'level': level,
                'description': f'Test description for {level}',
                'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'notes': f'Test notes for {level}'
            })
            self.assertEqual(wizard_line.level, level)

    def test_coordinator_condition_wizard_line_deadline_default(self):
        """Test coordinator condition wizard line deadline default"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard line without deadline
        wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'notes': 'Must be completed before enrollment'
        })
        
        # Check default deadline (30 days from today)
        expected_deadline = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        self.assertEqual(wizard_line.deadline, expected_deadline)

    def test_coordinator_condition_wizard_workflow_with_multiple_conditions(self):
        """Test coordinator condition wizard workflow with multiple conditions"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create multiple wizard lines
        wizard_line1 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line2 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Physics',
            'subject_code': 'PHYS101',
            'level': 'bachelor',
            'description': 'Complete physics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line3 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Chemistry',
            'subject_code': 'CHEM101',
            'level': 'bachelor',
            'description': 'Complete chemistry prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check conditions were created
        conditions = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(conditions), 3)
        
        # Check condition details
        condition1 = conditions.filtered(lambda c: c.subject_name == 'Mathematics')
        condition2 = conditions.filtered(lambda c: c.subject_name == 'Physics')
        condition3 = conditions.filtered(lambda c: c.subject_name == 'Chemistry')
        
        self.assertEqual(len(condition1), 1)
        self.assertEqual(len(condition2), 1)
        self.assertEqual(len(condition3), 1)
        
        self.assertEqual(condition1.subject_code, 'MATH101')
        self.assertEqual(condition2.subject_code, 'PHYS101')
        self.assertEqual(condition3.subject_code, 'CHEM101')

    def test_coordinator_condition_wizard_workflow_with_different_levels(self):
        """Test coordinator condition wizard workflow with different levels"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard lines with different levels
        wizard_line1 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'High School Math',
            'subject_code': 'HSMATH',
            'level': 'high_school',
            'description': 'Complete high school mathematics',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line2 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Bachelor Physics',
            'subject_code': 'BSPHYS',
            'level': 'bachelor',
            'description': 'Complete bachelor physics',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line3 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Master Chemistry',
            'subject_code': 'MSCHEM',
            'level': 'master',
            'description': 'Complete master chemistry',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check conditions were created
        conditions = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(conditions), 3)
        
        # Check condition levels
        high_school_conditions = conditions.filtered(lambda c: c.level == 'high_school')
        bachelor_conditions = conditions.filtered(lambda c: c.level == 'bachelor')
        master_conditions = conditions.filtered(lambda c: c.level == 'master')
        
        self.assertEqual(len(high_school_conditions), 1)
        self.assertEqual(len(bachelor_conditions), 1)
        self.assertEqual(len(master_conditions), 1)

    def test_coordinator_condition_wizard_workflow_with_different_deadlines(self):
        """Test coordinator condition wizard workflow with different deadlines"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard lines with different deadlines
        wizard_line1 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=15)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line2 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Physics',
            'subject_code': 'PHYS101',
            'level': 'bachelor',
            'description': 'Complete physics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        wizard_line3 = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Chemistry',
            'subject_code': 'CHEM101',
            'level': 'bachelor',
            'description': 'Complete chemistry prerequisite',
            'deadline': (date.today() + timedelta(days=45)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check conditions were created
        conditions = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(conditions), 3)
        
        # Check condition deadlines
        condition1 = conditions.filtered(lambda c: c.subject_name == 'Mathematics')
        condition2 = conditions.filtered(lambda c: c.subject_name == 'Physics')
        condition3 = conditions.filtered(lambda c: c.subject_name == 'Chemistry')
        
        self.assertEqual(condition1.deadline, (date.today() + timedelta(days=15)).strftime('%Y-%m-%d'))
        self.assertEqual(condition2.deadline, (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'))
        self.assertEqual(condition3.deadline, (date.today() + timedelta(days=45)).strftime('%Y-%m-%d'))

    def test_coordinator_condition_wizard_workflow_with_notes(self):
        """Test coordinator condition wizard workflow with notes"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard line with notes
        wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment. Additional requirements may apply.'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check condition was created with notes
        condition = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(condition), 1)
        self.assertEqual(condition.notes, 'Must be completed before enrollment. Additional requirements may apply.')

    def test_coordinator_condition_wizard_workflow_with_descriptions(self):
        """Test coordinator condition wizard workflow with descriptions"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard line with description
        wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite with minimum grade of B',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check condition was created with description
        condition = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(condition), 1)
        self.assertEqual(condition.description, 'Complete mathematics prerequisite with minimum grade of B')

    def test_coordinator_condition_wizard_workflow_with_subject_codes(self):
        """Test coordinator condition wizard workflow with subject codes"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard line with subject code
        wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check condition was created with subject code
        condition = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(condition), 1)
        self.assertEqual(condition.subject_code, 'MATH101')

    def test_coordinator_condition_wizard_workflow_with_subject_names(self):
        """Test coordinator condition wizard workflow with subject names"""
        # Set admission file to coordinator review state
        self.admission_file.action_ministry_approve()
        self.admission_file.action_health_required()
        self.admission_file.action_health_approved()
        self.admission_file.action_coordinator_review()
        
        wizard = self.env['acmst.coordinator.condition.wizard'].create({
            'admission_file_id': self.admission_file.id,
            'coordinator_id': self.coordinator.id
        })
        
        # Create wizard line with subject name
        wizard_line = self.env['acmst.coordinator.condition.wizard.line'].create({
            'wizard_id': wizard.id,
            'subject_name': 'Advanced Mathematics',
            'subject_code': 'MATH101',
            'level': 'bachelor',
            'description': 'Complete mathematics prerequisite',
            'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'notes': 'Must be completed before enrollment'
        })
        
        # Test action_create_conditions
        wizard.action_create_conditions()
        
        # Check condition was created with subject name
        condition = self.env['acmst.coordinator.condition'].search([
            ('admission_file_id', '=', self.admission_file.id)
        ])
        self.assertEqual(len(condition), 1)
        self.assertEqual(condition.subject_name, 'Advanced Mathematics')
