// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Hostel Room Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": "College",
            "fieldtype": "Link",
            "options": "Company"
        },
		{
            "fieldname": "student_code",
            "label": "Student Code",
            "fieldtype": "Link",
            "options": "Student"
        },
        {
            "fieldname": "hostel_type",
            "label": "Hostel Type",
            "fieldtype": "Link",
            "options": "Hostel Type"
        },
        {
            "fieldname": "asset_code",
            "label": "Asset Code",
            "fieldtype": "Link",
            "options": "Asset"
        },
        
    ]
}
