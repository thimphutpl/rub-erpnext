# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Club(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.club_action_plan_details.club_action_plan_details import ClubActionPlanDetails
		from erpnext.student_services.doctype.club_management_details.club_management_details import ClubManagementDetails
		from frappe.types import DF

		abbr: DF.Data | None
		club_activities: DF.Table[ClubActionPlanDetails]
		club_capacity: DF.Int
		club_management: DF.Table[ClubManagementDetails]
		club_name: DF.Data
		company: DF.Link
	# end: auto-generated types
	pass
