# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAcmstProgramType(TransactionCase):
    """Test cases for ACMST Program Type model"""

    def setUp(self):
        super().setUp()
        self.ProgramType = self.env['acmst.program.type']
        self.Program = self.env['acmst.program']
        self.University = self.env['acmst.university']
        self.College = self.env['acmst.college']

    def test_program_type_creation(self):
        """Test program type creation with valid data"""
        program_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'short_name': 'BSc',
            'level': 'bachelor',
            'duration_years': 4.0,
            'duration_months': 48,
            'min_credits': 120,
            'max_credits': 150,
            'is_degree': True,
            'requires_thesis': True,
            'requires_internship': True,
        })
        
        self.assertEqual(program_type.name, 'Bachelor of Science')
        self.assertEqual(program_type.code, 'BSC')
        self.assertEqual(program_type.level, 'bachelor')
        self.assertTrue(program_type.is_degree)
        self.assertTrue(program_type.requires_thesis)

    def test_program_type_code_unique(self):
        """Test that program type codes must be unique"""
        self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
        })
        
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Bachelor of Arts',
                'code': 'BSC',  # Same code
            })

    def test_duration_validation(self):
        """Test duration validation"""
        # Negative duration should fail
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Test Program',
                'code': 'TEST',
                'duration_years': -1,
            })
        
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Test Program',
                'code': 'TEST2',
                'duration_months': -1,
            })

    def test_duration_consistency(self):
        """Test duration consistency between years and months"""
        # Inconsistent durations should fail
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Test Program',
                'code': 'TEST',
                'duration_years': 4.0,  # 48 months
                'duration_months': 60,  # 5 years
            })

    def test_credits_validation(self):
        """Test credits validation"""
        # Negative credits should fail
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Test Program',
                'code': 'TEST',
                'min_credits': -1,
            })
        
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Test Program',
                'code': 'TEST2',
                'max_credits': -1,
            })
        
        # Min credits greater than max should fail
        with self.assertRaises(ValidationError):
            self.ProgramType.create({
                'name': 'Test Program',
                'code': 'TEST3',
                'min_credits': 150,
                'max_credits': 120,
            })

    def test_program_count_computation(self):
        """Test program count computation"""
        program_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'level': 'bachelor',
        })
        
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
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
        
        program_type.refresh()
        self.assertEqual(program_type.program_count, 2)
        
        # Archive one program
        program1.active = False
        program_type.refresh()
        self.assertEqual(program_type.program_count, 1)

    def test_student_count_computation(self):
        """Test student count computation"""
        program_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'level': 'bachelor',
        })
        
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG1',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        program_type.refresh()
        # Student count should be 0 since we don't have student module yet
        self.assertEqual(program_type.student_count, 0)

    def test_name_get(self):
        """Test name_get method"""
        program_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
        })
        
        name_get_result = program_type.name_get()
        expected_name = '[BSC] Bachelor of Science'
        self.assertEqual(name_get_result[0][1], expected_name)

    def test_toggle_active(self):
        """Test toggle_active method"""
        program_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'level': 'bachelor',
        })
        
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
        })
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG1',
            'college_id': college.id,
            'program_type_id': program_type.id,
        })
        
        # Archive program type
        program_type.active = False
        program_type.toggle_active()
        
        # Program should also be archived
        program.refresh()
        self.assertFalse(program.active)

    def test_get_program_types_by_level(self):
        """Test get_program_types_by_level method"""
        bachelor_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'level': 'bachelor',
        })
        
        master_type = self.ProgramType.create({
            'name': 'Master of Science',
            'code': 'MSC',
            'level': 'master',
        })
        
        bachelor_types = self.ProgramType.get_program_types_by_level('bachelor')
        self.assertEqual(len(bachelor_types), 1)
        self.assertEqual(bachelor_types[0].id, bachelor_type.id)

    def test_get_degree_program_types(self):
        """Test get_degree_program_types method"""
        degree_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'level': 'bachelor',
            'is_degree': True,
        })
        
        cert_type = self.ProgramType.create({
            'name': 'Certificate',
            'code': 'CERT',
            'level': 'certificate',
            'is_degree': False,
        })
        
        degree_types = self.ProgramType.get_degree_program_types()
        self.assertEqual(len(degree_types), 1)
        self.assertEqual(degree_types[0].id, degree_type.id)

    def test_get_certificate_program_types(self):
        """Test get_certificate_program_types method"""
        degree_type = self.ProgramType.create({
            'name': 'Bachelor of Science',
            'code': 'BSC',
            'level': 'bachelor',
            'is_degree': True,
        })
        
        cert_type = self.ProgramType.create({
            'name': 'Certificate',
            'code': 'CERT',
            'level': 'certificate',
            'is_degree': False,
        })
        
        cert_types = self.ProgramType.get_certificate_program_types()
        self.assertEqual(len(cert_types), 1)
        self.assertEqual(cert_types[0].id, cert_type.id)

    def test_sequence_auto_generation(self):
        """Test sequence auto-generation"""
        program_type1 = self.ProgramType.create({
            'name': 'Type 1',
            'code': 'TYPE1',
        })
        program_type2 = self.ProgramType.create({
            'name': 'Type 2',
            'code': 'TYPE2',
        })
        
        self.assertEqual(program_type1.sequence, 10)
        self.assertEqual(program_type2.sequence, 20)
