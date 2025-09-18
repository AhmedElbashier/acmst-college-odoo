# -*- coding: utf-8 -*-

from . import models
from . import wizards

def post_init_hook(env):
    """Post-installation hook for ACMST Core Settings module"""
    # For Odoo 17+, the hook receives env directly
    
    # Create default sequences if they don't exist
    sequence_data = [
        ('acmst.university', 'University Code', 'UNI', 3),
        ('acmst.college', 'College Code', 'COL', 3),
        ('acmst.program.type', 'Program Type Code', 'PT', 2),
        ('acmst.program', 'Program Code', 'PROG', 3),
        ('acmst.batch', 'Batch Code', 'BATCH', 3),
        ('acmst.academic.year', 'Academic Year Code', 'AY', 2),
        ('acmst.academic.rules', 'Academic Rules Code', 'RULE', 3),
    ]
    
    for model, name, prefix, padding in sequence_data:
        sequence = env['ir.sequence'].search([('code', '=', model)], limit=1)
        if not sequence:
            env['ir.sequence'].create({
                'name': name,
                'code': model,
                'prefix': prefix,
                'padding': padding,
                'number_next': 1,
                'number_increment': 1,
            })
    
    # Set up default security groups
    admin_group = env.ref('acmst_core_settings.group_admin', raise_if_not_found=False)
    if admin_group:
        # Add admin user to admin group
        admin_user = env.ref('base.user_admin', raise_if_not_found=False)
        if admin_user:
            admin_user.groups_id = [(4, admin_group.id)]
    
    # Create default academic year if none exists
    current_year = env['acmst.academic.year'].search([('is_current', '=', True)], limit=1)
    if not current_year:
        from datetime import datetime
        year = datetime.now().year
        env['acmst.academic.year'].create({
            'name': f'{year}-{year+1}',
            'code': f'AY{year}-{str(year+1)[-2:]}',
            'short_name': f'{year}-{year+1}',
            'start_date': f'{year}-09-01',
            'end_date': f'{year+1}-08-31',
            'semester_count': 2,
            'is_current': True,
        })
    
    print("ACMST Core Settings module installed successfully!")