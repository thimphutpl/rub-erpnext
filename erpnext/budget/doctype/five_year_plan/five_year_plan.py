# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FiveYearPlan(Document):
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
		rub_strategic_plan: DF.Link
		to_year: DF.Link
	# end: auto-generated types
	pass

# @frappe.whitelist()
# def fetch_budgetplan():
# 	planning = frappe.db.sql('''
#         SELECT    o.serial_number as output_sino,  o.output,    
# 		pp.serial_number as project_sino, pp.project, pa.serial_number as activity_sino,    
# 		pa.activities FROM `tabOutput` o INNER JOIN `tabPlanning Project` pp      
# 		ON o.name = pp.output INNER JOIN
# 		`tabPlanning Activities` pa     
# 		ON pa.project = pp.name ;
#     ''',  as_dict=True)

# 	planning_update = {}

# 	for i in planning:
# 		output_si_no = 0
# 		if i['output_sino'] == output_si_no:
# 			i['output_sino'] = ''
# 			i['output'] = ''
# 		else:
# 			output_si_no = i['output_si_no']
# 		planning_update.append(i)
		
		

# 	frappe.throw(str(planning))

# 	return planning

@frappe.whitelist()
def fetch_budgetplan():
	planning = frappe.db.sql('''
		SELECT  po.serial_number as output_si_no, 
		po.output, pp.serial_number as project_si_no, 
		pp.project, pa.activities, pa.name as activity_link FROM `tabPlanning Output` po 
		INNER JOIN `tabPlanning Project` pp ON po.name = pp.output 
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

    parent_fyp = frappe.get_doc("Five Year Plan", fyp_name)
    created = []

    for college in colleges:
        # prevent duplicate FYP per college
        if frappe.db.exists("Five Year Plan", {
            "colleges": college["name"],
            "parent_fyp": parent_fyp.name
        }):
            continue

        fyp_copy = frappe.new_doc("Five Year Plan")

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

