// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Hostel Change Application Report"] = {
	"filters": [
		{
            "fieldname": "company",
            "label": "College",
            "fieldtype": "Link",
            "options": "Company"
        },
        {
            "fieldname": "current_room",
            "label": "Current Room",
            "fieldtype": "Link",
            "options": "Hostel Room"
        },
        {
            "fieldname": "requested_room",
            "label": "Requested Room",
            "fieldtype": "Link",
            "options": "Hostel Room"
        },
		
        
    ]
};
