# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClubMembershipApplication(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		applying_for_club: DF.Link | None
		college: DF.Link
		first_name: DF.Data | None
		last_name: DF.Data | None
		posting_date: DF.Date
		program: DF.Data | None
		remarks: DF.SmallText | None
		semester: DF.Data | None
		student_code: DF.Link
		year: DF.Data | None
	# end: auto-generated types
	pass
