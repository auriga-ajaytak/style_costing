# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe


def validate(doc, event):
	"""Note on each order line the style its item was costed from."""
	for row in doc.items:
		row.style_master = style_for_item(row.item_code)


def style_for_item(item_code: str | None) -> str | None:
	"""The style costed for an Item, or for the template it is a variant of.
	With several, a submitted style is preferred and then the newest."""
	if not item_code:
		return None
	items = [item_code]
	template = frappe.get_cached_value("Item", item_code, "variant_of")
	if template:
		items.append(template)
	styles = frappe.get_all(
		"Style Master",
		filters={"item": ("in", items), "docstatus": ("<", 2)},
		pluck="name",
		order_by="docstatus desc, creation desc",
		limit=1,
	)
	return styles[0] if styles else None
