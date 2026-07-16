# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class AdditionalActivities(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_category_item.output_category_item import OutputCategoryItem
		from frappe.types import DF

		activities: DF.SmallText
		amended_from: DF.Link | None
		college: DF.Link
		disabled: DF.Check
		from_year: DF.Link
		funding_source: DF.Link | None
		include_in_apa: DF.Check
		is_capital: DF.Check
		is_current: DF.Check
		items: DF.Table[OutputCategoryItem]
		project: DF.Link
		to_year: DF.Link
		unit: DF.Link | None
	# end: auto-generated types

	def validate(self):
		duplicate = frappe.db.sql("""
			SELECT name
			FROM `tabAdditional Activities`
			WHERE LOWER(activities) = LOWER(%s)
			AND college = %s
			AND from_year = %s
			AND to_year = %s
			AND name != %s
			LIMIT 1
		""", (
			self.activities,
			self.college,
			self.from_year,
			self.to_year,
			self.name
		))

		if duplicate:
			frappe.throw("Activity: <b>{0}</b> already exists for the selected College: <b>{1}</b> for the Year <b>{2}</b> to <b>{3}</b>".format(self.activities, self.college, self.from_year, self.to_year))

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"Additional Activities/{college_abbr}/{self.from_year}-{self.to_year}/.##")