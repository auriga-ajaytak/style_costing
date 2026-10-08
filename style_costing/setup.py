# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from style_costing.item_types import ITEM_TYPES


# Role Profile -> roles. Each pairs one of this app's roles with the ERPNext
# roles that person needs for items, buyers, quotations and BOMs.
ROLE_PROFILES = {
	"Style Merchandiser": ("Merchandiser", "Sales User", "Item Manager"),
	"Style Costing Manager": ("Costing Manager", "Sales Manager", "Item Manager"),
	"Style Production Planner": ("Production Planner", "Manufacturing User"),
}


def after_install():
	create_role_profiles()


def create_role_profiles():
	"""Add the role profiles that are missing. An existing one is left as the
	site has it, so an administrator's changes survive upgrades."""
	for profile, roles in ROLE_PROFILES.items():
		if frappe.db.exists("Role Profile", profile):
			continue
		frappe.get_doc(
			{
				"doctype": "Role Profile",
				"role_profile": profile,
				"roles": [{"role": role} for role in roles if frappe.db.exists("Role", role)],
			}
		).insert(ignore_permissions=True)


@frappe.whitelist()
def setup_warnings():
	"""What an administrator should know before the first style is built."""
	frappe.only_for(("System Manager", "Costing Manager"))
	listed = {row.item_type for row in frappe.get_cached_doc("Style Costing Settings").item_groups}
	missing = [item_type for item_type in ITEM_TYPES if item_type not in listed]
	if not missing:
		return []
	return [
		_(
			"No Item Group is listed for: {0}. Add it under Item Groups below, or the matching item lists on a style will be empty."
		).format(", ".join(missing))
	]
