# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class OutputIndicator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_extra_item.output_extra_item import OutputExtraItem
		from erpnext.budget.doctype.output_indicator_item.output_indicator_item import OutputIndicatorItem
		from frappe.types import DF

		additional_activities: DF.Table[OutputExtraItem]
		amended_from: DF.Link | None
		college: DF.Link
		from_year: DF.Link
		items: DF.Table[OutputIndicatorItem]
		to_year: DF.Link
	# end: auto-generated types
	pass

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"Output Indicator/{college_abbr}/{self.from_year}-{self.to_year}/.####")

	def validate(self):
		self.check_output()
		self.check_empty_sub_activity()
	
	def check_empty_sub_activity(self):
		for item in self.get("additional_activities") or []:
			if not item.sub_activity:
				item.sub_activity = item.activities
		
	def check_output(self):
		output_indicator = frappe.get_value("Output Indicator", {"from_year": self.from_year, "to_year": self.to_year, "college": self.college, "docstatus": 1}, "name")
		if output_indicator:
			frappe.throw("Output Indicator exist from year {0} to {1} for {2}".format(self.from_year, self.to_year, self.college))

@frappe.whitelist()
def fetch_budgetplan(from_year, to_year, college):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year, To Year and College")
	
	approved_budget = frappe.db.sql('''
		SELECT  
			name
		FROM `tabApproved Budget`
		WHERE from_year = %s and to_year = %s and college = %s and docstatus = 1 LIMIT 1
	''',(from_year, to_year, college), as_dict=True)

	if not approved_budget:
		frappe.throw("No approved budget found from year {0} to {1} for {2}".format(from_year, to_year, college))
	approved_budget_items = frappe.db.sql("""
		SELECT  
			abi.output_no,
			abi.project_no,
			abi.activity_link,
			sa.name AS sub_activity_no,
			COALESCE(sa.sub_activity, abi.activities) AS sub_activity,
			COALESCE(sa.unit, pa.unit) AS unit,		
			abi.output,
			abi.project,
			abi.activities
		FROM `tabApproved Budget Item` abi
		LEFT JOIN `tabPlanning Activities` pa
			ON pa.name = abi.activity_link
		LEFT JOIN `tabAPA Sub Activities` sa
			ON sa.activity = abi.activity_link
			AND sa.from_year = %s
			AND sa.to_year = %s
			AND sa.college = %s
		WHERE abi.parent = %s
		ORDER BY abi.idx ASC
	""", (from_year, to_year, college, approved_budget[0].name), as_dict=True)

	approved_budget_extra_items = frappe.db.sql("""
		SELECT
			abei.output_no,
			abei.project_no,
			abei.output,
			abei.project,
			abei.activity_link,
			abei.activities,
			abei.is_current,
			abei.is_capital,
			COALESCE(sa.sub_activity, abei.activities) AS sub_activity,
			COALESCE(sa.unit, pa.unit) AS unit,
			abei.funding_source
		FROM `tabApproved Budget Extra Item` abei
		LEFT JOIN `tabAdditional Activities` pa
			ON pa.name = abei.activity_link
		LEFT JOIN `tabAdditional Sub Activities` sa
			ON sa.activity = abei.activity_link
			AND sa.from_year = %s
			AND sa.to_year = %s
			AND sa.college = %s
		WHERE parent = %s
		ORDER BY abei.idx ASC
	""", (from_year, to_year, college, approved_budget[0].name), as_dict=True)

	if not approved_budget_items:
		frappe.throw("No approved budget found from year {0} to {1} for {2}".format(from_year, to_year, college))

	return {
		"approved_budget_items": approved_budget_items,
		"approved_budget_extra_items": approved_budget_extra_items
	} 

# @frappe.whitelist()
# def fetch_unit(activity_link, sub_activity_no):
# 	if activity_link:
# 	unit = f
# 	approved_budget = frappe.db.sql('''
# 		SELECT  
# 			name
# 		FROM `tabApproved Budget`
# 		WHERE from_year = %s and to_year = %s and college = %s and docstatus = 1 LIMIT 1
# 	''',(from_year, to_year, college), as_dict=True)

# 	if not approved_budget:
# 		frappe.throw("No approved budget found from year {0} to {1} for {2}".format(from_year, to_year, college))
# 	approved_budget_items = frappe.db.sql("""
# 		SELECT  
# 			abi.output_no,
# 			abi.project_no,
# 			abi.activity_link,
# 			sa.name AS sub_activity_no,
# 			COALESCE(sa.sub_activity, abi.activities) AS sub_activity,
# 			abi.output,
# 			abi.project,
# 			abi.activities
# 		FROM `tabApproved Budget Item` abi
# 		LEFT JOIN `tabPlanning Activities` pa
# 			ON pa.name = abi.activity_link
# 		LEFT JOIN `tabAPA Sub Activities` sa
# 			ON sa.activity = abi.activity_link
# 			AND sa.from_year = %s
# 			AND sa.to_year = %s
# 			AND sa.college = %s
# 		WHERE abi.parent = %s
# 		ORDER BY abi.idx ASC
# 	""", (from_year, to_year, college, approved_budget[0].name), as_dict=True)

# 	approved_budget_extra_items = frappe.db.sql("""
# 		SELECT
# 			abei.output_no,
# 			abei.project_no,
# 			abei.output,
# 			abei.project,
# 			abei.activity_link,
# 			sa.name AS sub_activity_link,
# 			abei.activities,
# 			abei.is_current,
# 			abei.is_capital,
# 			COALESCE(sa.sub_activity, abei.activities) AS sub_activity,
# 			CASE
# 				WHEN abei.name THEN sa.unit
# 				ELSE pa.unit
# 			END AS unit,
# 			abei.funding_source
# 		FROM `tabApproved Budget Extra Item` abei
# 		LEFT JOIN `tabAdditional Activities` pa
# 			ON pa.name = abei.activity_link
# 		LEFT JOIN `tabAdditional Sub Activities` sa
# 			ON sa.activity = abei.activity_link
# 			AND sa.from_year = %s
# 			AND sa.to_year = %s
# 			AND sa.college = %s
# 		WHERE parent = %s
# 		ORDER BY abei.idx ASC
# 	""", (from_year, to_year, college, approved_budget[0].name), as_dict=True)

# 	if not approved_budget_items:
# 		frappe.throw("No approved budget found from year {0} to {1} for {2}".format(from_year, to_year, college))

# 	return {
# 		"approved_budget_items": approved_budget_items,
# 		"approved_budget_extra_items": approved_budget_extra_items
# 	} 
