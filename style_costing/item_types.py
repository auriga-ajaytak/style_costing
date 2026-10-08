# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt
"""Which Item Groups hold fabric, trims and finished goods.

Every site arranges its Item Groups differently, so the app does not mark the
groups themselves. Style Costing Settings lists the groups that matter, and a
group listed there speaks for everything beneath it.
"""

import frappe

ITEM_TYPES = ("Fabric", "Trims", "Finished Goods")


def item_group_types() -> dict[str, str]:
	"""Item Group -> item type, for every group at or below a listed one. Where
	listed groups nest, the nearest one decides."""
	rows = frappe.get_cached_doc("Style Costing Settings").item_groups
	if not rows:
		return {}

	bounds = {
		g.name: g
		for g in frappe.get_all(
			"Item Group",
			filters={"name": ("in", [r.item_group for r in rows])},
			fields=["name", "lft", "rgt"],
		)
	}
	listed = sorted(
		(r for r in rows if r.item_group in bounds), key=lambda r: bounds[r.item_group].lft
	)

	types = {}
	# outermost first, so a nested listing overwrites the one above it
	for row in listed:
		node = bounds[row.item_group]
		for name in frappe.get_all(
			"Item Group", filters={"lft": (">=", node.lft), "rgt": ("<=", node.rgt)}, pluck="name"
		):
			types[name] = row.item_type
	return types


def item_groups_of(item_type: str) -> list[str]:
	return [group for group, kind in item_group_types().items() if kind == item_type]


@frappe.whitelist()
def get_item_type(item_group: str | None = None) -> str | None:
	"""Fabric, Trims, Finished Goods or nothing: decides which fields an Item shows."""
	if not item_group:
		return None
	return item_group_types().get(item_group)
