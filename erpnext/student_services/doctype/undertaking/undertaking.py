# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Undertaking(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		college: DF.Data | None
		contact_number: DF.Data | None
		email: DF.Data | None
		id_card: DF.Data | None
		parent_address: DF.Data | None
		parent_name: DF.Data | None
		phone_number: DF.Int
		posting_date: DF.Date | None
		programme: DF.Data | None
		semester: DF.Data | None
		student: DF.Link | None
		student_name: DF.Data | None
		year: DF.Data | None
	# end: auto-generated types
	pass
