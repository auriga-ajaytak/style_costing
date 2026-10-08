# Copyright (c) 2022, Auriga and contributors
# For license information, please see license.txt

from style_costing.item_types import get_item_type


def validate(doc, event):
	"""Record whether the Item is a fabric, a trim or a garment, from the Item
	Groups listed in Style Costing Settings. The Item form shows its fabric or
	trim fields off this."""
	doc.item_group_category = get_item_type(doc.item_group)
