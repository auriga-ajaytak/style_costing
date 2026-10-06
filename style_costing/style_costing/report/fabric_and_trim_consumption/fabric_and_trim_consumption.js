// Copyright (c) 2026, Auriga and contributors
// For license information, please see license.txt

frappe.query_reports["Fabric and Trim Consumption"] = {
	filters: [
		{ fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company" },
		{ fieldname: "style", label: __("Style"), fieldtype: "Link", options: "Style Master" },
		{ fieldname: "customer", label: __("Buyer"), fieldtype: "Link", options: "Customer" },
		{ fieldname: "season", label: __("Season"), fieldtype: "Link", options: "Season" },
		{ fieldname: "material", label: __("Material"), fieldtype: "Select", options: ["", "Fabric", "Trims"] },
		{ fieldname: "item", label: __("Item"), fieldtype: "Link", options: "Item" },
	],
};
