# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Club(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.club_action_plan_details.club_action_plan_details import ClubActionPlanDetails
		from erpnext.student_services.doctype.club_management_details.club_management_details import ClubManagementDetails
		from frappe.types import DF

		abbr: DF.Data | None
		club_activities: DF.Table[ClubActionPlanDetails]
		club_capacity: DF.Int
		club_management: DF.Table[ClubManagementDetails]
		club_name: DF.Data
		company: DF.Link
		minimum_year_required_for_certification: DF.Data | None
	# end: auto-generated types


	def validate(self):
		for row in self.club_management:
			# Check if this employee_student already exists in THIS SAME parent
			exists = frappe.db.exists("Club Management Details", {
				"employee_student": row.employee_student,
				"parent": self.name,
				"name": ["!=", row.name]  # Exclude current row when editing
			})
			
			if exists:
				frappe.throw(f"Employee {row.employee_student} already exists in this club")

		
@frappe.whitelist()
def get_full_name(std_emp_id,type,doc):
	full_name=""
	exists = frappe.db.exists(
		"Club Management Details",
		{
			"parent": doc,
			"employee_student":std_emp_id
			
		},
	)
	if exists:
		return {
			"exists":True
		}
		#frappe.throw("There is an active membership for this member")
		
	if type=='Employee':
		doc=frappe.get_doc("Employee",std_emp_id)
		full_name=doc.employee_name
		#frappe.throw(str(full_name))
		return {
				"full_name":full_name,
				"designation":doc.designation, 
				"exists": False
			   }
	elif type=='Student':
		doc=frappe.get_doc("Student",std_emp_id)
		full_name = " ".join([doc.first_name or "", doc.middle_name or "", doc.last_name or ""]).strip()
		programme=doc.programme
		year=doc.year
		semester=doc.semester

		return {
            "full_name": full_name,
            "programme": programme,
            "year": year,
            "semester": semester,
			"exists": False
        }

	#frappe.throw(str(Std_emp_id))
