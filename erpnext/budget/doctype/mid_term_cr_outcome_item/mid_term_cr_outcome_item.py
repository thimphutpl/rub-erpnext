# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MidTermCROutcomeItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		drop_activity: DF.Check
		is_new_activity: DF.Check
		justification: DF.SmallText | None
		outcome: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
		target: DF.Data | None
		unit: DF.Link | None
		weightage: DF.Data | None
	# end: auto-generated types
	pass
