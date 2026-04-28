// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Hostel Check-In Summary"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Hostel Check-In Summary"] = {
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
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "hostel_room",
            "label": "Hostel Room",
            "fieldtype": "Link",
            "options": "Hostel Room"
        }
    ]
};
