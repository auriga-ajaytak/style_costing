import frappe

LEGACY_SERIES = "CMV-STYLE-.YYYY.-"


def execute():
	"""Sites that customised the old series carry a Property Setter pinning
	Style Master to it, which would leave the new default outside its options."""
	frappe.db.delete(
		"Property Setter",
		{"doc_type": "Style Master", "field_name": "naming_series", "value": LEGACY_SERIES},
	)
	frappe.clear_cache(doctype="Style Master")
