# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestWorkflowEngine(TransactionCase):
    """Test cases for workflow engine model"""

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

    def test_create_workflow_engine(self):
        """Test creating a workflow engine"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertEqual(workflow.model_id.model, 'acmst.admission.file')
        self.assertEqual(workflow.description, 'Test workflow for admission files')
        self.assertTrue(workflow.active)

    def test_create_workflow_state(self):
        """Test creating a workflow state"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        state = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'description': 'Initial state'
        })
        
        self.assertEqual(state.name, 'draft')
        self.assertEqual(state.workflow_id, workflow)
        self.assertTrue(state.is_initial)
        self.assertEqual(state.description, 'Initial state')

    def test_create_workflow_rule(self):
        """Test creating a workflow rule"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        self.assertEqual(rule.name, 'Test Rule')
        self.assertEqual(rule.workflow_id, workflow)
        self.assertEqual(rule.trigger_event, 'on_create')
        self.assertEqual(rule.action_type, 'update_field')
        self.assertEqual(rule.action_value, 'draft')

    def test_workflow_engine_validation(self):
        """Test workflow engine validation"""
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.workflow.engine'].create({
                'name': 'Test Workflow',
                # Missing required fields
            })

    def test_workflow_state_validation(self):
        """Test workflow state validation"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.workflow.state'].create({
                'workflow_id': workflow.id,
                # Missing required fields
            })

    def test_workflow_rule_validation(self):
        """Test workflow rule validation"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Test required fields
        with self.assertRaises(ValidationError):
            self.env['acmst.workflow.rule'].create({
                'workflow_id': workflow.id,
                # Missing required fields
            })

    def test_workflow_engine_initial_state_validation(self):
        """Test workflow engine initial state validation"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Test active workflow must have initial state
        with self.assertRaises(ValidationError):
            workflow.write({'active': True})

    def test_workflow_state_single_initial_validation(self):
        """Test workflow state single initial validation"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create first initial state
        state1 = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'description': 'Initial state'
        })
        
        # Try to create second initial state
        with self.assertRaises(ValidationError):
            self.env['acmst.workflow.state'].create({
                'name': 'draft2',
                'workflow_id': workflow.id,
                'is_initial': True,
                'description': 'Second initial state'
            })

    def test_workflow_rule_condition_domain_validation(self):
        """Test workflow rule condition domain validation"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Test invalid condition domain
        with self.assertRaises(ValidationError):
            self.env['acmst.workflow.rule'].create({
                'name': 'Test Rule',
                'workflow_id': workflow.id,
                'trigger_event': 'on_create',
                'action_type': 'update_field',
                'action_value': 'draft',
                'condition_domain': 'invalid_domain'
            })

    def test_workflow_engine_workflow_states(self):
        """Test workflow engine workflow states"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create states
        state1 = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'description': 'Initial state'
        })
        
        state2 = self.env['acmst.workflow.state'].create({
            'name': 'submitted',
            'workflow_id': workflow.id,
            'is_final': False,
            'description': 'Submitted state'
        })
        
        state3 = self.env['acmst.workflow.state'].create({
            'name': 'approved',
            'workflow_id': workflow.id,
            'is_final': True,
            'description': 'Final state'
        })
        
        # Check states
        self.assertEqual(len(workflow.state_ids), 3)
        self.assertIn(state1, workflow.state_ids)
        self.assertIn(state2, workflow.state_ids)
        self.assertIn(state3, workflow.state_ids)

    def test_workflow_engine_workflow_rules(self):
        """Test workflow engine workflow rules"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rules
        rule1 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 1',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        rule2 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 2',
            'workflow_id': workflow.id,
            'trigger_event': 'on_update',
            'action_type': 'send_email',
            'action_value': 'test@example.com'
        })
        
        # Check rules
        self.assertEqual(len(workflow.rule_ids), 2)
        self.assertIn(rule1, workflow.rule_ids)
        self.assertIn(rule2, workflow.rule_ids)

    def test_workflow_engine_action_view_states(self):
        """Test workflow engine action view states"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create state
        state = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'description': 'Initial state'
        })
        
        # Test action view states
        action = workflow.action_view_states()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'acmst.workflow.state')
        self.assertEqual(action['domain'], [('workflow_id', '=', workflow.id)])

    def test_workflow_engine_action_view_rules(self):
        """Test workflow engine action view rules"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rule
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        # Test action view rules
        action = workflow.action_view_rules()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'acmst.workflow.rule')
        self.assertEqual(action['domain'], [('workflow_id', '=', workflow.id)])

    def test_workflow_rule_evaluate_condition(self):
        """Test workflow rule condition evaluation"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rule with condition
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft',
            'condition_domain': '[("state", "=", "draft")]'
        })
        
        # Test condition evaluation
        self.assertTrue(rule._evaluate_condition(self.admission_file))

    def test_workflow_rule_execute_action(self):
        """Test workflow rule action execution"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rule with action
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        # Test action execution
        rule._execute_action(self.admission_file)

    def test_workflow_engine_run_workflow_rules(self):
        """Test workflow engine run workflow rules"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rule
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        # Test run workflow rules
        workflow._run_workflow_rules(self.admission_file, 'on_create')

    def test_workflow_engine_workflow_with_transitions(self):
        """Test workflow engine with state transitions"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create states
        state1 = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'description': 'Initial state'
        })
        
        state2 = self.env['acmst.workflow.state'].create({
            'name': 'submitted',
            'workflow_id': workflow.id,
            'is_final': False,
            'description': 'Submitted state'
        })
        
        state3 = self.env['acmst.workflow.state'].create({
            'name': 'approved',
            'workflow_id': workflow.id,
            'is_final': True,
            'description': 'Final state'
        })
        
        # Set allowed transitions
        state1.write({'allowed_transition_ids': [(6, 0, [state2.id])]})
        state2.write({'allowed_transition_ids': [(6, 0, [state3.id])]})
        
        # Check transitions
        self.assertEqual(len(state1.allowed_transition_ids), 1)
        self.assertIn(state2, state1.allowed_transition_ids)
        self.assertEqual(len(state2.allowed_transition_ids), 1)
        self.assertIn(state3, state2.allowed_transition_ids)

    def test_workflow_engine_workflow_with_rules(self):
        """Test workflow engine with rules"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rules
        rule1 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 1',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        rule2 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 2',
            'workflow_id': workflow.id,
            'trigger_event': 'on_update',
            'action_type': 'send_email',
            'action_value': 'test@example.com'
        })
        
        rule3 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 3',
            'workflow_id': workflow.id,
            'trigger_event': 'on_state_change',
            'action_type': 'create_activity',
            'action_value': 'Review required'
        })
        
        # Check rules
        self.assertEqual(len(workflow.rule_ids), 3)
        self.assertIn(rule1, workflow.rule_ids)
        self.assertIn(rule2, workflow.rule_ids)
        self.assertIn(rule3, workflow.rule_ids)

    def test_workflow_engine_workflow_with_conditions(self):
        """Test workflow engine with conditions"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rule with condition
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft',
            'condition_domain': '[("state", "=", "draft")]'
        })
        
        # Test condition evaluation
        self.assertTrue(rule._evaluate_condition(self.admission_file))
        
        # Test with different condition
        rule.write({'condition_domain': '[("state", "=", "submitted")]'})
        self.assertFalse(rule._evaluate_condition(self.admission_file))

    def test_workflow_engine_workflow_with_actions(self):
        """Test workflow engine with actions"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create rule with action
        rule = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft'
        })
        
        # Test action execution
        rule._execute_action(self.admission_file)

    def test_workflow_engine_workflow_with_sequences(self):
        """Test workflow engine with sequences"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create states with sequences
        state1 = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'sequence': 10,
            'description': 'Initial state'
        })
        
        state2 = self.env['acmst.workflow.state'].create({
            'name': 'submitted',
            'workflow_id': workflow.id,
            'is_final': False,
            'sequence': 20,
            'description': 'Submitted state'
        })
        
        state3 = self.env['acmst.workflow.state'].create({
            'name': 'approved',
            'workflow_id': workflow.id,
            'is_final': True,
            'sequence': 30,
            'description': 'Final state'
        })
        
        # Check sequences
        self.assertEqual(state1.sequence, 10)
        self.assertEqual(state2.sequence, 20)
        self.assertEqual(state3.sequence, 30)

    def test_workflow_engine_workflow_with_sequences_and_rules(self):
        """Test workflow engine with sequences and rules"""
        workflow = self.env['acmst.workflow.engine'].create({
            'name': 'Test Workflow',
            'model_id': self.env['ir.model']._get('acmst.admission.file').id,
            'description': 'Test workflow for admission files'
        })
        
        # Create states with sequences
        state1 = self.env['acmst.workflow.state'].create({
            'name': 'draft',
            'workflow_id': workflow.id,
            'is_initial': True,
            'sequence': 10,
            'description': 'Initial state'
        })
        
        state2 = self.env['acmst.workflow.state'].create({
            'name': 'submitted',
            'workflow_id': workflow.id,
            'is_final': False,
            'sequence': 20,
            'description': 'Submitted state'
        })
        
        state3 = self.env['acmst.workflow.state'].create({
            'name': 'approved',
            'workflow_id': workflow.id,
            'is_final': True,
            'sequence': 30,
            'description': 'Final state'
        })
        
        # Create rules with sequences
        rule1 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 1',
            'workflow_id': workflow.id,
            'trigger_event': 'on_create',
            'action_type': 'update_field',
            'action_value': 'draft',
            'sequence': 10
        })
        
        rule2 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 2',
            'workflow_id': workflow.id,
            'trigger_event': 'on_update',
            'action_type': 'send_email',
            'action_value': 'test@example.com',
            'sequence': 20
        })
        
        rule3 = self.env['acmst.workflow.rule'].create({
            'name': 'Test Rule 3',
            'workflow_id': workflow.id,
            'trigger_event': 'on_state_change',
            'action_type': 'create_activity',
            'action_value': 'Review required',
            'sequence': 30
        })
        
        # Check sequences
        self.assertEqual(state1.sequence, 10)
        self.assertEqual(state2.sequence, 20)
        self.assertEqual(state3.sequence, 30)
        self.assertEqual(rule1.sequence, 10)
        self.assertEqual(rule2.sequence, 20)
        self.assertEqual(rule3.sequence, 30)
