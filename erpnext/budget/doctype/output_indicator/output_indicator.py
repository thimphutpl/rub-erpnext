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
		department: DF.Link | None
		from_year: DF.Link
		items: DF.Table[OutputIndicatorItem]
		to_year: DF.Link
	# end: auto-generated types

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
	
	# approved_budget = frappe.db.sql('''
	# 	SELECT  
	# 		name
	# 	FROM `tabApproved Budget`
	# 	WHERE from_year = %s and to_year = %s and college = %s and docstatus = 1 LIMIT 1
	# ''',(from_year, to_year, college), as_dict=True)

	# if not approved_budget:
	# 	frappe.throw("No approved budget found from year {0} to {1} for {2}".format(from_year, to_year, college))
	approved_budget_items = frappe.db.sql("""
		SELECT  
			po.serial_number as output_no,
			pp.serial_number as project_no,
			pa.name as activity_link,
			sa.name AS sub_activity_no,
			COALESCE(sa.sub_activity, NULL) AS sub_activity,
			COALESCE(sa.unit, pats.unit) AS unit,		
			po.output,
			pp.project,
			pa.activities
		FROM `tabPlanning Activities` pa
		LEFT JOIN `tabPlanning Project` pp
		ON pa.project = pp.name
		LEFT JOIN `tabPlanning Output` po
		ON pp.planning_output = po.name
		LEFT JOIN `tabPlanning Activities Target Setup` pats
			ON pa.name = pats.activities
			AND pats.disabled = 0
			AND pats.college = %s
		LEFT JOIN `tabAPA Sub Activities` sa
			ON sa.activity = pa.name
			AND sa.from_year = %s
			AND sa.to_year = %s
			AND sa.college = %s
			AND sa.disabled = 0
		WHERE %s not in (select college from `tabIgnore PA For College` ipa where ipa.parent = pa.name)
	""", (college, from_year, to_year, college, college), as_dict=True)

	approved_budget_extra_items = frappe.db.sql("""
		SELECT
			po.serial_number as output_no,
			pp.serial_number as project_no,
			po.output,
			pp.project,
			aa.name as activity_link,
			aa.activities,
			aa.is_current,
			aa.is_capital,
			COALESCE(sa.sub_activity, NULL) AS sub_activity,
			COALESCE(sa.unit, aa.unit) AS unit,
			aa.funding_source,
			sa.name as sub_activity_link
		FROM `tabAdditional Activities` aa
		LEFT JOIN `tabPlanning Project` pp
		ON aa.project = pp.name
		LEFT JOIN `tabPlanning Output` po
		ON pp.planning_output = po.name
		LEFT JOIN `tabAdditional Sub Activities` sa
			ON sa.activity = aa.name
			AND sa.from_year = %s
			AND sa.to_year = %s
			AND sa.college = %s
		WHERE aa.include_in_apa = 1 AND aa.disabled = 0 AND aa.college = %s
	""", (from_year, to_year, college, college), as_dict=True)

	# if not approved_budget_items:
	# 	frappe.throw("No approved budget found from year {0} to {1} for {2}".format(from_year, to_year, college))

	return {
		"approved_budget_items": approved_budget_items,
		"approved_budget_extra_items": approved_budget_extra_items
	} 

@frappe.whitelist()
def get_activity_weightage(from_year, to_year, college, activity_link):
	if not activity_link:
		return
	
	output_category_items = frappe.db.sql("""
		SELECT  
			oic.category,
			oic.max,
			oic.min,
			oic.unit as grade,
			oic.raw_rating as score
		FROM `tabPlanning Activities Target Setup` pats
		INNER JOIN `tabOutput Category Item` oci
		ON pats.name = oci.parent
		WHERE pats.from_year = %s AND pats.to_year = %s AND pats.college = %s AND pats.activities = %s
		ORDER BY idx ASC
	""", (from_year, to_year, college, activity_link), as_dict=True)

	return output_category_items