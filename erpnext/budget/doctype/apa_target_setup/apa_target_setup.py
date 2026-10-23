# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import add_days, nowdate

class APATargetSetup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.apa_output_extra_item.apa_output_extra_item import APAOutputExtraItem
		from erpnext.budget.doctype.apa_target_outcome_item.apa_target_outcome_item import APATargetOutcomeItem
		from erpnext.budget.doctype.apa_target_output_item.apa_target_output_item import APATargetOutputItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		department: DF.Link | None
		from_year: DF.Link
		outcome_items: DF.Table[APATargetOutcomeItem]
		output_extra_items: DF.Table[APAOutputExtraItem]
		output_items: DF.Table[APATargetOutputItem]
		to_year: DF.Link
	# end: auto-generated types
	pass

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"APA Target Setup/{college_abbr}/{self.from_year}-{self.to_year}/.##")

@frappe.whitelist()
def fetch_output_and_outcome(from_year, to_year, college, department):
	ovc_condition = (college != "Office of Vice Chancellor") or (college == "Office of Vice Chancellor" and department)
		# if(from_year && to_year && college && ovc_condition){
	if not from_year or not to_year or not college or not ovc_condition:
		frappe.throw("Select From Year, To Year and College and if OVC select Department")

	conditions = ""
	values = [from_year, to_year, college]

	if college == "Office of Vice Chancellor":
		conditions = " AND oi.department = %s"
		values.append(department)

	output = frappe.db.sql(f'''
		SELECT  
			oii.output_no,
			oii.project_no,
			oii.activity_link,
			oii.sub_activity_no,
			oii.unit,
			oii.weightage,
			oii.output,
			oii.project,
			oii.activities,
			oii.sub_activity
		FROM `tabOutput Indicator` oi 
		INNER JOIN `tabOutput Indicator Item` oii ON oi.name = oii.parent
		WHERE oi.from_year = %s and oi.to_year = %s and oi.college = %s {conditions}
		ORDER BY oii.idx ASC
	''',tuple(values), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))\

	output_extra = frappe.db.sql(f'''
		SELECT  
			oii.output_no,
			oii.project_no,
			oii.unit,
			oii.weightage,
			oii.output,
			oii.project,
			oii.activities,
			oii.activity_link,
			oii.sub_activity_link,
			oii.sub_activity
		FROM `tabOutput Indicator` oi 
		INNER JOIN `tabOutput Extra Item` oii ON oi.name = oii.parent
		WHERE oi.from_year = %s and oi.to_year = %s and oi.college = %s {conditions}
		ORDER BY oii.idx ASC
	''',tuple(values), as_dict=True)

	ignore_colleges = frappe.db.sql("""
		SELECT
			college
		FROM `tabIgnore APA Outcome`
		WHERE parent = 'APA Settings'
	""", as_dict=True)
	# frappe.throw(str(ignore_colleges))
	outcome = None
	if college not in [d["college"] for d in ignore_colleges]:
		outcome = frappe.db.sql('''
			SELECT  
				ots.unit,
				oi.outcome
			FROM `tabOutcome Indicator` oi
			LEFT JOIN `tabOutcome Target Setup` ots
			ON oi.name = ots.outcome
			WHERE (oi.disabled = 0 OR ots.disabled = 0) AND ots.from_year = %s AND ots.to_year = %s AND ots.college = %s
		''', (from_year, to_year, college), as_dict=True)

		if not outcome:
			frappe.throw("No Outcome Indicator found")

	return {
		"output": output,
		"output_extra": output_extra,
		"outcome": outcome,
		"ignore_colleges": ignore_colleges,
	}

@frappe.whitelist()
def get_activity_weightage(from_year, to_year, college, activity_link, sub_activity_no = None):
	if not activity_link:
		return

	if sub_activity_no:
		output_category_items = frappe.db.sql("""
			SELECT  
				oci.category,
				oci.max,
				oci.min,
				oci.unit as grade,
				oci.raw_rating as score
			FROM `tabAPA Sub Activities` asa
			INNER JOIN `tabOutput Category Item` oci
			ON asa.name = oci.parent
			WHERE asa.from_year = %s AND asa.to_year = %s AND asa.college = %s AND asa.sub_activity = %s 
			ORDER BY oci.idx ASC
		""", (from_year, to_year, college, sub_activity_no), as_dict=True)

		return output_category_items
	else:
		output_category_items = frappe.db.sql("""
			SELECT  
				oci.category,
				oci.max,
				oci.min,
				oci.unit as grade,
				oci.raw_rating as score
			FROM `tabPlanning Activities Target Setup` pats
			INNER JOIN `tabOutput Category Item` oci
			ON pats.name = oci.parent
			WHERE pats.from_year = %s AND pats.to_year = %s AND pats.college = %s AND pats.activities = %s
			ORDER BY oci.idx ASC
		""", (from_year, to_year, college, activity_link), as_dict=True)

		return output_category_items

# def send_expiry_alerts():
#     today = nowdate()
#     # define reminder windows
#     target_dates = [
#         add_days(today, 1),
#         add_days(today, 2)
#     ]
#     docs = frappe.get_all(
#         "APA Calender",
#         filters={
#             "expiry_date": ["in", target_dates],
#             "docstatus": ["!=", 2]  # ignore cancelled
#         },
#         fields=["name", "expiry_date", "owner"]
#     )

#     for d in docs:
#         # Prevent duplicate sending (optional but important)
#         if not already_sent(d.name, d.expiry_date):
#             frappe.sendmail(
#                 recipients=[d.owner],
#                 subject="Expiry Reminder",
#                 message=f"""
#                 Document <b>{d.name}</b> is expiring on <b>{d.expiry_date}</b>.
#                 """
#             )

#             mark_as_sent(d.name, d.expiry_date)