# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class PlanningActivitiesTargetSetup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_category_item.output_category_item import OutputCategoryItem
		from frappe.types import DF

		activities: DF.Link
		college: DF.Link
		disabled: DF.Check
		from_year: DF.Link
		items: DF.Table[OutputCategoryItem]
		to_year: DF.Link
		unit: DF.Link
		
	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"PATS/{college_abbr}/{self.from_year}-{self.to_year}/.####")

	def validate(self):
		self.check_duplicate()
		
	def check_duplicate(self):
		pats = frappe.get_value("Planning Activities Target Setup", {"from_year": self.from_year, "to_year": self.to_year, "college": self.college, "activities": self.activities, "name": ["!=", self.name],}, "name")
		if pats:
			frappe.throw("Planning Activities Target Setup exist of <b>{0}</b> from year <b>{1}</b> to <b>{2}</b> for <b>{3}</b>".format(self.activities, self.from_year, self.to_year, self.college))
