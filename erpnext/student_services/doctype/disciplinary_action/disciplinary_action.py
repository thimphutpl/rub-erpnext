# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date, datetime,timedelta

from frappe.utils import getdate, today


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
		contact_number: DF.Data | None
		date_of_the_issue: DF.Date
		decision: DF.Link | None
		designation: DF.Data | None
		disciplinary_issue_type: DF.Link
		hostel: DF.Link | None
		issue_reported_by: DF.Link
		issue_severity: DF.Literal["Major Issue", "Minor Issue"]
		location_of_issue_caused: DF.Data
		name_reporter: DF.Data | None
		name_student: DF.Data | None
		posting_date: DF.Date
		problem_date: DF.Date
		problem_time: DF.Time
		program: DF.Data | None
		scholarship: DF.Literal["", "Self", "Government Scholarship"]
		section: DF.Data | None
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
	

	@frappe.whitelist()
	def has_appeal_action(self) -> dict[str, bool]:
		
		da = frappe.qb.DocType("Appeal")

		appeal = (
			frappe.qb.from_(da)
			.select(da.name)
			.where(
				(da.docstatus < 2)
				& (da.disciplinary_action_link == self.name)
			)
		).run(as_dict=True)
		target_date =  getdate(self.posting_date)
		current_date = getdate(today())
		#diff = (current_date - target_date).days
		diff = get_weekday_diff(target_date, current_date)
		#frappe.throw(str(diff))
		appeal_days=frappe.db.get_single_value("Student Service Settings","minimum_days_required_appeal")
		appeal_days = int(appeal_days) if appeal_days else 0
		if diff > appeal_days:
			appeal=True

		return {
			"has_appeal_action": bool(appeal)
		}
def get_weekday_diff(start_date, end_date):
		"""
		Calculate weekdays excluding weekends
		"""
		if start_date > end_date:
			start_date, end_date = end_date, start_date
		
		weekdays = 0
		current = start_date
		
		while current <= end_date:
			# In Python, Monday=0, Sunday=6
			# If you need to exclude Saturday(5) and Sunday(6)
			if current.weekday() not in [5, 6]:  # Monday=0 to Friday=4
				weekdays += 1
			current += timedelta(days=1)
		
		return weekdays
	
@frappe.whitelist()
def get_appeal(dt,dn):
	doc = frappe.get_doc(dt, dn)
	#frappe.throw("hii")

	ap = frappe.new_doc("Appeal")
	ap.posting_date = frappe.utils.nowdate()
	ap.company=doc.company
	ap.student_code=doc.student_code
	ap.name_student=doc.name_student
	ap.program=doc.program
	ap.semester=doc.semester
	ap.student_statement_link=doc.student_statement_link
	ap.disciplinary_action_link=doc.name
	ap.contact_number=doc.contact_number
	ap.decision=doc.decision
	ap.student_statement=doc.student_statement
	ap.disciplinary_issue_type=doc.disciplinary_issue_type


	return ap.as_dict()