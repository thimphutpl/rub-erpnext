# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Feedback(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		designation: DF.Data | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		feedback: DF.LongText | None
		feedback_type: DF.Link
		posting_date: DF.Date
		resolution_date: DF.Date | None
		what_was_the_resolution_drawn: DF.LongText | None
	# end: auto-generated types
	pass
