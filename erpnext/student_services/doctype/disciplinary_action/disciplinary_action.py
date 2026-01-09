# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DisciplinaryAction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		attachments_investigator: DF.Attach | None
		attachments_student: DF.Attach | None
		attah_cdc: DF.Attach | None
		cdc_remarks: DF.TextEditor | None
		company: DF.Link
		date_of_the_issue: DF.Date
		designation: DF.Data | None
		disciplinary_issue_type: DF.Link
		issue_reported_by: DF.Link
		name_reporter: DF.Data | None
		name_student: DF.Data | None
		posting_date: DF.Data
		program: DF.Data | None
		semester: DF.Data | None
		small_text_xble: DF.SmallText | None
		student_code: DF.Link
		student_statement: DF.LongText | None
		student_statement_link: DF.Link | None
	# end: auto-generated types
	def on_submit(self):
		
			#frappe.throw("hu")
		parent_doc = frappe.get_doc("Student", self.student_code)
		#frappe.throw(str(parent_doc))
		parent_doc.append("disciplinary_action_details", {
			"disciplinary_issue_type": self.disciplinary_issue_type,
			"reference_doctype":self.doctype,
			"link_disciplinary_action":self.name,
			#"statements":self.student_statement,
			"date": self.posting_date		
		})
		
		parent_doc.save()
