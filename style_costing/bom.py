# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt
"""ERPNext BOMs from a Style Master.

A style lists the fabric and trims one garment consumes; the garment Items made
from it point back through `Item.style_master`. This turns the first into a BOM
for each of the second. It reads the style and never writes to it.
"""

import erpnext
import frappe
from frappe import _
from frappe.utils import flt


def style_materials(style) -> dict[str, frappe._dict]:
	"""Per-garment quantity of each fabric and trim on a style, keyed by item.

	The quantity is the row's consumption - for trims, times the pieces per
	garment - before purchase extra, production extra, wastage and samples,
	which belong to buying for an order rather than to making one garment.
	"""
	materials = {}

	def add(item, qty, row):
		if not item:
			return
		material = materials.setdefault(
			item, frappe._dict(item_code=item, qty=0, uom=row.unit, rate=flt(row.rate_our))
		)
		material.qty += flt(qty)

	for row in style.fabric_table:
		add(row.fabric_name, row.consumption, row)
	for row in style.trims_table:
		add(row.trim_name, flt(row.consumption) * (row.per_garment or 1), row)
	return materials


def garment_items(style_name: str) -> list[str]:
	"""Items made from this style: the variants of a linked template, or a
	linked item that has none. A template itself gets no BOM."""
	return frappe.get_all(
		"Item",
		filters={"style_master": style_name, "has_variants": 0, "disabled": 0},
		pluck="name",
		order_by="name",
	)


@frappe.whitelist()
def generate_boms(style: str):
	"""Create a draft BOM for every garment item of the style, or refresh the
	draft it already has. An item with a submitted BOM is left alone."""
	doc = frappe.get_doc("Style Master", style)
	doc.check_permission("read")
	frappe.has_permission("BOM", "create", throw=True)

	items = garment_items(doc.name)
	if not items:
		frappe.throw(
			_("No garment Item is linked to this style. Set Style Master on the Item (or its variants) first.")
		)
	materials = style_materials(doc)
	if not materials:
		frappe.throw(_("This style has no fabric or trims to build a BOM from."))

	company = doc.company or erpnext.get_default_company()
	if not company:
		frappe.throw(_("Set a Company on the style to generate BOMs."))

	result = {"created": [], "updated": [], "skipped": []}
	for item in items:
		if frappe.db.exists("BOM", {"item": item, "docstatus": 1}):
			result["skipped"].append(item)
			continue

		draft = frappe.db.exists("BOM", {"item": item, "docstatus": 0})
		bom = frappe.get_doc("BOM", draft) if draft else frappe.new_doc("BOM")
		bom.update(
			{
				"item": item,
				"quantity": 1,
				"company": company,
				"currency": erpnext.get_company_currency(company),
				"conversion_rate": 1,
			}
		)
		bom.set(
			"items",
			[
				{
					"item_code": m.item_code,
					"qty": m.qty,
					"uom": m.uom or frappe.get_cached_value("Item", m.item_code, "stock_uom"),
					"rate": m.rate,
				}
				for m in materials.values()
			],
		)
		bom.save()
		result["updated" if draft else "created"].append(bom.name)
	return result
