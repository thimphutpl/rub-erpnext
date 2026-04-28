# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class APACalendar(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		evaluation_end_date: DF.Date
		evaluation_start_date: DF.Date
		from_year: DF.Link
		review_end_date: DF.Date
		review_start_date: DF.Date
		target_setup_end_date: DF.Date
		target_setup_start_date: DF.Date
		to_year: DF.Link
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		evaluation_end_date: DF.Date
		evaluation_start_date: DF.Date
		from_year: DF.Link
		review_end_date: DF.Dateπ
		review_start_date: DF.Date
		target_setup_end_date: DF.Date
		target_setup_start_date: DF.Date
		to_year: DF.Link

	def autoname(self):
		self.name = str(self.from_year)+"-"+str(self.to_year)
