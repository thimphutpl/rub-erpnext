# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OutputCategoryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category: DF.Link | None
		max: DF.Float
		min: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		raw_rating: DF.Data | None
		unit: DF.Data | None
	# end: auto-generated types
	pass
