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
		{"label": _("College"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
		{"label": _("Fiscal Year"), "fieldname": "fiscal_yaer", "fieldtype": "Link", "options": "Fiscal Yaer", "width": 150},
		{"label": _("Check-In ID"), "fieldname": "checkin", "fieldtype": "Link", "options": "Hostel Check-In Form", "width": 150},
		{"label": _("Check-In Date"), "fieldname": "checkin_date", "fieldtype": "Date", "width": 120},

		{"label": _("Check-Out ID"), "fieldname": "checkout", "fieldtype": "Link", "options": "Hostel Check-Out Form", "width": 150},
		{"label": _("Check-Out Date"), "fieldname": "checkout_date", "fieldtype": "Date", "width": 120},

		{"label": _("Hostel Room"), "fieldname": "hostel_room", "fieldtype": "Link", "options": "Hostel Room", "width": 150},

		{"label": _("Student Code"), "fieldname": "student_code", "width": 120},
		{"label": _("Student Name"), "fieldname": "student_name", "width": 180},
		{"label": _("Year"), "fieldname": "year", "width": 80},

		{"label": _("Asset Code"), "fieldname": "asset_code", "width": 120},
		{"label": _("Asset Name"), "fieldname": "asset_name", "width": 150},

		{"label": _("Condition (Check-In)"), "fieldname": "condition_in", "width": 150},
		{"label": _("Condition (Check-Out)"), "fieldname": "condition_out", "width": 150},

		{"label": _("Remarks (In)"), "fieldname": "remarks_in", "width": 200},
		{"label": _("Remarks (Out)"), "fieldname": "remarks_out", "width": 200},
	]


def get_data(filters):
	conditions = "1=1"

	if filters.get("from_date"):
		conditions += " AND h.posting_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND h.posting_date <= %(to_date)s"

	if filters.get("hostel_room"):
		conditions += " AND h.hostel_room = %(hostel_room)s"

	if filters.get("company"):
		conditions += " AND h.company = %(company)s"	

	if filters.get("student_code"):
		conditions += " AND s.student_code = %(student_code)s"		

	data = frappe.db.sql(f"""
		SELECT
			h.name AS checkin,
			h.posting_date AS checkin_date,
			h.company,
			h.fiscal_year,

			co.name AS checkout,
			co.posting_date AS checkout_date,

			h.hostel_room,

			s.student_code,
			s.student_name,
			s.year,

			a.asset_code,
			a.asset_name,
			a.asset_condition AS condition_in,
			a.remarks AS remarks_in,

			co_a.asset_condition_check_out AS condition_out,
			co_a.remarks_check_out AS remarks_out

		FROM `tabHostel Check-In Form` h

		LEFT JOIN `tabHostel Check-Out Form` co
			ON co.hostel_check_in_link = h.name

		LEFT JOIN `tabCheck-In Students Items` s
			ON s.parent = h.name

		LEFT JOIN `tabCheck-In Asset Items` a
			ON a.parent = h.name

		LEFT JOIN `tabCheck-Out Asset Items` co_a
			ON co_a.parent = co.name
			AND co_a.asset_code = a.asset_code

		WHERE {conditions}

		ORDER BY h.posting_date DESC
	""", filters, as_dict=1)

	return data