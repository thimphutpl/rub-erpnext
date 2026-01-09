# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters=None):
	conditions = []

	if filters.get("company"):
		conditions.append("hca.company = %(company)s")
	if filters.get("current_room"):
		conditions.append("hca.current_room = %(current_room)s")
	if filters.get("requested_room"):
		conditions.append("hca.requested_room = %(requested_room)s")

	condition_str = " AND ".join(conditions)
	if condition_str:
		condition_str = " AND " + condition_str

	query = f"""
		SELECT
			hca.company,
			hca.applied_by,
			s1.first_name as applied_by_first_name,
			s1.last_name as applied_by_last_name,
			hca.current_room,
			hca.hostel_type,
			hca.requested_room,
			hca.student_code,
			s2.first_name as student_first_name,
			s2.last_name as student_last_name,
			hr.name as student_room,
			hr.hostel_type as student_hostel_type,
			hca.reason_for_change_for_student as reason,
			hca.comments_approver,
			CASE 
				WHEN hca.qrc = 1 THEN 'Switch Room'
				ELSE 'Room Change'
			END as request_type
		FROM `tabHostel Change Application` hca
		LEFT JOIN `tabStudent` s1 ON s1.name = hca.applied_by
		LEFT JOIN `tabStudent` s2 ON s2.name = hca.student_code
		LEFT JOIN `tabHostel Room` hr ON hr.name = hca.room
		WHERE hca.docstatus = 1 {condition_str}
	"""
	return frappe.db.sql(query, filters, as_dict=True)

def get_columns():	
	return [
		{"label": "College", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
		{"label": "Applied By", "fieldname": "applied_by", "fieldtype": "Link", "options": "Student", "width": 150},
		{"label": "Applied By First Name", "fieldname": "applied_by_first_name", "fieldtype": "Data", "width": 150},
		{"label": "Applied By Last Name", "fieldname": "applied_by_last_name", "fieldtype": "Data", "width": 150},
		{"label": "Current Room", "fieldname": "current_room", "fieldtype": "Link", "options": "Hostel Room", "width": 120},
		{"label": "Hostel Type", "fieldname": "hostel_type", "fieldtype": "Data", "width": 120},
		{"label": "Requested Room", "fieldname": "requested_room", "fieldtype": "Link", "options": "Hostel Room", "width": 120},
		{"label": "Request Type", "fieldname": "request_type", "fieldtype": "Data", "width": 120},
		{"label": "Student Code", "fieldname": "student_code", "fieldtype": "Link", "options": "Student", "width": 150},
		{"label": "Student First Name", "fieldname": "student_first_name", "fieldtype": "Data", "width": 150},
		{"label": "Student Last Name", "fieldname": "student_last_name", "fieldtype": "Data", "width": 150},
		{"label": "Student Room", "fieldname": "student_room", "fieldtype": "Link", "options": "Hostel Room", "width": 120},
		{"label": "Student Hostel Type", "fieldname": "student_hostel_type", "fieldtype": "Data", "width": 120},
		{"label": "Reason for Change", "fieldname": "reason", "fieldtype": "Small Text", "width": 250},
		{"label": "Comments (Approver)", "fieldname": "comments_approver", "fieldtype": "Small Text", "width": 200},
	]
