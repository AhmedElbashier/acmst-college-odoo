#!/usr/bin/env python3
"""
Fix script to add Admission Manager group to Administrator user
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

    print("=== FIX MANAGER PERMISSIONS ===")

    # Find the Administrator user
    admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
    if not admin_user:
        print("❌ Administrator user not found")
        sys.exit(1)

    print(f"✅ Found Administrator user: {admin_user.name}")

    # Find the Admission Manager group
    manager_group = env['res.groups'].search([('name', '=', 'Admission Manager')], limit=1)
    if not manager_group:
        print("❌ Admission Manager group not found")
        sys.exit(1)

    print(f"✅ Found Admission Manager group: {manager_group.name}")

    # Check if user already has the group
    if manager_group in admin_user.groups_id:
        print("✅ Administrator already has Admission Manager group")
    else:
        print("📝 Adding Admission Manager group to Administrator...")

        # Add the group to the user
        admin_user.write({
            'groups_id': [(4, manager_group.id)]
        })

        print("✅ Successfully added Admission Manager group to Administrator")

    # Verify the change
    admin_user.refresh()
    groups = [group.name for group in admin_user.groups_id]
    print(f"🔐 Administrator groups now: {groups}")

    print("=== FIX COMPLETE ===")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
