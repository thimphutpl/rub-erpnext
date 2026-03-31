# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class APATargetOutputItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activities: DF.SmallText | None
		activities_no: DF.Link | None
		activity_link: DF.Link | None
		justification: DF.SmallText | None
		output: DF.SmallText | None
		output_no: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		project: DF.SmallText | None
		project_no: DF.Int
		sub_activity: DF.SmallText | None
		sub_activity_no: DF.Link | None
		target: DF.Data | None
		unit: DF.Link | None
		weightage: DF.Percent
	# end: auto-generated types
	pass
