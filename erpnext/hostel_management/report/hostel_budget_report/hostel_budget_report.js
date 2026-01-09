// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Hostel Budget Report"] = {
    "filters": [
        {
            "fieldname": "college",
            "label": "College",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 0
        },
        {
            "fieldname": "hostel_councilor_name",
            "label": "Hostel Councilor Name",
            "fieldtype": "Link",
            "options": "Student",
            "reqd": 0
        },
        {
            "fieldname": "posting_date",
            "label": "Posting Date",
            "fieldtype": "Date",
            "reqd": 0
        }
    ]
};
