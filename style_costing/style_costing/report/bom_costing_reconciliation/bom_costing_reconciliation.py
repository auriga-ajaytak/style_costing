# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from style_costing.bom import garment_items, style_materials

# quantities this close are the same material quantity
TOLERANCE = 0.0005


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("style"):
		return get_columns(), []
	return get_columns(), get_data(filters)


def get_data(filters):
	style = frappe.get_doc("Style Master", filters.style)
	style.check_permission("read")
	costing = style_materials(style)

	rows = []
	for item in garment_items(style):
		bom = _current_bom(item)
		in_bom = _bom_materials(bom) if bom else {}
		for material in sorted(set(costing) | set(in_bom)):
			costing_qty = costing[material].qty if material in costing else None
			bom_qty = in_bom.get(material)
			rows.append(
				{
					"garment_item": item,
					"bom": bom,
					"material": material,
					"costing_qty": costing_qty,
					"bom_qty": bom_qty,
					"variance": flt(bom_qty) - flt(costing_qty),
					"status": _status(bom, costing_qty, bom_qty),
				}
			)
	if filters.get("differences_only"):
		rows = [r for r in rows if r["status"] != "Match"]
	return rows


def _status(bom, costing_qty, bom_qty):
	if not bom:
		return "No BOM"
	if bom_qty is None:
		return "Only in costing"
	if costing_qty is None:
		return "Only in BOM"
	return "Match" if abs(bom_qty - costing_qty) <= TOLERANCE else "Quantity differs"


def _current_bom(item):
	"""The item's default BOM, else its latest one that is not cancelled."""
	boms = frappe.get_all(
		"BOM",
		filters={"item": item, "docstatus": ("<", 2)},
		pluck="name",
		order_by="is_default desc, docstatus desc, creation desc",
		limit=1,
	)
	return boms[0] if boms else None


def _bom_materials(bom):
	"""Material quantities for one unit of the BOM's item."""
	quantity = flt(frappe.db.get_value("BOM", bom, "quantity")) or 1
	materials = {}
	for row in frappe.get_all("BOM Item", filters={"parent": bom}, fields=["item_code", "qty"]):
		materials[row.item_code] = materials.get(row.item_code, 0) + flt(row.qty) / quantity
	return materials


def get_columns():
	return [
		{
			"fieldname": "garment_item",
			"label": _("Garment Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{"fieldname": "bom", "label": _("BOM"), "fieldtype": "Link", "options": "BOM", "width": 170},
		{"fieldname": "material", "label": _("Material"), "fieldtype": "Link", "options": "Item", "width": 150},
		{"fieldname": "costing_qty", "label": _("Costing Qty / Garment"), "fieldtype": "Float", "width": 160},
		{"fieldname": "bom_qty", "label": _("BOM Qty / Garment"), "fieldtype": "Float", "width": 150},
		{"fieldname": "variance", "label": _("Variance (BOM - Costing)"), "fieldtype": "Float", "width": 170},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 130},
	]
