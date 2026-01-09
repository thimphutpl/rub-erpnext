# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StudentLeaveApplication(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		approved_by_sso: DF.Check
		approver: DF.Link | None
		approver_designation: DF.Link | None
		approver_name: DF.Data | None
		attach_zqhy: DF.Attach
		college: DF.Link
		from_date: DF.Date
		leave_type: DF.Link
		programme: DF.Link
		reason: DF.Text | None
		reason_for_late_rejoining: DF.SmallText | None
		rejoining_date: DF.Date | None
		student: DF.Link
		student_name: DF.ReadOnly | None
		to_date: DF.Date
		total_leave_days: DF.Float
	# end: auto-generated types
	pass
