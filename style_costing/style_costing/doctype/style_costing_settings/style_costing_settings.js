// Copyright (c) 2026, Auriga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Style Costing Settings", {
	refresh(frm) {
		frappe.call("style_costing.setup.item_override_conflict").then((r) => {
			if (r.message) {
				frm.set_intro(r.message, "orange");
			}
		});
	},
});
