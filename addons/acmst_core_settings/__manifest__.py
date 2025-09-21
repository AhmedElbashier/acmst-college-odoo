# -*- coding: utf-8 -*-
{
    'name': 'ACMST Core Settings',
    'version': '17.0.1.0.0',
    'category': 'Education',
    'summary': 'Core settings and configuration module for ACMST College management system',
    'description': """
        ACMST Core Settings Module
        =========================
        
        This module provides the foundational configuration and management system for ACMST College.
        It includes:
        
        * University/Institution Management
        * College/Department Structure
        * Academic Program Hierarchy
        * Personnel Management (Managers & Coordinators)
        * Batch Management System
        * Academic Year Management
        * Academic Rules Configuration
        
        This module serves as the foundation for all other ACMST College modules.
    """,
    'author': 'ACMST College Development Team',
    'website': 'https://www.acmst-edu.com',
    #'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'web',
    ],
    'data': [
        # Security - Groups first, then access rights
        'security/acmst_core_settings_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/ir_sequence_data.xml',
        'data/acmst_core_settings_data.xml',


        # Views
        'views/acmst_university_views.xml',
        'views/acmst_college_views.xml',
        'views/acmst_program_type_views.xml',
        'views/acmst_program_views.xml',
        'views/acmst_batch_views.xml',
        'views/acmst_academic_year_views.xml',
        'views/acmst_academic_rules_views.xml',

        # Wizards
        'views/acmst_batch_creation_wizard_views.xml',

        # Menus (loaded after all views and wizards)
        'views/acmst_core_settings_menus.xml',
    ],
    # 'demo': [
    #     'demo/acmst_core_settings_demo.xml',
    # ],
    'assets': {
        'web.assets_backend': [
            'acmst_core_settings/static/src/css/acmst_core_settings.css',
            'acmst_core_settings/static/src/js/acmst_core_settings.js',
        ],
        'web.assets_qweb': [
            'acmst_core_settings/static/src/xml/acmst_core_settings_templates.xml',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
    'post_init_hook': 'post_init_hook',
}
