# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from frappe.model.document import Document


class DepreciationSchedule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		accumulated_depreciation_amount: DF.Currency
		depreciation_amount: DF.Currency
		income_accumulated_depreciation: DF.Currency
		income_depreciation_amount: DF.Currency
		journal_entry: DF.Link | None
		no_of_days_in_a_schedule: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		schedule_date: DF.Date
		schedule_start_date: DF.Date | None
		shift: DF.Link | None
	# end: auto-generated types

	pass
