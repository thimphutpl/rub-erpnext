# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _

class BudgetReappropiations(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		appropiation_amount: DF.Currency
		appropriation_date: DF.Date
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		college: DF.Link
		fiscal_year: DF.Link
		from_activity: DF.Link
		remarks: DF.SmallText | None
		to_activity: DF.Link
	# end: auto-generated types

	def validate(self):
		self.validate_budget()

	def validate_budget(self):
		if not self.fiscal_year or not self.college or not self.from_activity:
			frappe.throw(
				_("Select College, From Activity and Fiscal Year First")
			)
		self.approved_budget_list = frappe.db.sql("""
			SELECT abi.approved_budget, ab.name
			FROM `tabApproved Budget` ab
			INNER JOIN `tabApproved Budget Item` abi 
				ON ab.name = abi.parent
			WHERE ab.college = %s
			AND ab.fiscal_year = %s
			AND ab.docstatus = 1
			AND abi.activity_link = %s
			ORDER BY abi.idx
		""", (self.college, self.fiscal_year, self.from_activity), as_dict=True)

		if not self.approved_budget_list:
			frappe.throw(
				_("No budget found for year {0} in Approved Budget")
				.format(self.fiscal_year)
			)
		if self.appropiation_amount:
			# frappe.throw("{0}, {1}".format(flt(self.appropiation_amount), flt(str(self.approved_budget_list[0].approved_budget))))
			if flt(self.appropiation_amount) > flt(str(self.approved_budget_list[0].approved_budget)):
				frappe.throw(
					_("Appropiation Amount is more than Approved Budget ({0})")
					.format(str(self.approved_budget_list[0].approved_budget))
				)

	def on_submit(self):
		self.update_budget()

	def on_cancel(self):
		self.update_budget(cancel=True)

	def update_budget(self, cancel = False):
		# ab = frappe.get_doc("Approved Budget", {"college": self.college, "fiscal_year": self.fiscal_year, "docstatus": 1})
		# from_activity = frappe.get_doc("Approved Budget Item", {"parent": ab.name, "activity_link": self.from_activity})
		# to_activity = frappe.get_doc("Approved Budget Item", {"parent": ab.name, "activity_link": self.to_activity})
		# from_activity.approved_budget = from_activity.approved_budget - self.appropiation_amount
		# to_activity.approved_budget = to_activity.approved_budget + self.appropiation_amount
		# from_activity.save(ignore_permissions=True)
		# to_activity.save(ignore_permissions=True)
		
		ab_name = frappe.db.get_value(
			"Approved Budget",
			{
				"college": self.college,
				"fiscal_year": self.fiscal_year,
				"docstatus": 1
			},
		)

		if not ab_name:
			frappe.throw(_("Approved Budget not found"))

		ab = frappe.get_doc("Approved Budget", ab_name)

		from_row = None
		to_row = None

		# frappe.throw(frappe.as_json(str(ab.items)))
		for row in ab.items:   # use your child table fieldname
			if row.activity_link == self.from_activity:
				from_row = row
			if row.activity_link == self.to_activity:
				to_row = row

		if not from_row or not to_row:
			frappe.throw(_("Activity not found in Approved Budget"))

		amount = flt(self.appropiation_amount)

		if not cancel:
			if from_row.approved_budget < amount:
				frappe.throw(_("Insufficient budget in source activity"))

			from_row.approved_budget -= amount
			from_row.reappropiation_sent += amount
			to_row.approved_budget += amount
			to_row.reappropiation_received += amount


		else:
			if to_row.approved_budget < amount:
				frappe.throw(_("Insufficient budget in source activity"))

			from_row.approved_budget += amount
			from_row.reappropiation_sent -= amount
			to_row.approved_budget -= amount
			to_row.reappropiation_received -= amount

		frappe.db.set_value(
			"Approved Budget Item",
			from_row.name,
			{
				"approved_budget": from_row.approved_budget,
				"reappropiation_sent": from_row.reappropiation_sent
			},
			update_modified=False
		)
		frappe.db.set_value(
			"Approved Budget Item",
			to_row.name,
			{
				"approved_budget": to_row.approved_budget,
				"reappropiation_received": to_row.reappropiation_received
			},
			update_modified=False
		)
		# from_row.db_set("approved_budget", from_row.approved_budget, update_modified=False)
		# to_row.db_set("approved_budget", to_row.approved_budget, update_modified=False)
