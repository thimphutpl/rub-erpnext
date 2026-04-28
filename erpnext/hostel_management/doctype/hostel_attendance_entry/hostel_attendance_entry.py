# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HostelAttendanceEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attendance: DF.Data | None
		college: DF.Link | None
		councilor_name: DF.Data | None
		hostel_councilor: DF.Link | None
		posting_date: DF.Date | None
		room_number: DF.Link | None
		student_code: DF.Link | None
		student_name: DF.Data | None
	# end: auto-generated types
	pass
