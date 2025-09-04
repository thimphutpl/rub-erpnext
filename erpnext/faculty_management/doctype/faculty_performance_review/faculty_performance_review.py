# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FacultyPerformanceReview(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		comments: DF.Text
		document: DF.Attach | None
		improvement_areas: DF.Text | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rating: DF.Literal["1 - Poor", "2 - Below Average", "3 - Average\\n4 - Good", "5 - Excellent"]
		review_date: DF.Date | None
		reviewer: DF.Link
	# end: auto-generated types
	pass
