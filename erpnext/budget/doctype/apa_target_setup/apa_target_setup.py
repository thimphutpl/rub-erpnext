# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class APATargetSetup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.apa_output_extra_item.apa_output_extra_item import APAOutputExtraItem
		from erpnext.budget.doctype.apa_target_outcome_item.apa_target_outcome_item import APATargetOutcomeItem
		from erpnext.budget.doctype.apa_target_output_item.apa_target_output_item import APATargetOutputItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		from_year: DF.Link
		outcome_items: DF.Table[APATargetOutcomeItem]
		output_extra_items: DF.Table[APAOutputExtraItem]
		output_items: DF.Table[APATargetOutputItem]
		to_year: DF.Link
	# end: auto-generated types
	pass

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"APA Target/{college_abbr}/{self.from_year}-{self.to_year}/.##")

@frappe.whitelist()
def fetch_output_and_outcome(from_year, to_year, college):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year, To Year and College")
	output = frappe.db.sql('''
		SELECT  
			oii.output_no,
			oii.project_no,
			oii.activity_link,
			oii.sub_activity_no,
			oii.unit,
			oii.weightage,
			oii.output,
			oii.project,
			oii.activities,
			oii.sub_activity,
			oii.activities_no
		FROM `tabOutput Indicator` oi 
		INNER JOIN `tabOutput Indicator Item` oii ON oi.name = oii.parent
		WHERE oi.from_year = %s and oi.to_year = %s and oi.college = %s
		ORDER BY oii.idx ASC
	''',(from_year, to_year, college), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))
		
	output_extra = frappe.db.sql('''
		SELECT  
			oii.output_no,
			oii.project_no,
			oii.unit,
			oii.weightage,
			oii.output,
			oii.project,
			oii.activities,
			oii.activity_link,
			oii.sub_activity_link,
			oii.sub_activity
		FROM `tabOutput Indicator` oi 
		INNER JOIN `tabOutput Extra Item` oii ON oi.name = oii.parent
		WHERE oi.from_year = %s and oi.to_year = %s and oi.college = %s
		ORDER BY oii.idx ASC
	''',(from_year, to_year, college), as_dict=True)

	outcome = frappe.db.sql('''
		SELECT  
			unit,
			weightage,
			outcome
		FROM `tabOutcome Indicator`
		WHERE disabled = 0
	''', as_dict=True)

	if not outcome:
		frappe.throw("No Outcome Indicator found")

	return {
		"output": output,
		"output_extra": output_extra,
		"outcome": outcome
	}