# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StudentWelfareSchemeClaim(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		attach: DF.Attach | None
		bank_account_number: DF.Data | None
		cid_number: DF.Data | None
		claim_type: DF.Link | None
		date_of_the_incident: DF.Date | None
		description_of_the_claim: DF.LongText | None
		full_name: DF.Data | None
		name_of_the_deceased: DF.Data | None
		phone_number: DF.Data | None
		program: DF.Data | None
		receivable_amount_in_figures: DF.Currency
		receivable_amount_in_words: DF.Data | None
		relation_to_the_member: DF.Data | None
		remarks: DF.SmallText | None
		scholarship_type: DF.Data | None
		semester: DF.Data | None
		student_code: DF.Link | None
		year: DF.Data | None
	# end: auto-generated types
	pass
