# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClubList(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		abbr: DF.Data | None
		club_capacity: DF.Int
		club_name: DF.Data
		company: DF.Link
		table_bafb: DF.Table[Document]
		table_hwxy: DF.Table[Document]
		table_yfqw: DF.Table[Document]
	# end: auto-generated types
	pass
