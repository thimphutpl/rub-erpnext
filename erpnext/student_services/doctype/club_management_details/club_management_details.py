# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClubManagementDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		designation: DF.Data | None
		employee_student: DF.DynamicLink | None
		full_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		program: DF.Data | None
		role: DF.Literal["", "Club Advisor", "Club Coordinator"]
		semester: DF.Data | None
		type: DF.Literal["", "Employee", "Student"]
		year: DF.Data | None
	# end: auto-generated types
	pass
