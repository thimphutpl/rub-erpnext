# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class InterpolationFormula(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		apa_max: DF.Float
		apa_min: DF.Float
		category: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		pms_max: DF.Float
		pms_min: DF.Float
	# end: auto-generated types
	pass
