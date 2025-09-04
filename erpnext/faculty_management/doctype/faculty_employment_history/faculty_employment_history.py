# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FacultyEmploymentHistory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		designation: DF.Data | None
		from_date: DF.Date | None
		key_achievements: DF.Text | None
		organization: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		responsibilities: DF.Text | None
		to_date: DF.Date
	# end: auto-generated types
	pass
