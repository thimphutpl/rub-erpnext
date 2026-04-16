# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
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
		career_guidance: DF.Check
		cosent: DF.Check
		do_you_consent_to_being_contacted_by_the_counsellor: DF.Literal["Yes", "No"]
		email_address: DF.Data | None
		financial_concerns: DF.Check
		help_resource: DF.Literal["Yes", "No"]
		how_urgent_is_your_concern: DF.Literal["Urgent", "Moderate", "Not urgent"]
		other: DF.Check
		phone_number: DF.Date | None
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
	pass
