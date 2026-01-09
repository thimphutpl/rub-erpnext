// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Hostel Allocation Bulk Upload Report"] = {
	"filters": [
		{
            "fieldname": "company",
            "label": "College",
            "fieldtype": "Link",
            "options": "Company"
        }
    ]
};
