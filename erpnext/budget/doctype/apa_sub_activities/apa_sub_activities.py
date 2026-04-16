# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.model.naming import make_autoname

class APASubActivities(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_category_item.output_category_item import OutputCategoryItem
		from frappe.types import DF

		activity: DF.Link
		amended_from: DF.Link | None
		college: DF.Link
		disabled: DF.Check
		from_year: DF.Link
		items: DF.Table[OutputCategoryItem]
		sub_activity: DF.Data
		to_year: DF.Link
		unit: DF.Link
	# end: auto-generated types
	pass

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"Sub-Activity/{college_abbr}/{self.from_year}-{self.to_year}/.####")
