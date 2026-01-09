# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HostelMaintenanceReportItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Float
		asset: DF.Link | None
		asset_name: DF.Data | None
		conversion_factor: DF.Float
		expenses_type: DF.Literal["Asset", "Stock Item", "Others"]
		item_code: DF.Link | None
		item_name: DF.Data | None
		others: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		qty: DF.Int
		rate: DF.Int
		warehouse: DF.Link | None
	# end: auto-generated types
	pass
