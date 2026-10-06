# Copyright (c) 2026, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.model.document import Document
from frappe.model.naming import NamingSeries

# Other Cost columns carried from the settings onto a new style
COST_HEAD_FIELDS = (
	"cost_head",
	"based_on",
	"charge_on",
	"percent_our",
	"percent_buyer",
	"rate_our",
	"rate_buyer",
	"currency",
)


class StyleCostingSettings(Document):
	def validate(self):
		self.style_naming_series = (self.style_naming_series or "").strip()
		NamingSeries(self.style_naming_series).validate()

	def on_update(self):
		# Style Master names itself from its naming_series Select, the same
		# mechanism Document Naming Settings drives.
		# The default is cleared first: it has to be one of the options.
		for prop, value in (
			("default", ""),
			("options", self.style_naming_series),
			("default", self.style_naming_series),
		):
			make_property_setter("Style Master", "naming_series", prop, value, "Text")
		frappe.clear_cache(doctype="Style Master")
		# clear_cache leaves this request's new-document template, which still
		# carries the previous default series.
		frappe.local.new_doc_templates.pop("Style Master", None)


@frappe.whitelist()
def get_style_defaults():
	"""Defaults a new Style Master starts from. The settings themselves are
	System Manager only, so the form reads them through here."""
	frappe.has_permission("Style Master", "read", throw=True)
	settings = frappe.get_cached_doc("Style Costing Settings")
	return {
		"style_rate": settings.default_style_rate,
		"efficiency": settings.default_efficiency,
		"cost_heads": [{f: row.get(f) for f in COST_HEAD_FIELDS} for row in settings.default_cost_heads],
	}
