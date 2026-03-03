# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PlanningOutput(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		from_date: DF.Date | None
		output: DF.SmallText | None
		rub_strategic_plan: DF.Link | None
		serial_number: DF.Int
		to_date: DF.Date | None
	# end: auto-generated types
	pass

	def validate(self):
		self.check_serial_number()

	def check_serial_number(self):
		serials = frappe.get_all(
			"Planning Output",
			filters={
				"from_date": [">=", self.from_date],
				"to_date": ["<=", self.to_date],
				"docstatus": 1
			},
			pluck="serial_number"
		)
		if self.serial_number in serials:
			frappe.throw(_("Serial Number: {0} exists for date between {1} and {2}".format(self.serial_number, self.from_date, self.to_date)))

@frappe.whitelist()
def make_planning_project(name, from_date, to_date):
	po = frappe.new_doc("Planning Project")
	po.planning_output = name
	po.from_date = from_date
	po.to_date = to_date
	max_serial = frappe.db.sql(
		"""SELECT MAX(serial_number) FROM `tabPlanning Project` where from_date >= %s and to_date <= %s and docstatus = 1""", (from_date, to_date),
		as_dict=False
	)[0][0]

	po.serial_number = (max_serial if max_serial else 0) + 1

	# po.serial_number = max_serial + 1
	return po

