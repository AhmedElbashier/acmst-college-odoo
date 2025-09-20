# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestAdmissionApproval(TransactionCase):
    """Test cases for admission approval model"""

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
        
        self.approver = self.env['res.users'].create({
            'name': 'Test Approver',
            'login': 'approver',
            'email': 'approver@example.com'
        })
        
        self.admission_file = self.env['acmst.admission.file'].create({
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

    def test_create_admission_approval(self):
        """Test creating an admission approval"""
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry'
        })
        
        self.assertEqual(approval.admission_file_id, self.admission_file)
        self.assertEqual(approval.approver_id, self.approver)
        self.assertEqual(approval.approval_type, 'ministry')
        self.assertEqual(approval.decision, 'approved')

    def test_admission_approval_validation(self):
        """Test admission approval validation"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.admission.approval'].create({
                'admission_file_id': self.admission_file.id,
                'approver_id': self.approver.id,
                # Missing required fields
            })

    def test_admission_approval_decision_validation(self):
        """Test admission approval decision validation"""
        # Test valid decisions
        valid_decisions = ['approved', 'rejected', 'conditional', 'pending']
        for decision in valid_decisions:
            approval = self.env['acmst.admission.approval'].create({
                'admission_file_id': self.admission_file.id,
                'approver_id': self.approver.id,
                'approval_type': 'ministry',
                'approval_date': fields.Datetime.now(),
                'decision': decision,
                'comments': f'Application {decision} by ministry'
            })
            self.assertEqual(approval.decision, decision)

    def test_admission_approval_type_validation(self):
        """Test admission approval type validation"""
        # Test valid approval types
        valid_types = ['ministry', 'health', 'coordinator', 'manager', 'final', 'completion']
        for approval_type in valid_types:
            approval = self.env['acmst.admission.approval'].create({
                'admission_file_id': self.admission_file.id,
                'approver_id': self.approver.id,
                'approval_type': approval_type,
                'approval_date': fields.Datetime.now(),
                'decision': 'approved',
                'comments': f'Application approved by {approval_type}'
            })
            self.assertEqual(approval.approval_type, approval_type)

    def test_admission_approval_workflow(self):
        """Test admission approval workflow"""
        # Create multiple approvals for different stages
        ministry_approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry'
        })
        
        health_approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'health',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Health check approved'
        })
        
        coordinator_approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'coordinator',
            'approval_date': fields.Datetime.now(),
            'decision': 'conditional',
            'comments': 'Approved with conditions'
        })
        
        manager_approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'manager',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Final approval granted'
        })
        
        # Check approvals are created
        self.assertEqual(len(self.admission_file.approval_ids), 4)
        self.assertIn(ministry_approval, self.admission_file.approval_ids)
        self.assertIn(health_approval, self.admission_file.approval_ids)
        self.assertIn(coordinator_approval, self.admission_file.approval_ids)
        self.assertIn(manager_approval, self.admission_file.approval_ids)

    def test_admission_approval_conditional_decision(self):
        """Test conditional approval decision"""
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'coordinator',
            'approval_date': fields.Datetime.now(),
            'decision': 'conditional',
            'comments': 'Approved with conditions',
            'conditions': 'Complete mathematics prerequisite'
        })
        
        self.assertEqual(approval.decision, 'conditional')
        self.assertEqual(approval.conditions, 'Complete mathematics prerequisite')

    def test_admission_approval_rejection(self):
        """Test rejection approval decision"""
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': 'Application rejected due to incomplete documentation',
            'rejection_reason': 'Missing required documents'
        })
        
        self.assertEqual(approval.decision, 'rejected')
        self.assertEqual(approval.rejection_reason, 'Missing required documents')

    def test_admission_approval_pending_decision(self):
        """Test pending approval decision"""
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'manager',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Under review by management'
        })
        
        self.assertEqual(approval.decision, 'pending')
        self.assertEqual(approval.comments, 'Under review by management')

    def test_admission_approval_attachments(self):
        """Test admission approval attachments"""
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry'
        })
        
        # Test attachment fields
        self.assertFalse(approval.attachments)

    def test_admission_approval_workflow_with_conditions(self):
        """Test admission approval workflow with conditions"""
        # Create conditional approval
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'coordinator',
            'approval_date': fields.Datetime.now(),
            'decision': 'conditional',
            'comments': 'Approved with conditions',
            'conditions': 'Complete mathematics prerequisite, Submit health certificate'
        })
        
        # Check conditions
        self.assertEqual(approval.conditions, 'Complete mathematics prerequisite, Submit health certificate')
        
        # Update conditions
        approval.write({'conditions': 'Complete mathematics prerequisite, Submit health certificate, Pass English test'})
        self.assertEqual(approval.conditions, 'Complete mathematics prerequisite, Submit health certificate, Pass English test')

    def test_admission_approval_workflow_with_rejection(self):
        """Test admission approval workflow with rejection"""
        # Create rejection approval
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'rejected',
            'comments': 'Application rejected due to incomplete documentation',
            'rejection_reason': 'Missing required documents: Transcript, Recommendation letter'
        })
        
        # Check rejection details
        self.assertEqual(approval.decision, 'rejected')
        self.assertEqual(approval.rejection_reason, 'Missing required documents: Transcript, Recommendation letter')
        
        # Update rejection reason
        approval.write({'rejection_reason': 'Missing required documents: Transcript, Recommendation letter, Health certificate'})
        self.assertEqual(approval.rejection_reason, 'Missing required documents: Transcript, Recommendation letter, Health certificate')

    def test_admission_approval_workflow_with_pending(self):
        """Test admission approval workflow with pending"""
        # Create pending approval
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'manager',
            'approval_date': fields.Datetime.now(),
            'decision': 'pending',
            'comments': 'Under review by management',
            'next_review_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        })
        
        # Check pending details
        self.assertEqual(approval.decision, 'pending')
        self.assertEqual(approval.comments, 'Under review by management')
        self.assertEqual(approval.next_review_date, (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'))

    def test_admission_approval_workflow_with_attachments(self):
        """Test admission approval workflow with attachments"""
        # Create approval with attachments
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry',
            'attachments': 'Approval letter, Ministry certificate'
        })
        
        # Check attachments
        self.assertEqual(approval.attachments, 'Approval letter, Ministry certificate')
        
        # Update attachments
        approval.write({'attachments': 'Approval letter, Ministry certificate, Official stamp'})
        self.assertEqual(approval.attachments, 'Approval letter, Ministry certificate, Official stamp')

    def test_admission_approval_workflow_with_comments(self):
        """Test admission approval workflow with comments"""
        # Create approval with comments
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry after thorough review'
        })
        
        # Check comments
        self.assertEqual(approval.comments, 'Application approved by ministry after thorough review')
        
        # Update comments
        approval.write({'comments': 'Application approved by ministry after thorough review and verification'})
        self.assertEqual(approval.comments, 'Application approved by ministry after thorough review and verification')

    def test_admission_approval_workflow_with_dates(self):
        """Test admission approval workflow with dates"""
        # Create approval with specific dates
        approval_date = fields.Datetime.now()
        next_review_date = date.today() + timedelta(days=7)
        
        approval = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'manager',
            'approval_date': approval_date,
            'decision': 'pending',
            'comments': 'Under review by management',
            'next_review_date': next_review_date.strftime('%Y-%m-%d')
        })
        
        # Check dates
        self.assertEqual(approval.approval_date, approval_date)
        self.assertEqual(approval.next_review_date, next_review_date.strftime('%Y-%m-%d'))

    def test_admission_approval_workflow_with_multiple_approvers(self):
        """Test admission approval workflow with multiple approvers"""
        # Create second approver
        approver2 = self.env['res.users'].create({
            'name': 'Test Approver 2',
            'login': 'approver2',
            'email': 'approver2@example.com'
        })
        
        # Create approvals with different approvers
        approval1 = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': self.approver.id,
            'approval_type': 'ministry',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Application approved by ministry'
        })
        
        approval2 = self.env['acmst.admission.approval'].create({
            'admission_file_id': self.admission_file.id,
            'approver_id': approver2.id,
            'approval_type': 'health',
            'approval_date': fields.Datetime.now(),
            'decision': 'approved',
            'comments': 'Health check approved'
        })
        
        # Check approvals
        self.assertEqual(len(self.admission_file.approval_ids), 2)
        self.assertIn(approval1, self.admission_file.approval_ids)
        self.assertIn(approval2, self.admission_file.approval_ids)
        self.assertEqual(approval1.approver_id, self.approver)
        self.assertEqual(approval2.approver_id, approver2)
