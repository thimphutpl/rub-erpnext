# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FacultyProjectAssignment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		end_date: DF.Date
		gantt_chart_reference: DF.Data | None
		hours_per_week: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.Link
		role: DF.Data
		start_date: DF.Date
	# end: auto-generated types
	pass
