# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class HostelApply(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		company: DF.Link
		first_name: DF.Data | None
		fiscal_year: DF.Link
		hostel_room: DF.Link
		hostel_type: DF.Data | None
		last_name: DF.Data | None
		middle_name: DF.Data | None
		posting_date: DF.Date
		student_code: DF.Link
	# end: auto-generated types

	def validate(self):
		if not self.hostel_room:
			frappe.throw(_("Hostel Room is required for Apply."))

		self.validate_room_capacity()

	def on_submit(self):
		self.move_student()

	def on_cancel(self):
		self.remove_student()	

	def validate_room_capacity(self):
		requested_room_doc = frappe.get_doc("Hostel Room", self.hostel_room)

		room_capacity = requested_room_doc.capacity
		current_student_count = len(requested_room_doc.get("student_list", []))

		if current_student_count >= room_capacity:
			frappe.throw(
				_("Requested room {0} has reached its full capacity ({1} students).").format(
					self.hostel_room, room_capacity
				)
			)

	def move_student(self):
		room_doc = frappe.get_doc("Hostel Room", self.hostel_room)

		#Prevent duplicate student entry
		for row in room_doc.get("student_list", []):
			if row.student_code == self.student_code:
				frappe.throw(_("Student already assigned to this room"))

		#Append student
		room_doc.append("student_list", {
			"student_code": self.student_code,
			"first_name": self.first_name,
			"last_name": self.last_name
		})

		# Save room
		room_doc.save(ignore_permissions=True)

		# Update fields correctly
		self.db_set("hostel_type", room_doc.hostel_type)

		frappe.msgprint(_(f"Student applied for room {self.hostel_room}"))

	# REMOVE STUDENT (ON CANCEL)
	def remove_student(self):
		room_doc = frappe.get_doc("Hostel Room", self.hostel_room)

		updated_list = []
		removed = False

		for row in room_doc.get("student_list", []):
			if row.student_code != self.student_code:
				updated_list.append(row)
			else:
				removed = True

		if not removed:
			frappe.msgprint(_("Student was not found in the room list"))
			return

		#Reset child table
		room_doc.set("student_list", [])

		for row in updated_list:
			room_doc.append("student_list", {
				"student_code": row.student_code,
				"first_name": row.first_name,
				"last_name": row.last_name
			})

		room_doc.flags.ignore_permissions = True
		room_doc.save()

		frappe.msgprint(_(f"Student removed from room {self.hostel_room}"))	
