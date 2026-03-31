# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class APAMidTermReview(Document):
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
		self.name = make_autoname(f"Mid Term Review/{college_abbr}/{self.from_year}-{self.to_year}")

@frappe.whitelist()
def get_target_setup_details(from_year, to_year, college):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year and To Year and College")
	output = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.activity_link,
			atoi.sub_activity_no,
			atoi.sub_activity,
			atoi.unit,
			atoi.weightage,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.activities_no,
			atoi.target,
			atoi.justification
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Target Output Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s
		ORDER BY atoi.idx desc
	''',(from_year, to_year, college), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	output_extra = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.sub_activity,
			atoi.unit,
			atoi.weightage,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.target,
			atoi.justification
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Output Extra Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s and ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s
		ORDER BY atoi.idx desc
	''',(from_year, to_year, college), as_dict=True)

	outcome = frappe.db.sql('''
		SELECT  
			atoi.outcome,
			atoi.unit,
			atoi.weightage,
			atoi.target,
			atoi.justification
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Target Outcome Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s
		ORDER BY atoi.idx
	''',(from_year, to_year, college), as_dict=True)

	if not outcome:
		frappe.throw("No Outcome Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	return {
		"output": output,
		"output_extra": output_extra,
		"outcome": outcome
	}