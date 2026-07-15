# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate, today

class AnnualWorkPlan(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.apa_detail.apa_detail import APADetail
		from erpnext.budget.doctype.apa_detail_extra.apa_detail_extra import APADetailExtra
		from frappe.types import DF

		amended_from: DF.Link | None
		apa_copies: DF.Check
		apa_details: DF.Table[APADetail]
		apa_extra_details: DF.Table[APADetailExtra]
		colleges: DF.Link
		from_year: DF.Link
		fyp: DF.Link
		remarks: DF.SmallText | None
		to_year: DF.Link
		total_approved_budget: DF.Currency
		total_approved_budget_in_fyp: DF.Currency
		total_proposed_budget: DF.Currency

	def autoname(self):
		abbr = frappe.db.get_value("Company", self.colleges, "abbr")
		self.name = "AWP/"+self.from_year+"-"+self.to_year+"/"+abbr

	def validate(self):
		self.check_applicable_date()
		self.validate_college()
		self.validate_budget()
		self.validate_proposed_and_approved_budget()
		self.calculate_proposed_and_approved_budget()
		self.apply_proposed_to_approved()
	
	def on_cancel(self):
		if frappe.db.exists(
			"Approved Budget",
			{"college": self.colleges, "from_year": self.from_year, "to_year": self.to_year, "docstatus": 1},
			"name",
		):
			frappe.throw("Cancel the existing Approved Budget for college: <b>{0}</b> for the year <b>{1}</b> to <b>{2}</b>".format(self.colleges, self.from_year, self.to_year))

	
	def check_applicable_date(self):
		current_date = getdate(today())
		from_date = frappe.db.get_single_value("Budget Settings", "awp_from_date")
		to_date = frappe.db.get_single_value("Budget Settings", "awp_to_date")
		allow_transaction = frappe.db.exists(
			"Allow Budget Transaction",
			{"college": self.colleges, "from_date": ["<=", today()], "to_date": [">=", today()], "transaction_type": self.doctype, "docstatus": 1},
			"name",
		)

		if not from_date or not to_date:
			frappe.throw("Transaction not allowed because Annual Work Plan dates (from & to) not set in Budget Settings")

		if not (allow_transaction or getdate(today()) <= getdate(to_date)):
			frappe.throw("Transaction not allowed after <b>{0}</b>".format(to_date))

		if not (allow_transaction or getdate(from_date) <= getdate(today())):
			frappe.throw("Transaction not allowed before <b>{0}</b>".format(from_date))

	def apply_proposed_to_approved(self):
		actions = get_apply_reapply_actions("Annual Work Plan", self.name)
		# frappe.throw(str(actions))
		if frappe.form_dict.get("action") == "Apply":
			if self.apa_details:
				for row in self.apa_details:
					row.approved_budget = row.proposed_budget

			if self.apa_extra_details:
				for row in self.apa_extra_details:
					row.approved_budget = row.proposed_budget

	def validate_proposed_and_approved_budget(self):
		if self.apa_details:
			for row in self.apa_details:
				if not row.proposed_budget or row.proposed_budget <= 0:
					frappe.throw("Proposed budget not set or is zero for row: {0}".format(row.idx))

				if frappe.form_dict.get("action") != "Apply" and self.workflow_state != "Draft":
					if not row.approved_budget or row.approved_budget <= 0:
						frappe.throw("Approved budget not set or is zero for row: {0}".format(row.idx))

		if self.apa_extra_details:
			for row in self.apa_extra_details:
				# if not row.proposed_budget or row.proposed_budget <= 0:
				# 	frappe.throw("Proposed budget not set or is zero for row: {0} in additional activities".format(row.idx))

				if frappe.form_dict.get("action") != "Apply" and self.workflow_state != "Draft":
					if not row.approved_budget or row.approved_budget <= 0:
						frappe.throw("Approved budget not set or is zero for row: {0} in additional activities".format(row.idx))

	def calculate_proposed_and_approved_budget(self):
		total_proposed_budget = 0
		total_approved_budget = 0

		if self.apa_details:
			for row in self.apa_details:
				total_approved_budget += flt(row.approved_budget)
				total_proposed_budget += flt(row.proposed_budget)
				
		if self.apa_extra_details:
			for row in self.apa_extra_details:
				total_approved_budget += flt(row.approved_budget)
				total_proposed_budget += flt(row.proposed_budget)

		self.total_proposed_budget = total_proposed_budget
		self.total_approved_budget = total_approved_budget

	def validate_college(self):
		proposal_list = frappe.db.sql(""" 
			SELECT colleges
			FROM `tabFive Year Plan Proposal`
			WHERE colleges = %s 
			AND %s BETWEEN from_year AND to_year
			AND %s BETWEEN from_year AND to_year
			AND docstatus = 1
		""", (self.colleges, self.from_year, self.to_year), as_dict=True)
		if len(proposal_list) <= 0:
			frappe.throw(_("No proposed budget found for college: {0} in the five year plan proposal".format(self.colleges)))

	def validate_budget(self):
		approved_budget_list = frappe.db.sql("""
			SELECT fypi.approved_budget, fypi.activity_link
			FROM `tabFive Year Plan` fyp
			INNER JOIN `tabFive Year Plan Items` fypi 
				ON fyp.name = fypi.parent
			WHERE fyp.name = %s 
			AND %s BETWEEN fyp.from_year AND fyp.to_year
			AND %s BETWEEN fyp.from_year AND fyp.to_year
			AND fyp.docstatus = 1
			ORDER BY fypi.idx
		""", (self.fyp, self.from_year, self.to_year), as_dict=True)

		if not approved_budget_list:
			frappe.throw(
				_("No budget found for year {0} - {1} in Five Year Plan")
				.format(self.from_year, self.to_year)
			)

		awp_list = frappe.db.sql("""
			SELECT awpi.approved_budget, awpi.proposed_budget, awpi.activity_link
			FROM `tabAnnual Work Plan` awp
			INNER JOIN `tabAPA Detail` awpi 
				ON awp.name = awpi.parent
			WHERE awp.from_year = %s and awp.to_year = %s and awp.docstatus = 1
			ORDER BY awpi.idx
		""", (self.from_year, self.to_year), as_dict=True)

		approved_budget_map = {}
		for d in approved_budget_list:
			approved_budget_map[d.activity_link] = (
				approved_budget_map.get(d.activity_link, 0)
				+ flt(d.approved_budget)
			)
		awp_approved_map = {}
		awp_proposed_map = {}

		for d in awp_list:
			awp_approved_map[d.activity_link] = (
				awp_approved_map.get(d.activity_link, 0)
				+ flt(d.approved_budget)
			)
			awp_approved_map[d.activity_link] = (
				awp_approved_map.get(d.activity_link, 0)
				+ flt(d.proposed_budget)
			)
			
		for row in self.apa_details:
			available_budget = approved_budget_map.get(row.activity_link, 0)
			already_approved_budget = awp_approved_map.get(row.activity_link, 0)
			already_proposed_budget = awp_proposed_map.get(row.activity_link, 0)

			if not available_budget or available_budget <= 0:
				frappe.throw(
					_("No approved budget found for Activity: <b>{0}</>")
					.format(row.activities)
				)

			total_approved_budget = (
				flt(row.approved_budget)
				+ already_approved_budget
			)

			total_proposed_budget = (
				flt(row.proposed_budget)
				+ already_proposed_budget
			)

			if total_approved_budget > available_budget:
				frappe.throw(
					_("Approved budget for Activity <b>{0}<b/> exceeds available budget <b>({1})</b>")
					.format(row.activities, available_budget)
				)

			if total_proposed_budget > available_budget:
				frappe.throw(
					_("Approved budget for Activity <b>{0}<b/> exceeds available budget <b>({1})</b>")
					.format(row.activities, available_budget)
				)

@frappe.whitelist()
def get_additional_activities(from_year, to_year, college):
	if not college and not from_year and not to_year:
		frappe.throw("Select College, From Year and To Year")
	additional = frappe.db.sql('''
		SELECT t3.name AS output_no, t3.output, t2.name AS project_no, t2.project, t1.name AS activity_link,
		t1.activities, t1.is_current, t1.is_capital, t1.funding_source
		FROM `tabAdditional Activities` t1
		INNER JOIN `tabPlanning Project` t2
		ON t1.project = t2.name
		INNER JOIN `tabPlanning Output` t3
		ON t2.planning_output = t3.name
		WHERE t1.college=%s AND t1.from_year=%s AND t1.to_year=%s
	''',(college, from_year, to_year), as_dict=True)

	return additional

@frappe.whitelist()
def create_apa_for_subsidiaries(apa_name):
	colleges = frappe.db.sql("""
		SELECT name
		FROM `tabCompany`
		WHERE IFNULL(is_overseeing_company, 0) != 1
	""", as_dict=True)

	parent_apa = frappe.get_doc("Annual Performance Agreement", apa_name)
	created = []

	for college in colleges:
		if frappe.db.exists("Annual Performance Agreement", {
			"colleges": college["name"],
			"parent_fyp": parent_apa.name
		}):
			continue

		fyp_copy = frappe.new_doc("Annual Performance Agreement")

		fyp_copy.update({
			key: value
			for key, value in parent_apa.as_dict().items()
			if key not in (
				"name", "doctype", "owner", "creation", "modified",
				"modified_by", "docstatus"
			)
		})

		fyp_copy.colleges = college["name"]
		fyp_copy.parent_apa = parent_apa.name  # recommended tracking

		fyp_copy.insert(ignore_permissions=True)
		created.append(fyp_copy.name)

	if created:
		parent_apa.db_set("apa_copies", 1)

	return {
		"status": "success",
		"created_apa_count": len(created),
		"apa_records": created
	}

@frappe.whitelist()
def make_approved_budget(source_name, target_doc=None):
	def set_missing_values(source, target):
		return

	def postprocess(source, target):
		target.college = source.colleges

		# Main activities
		for source_row, target_row in zip(source.apa_details, target.items):
			existing_total = frappe.db.sql("""
				SELECT COALESCE(SUM(child.initial_approved_budget), 0)
				FROM `tabApproved Budget Item` child
				INNER JOIN `tabApproved Budget` parent
					ON child.parent = parent.name
				WHERE parent.docstatus = 1
				AND parent.from_year = %s
				AND parent.to_year = %s
				AND parent.college = %s
				AND child.activity_link = %s
			""", (
				source.from_year,
				source.to_year,
				source.colleges,
				source_row.activity_link
			))[0][0]

			target_row.available_budget = (
				(source_row.approved_budget or 0) - existing_total
			)

		# Extra activities
		for source_row, target_row in zip(source.apa_extra_details, target.ab_extra_item):
			existing_total = frappe.db.sql("""
				SELECT COALESCE(SUM(child.initial_approved_budget), 0)
				FROM `tabApproved Budget Extra Item` child
				INNER JOIN `tabApproved Budget` parent
					ON child.parent = parent.name
				WHERE parent.docstatus = 1
				AND parent.from_year = %s
				AND parent.to_year = %s
				AND parent.college = %s
				AND child.activity_link = %s
			""", (
				source.from_year,
				source.to_year,
				source.colleges,
				source_row.activity_link
			))[0][0]

			target_row.available_budget = (
				(source_row.approved_budget or 0) - existing_total
			)
			
	doc = get_mapped_doc(
		"Annual Work Plan",
		source_name,
		{
			"Annual Work Plan": {
				"doctype": "Approved Budget"
			},
			"APA Detail": {
				"doctype": "Approved Budget Item",
				# "field_map": {
				# 	"approved_budget": "available_budget"
				# },
				"field_no_map": {
					"approved_budget"
				}
			},
			"APA Detail Extra": {
				"doctype": "Approved Budget Extra Item",
				# "field_map": {
				# 	"approved_budget": "available_budget"
				# },
				"field_no_map": {
					"approved_budget"
				}
			}
		},
		target_doc,
		# set_missing_values,
		ignore_permissions=True,
		postprocess=postprocess
	)

	return doc

def get_apply_reapply_actions(doctype, docname=None):
	"""
	Returns workflow actions 'Apply' and 'Re-Apply' available for a doc or doctype.
	"""
	actions = []

	workflow_name = frappe.db.get_value("Workflow", {"document_type": doctype}, "name")
	if not workflow_name:
		return actions

	transitions = frappe.get_all(
		"Workflow Transition",
		filters={"parent": workflow_name},
		fields=["action", "state", "next_state"]
	)

	current_state = None
	if docname:
		current_state = frappe.db.get_value(doctype, docname, "workflow_state")

	for t in transitions:
		if t["action"] in ["Apply", "Re-Apply"]:
			if current_state:
				if t["state"] == current_state:
					actions.append(t["action"])
			else:
				actions.append(t["action"])

	return actions