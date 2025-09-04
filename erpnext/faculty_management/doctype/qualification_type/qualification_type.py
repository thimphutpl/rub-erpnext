# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class QualificationType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		duration_years: DF.Float
		level: DF.Literal["", "Certificate", "Diploma", "Bachelor's", "Master's", "Doctorate"]
		qualification_name: DF.Data
		quatification_code: DF.Data
	# end: auto-generated types
	pass
