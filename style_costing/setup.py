# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import click
import frappe
from frappe import _

ITEM_CONTROLLER = "style_costing.docevents.item.StyleItem"


# Role Profile -> roles. Each pairs one of this app's roles with the ERPNext
# roles that person needs for items, buyers, quotations and BOMs.
ROLE_PROFILES = {
	"Style Merchandiser": ("Merchandiser", "Sales User", "Item Manager"),
	"Style Costing Manager": ("Costing Manager", "Sales Manager", "Item Manager"),
	"Style Production Planner": ("Production Planner", "Manufacturing User"),
}


def after_install():
	create_role_profiles()
	warn_on_item_override_conflict()


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


def get_item_override_conflict() -> str | None:
	"""Explain an Item controller clash with another app, if there is one.

	Frappe uses the last `override_doctype_class` entry for a DocType and drops
	the rest without a word. When this app loses, the F-/T-/G- item code series
	stops running; when it wins, the other app's Item logic does.
	"""
	overrides = frappe.get_hooks("override_doctype_class").get("Item") or []
	others = [path for path in overrides if path != ITEM_CONTROLLER]
	if not others:
		return None

	if overrides[-1] == ITEM_CONTROLLER:
		return _(
			"Style Costing overrides the Item controller, and so does {0}. Style Costing's is the one in use; the other is ignored."
		).format(", ".join(others))

	if frappe.db.get_single_value("Style Costing Settings", "keep_erpnext_item_codes"):
		return None
	return _(
		"The Item controller from {0} is in use instead of Style Costing's, so item codes are not generated from the Item Group category. Tick 'Keep ERPNext Item Codes' in Style Costing Settings to accept this."
	).format(overrides[-1])


def warn_on_item_override_conflict():
	message = get_item_override_conflict()
	if message:
		click.secho(f"style_costing: {message}", fg="yellow")


def untagged_item_groups() -> int:
	"""Leaf Item Groups with no Group Category. The Fabric and Trims pickers
	on a style list items by that category, so items in these never appear."""
	return frappe.db.count("Item Group", {"is_group": 0, "group_category": ("is", "not set")})


@frappe.whitelist()
def setup_warnings():
	"""What an administrator should know before the first style is built."""
	frappe.only_for(("System Manager", "Costing Manager"))
	warnings = []
	conflict = get_item_override_conflict()
	if conflict:
		warnings.append(conflict)
	untagged = untagged_item_groups()
	if untagged:
		warnings.append(
			_(
				"{0} Item Group(s) have no Group Category. Items in them will not appear in the Fabric and Trims pickers on a style until the group is tagged Fabric or Trims."
			).format(untagged)
		)
	return warnings
