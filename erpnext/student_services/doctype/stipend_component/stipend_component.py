# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StipendComponent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		component: DF.Data
		component_type: DF.Literal["Earning", "Deduction"]
		default_amount: DF.Currency
		description: DF.SmallText | None
		field_name: DF.Data | None
		payment_method: DF.Literal["Lumpsum", "Percent"]
		stipend_component_details: DF.Table[Document]
	# end: auto-generated types
	pass
