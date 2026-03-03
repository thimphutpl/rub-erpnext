# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from frappe.model.mapper import get_mapped_doc

class AnnualWorkPlan(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.apa_detail.apa_detail import APADetail
		from frappe.types import DF

		amended_from: DF.Link | None
		apa_copies: DF.Check
		apa_details: DF.Table[APADetail]
		colleges: DF.Link
		fyp: DF.Link
		remarks: DF.SmallText | None
		total_approved_budget: DF.Currency
		total_proposed_budget: DF.Currency
		year: DF.Link
	# end: auto-generated types
	pass

	def validate(self):
		self.validate_college()
		self.validate_budget()
		self.validate_approved_budget()
		self.calculate_proposed_budget()
		self.calculate_approved_budget()
	
	def validate_approved_budget(self):
		for row in self.items:
			if not row.approved_budget or row.approved_budget <= 0:
				frappe.throw("Approved budget not set or is zero for row: {0}".format(row.idx))

	def calculate_proposed_budget(self):
		total_proposed_budget = 0
		for row in self.items:
			total_proposed_budget += flt(row.proposed_budget)
		self.total_proposed_budget = total_proposed_budget

	def calculate_approved_budget(self):
		total_approved_budget = 0
		for row in self.items:
			total_approved_budget += flt(row.approved_budget)
		self.total_approved_budget = total_approved_budget

	def validate_college(self):
		proposal_list = frappe.db.sql(""" 
			SELECT colleges
			FROM `tabFive Year Plan Proposal`
			WHERE colleges = %s 
			AND %s BETWEEN from_year AND to_year
			AND docstatus = 1
		""", (self.colleges, self.year), as_dict=True)
		if len(proposal_list) <= 0:
			frappe.throw(_("No proposed budget found for college: {0} in the five year plan proposal".format(self.colleges)))

	def validate_budget(self):
		# Get Approved Budget from Five Year Plan
		approved_budget_list = frappe.db.sql("""
			SELECT fypi.approved_budget, fypi.activity_link
			FROM `tabFive Year Plan` fyp
			INNER JOIN `tabFive Year Plan Items` fypi 
				ON fyp.name = fypi.parent
			WHERE fyp.name = %s 
			AND %s BETWEEN fyp.from_year AND fyp.to_year
			AND fyp.docstatus = 1
			ORDER BY fypi.idx
		""", (self.fyp, self.year), as_dict=True)

		if not approved_budget_list:
			frappe.throw(
				_("No budget found for year {0} in Five Year Plan")
				.format(self.year)
			)

		# Get Already Approved Budget from Annual Work Plan
		awp_list = frappe.db.sql("""
			SELECT awpi.approved_budget, awpi.activity_link
			FROM `tabAnnual Work Plan` awp
			INNER JOIN `tabAPA Detail` awpi 
				ON awp.name = awpi.parent
			WHERE awp.year = %s and awp.docstatus = 1
			ORDER BY awpi.idx
		""", (self.year,), as_dict=True)

		approved_budget_map = {}
		for d in approved_budget_list:
			approved_budget_map[d.activity_link] = (
				approved_budget_map.get(d.activity_link, 0)
				+ flt(d.approved_budget)
			)
		# Sum AWP budgets properly (important!)
		awp_map = {}

		for d in awp_list:
			awp_map[d.activity_link] = (
				awp_map.get(d.activity_link, 0)
				+ flt(d.approved_budget)
			)

		# Validate current document rows
		for row in self.apa_details:

			available_budget = approved_budget_map.get(row.activity_link, 0)
			already_approved_budget = awp_map.get(row.activity_link, 0)

			if not available_budget:
				frappe.throw(
					_("No approved budget found for Activity: {0}")
					.format(row.activity_link)
				)

			total_budget = (
				flt(row.approved_budget)
				+ already_approved_budget
			)

			if total_budget > available_budget:
				frappe.throw(
					_("Approved budget for Activity {0} exceeds available budget ({1})")
					.format(row.activity_link, available_budget)
				)

@frappe.whitelist()
def fetch_budgetplan(fyp):
	planning = frappe.db.sql('''
		select output, project, activities, activity_link,
		output_no, activities_no,project_no 
		from `tabFYP Detail` 
		where parent=%s order by idx 
	''',(fyp), as_dict=True)

	# Should be list
	planning_update = []

	# Track last seen serial numbers
	last_output_no = None
	# last_project_no = None

	for row in planning:
		# Hide repeated output
		if row["output_si_no"] == last_output_no:
			# row["output_si_no"] = ""
			row["output"] = ""
		else:
			last_output_no = row["output_si_no"]

		# Hide repeated project
		# if row["project_si_no"] == last_project_no:
		# 	# row["project_si_no"] = ""
		# 	row["project"] = ""
		# else:
		# 	last_project_no = row["project_si_no"]

		planning_update.append(row)

	# frappe.throw(str(planning_update))

	return planning_update

@frappe.whitelist()
def create_apa_for_subsidiaries(apa_name):
	colleges = frappe.db.sql("""
		SELECT name
		FROM `tabCompany`
		WHERE IFNULL(is_overseeing_company, 0) != 1
	""", as_dict=True)

	parent_apa = frappe.get_doc("Annual Performance Agreement", apa_name)
	created = []

	for college in colleges:
		# prevent duplicate FYP per college
		if frappe.db.exists("Annual Performance Agreement", {
			"colleges": college["name"],
			"parent_fyp": parent_apa.name
		}):
			continue

		fyp_copy = frappe.new_doc("Annual Performance Agreement")

		# copy all fields safely
		fyp_copy.update({
			key: value
			for key, value in parent_apa.as_dict().items()
			if key not in (
				"name", "doctype", "owner", "creation", "modified",
				"modified_by", "docstatus"
			)
		})

		fyp_copy.colleges = college["name"]
		fyp_copy.parent_apa = parent_apa.name  # recommended tracking

		fyp_copy.insert(ignore_permissions=True)
		created.append(fyp_copy.name)

	# mark parent only if copies created
	if created:
		parent_apa.db_set("apa_copies", 1)

	return {
		"status": "success",
		"created_apa_count": len(created),
		"apa_records": created
	}

@frappe.whitelist()
def make_approved_budget(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.college = source.colleges
        target.fiscal_year = source.year

    doc = get_mapped_doc(
        "Annual Work Plan",   # Source DocType
        source_name,
        {
            "Annual Work Plan": {
                "doctype": "Approved Budget"
            },
            "APA Detail": {
                "doctype": "Approved Budget Item",
                # "field_map": {
                #     "activity_link": "activity_link",
                #     "approved_budget": "approved_budget"
                # }
            }
        },
        target_doc,
        set_missing_values
    )

    return doc