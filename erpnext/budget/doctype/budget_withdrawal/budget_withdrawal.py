# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt

class BudgetWithdrawal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		budget_activity: DF.Link
		budget_output: DF.Link
		budget_project: DF.Link
		budget_type: DF.Literal["", "Current", "Capital"]
		college: DF.Link
		from_year: DF.Link
		posting_date: DF.Date
		remarks: DF.SmallText | None
		to_year: DF.Link
		withdrawal_amount: DF.Currency
	# end: auto-generated types

	def autoname(self):
		self.name = make_autoname(
			f"BW/{self.from_year}-{self.to_year}/.##"
		)	

	def validate(self):
		self.validate_budget()

	def validate_budget(self):
		if not self.from_year or not self.to_year or not self.college or not self.budget_activity:
			frappe.throw(
				_("Select College, From Activity and Fiscal Year First")
			)
		self.approved_budget_list = frappe.db.sql("""
			SELECT abi.approved_budget, ab.name
			FROM `tabApproved Budget` ab
			INNER JOIN `tabApproved Budget Item` abi 
				ON ab.name = abi.parent
			WHERE ab.college = %s
			AND ab.from_year = %s
			AND ab.to_year = %s
			AND ab.docstatus = 1
			AND abi.activity_link = %s
			ORDER BY abi.idx
		""", (self.college, self.from_year, self.to_year, self.budget_activity), as_dict=True)

		if not self.approved_budget_list:
			frappe.throw(
				_("No budget or activity found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b> in Approved Budget")
				.format(self.from_year, self.to_year, self.college)
			)

	def on_submit(self):
		self.update_budget()

	def on_cancel(self):
		self.update_budget(cancel=True)

	def update_budget(self, cancel = False):		
		ab_name = frappe.db.get_value(
			"Approved Budget",
			{
				"college": self.college,
				"from_year": self.from_year,
				"to_year": self.to_year,
				"docstatus": 1
			},
		)

		if not ab_name:
			frappe.throw(_("Approved Budget not found"))

		ab = frappe.get_doc("Approved Budget", ab_name)

		budget_row = None

		# frappe.throw(frappe.as_json(str(ab.items)))
		for row in ab.items:   # use your child table fieldname
			if row.activity_link == self.budget_activity:
				budget_row = row

		if not budget_row:
			frappe.throw(_("Activity not found in Approved Budget"))

		amount = flt(self.withdrawal_amount)

		if not cancel:
			if budget_row.approved_budget < amount:
				frappe.throw(_("Insufficient budget in source activity"))
				
			budget_row.approved_budget -= amount
			budget_row.withdrawal_amount += amount

		else:
			budget_row.approved_budget += amount
			budget_row.withdrawal_amount -= amount

		frappe.db.set_value(
			"Approved Budget Item",
			budget_row.name,
			{
				"approved_budget": budget_row.approved_budget,
				"withdrawal_amount": budget_row.withdrawal_amount
			},
			update_modified=False
		)
		# budget_row.db_set("approved_budget", budget_row.approved_budget, update_modified=False)
