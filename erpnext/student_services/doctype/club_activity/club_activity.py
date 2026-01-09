# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document


class ClubActivity(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.club_activity_details.club_activity_details import ClubActivityDetails
		from erpnext.student_services.doctype.club_activity_expenses_details.club_activity_expenses_details import ClubActivityExpensesDetails
		from erpnext.student_services.doctype.club_attendance_details.club_attendance_details import ClubAttendanceDetails
		from erpnext.student_services.doctype.club_coordinator_details.club_coordinator_details import ClubCoordinatorDetails
		from frappe.types import DF

		activity: DF.Data | None
		activity_name: DF.Link | None
		amended_from: DF.Link | None
		attachments_if_any: DF.Attach | None
		club_action_plan: DF.Link | None
		club_attendance_details: DF.Table[ClubAttendanceDetails]
		club_coordinator_details: DF.Table[ClubCoordinatorDetails]
		club_name: DF.Link
		company: DF.Link
		description: DF.SmallText | None
		items: DF.Table[ClubActivityExpensesDetails]
		table_hulc: DF.Table[ClubActivityDetails]
		total_expenses: DF.Data | None
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.club_activity_details.club_activity_details import ClubActivityDetails
		from erpnext.student_services.doctype.club_activity_expenses_details.club_activity_expenses_details import ClubActivityExpensesDetails
		from erpnext.student_services.doctype.club_attendance_details.club_attendance_details import ClubAttendanceDetails
		from erpnext.student_services.doctype.club_coordinator_details.club_coordinator_details import ClubCoordinatorDetails
		from frappe.types import DF

		activity_name: DF.Data | None
		amended_from: DF.Link | None
		attachments_if_any: DF.Attach | None
		club_coordinator_details: DF.Table[ClubCoordinatorDetails]
		club_name: DF.Link
		company: DF.Link
		description: DF.SmallText | None
		table_hulc: DF.Table[ClubActivityDetails]
		table_mngb: DF.Table[ClubActivityExpensesDetails]
		table_nevm: DF.Table[ClubAttendanceDetails]
		total_expenses: DF.Data | None

	def on_submit(self):
		#frappe.throw(str(self.active_name))
		self.update_action_plan_detail_status(self.activity_name)
	def validate(self):
		#self.get_attendance_club_activites(self.club_name)
		self.calculate_expansive()
	@frappe.whitelist()
	def get_attendance_club_activites(self,club_name):
		self.club_attendance_details = []
		students = frappe.get_all(
		'Club Membership Application',
		filters={
			'docstatus': 1,
			
			'applying_for_club': club_name
		},
		fields=['student_code','first_name','last_name']
		)

		for std in students:
			self.append('club_attendance_details', {
            'student_code': std.student_code,
            'first_name': std.first_name,
            'last_name': std.last_name
        	})
    

		frappe.msgprint(f"Added {len(students)} students to attendance list")
			#frappe.msgprint(str(std.student_code))
	def update_action_plan_detail_status(self,name):
    
		try:
			frappe.db.set_value(
				"Club Action Plan Details",
				name,
				{
					"status": "Complete"
					
				}
			)
			frappe.db.commit()
			frappe.msgprint("Status updated successfully")
		except Exception as e:
			frappe.log_error(f"Error updating status: {str(e)}")
			frappe.throw("Failed to update status")

	def calculate_expansive(self):
		total_exp=0
		for idx, row in enumerate(self.items):
			total_exp += flt(row.amount)

		self.total_expenses=total_exp

	@frappe.whitelist()
	def get_activity_name(self):
		if self.activity_name:
			activity_name = frappe.db.sql("SELECT activity_name FROM `tabClub Action Plan Details` WHERE name = %s", (self.activity_name,), as_dict=True)
			if activity_name:
				activity_name = activity_name[0].activity_name
			else:
				activity_name = ""
			return activity_name
	

@frappe.whitelist()
def get_coordinators(club_name):
	
	
	coordinators = frappe.get_all(
		'Club Management Details',
		filters={
			'role': 'Club Coordinator',
			'parentfield': 'club_management', 
			'parent': club_name
		},
		fields=['student_code','first_name','last_name']
	)
	

	#return [coordinator['student_code'] for coordinator in coordinators]
	return coordinators

