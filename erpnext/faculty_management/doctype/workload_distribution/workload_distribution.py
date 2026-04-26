# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.database.database import getdate
from frappe.model.document import Document
from datetime import datetime

class WorkloadDistribution(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		description: DF.Data | None
		duration: DF.Float
		end_date: DF.Date | None
		faculty_id: DF.Link | None
		faculty_name: DF.Data | None
		priority: DF.Literal["", "High", "Medium", "Low"]
		start_date: DF.Date | None
		status: DF.Literal["", "On Schedule", "Needs Attention"]
	# end: auto-generated types
	def validate(self):
		self.validate_from_to_dates()
		self.calculate_day_diff()
	def validate_from_to_dates(self):
		if self.start_date > self.end_date:
			frappe.throw("From Date cannot be after To Date")
	def calculate_day_diff(self):
		if self.start_date and self.end_date:
			start = getdate(self.start_date)
			end = getdate(self.end_date)
			self.duration = (end - start).days + 1
	
		
	
		

