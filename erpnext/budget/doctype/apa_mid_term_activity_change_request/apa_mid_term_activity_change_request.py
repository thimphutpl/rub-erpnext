# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.model.naming import make_autoname

class APAMidTermActivityChangeRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.mid_term_cr_outcome_item.mid_term_cr_outcome_item import MidTermCROutcomeItem
		from erpnext.budget.doctype.mid_term_cr_output_extra_item.mid_term_cr_output_extra_item import MidTermCROutputExtraItem
		from erpnext.budget.doctype.mid_term_cr_output_item.mid_term_cr_output_item import MidTermCROutputItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		department: DF.Link | None
		from_year: DF.Link
		outcome_items: DF.Table[MidTermCROutcomeItem]
		output_extra_items: DF.Table[MidTermCROutputExtraItem]
		output_items: DF.Table[MidTermCROutputItem]
		to_year: DF.Link
	# end: auto-generated types
	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"Mid Term Review CR/{college_abbr}/{self.from_year}-{self.to_year}")

	# def validate(self):
	# 	self.check_mid_term_review_exists()

	# def check_mid_term_review_exists(self):
	# 	if frappe.db.exists("APA Mid Term Review CR", {
	# 		"from_year": self.from_year,
	# 		"to_year": self.to_year,
	# 		"college": self.college,
	# 	}):
	# 		frappe.throw("APA Mid Term Change Review completed for college: <b>{0}</b> from year: <b>{1}</b> to <b>{2}</b>".format(self.from_year, self.to_year, self.college))

@frappe.whitelist()
def get_target_setup_details(from_year, to_year, college, department = None):
	ovc_condition = (college != "Office of Vice Chancellor") or (college == "Office of Vice Chancellor" and department)
	if not from_year or not to_year or not college or not ovc_condition:
		frappe.throw("Select From Year, To Year and College and if OVC select Department")

	conditions = ""
	values = [from_year, to_year, college]

	if college == "Office of Vice Chancellor":
		conditions = " AND ats.department = %s"
		values.append(department)

	output = frappe.db.sql(f'''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.activity_link,
			atoi.sub_activity_no,
			atoi.sub_activity,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.weightage,
			atoi.unit,
			atoi.target,
			atoi.justification,
			atoi.activities_no
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Target Output Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s AND ats.docstatus = 1 {conditions}
		ORDER BY atoi.idx
	''',tuple(values), as_dict=True)

	if not output:
		frappe.throw("No Output Target Setup found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	output_extra = frappe.db.sql(f'''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.sub_activity,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.activity_link,
			atoi.weightage,
			atoi.unit,
			atoi.target,
			atoi.justification,
			atoi.sub_activity_link
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Output Extra Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s and ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s AND ats.docstatus = 1 {conditions}
		ORDER BY atoi.idx
	''',tuple(values), as_dict=True)

	ignore_colleges = frappe.db.sql("""
		SELECT
			college
		FROM `tabIgnore APA Outcome`
		WHERE parent = 'APA Settings'
	""", as_dict=True)
	
	outcome = None
	if college not in [d["college"] for d in ignore_colleges]:
		outcome = frappe.db.sql('''
			SELECT  
				atoi.outcome,
				atoi.unit,
				atoi.target,
				atoi.justification
			FROM `tabAPA Target Setup` ats
			INNER JOIN `tabAPA Target Outcome Item` atoi ON ats.name = atoi.parent
			WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s AND ats.docstatus = 1
			ORDER BY atoi.idx
		''',(from_year, to_year, college), as_dict=True)

		if not outcome:
			frappe.throw("No Outcome Target Setup found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	return {
		"output": output,
		"output_extra": output_extra,
		"outcome": outcome,
		"ignore_colleges": ignore_colleges,
	}

@frappe.whitelist()
def get_output_unit(from_year, to_year, college, activity_link, sub_activity_no = None):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year and To Year and College")
	unit = None
	if sub_activity_no:
		unit = frappe.db.get_value("APA Sub Activities", {"from_year": from_year, "to_year": to_year, "college": college, "disabled": 0, "activity": activity_link, "name": sub_activity_no}, "unit")
		if not unit:
			frappe.throw("No Unit under Activity <b>{0}</b> found from year <b>{1}</b> to <b>{2}</b> for <b>{3}</b>".format(sub_activity_no, from_year, to_year, college))
	else:
		unit = frappe.db.get_value("Planning Activities Target Setup", {"from_year": from_year, "to_year": to_year, "college": college, "disabled": 0, "activities": activity_link}, "unit")
		if not unit:
			frappe.throw("No Unit under Major Activity <b>{0}</b> found from year <b>{1}</b> to <b>{2}</b> for <b>{3}</b>".format(activity_link, from_year, to_year, college))

	return unit

@frappe.whitelist()
def get_output_extra_unit(from_year, to_year, college, activity_link, sub_activity_link = None):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year and To Year and College")
	unit = None
	if sub_activity_link:
		unit = frappe.db.get_value("Additional Sub Activities", {"from_year": from_year, "to_year": to_year, "college": college, "disabled": 0, "activity": activity_link, "name": sub_activity_link}, "unit")
		if not unit:
			frappe.throw("No Unit under Additional Activity <b>{0}</b> found from year <b>{1}</b> to <b>{2}</b> for <b>{3}</b>".format(sub_activity_link, from_year, to_year, college))
	else:
		unit = frappe.db.get_value("Additional Activities", {"from_year": from_year, "to_year": to_year, "college": college, "disabled": 0, "name": activity_link}, "unit")
		if not unit:
			frappe.throw("No Unit under Additional Major Activity <b>{0}</b> found from year <b>{1}</b> to <b>{2}</b> for <b>{3}</b>".format(activity_link, from_year, to_year, college))

	return unit

@frappe.whitelist()
def get_outcome_unit(from_year, to_year, college, outcome):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year and To Year and College")
	unit = frappe.db.get_value("Outcome Target Setup", {"from_year": from_year, "to_year": to_year, "college": college, "disabled": 0, "outcome": outcome}, "unit")
	if not unit:
		frappe.throw("No Unit under Outcome <b>{0}</b> found from year <b>{1}</b> to <b>{2}</b> for <b>{3}</b>".format(outcome, from_year, to_year, college))

	return unit
