# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FacultyProfessionalDevelopment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activity_type: DF.Literal["", "Workshop", "Conference", "Training", "Certification", "Research", "Other"]
		certificate: DF.Attach | None
		end_date: DF.Date | None
		organizer: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		skills_gained: DF.Text | None
		start_date: DF.Date
		title: DF.Data
	# end: auto-generated types
	pass
