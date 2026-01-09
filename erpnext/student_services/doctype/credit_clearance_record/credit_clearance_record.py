# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	ceil,
	cint,
	cstr,
	date_diff,
	floor,
	flt,
	formatdate,
	get_first_day,
	get_last_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
	nowdate,
	now_datetime
)


class CreditClearanceRecord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		credit_type: DF.Link
		posting_date: DF.Date
		student_details: DF.Table[Document]
		student_record_ref: DF.Link | None
	# end: auto-generated types
	def on_submit(self):
		for child in self.student_details:
			if child.status=='Unpaid':
				frappe.throw("All the student status should paid")
		



	
@frappe.whitelist()
def get_credit_clearance(dt, dn):
	doc = frappe.get_doc(dt, dn)
	
	# self.student_details = []

	cc = frappe.new_doc("Credit Clearance Record")
	cc.posting_date = frappe.utils.nowdate()
	cc.college = doc.company
	cc.credit_type = doc.credit_type
	cc.student_record_ref=doc.name
	

	for d in doc.get("student_details"):
		item = d.as_dict()
		
		cc.append("student_details", {
			"student_code": item["student_code"],
			"full_name": item["full_name"],
			"programme": item["programme"],
			"semester": item["semester"],
			"year": item["year"],
			"amount":item["amount"]
		})
	
	return cc.as_dict()

		