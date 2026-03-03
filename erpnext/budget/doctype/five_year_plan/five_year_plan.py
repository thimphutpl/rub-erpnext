# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class FiveYearPlan(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.five_year_plan_items.five_year_plan_items import FiveYearPlanItems
		from frappe.types import DF

		amended_from: DF.Link | None
		from_year: DF.Link
		fyp_copies: DF.Check
		items: DF.Table[FiveYearPlanItems]
		remarks: DF.SmallText | None
		rub_strategic_plan: DF.Link | None
		to_year: DF.Link
		total_approved_budget: DF.Currency
	# end: auto-generated types
	pass

	def validate(self):
		self.check_fyp_year()
		self.validate_approved_budget()

	def check_fyp_year(self):
		fyp = frappe.db.sql('''
			SELECT name FROM `tabFive Year Plan` 
			WHERE from_year = %s and to_year = %s and docstatus = 1
		''',(self.from_year, self.to_year), as_dict=True)
		if fyp:
			frappe.throw("Five Year Plan from year {0} to {1}".format(self.from_year, self.to_year))

	def validate_approved_budget(self):
		for row in self.items:
			if not row.approved_budget or row.approved_budget <= 0:
				frappe.throw("Approved budget not set or is zero for row: {0}".format(row.idx))

@frappe.whitelist()
def get_fyp_proposal(rub_strategic_plan, from_year, to_year):
	if not from_year or not to_year or not rub_strategic_plan:
		frappe.throw(_("From Year, To Year and RUB Strategic Plan are required"))

	fyp_proposals = frappe.db.sql("""SELECT 
			FROM `tabFive Year Plan Proposal` t1
			JOIN `tabFYP Detail` t2 ON t1.name = t2.parent
			WHERE from_year = %s and to_year = %s and 
			rub_strategic_plan = %s""", (from_year, to_year, rub_strategic_plan), as_dict=True)

	return fyp_proposals


@frappe.whitelist()
def fetch_budgetplan(from_year, to_year):
	planning = frappe.db.sql('''
		SELECT  
			po.serial_number as output_si_no, 
			SUM(fypi.proposed_budget) as amount,
			po.output, 
			pp.serial_number as project_si_no, 
			pp.project, 
			pa.activities, 
			pa.name as activity_link
		FROM `tabPlanning Output` po 
		INNER JOIN `tabPlanning Project` pp ON po.name = pp.planning_output 
		INNER JOIN `tabPlanning Activities` pa ON pa.project = pp.name 
		INNER JOIN `tabFYP Detail` fypi ON fypi.activity_link = pa.name
		INNER JOIN `tabFive Year Plan Proposal` fypp ON fypi.parent = fypp.name
		WHERE fypp.from_year = %s and fypp.to_year = %s and fypp.docstatus = 1

		GROUP BY 
			po.serial_number,
			po.output,
			pp.serial_number,
			pp.project,
			pa.activities,
			pa.name

		ORDER BY 
			po.serial_number, 
			pp.serial_number;

	''',(from_year, to_year), as_dict=True)
	# frappe.throw(frappe.as_json(str(planning)))
	# Should be list
	planning_update = []

	# Track last seen serial numbers
	last_output_no = None
	# last_project_no = None
	if planning:
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
	else:
		frappe.throw("No FYP Proposal found for the year {0} to {1}".format(from_year, to_year))

	# frappe.throw(str(planning_update))

	return planning_update


@frappe.whitelist()
def create_awp_for_subsidiaries(fyp_name):
    colleges = frappe.db.sql("""
        SELECT name
        FROM `tabCompany`
        WHERE IFNULL(is_group, 0) != 1
    """, as_dict=True)

    fyp = frappe.get_doc("Five Year Plan", fyp_name)
    created = []

    for college in colleges:
        # prevent duplicate FYP per college
        if frappe.db.exists("Annual Work Plan", {
            "colleges": college["name"],
            "fyp": fyp.name
            "fiscal_year": now_datetime().year
			# "apa_details": fyp.items
        }):
            continue

        awp = frappe.new_doc("Annual Work Plan")

        # copy all fields safely
        awp.update({
            key: value
            for key, value in fyp.as_dict().items()
            if key not in (
                "name", "doctype", "owner", "creation", "modified",
                "modified_by", "docstatus", "amended_from"
            )
        })

        awp.colleges = college["name"]
        awp.year = now_datetime().year
        awp.fyp = fyp.name  # recommended tracking
        awp.workflow_state = "Draft"

        awp.insert(ignore_permissions=True)
        created.append(awp.name)

    # mark parent only if copies created
    # if created:
    #     fyp.db_set("fyp_copies", 1)

    return {
        "status": "success",
        "created_fyp_count": len(created),
        "fyp_records": created
    }

