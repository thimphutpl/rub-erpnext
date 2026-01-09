# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "College", "fieldname": "company", "fieldtype": "Data", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Student Code", "fieldname": "student_code", "fieldtype": "Data", "width": 120},
        {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data", "width": 120},
        {"label": "Last Name", "fieldname": "last_name", "fieldtype": "Data", "width": 120},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": "Hostel Room", "fieldname": "hostel_room", "fieldtype": "Data", "width": 100},
        {"label": "Hostel Type", "fieldname": "hostel_type", "fieldtype": "Data", "width": 100},
        {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 60},
        {"label": "Capacity", "fieldname": "capacity", "fieldtype": "Int", "width": 80},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 80},
    ]

def get_data(filters=None):
    if not filters:
        filters = {}

    conditions = []

    if filters.get("company"):
        conditions.append("habu.company = %(company)s")

    condition_str = ""
    if conditions:
        condition_str = " AND " + " AND ".join(conditions)

    query = f"""
        SELECT 
            hai.student_code,
            hai.first_name,
            hai.last_name,
            hai.hostel_room,
            hai.gender,
            hai.hostel_type,
            hai.year,
            hai.capacity,
            hai.status,
            habu.posting_date,
            habu.company
        FROM `tabHostel Allocation Item` AS hai
        INNER JOIN `tabHostel Allocation Bulk Upload` AS habu
        ON hai.parent = habu.name
        WHERE habu.docstatus = 1 {condition_str}
    """

    return frappe.db.sql(query, filters, as_dict=True)
