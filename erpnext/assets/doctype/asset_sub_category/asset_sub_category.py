# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetSubCategory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		asset_category: DF.Link
		asset_sub_category: DF.Data
		asset_sub_category_code: DF.Data | None
	# end: auto-generated types
	pass

	def validate(self):
		self.asset_sub_category_code_generation()

	def asset_sub_category_code_generation(self):
		last_code = frappe.db.get_value(
			"Asset Sub Category",
			{"asset_category": self.asset_category},
			"asset_sub_category_code",
			order_by="creation desc"
		)

		if last_code:
			next_number = int(last_code) + 1
		else:
			next_number = 1

		self.code = f"{next_number:02d}"

		self.asset_sub_category_code = f"{self.code}"