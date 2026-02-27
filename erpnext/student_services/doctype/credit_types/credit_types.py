# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CreditTypes(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.credit_type.credit_type import CreditType
		from frappe.types import DF

		college: DF.Table[CreditType]
	# end: auto-generated types
	pass
