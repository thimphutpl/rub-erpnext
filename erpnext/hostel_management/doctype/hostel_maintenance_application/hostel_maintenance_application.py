# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class HostelMaintenanceApplication(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.hostel_asset_maintenance.hostel_asset_maintenance import HostelAssetMaintenance
		from frappe.types import DF

		amended_from: DF.Link | None
		applied_by: DF.Link | None
		assets: DF.Table[HostelAssetMaintenance]
		branch: DF.Link | None
		college: DF.Link | None
		cost_center: DF.Link | None
		description_of_maintenance: DF.SmallText | None
		first_name: DF.Data | None
		hostel_room: DF.Link | None
		hostel_type: DF.Data | None
		last_name: DF.Data | None
		maintenance_required_on: DF.Date | None
		maintenance_type: DF.Literal["Repair", "Replacement"]
		phone_number: DF.Data | None
	# end: auto-generated types
	pass

@frappe.whitelist()
def make_maintenance_application(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Hostel Maintenance Application", source_name, {
			"Hostel Maintenance Application": {
				"doctype": "Hostel Maintenance Report",
				"field_map": {
					"name": "hostel_maintenance_report",
					"posting_date": "ta_date",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Hostel Asset Maintenance": {
				"doctype": "Hostel Maintenance Expenses Item",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc	
