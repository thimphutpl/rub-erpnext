# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class APAMidTermReview(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.apa_target_outcome_item.apa_target_outcome_item import APATargetOutcomeItem
		from erpnext.budget.doctype.apa_target_output_item.apa_target_output_item import APATargetOutputItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		fiscal_year: DF.Link
		outcome_items: DF.Table[APATargetOutcomeItem]
		output_items: DF.Table[APATargetOutputItem]
	# end: auto-generated types
	pass

@frappe.whitelist()
def get_target_setup_details(fiscal_year, college):
	if not fiscal_year or not college:
		frappe.throw("Select Fiscal Year and College")
	output = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.activity_link,
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
		WHERE ats.fiscal_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s
	''',(fiscal_year, college), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found for the college: {1} in the year: {0}".format(fiscal_year, college))

	outcome = frappe.db.sql('''
		SELECT  
			atoi.outcome,
			atoi.unit,
			atoi.weightage,
			atoi.target,
			atoi.justification
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Target Outcome Item` atoi ON ats.name = atoi.parent
		WHERE ats.fiscal_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s
	''',(fiscal_year, college), as_dict=True)

	if not outcome:
		frappe.throw("No Outcome Indicator found for the college: {1} in the year: {0}".format(fiscal_year, college))

	return {
		"output": output,
		"outcome": outcome
	}