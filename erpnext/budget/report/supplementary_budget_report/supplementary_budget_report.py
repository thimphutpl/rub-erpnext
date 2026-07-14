# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data

def validate_filters(filters):
	if not filters.from_year:
		frappe.throw(_("From Year {0} is required").format(filters.from_year))

	if not filters.to_year:
		frappe.throw(_("To Year {0} is required").format(filters.to_year))

	from_date = f"{filters.from_year}-07-01"
	to_date = f"{filters.to_year}-06-30"
	
	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if not filters.from_date:
		filters.from_date = from_date

	if not to_date:
		filters.to_date = to_date

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

	if (filters.from_date < getdate(from_date)) or (filters.from_date > getdate(to_date)):
		frappe.msgprint(_("From Date should be within the From Year. Assuming From Date = {0}")\
			.format(formatdate(from_date)))

		filters.from_date = from_date

	if (filters.to_date < getdate(from_date)) or (filters.to_date > getdate(to_date)):
		frappe.msgprint(_("To Date should be within the To Year. Assuming To Date = {0}")\
			.format(formatdate(to_date)))
		filters.to_date = to_date

def get_data(filters):
	query = """
		select sb.name, sb.cost_center, sb.budget_activity_type, sb.budget_activity, sb.budget_type, sb.supplement_amount,
		sb.remarks, sb.posting_date as date,
		CASE
			WHEN sb.budget_activity_type = 'Planning Activities'
				THEN pa.activities
			WHEN sb.budget_activity_type = 'Additional Activities'
				THEN aa.activities
		END AS budget_activity_name
		from `tabSupplementary Budgets` sb
		LEFT JOIN `tabPlanning Activities` pa
			ON pa.name = sb.budget_activity
		LEFT JOIN `tabAdditional Activities` aa
			ON aa.name = sb.budget_activity
		where sb.posting_date between '{from_date}' and '{to_date}' AND sb.college = '{college}'
		""".format(from_date=filters.from_date, to_date=filters.to_date, college=filters.college)

	# frappe.throw(str(query))
	if filters.cost_center:
		query+=" and sb.cost_center = \'" + filters.cost_center  + "\'"
	if filters.activity_type:
		query+=" and sb.budget_activity_type = \'" + filters.activity_type  + "\'"
	if filters.activity:
		query+=" and sb.budget_activity = \'" + filters.activity  + "\'"

	sup_data = frappe.db.sql(query, as_dict=True)

	data = []

	if sup_data:
		for a in sup_data:
			row = {
				"cost_center": a.cost_center,
				"supplement_amount": a.supplement_amount,
				"date": a.date,
               	"budget_type": a.budget_type,
               	"budget_activity_type": a.budget_activity_type,
               	"budget_activity": a.budget_activity,
               	"budget_activity_name": a.budget_activity_name,
                "name": a.name,
			}
			data.append(row)
	
	return data

def get_columns(filters):
	return [
		{
			"fieldname": "name",
			"label": _("Transaction Name"),
			"fieldtype": "Link",
			"options": "Supplementary Budgets",
			"with": 120
		},
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
		   "fieldname": "budget_activity_type",
			"label": _("Activity Type"),
			"fieldtype": "Select",
			"options": ["Planning Activities, Additional Activities"],
			"width": 120
		},
		{
		   "fieldname": "budget_activity",
			"label": _("Activity"),
			"fieldtype": "Dynamic Link",
			"options": "budget_activity_type",
			"width": 120
		},
		{
		   "fieldname": "budget_activity_name",
			"label": _("Activity Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
		   "fieldname": "budget_type",
			"label": _("Budget Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "cost_center",
			"label": _("To Cost Center"),
			"fieldtype": "Link",
			"options":"Cost Center",
			"width": 200
		},
		{
			"fieldname": "supplement_amount",
			"label": _("Supplement Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 200
		}
	]
