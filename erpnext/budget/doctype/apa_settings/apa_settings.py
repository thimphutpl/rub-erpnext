# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class APASettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.interpolation_category.interpolation_category import InterpolationCategory
		from frappe.model.document import Document
		from frappe.types import DF

		items: DF.Table[Document]
		outcome_2a_percentage: DF.Percent
		output_2b_percentage: DF.Percent
		table_jgpc: DF.Table[InterpolationCategory]
	# end: auto-generated types
	pass

	def validate(self):
		total = self.outcome_2a_percentage + self.output_2b_percentage
		if total > 100 or total < 100:
			frappe.throw("Output + Outcome should be 100")

