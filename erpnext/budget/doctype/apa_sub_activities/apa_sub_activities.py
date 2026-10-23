# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.model.naming import make_autoname

class APASubActivities(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_category_item.output_category_item import OutputCategoryItem
		from frappe.types import DF

		activity: DF.Link
		amended_from: DF.Link | None
		college: DF.Link
		department: DF.Link | None
		disabled: DF.Check
		from_year: DF.Link
		is_not_range: DF.Check
		items: DF.Table[OutputCategoryItem]
		sub_activity: DF.Link
		to_year: DF.Link
		unit: DF.Link
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"Sub-Activity/{college_abbr}/{self.from_year}-{self.to_year}/.####")

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_planning_activities(doctype, txt, searchfield, start, page_len, filters):

	college = filters.get("college")
	from_year = filters.get("from_year")
	to_year = filters.get("to_year")
	department = filters.get("department")
	ovc_condition = (college != "Office of Vice Chancellor") or (college == "Office of Vice Chancellor" and department)

	if not college or not from_year or not to_year or not ovc_condition:
		return []

	return frappe.db.sql(
		"""
		SELECT
			pa.name,
			pa.activities
		FROM `tabPlanning Activities` pa
		WHERE
			%(from_year)s >= YEAR(pa.from_date) and %(to_year)s <= YEAR(pa.to_date) and
			pa.activities LIKE %(txt)s
			AND NOT EXISTS (
				SELECT 1
				FROM `tabIgnore PA For College` ipc
				WHERE
					ipc.parent = pa.name
					AND ipc.parenttype = 'Planning Activities'
					AND ipc.college = %(college)s
					AND (
						%(college)s != 'Office of Vice Chancellor'
						OR ipc.department = %(department)s
					)
			)
		ORDER BY pa.name
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"txt": f"%{txt}%",
			"college": college,
			"from_year": from_year,
			"to_year": to_year,
			"department": department,
			"start": start,
			"page_len": page_len,
		},
	)