# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AcmstAcademicRules(models.Model):
    """Academic Rules Management Model
    
    This model manages academic rules and policies including:
    - Rule definitions and descriptions
    - Rule hierarchy (university, college, program level)
    - Rule types and categories
    - Effective dates and validity periods
    """
    _name = 'acmst.academic.rules'
    _description = 'Academic Rules'
    _order = 'sequence, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Rule Name',
        required=True,
        tracking=True,
        help="Name of the academic rule"
    )
    code = fields.Char(
        string='Rule Code',
        size=20,
        tracking=True,
        help="Unique code for the rule (max 20 characters)"
    )
    
    # Rule Classification
    rule_type = fields.Selection([
        ('attendance', 'Attendance'),
        ('grading', 'Grading'),
        ('promotion', 'Promotion'),
        ('graduation', 'Graduation'),
        ('admission', 'Admission'),
        ('examination', 'Examination'),
        ('discipline', 'Discipline'),
        ('financial', 'Financial'),
        ('academic_integrity', 'Academic Integrity'),
        ('other', 'Other')
    ], string='Rule Type', required=True, default='other', tracking=True)
    
    category = fields.Selection([
        ('general', 'General'),
        ('specific', 'Specific'),
        ('exception', 'Exception'),
        ('temporary', 'Temporary'),
        ('emergency', 'Emergency')
    ], string='Category', default='general', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='medium', tracking=True)
    
    # Rule Content
    description = fields.Text(
        string='Description',
        required=True,
        help="Brief description of the rule"
    )
    rule_text = fields.Html(
        string='Rule Details',
        required=True,
        help="Detailed rule content and specifications"
    )
    conditions = fields.Text(
        string='Conditions',
        help="Conditions under which this rule applies"
    )
    exceptions = fields.Text(
        string='Exceptions',
        help="Exceptions to this rule"
    )
    
    # Rule Hierarchy
    university_id = fields.Many2one(
        'acmst.university',
        string='University',
        tracking=True,
        help="University this rule applies to (if university-level)"
    )
    college_id = fields.Many2one(
        'acmst.college',
        string='College',
        tracking=True,
        help="College this rule applies to (if college-level)"
    )
    program_id = fields.Many2one(
        'acmst.program',
        string='Program',
        tracking=True,
        help="Program this rule applies to (if program-level)"
    )
    program_type_id = fields.Many2one(
        'acmst.program.type',
        string='Program Type',
        tracking=True,
        help="Program type this rule applies to"
    )
    
    # Validity and Dates
    effective_date = fields.Date(
        string='Effective Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help="Date from which this rule becomes effective"
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        tracking=True,
        help="Date after which this rule expires (optional)"
    )
    is_active = fields.Boolean(
        string='Active',
        compute='_compute_is_active',
        store=True,
        help="Whether this rule is currently active"
    )
    
    # Status and Settings
    active = fields.Boolean(
        string='Archived',
        default=True,
        tracking=True,
        help="Uncheck to archive this rule"
    )
    is_mandatory = fields.Boolean(
        string='Mandatory',
        default=True,
        tracking=True,
        help="Whether this rule is mandatory"
    )
    requires_approval = fields.Boolean(
        string='Requires Approval',
        default=False,
        tracking=True,
        help="Whether this rule requires special approval"
    )
    
    # Related Information
    related_rule_ids = fields.Many2many(
        'acmst.academic.rules',
        'acmst_rule_relation_rel',
        'rule_id',
        'related_rule_id',
        string='Related Rules',
        help="Rules related to this rule"
    )
    parent_rule_id = fields.Many2one(
        'acmst.academic.rules',
        string='Parent Rule',
        help="Parent rule if this is a sub-rule"
    )
    child_rule_ids = fields.One2many(
        'acmst.academic.rules',
        'parent_rule_id',
        string='Child Rules',
        help="Sub-rules of this rule"
    )
    
    # System Fields
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of display"
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help="Color for kanban view"
    )
    
    # Computed Fields
    rule_level = fields.Selection([
        ('university', 'University Level'),
        ('college', 'College Level'),
        ('program', 'Program Level'),
        ('program_type', 'Program Type Level')
    ], string='Rule Level', compute='_compute_rule_level', store=True)
    
    @api.depends('university_id', 'college_id', 'program_id', 'program_type_id')
    def _compute_rule_level(self):
        """Compute the level of this rule"""
        for record in self:
            if record.program_id:
                record.rule_level = 'program'
            elif record.college_id:
                record.rule_level = 'college'
            elif record.program_type_id:
                record.rule_level = 'program_type'
            elif record.university_id:
                record.rule_level = 'university'
            else:
                record.rule_level = 'university'  # Default to university level
    
    @api.depends('effective_date', 'expiry_date', 'active')
    def _compute_is_active(self):
        """Compute whether this rule is currently active"""
        today = fields.Date.today()
        for record in self:
            if not record.active:
                record.is_active = False
            elif record.effective_date and record.effective_date > today:
                record.is_active = False
            elif record.expiry_date and record.expiry_date < today:
                record.is_active = False
            else:
                record.is_active = True
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure rule code is unique"""
        for record in self:
            if record.code:
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        _("Rule code '%s' already exists. Please use a different code.") % record.code
                    )
    
    @api.constrains('effective_date', 'expiry_date')
    def _check_dates(self):
        """Validate date fields"""
        for record in self:
            if record.effective_date and record.expiry_date:
                if record.effective_date >= record.expiry_date:
                    raise ValidationError(
                        _("Effective date must be before expiry date.")
                    )
    
    @api.constrains('university_id', 'college_id', 'program_id')
    def _check_rule_hierarchy(self):
        """Validate rule hierarchy"""
        for record in self:
            if record.program_id and record.college_id:
                if record.program_id.college_id != record.college_id:
                    raise ValidationError(
                        _("Program must belong to the specified college.")
                    )
            if record.college_id and record.university_id:
                if record.college_id.university_id != record.university_id:
                    raise ValidationError(
                        _("College must belong to the specified university.")
                    )
    
    @api.constrains('parent_rule_id')
    def _check_parent_rule(self):
        """Validate parent rule relationship"""
        for record in self:
            if record.parent_rule_id:
                if record.parent_rule_id.id == record.id:
                    raise ValidationError(
                        _("A rule cannot be its own parent.")
                    )
                # Check for circular references
                parent = record.parent_rule_id
                while parent:
                    if parent.parent_rule_id == record:
                        raise ValidationError(
                            _("Circular reference detected in parent-child rule relationship.")
                        )
                    parent = parent.parent_rule_id
    
    @api.model
    def create(self, vals):
        """Override create to set sequence and validate"""
        if 'sequence' not in vals:
            vals['sequence'] = self._get_next_sequence()
        return super().create(vals)
    
    def _get_next_sequence(self):
        """Get next sequence number"""
        last_record = self.search([], order='sequence desc', limit=1)
        return (last_record.sequence or 0) + 10
    
    def name_get(self):
        """Custom name_get to show code and name"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.rule_level:
                name = f"{name} ({record.rule_level.title()})"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        """Custom name search to include code and description"""
        args = args or []
        if name:
            domain = [
                '|', '|', '|',
                ('name', operator, name),
                ('code', operator, name),
                ('description', operator, name),
                ('rule_text', operator, name)
            ]
            return self.search(domain + args, limit=limit).name_get()
        return super()._name_search(name, args, operator, limit)
    
    def action_view_related_rules(self):
        """Action to view related rules"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_academic_rules')
        action['domain'] = [('id', 'in', self.related_rule_ids.ids)]
        action['context'] = {
            'search_default_related_rules': True,
        }
        return action
    
    def action_view_child_rules(self):
        """Action to view child rules"""
        action = self.env['ir.actions.act_window']._for_xml_id('acmst_core_settings.action_acmst_academic_rules')
        action['domain'] = [('parent_rule_id', '=', self.id)]
        action['context'] = {
            'default_parent_rule_id': self.id,
            'search_default_parent_rule_id': self.id,
        }
        return action
    
    def action_activate_rule(self):
        """Activate this rule"""
        for record in self:
            if not record.is_active:
                record.write({
                    'effective_date': fields.Date.today(),
                    'expiry_date': False
                })
    
    def action_deactivate_rule(self):
        """Deactivate this rule"""
        for record in self:
            if record.is_active:
                record.write({'expiry_date': fields.Date.today()})
    
    def toggle_active(self):
        """Override toggle_active to handle related records"""
        for record in self:
            if not record.active:
                # Archive related child rules
                record.child_rule_ids.write({'active': False})
        return super().toggle_active()
    
    def _get_applicable_rules(self, university_id=None, college_id=None, program_id=None, program_type_id=None):
        """Get rules applicable to specific context"""
        domain = [('is_active', '=', True), ('active', '=', True)]
        
        # Add hierarchy-specific conditions
        if program_id:
            domain.extend([
                '|', '|', '|', '|',
                ('program_id', '=', program_id),
                ('college_id', '=', program_id.college_id.id),
                ('university_id', '=', program_id.university_id.id),
                ('program_type_id', '=', program_id.program_type_id.id),
                ('university_id', '=', False)
            ])
        elif college_id:
            domain.extend([
                '|', '|',
                ('college_id', '=', college_id),
                ('university_id', '=', college_id.university_id.id),
                ('university_id', '=', False)
            ])
        elif university_id:
            domain.extend([
                '|',
                ('university_id', '=', university_id),
                ('university_id', '=', False)
            ])
        elif program_type_id:
            domain.extend([
                '|',
                ('program_type_id', '=', program_type_id),
                ('university_id', '=', False)
            ])
        
        return self.search(domain)
    
    @api.model
    def get_rules_by_type(self, rule_type, university_id=None, college_id=None, program_id=None):
        """Get rules of specific type for given context"""
        domain = [
            ('rule_type', '=', rule_type),
            ('is_active', '=', True),
            ('active', '=', True)
        ]
        
        if program_id:
            domain.extend([
                '|', '|', '|', '|',
                ('program_id', '=', program_id),
                ('college_id', '=', program_id.college_id.id),
                ('university_id', '=', program_id.university_id.id),
                ('program_type_id', '=', program_id.program_type_id.id),
                ('university_id', '=', False)
            ])
        elif college_id:
            domain.extend([
                '|', '|',
                ('college_id', '=', college_id),
                ('university_id', '=', college_id.university_id.id),
                ('university_id', '=', False)
            ])
        elif university_id:
            domain.extend([
                '|',
                ('university_id', '=', university_id),
                ('university_id', '=', False)
            ])
        
        return self.search(domain)
    
    @api.model
    def get_mandatory_rules(self, university_id=None, college_id=None, program_id=None):
        """Get mandatory rules for given context"""
        domain = [
            ('is_mandatory', '=', True),
            ('is_active', '=', True),
            ('active', '=', True)
        ]
        
        if program_id:
            domain.extend([
                '|', '|', '|', '|',
                ('program_id', '=', program_id),
                ('college_id', '=', program_id.college_id.id),
                ('university_id', '=', program_id.university_id.id),
                ('program_type_id', '=', program_id.program_type_id.id),
                ('university_id', '=', False)
            ])
        elif college_id:
            domain.extend([
                '|', '|',
                ('college_id', '=', college_id),
                ('university_id', '=', college_id.university_id.id),
                ('university_id', '=', False)
            ])
        elif university_id:
            domain.extend([
                '|',
                ('university_id', '=', university_id),
                ('university_id', '=', False)
            ])
        
        return self.search(domain)
    
    def _check_rule_conflicts(self):
        """Check for conflicts with existing rules"""
        # This method can be extended to implement conflict detection logic
        pass
