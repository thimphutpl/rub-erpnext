# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class APAOutcomeItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category: DF.Data | None
		irt_rating: DF.Percent
		justification: DF.SmallText | None
		means_of_verification: DF.Data | None
		outcome: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		raw_rating: DF.Data | None
		remarks: DF.SmallText | None
		self_rating: DF.Data | None
		target: DF.Data | None
		unit: DF.Link | None
		weightage: DF.Percent
	# end: auto-generated types
	pass
