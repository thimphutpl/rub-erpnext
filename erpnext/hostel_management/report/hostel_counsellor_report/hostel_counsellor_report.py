# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}
    columns = [
        {"label": "No.", "fieldname": "idx", "fieldtype": "Int", "width": 50},
        {"label": "Student Code", "fieldname": "student_code", "fieldtype": "Link", "options": "Student", "width": 150},
        {"label": "Full Name", "fieldname": "full_name", "fieldtype": "Data", "width": 200},
        {"label": "Programme", "fieldname": "programme", "fieldtype": "Data", "width": 200},
        {"label": "Student Responsibility", "fieldname": "student_responsibility", "fieldtype": "Data", "width": 180},
        {"label": "College", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
        {"label": "Hostel Block", "fieldname": "hostel_block", "fieldtype": "Data", "width": 150},
        {"label": "Hostel Type", "fieldname": "hostel_type", "fieldtype": "Data", "width": 150},
        {"label": "Room Number", "fieldname": "room_number", "fieldtype": "Data", "width": 140},
        {"label": "Hostel Capacity", "fieldname": "hostel_capacity", "fieldtype": "Int", "width": 120},
    ]
    conditions = ["sd.student_responsibiltiy = 'Hostel Counsellor'"]
    values = []

    if filters.get("academic_year"):
        conditions.append("slac.academic_year = %s")
        values.append(filters.get("academic_year"))

    if filters.get("academic_term"):
        conditions.append("slac.academic_term = %s")
        values.append(filters.get("academic_term"))

    if filters.get("college"):
        conditions.append("slac.company = %s")
        values.append(filters.get("college"))

    if filters.get("hostel_block"):
        conditions.append("hc.hostel_block = %s")
        values.append(filters.get("hostel_block"))

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT
            slac.academic_year,
            slac.company,
            slac.academic_term,
            sd.student_code,
            sd.full_name,
            sd.programme,
            sd.student_responsibiltiy AS student_responsibility,
            hc.hostel_block,
            cd.hostel_type,
            cd.room_number,
            cd.hostel_capacity
        FROM
            `tabStudent Leader and Coordinator List` slac
        JOIN
            `tabStudent Leader and Coordinator Items` sd
                ON sd.parent = slac.name
        LEFT JOIN
            `tabHostel Counsellor` hc
                ON sd.hostel_counsellor = hc.name
        LEFT JOIN
            `tabBlock Counsellor Details` cd
                ON cd.parent = hc.name
        WHERE
            {where_clause}
    """
    data = frappe.db.sql(query, tuple(values), as_dict=True)
    for idx, row in enumerate(data, start=1):
        row["idx"] = idx

    return columns, data

