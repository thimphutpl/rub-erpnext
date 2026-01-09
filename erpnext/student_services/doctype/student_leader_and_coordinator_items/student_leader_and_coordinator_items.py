# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StudentLeaderandCoordinatorItems(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		full_name: DF.Data | None
		hostel_counsellor: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		programme: DF.Data | None
		student_code: DF.Link | None
		student_responsibiltiy: DF.Link | None
	# end: auto-generated types
	pass
