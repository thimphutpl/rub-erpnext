# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": "College", "fieldname": "college", "fieldtype": "Link", "options": "Company", "width": 200},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Hostel Councilor", "fieldname": "hostel_councilor", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Hostel Councilor Name", "fieldname": "hostel_councilor_name", "fieldtype": "Data", "width": 150},
        {"label": "Hostel Block", "fieldname": "hostel_block", "fieldtype": "Data", "width": 120},
        {"label": "Expense Type", "fieldname": "expense_type", "fieldtype": "Data", "width": 120},
        {"label": "Total Budget Collection", "fieldname": "total_budget_collection", "fieldtype": "Float", "width": 150},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Float", "width": 120},
        {"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": "Balance Amount", "fieldname": "balance_amount", "fieldtype": "Float", "width": 120},
    ]

    conditions = "hb.docstatus = 1"
    values = []

    if filters.get("college"):
        conditions += " AND hb.college = %s"
        values.append(filters.get("college"))

    if filters.get("hostel_councilor_name"):
        conditions += " AND hb.hostel_councilor_name = %s"
        values.append(filters.get("hostel_councilor_name"))

    if filters.get("posting_date"):
        conditions += " AND hb.posting_date = %s"
        values.append(filters.get("posting_date"))

    query = f"""
        SELECT
            hb.college,
            hb.posting_date,
            hb.hostel_councilor,
            hb.hostel_councilor_name,
            hb.hostel_block,
            hb.expense_type,
            hb.total_budget_collection,
            COALESCE(SUM(hbi.amount), 0) AS amount,
            GROUP_CONCAT(hbi.description) AS description,
            hb.total_budget_collection - COALESCE(SUM(hbi.amount), 0) AS balance_amount
        FROM
            `tabHostel Budget` hb
        LEFT JOIN
            `tabHostel Budget Item` hbi
        ON
            hb.name = hbi.parent
        WHERE
            {conditions}
        GROUP BY
            hb.name
        ORDER BY
            hb.posting_date ASC
    """

    data = frappe.db.sql(query, tuple(values), as_dict=True)

    return columns, data
