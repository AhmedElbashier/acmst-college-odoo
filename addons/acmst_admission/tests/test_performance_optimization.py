# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import time
import logging

_logger = logging.getLogger(__name__)


class TestPerformanceOptimization(TransactionCase):
    """Test performance optimization features"""

    def setUp(self):
        super().setUp()
        self.performance_model = self.env['acmst.performance']
        self.admission_file_model = self.env['acmst.admission.file']
        self.health_check_model = self.env['acmst.health.check']
        self.coordinator_condition_model = self.env['acmst.coordinator.condition']

    def test_performance_model_creation(self):
        """Test creating performance optimization records"""
        performance = self.performance_model.create({
            'name': 'Test Optimization',
            'description': 'Test performance optimization',
            'optimization_type': 'query_optimization',
            'model_id': self.env.ref('acmst_admission.model_acmst_admission_file').id,
            'method_name': 'search_read',
            'active': True,
            'performance_gain': 25.0,
            'notes': 'Test optimization notes'
        })
        
        self.assertEqual(performance.name, 'Test Optimization')
        self.assertEqual(performance.optimization_type, 'query_optimization')
        self.assertEqual(performance.performance_gain, 25.0)
        self.assertTrue(performance.active)

    def test_performance_optimization_types(self):
        """Test different optimization types"""
        optimization_types = [
            'query_optimization',
            'caching',
            'indexing',
            'code_refactoring',
            'other'
        ]
        
        for opt_type in optimization_types:
            performance = self.performance_model.create({
                'name': f'Test {opt_type}',
                'optimization_type': opt_type,
                'active': True
            })
            self.assertEqual(performance.optimization_type, opt_type)

    def test_log_query_performance(self):
        """Test logging query performance metrics"""
        result = self.performance_model.log_query_performance(
            'acmst.admission.file',
            'search_read',
            0.5,
            100,
            'Test query performance'
        )
        self.assertTrue(result)

    def test_action_run_optimization_check(self):
        """Test running optimization check"""
        performance = self.performance_model.create({
            'name': 'Test Optimization Check',
            'optimization_type': 'query_optimization',
            'active': True
        })
        
        result = performance.action_run_optimization_check()
        self.assertIn('type', result)
        self.assertEqual(result['type'], 'ir.actions.client')

    def test_get_admission_file_statistics_optimized(self):
        """Test optimized admission file statistics"""
        # Create test admission files
        self.admission_file_model.create({
            'applicant_name': 'Test Student 1',
            'email': 'test1@example.com',
            'phone': '1234567890',
            'state': 'submitted'
        })
        
        self.admission_file_model.create({
            'applicant_name': 'Test Student 2',
            'email': 'test2@example.com',
            'phone': '1234567891',
            'state': 'approved'
        })
        
        stats = self.performance_model.get_admission_file_statistics_optimized()
        self.assertIsInstance(stats, dict)
        self.assertIn('submitted', stats)
        self.assertIn('approved', stats)

    def test_get_health_check_summary_optimized(self):
        """Test optimized health check summary"""
        # Create test health checks
        admission_file = self.admission_file_model.create({
            'applicant_name': 'Test Student',
            'email': 'test@example.com',
            'phone': '1234567890'
        })
        
        self.health_check_model.create({
            'admission_file_id': admission_file.id,
            'medical_fitness': 'fit'
        })
        
        self.health_check_model.create({
            'admission_file_id': admission_file.id,
            'medical_fitness': 'unfit'
        })
        
        stats = self.performance_model.get_health_check_summary_optimized()
        self.assertIsInstance(stats, dict)
        self.assertIn('fit', stats)
        self.assertIn('unfit', stats)

    def test_get_coordinator_condition_summary_optimized(self):
        """Test optimized coordinator condition summary"""
        # Create test coordinator conditions
        admission_file = self.admission_file_model.create({
            'applicant_name': 'Test Student',
            'email': 'test@example.com',
            'phone': '1234567890'
        })
        
        self.coordinator_condition_model.create({
            'admission_file_id': admission_file.id,
            'condition_name': 'Test Condition 1',
            'state': 'pending'
        })
        
        self.coordinator_condition_model.create({
            'admission_file_id': admission_file.id,
            'condition_name': 'Test Condition 2',
            'state': 'completed'
        })
        
        stats = self.performance_model.get_coordinator_condition_summary_optimized()
        self.assertIsInstance(stats, dict)
        self.assertIn('pending', stats)
        self.assertIn('completed', stats)

    def test_get_top_n_admission_files_by_date(self):
        """Test getting top N admission files by date"""
        # Create test admission files
        for i in range(15):
            self.admission_file_model.create({
                'applicant_name': f'Test Student {i}',
                'email': f'test{i}@example.com',
                'phone': f'123456789{i}',
                'state': 'submitted'
            })
        
        # Test with limit 10
        results = self.performance_model.get_top_n_admission_files_by_date(10)
        self.assertEqual(len(results), 10)
        
        # Test with limit 5
        results = self.performance_model.get_top_n_admission_files_by_date(5)
        self.assertEqual(len(results), 5)

    def test_performance_gain_validation(self):
        """Test performance gain validation"""
        # Test valid performance gain
        performance = self.performance_model.create({
            'name': 'Valid Performance Gain',
            'optimization_type': 'query_optimization',
            'performance_gain': 50.0
        })
        self.assertEqual(performance.performance_gain, 50.0)
        
        # Test negative performance gain (should be allowed for testing)
        performance = self.performance_model.create({
            'name': 'Negative Performance Gain',
            'optimization_type': 'query_optimization',
            'performance_gain': -10.0
        })
        self.assertEqual(performance.performance_gain, -10.0)

    def test_performance_model_search(self):
        """Test searching performance records"""
        # Create test records
        self.performance_model.create({
            'name': 'Search Test 1',
            'optimization_type': 'query_optimization',
            'active': True
        })
        
        self.performance_model.create({
            'name': 'Search Test 2',
            'optimization_type': 'caching',
            'active': False
        })
        
        # Test search by name
        records = self.performance_model.search([('name', 'ilike', 'Search Test')])
        self.assertEqual(len(records), 2)
        
        # Test search by optimization type
        records = self.performance_model.search([('optimization_type', '=', 'query_optimization')])
        self.assertEqual(len(records), 1)
        
        # Test search by active status
        records = self.performance_model.search([('active', '=', True)])
        self.assertEqual(len(records), 1)

    def test_performance_model_read_group(self):
        """Test read_group functionality for performance records"""
        # Create test records
        self.performance_model.create({
            'name': 'Group Test 1',
            'optimization_type': 'query_optimization',
            'performance_gain': 25.0
        })
        
        self.performance_model.create({
            'name': 'Group Test 2',
            'optimization_type': 'caching',
            'performance_gain': 40.0
        })
        
        # Test grouping by optimization type
        groups = self.performance_model.read_group(
            domain=[],
            fields=['optimization_type', 'performance_gain'],
            groupby=['optimization_type'],
            lazy=False
        )
        
        self.assertIsInstance(groups, list)
        self.assertEqual(len(groups), 2)

    def test_performance_model_compute_fields(self):
        """Test computed fields in performance model"""
        performance = self.performance_model.create({
            'name': 'Compute Test',
            'optimization_type': 'query_optimization',
            'performance_gain': 30.0
        })
        
        # Test that computed fields are accessible
        self.assertIsNotNone(performance.name)
        self.assertIsNotNone(performance.optimization_type)
        self.assertIsNotNone(performance.performance_gain)

    def test_performance_model_constraints(self):
        """Test model constraints"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.performance_model.create({
                'optimization_type': 'query_optimization'
                # Missing required 'name' field
            })

    def test_performance_model_permissions(self):
        """Test model permissions"""
        # Test that admin can create, read, write, unlink
        admin_user = self.env.ref('base.user_admin')
        performance = self.performance_model.with_user(admin_user).create({
            'name': 'Permission Test',
            'optimization_type': 'query_optimization'
        })
        
        self.assertTrue(performance.exists())
        
        # Test read access
        performance.read(['name', 'optimization_type'])
        
        # Test write access
        performance.write({'name': 'Updated Permission Test'})
        
        # Test unlink access
        performance.unlink()

    def test_performance_model_workflow(self):
        """Test performance model workflow"""
        performance = self.performance_model.create({
            'name': 'Workflow Test',
            'optimization_type': 'query_optimization',
            'active': True
        })
        
        # Test activation/deactivation
        performance.write({'active': False})
        self.assertFalse(performance.active)
        
        performance.write({'active': True})
        self.assertTrue(performance.active)

    def test_performance_model_integration(self):
        """Test performance model integration with other models"""
        # Create admission file
        admission_file = self.admission_file_model.create({
            'applicant_name': 'Integration Test',
            'email': 'integration@example.com',
            'phone': '1234567890'
        })
        
        # Create performance record with model reference
        performance = self.performance_model.create({
            'name': 'Integration Test',
            'optimization_type': 'query_optimization',
            'model_id': self.env.ref('acmst_admission.model_acmst_admission_file').id,
            'method_name': 'search_read'
        })
        
        self.assertEqual(performance.model_id.model, 'acmst.admission.file')
        self.assertEqual(performance.method_name, 'search_read')

    def test_performance_model_data_integrity(self):
        """Test data integrity in performance model"""
        # Create performance record
        performance = self.performance_model.create({
            'name': 'Data Integrity Test',
            'optimization_type': 'query_optimization',
            'performance_gain': 25.5
        })
        
        # Test that data is preserved
        self.assertEqual(performance.name, 'Data Integrity Test')
        self.assertEqual(performance.optimization_type, 'query_optimization')
        self.assertEqual(performance.performance_gain, 25.5)
        
        # Test that data can be updated
        performance.write({
            'name': 'Updated Data Integrity Test',
            'performance_gain': 30.0
        })
        
        self.assertEqual(performance.name, 'Updated Data Integrity Test')
        self.assertEqual(performance.performance_gain, 30.0)

    def test_performance_model_cleanup(self):
        """Test cleanup operations"""
        # Create test records
        performance1 = self.performance_model.create({
            'name': 'Cleanup Test 1',
            'optimization_type': 'query_optimization'
        })
        
        performance2 = self.performance_model.create({
            'name': 'Cleanup Test 2',
            'optimization_type': 'caching'
        })
        
        # Test individual deletion
        performance1.unlink()
        self.assertFalse(performance1.exists())
        
        # Test bulk deletion
        performance2.unlink()
        self.assertFalse(performance2.exists())

    def test_performance_model_benchmarking(self):
        """Test performance benchmarking capabilities"""
        start_time = time.time()
        
        # Create multiple records
        for i in range(100):
            self.performance_model.create({
                'name': f'Benchmark Test {i}',
                'optimization_type': 'query_optimization',
                'performance_gain': float(i)
            })
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Test that creation time is reasonable (less than 10 seconds for 100 records)
        self.assertLess(creation_time, 10.0)
        
        # Test read performance
        start_time = time.time()
        records = self.performance_model.search([])
        end_time = time.time()
        read_time = end_time - start_time
        
        # Test that read time is reasonable (less than 1 second)
        self.assertLess(read_time, 1.0)
        self.assertEqual(len(records), 100)
