# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
import time
from odoo import api


class TestAcmstPerformance(TransactionCase):
    """Performance tests for ACMST Core Settings module"""

    def setUp(self):
        super().setUp()
        self.University = self.env['acmst.university']
        self.College = self.env['acmst.college']
        self.Program = self.env['acmst.program']
        self.ProgramType = self.env['acmst.program.type']
        self.Batch = self.env['acmst.batch']
        self.AcademicYear = self.env['acmst.academic.year']
        self.AcademicRules = self.env['acmst.academic.rules']

    def test_university_search_performance(self):
        """Test university search performance with large dataset"""
        # Create multiple universities
        start_time = time.time()
        
        for i in range(100):
            self.University.create({
                'name': f'University {i}',
                'code': f'UNI{i:03d}',
                'city': f'City {i}',
            })
        
        creation_time = time.time() - start_time
        print(f"Created 100 universities in {creation_time:.2f} seconds")
        
        # Test search performance
        start_time = time.time()
        universities = self.University.search([('active', '=', True)])
        search_time = time.time() - start_time
        
        print(f"Searched {len(universities)} universities in {search_time:.2f} seconds")
        self.assertLess(search_time, 1.0)  # Should complete in less than 1 second

    def test_college_search_performance(self):
        """Test college search performance with large dataset"""
        # Create university first
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        # Create multiple colleges
        start_time = time.time()
        
        for i in range(100):
            self.College.create({
                'name': f'College {i}',
                'code': f'COL{i:03d}',
                'university_id': university.id,
            })
        
        creation_time = time.time() - start_time
        print(f"Created 100 colleges in {creation_time:.2f} seconds")
        
        # Test search performance
        start_time = time.time()
        colleges = self.College.search([('university_id', '=', university.id)])
        search_time = time.time() - start_time
        
        print(f"Searched {len(colleges)} colleges in {search_time:.2f} seconds")
        self.assertLess(search_time, 1.0)

    def test_program_search_performance(self):
        """Test program search performance with large dataset"""
        # Create university and college
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        # Create multiple programs
        start_time = time.time()
        
        for i in range(100):
            self.Program.create({
                'name': f'Program {i}',
                'code': f'PROG{i:03d}',
                'college_id': college.id,
                'program_type_id': program_type.id,
            })
        
        creation_time = time.time() - start_time
        print(f"Created 100 programs in {creation_time:.2f} seconds")
        
        # Test search performance
        start_time = time.time()
        programs = self.Program.search([('college_id', '=', college.id)])
        search_time = time.time() - start_time
        
        print(f"Searched {len(programs)} programs in {search_time:.2f} seconds")
        self.assertLess(search_time, 1.0)

    def test_batch_search_performance(self):
        """Test batch search performance with large dataset"""
        # Create university, college, program, and academic year
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG001',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        academic_year = self.AcademicYear.create({
            'name': '2024-2025',
            'code': 'AY24-25',
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        # Create multiple batches
        start_time = time.time()
        
        for i in range(100):
            self.Batch.create({
                'name': f'Batch {i}',
                'code': f'BATCH{i:03d}',
                'program_id': program.id,
                'academic_year_id': academic_year.id,
                'start_date': '2024-09-01',
                'end_date': '2025-08-31',
            })
        
        creation_time = time.time() - start_time
        print(f"Created 100 batches in {creation_time:.2f} seconds")
        
        # Test search performance
        start_time = time.time()
        batches = self.Batch.search([('program_id', '=', program.id)])
        search_time = time.time() - start_time
        
        print(f"Searched {len(batches)} batches in {search_time:.2f} seconds")
        self.assertLess(search_time, 1.0)

    def test_computed_fields_performance(self):
        """Test computed fields performance"""
        # Create university with colleges and programs
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        colleges = []
        for i in range(10):
            college = self.College.create({
                'name': f'College {i}',
                'code': f'COL{i:03d}',
                'university_id': university.id,
            })
            colleges.append(college)
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        programs = []
        for college in colleges:
            for i in range(5):
                program = self.Program.create({
                    'name': f'Program {college.name} {i}',
                    'code': f'PROG{college.code}{i:02d}',
                    'college_id': college.id,
                    'program_type_id': program_type.id,
                })
                programs.append(program)
        
        # Test computed fields performance
        start_time = time.time()
        university.refresh()
        computation_time = time.time() - start_time
        
        print(f"Computed university statistics in {computation_time:.2f} seconds")
        self.assertEqual(university.college_count, 10)
        self.assertEqual(university.program_count, 50)
        self.assertLess(computation_time, 2.0)

    def test_academic_rules_search_performance(self):
        """Test academic rules search performance"""
        # Create university and college
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        # Create multiple academic rules
        start_time = time.time()
        
        for i in range(100):
            self.AcademicRules.create({
                'name': f'Rule {i}',
                'code': f'RULE{i:03d}',
                'rule_type': 'attendance',
                'university_id': university.id,
                'effective_date': '2024-01-01',
            })
        
        creation_time = time.time() - start_time
        print(f"Created 100 academic rules in {creation_time:.2f} seconds")
        
        # Test search performance
        start_time = time.time()
        rules = self.AcademicRules.search([('university_id', '=', university.id)])
        search_time = time.time() - start_time
        
        print(f"Searched {len(rules)} academic rules in {search_time:.2f} seconds")
        self.assertLess(search_time, 1.0)

    def test_batch_creation_wizard_performance(self):
        """Test batch creation wizard performance"""
        # Create university, college, program, and academic year
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG001',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        academic_year = self.AcademicYear.create({
            'name': '2024-2025',
            'code': 'AY24-25',
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        # Test batch creation wizard performance
        start_time = time.time()
        
        wizard = self.env['acmst.batch.creation.wizard'].create({
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'batch_count': 50,
            'batch_prefix': 'Batch',
            'start_number': 1,
            'start_date': '2024-09-01',
            'duration_months': 12,
            'max_students': 50,
        })
        
        wizard.action_create_batches()
        
        creation_time = time.time() - start_time
        print(f"Created 50 batches via wizard in {creation_time:.2f} seconds")
        
        # Verify batches were created
        batches = self.Batch.search([('program_id', '=', program.id)])
        self.assertEqual(len(batches), 50)
        self.assertLess(creation_time, 5.0)

    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        colleges = []
        for i in range(50):
            college = self.College.create({
                'name': f'College {i}',
                'code': f'COL{i:03d}',
                'university_id': university.id,
            })
            colleges.append(college)
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        programs = []
        for college in colleges:
            for i in range(10):
                program = self.Program.create({
                    'name': f'Program {college.name} {i}',
                    'code': f'PROG{college.code}{i:02d}',
                    'college_id': college.id,
                    'program_type_id': program_type.id,
                })
                programs.append(program)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage increased by {memory_increase:.2f} MB")
        self.assertLess(memory_increase, 100)  # Should not increase by more than 100MB
