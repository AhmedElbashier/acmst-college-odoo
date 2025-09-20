# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging
import time

_logger = logging.getLogger(__name__)


class TestPerformance(TransactionCase):
    """Test cases for admission performance"""

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

    def test_admission_file_creation_performance(self):
        """Test admission file creation performance"""
        start_time = time.time()
        
        # Create multiple admission files
        for i in range(100):
            self.env['acmst.admission.file'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 admission files in {duration:.2f} seconds")

    def test_admission_file_search_performance(self):
        """Test admission file search performance"""
        # Create test data
        for i in range(1000):
            self.env['acmst.admission.file'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
        
        start_time = time.time()
        
        # Test search performance
        admission_files = self.env['acmst.admission.file'].search([])
        self.assertEqual(len(admission_files), 1000)
        
        # Test filtered search
        filtered_files = self.env['acmst.admission.file'].search([
            ('applicant_name', 'like', 'John Doe 1')
        ])
        self.assertGreater(len(filtered_files), 0)
        
        # Test count performance
        count = self.env['acmst.admission.file'].search_count([])
        self.assertEqual(count, 1000)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should search within reasonable time
        self.assertLess(duration, 5.0)
        _logger.info(f"Searched 1000 admission files in {duration:.2f} seconds")

    def test_health_check_creation_performance(self):
        """Test health check creation performance"""
        # Create admission file
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
        
        start_time = time.time()
        
        # Create multiple health checks
        for i in range(100):
            self.env['acmst.health.check'].create({
                'admission_file_id': admission_file.id,
                'examiner_id': self.user.id,
                'height': 175.0 + i,
                'weight': 70.0 + i,
                'medical_fitness': 'fit',
                'blood_type': 'O+',
                'has_chronic_diseases': i % 2 == 0,
                'takes_medications': i % 3 == 0,
                'has_allergies': i % 4 == 0,
                'has_disabilities': i % 5 == 0,
                'follow_up_required': i % 6 == 0,
                'medical_notes': f'Test notes {i}',
                'restrictions': f'Test restrictions {i}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 health checks in {duration:.2f} seconds")

    def test_coordinator_condition_creation_performance(self):
        """Test coordinator condition creation performance"""
        # Create admission file
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
        
        start_time = time.time()
        
        # Create multiple coordinator conditions
        for i in range(100):
            self.env['acmst.coordinator.condition'].create({
                'admission_file_id': admission_file.id,
                'coordinator_id': self.user.id,
                'subject_name': f'Subject {i}',
                'subject_code': f'SUB{i:03d}',
                'level': 'bachelor',
                'description': f'Complete subject {i} prerequisite',
                'deadline': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'notes': f'Must be completed before enrollment {i}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 coordinator conditions in {duration:.2f} seconds")

    def test_admission_approval_creation_performance(self):
        """Test admission approval creation performance"""
        # Create admission file
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
        
        start_time = time.time()
        
        # Create multiple admission approvals
        for i in range(100):
            self.env['acmst.admission.approval'].create({
                'admission_file_id': admission_file.id,
                'approver_id': self.user.id,
                'approval_type': 'ministry',
                'approval_date': fields.Datetime.now(),
                'decision': 'approved',
                'comments': f'Application approved by ministry {i}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 admission approvals in {duration:.2f} seconds")

    def test_portal_application_creation_performance(self):
        """Test portal application creation performance"""
        start_time = time.time()
        
        # Create multiple portal applications
        for i in range(100):
            self.env['acmst.portal.application'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 portal applications in {duration:.2f} seconds")

    def test_workflow_engine_creation_performance(self):
        """Test workflow engine creation performance"""
        start_time = time.time()
        
        # Create multiple workflow engines
        for i in range(100):
            self.env['acmst.workflow.engine'].create({
                'name': f'Test Workflow {i}',
                'model_id': self.env['ir.model']._get('acmst.admission.file').id,
                'description': f'Test workflow {i} for admission files'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 workflow engines in {duration:.2f} seconds")

    def test_audit_log_creation_performance(self):
        """Test audit log creation performance"""
        # Create admission file
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
        
        start_time = time.time()
        
        # Create multiple audit logs
        for i in range(100):
            self.env['acmst.audit.log'].create({
                'name': f'Test Action {i}',
                'res_model_id': self.env['ir.model']._get('acmst.admission.file').id,
                'res_id': admission_file.id,
                'user_id': self.user.id,
                'action_type': 'create',
                'description': f'Test audit log entry {i}'
            })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 100 records within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Created 100 audit logs in {duration:.2f} seconds")

    def test_database_query_performance(self):
        """Test database query performance"""
        # Create test data
        for i in range(1000):
            self.env['acmst.admission.file'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
        
        start_time = time.time()
        
        # Test complex queries
        admission_files = self.env['acmst.admission.file'].search([
            ('applicant_name', 'like', 'John Doe'),
            ('gender', '=', 'male'),
            ('nationality', '=', 'Saudi')
        ])
        
        # Test joins
        admission_files_with_program = self.env['acmst.admission.file'].search([
            ('program_id.name', 'like', 'Test Program')
        ])
        
        # Test aggregations
        count_by_gender = self.env['acmst.admission.file'].read_group(
            [('gender', '=', 'male')],
            ['gender'],
            ['gender']
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should query within reasonable time
        self.assertLess(duration, 5.0)
        _logger.info(f"Executed complex queries in {duration:.2f} seconds")

    def test_memory_usage_performance(self):
        """Test memory usage performance"""
        start_time = time.time()
        
        # Create large dataset
        admission_files = []
        for i in range(1000):
            admission_file = self.env['acmst.admission.file'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
            admission_files.append(admission_file)
        
        # Test memory usage
        all_files = self.env['acmst.admission.file'].search([])
        self.assertEqual(len(all_files), 1000)
        
        # Test reading all records
        all_data = all_files.read(['applicant_name', 'national_id', 'email'])
        self.assertEqual(len(all_data), 1000)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle large dataset within reasonable time
        self.assertLess(duration, 15.0)
        _logger.info(f"Handled large dataset in {duration:.2f} seconds")

    def test_concurrent_access_performance(self):
        """Test concurrent access performance"""
        # Create test data
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
        
        start_time = time.time()
        
        # Simulate concurrent access
        for i in range(100):
            # Read operation
            admission_file.read(['name', 'state'])
            
            # Write operation
            admission_file.write({'notes': f'Updated {i}'})
            
            # Search operation
            self.env['acmst.admission.file'].search([('id', '=', admission_file.id)])
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle concurrent access within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Handled concurrent access in {duration:.2f} seconds")

    def test_workflow_performance(self):
        """Test workflow performance"""
        # Create admission file
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
        
        start_time = time.time()
        
        # Test workflow transitions
        for i in range(100):
            # Reset to draft
            admission_file.write({'state': 'draft'})
            
            # Submit
            admission_file.action_submit()
            
            # Ministry approve
            admission_file.action_ministry_approve()
            
            # Health required
            admission_file.action_health_required()
            
            # Health approved
            admission_file.action_health_approved()
            
            # Coordinator review
            admission_file.action_coordinator_review()
            
            # Manager approve
            admission_file.action_manager_approve()
            
            # Complete
            admission_file.action_complete()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle workflow transitions within reasonable time
        self.assertLess(duration, 15.0)
        _logger.info(f"Handled workflow transitions in {duration:.2f} seconds")

    def test_report_generation_performance(self):
        """Test report generation performance"""
        # Create test data
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
        
        start_time = time.time()
        
        # Test report generation
        for i in range(10):
            # Test admission file report
            report = self.env['ir.actions.report']._get_report_from_name('acmst_admission.admission_file_report')
            if report:
                report_html = report._render_qweb_html(admission_file.ids)
                self.assertTrue(report_html)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should generate reports within reasonable time
        self.assertLess(duration, 10.0)
        _logger.info(f"Generated reports in {duration:.2f} seconds")

    def test_caching_performance(self):
        """Test caching performance"""
        # Create test data
        for i in range(100):
            self.env['acmst.admission.file'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
        
        start_time = time.time()
        
        # Test caching by repeating queries
        for i in range(10):
            # First query (cold cache)
            admission_files = self.env['acmst.admission.file'].search([])
            self.assertEqual(len(admission_files), 100)
            
            # Second query (warm cache)
            admission_files = self.env['acmst.admission.file'].search([])
            self.assertEqual(len(admission_files), 100)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should benefit from caching
        self.assertLess(duration, 5.0)
        _logger.info(f"Tested caching performance in {duration:.2f} seconds")

    def test_index_performance(self):
        """Test index performance"""
        # Create test data with various search patterns
        for i in range(1000):
            self.env['acmst.admission.file'].create({
                'applicant_name': f'John Doe {i}',
                'national_id': f'123456789{i:03d}',
                'phone': f'+966501234{i:03d}',
                'email': f'john.doe{i}@example.com',
                'program_id': self.program.id,
                'batch_id': self.batch.id,
                'birth_date': '1990-01-01',
                'gender': 'male',
                'nationality': 'Saudi',
                'address': f'{i} Test Street, Riyadh',
                'emergency_contact': f'Jane Doe {i}',
                'emergency_phone': f'+966501234{i:03d}'
            })
        
        start_time = time.time()
        
        # Test indexed field searches
        for i in range(100):
            # Search by indexed field
            admission_files = self.env['acmst.admission.file'].search([
                ('applicant_name', 'like', f'John Doe {i}')
            ])
            self.assertEqual(len(admission_files), 1)
            
            # Search by another indexed field
            admission_files = self.env['acmst.admission.file'].search([
                ('national_id', '=', f'123456789{i:03d}')
            ])
            self.assertEqual(len(admission_files), 1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should benefit from indexes
        self.assertLess(duration, 5.0)
        _logger.info(f"Tested index performance in {duration:.2f} seconds")
