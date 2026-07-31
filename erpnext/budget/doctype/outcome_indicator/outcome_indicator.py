# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OutcomeIndicator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.outcome_indicator_item.outcome_indicator_item import OutcomeIndicatorItem
		from frappe.types import DF

		category: DF.Literal["", "Mandatory", "Developmental", "Survey"]
		data_collection_method: DF.Data | None
		data_source: DF.Data | None
		definition: DF.LongText | None
		disabled: DF.Check
		items: DF.Table[OutcomeIndicatorItem]
		outcome: DF.Data
		remarks: DF.LongText | None
		unit: DF.Link | None
		weightage: DF.Data | None
	# end: auto-generated types
	pass
