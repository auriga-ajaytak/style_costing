import frappe

RENAMES = (
	("Season", "Autmn", "Autumn"),
	("Cost Head", "GARMENT REJECTION", "Garment Rejection"),
)


def execute():
	"""The shipped Season and Cost Head records were corrected. Rename the old
	ones so the fixture sync updates them instead of adding a second record."""
	for doctype, old, new in RENAMES:
		# MariaDB compares names case-insensitively, so `new` can match `old`
		if frappe.db.get_value(doctype, old, "name") == old and (
			frappe.db.get_value(doctype, new, "name") in (None, old)
		):
			frappe.rename_doc(doctype, old, new, force=True)
