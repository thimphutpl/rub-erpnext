# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AnnualPerformanceAgreement(Document):
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
		year: DF.Link
	# end: auto-generated types
	pass

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


