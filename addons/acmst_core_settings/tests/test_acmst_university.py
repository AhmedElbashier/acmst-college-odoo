# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestAcmstUniversity(TransactionCase):
    """Test cases for ACMST University model"""

    def setUp(self):
        super().setUp()
        self.University = self.env['acmst.university']
        self.College = self.env['acmst.college']
        self.Program = self.env['acmst.program']
        self.ProgramType = self.env['acmst.program.type']
        self.Batch = self.env['acmst.batch']
        self.AcademicYear = self.env['acmst.academic.year']

    def test_university_creation(self):
        """Test university creation with valid data"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
            'short_name': 'TU',
            'city': 'Test City',
            'established_year': 2000,
            'email': 'test@university.edu',
            'website': 'https://www.testuniversity.edu'
        })
        
        self.assertEqual(university.name, 'Test University')
        self.assertEqual(university.code, 'TU001')
        self.assertTrue(university.active)
        self.assertFalse(university.is_main)

    def test_university_code_unique(self):
        """Test that university codes must be unique"""
        self.University.create({
            'name': 'First University',
            'code': 'UNI001',
        })
        
        with self.assertRaises(ValidationError):
            self.University.create({
                'name': 'Second University',
                'code': 'UNI001',  # Same code
            })

    def test_main_university_unique(self):
        """Test that only one university can be marked as main"""
        self.University.create({
            'name': 'First University',
            'code': 'UNI001',
            'is_main': True,
        })
        
        with self.assertRaises(ValidationError):
            self.University.create({
                'name': 'Second University',
                'code': 'UNI002',
                'is_main': True,
            })

    def test_established_year_validation(self):
        """Test established year validation"""
        # Future year should fail
        with self.assertRaises(ValidationError):
            self.University.create({
                'name': 'Test University',
                'code': 'TU001',
                'established_year': 2030,
            })
        
        # Very old year should fail
        with self.assertRaises(ValidationError):
            self.University.create({
                'name': 'Test University',
                'code': 'TU002',
                'established_year': 1500,
            })

    def test_email_validation(self):
        """Test email format validation"""
        with self.assertRaises(ValidationError):
            self.University.create({
                'name': 'Test University',
                'code': 'TU001',
                'email': 'invalid-email',
            })

    def test_college_count_computation(self):
        """Test college count computation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        # Initially no colleges
        self.assertEqual(university.college_count, 0)
        
        # Create colleges
        college1 = self.College.create({
            'name': 'College 1',
            'code': 'COL1',
            'university_id': university.id,
        })
        college2 = self.College.create({
            'name': 'College 2',
            'code': 'COL2',
            'university_id': university.id,
        })
        
        # Refresh and check count
        university.refresh()
        self.assertEqual(university.college_count, 2)
        
        # Archive one college
        college1.active = False
        university.refresh()
        self.assertEqual(university.college_count, 1)

    def test_program_count_computation(self):
        """Test program count computation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL1',
            'university_id': university.id,
        })
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        # Create programs
        program1 = self.Program.create({
            'name': 'Program 1',
            'code': 'PROG1',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        program2 = self.Program.create({
            'name': 'Program 2',
            'code': 'PROG2',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        university.refresh()
        self.assertEqual(university.program_count, 2)

    def test_student_count_computation(self):
        """Test student count computation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL1',
            'university_id': university.id,
        })
        
        program_type = self.ProgramType.create({
            'name': 'Bachelor',
            'code': 'BACH',
            'level': 'bachelor',
        })
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG1',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        academic_year = self.AcademicYear.create({
            'name': '2024-2025',
            'code': 'AY24-25',
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        # Create batch
        batch = self.Batch.create({
            'name': 'Test Batch',
            'code': 'BATCH1',
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        university.refresh()
        # Student count should be 0 since we don't have student module yet
        self.assertEqual(university.student_count, 0)

    def test_full_address_computation(self):
        """Test full address computation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
            'address': '123 Main St',
            'city': 'Test City',
            'zip': '12345',
        })
        
        expected_address = '123 Main St, Test City, 12345'
        self.assertEqual(university.full_address, expected_address)

    def test_name_get(self):
        """Test name_get method"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        name_get_result = university.name_get()
        expected_name = '[TU001] Test University'
        self.assertEqual(name_get_result[0][1], expected_name)

    def test_toggle_active(self):
        """Test toggle_active method"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL1',
            'university_id': university.id,
        })
        
        # Archive university
        university.active = False
        university.toggle_active()
        
        # College should also be archived
        college.refresh()
        self.assertFalse(college.active)

    def test_get_main_university(self):
        """Test get_main_university method"""
        # No main university initially
        main_university = self.University.get_main_university()
        self.assertFalse(main_university)
        
        # Create main university
        university = self.University.create({
            'name': 'Main University',
            'code': 'MAIN',
            'is_main': True,
        })
        
        main_university = self.University.get_main_university()
        self.assertEqual(main_university.id, university.id)

    def test_sequence_auto_generation(self):
        """Test sequence auto-generation"""
        university1 = self.University.create({
            'name': 'University 1',
            'code': 'U1',
        })
        university2 = self.University.create({
            'name': 'University 2',
            'code': 'U2',
        })
        
        self.assertEqual(university1.sequence, 10)
        self.assertEqual(university2.sequence, 20)
