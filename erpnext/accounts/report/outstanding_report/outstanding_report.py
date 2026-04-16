# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": _("ID"),
			"fieldname": "name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("College"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",	
			"width": 140,
		},	
		
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",	
			"width": 140,
		},	
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"width": 140,
		},
		
	]


def get_data(filters):
	conditions = "WHERE pi.outstanding_amount > 0 AND pi.status = 'Unpaid'"

	if filters.get("supplier"):
		conditions += " AND pi.supplier = %(supplier)s"

	if filters.get("company"):
		conditions += " AND pi.company = %(company)s"

	if filters.get("from_date"):
		conditions += " AND pi.posting_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " AND pi.posting_date <= %(to_date)s"
		

	data = frappe.db.sql(
		f"""
		SELECT
			pi.name,
			pi.outstanding_amount,
			pi.supplier,
			pi.company 
		FROM `tabPurchase Invoice` pi
		{conditions}
		""",
		filters,
		as_dict=True,
	)

	return data
