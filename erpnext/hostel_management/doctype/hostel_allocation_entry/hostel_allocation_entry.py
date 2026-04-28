# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HostelAllocationEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		capacity: DF.Int
		catering_type: DF.Literal["", "Mess Services", "Self-Catering", "Day Scholar"]
		current_hostel_room: DF.Link | None
		current_hostel_type: DF.Link | None
		hostel_change_type: DF.Literal["", "Swap", "Room Transfer", "Day Scholar"]
		hostel_room: DF.Link | None
		hostel_type: DF.Link | None
		posting_date: DF.Date | None
		scholarship_type: DF.Link | None
		student: DF.Link | None
		student_name: DF.Data | None
		transaction_name: DF.DynamicLink | None
		transaction_type: DF.Link | None
		year: DF.Link | None
	# end: auto-generated types
	pass
