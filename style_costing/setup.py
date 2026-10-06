# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import click
import frappe
from frappe import _

ITEM_CONTROLLER = "style_costing.docevents.item.StyleItem"


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


@frappe.whitelist()
def item_override_conflict():
	frappe.only_for(("System Manager", "Costing Manager"))
	return get_item_override_conflict()
