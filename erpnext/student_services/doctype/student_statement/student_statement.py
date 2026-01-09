# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document


class StudentStatement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		company: DF.Link
		disciplinary_issue_type: DF.Link
		name_student: DF.Data | None
		posting_date: DF.Date
		program: DF.Data | None
		semester: DF.Data | None
		student_code: DF.Link
		student_statement: DF.LongText | None
		verifier: DF.Data | None
		verifier_designation: DF.Data | None
	# end: auto-generated types
	
	def on_submit(self):
		if self.disciplinary_issue_type=='Minor Issue':
			#frappe.throw("hu")
			parent_doc = frappe.get_doc("Student", self.student_code)
			#frappe.throw(str(parent_doc))
			parent_doc.append("disciplinary_action_details", {
				"disciplinary_issue_type": self.disciplinary_issue_type,
				"reference_doctype":self.doctype,
				"link_student_statements":self.name,
				#"statements":self.student_statement,
				"date": self.posting_date		
			})
			
			parent_doc.save()

			

	@frappe.whitelist()
	def has_disciplinary_action(self) -> dict[str, bool]:
		da = frappe.qb.DocType("Disciplinary Action")

		travel_claim = (
			frappe.qb.from_(da)
			.select(da.name)
			.where(
				(da.docstatus < 2)
				& (da.student_statement_link == self.name)
			)
		).run(as_dict=True)

		return {
			"has_disciplinary_action": bool(travel_claim)
		}


@frappe.whitelist()
def get_disciplinary_action(dt, dn):
	doc = frappe.get_doc(dt, dn)
	

	da = frappe.new_doc("Disciplinary Action")
	da.posting_date = frappe.utils.nowdate()
	da.company=doc.company
	da.student_code=doc.student_code
	da.name_student=doc.name_student
	da.program=doc.program
	da.semester=doc.semester
	da.student_statement_link=doc.name
	da.student_statement=doc.student_statement
	da.disciplinary_issue_type=doc.disciplinary_issue_type


	return da.as_dict()


