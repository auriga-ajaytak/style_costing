# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

STATUS = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
LINK_FILTERS = ("company", "customer", "season", "segment", "merchandiser")


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_data(filters):
	conditions = {f: filters[f] for f in LINK_FILTERS if filters.get(f)}
	if filters.get("status"):
		conditions["docstatus"] = {v: k for k, v in STATUS.items()}[filters.status]
	else:
		conditions["docstatus"] = ("<", 2)

	styles = frappe.get_list(
		"Style Master",
		filters=conditions,
		fields=[
			"name",
			"style_master_name",
			"style_number",
			"customer",
			"season",
			"segment",
			"merchandiser",
			"docstatus",
			"garment_qty",
			"currency",
			"cost_price_our",
			"sales_price_target",
		],
		order_by="creation desc",
	)
	for style in styles:
		# The same Difference (B - A) the costing sheet shows, off the stored totals
		style.status = STATUS[style.docstatus]
		style.margin = flt(style.sales_price_target) - flt(style.cost_price_our)
		style.margin_percent = (
			style.margin / style.sales_price_target * 100 if flt(style.sales_price_target) else 0
		)
	return styles


def get_columns():
	return [
		{"fieldname": "name", "label": _("Style"), "fieldtype": "Link", "options": "Style Master", "width": 160},
		{"fieldname": "style_master_name", "label": _("Style Name"), "fieldtype": "Data", "width": 160},
		{"fieldname": "style_number", "label": _("Style Number"), "fieldtype": "Data", "width": 120},
		{"fieldname": "customer", "label": _("Buyer"), "fieldtype": "Link", "options": "Customer", "width": 150},
		{"fieldname": "season", "label": _("Season"), "fieldtype": "Link", "options": "Season", "width": 90},
		{"fieldname": "segment", "label": _("Segment"), "fieldtype": "Link", "options": "Segment", "width": 90},
		{
			"fieldname": "merchandiser",
			"label": _("Merchandiser"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 130,
		},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 90},
		{"fieldname": "garment_qty", "label": _("Garment Qty"), "fieldtype": "Float", "width": 100},
		{"fieldname": "currency", "label": _("Currency"), "fieldtype": "Link", "options": "Currency", "width": 80},
		{"fieldname": "cost_price_our", "label": _("Total Cost (A)"), "fieldtype": "Float", "width": 120},
		{
			"fieldname": "sales_price_target",
			"label": _("Sales Price Target (B)"),
			"fieldtype": "Float",
			"width": 150,
		},
		{"fieldname": "margin", "label": _("Difference (B - A)"), "fieldtype": "Float", "width": 130},
		{"fieldname": "margin_percent", "label": _("Margin %"), "fieldtype": "Percent", "width": 90},
	]
