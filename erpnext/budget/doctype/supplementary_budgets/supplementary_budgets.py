# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from frappe.model.naming import make_autoname

class SupplementaryBudgets(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		budget_activity: DF.DynamicLink
		budget_activity_type: DF.Literal["Planning Activities", "Additional Activities"]
		budget_output: DF.Link
		budget_project: DF.Link
		budget_type: DF.Literal["", "Current", "Capital"]
		college: DF.Link
		cost_center: DF.Link
		from_year: DF.Link
		posting_date: DF.Date
		remarks: DF.SmallText | None
		supplement_amount: DF.Currency
		to_year: DF.Link
	# end: auto-generated types

	def autoname(self):
		abbr = frappe.db.get_value("Company", self.college, "abbr")
		self.name = make_autoname(
			f"SB/{abbr}/{self.from_year}-{self.to_year}/.##"
		)	
	def validate(self):
		self.validate_budget()

	def validate_budget(self):
		if not self.from_year or not self.to_year or not self.college or not self.budget_activity:
			frappe.throw(
				_("Select College, From Activity and Fiscal Year First")
			)
		if self.budget_activity_type == "Planning Activities":
			self.approved_budget_list = frappe.db.sql("""
				SELECT abi.approved_budget, ab.name
				FROM `tabApproved Budget` ab
				INNER JOIN `tabApproved Budget Item` abi 
					ON ab.name = abi.parent
				WHERE ab.college = %s
				AND ab.from_year = %s
				AND ab.to_year = %s
				AND ab.cost_center = %s
				AND ab.docstatus = 1
				AND abi.activity_link = %s
				ORDER BY abi.idx
			""", (self.college, self.from_year, self.to_year, self.cost_center, self.budget_activity), as_dict=True)

			if not self.approved_budget_list:
				frappe.throw(
					_("No budget or activity found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b> in Approved Budget")
					.format(self.from_year, self.to_year, self.college)
				)

		# if self.budget_activity_type == "Additional Activities":
		# 	self.approved_budget_additional_list = frappe.db.sql("""
		# 		SELECT abi.approved_budget, ab.name
		# 		FROM `tabApproved Budget` ab
		# 		INNER JOIN `tabApproved Budget Extra Item` abi 
		# 			ON ab.name = abi.parent
		# 		WHERE ab.college = %s
		# 		AND ab.from_year = %s
		# 		AND ab.to_year = %s
		# 		AND ab.docstatus = 1
		# 		AND abi.activity_link = %s
		# 		ORDER BY abi.idx
		# 	""", (self.college, self.from_year, self.to_year, self.budget_activity), as_dict=True)

		# 	if not self.approved_budget_additional_list:
		# 		frappe.throw(
		# 			_("No additional activity found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b> in Approved Budget")
		# 			.format(self.from_year, self.to_year, self.college)
		# 		)

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
		approved_budget_additional_list = None

		if self.budget_activity_type == "Additional Activities":
			approved_budget_additional_list = frappe.db.sql("""
				SELECT abi.approved_budget, ab.name
				FROM `tabApproved Budget` ab
				INNER JOIN `tabApproved Budget Extra Item` abi 
					ON ab.name = abi.parent
				WHERE ab.college = %s
				AND ab.from_year = %s
				AND ab.to_year = %s
				AND ab.cost_center = %s
				AND ab.docstatus = 1
				AND abi.activity_link = %s
				ORDER BY abi.idx
			""", (self.college, self.from_year, self.to_year, self.cost_center, self.budget_activity), as_dict=True)

			if not approved_budget_additional_list:
				activity = frappe.get_doc("Additional Activities", self.budget_activity)
				project = frappe.get_doc("Planning Project", activity.project)
				ab.append("ab_extra_item", {
					"activity_link": self.budget_activity,
					"output_no": project.planning_output,
					"output": project.planning_output,
					"project_no": activity.project,
					"project": activity.project,
					"project": activity.project,
					"is_capital": activity.is_capital,
					"is_current": activity.is_current,
					"funding_source": activity.funding_source,
					"is_new_activity": 1,
					"activities": activity.activities,
					"approved_budget": self.supplement_amount,
					"initial_approved_budget": self.supplement_amount,
				})
				# frappe.throw(frappe.as_json((ab)))
				ab.save(ignore_permissions=True)
			elif ab.ab_extra_item:
				for row in ab.ab_extra_item:
					if row.activity_link == self.budget_activity:
						budget_row = row

		for row in ab.items:
			if row.activity_link == self.budget_activity:
				budget_row = row
		# frappe.throw(str(approved_budget_additional_list))
		if not budget_row and approved_budget_additional_list:
			frappe.throw(_("Activity not found in Approved Budget"))

		amount = flt(self.supplement_amount)

		if not cancel:
			if approved_budget_additional_list:
				budget_row.approved_budget += amount
				budget_row.supplementary_received += amount

		else:
			if budget_row.approved_budget < amount:
				frappe.throw(_("Insufficient budget in source activity"))

			budget_row.approved_budget -= amount
			budget_row.supplementary_received -= amount

		if self.budget_activity_type == "Additional Activities" and approved_budget_additional_list:
			frappe.db.set_value(
				"Approved Budget Extra Item",
				budget_row.name,
				{
					"approved_budget": budget_row.approved_budget,
					"supplementary_received": budget_row.supplementary_received
				},
				update_modified=False
			)
		elif self.budget_activity_type == "Planning Activities":
			frappe.db.set_value(
				"Approved Budget Item",
				budget_row.name,
				{
					"approved_budget": budget_row.approved_budget,
					"supplementary_received": budget_row.supplementary_received
				},
				update_modified=False
			)
		# budget_row.db_set("approved_budget", budget_row.approved_budget, update_modified=False)
