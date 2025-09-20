# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestPortalApplication(TransactionCase):
    """Test cases for portal application model"""

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

    def test_create_portal_application(self):
        """Test creating a portal application"""
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
        
        self.assertEqual(application.applicant_name, 'John Doe')
        self.assertEqual(application.national_id, '1234567890')
        self.assertEqual(application.program_id, self.program)
        self.assertEqual(application.batch_id, self.batch)
        self.assertEqual(application.state, 'draft')

    def test_portal_application_workflow(self):
        """Test portal application workflow"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Review application
        application.action_review()
        self.assertEqual(application.state, 'under_review')
        
        # Approve application
        application.action_approve()
        self.assertEqual(application.state, 'approved')
        
        # Create admission file
        application.action_create_admission_file()
        self.assertEqual(application.state, 'admission_created')
        self.assertTrue(application.admission_file_id)

    def test_portal_application_rejection(self):
        """Test portal application rejection"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Review application
        application.action_review()
        self.assertEqual(application.state, 'under_review')
        
        # Reject application
        application.action_reject()
        self.assertEqual(application.state, 'rejected')

    def test_portal_application_validation(self):
        """Test portal application validation"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.portal.application'].create({
                'applicant_name': 'John Doe',
                # Missing required fields
            })

    def test_portal_application_email_validation(self):
        """Test portal application email validation"""
        # Test valid email
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
        self.assertEqual(application.email, 'john.doe@example.com')

    def test_portal_application_phone_validation(self):
        """Test portal application phone validation"""
        # Test valid phone
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
        self.assertEqual(application.phone, '+966501234567')

    def test_portal_application_national_id_validation(self):
        """Test portal application national ID validation"""
        # Test valid national ID
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
        self.assertEqual(application.national_id, '1234567890')

    def test_portal_application_gender_validation(self):
        """Test portal application gender validation"""
        # Test valid gender
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
        self.assertEqual(application.gender, 'male')

    def test_portal_application_nationality_validation(self):
        """Test portal application nationality validation"""
        # Test valid nationality
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
        self.assertEqual(application.nationality, 'Saudi')

    def test_portal_application_birth_date_validation(self):
        """Test portal application birth date validation"""
        # Test valid birth date
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
        self.assertEqual(application.birth_date, '1990-01-01')

    def test_portal_application_program_validation(self):
        """Test portal application program validation"""
        # Test valid program
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
        self.assertEqual(application.program_id, self.program)

    def test_portal_application_batch_validation(self):
        """Test portal application batch validation"""
        # Test valid batch
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
        self.assertEqual(application.batch_id, self.batch)

    def test_portal_application_address_validation(self):
        """Test portal application address validation"""
        # Test valid address
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
        self.assertEqual(application.address, '123 Test Street, Riyadh')

    def test_portal_application_emergency_contact_validation(self):
        """Test portal application emergency contact validation"""
        # Test valid emergency contact
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
        self.assertEqual(application.emergency_contact, 'Jane Doe')

    def test_portal_application_emergency_phone_validation(self):
        """Test portal application emergency phone validation"""
        # Test valid emergency phone
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
        self.assertEqual(application.emergency_phone, '+966501234568')

    def test_portal_application_workflow_with_notes(self):
        """Test portal application workflow with notes"""
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
            'notes': 'Application submitted with additional documents'
        })
        
        # Check notes
        self.assertEqual(application.notes, 'Application submitted with additional documents')
        
        # Update notes
        application.write({'notes': 'Application submitted with additional documents and verification'})
        self.assertEqual(application.notes, 'Application submitted with additional documents and verification')

    def test_portal_application_workflow_with_attachments(self):
        """Test portal application workflow with attachments"""
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
            'attachments': 'Transcript, Recommendation letter, Health certificate'
        })
        
        # Check attachments
        self.assertEqual(application.attachments, 'Transcript, Recommendation letter, Health certificate')
        
        # Update attachments
        application.write({'attachments': 'Transcript, Recommendation letter, Health certificate, ID copy'})
        self.assertEqual(application.attachments, 'Transcript, Recommendation letter, Health certificate, ID copy')

    def test_portal_application_workflow_with_rejection_reason(self):
        """Test portal application workflow with rejection reason"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Review application
        application.action_review()
        self.assertEqual(application.state, 'under_review')
        
        # Reject application with reason
        application.write({'rejection_reason': 'Incomplete documentation'})
        application.action_reject()
        self.assertEqual(application.state, 'rejected')
        self.assertEqual(application.rejection_reason, 'Incomplete documentation')

    def test_portal_application_workflow_with_approval_notes(self):
        """Test portal application workflow with approval notes"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Review application
        application.action_review()
        self.assertEqual(application.state, 'under_review')
        
        # Approve application with notes
        application.write({'approval_notes': 'Application approved after thorough review'})
        application.action_approve()
        self.assertEqual(application.state, 'approved')
        self.assertEqual(application.approval_notes, 'Application approved after thorough review')

    def test_portal_application_workflow_with_admission_file_creation(self):
        """Test portal application workflow with admission file creation"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Review application
        application.action_review()
        self.assertEqual(application.state, 'under_review')
        
        # Approve application
        application.action_approve()
        self.assertEqual(application.state, 'approved')
        
        # Create admission file
        application.action_create_admission_file()
        self.assertEqual(application.state, 'admission_created')
        self.assertTrue(application.admission_file_id)
        
        # Check admission file details
        admission_file = application.admission_file_id
        self.assertEqual(admission_file.applicant_name, 'John Doe')
        self.assertEqual(admission_file.national_id, '1234567890')
        self.assertEqual(admission_file.program_id, self.program)
        self.assertEqual(admission_file.batch_id, self.batch)

    def test_portal_application_workflow_with_invalid_state_transitions(self):
        """Test portal application workflow with invalid state transitions"""
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
        
        # Test invalid transitions
        with self.assertRaises(UserError):
            application.action_review()  # Cannot review from draft
        
        with self.assertRaises(UserError):
            application.action_approve()  # Cannot approve from draft
        
        with self.assertRaises(UserError):
            application.action_reject()  # Cannot reject from draft
        
        with self.assertRaises(UserError):
            application.action_create_admission_file()  # Cannot create admission file from draft

    def test_portal_application_workflow_with_reset(self):
        """Test portal application workflow with reset"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Reset application
        application.action_reset()
        self.assertEqual(application.state, 'draft')

    def test_portal_application_workflow_with_cancel(self):
        """Test portal application workflow with cancel"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Cancel application
        application.action_cancel()
        self.assertEqual(application.state, 'cancelled')

    def test_portal_application_workflow_with_reopen(self):
        """Test portal application workflow with reopen"""
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
        
        # Submit application
        application.action_submit()
        self.assertEqual(application.state, 'submitted')
        
        # Cancel application
        application.action_cancel()
        self.assertEqual(application.state, 'cancelled')
        
        # Reopen application
        application.action_reopen()
        self.assertEqual(application.state, 'draft')
