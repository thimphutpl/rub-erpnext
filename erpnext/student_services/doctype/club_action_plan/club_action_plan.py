# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClubActionPlan(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.club_action_plan_details.club_action_plan_details import ClubActionPlanDetails
		from frappe.types import DF

		academic_session: DF.Data | None
		academic_term: DF.Link
		academic_year: DF.Data | None
		amended_from: DF.Link | None
		club_action_plan_details: DF.Table[ClubActionPlanDetails]
		club_action_plan_name: DF.Data
		club_name: DF.Link
		company: DF.Link
	# end: auto-generated types
	def validate(self):
		self.check_dublicate()

	def check_dublicate(self):
		exists=frappe.db.exists("Club Action Plan",
								{"company":self.company,
								"club_name":self.club_name,
								"academic_term":self.academic_term

								}
								)
		if exists:
			frappe.throw("Club Action Plan is already exists for " + str(self.academic_term))
