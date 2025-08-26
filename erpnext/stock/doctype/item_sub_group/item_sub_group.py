# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ItemSubGroup(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		asset_category: DF.Link | None
		asset_sub_category: DF.Link | None
		company: DF.Link | None
		disabled: DF.Check
		expense_head: DF.Link | None
		item_code_base: DF.Data | None
		item_group: DF.Link
		item_sub_group: DF.Data
	# end: auto-generated types
	pass
