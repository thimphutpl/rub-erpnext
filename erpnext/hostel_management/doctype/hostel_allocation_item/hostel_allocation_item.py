# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HostelAllocationItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		capacity: DF.Data | None
		catering_type: DF.Literal["", "Mess", "Self-catering"]
		cid_number: DF.Int
		first_name: DF.Data | None
		gender: DF.Data | None
		hostel_room: DF.Link
		hostel_type: DF.Data | None
		last_name: DF.Data | None
		middle_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		scholarship_type: DF.Literal["", "Government Scholarship", "Self Funding"]
		status: DF.Data | None
		student_code: DF.Link | None
		year: DF.Data | None
	# end: auto-generated types
	pass
