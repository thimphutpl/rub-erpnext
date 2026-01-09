# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClubMembershipApplication(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		applying_for_club: DF.Link | None
		college: DF.Link
		first_name: DF.Data | None
		from_date: DF.Date | None
		last_name: DF.Data | None
		posting_date: DF.Date
		programme: DF.Data | None
		remarks: DF.SmallText | None
		semester: DF.Data | None
		status: DF.Literal["Active", "In Active"]
		student_code: DF.Link
		to: DF.Date | None
		year: DF.Data | None
	# end: auto-generated types

	def validate(self):
		#pass
		self.from_date=self.posting_date

	def on_submit(self):
		club_doc = frappe.get_doc("Club", self.applying_for_club)
		count = frappe.db.count('Club Membership Application', {
		'docstatus': 1,
		'applying_for_club': self.applying_for_club,
		'name': ['!=', self.name] 
		})
		if club_doc.club_capacity > count:
			parent_doc = frappe.get_doc("Student", self.student_code)
			record_updated = False
			current_from_date = str(self.from_date) if self.from_date else None
			for row in parent_doc.extra_curricular_activities_details:
				row_from_date = str(row.from_date) if row.from_date else None
				#frappe.throw(str(row.from_date))
				if (row_from_date == current_from_date and row.club_name == self.applying_for_club):
					#frappe.throw("jg")
					row.to_date = self.to
					record_updated = True
					frappe.msgprint("Updated to_date for existing activity")
					break
			
			if not record_updated:
				parent_doc.append("extra_curricular_activities_details", {
					"from_date": self.from_date,
					"to_date": self.to,
					"club_name": self.applying_for_club
				})
				frappe.msgprint("Added new activity record")
			parent_doc.save()
		# if not frappe.db.exists("Club Member Details", {"student_code": self.student_code, "parent": self.applying_for_club}):
		# 	club_doc = frappe.get_doc("Club", self.applying_for_club)
		# 	club_member = club_doc.append("club_members", {})
		# 	club_member.student_code = self.student_code
		# 	club_member.first_name = self.first_name
		# 	club_member.last_name = self.last_name
		# 	club_member.programme = self.programme
		# 	club_member.semester = self.semester
		# 	club_doc.save()
			
