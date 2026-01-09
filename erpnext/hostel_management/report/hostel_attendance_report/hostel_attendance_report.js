frappe.query_reports["Hostel Attendance Report"] = {
    "filters": [
        {
            "fieldname": "college",
            "label": __("College"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 0
        },
        {
            "fieldname": "hostel_block",
            "label": __("Hostel Block"),
            "fieldtype": "Link",
            "options": "Hostel Counsellor",
            "reqd": 0
        },
        {
            "fieldname": "student_code",
            "label": __("Student Code"),
            "fieldtype": "Link",
            "options": "Student",
            "reqd": 0
        },
        
    ]
}
