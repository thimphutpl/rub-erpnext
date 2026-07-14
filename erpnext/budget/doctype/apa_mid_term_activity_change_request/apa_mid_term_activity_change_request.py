# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class APAMidTermActivityChangeRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activity_name: DF.DynamicLink
		activity_type: DF.Literal["Planning Activities", "Additional Activities"]
		add_drop: DF.Literal["", "Add", "Drop"]
		amended_from: DF.Link | None
		college: DF.Link
		from_year: DF.Link
		to_year: DF.Link
	# end: auto-generated types
	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"Mid Term Review/{college_abbr}/{self.from_year}-{self.to_year}")

	def validate(self):
		self.check_mid_term_review_exists()

	def check_mid_term_review_exists(self):
		if frappe.db.exists("APA Mid Term Review", {
			"from_year": self.from_year,
			"to_year": self.to_year,
			"college": self.college,
		}):
			frappe.throw("APA Mid Term Review completed for college: <b>{0}</b> from year: <b>{1}</b> to <b>{2}</b>".format(self.from_year, self.to_year, self.college))

@frappe.whitelist()
def get_target_setup_details(from_year, to_year, college):
	if not from_year or not to_year or not college:
		frappe.throw("Select From Year and To Year and College")
	output = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no, d
			atoi.activity_link,
			atoi.sub_activity_no,
			atoi.sub_activity,
			atoi.unit,
			atoi.weightage,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.activities_no,
			atoi.target,
			atoi.justification
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Target Output Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s AND ats.docstatus = 1
		ORDER BY atoi.idx
	''',(from_year, to_year, college), as_dict=True)

	if not output:
		frappe.throw("No Output Target Setup found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	output_extra = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.sub_activity,
			atoi.unit,
			atoi.weightage,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.activity_link,
			atoi.sub_activity_link,
			atoi.target,
			atoi.justification
		FROM `tabAPA Target Setup` ats
		INNER JOIN `tabAPA Output Extra Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s and ats.to_year = %s AND atoi.parenttype = "APA Target Setup" AND ats.college = %s AND ats.docstatus = 1
		ORDER BY atoi.idx
	''',(from_year, to_year, college), as_dict=True)

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
				atoi.weightage,
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