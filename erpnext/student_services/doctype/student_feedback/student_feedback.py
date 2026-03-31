# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StudentFeedback(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.oeq_responses.oeq_responses import OEQResponses
		from erpnext.student_services.doctype.rating_responses.rating_responses import RatingResponses
		from frappe.types import DF

		academic_year: DF.Link | None
		college: DF.Link | None
		date: DF.Date | None
		feedback_type: DF.Data | None
		oeq_responses: DF.Table[OEQResponses]
		rating_responses: DF.Table[RatingResponses]
		student: DF.Data | None
	# end: auto-generated types
	pass
