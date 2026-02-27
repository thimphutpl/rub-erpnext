# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StudentCulturalPerformers(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.cultural_performers.cultural_performers import CulturalPerformers
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		fiscal_year: DF.Link
		posting_date: DF.Date
		student_list: DF.Table[CulturalPerformers]
	# end: auto-generated types
	pass
