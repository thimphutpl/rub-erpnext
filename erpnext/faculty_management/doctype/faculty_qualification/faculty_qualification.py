# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FacultyQualification(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		document: DF.Attach | None
		institution: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qualification: DF.Data
		specialization: DF.Data | None
		year: DF.Int
	# end: auto-generated types
	pass
