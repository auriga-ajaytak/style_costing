# Copyright (c) 2022, Auriga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

# Link queries live in style_costing.queries; re-exported here so that
# older `set_query` paths keep resolving.
from style_costing.queries import (
	fabric_item_group_wise_items,
	get_doc_wise_columns,
	get_merchandisers,
	trims_item_group_wise_items,
	value_addition_fabric,
)


class StyleMaster(Document):
	def validate(self):
		if self.item:
			self.style_master_name = frappe.get_cached_value("Item", self.item, "item_name")

	def on_update(self):
		self.link_garment_items()

	def link_garment_items(self):
		"""Point the style's Item and its variants back at the style, so Sales
		Order lines trace to it without anyone setting Item.style_master by hand.

		An Item keeps the first style that claimed it - the same garment can be
		costed again for another buyer or season - except that an amended style
		takes over from the one it replaces.
		"""
		item = frappe.qb.DocType("Item")
		is_ours = (item.name == self.item) | (item.variant_of == self.item)

		# the style used to be for a different Item
		frappe.qb.update(item).set(item.style_master, None).where(
			(item.style_master == self.name) & ~is_ours
		).run()

		if not self.item:
			return
		unclaimed = item.style_master.isnull() | (item.style_master == "")
		if self.amended_from:
			unclaimed = unclaimed | (item.style_master == self.amended_from)
		frappe.qb.update(item).set(item.style_master, self.name).where(is_ours & unclaimed).run()
