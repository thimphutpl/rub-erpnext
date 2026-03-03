# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": "Activities ",
			"fieldname": "activities",
			"fieldtype": "Link",
			"options": "Planning Activities",
			"width": 100
		},
		{
			"label": "Activities Name",
			"fieldname": "activities_name",
			"fieldtype": "Link",
			"options": "Planning Activities",
			"width": 200
		},
		{
			"label": "Initial",
			"fieldname": "initial",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Reappropiation Received",
			"fieldname": "reappropiation_received",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Reappropiation Sent",
			"fieldname": "reappropiation_sent",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Supplementary Received",
			"fieldname": "supplementary_received",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Current",
			"fieldname": "current",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Committed",
			"fieldname": "committed",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Consumed",
			"fieldname": "consumed",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Available",
			"fieldname": "available",
			"fieldtype": "Currency",
			"width": 120
		},
	]


def get_data(filters):
	filters = filters or {}

	conditions = []
	values = {}

	if filters.get("college"):
		conditions.append("mc.college = %(college)s")
		values["college"] = filters.get("college")

	if filters.get("semester"):
		conditions.append("mc.module_semester = %(semester)s")
		values["semester"] = filters.get("semester")

	if filters.get("programme"):
		conditions.append("mc.programme = %(programme)s")
		values["programme"] = filters.get("programme")

	condition_sql = ""
	if conditions:
		condition_sql = "WHERE " + " AND ".join(conditions)

	query = f"""
		select name as activities, activities as activities_name from `tabPlanning Activities`;
	"""



	data = frappe.db.sql(query, values, as_dict=True)

	college = filters.get("college")
	fiscal_year = filters.get("fiscal_year")

	if college and fiscal_year:
		for i in data:
			budgets = frappe.db.sql('''
			select abi.approved_budget,abi.reappropiation_received,
			abi.reappropiation_sent,abi.supplementary_received,
			abi.activity_link from `tabApproved Budget Item` abi 
			inner join `tabApproved Budget` ab on abi.parent=ab.name 
			where ab.college=%s 
			and fiscal_year=%s
			and activity_link = %s
			''',(college, fiscal_year, i.activities))
			# frappe.throw(str(budgets))
			# approved_budget = budgets[0][0]
			# approved_budget = budgets[0][0] if budgets and budgets[0][0] else 0
			# reappropiation_received= budgets[0][1]
			# reappropiation_sent = budgets[0][2]
			# supplementary_received = budgets[0][3]
			# activity_link = budgets[0][4]
			if budgets:
				row = budgets[0]

				approved_budget = row[0] or 0
				reappropiation_received = row[1] or 0
				reappropiation_sent = row[2] or 0
				supplementary_received = row[3] or 0
				activity_link = row[4]
			else:
				approved_budget = 0
				reappropiation_received = 0
				reappropiation_sent = 0
				supplementary_received = 0
				activity_link = None

			current = flt(approved_budget) + flt(reappropiation_received)- flt(reappropiation_sent) + flt(supplementary_received)

			from_date = f"{fiscal_year}-01-01"
			to_date = f"{fiscal_year}-12-31"
			committed = frappe.db.sql("""
				SELECT SUM(amount)
				FROM `tabCommitted Budget`
				WHERE company = %s
				AND reference_date BETWEEN %s AND %s
				AND business_activity = %s
			""", (
				college,
				from_date,
				to_date,
				i.activities
			))[0][0]

			committed = flt(committed)

			consumed = frappe.db.sql("""
				SELECT SUM(amount)
				FROM `tabConsumed Budget`
				WHERE company = %s
				AND reference_date BETWEEN %s AND %s
				AND business_activity = %s
			""", (
				college,
				from_date,
				to_date,
				i.activities
			))[0][0]

			consumed = flt(consumed)

			available = flt(current) - consumed

			i['initial'] = approved_budget
			i['reappropiation_received'] = reappropiation_received
			i['reappropiation_sent'] = reappropiation_sent
			i['supplementary_received'] = supplementary_received
			i['current'] = current
			i['committed'] = committed
			i['consumed'] = consumed
			i['available'] = available

			
	# for i in data:
		

	# #Adding total marks for each module here on
	# new_data = []

	# for row in data:
	#     # First copy → Continuous Assessment
	#     ca_row = row.copy()
	#     ca_row["type"] = "CA"
	#     new_data.append(ca_row)

	#     # Second copy → Semester Exam
	#     se_row = row.copy()
	#     se_row["type"] = "SE"
	#     new_data.append(se_row)

	# data = new_data

	# student = filters.get("student")
	# college = filters.get("college")
	# programme = filters.get("programme")
	# semester = filters.get("semester")

	# for i in data:
	#     # Determine the assessment type
	#     if i.type == 'SE':
	#         assessment_type = 'Semester Exam'
	#     elif i.type == 'CA':
	#         assessment_type = 'Continuous Assessment'
	#     else:
	#         continue  # skip if type is unknown

	#     total = frappe.db.sql("""
	#         SELECT SUM(al.weightage_achieved), SUM(al.assessment_weightage)
	#         FROM `tabAssessment Ledger` al
	#         INNER JOIN `tabAssessment Component` ac
	#             ON al.assessment_component = ac.name
	#         WHERE al.student = %s
	#         AND al.college = %s
	#         AND al.programme = %s
	#         AND al.semester = %s
	#         AND al.module = %s
	#         AND al.is_cancelled != 1
	#         AND ac.assessment_component_type = %s
	#     """, (student, college, programme, semester, i.module, assessment_type))

	#     i["marks_secured"] = total[0][0] or 0
	#     i['max_marks']=total[0][1] or 0

		

	# frappe.throw(frappe.as_json(data))

	return data