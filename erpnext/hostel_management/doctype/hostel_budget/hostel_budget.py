# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HostelBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.hostel_budget_item.hostel_budget_item import HostelBudgetItem
		from frappe.types import DF

		amended_from: DF.Link | None
		balance_amount: DF.Float
		college: DF.Link
		expense_type: DF.Link | None
		expenses_amount: DF.Table[HostelBudgetItem]
		hostel_block: DF.Link
		hostel_councilor: DF.Link
		hostel_councilor_name: DF.Data | None
		posting_date: DF.Date
		previous_amount: DF.Float
		total_budget_collection: DF.Float
	# end: auto-generated types
	# pass

	# def validate(self):
	# 	total_amount = sum([d.amount for d in self.get("expenses_amount")])
	# 	self.balance_amount = (self.total_budget_collection or 0) - total_amount

	def validate(self):
		previous = frappe.db.sql("""
			SELECT balance_amount
			FROM `tabHostel Budget`
			WHERE hostel_block = %s
			AND name != %s
			AND docstatus = 1
			ORDER BY posting_date DESC, creation DESC
			LIMIT 1
		""", (self.hostel_block, self.name), as_dict=True)

		self.previous_amount = previous[0].balance_amount if previous else 0
		self.total_budget_collection = (self.total_budget_collection or 0) + self.previous_amount
		total_expense = sum([d.amount for d in self.get("expenses_amount")])
		self.balance_amount = self.total_budget_collection - total_expense