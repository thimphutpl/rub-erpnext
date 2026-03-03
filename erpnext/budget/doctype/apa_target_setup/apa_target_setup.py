# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class APATargetSetup(Document):
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
def fetch_output_and_outcome(fiscal_year):
	if not fiscal_year:
		frappe.throw("Select Fiscal Year")
	output = frappe.db.sql('''
		SELECT  
			oii.output_no,
			oii.project_no,
			oii.activity_link,
			oii.unit,
			oii.weightage,
			oii.output,
			oii.project,
			oii.activities,
			oii.activities_no
		FROM `tabOutput Indicator` oi 
		INNER JOIN `tabOutput Indicator Item` oii ON oi.name = oii.parent
		WHERE oi.fiscal_year = %s
	''',(fiscal_year), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found for the year: {0}".format(fiscal_year))

	outcome = frappe.db.sql('''
		SELECT  
			unit,
			weightage,
			outcome
		FROM `tabOutcome Indicator`
		WHERE disabled = 0
	''', as_dict=True)

	if not outcome:
		frappe.throw("No Outcome Indicator found for the year: {0}".format(fiscal_year))

	return {
		"output": output,
		"outcome": outcome
	}