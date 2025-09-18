# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class TestAcmstBatchCreationWizard(TransactionCase):
    """Test cases for ACMST Batch Creation Wizard"""

    def setUp(self):
        super().setUp()
        self.Wizard = self.env['acmst.batch.creation.wizard']
        self.University = self.env['acmst.university']
        self.College = self.env['acmst.college']
        self.Program = self.env['acmst.program']
        self.ProgramType = self.env['acmst.program.type']
        self.Batch = self.env['acmst.batch']
        self.AcademicYear = self.env['acmst.academic.year']

    def test_wizard_creation(self):
        """Test wizard creation with valid data"""
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
        
        wizard = self.Wizard.create({
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'batch_count': 2,
            'batch_prefix': 'Batch',
            'start_number': 1,
            'start_date': '2024-09-01',
            'duration_months': 12,
            'max_students': 50,
        })
        
        self.assertEqual(wizard.program_id.id, program.id)
        self.assertEqual(wizard.batch_count, 2)
        self.assertEqual(wizard.batch_prefix, 'Batch')

    def test_batch_count_validation(self):
        """Test batch count validation"""
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'batch_count': 0,  # Invalid count
            })
        
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'batch_count': 100,  # Too many batches
            })

    def test_start_number_validation(self):
        """Test start number validation"""
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'start_number': 0,  # Invalid start number
            })

    def test_duration_validation(self):
        """Test duration validation"""
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'duration_months': 0,  # Invalid duration
            })
        
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'duration_months': 100,  # Too long duration
            })

    def test_max_students_validation(self):
        """Test max students validation"""
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'max_students': 0,  # Invalid max students
            })
        
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'max_students': 2000,  # Too many students
            })

    def test_registration_days_validation(self):
        """Test registration days validation"""
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'registration_days_before': -1,  # Invalid days
            })
        
        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'registration_days_before': 500,  # Too many days
            })

    def test_onchange_program_id(self):
        """Test onchange_program_id method"""
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
            'is_current': True,
        })
        
        wizard = self.Wizard.new({
            'program_id': program.id,
        })
        wizard._onchange_program_id()
        
        self.assertEqual(wizard.college_id.id, college.id)
        self.assertEqual(wizard.university_id.id, university.id)
        self.assertEqual(wizard.academic_year_id.id, academic_year.id)
        self.assertEqual(wizard.start_date, academic_year.start_date)

    def test_onchange_academic_year_id(self):
        """Test onchange_academic_year_id method"""
        academic_year = self.AcademicYear.create({
            'name': '2024-2025',
            'code': 'AY24-25',
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        wizard = self.Wizard.new({
            'academic_year_id': academic_year.id,
        })
        wizard._onchange_academic_year_id()
        
        self.assertEqual(wizard.start_date, academic_year.start_date)

    def test_action_create_batches(self):
        """Test action_create_batches method"""
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
        
        wizard = self.Wizard.create({
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'batch_count': 2,
            'batch_prefix': 'Batch',
            'start_number': 1,
            'start_date': '2024-09-01',
            'duration_months': 12,
            'max_students': 50,
        })
        
        result = wizard.action_create_batches()
        
        # Check that batches were created
        batches = self.Batch.search([('program_id', '=', program.id)])
        self.assertEqual(len(batches), 2)
        
        # Check batch names and codes
        batch1 = batches[0]
        batch2 = batches[1]
        
        self.assertEqual(batch1.name, 'Batch 1')
        self.assertEqual(batch1.code, 'PROG1-AY24-25-01')
        self.assertEqual(batch2.name, 'Batch 2')
        self.assertEqual(batch2.code, 'PROG1-AY24-25-02')

    def test_action_create_batches_missing_data(self):
        """Test action_create_batches with missing data"""
        wizard = self.Wizard.create({})
        
        with self.assertRaises(UserError):
            wizard.action_create_batches()

    def test_get_program_batches_count(self):
        """Test get_program_batches_count method"""
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
        
        # Create some batches
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
        
        count = self.Wizard.get_program_batches_count(program.id)
        self.assertEqual(count, 2)

    def test_get_next_batch_number(self):
        """Test get_next_batch_number method"""
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
        
        # No batches initially
        next_number = self.Wizard.get_next_batch_number(program.id, academic_year.id)
        self.assertEqual(next_number, 1)
        
        # Create some batches
        batch1 = self.Batch.create({
            'name': 'Batch 1',
            'code': 'PROG1-AY24-25-01',
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        batch2 = self.Batch.create({
            'name': 'Batch 2',
            'code': 'PROG1-AY24-25-02',
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        next_number = self.Wizard.get_next_batch_number(program.id, academic_year.id)
        self.assertEqual(next_number, 3)
