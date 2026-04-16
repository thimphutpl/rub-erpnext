# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from frappe.model.naming import make_autoname

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
		from_activity: DF.DynamicLink
		from_activity_type: DF.Literal["Planning Activities", "Additional Activities"]
		from_budget_type: DF.Literal["", "Current", "Capital"]
		from_output: DF.Link
		from_project: DF.Link
		from_year: DF.Link
		remarks: DF.SmallText | None
		to_activity: DF.DynamicLink
		to_activity_type: DF.Literal["Planning Activities", "Additional Activities"]
		to_budget_type: DF.Literal["", "Current", "Capital"]
		to_output: DF.Link
		to_project: DF.Link
		to_year: DF.Link
	# end: auto-generated types

	def autoname(self):
		self.name = make_autoname(
			f"BR/{self.from_year}-{self.to_year}/.##"
		)	
	def validate(self):
		self.validate_budget()

	def validate_budget(self):
		if not self.from_year or not self.to_year or not self.college or not self.from_activity:
			frappe.throw(
				_("Select College, From Activity, From and To Year First")
			)
		if self.from_activity_type == "Planning Activities":
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
			""", (self.college, self.from_year, self.to_year, self.from_activity), as_dict=True)

			if not self.approved_budget_list:
				frappe.throw(
					_("No budget found from year {0} to {1} in Approved Budget")
					.format(self.from_year, self.to_year)
				)

			if self.appropiation_amount:
				if flt(self.appropiation_amount) > flt(str(self.approved_budget_list[0].approved_budget)):
					frappe.throw(
						_("Appropiation Amount is more than Approved Budget ({0})")
						.format(str(self.approved_budget_list[0].approved_budget))
					)
		
		if self.from_activity_type == "Additional Activities":
			self.approved_budget_additional_list = frappe.db.sql("""
				SELECT abi.approved_budget, ab.name
				FROM `tabApproved Budget` ab
				INNER JOIN `tabApproved Budget Extra Item` abi 
					ON ab.name = abi.parent
				WHERE ab.college = %s
				AND ab.from_year = %s
				AND ab.to_year = %s
				AND ab.docstatus = 1
				AND abi.activity_link = %s
				ORDER BY abi.idx
			""", (self.college, self.from_year, self.to_year, self.from_activity), as_dict=True)

			if not self.approved_budget_additional_list:
				frappe.throw(
					_("No additional activities found from year {0} to {1} in Approved Budget")
					.format(self.from_year, self.to_year)
				)

			if self.appropiation_amount:
				if flt(self.appropiation_amount) > flt(str(self.approved_budget_additional_list[0].approved_budget)):
					frappe.throw(
						_("Appropiation Amount is more than Approved Budget ({0})")
						.format(str(self.approved_budget_additional_list[0].approved_budget))
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

		from_row = None
		to_row = None

		if ab.ab_extra_item:
			for row in ab.ab_extra_item:
				if row.activity_link == self.from_activity:
					from_row = row
				if row.activity_link == self.to_activity:
					to_row = row

		for row in ab.items:
			if row.activity_link == self.from_activity:
				from_row = row
			if row.activity_link == self.to_activity:
				to_row = row

		if not from_row or not to_row:
			frappe.throw(_("Activity not found in Approved Budget"))

		# if ab.ab_extra_item and not from_row or not to_row:
		# 	frappe.throw(_("Additional Activity not found in Approved Budget"))

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
				frappe.throw(_("Insufficient budget in target activity"))

			from_row.approved_budget += amount
			from_row.reappropiation_sent -= amount
			to_row.approved_budget -= amount
			to_row.reappropiation_received -= amount

		if self.from_activity_type == "Additional Activities":
			frappe.db.set_value(
				"Approved Budget Extra Item",
				from_row.name,
				{
					"approved_budget": from_row.approved_budget,
					"reappropiation_sent": from_row.reappropiation_sent
				},
				update_modified=False
			)
		else:
			frappe.db.set_value(
				"Approved Budget Item",
				from_row.name,
				{
					"approved_budget": from_row.approved_budget,
					"reappropiation_sent": from_row.reappropiation_sent
				},
				update_modified=False
			)
		if self.to_activity_type == "Additional Activities":
			frappe.db.set_value(
				"Approved Budget Extra Item",
				to_row.name,
				{
					"approved_budget": to_row.approved_budget,
					"reappropiation_received": to_row.reappropiation_received
				},
				update_modified=False
			)
		else:
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
