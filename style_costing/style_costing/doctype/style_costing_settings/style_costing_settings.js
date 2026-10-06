// Copyright (c) 2026, Auriga and contributors
// For license information, please see license.txt

frappe.ui.form.on("Style Costing Settings", {
	refresh(frm) {
		frappe.call("style_costing.setup.item_override_conflict").then((r) => {
			if (r.message) {
				frm.set_intro(r.message, "orange");
			}
		});

		const installed = JSON.parse(frm.doc.demo_records || "[]").length;
		if (installed) {
			frm.add_custom_button(__("Remove Demo Data"), () => {
				frappe.call("style_costing.demo.remove").then((r) => {
					const kept = r.message || [];
					frappe.msgprint(
						kept.length
							? __("Kept because they are in use: {0}", [kept.map((d) => d[1]).join(", ")])
							: __("Demo data removed.")
					);
					frm.reload_doc();
				});
			});
		} else {
			frm.add_custom_button(__("Install Demo Data"), () => {
				frappe.call("style_costing.demo.install").then((r) => {
					frappe.show_alert(__("{0} demo records created", [r.message]));
					frm.reload_doc();
				});
			});
		}
	},
});
