# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class PlanningOutput(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		from_date: DF.Date
		output: DF.SmallText | None
		rub_strategic_plan: DF.Link | None
		serial_number: DF.Int
		to_date: DF.Date

	def autoname(self):
		self.name = "Output("+str(getdate(self.from_date).year)+"-"+str(getdate(self.to_date).year)+") - "+str(self.serial_number_generation())

	def validate(self):
		self.serial_number = int(self.serial_number_generation())

	def serial_number_generation(self):
		max_serial = frappe.db.sql(
				"""SELECT MAX(serial_number) FROM `tabPlanning Output` where from_date = %s and to_date = %s and docstatus = 1""", (self.from_date, self.to_date),
				as_dict=False
			)[0][0]
		serial_number = (max_serial if max_serial else 0) + 1

		return serial_number

@frappe.whitelist()
def make_planning_project(name, from_date, to_date):
	po = frappe.new_doc("Planning Project")
	po.planning_output = name
	po.from_date = from_date
	po.to_date = to_date
	return po

