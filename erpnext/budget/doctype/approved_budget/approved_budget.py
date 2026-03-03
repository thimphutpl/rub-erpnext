# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ApprovedBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.approved_budget_item.approved_budget_item import ApprovedBudgetItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		fiscal_year: DF.Link
		items: DF.Table[ApprovedBudgetItem]
	# end: auto-generated types
	pass
