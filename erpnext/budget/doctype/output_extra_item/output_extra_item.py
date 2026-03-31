# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class OutputExtraItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activities: DF.SmallText
		activity_link: DF.Link
		output: DF.SmallText | None
		output_no: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.SmallText | None
		project_no: DF.Link
		sub_activity: DF.SmallText | None
		sub_activity_link: DF.Link | None
		unit: DF.Link | None
		weightage: DF.Data | None
	# end: auto-generated types
	pass
