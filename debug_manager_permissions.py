#!/usr/bin/env python3
"""
Debug script to check manager permissions and application state
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

    # Create environment
    env = api.Environment(api.create_cursor(), SUPERUSER_ID, {})

    print("=== DEBUG MANAGER PERMISSIONS ===")

    # Find the application
    application = env['acmst.admission.file'].search([('name', '=', 'ADM000007')], limit=1)
    if not application:
        print("❌ Application ADM000007 not found")
        sys.exit(1)

    print(f"✅ Application found: {application.name}")
    print(f"📊 Current state: {application.state}")

    # Check user groups
    user = env.user
    groups = [group.name for group in user.groups_id]

    print(f"👤 Current user: {user.name} (ID: {user.id})")
    print(f"🔐 User groups: {groups}")
    print(f"🎯 Has Admission Manager group: {'Admission Manager' in groups}")

    # Check if buttons should be visible
    button_visible = application.state == 'manager_review' and 'Admission Manager' in groups
    print(f"🔘 Buttons should be visible: {button_visible}")

    if not button_visible:
        print("❌ Buttons are hidden because:")
        if application.state != 'manager_review':
            print(f"   - Application state is '{application.state}', not 'manager_review'")
        if 'Admission Manager' not in groups:
            print("   - User does not have 'Admission Manager' group"

    # Test the debug method
    try:
        debug_result = application.debug_manager_permissions()
        print(f"🔍 Debug result: {debug_result}")
    except Exception as e:
        print(f"⚠️ Error calling debug method: {e}")

    print("=== END DEBUG ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
