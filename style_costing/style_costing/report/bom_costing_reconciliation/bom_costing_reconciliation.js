// Copyright (c) 2026, Auriga and contributors
// For license information, please see license.txt

frappe.query_reports["BOM Costing Reconciliation"] = {
	filters: [
		{ fieldname: "style", label: __("Style"), fieldtype: "Link", options: "Style Master", reqd: 1 },
		{ fieldname: "differences_only", label: __("Differences Only"), fieldtype: "Check" },
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "status" && data && data.status !== "Match") {
			value = `<span class="text-danger">${value}</span>`;
		}
		return value;
	},
};
