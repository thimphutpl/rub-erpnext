# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ApprovedBudgetItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activities: DF.SmallText | None
		activities_no: DF.Link | None
		activity_link: DF.Link | None
		approved_budget: DF.Currency
		output: DF.SmallText | None
		output_no: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.SmallText | None
		project_no: DF.Int
		reappropiation_received: DF.Currency
		reappropiation_sent: DF.Currency
		supplementary_received: DF.Currency
	# end: auto-generated types
	pass
