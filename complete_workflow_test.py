#!/usr/bin/env python3
"""
Complete workflow test script to move application through all states
"""

import sys
import os

# Add the Odoo path
sys.path.append('.')

try:
    from odoo import api, SUPERUSER_ID
    from odoo.tools import config

    # Configure database
    config['db_name'] = 'acmst_college'

    # Create environment as superuser
    env = api.Environment(api.create_cursor(), SUPERUSER_ID, {})

    print("=== COMPLETE WORKFLOW TEST ===")

    # Find the application
    application = env['acmst.admission.file'].search([('name', '=', 'ADM000008')], limit=1)
    if not application:
        print("❌ Application ADM000008 not found")
        sys.exit(1)

    print(f"✅ Found application: {application.name}")
    print(f"📊 Current state: {application.state}")

    # Move through all states to reach manager_review
    if application.state == 'health_required':
        print("📋 Moving through health check process...")

        # Create and approve health check
        health_check = env['acmst.health.check'].create({
            'admission_file_id': application.id,
            'check_date': '2024-09-20',
            'examiner_id': 1,  # Administrator
            'medical_fitness': 'fit',
            'height': 175.0,
            'weight': 70.0,
            'blood_type': 'A+'
        })

        # Submit and approve health check
        health_check.action_submit()
        health_check.action_approve()

        print(f"✅ Health check approved. New state: {application.state}")

    if application.state == 'health_approved':
        print("📋 Moving to coordinator review...")

        # Move to coordinator review
        application.action_coordinator_review()
        print(f"✅ Coordinator review initiated. New state: {application.state}")

    if application.state == 'coordinator_review':
        print("📋 Approving by coordinator...")

        # Approve by coordinator
        application.action_coordinator_approve()
        print(f"✅ Coordinator approved. New state: {application.state}")

    if application.state == 'coordinator_approved':
        print("📋 Sending to manager review...")

        # Send to manager review
        application.action_manager_review()
        print(f"✅ Sent to manager review. New state: {application.state}")

    print(f"🎯 Final state: {application.state}")

    if application.state == 'manager_review':
        print("✅ SUCCESS! Application is now in manager_review state")
        print("🔘 Manager approve/reject buttons should now be visible")
    else:
        print(f"❌ Application is still in {application.state} state")
        print("📝 Need to complete the workflow steps above")

    print("=== WORKFLOW TEST COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
