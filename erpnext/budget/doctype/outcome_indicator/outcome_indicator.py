# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OutcomeIndicator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		category: DF.Data | None
		data_collection_method: DF.Data | None
		data_source: DF.Data | None
		definition: DF.SmallText | None
		disabled: DF.Check
		items: DF.Table[Document]
		outcome: DF.Data | None
		remarks: DF.SmallText | None
		unit: DF.Data | None
		weightage: DF.Data | None
	# end: auto-generated types
	pass
