// Copyright (c) 2026, Auriga and contributors
// For license information, please see license.txt

frappe.query_reports["Style Costing Summary"] = {
	filters: [
		{ fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company" },
		{ fieldname: "customer", label: __("Buyer"), fieldtype: "Link", options: "Customer" },
		{ fieldname: "season", label: __("Season"), fieldtype: "Link", options: "Season" },
		{ fieldname: "segment", label: __("Segment"), fieldtype: "Link", options: "Segment" },
		{ fieldname: "merchandiser", label: __("Merchandiser"), fieldtype: "Link", options: "Employee" },
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Draft", "Submitted", "Cancelled"],
		},
	],
};
