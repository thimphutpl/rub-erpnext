# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FiveYearPlanProposal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.fyp_detail.fyp_detail import FYPDetail
		from frappe.types import DF

		amended_from: DF.Link | None
		colleges: DF.Link
		from_year: DF.Link
		fyp_copies: DF.Check
		fyp_details: DF.Table[FYPDetail]
		remarks: DF.SmallText | None
		rub_strategic_plan: DF.Link
		to_year: DF.Link
		total_proposed_budget: DF.Currency
	# end: auto-generated types
	pass

	def validate(self):
		self.check_college()
		self.calculate_proposed_amount()

	def check_college(self):
		proposal = frappe.db.sql('''
			SELECT name FROM `tabFive Year Plan Proposal` 
			WHERE colleges = %s and from_year = %s and to_year = %s and docstatus = 1
		''',(self.colleges, self.from_year, self.to_year), as_dict=True)
		if proposal:
			frappe.throw("Five Year Plan Proposal exist for college: {0} from year {1} to {2}".format(self.colleges, self.from_year, self.to_year))

	def calculate_proposed_amount(self):
		self.total_proposed_budget = 0
		for item in self.get("fyp_details"):
			self.total_proposed_budget += flt(item.proposed_budget)

@frappe.whitelist()
def fetch_budgetplan():
	planning = frappe.db.sql('''
		SELECT po.serial_number as output_si_no, 
		po.output, pp.serial_number as project_si_no, 
		pp.project, pa.activities, pa.name as activity_link FROM `tabPlanning Output` po 
		INNER JOIN `tabPlanning Project` pp ON po.name = pp.planning_output 
		INNER JOIN `tabPlanning Activities` pa ON pa.project = pp.name 
		ORDER BY po.serial_number, pp.serial_number;
	''', as_dict=True)

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
def create_fyp_for_subsidiaries(fyp_name):
    colleges = frappe.db.sql("""
        SELECT name
        FROM `tabCompany`
        WHERE IFNULL(is_overseeing_company, 0) != 1
    """, as_dict=True)

    parent_fyp = frappe.get_doc("Five Year Plan Proposal", fyp_name)
    created = []

    for college in colleges:
        # prevent duplicate FYP per college
        if frappe.db.exists("Five Year Plan Proposal", {
            "colleges": college["name"],
            "parent_fyp": parent_fyp.name
        }):
            continue

        fyp_copy = frappe.new_doc("Five Year Plan Proposal")

        # copy all fields safely
        fyp_copy.update({
            key: value
            for key, value in parent_fyp.as_dict().items()
            if key not in (
                "name", "doctype", "owner", "creation", "modified",
                "modified_by", "docstatus"
            )
        })

        fyp_copy.colleges = college["name"]
        fyp_copy.parent_fyp = parent_fyp.name  # recommended tracking

        fyp_copy.insert(ignore_permissions=True)
        created.append(fyp_copy.name)

    # mark parent only if copies created
    if created:
        parent_fyp.db_set("fyp_copies", 1)

    return {
        "status": "success",
        "created_fyp_count": len(created),
        "fyp_records": created
    }

