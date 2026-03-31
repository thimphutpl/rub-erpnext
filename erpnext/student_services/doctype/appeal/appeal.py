# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Appeal(Document):
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
		disciplinary_action_link: DF.Link | None
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
	pass
