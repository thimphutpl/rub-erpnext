# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ApprovedBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.approved_budget_extra_item.approved_budget_extra_item import ApprovedBudgetExtraItem
		from erpnext.budget.doctype.approved_budget_item.approved_budget_item import ApprovedBudgetItem
		from frappe.types import DF

		ab_extra_item: DF.Table[ApprovedBudgetExtraItem]
		amended_from: DF.Link | None
		college: DF.Link
		from_year: DF.Link
		items: DF.Table[ApprovedBudgetItem]
		to_year: DF.Link
		total_approved_budget: DF.Currency
	# end: auto-generated types
	
	def validate(self):
		self.check_approved_budget()
		self.validate_approved_budget()
		self.calculate_approved_budget()

	def validate_approved_budget(self):
		for row in self.items:
			if not row.approved_budget or row.approved_budget <= 0:
				frappe.throw("Approved budget not set or is zero for row: {0}".format(row.idx))

	def calculate_approved_budget(self):
		total_approved_budget = 0
		for row in self.items:
			total_approved_budget += flt(row.approved_budget)
		self.total_approved_budget = total_approved_budget

	def check_approved_budget(self):
		fyp = frappe.db.sql('''
			SELECT name FROM `tabApproved Budget` 
			WHERE from_year = %s and to_year = %s and college = %s and docstatus = 1
		''',(self.from_year, self.to_year, self.college), as_dict=True)
		if fyp:
			frappe.throw("Approved Budget exists for year {0}".format(self.from_year))

