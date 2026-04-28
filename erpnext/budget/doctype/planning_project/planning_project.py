# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class PlanningProject(Document):
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		from_date: DF.Date | None
		planning_output: DF.Link | None
		project: DF.SmallText | None
		serial_number: DF.Int
		to_date: DF.Date | None

	def autoname(self):
		self.name = "Project("+str(self.planning_output)+") - "+str(self.serial_number_generation())

	def validate(self):
		self.serial_number = int(self.serial_number_generation())

	def serial_number_generation(self):
		max_serial = frappe.db.sql(
				"""SELECT MAX(serial_number) FROM `tabPlanning Project` where from_date = %s and to_date = %s and planning_output = %s and docstatus = 1""", (self.from_date, self.to_date, self.planning_output),
				as_dict=False
			)[0][0]
		serial_number = (max_serial if max_serial else 0) + 1

		return serial_number
		
@frappe.whitelist()
def make_planning_activities(name, from_date, to_date, planning_output):
	po = frappe.new_doc("Planning Activities")
	po.project = name
	po.from_date = from_date
	po.to_date = to_date
	po.output = planning_output
	return po

