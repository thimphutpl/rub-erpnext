// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Outstanding Report"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Outstanding Report"] = {
    filters: [

		 {
            fieldname: "company",
            label: __("College"),
            fieldtype: "Link",
            options: "Company"
        },
        {
            fieldname: "supplier",
            label: __("Supplier"),
            fieldtype: "Link",
            options: "Supplier"
        },
       
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date"
        }
    ]
};