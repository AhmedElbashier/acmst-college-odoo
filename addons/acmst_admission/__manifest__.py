# -*- coding: utf-8 -*-
# Copyright 2024 ACMST College
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'ACMST Admission Management',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Comprehensive admission management system for ACMST College',
    'description': """
        ACMST Admission Management System
        ================================
        
        This module provides a complete admission management system for ACMST College,
        including:
        
        * Application submission and tracking
        * Multi-stage approval workflow
        * Health check and medical assessment
        * Coordinator and manager approvals
        * Portal integration for students
        * Document management
        * Conditional requirements tracking
        
        Features:
        ---------
        * Public portal for application submission
        * Multi-state workflow with approvals
        * Health questionnaire and medical assessment
        * Academic coordinator review with conditions
        * Final manager approval
        * Automatic student record creation
        * Comprehensive reporting and analytics
        * Mobile-responsive design
        * Multi-language support (Arabic/English)
    """,
    'author': 'ACMST College',
    'website': 'https://www.acmst.edu.sa',
    'depends': [
        'base',
        'mail',
        'portal',
        'web',
        'acmst_core_settings',
    ],
    'data': [
        'security/acmst_admission_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/sequence_sync_data.xml',
        'data/acmst_admission_data.xml',
        'data/acmst_workflow_data.xml',
        'views/acmst_admission_file_views.xml',
        'views/acmst_health_check_views.xml',
        'views/acmst_health_dashboard_views.xml',
        'views/acmst_coordinator_condition_views.xml',
        'views/acmst_coordinator_admission_views.xml',
        'views/acmst_coordinator_dashboard_views.xml',
        'views/acmst_officer_dashboard_views.xml',
        'views/acmst_health_officer_dashboard_views.xml',
        'views/acmst_admission_manager_dashboard_views.xml',
        'views/acmst_manager_dashboard_views.xml',
        'views/acmst_workflow_engine_views.xml',
        'views/acmst_admission_dashboard_views.xml',
        'views/acmst_dashboard_views.xml',
        'views/acmst_reports_dashboard_views.xml',
        'views/acmst_audit_log_views.xml',
        'views/acmst_admission_approval_views.xml',
        'views/acmst_portal_application_views.xml',
        'views/acmst_admission_menus.xml',
        'views/acmst_performance_views.xml',
        'views/acmst_performance_monitoring_views.xml',
        'wizards/acmst_admission_wizard_views.xml',
        'wizards/acmst_coordinator_condition_wizard_views.xml',
        'wizards/acmst_ministry_approval_wizard_views.xml',
        'wizards/acmst_university_id_update_wizard_views.xml',
        'static/src/xml/acmst_admission_portal_templates.xml',
        'static/src/xml/acmst_admission_portal_dashboard.xml',
        'static/src/xml/acmst_admission_form_wizard.xml',
        'reports/health_check_report_template.xml',
        'static/src/xml/acmst_admission_dashboard.xml',
        'static/src/xml/acmst_admission_progress_tracking.xml',
        'static/src/xml/acmst_performance_dashboard.xml',
    ],
    'demo': [
        'demo/acmst_admission_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'acmst_admission/static/src/css/acmst_admission.css',
            'acmst_admission/static/src/css/acmst_performance_dashboard.css',
            'acmst_admission/static/src/css/dashboard_enhancements.css',
            'acmst_admission/static/src/js/acmst_admission.js',
            'acmst_admission/static/src/js/acmst_performance_monitor.js',
        ],
        'web.assets_frontend': [
            'acmst_admission/static/src/css/acmst_admission_portal.css',
            'acmst_admission/static/src/js/acmst_admission_portal.js',
        ],
    },
    'icon': '/acmst_admission/static/description/icon_128.png',
    'sequence': 2,
    'installable': True,
    'auto_install': False,
    'application': True,
    #'license': 'AGPL-3',
}
