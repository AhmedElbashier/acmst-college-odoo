# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from odoo import api


class TestAcmstSecurity(TransactionCase):
    """Security tests for ACMST Core Settings module"""

    def setUp(self):
        super().setUp()
        self.University = self.env['acmst.university']
        self.College = self.env['acmst.college']
        self.Program = self.env['acmst.program']
        self.ProgramType = self.env['acmst.program.type']
        self.Batch = self.env['acmst.batch']
        self.AcademicYear = self.env['acmst.academic.year']
        self.AcademicRules = self.env['acmst.academic.rules']

    def test_admin_group_access(self):
        """Test admin group has full access to all models"""
        # Admin should have full access
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        self.assertTrue(university)
        self.assertTrue(university.write({'name': 'Updated University'}))
        self.assertTrue(university.unlink())

    def test_manager_group_access(self):
        """Test manager group access"""
        # Create manager user
        manager_user = self.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager@test.com',
            'email': 'manager@test.com',
        })
        
        # Add to manager group
        manager_group = self.env.ref('acmst_core_settings.group_manager')
        manager_user.groups_id = [(4, manager_group.id)]
        
        # Test access with manager user
        with self.env.do_as(manager_user):
            university = self.University.create({
                'name': 'Test University',
                'code': 'TU001',
            })
            
            self.assertTrue(university)
            self.assertTrue(university.write({'name': 'Updated University'}))
            # Manager should not be able to delete
            with self.assertRaises(AccessError):
                university.unlink()

    def test_coordinator_group_access(self):
        """Test coordinator group access"""
        # Create coordinator user
        coordinator_user = self.env['res.users'].create({
            'name': 'Coordinator User',
            'login': 'coordinator@test.com',
            'email': 'coordinator@test.com',
        })
        
        # Add to coordinator group
        coordinator_group = self.env.ref('acmst_core_settings.group_coordinator')
        coordinator_user.groups_id = [(4, coordinator_group.id)]
        
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
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG001',
            'college_id': college.id,
            'program_type_id': program_type.id,
            'coordinator_id': coordinator_user.id,
        })
        
        # Test access with coordinator user
        with self.env.do_as(coordinator_user):
            # Should be able to read program they coordinate
            self.assertTrue(program.read())
            self.assertTrue(program.write({'name': 'Updated Program'}))
            
            # Should not be able to delete
            with self.assertRaises(AccessError):
                program.unlink()
            
            # Should not be able to create new programs
            with self.assertRaises(AccessError):
                self.Program.create({
                    'name': 'New Program',
                    'code': 'PROG002',
                    'college_id': college.id,
                    'program_type_id': program_type.id,
                })

    def test_dean_group_access(self):
        """Test dean group access"""
        # Create dean user
        dean_user = self.env['res.users'].create({
            'name': 'Dean User',
            'login': 'dean@test.com',
            'email': 'dean@test.com',
        })
        
        # Add to dean group
        dean_group = self.env.ref('acmst_core_settings.group_dean')
        dean_user.groups_id = [(4, dean_group.id)]
        
        # Create university and college
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university.id,
            'dean_id': dean_user.id,
        })
        
        # Test access with dean user
        with self.env.do_as(dean_user):
            # Should be able to read college they are dean of
            self.assertTrue(college.read())
            self.assertTrue(college.write({'name': 'Updated College'}))
            
            # Should not be able to delete
            with self.assertRaises(AccessError):
                college.unlink()
            
            # Should not be able to create new colleges
            with self.assertRaises(AccessError):
                self.College.create({
                    'name': 'New College',
                    'code': 'COL002',
                    'university_id': university.id,
                })

    def test_viewer_group_access(self):
        """Test viewer group access"""
        # Create viewer user
        viewer_user = self.env['res.users'].create({
            'name': 'Viewer User',
            'login': 'viewer@test.com',
            'email': 'viewer@test.com',
        })
        
        # Add to viewer group
        viewer_group = self.env.ref('acmst_core_settings.group_viewer')
        viewer_user.groups_id = [(4, viewer_group.id)]
        
        # Create university
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        # Test access with viewer user
        with self.env.do_as(viewer_user):
            # Should be able to read
            self.assertTrue(university.read())
            
            # Should not be able to write
            with self.assertRaises(AccessError):
                university.write({'name': 'Updated University'})
            
            # Should not be able to create
            with self.assertRaises(AccessError):
                self.University.create({
                    'name': 'New University',
                    'code': 'TU002',
                })
            
            # Should not be able to delete
            with self.assertRaises(AccessError):
                university.unlink()

    def test_record_rules_university(self):
        """Test university record rules"""
        # Create two universities
        university1 = self.University.create({
            'name': 'University 1',
            'code': 'U1',
        })
        
        university2 = self.University.create({
            'name': 'University 2',
            'code': 'U2',
        })
        
        # Create dean for university1
        dean_user = self.env['res.users'].create({
            'name': 'Dean User',
            'login': 'dean@test.com',
            'email': 'dean@test.com',
        })
        
        dean_group = self.env.ref('acmst_core_settings.group_dean')
        dean_user.groups_id = [(4, dean_group.id)]
        
        college = self.College.create({
            'name': 'Test College',
            'code': 'COL001',
            'university_id': university1.id,
            'dean_id': dean_user.id,
        })
        
        # Test record rules with dean user
        with self.env.do_as(dean_user):
            # Should be able to access college they are dean of
            colleges = self.College.search([])
            self.assertIn(college.id, colleges.ids)
            
            # Should not be able to access other colleges
            other_college = self.College.create({
                'name': 'Other College',
                'code': 'COL002',
                'university_id': university2.id,
            })
            
            colleges = self.College.search([])
            self.assertNotIn(other_college.id, colleges.ids)

    def test_record_rules_program(self):
        """Test program record rules"""
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
        
        # Create coordinator user
        coordinator_user = self.env['res.users'].create({
            'name': 'Coordinator User',
            'login': 'coordinator@test.com',
            'email': 'coordinator@test.com',
        })
        
        coordinator_group = self.env.ref('acmst_core_settings.group_coordinator')
        coordinator_user.groups_id = [(4, coordinator_group.id)]
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG001',
            'college_id': college.id,
            'program_type_id': program_type.id,
            'coordinator_id': coordinator_user.id,
        })
        
        # Test record rules with coordinator user
        with self.env.do_as(coordinator_user):
            # Should be able to access program they coordinate
            programs = self.Program.search([])
            self.assertIn(program.id, programs.ids)
            
            # Should not be able to access other programs
            other_program = self.Program.create({
                'name': 'Other Program',
                'code': 'PROG002',
                'college_id': college.id,
                'program_type_id': program_type.id,
            })
            
            programs = self.Program.search([])
            self.assertNotIn(other_program.id, programs.ids)

    def test_record_rules_batch(self):
        """Test batch record rules"""
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
        
        # Create coordinator user
        coordinator_user = self.env['res.users'].create({
            'name': 'Coordinator User',
            'login': 'coordinator@test.com',
            'email': 'coordinator@test.com',
        })
        
        coordinator_group = self.env.ref('acmst_core_settings.group_coordinator')
        coordinator_user.groups_id = [(4, coordinator_group.id)]
        
        program = self.Program.create({
            'name': 'Test Program',
            'code': 'PROG001',
            'college_id': college.id,
            'program_type_id': program_type.id,
            'coordinator_id': coordinator_user.id,
        })
        
        academic_year = self.AcademicYear.create({
            'name': '2024-2025',
            'code': 'AY24-25',
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        batch = self.Batch.create({
            'name': 'Test Batch',
            'code': 'BATCH001',
            'program_id': program.id,
            'academic_year_id': academic_year.id,
            'start_date': '2024-09-01',
            'end_date': '2025-08-31',
        })
        
        # Test record rules with coordinator user
        with self.env.do_as(coordinator_user):
            # Should be able to access batch of program they coordinate
            batches = self.Batch.search([])
            self.assertIn(batch.id, batches.ids)
            
            # Should not be able to access other batches
            other_program = self.Program.create({
                'name': 'Other Program',
                'code': 'PROG002',
                'college_id': college.id,
                'program_type_id': program_type.id,
            })
            
            other_batch = self.Batch.create({
                'name': 'Other Batch',
                'code': 'BATCH002',
                'program_id': other_program.id,
                'academic_year_id': academic_year.id,
                'start_date': '2024-09-01',
                'end_date': '2025-08-31',
            })
            
            batches = self.Batch.search([])
            self.assertNotIn(other_batch.id, batches.ids)

    def test_academic_rules_access(self):
        """Test academic rules access"""
        # Create university
        university = self.University.create({
            'name': 'Test University',
            'code': 'TU001',
        })
        
        # Create manager user
        manager_user = self.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager@test.com',
            'email': 'manager@test.com',
        })
        
        manager_group = self.env.ref('acmst_core_settings.group_manager')
        manager_user.groups_id = [(4, manager_group.id)]
        
        # Test access with manager user
        with self.env.do_as(manager_user):
            rule = self.AcademicRules.create({
                'name': 'Test Rule',
                'code': 'RULE001',
                'rule_type': 'attendance',
                'university_id': university.id,
                'effective_date': '2024-01-01',
            })
            
            self.assertTrue(rule)
            self.assertTrue(rule.write({'name': 'Updated Rule'}))
            
            # Manager should not be able to delete
            with self.assertRaises(AccessError):
                rule.unlink()

    def test_batch_creation_wizard_access(self):
        """Test batch creation wizard access"""
        # Create coordinator user
        coordinator_user = self.env['res.users'].create({
            'name': 'Coordinator User',
            'login': 'coordinator@test.com',
            'email': 'coordinator@test.com',
        })
        
        coordinator_group = self.env.ref('acmst_core_settings.group_coordinator')
        coordinator_user.groups_id = [(4, coordinator_group.id)]
        
        # Test access with coordinator user
        with self.env.do_as(coordinator_user):
            wizard = self.env['acmst.batch.creation.wizard'].create({})
            self.assertTrue(wizard)
            
            # Should be able to create wizard
            self.assertTrue(wizard.write({'batch_count': 5}))
            
            # Should not be able to delete
            with self.assertRaises(AccessError):
                wizard.unlink()
