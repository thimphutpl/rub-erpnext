# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("ID"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Disciplinary Action",
            "width": 150
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Student"),
            "fieldname": "student_code",
            "fieldtype": "Link",
            "options": "Student",
            "width": 150
        },
        {
            "label": _("Student Name"),
            "fieldname": "name_student",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Issue Type"),
            "fieldname": "disciplinary_issue_type",
            "fieldtype": "Link",
            "options": "Disciplinary Issue Type",
            "width": 150
        },
        {
            "label": _("Problem Date"),
            "fieldname": "problem_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Time"),
            "fieldname": "problem_time",
            "fieldtype": "Time",
            "width": 100
        },
        {
            "label": _("Location"),
            "fieldname": "location_of_issue_caused",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Reported By"),
            "fieldname": "issue_reported_by",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 150
        },
        {
            "label": _("Semester"),
            "fieldname": "semester",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Section"),
            "fieldname": "section",
            "fieldtype": "Data",
            "width": 100
        },
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("student_code"):
        conditions += " AND student_code = %(student_code)s"
        values["student_code"] = filters.get("student_code")

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND posting_date BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    return frappe.db.sql(f"""
        SELECT
            name,
            posting_date,
            student_code,
            name_student,
            disciplinary_issue_type,
            problem_date,
            problem_time,
            location_of_issue_caused,
            issue_reported_by,
            semester,
            section
        FROM `tabDisciplinary Action`
        WHERE docstatus = 1
        {conditions}
        ORDER BY posting_date DESC
    """, values, as_dict=True)
