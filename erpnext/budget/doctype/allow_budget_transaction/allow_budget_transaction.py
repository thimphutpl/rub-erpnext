# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.naming import make_autoname
from frappe.utils import getdate, today

class AllowBudgetTransaction(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		from_date: DF.Date
		to_date: DF.Date
		transaction_type: DF.Literal["", "Five Year Plan Proposal", "Annual Work Plan"]
	
	def autoname(self):
		abbr = frappe.db.get_value("Company", self.college, "abbr")
		self.name = make_autoname(
			f"AT/{abbr}/{getdate(self.from_date).year}-{getdate(self.to_date).year}/.##"
		)	

	# def validate(self):
	# 	self.validate_date()
	
	# def validate_date(self):
	# 	result = frappe.db.get_value(
	# 		"Allow Budget Transaction",
	# 		{"college": self.college, "from_date": self.from_date, "to_date": self.to_date, "transaction_type": self.transaction_type},
	# 		"name",
	# 	)
	# 	if result:
	# 		frappe.throw("Transaction exists with same parameter for college <b>{0}</b> (Transaction No: {1})".format(self.college, result))

