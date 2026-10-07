// Copyright (c) 2026, Auriga and contributors
// For license information, please see license.txt

frappe.query_reports["Style Order Tracking"] = {
	filters: [
		{ fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company" },
		{ fieldname: "customer", label: __("Buyer"), fieldtype: "Link", options: "Customer" },
		{ fieldname: "season", label: __("Season"), fieldtype: "Link", options: "Season" },
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: ["", "Ordered", "Not Ordered"] },
	],
};
