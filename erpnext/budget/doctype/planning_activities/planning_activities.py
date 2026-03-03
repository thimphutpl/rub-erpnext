# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PlanningActivities(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.output_category_item.output_category_item import OutputCategoryItem
		from frappe.types import DF

		activities: DF.SmallText | None
		amended_from: DF.Link | None
		from_date: DF.Date | None
		is_capital: DF.Check
		is_current: DF.Check
		items: DF.Table[OutputCategoryItem]
		project: DF.Link | None
		to_date: DF.Date | None
	# end: auto-generated types
	pass
