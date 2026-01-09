# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": "College", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
        {"label": "Student Code", "fieldname": "student_code", "fieldtype": "Link","options": "Student", "width": 150},
        {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data", "width": 200},
        {"label": "Last Name", "fieldname": "last_name", "fieldtype": "Data", "width": 200},
        {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 120},
        {"label": "Hostel Type", "fieldname": "hostel_type", "fieldtype": "Link", "options": "Hostel Type", "width": 120},
        {"label": "Room Number", "fieldname": "room_number", "fieldtype": "Data", "width": 150},
        {"label": "Capacity", "fieldname": "capacity", "fieldtype": "Int", "width": 150},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Data", "width": 120},
        {"label": "Room Description", "fieldname": "room_description", "fieldtype": "Text", "width": 120},
        {"label": "Asset Code", "fieldname": "asset_code", "fieldtype": "Link","options": "Asset", "width": 150},
        {"label": "Number of Asset", "fieldname": "number_of_asset", "fieldtype": "Data", "width": 120},
    ]
    conditions = []
    if filters.get("hostel_type"):
        conditions.append(f"hr.hostel_type = '{filters.get('hostel_type')}'")
    if filters.get("company"):
        conditions.append(f"hr.company = '{filters.get('company')}'")
    if filters.get("asset_code"):
        conditions.append(f"hai.asset_code = '{filters.get('asset_code')}'")
    if filters.get("student_code"):
        conditions.append(f"sli.student_code = '{filters.get('student_code')}'")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    # SQL query
    data = frappe.db.sql(f"""
        SELECT
            hr.company,
            hr.hostel_type,
            hr.room_number,
            hr.capacity,
            hr.cost_center,
            hr.room_description,
            
            hai.asset_code,
            hai.number_of_asset,
            
            sli.student_code,
            sli.first_name,
            sli.last_name,
            sli.year
            
        FROM `tabHostel Room` hr
        LEFT JOIN `tabHostel Asset Item` hai
            ON hr.name = hai.parent AND hai.docstatus = 0
        LEFT JOIN `tabStudent List Item` sli
            ON hr.name = sli.parent AND sli.docstatus = 0
        {where_clause}
        ORDER BY hr.company, hr.room_number, sli.student_code
    """, as_dict=True)

    return columns, data