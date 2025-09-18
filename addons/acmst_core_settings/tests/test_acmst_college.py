# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAcmstCollege(TransactionCase):
    """Test cases for ACMST College model"""

    def setUp(self):
        super().setUp()
        self.University = self.env['acmst.university']
        self.College = self.env['acmst.college']
        self.Program = self.env['acmst.program']
        self.ProgramType = self.env['acmst.program.type']
        self.Batch = self.env['acmst.batch']
        self.AcademicYear = self.env['acmst.academic.year']

    def test_college_creation(self):
        """Test college creation with valid data"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
            'established_year': 2000,
            'program_types': 'both',
        })
        
        self.assertEqual(college.name, 'Test College')
        self.assertEqual(college.code, 'COL001')
        self.assertEqual(college.university_id.id, university.id)
        self.assertTrue(college.active)

    def test_college_code_unique_per_university(self):
        """Test that college codes must be unique within university"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        self.College.create({
            'name': 'First College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        # Same code in same university should fail
        with self.assertRaises(ValidationError):
            self.College.create({
                'name': 'Second College',
                'code': 'COL001',
                'university_id': university.id,
            })
        
        # Same code in different university should work
        university2 = self.University.create({
            'name': 'Test University 2',
            'code': 'TU002',
        })
        
        college2 = self.College.create({
            'name': 'Second College',
            'code': 'COL001',
            'university_id': university2.id,
        })
        self.assertTrue(college2)

    def test_main_college_unique_per_university(self):
        """Test that only one college can be marked as main per university"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        self.College.create({
            'name': 'First College',
            'code': 'COL001',
            'university_id': university.id,
            'is_main': True,
        })
        
        with self.assertRaises(ValidationError):
            self.College.create({
                'name': 'Second College',
                'code': 'COL002',
                'university_id': university.id,
                'is_main': True,
            })

    def test_established_year_validation(self):
        """Test established year validation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
            'established_year': 2000,
        })
        
        # College established before university should fail
        with self.assertRaises(ValidationError):
            self.College.create({
                'name': 'Test College',
                'code': 'COL001',
                'university_id': university.id,
                'established_year': 1995,
            })

    def test_email_validation(self):
        """Test email format validation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        with self.assertRaises(ValidationError):
            self.College.create({
                'name': 'Test College',
                'code': 'COL001',
                'university_id': university.id,
                'email': 'invalid-email',
            })

    def test_program_count_computation(self):
        """Test program count computation"""
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
        
        college.refresh()
        self.assertEqual(college.program_count, 2)
        
        # Archive one program
        program1.active = False
        college.refresh()
        self.assertEqual(college.program_count, 1)

    def test_batch_count_computation(self):
        """Test batch count computation"""
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
        
        # Create batches
        batch1 = self.Batch.create({
            'name': 'Batch 1',
            'code': 'BATCH1',
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        batch2 = self.Batch.create({
            'name': 'Batch 2',
            'code': 'BATCH2',
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        college.refresh()
        self.assertEqual(college.batch_count, 2)

    def test_faculty_count_computation(self):
        """Test faculty count computation"""
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
        
        # Create user for manager
        manager = self.env['res.users'].create({
            'name': 'Test Manager',
            'login': 'manager@test.com',
            'email': 'manager@test.com',
        })
        
        # Create program with manager
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG1',
            'college_id': college.id,
            'program_type_id': program_type.id,
            'manager_id': manager.id,
        })
        
        college.refresh()
        self.assertEqual(college.faculty_count, 1)

    def test_full_name_computation(self):
        """Test full name computation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        expected_name = 'Test College - Test University'
        self.assertEqual(college.full_name, expected_name)

    def test_name_get(self):
        """Test name_get method"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        name_get_result = college.name_get()
        expected_name = '[COL001] Test College - Test University'
        self.assertEqual(name_get_result[0][1], expected_name)

    def test_toggle_active(self):
        """Test toggle_active method"""
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
            'code': 'PROG1',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        # Archive college
        college.active = False
        college.toggle_active()
        
        # Program should also be archived
        program.refresh()
        self.assertFalse(program.active)

    def test_get_colleges_by_university(self):
        """Test get_colleges_by_university method"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
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
        
        colleges = self.College.get_colleges_by_university(university.id)
        self.assertEqual(len(colleges), 2)
        self.assertIn(college1.id, colleges.ids)
        self.assertIn(college2.id, colleges.ids)

    def test_get_main_college(self):
        """Test get_main_college method"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        # No main college initially
        main_college = self.College.get_main_college(university.id)
        self.assertFalse(main_college)
        
        # Create main college
        college = self.College.create({
            'name': 'Main College',
            'code': 'MAIN',
            'university_id': university.id,
            'is_main': True,
        })
        
        main_college = self.College.get_main_college(university.id)
        self.assertEqual(main_college.id, college.id)

    def test_sequence_auto_generation(self):
        """Test sequence auto-generation"""
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
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
        
        self.assertEqual(college1.sequence, 10)
        self.assertEqual(college2.sequence, 20)
