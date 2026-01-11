# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentCreditRecord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.student_credit_details.student_credit_details import StudentCreditDetails
		from frappe.types import DF

		academic_term: DF.Link
		amended_from: DF.Link | None
		company: DF.Link
		credit_type: DF.Link
		posting_date: DF.Date
		student_details: DF.Table[StudentCreditDetails]
	# end: auto-generated types
	@frappe.whitelist()
	def has_credit_clearance(self) -> dict[str, bool]:
		cc = frappe.qb.DocType("Credit Clearance Record")

		student_rec = (
			frappe.qb.from_(cc)
			.select(cc.name)
			.where(
				(cc.docstatus < 2)
				& (cc.student_record_ref == self.name)
			)
		).run(as_dict=True)

		return {
			"has_credit_clearance": bool(student_rec)
		}
