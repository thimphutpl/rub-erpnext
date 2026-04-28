# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class HostelRoom(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		capacity: DF.Int
		catering_type: DF.Literal["", "Mess", "Self-catering"]
		college_abbreviation: DF.Data | None
		company: DF.Link
		cost_center: DF.Link | None
		hostel_room_item: DF.Table[Document]
		hostel_room_sub_category: DF.Link | None
		hostel_type: DF.Link
		room_description: DF.Text | None
		room_number: DF.Data
		student_list: DF.Table[Document]
	# end: auto-generated types
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		capacity: DF.Int
		company: DF.Link | None
		hostel_type: DF.Link | None
		room_number: DF.Data | None
		student_list: DF.Table[Document]
		table_jpww: DF.Table[Document]	

	def validate(self):
		self.validate_company_before_hostel_room()

	def validate_company_before_hostel_room(self):
		"""Validate that hostel_room cannot be selected without company"""
		if self.hostel_type and not self.company:
			frappe.throw(_("Please select a College first before selecting Hostel Room"))

		if self.hostel_type and self.company:
			# Get the company from the selected Hostel Room
			room_company = frappe.db.get_value("Hostel Type", self.hostel_type, "company")
			
			if room_company and room_company != self.company:
				frappe.throw(_("Hostel Tyoe {0} belongs to {1}, but you have selected {2}. Please select a Hostel Type from the correct College.").format(
					frappe.bold(self.hostel_type),
					frappe.bold(room_company),
					frappe.bold(self.company)
				))

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user
	
	user_roles = frappe.get_roles(user)
	if "SSO" in user_roles or "Administrator" in user_roles:
		return 		

	# Get student linked to user
	student = frappe.db.get_value(
		"Student",
		{"user": user},
		"name",
		"gender"
	)

	if not student:
		return ""

	return f"""
		EXISTS (
			SELECT 1 FROM `tabStudent List Item` sli
			WHERE sli.parent = `tabHostel Room`.name
			AND sli.student_code = '{student}'
		)
	"""    	