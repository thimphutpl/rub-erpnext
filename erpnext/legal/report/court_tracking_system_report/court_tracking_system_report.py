# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	column = [
		{
			"fieldname": "court_tracking_id",
			"label": "Case Tracking System",
			"fieldtype": "Link",
			"options": "Case Tracking System",
			"width": 170
		},
		{
			"fieldname": "case_type",
			"label": "Case Type",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "referring_agency",
			"label": "Referring Agency",
			"fieldtype": "Data",
			"width": 250
		},
		{
			"fieldname": "branch",
			"label": "Branch",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "date",
			"label": "Date of Registration/Filing/Complaint",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"fieldname": "status",
			"label": "Case Status",
			"fieldtype": "Data",
			"width": 150
		},
			{
			"fieldname": "date",
			"label": "Date of Registration/Filing/Complaint",
			"fieldtype": "Data",
			"width": 150
		},
		
	]

	if filters.get('case_type') == 'NPL Recovery Cases':
		column.extend([
			{
				"fieldname": "court_venue",
				"label": "Court Venue",
				"fieldtype": "Data",
				"width": 100
			},
			{
				"fieldname": "borrower_filed_by",
				"label": "Borrower/Filed By Name",
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "cid_license_number",
				"label": "CID/License Number",
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "loan_account_no",
				"label": "Loan Account",
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "case_status",
				"label": "Case Status",
				"fieldtype": "Data",
				"width": 180
			},
			{
				"fieldname": "case_description",
				"label": "Case Description",
				"fieldtype": "Data",
				"width": 180
			},
			{
				"fieldname": "case_date",
				"label": "Case Date",
				"fieldtype": "Date",
				"width": 180
			},
		])
	elif filters.get('case_type') == 'Criminal & ACC Cases':
		column.extend([
			{
				"fieldname": "investigation",
				"label": "Investigation",
				"fieldtype": "Data",
				"width": 130
			}
		])
	# elif filters.get('case_type') == 'Civil Litigation':
	# 	column.extend([
	# 		{
	# 			"fieldname": "court_venue",
	# 			"label": "Court Venue",
	# 			"fieldtype": "Data",
	# 			"width": 100
	# 		},
	# 		{
	# 			"fieldname": "borrower_filed_by",
	# 			"label": "Borrower/Filed By Name",
	# 			"fieldtype": "Data",
	# 			"width": 130
	# 		},
	# 		{
	# 			"fieldname": "cid_license_number",
	# 			"label": "CID/License Number",
	# 			"fieldtype": "Data",
	# 			"width": 130
	# 		},
	# 	])

	return column

def get_data(filters):
	if not filters.get('case_type'):
		return []
	
	condition = ""
	if filters.get('case_type'):
		condition = f" AND case_type='{filters.get('case_type')}'"
	
	if filters.get('case_type') == 'Criminal & ACC Cases':
		query = """
			SELECT 
				a.name AS court_tracking_id,
				a.branch,
				a.case_type,
				a.investigation,
				a.date
			FROM `tabCase Tracking System` a
			WHERE a.docstatus = 1
			AND a.date BETWEEN '{from_date}' AND '{to_date}'
			{cond}
			ORDER BY a.date DESC
			""".format(cond=condition, from_date=filters.get('from_date'), to_date=filters.get('to_date'))
		result = frappe.db.sql(query, as_dict=1)
		return result

	query = """
		SELECT 
			a.name AS court_tracking_id,
			a.branch,
			a.case_type,
			a.court_venue,
			a.date,
			a.referring_agency,
			a.status
		FROM `tabCase Tracking System` a
		WHERE a.docstatus = 0
		{cond}
		ORDER BY a.date DESC
		""".format(cond=condition, from_date=filters.get('from_date'), to_date=filters.get('to_date'))
	
	result = frappe.db.sql(query, as_dict=1)

	return result