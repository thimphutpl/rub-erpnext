# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if filters.fiscal_year and filters.to_fiscal_year and filters.report_type:
		data = get_data(filters)
		columns = get_columns(filters, data)
		# frappe.throw(str(columns))
		return columns, data
	
def get_data(filters=None):
	data = []
	if filters.to_fiscal_year < filters.fiscal_year:
		frappe.throw(_("To Fiscal Year cannot be earlier than From Fiscal Year"))
	if filters.report_type == "Overall Compact Achievement":
		data.append({"kpi": "Financial"})
		data.append({"kpi": "Non Financial",
				"weight": "",})
		data.append({"kpi": "2.1 Customer Perspective"})
		data.append({"kpi": "2.2 Innovation and Talent"})
		data.append({"kpi": "2.3 Risk and Control"})
		data.append({"kpi": "Business As Usual"})
		if not filters.department:
			for year in range(int(filters.fiscal_year), int(filters.to_fiscal_year) + 1):
				df = frappe.db.sql("""
					select sum(cci.weight)/count(cci.name) as weight, sum(cci.weight_awarded)/count(cci.name) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
					where cci.parent = cc.name
					and cc.type = "Company"
					and cc.fiscal_year = '{}'
					and cc.docstatus = 1
					and cci.parentfield like 'financial%'
				""".format(year),as_dict = 1)
				data[0]["weight "+str(year)] = df[0].weight if df else 0
				data[0]["weight_achieved "+str(year)] = df[0].weight_achieved if df else 0

				idx = 2
				for nf in frappe.db.sql("""
					select sum(cci.weight) as weight, sum(cci.weight_awarded) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
					where cci.parent = cc.name
					and cc.type = "Company"
					and cc.fiscal_year = '{}'
					and cc.docstatus = 1
					and cci.parentfield like 'non_financial%'
					group by cci.parentfield
				""".format(year),as_dict = 1):
					data[idx]["weight "+str(year)] = nf.weight
					data[idx]["weight_achieved "+str(year)] = nf.weight_achieved
					idx += 1
				for bau in frappe.db.sql("""
					select sum(cci.weight) as weight, sum(cci.weight_awarded) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
					where cci.parent = cc.name
					and cc.type = "Company"
					and cc.fiscal_year = '{}'
					and cc.docstatus = 1
					and cci.parentfield like 'business_as_usual%'
				""".format(year),as_dict = 1):
					data[5]["weight "+str(year)] = bau.weight
					data[5]["weight_achieved "+str(year)] = bau.weight_achieved
		else:
			for year in range(int(filters.fiscal_year), int(filters.to_fiscal_year) + 1):
				df = frappe.db.sql("""
					select sum(cci.weight)/count(cci.name) as weight, sum(cci.weight_awarded)/count(cci.name) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
					where cci.parent = cc.name
					and cc.department = '{}'
					and cc.fiscal_year = '{}'
					and cc.docstatus = 1
					and cci.parentfield like 'financial%'
				""".format(filters.department, year),as_dict = 1)
				data[0]["weight "+str(year)] = df[0].weight if df else 0
				data[0]["weight_achieved "+str(year)] = df[0].weight_achieved if df else 0

				idx = 2
				for nf in frappe.db.sql("""
					select sum(cci.weight) as weight, sum(cci.weight_awarded) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
					where cci.parent = cc.name
					and cc.department = "{}"
					and cc.fiscal_year = '{}'
					and cc.docstatus = 1
					and cci.parentfield like 'non_financial%'
					group by cci.parentfield
				""".format(filters.department, year),as_dict = 1):
					data[idx]["weight "+str(year)] = nf.weight
					data[idx]["weight_achieved "+str(year)] = nf.weight_achieved
					idx += 1
				for bau in frappe.db.sql("""
					select sum(cci.weight) as weight, sum(cci.weight_awarded) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
					where cci.parent = cc.name
					and cc.department = "{}"
					and cc.fiscal_year = '{}'
					and cc.docstatus = 1
					and cci.parentfield like 'business_as_usual%'
				""".format(filters.department, year),as_dict = 1):
					data[5]["weight "+str(year)] = bau.weight
					data[5]["weight_achieved "+str(year)] = bau.weight_achieved
	else:
		if not filters.department:
			idx = 0
			for kpi in frappe.db.sql("""
				select distinct cci.key_performance_indicator as kpi from `tabCompany Compact Item` cci, `tabCompany Compact` cc
				where cci.parent = cc.name and cc.type = "Company"
				and cc.docstatus = 1
			""", as_dict = 1):
				data.append({"kpi": kpi.kpi})
				for year in range(int(filters.fiscal_year), int(filters.to_fiscal_year) + 1):
					df = frappe.db.sql("""
						select sum(cci.target)/count(cci.name) as weight, sum(cci.achievement)/count(cci.name) as weight_achieved from `tabCompany Compact Item` cci, `tabCompany Compact` cc
						where cci.parent = cc.name
						and cc.type = "Company"
						and cc.fiscal_year = '{}'
						and cc.docstatus = 1
						and cci.key_performance_indicator = '{}'
					""".format(year, kpi.kpi),as_dict = 1)
					data[idx]["target "+str(year)] = df[0].weight if df else 0
					data[idx]["achievement "+str(year)] = df[0].weight_achieved if df else 0
				idx += 1
		else:
			idx = 0
			for kpi in frappe.db.sql("""
				select distinct cci.key_performance_indicator as kpi from `tabCompany Compact Item` cci, `tabCompany Compact` cc
				where cci.parent = cc.name and cc.department = '{}'
				and cc.docstatus = 1
			""".format(filters.department), as_dict = 1):
				data.append({"kpi": kpi.kpi})
				for year in range(int(filters.fiscal_year), int(filters.to_fiscal_year) + 1):
					df = frappe.db.sql("""
						select sum(cci.target)/count(cci.name) as target, sum(cci.achievement)/count(cci.name) as achievement from `tabCompany Compact Item` cci, `tabCompany Compact` cc
						where cci.parent = cc.name
						and cc.department = '{}'
						and cc.fiscal_year = '{}'
						and cc.docstatus = 1
						and cci.key_performance_indicator = '{}'
					""".format(filters.department, year, kpi.kpi),as_dict = 1)
					data[idx]["target "+str(year)] = df[0].target if df else 0
					data[idx]["achievement "+str(year)] = df[0].achievement if df else 0
				idx += 1
	return data

