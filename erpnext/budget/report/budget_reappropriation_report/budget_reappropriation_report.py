# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
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
		select 
			br.name,
			br.from_cost_center,
			br.to_cost_center,
			br.appropiation_amount,

			br.from_activity_type,
			br.from_activity,
			CASE
				WHEN br.from_activity_type = 'Planning Activities'
					THEN pa_from.activities
				WHEN br.from_activity_type = 'Additional Activities'
					THEN aa_from.activities
			END AS from_activity_name,

			br.to_activity_type,
			br.to_activity,
			CASE
				WHEN br.to_activity_type = 'Planning Activities'
					THEN pa_to.activities
				WHEN br.to_activity_type = 'Additional Activities'
					THEN aa_to.activities
			END AS to_activity_name,

			br.from_budget_type,
			br.to_budget_type,
			br.remarks,
			br.appropriation_date
		from 
			`tabBudget Reappropiations` br
		LEFT JOIN `tabPlanning Activities` pa_from
			ON pa_from.name = br.from_activity

		LEFT JOIN `tabAdditional Activities` aa_from
			ON aa_from.name = br.from_activity

		LEFT JOIN `tabPlanning Activities` pa_to
			ON pa_to.name = br.to_activity

		LEFT JOIN `tabAdditional Activities` aa_to
			ON aa_to.name = br.to_activity
		where br.docstatus = 1 
		and br.appropriation_date between '{0}' and '{1}' and br.college = '{2}'
		""".format(filters.from_date, filters.to_date, filters.college)

	if filters.to_cost_center:
		query+=" and br.to_cost_center = \'" + filters.to_cost_center  + "\'"

	if filters.from_cost_center:
		query+=" and br.from_cost_center = \'" + filters.from_cost_center  + "\'"

	if filters.from_activity_type:
		query+=" and br.from_activity_type = \'" + filters.from_activity_type  + "\'"
		
	if filters.from_activity:
		query+=" and br.from_activity = \'" + filters.from_activity  + "\'"

	if filters.to_activity_type:
		query+=" and br.to_activity_type = \'" + filters.to_activity_type  + "\'"

	if filters.to_activity:
		query+=" and br.to_activity = \'" + filters.to_activity  + "\'"

	app_data = frappe.db.sql(query, as_dict=True)

	data = []

	if app_data:
		for a in app_data:
			row = {
				"to_cost_center": a.to_cost_center,
				"to_activity_type": a.to_activity_type,
				"to_activity": a.to_activity,
				"to_budget_type": a.to_budget_type,
				"to_activity_name": a.to_activity_name,
				"from_cost_center": a.from_cost_center,
				"from_activity_type": a.from_activity_type,
				"from_activity": a.from_activity,
				"from_budget_type": a.from_budget_type,
				"from_activity_name": a.from_activity_name,
				"amount": a.appropiation_amount,
				"date": a.appropriation_date,
				"name": a.name,
			}
			data.append(row)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "name",
			"label": _("Transaction Name"),
			"fieldtype": "Link",
			"options": "Budget Reappropiations",
			"with": 120
		},
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "from_cost_center",
			"label": _("From Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200
		},
		{
			"fieldname": "from_activity_type",
			"label": _("From Activity Type"),
			"fieldtype": "Select",
			"options": ["Planning Activities", "Additional Activities"],
			"width": 200
		},
		{
			"fieldname": "from_activity",
			"label": _("From Activity"),
			"fieldtype": "Dynamic Link",
			"options": "from_activity_type",
			"width": 200
		},
		{
			"fieldname": "from_activity_name",
			"label": _("From Activity Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "from_budget_type",
			"label": _("From Budget Type"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "to_cost_center",
			"label": _("To Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200
		},
		{
			"fieldname": "to_activity_type",
			"label": _("To Activity Type"),
			"fieldtype": "Select",
			"options": ["Planning Activities", "Additional Activities"],
			"width": 200
		},
		{
			"fieldname": "to_activity",
			"label": _("To Activity"),
			"fieldtype": "Dynamic Link",
			"options": "to_activity_type",
			"width": 200
		},
		{
			"fieldname": "to_activity_name",
			"label": _("To Activity Name"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "to_budget_type",
			"label": _("To Budget Type"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
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
