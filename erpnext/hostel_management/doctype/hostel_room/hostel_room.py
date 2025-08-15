# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HostelRoom(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		capacity: DF.Int
		company: DF.Link | None
		hostel_type: DF.Link | None
		room_number: DF.Data | None
		student_list: DF.Table[Document]
		table_jpww: DF.Table[Document]
	# end: auto-generated types
	pass
