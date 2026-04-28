# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentCounsellingRequestForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		academic_stress: DF.Check
		amended_from: DF.Link | None
		anxiety_or_depression: DF.Check
		approver: DF.Data | None
		career_guidance: DF.Check
		college: DF.Link
		cosent: DF.Check
		do_you_consent_to_being_contacted_by_the_counsellor: DF.Literal["Yes", "No"]
		email_address: DF.Data | None
		financial_concerns: DF.Check
		help_resource: DF.Literal["Yes", "No"]
		how_urgent_is_your_concern: DF.Literal["Urgent", "Moderate", "Not urgent"]
		other: DF.Check
		phone_number: DF.Data | None
		please_briefly_describe_your_concern: DF.Text | None
		preferred_date: DF.Date | None
		preferred_mode_of_counselling: DF.Literal["Face-to-face", "Phone call", "Online"]
		preferred_time: DF.Literal["Morning (9:00 AM \u2013 12:00 PM)", "Afternoon (1:00 PM \u2013 4:00 PM)"]
		programme: DF.Data | None
		reason: DF.Data | None
		relationship_issues: DF.Check
		student_id: DF.Link
		student_name: DF.Data | None
		substance_use: DF.Check
		year_of_study: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.check_validate_approval()

		
		self.validate_workflow()


	def check_validate_approval(self):
		doc=frappe.get_doc("Company",self.college)
		if doc.student_counsellor is None:
			frappe.throw("Set student counsellor in "+ str(self.college))

	def validate_workflow(self):
		self.new_state = self.workflow_state
		self.old_state = self.get_db_value("workflow_state")

		if self.new_state=='Waiting Approval':
			if self.owner != frappe.session.user:
				frappe.throw("Only "+str(self.owner)+ " can able to apply ")

		if self.new_state=='Approved':
			approver_user=get_user_id(self.approver)
			
			if frappe.session.user != approver_user:
				frappe.throw("Only "+str(approver_user)+ " can able to approved")

		
		#frappe.throw(str(self.new_state))

def get_user_id(approver):
	doc=frappe.get_doc("Employee",approver)
	return doc.user_id

def get_permission_query_conditions(user):
	if not user:
		user=frappe.session.user

	user_roles=frappe.get_roles(user)
	
	if "Administrator" in user_roles:
		return
	if "Councillor" in user_roles or "Student" in user_roles :
		#frappe.throw(str(`tabStudent Counselling Request Form`.`approver`))
		empid=''
		return f"""(`tabStudent Counselling Request Form`.approver='{user}'  ) or (`tabStudent Counselling Request Form`.owner='{user}'  )"""