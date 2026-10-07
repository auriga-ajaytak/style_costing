# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Sum


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_data(filters):
	conditions = {"docstatus": ("<", 2)}
	for fieldname in ("company", "customer", "season"):
		if filters.get(fieldname):
			conditions[fieldname] = filters[fieldname]

	styles = frappe.get_list(
		"Style Master",
		filters=conditions,
		fields=["name", "style_master_name", "customer", "season", "garment_qty", "sales_price_target"],
		order_by="creation desc",
	)
	orders = _orders_by_style([s.name for s in styles])

	rows = []
	for style in styles:
		ordered = orders.get(style.name, frappe._dict(sales_orders=0, ordered_qty=0, ordered_amount=0))
		style.update(ordered)
		style.status = "Ordered" if ordered.sales_orders else "Not Ordered"
		if filters.get("status") and filters.status != style.status:
			continue
		rows.append(style)
	return rows


def _orders_by_style(styles):
	"""Submitted Sales Order lines whose item was costed from each style."""
	if not styles:
		return {}
	line = frappe.qb.DocType("Sales Order Item")
	query = (
		frappe.qb.from_(line)
		.select(
			line.style_master,
			Count(line.parent).distinct().as_("sales_orders"),
			Sum(line.qty).as_("ordered_qty"),
			Sum(line.base_amount).as_("ordered_amount"),
		)
		.where((line.docstatus == 1) & line.style_master.isin(styles))
		.groupby(line.style_master)
	)
	return {row.style_master: row for row in query.run(as_dict=True)}


def get_columns():
	return [
		{"fieldname": "name", "label": _("Style"), "fieldtype": "Link", "options": "Style Master", "width": 160},
		{"fieldname": "style_master_name", "label": _("Style Name"), "fieldtype": "Data", "width": 160},
		{"fieldname": "customer", "label": _("Buyer"), "fieldtype": "Link", "options": "Customer", "width": 150},
		{"fieldname": "season", "label": _("Season"), "fieldtype": "Link", "options": "Season", "width": 90},
		{"fieldname": "garment_qty", "label": _("Costed Qty"), "fieldtype": "Float", "width": 100},
		{
			"fieldname": "sales_price_target",
			"label": _("Sales Price Target"),
			"fieldtype": "Float",
			"width": 140,
		},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "sales_orders", "label": _("Sales Orders"), "fieldtype": "Int", "width": 110},
		{"fieldname": "ordered_qty", "label": _("Ordered Qty"), "fieldtype": "Float", "width": 110},
		{
			"fieldname": "ordered_amount",
			"label": _("Ordered Amount (Company Currency)"),
			"fieldtype": "Float",
			"width": 220,
		},
	]
