# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClubActivity(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		activity_name: DF.Data | None
		amended_from: DF.Link | None
		attachments_if_any: DF.Attach | None
		club_coordinator: DF.Data
		club_name: DF.Link
		college: DF.Data
		description: DF.SmallText | None
		first_name: DF.Data | None
		last_name: DF.Data | None
		program: DF.Data | None
		table_hulc: DF.Table[Document]
		table_mngb: DF.Table[Document]
		table_nevm: DF.Table[Document]
		total_expenses: DF.Data | None
		year: DF.Data | None
	# end: auto-generated types
	pass
