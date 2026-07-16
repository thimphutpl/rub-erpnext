# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	# frappe.throw(str(data))
	return columns, data


def get_columns():
	return [
		{
			"label": "Cost Center",
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200
		},
		{
			"label": "Activity Type",
			"fieldname": "activity_type",
			"fieldtype": "Select",
			"options": ["Planning Activities", "Additional Activities"],
			"width": 200
		},
		{
			"label": "Activities",
			"fieldname": "activities",
			"fieldtype": "Dynamic Link",
			"options": "activity_type",
			"width": 100
		},
		{
			"label": "Activities Name",
			"fieldname": "activities_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": "Budget Type",
			"fieldname": "budget_type",
			"fieldtype": "Data",
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
			"label": "Withdrawal Amount",
			"fieldname": "withdrawal_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Current",
			"fieldname": "current",
			"fieldtype": "Currency",
			"width": 120
		},
		# {
		# 	"label": "Committed",
		# 	"fieldname": "committed",
		# 	"fieldtype": "Currency",
		# 	"width": 120
		# },
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
	values = {}
	conditions = []
	planning_condition = ""
	additional_condition = ""
	# budget_type_condition = ""

	if filters.get("cost_center"):
		conditions.append("AND ab.cost_center = %(cost_center)s")
		values["cost_center"] = filters.get("cost_center")
	if filters.get("activity"):
		conditions.append("AND abi.activity_link = %(activity)s")
		values["activity"] = filters.get("activity")

	activity_type = filters.get("activity_type")
	budget_type = filters.get("budget_type")

	if activity_type == "Planning Activities":
		additional_condition = "AND 1 = 0"
	elif activity_type == "Additional Activities":
		planning_condition = "AND 1 = 0"
	# if budget_type == "Current":
	# 	budget_type_condition = "AND 1 = 0"
	# elif budget_type == "Capital":
	# 	budget_type_condition = "AND 1 = 0"
	conditions = "\n".join(conditions)

	college = filters.get("college")
	from_year = filters.get("from_year")
	end_year = filters.get("to_year")

	values["college"] = college
	values["from_year"] = from_year
	values["end_year"] = end_year

	query = f"""
		SELECT
			pa.name AS activities,
			pa.activities AS activities_name,
			'Planning Activities' AS activity_type
		FROM `tabPlanning Activities` pa
		WHERE pa.disabled = 0
			AND YEAR(pa.from_date) <= %(end_year)s
			AND YEAR(pa.to_date) >= %(from_year)s
			AND EXISTS (
				SELECT 1
				FROM `tabApproved Budget Item` abi
				INNER JOIN `tabApproved Budget` ab
					ON abi.parent = ab.name
				WHERE abi.activity_link = pa.name
					AND ab.college = %(college)s
					AND %(from_year)s >= ab.from_year
					AND %(end_year)s <= ab.to_year
					AND ab.docstatus = 1
					{conditions}{planning_condition}
			)

		UNION ALL

		SELECT
			aa.name AS activities,
			aa.activities AS activities_name,
			'Additional Activities' AS activity_type
		FROM `tabAdditional Activities` aa
		WHERE aa.disabled = 0
			AND aa.college = %(college)s
			AND aa.from_year <= %(end_year)s
			AND aa.to_year >= %(from_year)s
			AND EXISTS (
				SELECT 1
				FROM `tabApproved Budget Extra Item` abi
				INNER JOIN `tabApproved Budget` ab
					ON abi.parent = ab.name
				WHERE abi.activity_link = aa.name
					AND ab.college = %(college)s
					AND %(from_year)s >= ab.from_year
					AND %(end_year)s <= ab.to_year
					AND ab.docstatus = 1
					{conditions}{additional_condition}
			)
	"""

	data = frappe.db.sql(query, values, as_dict=True)

	if college and from_year and end_year:
		for i in data:
			values["activity"] = i.activities
			budgets = frappe.db.sql(f"""
				SELECT
					abi.approved_budget,
					abi.reappropiation_received,
					abi.reappropiation_sent,
					abi.supplementary_received,
					abi.withdrawal_amount,
					CASE
						WHEN abi.is_current = 1 THEN 'Current'
						WHEN abi.is_capital = 1 THEN 'Capital'
					END AS budget_type,
					abi.initial_approved_budget,
					ab.cost_center
				FROM (
					SELECT
						parent,
						approved_budget,
						reappropiation_received,
						reappropiation_sent,
						supplementary_received,
						withdrawal_amount,
						is_current,
						is_capital,
						initial_approved_budget,
						activity_link
					FROM `tabApproved Budget Item`

					UNION ALL

					SELECT
						parent,
						approved_budget,
						reappropiation_received,
						reappropiation_sent,
						supplementary_received,
						withdrawal_amount,
						is_current,
						is_capital,
						initial_approved_budget,
						activity_link
					FROM `tabApproved Budget Extra Item`
				) abi
				LEFT JOIN `tabApproved Budget` ab
					ON abi.parent = ab.name
				WHERE ab.college = %(college)s
					AND %(from_year)s >= ab.from_year
					AND %(end_year)s <= ab.to_year
					AND abi.activity_link = %(activity)s
					AND ab.docstatus = 1
					{conditions}
			""", values, as_dict=True)
			if budgets:
				row = budgets[0]
				approved_budget = flt(row.approved_budget) * 1000000
				reappropiation_received = flt(row.reappropiation_received) * 1000000
				reappropiation_sent = flt(row.reappropiation_sent) * 1000000
				supplementary_received = flt(row.supplementary_received) * 1000000
				withdrawal_amount = flt(row.withdrawal_amount) * 1000000
				budget_type = row.budget_type
				initial_approved_budget = flt(row.initial_approved_budget) * 1000000
				cost_center = row.cost_center
			else:
				approved_budget = 0
				reappropiation_received = 0
				reappropiation_sent = 0
				supplementary_received = 0
				withdrawal_amount = 0
				budget_type = None
				initial_approved_budget = 0
				cost_center = None

			current = flt(initial_approved_budget) + flt(reappropiation_received)- flt(reappropiation_sent) + flt(supplementary_received) - flt(withdrawal_amount)

			from_date = f"{from_year}-07-01"
			to_date = f"{end_year}-06-30"
			consumed = flt(frappe.db.sql("""
				SELECT SUM(amount)
				FROM `tabConsumed Budget`
				WHERE company = %s
				AND reference_date BETWEEN %s AND %s
				AND activity_type = %s
				AND activity = %s
				AND cost_center = %s
			""", (
				college,
				from_date,
				to_date,
				i.activity_type,
				i.activities,
				cost_center
			))[0][0])

			# committed = flt(frappe.db.sql("""
			# 	SELECT SUM(amount)
			# 	FROM `tabCommitted Budget`
			# 	WHERE company = %s
			# 	AND reference_date BETWEEN %s AND %s
			# 	AND activity_type = %s
			# 	AND activity = %s
			# 	AND cost_center = %s
			# 	AND closed = 0
			# """, (
			# 	college,
			# 	from_date,
			# 	to_date,
			# 	i.activity_type,
			# 	i.activities,
			# 	cost_center
			# ))[0][0])

			available = flt(current) - consumed

			i["initial"] = flt(initial_approved_budget)
			i["reappropiation_received"] = reappropiation_received
			i["reappropiation_sent"] = reappropiation_sent
			i["supplementary_received"] = supplementary_received
			i["withdrawal_amount"] = withdrawal_amount
			i["current"] = current
			i["budget_type"] = budget_type
			i["cost_center"] = cost_center
			# i["committed"] = committed
			i["consumed"] = consumed
			i["available"] = available
	return data

@frappe.whitelist()
def get_activity_list(activity_type, college=None):
    if not activity_type:
        return []

    if activity_type == "Planning Activities":
        return frappe.db.get_all(
            "Planning Activities",
            fields=["name"],
            order_by="name"
        )

    elif activity_type == "Additional Activities":
        return frappe.db.get_all(
            "Additional Activities",
            filters={
                "college": college
            },
            fields=["name"],
            order_by="name"
        )

    return []