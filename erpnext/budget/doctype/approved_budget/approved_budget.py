# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ApprovedBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.approved_budget_item.approved_budget_item import ApprovedBudgetItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		fiscal_year: DF.Link
		items: DF.Table[ApprovedBudgetItem]
	# end: auto-generated types
	
	def validate(self):
		self.check_approved_budget()

	def check_approved_budget(self):
		fyp = frappe.db.sql('''
			SELECT name FROM `tabApproved Budget` 
			WHERE fiscal_year = %s and docstatus = 1
		''',(self.fiscal_year), as_dict=True)
		if fyp:
			frappe.throw("Approved Budget exists for year {0}".format(self.fiscal_year))