def get_columns(filters=None, data=None):
	columns = []
	if filters.report_type == "Overall Compact Achievement":
		columns = [
		{
            "fieldname": "kpi",
            "label": _("Key Performance Indicator"),
            "fieldtype": "Data",
            "width": 120
        }
		]
		for year in range(int(filters.fiscal_year), int(filters.to_fiscal_year) + 1):
			columns.append(
			{
				"fieldname": "weight "+str(year),
				"label": _("Weight "+str(year)),
				"fieldtype": "Float",
				"width": 160
			})
			columns.append(
			{
				"fieldname": "weight_achieved "+str(year),
				"label": _("Weight Achieved "+str(year)),
				"fieldtype": "Float",
				"width": 160
			})
	else:
		columns = [
		{
            "fieldname": "kpi",
            "label": _("Key Performance Indicator"),
            "fieldtype": "Data",
            "width": 120
        }]
		for year in range(int(filters.fiscal_year), int(filters.to_fiscal_year) + 1):
			columns.append(
			{
				"fieldname": "target "+str(year),
				"label": _("Target "+str(year)),
				"fieldtype": "Float",
				"width": 160
			})
			columns.append(
			{
				"fieldname": "achievement "+str(year),
				"label": _("Achievement "+str(year)),
				"fieldtype": "Float",
				"width": 160
			})
	
	return columns
		
		