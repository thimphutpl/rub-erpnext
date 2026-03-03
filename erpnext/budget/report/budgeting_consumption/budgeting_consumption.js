// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budgeting Consumption"] = {
	"filters": [
		{
            fieldname: "college",
            label: __("College"),
            fieldtype: "Link",
            options: "Company"
        },
		{
            fieldname: "fiscal_year",
            label: __("Fiscal Year"),
            fieldtype: "Link",
            options: "Fiscal Year"
        },

	]
};
