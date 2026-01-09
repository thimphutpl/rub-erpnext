# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class HostelCheckInForm(Document):
	def validate(self):
		pass
	def on_submit(self):
		pass	

@frappe.whitelist()
def get_students_from_room(hostel_room):
	if not hostel_room:
		frappe.throw("Please select a Hostel Room first")

	students = frappe.get_all(
		"Student List Item",
		filters={"parent": hostel_room, "parenttype": "Hostel Room"},
		fields=["student_code", "year",]
	)

	return students

@frappe.whitelist()
def get_assets_from_room(hostel_room):
	if not hostel_room:
		frappe.throw("Please select a Hostel Room first")

	assets = frappe.get_all(
		"Hostel Asset Item",
		filters={"parent": hostel_room, "parenttype": "Hostel Room"},
		fields=["asset_code", "asset_name"]
	)

	return assets

@frappe.whitelist()
def make_checkout_form(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Hostel Check-In Form", source_name, {
			"Hostel Check-In Form": {
				"doctype": "Hostel Check-Out Form",
				"field_map": {
					"name": "hostel_check_out_form",
					"posting_date": "posting_date",
					"company": "college",
					"hostel_room": "hostel_room",
					"hostel_type": "hostel_type",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Check-In Students Items": {
				"doctype": "Check-Out Student Details",
				"postprocess": transfer_currency,
			},
			"Check-In Asset Items": {
				"doctype": "Check-Out Asset Items",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc	