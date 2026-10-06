# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe import _

# child table -> (label, item field, source field, supplier field)
MATERIALS = {
	"Fabric": ("Fabric", "fabric_name", "fabric_type", "fabric_supplier_name"),
	"Trims": ("Trims", "trim_name", "trims_type", "trims_supplier_name"),
}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_data(filters):
	conditions = {"docstatus": ("<", 2)}
	for fieldname in ("company", "customer", "season"):
		if filters.get(fieldname):
			conditions[fieldname] = filters[fieldname]
	if filters.get("style"):
		conditions["name"] = filters.style

	# get_list, so a user only sees materials of styles they may read
	styles = {
		s.name: s
		for s in frappe.get_list(
			"Style Master", filters=conditions, fields=["name", "style_master_name", "customer"]
		)
	}
	if not styles:
		return []

	rows = []
	for doctype, (label, item_field, source_field, supplier_field) in MATERIALS.items():
		if filters.get("material") and filters.material != label:
			continue
		child_filters = {"parenttype": "Style Master", "parent": ("in", list(styles))}
		if filters.get("item"):
			child_filters[item_field] = filters.item
		for row in frappe.get_all(
			doctype,
			filters=child_filters,
			fields=[
				"parent",
				f"{item_field} as item",
				f"{source_field} as source",
				f"{supplier_field} as supplier",
				"unit",
				"consumption",
				"total_req_qty",
				"rate_our",
				"total_amt",
				"per_piece_value",
			],
			order_by="parent, idx",
		):
			style = styles[row.parent]
			rows.append(
				{
					**row,
					"style": row.parent,
					"style_name": style.style_master_name,
					"customer": style.customer,
					"material": label,
				}
			)
	return sorted(rows, key=lambda r: r["style"])


def get_columns():
	return [
		{"fieldname": "style", "label": _("Style"), "fieldtype": "Link", "options": "Style Master", "width": 160},
		{"fieldname": "style_name", "label": _("Style Name"), "fieldtype": "Data", "width": 150},
		{"fieldname": "customer", "label": _("Buyer"), "fieldtype": "Link", "options": "Customer", "width": 140},
		{"fieldname": "material", "label": _("Material"), "fieldtype": "Data", "width": 80},
		{"fieldname": "item", "label": _("Item"), "fieldtype": "Link", "options": "Item", "width": 140},
		{"fieldname": "source", "label": _("Source"), "fieldtype": "Data", "width": 80},
		{"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "Supplier", "width": 140},
		{"fieldname": "unit", "label": _("Unit"), "fieldtype": "Link", "options": "UOM", "width": 70},
		{"fieldname": "consumption", "label": _("Consumption"), "fieldtype": "Float", "width": 110},
		{"fieldname": "total_req_qty", "label": _("Total Required Qty"), "fieldtype": "Float", "width": 140},
		{"fieldname": "rate_our", "label": _("Rate"), "fieldtype": "Float", "width": 90},
		{"fieldname": "total_amt", "label": _("Total Amount"), "fieldtype": "Float", "width": 120},
		{"fieldname": "per_piece_value", "label": _("Per Piece Value"), "fieldtype": "Float", "width": 120},
	]
