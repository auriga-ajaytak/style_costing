# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt
"""Sample masters for a trial site, installed and removed from Style Costing
Settings. Only masters: a style's costs are worked out on the form, so no
sample Style Master is shipped."""

import json
from pathlib import Path

import frappe
from frappe import _
from frappe.utils.nestedset import get_root_of

SETTINGS = "Style Costing Settings"
# demo Item Group -> what Style Costing Settings should list it as
ITEM_GROUPS = {"Demo Fabric": "Fabric", "Demo Trims": "Trims", "Demo Finished Goods": "Finished Goods"}
ROLES = ("System Manager", "Costing Manager")


def _installed() -> list[list[str]]:
	return json.loads(frappe.db.get_single_value(SETTINGS, "demo_records") or "[]")


def _remember(records):
	frappe.db.set_single_value(SETTINGS, "demo_records", json.dumps(records))


@frappe.whitelist()
def install():
	frappe.only_for(ROLES)
	if _installed():
		frappe.throw(_("Demo data is already installed."))

	created = []
	for record in json.loads(Path(__file__).with_name("records.json").read_text()):
		if record["doctype"] == "Item Group":
			record["parent_item_group"] = get_root_of("Item Group")
		doc = frappe.get_doc(record).insert()
		created.append([doc.doctype, doc.name])
		if doc.doctype == "Item Group":
			_list_item_group(doc.name, ITEM_GROUPS[doc.name])
	_remember(created)
	return len(created)


def _list_item_group(item_group, item_type):
	settings = frappe.get_doc(SETTINGS)
	settings.append("item_groups", {"item_group": item_group, "item_type": item_type})
	settings.save()


def _unlist_item_groups():
	settings = frappe.get_doc(SETTINGS)
	settings.set("item_groups", [row for row in settings.item_groups if row.item_group not in ITEM_GROUPS])
	settings.save()


@frappe.whitelist()
def remove():
	"""Delete what `install` created, newest first. A record that has since
	been used elsewhere is left in place and reported."""
	frappe.only_for(ROLES)
	_unlist_item_groups()
	kept = []
	for doctype, name in reversed(_installed()):
		if not frappe.db.exists(doctype, name):
			continue
		try:
			frappe.delete_doc(doctype, name)
		except frappe.LinkExistsError:
			frappe.clear_last_message()
			kept.append([doctype, name])
	_remember(list(reversed(kept)))
	return kept
