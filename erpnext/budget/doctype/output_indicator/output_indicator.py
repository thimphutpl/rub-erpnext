# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OutputIndicator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_indicator_item.output_indicator_item import OutputIndicatorItem
		from frappe.types import DF

		amended_from: DF.Link | None
		fiscal_year: DF.Link
		items: DF.Table[OutputIndicatorItem]
	# end: auto-generated types
	pass

	def validate(self):
		self.check_output()
		
	def check_output(self):
		output_indicator = frappe.get_value("Output Indicator", {"fiscal_year": self.fiscal_year, "docstatus": 1}, "name")
		if output_indicator:
			frappe.throw("Output Indicator exist for the year: {0}".format(self.fiscal_year))

@frappe.whitelist()
def fetch_budgetplan(fiscal_year):
	if not fiscal_year:
		frappe.throw("Select Fiscal Year First")
	
	approved_budget = frappe.db.sql('''
		SELECT  
			name
		FROM `tabApproved Budget`
		WHERE fiscal_year = %s and docstatus = 1 LIMIT 1
	''',(fiscal_year), as_dict=True)

	# frappe.throw(str(approved_budget))
	approved_budget_items = frappe.db.sql('''
		SELECT  
			output_no,
			project_no,
			activity_link,
			output,
			project,
			activities
		FROM `tabApproved Budget Item`
		WHERE parent = %s ORDER BY idx ASC
	''',(approved_budget[0].name), as_dict=True)

	if not approved_budget_items:
		frappe.throw("No approved budget found for fiscal year: {0}".format(fiscal_year))

	return approved_budget_items
