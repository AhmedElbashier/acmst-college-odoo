# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, HttpCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestControllers(HttpCase):
    """Test cases for admission controllers"""

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

    def test_portal_application_form(self):
        """Test portal application form"""
        # Test GET request to application form
        response = self.url_open('/admission/apply')
        self.assertEqual(response.status_code, 200)

    def test_portal_application_submit(self):
        """Test portal application submission"""
        # Test POST request to application submission
        data = {
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        self.assertEqual(response.status_code, 200)

    def test_portal_application_status(self):
        """Test portal application status"""
        # Create test application
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
        
        # Test GET request to application status
        response = self.url_open(f'/admission/status/{application.id}')
        self.assertEqual(response.status_code, 200)

    def test_portal_health_check_form(self):
        """Test portal health check form"""
        # Create test admission file
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
        
        # Test GET request to health check form
        response = self.url_open(f'/admission/health-check/{admission_file.id}')
        self.assertEqual(response.status_code, 200)

    def test_portal_conditions_form(self):
        """Test portal conditions form"""
        # Create test admission file
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
        
        # Test GET request to conditions form
        response = self.url_open(f'/admission/conditions/{admission_file.id}')
        self.assertEqual(response.status_code, 200)

    def test_portal_dashboard(self):
        """Test portal dashboard"""
        # Test GET request to dashboard
        response = self.url_open('/admission/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_portal_application_form_validation(self):
        """Test portal application form validation"""
        # Test POST request with invalid data
        data = {
            'applicant_name': '',  # Empty name
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        # Should return error or redirect to form with validation errors
        self.assertIn(response.status_code, [200, 400, 422])

    def test_portal_application_form_success(self):
        """Test portal application form success"""
        # Test POST request with valid data
        data = {
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        # Should return success or redirect to status page
        self.assertIn(response.status_code, [200, 302])

    def test_portal_application_status_not_found(self):
        """Test portal application status not found"""
        # Test GET request with non-existent application ID
        response = self.url_open('/admission/status/99999')
        self.assertEqual(response.status_code, 404)

    def test_portal_health_check_form_not_found(self):
        """Test portal health check form not found"""
        # Test GET request with non-existent admission file ID
        response = self.url_open('/admission/health-check/99999')
        self.assertEqual(response.status_code, 404)

    def test_portal_conditions_form_not_found(self):
        """Test portal conditions form not found"""
        # Test GET request with non-existent admission file ID
        response = self.url_open('/admission/conditions/99999')
        self.assertEqual(response.status_code, 404)

    def test_portal_dashboard_authenticated(self):
        """Test portal dashboard authenticated"""
        # Test GET request to dashboard with authentication
        response = self.url_open('/admission/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_portal_application_form_get(self):
        """Test portal application form GET request"""
        # Test GET request to application form
        response = self.url_open('/admission/apply')
        self.assertEqual(response.status_code, 200)
        # Should contain form fields
        self.assertIn('applicant_name', response.text)
        self.assertIn('national_id', response.text)
        self.assertIn('phone', response.text)
        self.assertIn('email', response.text)

    def test_portal_application_form_post(self):
        """Test portal application form POST request"""
        # Test POST request to application form
        data = {
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        self.assertIn(response.status_code, [200, 302])

    def test_portal_application_status_get(self):
        """Test portal application status GET request"""
        # Create test application
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
        
        # Test GET request to application status
        response = self.url_open(f'/admission/status/{application.id}')
        self.assertEqual(response.status_code, 200)
        # Should contain application details
        self.assertIn('John Doe', response.text)
        self.assertIn('1234567890', response.text)

    def test_portal_health_check_form_get(self):
        """Test portal health check form GET request"""
        # Create test admission file
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
        
        # Test GET request to health check form
        response = self.url_open(f'/admission/health-check/{admission_file.id}')
        self.assertEqual(response.status_code, 200)
        # Should contain health check form fields
        self.assertIn('height', response.text)
        self.assertIn('weight', response.text)
        self.assertIn('medical_fitness', response.text)

    def test_portal_conditions_form_get(self):
        """Test portal conditions form GET request"""
        # Create test admission file
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
        
        # Test GET request to conditions form
        response = self.url_open(f'/admission/conditions/{admission_file.id}')
        self.assertEqual(response.status_code, 200)
        # Should contain conditions form fields
        self.assertIn('subject_name', response.text)
        self.assertIn('subject_code', response.text)
        self.assertIn('level', response.text)

    def test_portal_dashboard_get(self):
        """Test portal dashboard GET request"""
        # Test GET request to dashboard
        response = self.url_open('/admission/dashboard')
        self.assertEqual(response.status_code, 200)
        # Should contain dashboard elements
        self.assertIn('dashboard', response.text.lower())

    def test_portal_application_form_validation_errors(self):
        """Test portal application form validation errors"""
        # Test POST request with invalid data
        data = {
            'applicant_name': '',  # Empty name
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        # Should return error or redirect to form with validation errors
        self.assertIn(response.status_code, [200, 400, 422])

    def test_portal_application_form_success_redirect(self):
        """Test portal application form success redirect"""
        # Test POST request with valid data
        data = {
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        # Should return success or redirect to status page
        self.assertIn(response.status_code, [200, 302])

    def test_portal_application_status_not_found_404(self):
        """Test portal application status not found 404"""
        # Test GET request with non-existent application ID
        response = self.url_open('/admission/status/99999')
        self.assertEqual(response.status_code, 404)

    def test_portal_health_check_form_not_found_404(self):
        """Test portal health check form not found 404"""
        # Test GET request with non-existent admission file ID
        response = self.url_open('/admission/health-check/99999')
        self.assertEqual(response.status_code, 404)

    def test_portal_conditions_form_not_found_404(self):
        """Test portal conditions form not found 404"""
        # Test GET request with non-existent admission file ID
        response = self.url_open('/admission/conditions/99999')
        self.assertEqual(response.status_code, 404)

    def test_portal_dashboard_authenticated_200(self):
        """Test portal dashboard authenticated 200"""
        # Test GET request to dashboard with authentication
        response = self.url_open('/admission/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_portal_application_form_get_200(self):
        """Test portal application form GET request 200"""
        # Test GET request to application form
        response = self.url_open('/admission/apply')
        self.assertEqual(response.status_code, 200)
        # Should contain form fields
        self.assertIn('applicant_name', response.text)
        self.assertIn('national_id', response.text)
        self.assertIn('phone', response.text)
        self.assertIn('email', response.text)

    def test_portal_application_form_post_200_or_302(self):
        """Test portal application form POST request 200 or 302"""
        # Test POST request to application form
        data = {
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
        }
        
        response = self.url_open('/admission/submit', data=data)
        self.assertIn(response.status_code, [200, 302])

    def test_portal_application_status_get_200(self):
        """Test portal application status GET request 200"""
        # Create test application
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
        
        # Test GET request to application status
        response = self.url_open(f'/admission/status/{application.id}')
        self.assertEqual(response.status_code, 200)
        # Should contain application details
        self.assertIn('John Doe', response.text)
        self.assertIn('1234567890', response.text)

    def test_portal_health_check_form_get_200(self):
        """Test portal health check form GET request 200"""
        # Create test admission file
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
        
        # Test GET request to health check form
        response = self.url_open(f'/admission/health-check/{admission_file.id}')
        self.assertEqual(response.status_code, 200)
        # Should contain health check form fields
        self.assertIn('height', response.text)
        self.assertIn('weight', response.text)
        self.assertIn('medical_fitness', response.text)

    def test_portal_conditions_form_get_200(self):
        """Test portal conditions form GET request 200"""
        # Create test admission file
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
        
        # Test GET request to conditions form
        response = self.url_open(f'/admission/conditions/{admission_file.id}')
        self.assertEqual(response.status_code, 200)
        # Should contain conditions form fields
        self.assertIn('subject_name', response.text)
        self.assertIn('subject_code', response.text)
        self.assertIn('level', response.text)

    def test_portal_dashboard_get_200(self):
        """Test portal dashboard GET request 200"""
        # Test GET request to dashboard
        response = self.url_open('/admission/dashboard')
        self.assertEqual(response.status_code, 200)
        # Should contain dashboard elements
        self.assertIn('dashboard', response.text.lower())
