# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestAdmissionWizard(TransactionCase):
    """Test cases for admission wizard"""

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

    def test_create_admission_wizard(self):
        """Test creating an admission wizard"""
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

    def test_admission_wizard_workflow(self):
        """Test admission wizard workflow"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing'
        })
        
        # Test wizard workflow
        self.assertEqual(wizard.name, 'Test Wizard')
        self.assertEqual(wizard.description, 'Test wizard for testing')

    def test_admission_wizard_workflow_with_notes(self):
        """Test admission wizard workflow with notes"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Additional notes for the wizard'
        })
        
        # Check notes
        self.assertEqual(wizard.notes, 'Additional notes for the wizard')
        
        # Update notes
        wizard.write({'notes': 'Updated notes for the wizard'})
        self.assertEqual(wizard.notes, 'Updated notes for the wizard')

    def test_admission_wizard_workflow_with_descriptions(self):
        """Test admission wizard workflow with descriptions"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Additional notes for the wizard'
        })
        
        # Check description
        self.assertEqual(wizard.description, 'Test wizard for testing')
        
        # Update description
        wizard.write({'description': 'Updated description for the wizard'})
        self.assertEqual(wizard.description, 'Updated description for the wizard')

    def test_admission_wizard_workflow_with_names(self):
        """Test admission wizard workflow with names"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Additional notes for the wizard'
        })
        
        # Check name
        self.assertEqual(wizard.name, 'Test Wizard')
        
        # Update name
        wizard.write({'name': 'Updated Test Wizard'})
        self.assertEqual(wizard.name, 'Updated Test Wizard')

    def test_admission_wizard_workflow_with_multiple_wizards(self):
        """Test admission wizard workflow with multiple wizards"""
        # Create multiple wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        wizard3 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 3',
            'description': 'Test wizard 3 for testing',
            'notes': 'Notes for wizard 3'
        })
        
        # Check wizards
        self.assertEqual(len(self.env['acmst.admission.wizard'].search([])), 3)
        self.assertIn(wizard1, self.env['acmst.admission.wizard'].search([]))
        self.assertIn(wizard2, self.env['acmst.admission.wizard'].search([]))
        self.assertIn(wizard3, self.env['acmst.admission.wizard'].search([]))

    def test_admission_wizard_workflow_with_different_names(self):
        """Test admission wizard workflow with different names"""
        # Create wizards with different names
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Admission Wizard',
            'description': 'Wizard for admission process',
            'notes': 'Notes for admission wizard'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Health Check Wizard',
            'description': 'Wizard for health check process',
            'notes': 'Notes for health check wizard'
        })
        
        wizard3 = self.env['acmst.admission.wizard'].create({
            'name': 'Coordinator Wizard',
            'description': 'Wizard for coordinator process',
            'notes': 'Notes for coordinator wizard'
        })
        
        # Check wizards
        self.assertEqual(len(self.env['acmst.admission.wizard'].search([])), 3)
        self.assertIn(wizard1, self.env['acmst.admission.wizard'].search([]))
        self.assertIn(wizard2, self.env['acmst.admission.wizard'].search([]))
        self.assertIn(wizard3, self.env['acmst.admission.wizard'].search([]))

    def test_admission_wizard_workflow_with_different_descriptions(self):
        """Test admission wizard workflow with different descriptions"""
        # Create wizards with different descriptions
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'First test wizard for testing',
            'notes': 'Notes for first wizard'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Second test wizard for testing',
            'notes': 'Notes for second wizard'
        })
        
        wizard3 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 3',
            'description': 'Third test wizard for testing',
            'notes': 'Notes for third wizard'
        })
        
        # Check descriptions
        self.assertEqual(wizard1.description, 'First test wizard for testing')
        self.assertEqual(wizard2.description, 'Second test wizard for testing')
        self.assertEqual(wizard3.description, 'Third test wizard for testing')

    def test_admission_wizard_workflow_with_different_notes(self):
        """Test admission wizard workflow with different notes"""
        # Create wizards with different notes
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'First set of notes for the wizard'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Second set of notes for the wizard'
        })
        
        wizard3 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 3',
            'description': 'Test wizard 3 for testing',
            'notes': 'Third set of notes for the wizard'
        })
        
        # Check notes
        self.assertEqual(wizard1.notes, 'First set of notes for the wizard')
        self.assertEqual(wizard2.notes, 'Second set of notes for the wizard')
        self.assertEqual(wizard3.notes, 'Third set of notes for the wizard')

    def test_admission_wizard_workflow_with_updates(self):
        """Test admission wizard workflow with updates"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Initial notes for the wizard'
        })
        
        # Update wizard
        wizard.write({
            'name': 'Updated Test Wizard',
            'description': 'Updated test wizard for testing',
            'notes': 'Updated notes for the wizard'
        })
        
        # Check updates
        self.assertEqual(wizard.name, 'Updated Test Wizard')
        self.assertEqual(wizard.description, 'Updated test wizard for testing')
        self.assertEqual(wizard.notes, 'Updated notes for the wizard')

    def test_admission_wizard_workflow_with_partial_updates(self):
        """Test admission wizard workflow with partial updates"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Initial notes for the wizard'
        })
        
        # Update only name
        wizard.write({'name': 'Updated Test Wizard'})
        self.assertEqual(wizard.name, 'Updated Test Wizard')
        self.assertEqual(wizard.description, 'Test wizard for testing')
        self.assertEqual(wizard.notes, 'Initial notes for the wizard')
        
        # Update only description
        wizard.write({'description': 'Updated test wizard for testing'})
        self.assertEqual(wizard.name, 'Updated Test Wizard')
        self.assertEqual(wizard.description, 'Updated test wizard for testing')
        self.assertEqual(wizard.notes, 'Initial notes for the wizard')
        
        # Update only notes
        wizard.write({'notes': 'Updated notes for the wizard'})
        self.assertEqual(wizard.name, 'Updated Test Wizard')
        self.assertEqual(wizard.description, 'Updated test wizard for testing')
        self.assertEqual(wizard.notes, 'Updated notes for the wizard')

    def test_admission_wizard_workflow_with_validation_errors(self):
        """Test admission wizard workflow with validation errors"""
        # Test creating wizard without required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.admission.wizard'].create({
                'name': 'Test Wizard',
                # Missing required fields
            })

    def test_admission_wizard_workflow_with_successful_creation(self):
        """Test admission wizard workflow with successful creation"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Check wizard was created successfully
        self.assertTrue(wizard.id)
        self.assertEqual(wizard.name, 'Test Wizard')
        self.assertEqual(wizard.description, 'Test wizard for testing')
        self.assertEqual(wizard.notes, 'Notes for the wizard')

    def test_admission_wizard_workflow_with_successful_updates(self):
        """Test admission wizard workflow with successful updates"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Update wizard
        wizard.write({
            'name': 'Updated Test Wizard',
            'description': 'Updated test wizard for testing',
            'notes': 'Updated notes for the wizard'
        })
        
        # Check updates were successful
        self.assertEqual(wizard.name, 'Updated Test Wizard')
        self.assertEqual(wizard.description, 'Updated test wizard for testing')
        self.assertEqual(wizard.notes, 'Updated notes for the wizard')

    def test_admission_wizard_workflow_with_successful_deletion(self):
        """Test admission wizard workflow with successful deletion"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Delete wizard
        wizard.unlink()
        
        # Check wizard was deleted
        self.assertFalse(self.env['acmst.admission.wizard'].search([('id', '=', wizard.id)]))

    def test_admission_wizard_workflow_with_successful_search(self):
        """Test admission wizard workflow with successful search"""
        # Create wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Search wizards
        wizards = self.env['acmst.admission.wizard'].search([])
        self.assertEqual(len(wizards), 2)
        self.assertIn(wizard1, wizards)
        self.assertIn(wizard2, wizards)

    def test_admission_wizard_workflow_with_successful_filtering(self):
        """Test admission wizard workflow with successful filtering"""
        # Create wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Filter wizards by name
        wizards = self.env['acmst.admission.wizard'].search([('name', '=', 'Test Wizard 1')])
        self.assertEqual(len(wizards), 1)
        self.assertIn(wizard1, wizards)
        self.assertNotIn(wizard2, wizards)

    def test_admission_wizard_workflow_with_successful_counting(self):
        """Test admission wizard workflow with successful counting"""
        # Create wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Count wizards
        count = self.env['acmst.admission.wizard'].search_count([])
        self.assertEqual(count, 2)

    def test_admission_wizard_workflow_with_successful_reading(self):
        """Test admission wizard workflow with successful reading"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Read wizard
        wizard_data = wizard.read(['name', 'description', 'notes'])
        self.assertEqual(len(wizard_data), 1)
        self.assertEqual(wizard_data[0]['name'], 'Test Wizard')
        self.assertEqual(wizard_data[0]['description'], 'Test wizard for testing')
        self.assertEqual(wizard_data[0]['notes'], 'Notes for the wizard')

    def test_admission_wizard_workflow_with_successful_browsing(self):
        """Test admission wizard workflow with successful browsing"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Browse wizard
        wizard_browse = self.env['acmst.admission.wizard'].browse(wizard.id)
        self.assertEqual(wizard_browse.name, 'Test Wizard')
        self.assertEqual(wizard_browse.description, 'Test wizard for testing')
        self.assertEqual(wizard_browse.notes, 'Notes for the wizard')

    def test_admission_wizard_workflow_with_successful_exists(self):
        """Test admission wizard workflow with successful exists"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Check if wizard exists
        self.assertTrue(wizard.exists())
        
        # Delete wizard
        wizard.unlink()
        
        # Check if wizard no longer exists
        self.assertFalse(wizard.exists())

    def test_admission_wizard_workflow_with_successful_ensure_one(self):
        """Test admission wizard workflow with successful ensure_one"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Ensure one wizard
        wizard.ensure_one()
        
        # This should not raise an error
        self.assertTrue(True)

    def test_admission_wizard_workflow_with_successful_ensure_one_error(self):
        """Test admission wizard workflow with successful ensure_one error"""
        # Create multiple wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Try to ensure one with multiple wizards
        wizards = self.env['acmst.admission.wizard'].search([])
        with self.assertRaises(ValueError):
            wizards.ensure_one()

    def test_admission_wizard_workflow_with_successful_ensure_one_success(self):
        """Test admission wizard workflow with successful ensure_one success"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Ensure one wizard
        wizard.ensure_one()
        
        # This should not raise an error
        self.assertTrue(True)

    def test_admission_wizard_workflow_with_successful_ensure_one_empty(self):
        """Test admission wizard workflow with successful ensure_one empty"""
        # Try to ensure one with empty recordset
        wizards = self.env['acmst.admission.wizard'].search([('name', '=', 'Non-existent Wizard')])
        with self.assertRaises(ValueError):
            wizards.ensure_one()

    def test_admission_wizard_workflow_with_successful_ensure_one_single(self):
        """Test admission wizard workflow with successful ensure_one single"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Ensure one wizard
        wizard.ensure_one()
        
        # This should not raise an error
        self.assertTrue(True)

    def test_admission_wizard_workflow_with_successful_ensure_one_multiple(self):
        """Test admission wizard workflow with successful ensure_one multiple"""
        # Create multiple wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Try to ensure one with multiple wizards
        wizards = self.env['acmst.admission.wizard'].search([])
        with self.assertRaises(ValueError):
            wizards.ensure_one()

    def test_admission_wizard_workflow_with_successful_ensure_one_success_single(self):
        """Test admission wizard workflow with successful ensure_one success single"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Ensure one wizard
        wizard.ensure_one()
        
        # This should not raise an error
        self.assertTrue(True)

    def test_admission_wizard_workflow_with_successful_ensure_one_success_multiple(self):
        """Test admission wizard workflow with successful ensure_one success multiple"""
        # Create multiple wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Try to ensure one with multiple wizards
        wizards = self.env['acmst.admission.wizard'].search([])
        with self.assertRaises(ValueError):
            wizards.ensure_one()

    def test_admission_wizard_workflow_with_successful_ensure_one_success_empty(self):
        """Test admission wizard workflow with successful ensure_one success empty"""
        # Try to ensure one with empty recordset
        wizards = self.env['acmst.admission.wizard'].search([('name', '=', 'Non-existent Wizard')])
        with self.assertRaises(ValueError):
            wizards.ensure_one()

    def test_admission_wizard_workflow_with_successful_ensure_one_success_single(self):
        """Test admission wizard workflow with successful ensure_one success single"""
        wizard = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard',
            'description': 'Test wizard for testing',
            'notes': 'Notes for the wizard'
        })
        
        # Ensure one wizard
        wizard.ensure_one()
        
        # This should not raise an error
        self.assertTrue(True)

    def test_admission_wizard_workflow_with_successful_ensure_one_success_multiple(self):
        """Test admission wizard workflow with successful ensure_one success multiple"""
        # Create multiple wizards
        wizard1 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 1',
            'description': 'Test wizard 1 for testing',
            'notes': 'Notes for wizard 1'
        })
        
        wizard2 = self.env['acmst.admission.wizard'].create({
            'name': 'Test Wizard 2',
            'description': 'Test wizard 2 for testing',
            'notes': 'Notes for wizard 2'
        })
        
        # Try to ensure one with multiple wizards
        wizards = self.env['acmst.admission.wizard'].search([])
        with self.assertRaises(ValueError):
            wizards.ensure_one()

    def test_admission_wizard_workflow_with_successful_ensure_one_success_empty(self):
        """Test admission wizard workflow with successful ensure_one success empty"""
        # Try to ensure one with empty recordset
        wizards = self.env['acmst.admission.wizard'].search([('name', '=', 'Non-existent Wizard')])
        with self.assertRaises(ValueError):
            wizards.ensure_one()
