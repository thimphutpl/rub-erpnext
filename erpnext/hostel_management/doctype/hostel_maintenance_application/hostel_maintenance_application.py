# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class HostelMaintenanceApplication(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.hostel_asset_maintenance.hostel_asset_maintenance import HostelAssetMaintenance
		from erpnext.hostel_management.doctype.hostel_check_out_item.hostel_check_out_item import HostelCheckOutItem
		from frappe.types import DF

		amended_from: DF.Link | None
		applied_by: DF.Link
		assets: DF.Table[HostelAssetMaintenance]
		attach_picture: DF.AttachImage | None
		available_time: DF.Time | None
		branch: DF.Link | None
		check_out_list: DF.Table[HostelCheckOutItem]
		college: DF.Link
		cost_center: DF.Link | None
		damage_type: DF.Literal["Vandalism", "Loss or Misuse of Property", "Damage to Shared Facilities"]
		description_of_maintenance: DF.SmallText | None
		first_name: DF.Data | None
		fiscal_year: DF.Link
		focal_type: DF.Literal["", "Plumber", "Electrician", "Mason", "Carpenter"]
		full_name: DF.Data | None
		hostel_check_in_form: DF.Link | None
		hostel_check_out_form: DF.Link | None
		hostel_maintenance_report: DF.Data | None
		hostel_room: DF.Link | None
		hostel_type: DF.Data
		last_name: DF.Data | None
		maintenance_focal: DF.Link | None
		maintenance_required_on: DF.Date | None
		maintenance_type: DF.Literal["Repair", "Replacement"]
		phone_number: DF.Data | None
		posting_date: DF.Date
	# end: auto-generated types

	def validate(self):
		self.set_maintenance_focal_from_college()

		if not self.maintenance_focal:
			frappe.throw("Please Assign Maintenace focal in Company under hostel")
		
	def set_maintenance_focal_from_college(self):
		"""Auto-set maintenance_focal based on focal_type from the college"""
		if self.focal_type and self.college:
			# Map focal_type to the corresponding field in Company doctype
			focal_field_map = {
				"Plumber": "plumber",
				"Electrician": "electrician",
				"Mason": "mason",
				"Carpenter": "carpenter"
			}
			
			focal_field = focal_field_map.get(self.focal_type)
			
			if focal_field:
				# Get the employee from the company
				company_focal = frappe.db.get_value("Company", self.college, focal_field)
				
				if company_focal:
					self.maintenance_focal = company_focal
				else:
					frappe.msgprint(_("No {0} assigned to {1}. Please assign one in Company master.").format(
						self.focal_type, self.college
					), alert=True, indicator='orange')
			else:
				# Clear maintenance_focal if focal_type is invalid
				self.maintenance_focal = None	
	def on_cancel(self):
		# Ver 2.0.190509, Following method added by SHIV on 2019/05/20
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Hostel Maintenance Report",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)
		# docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		# if docstatus and docstatus != 2:
		# 	frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")

		# self.db_set("jv", None)

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
					"college": "company",
					"applied_by": "student_code",
					"full_name": "full_name",
					"name": "hostel_maintenance_application"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Hostel Asset Maintenance": {
				"doctype": "Hostel Maintenance Item",
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc	

@frappe.whitelist()
def get_asset_rate(asset):
	# Fetch Item Price for given Asset (Item)
	price = frappe.db.get_value("Item Price", {"item_code": asset}, "price_list_rate")
	return price or 0

@frappe.whitelist()
def get_hostel_room_by_student(applied_by):
	# frappe.throw("hhh")
	room = frappe.db.sql("""
		SELECT parent 
		FROM `tabStudent List Item`
		WHERE student_code = %s
		LIMIT 1
	""", applied_by)
	return room[0][0] if room else None

@frappe.whitelist()
def get_hostel_checkin_form(applied_by, fiscal_year):
	result = frappe.db.sql("""
		SELECT hci.name
		FROM `tabHostel Check-In Form` hci
		INNER JOIN `tabCheck-In Students Items` cisi
			ON cisi.parent = hci.name
		WHERE cisi.student_code = %s
		AND hci.fiscal_year = %s
		AND hci.docstatus = 1
		LIMIT 1
	""", (applied_by, fiscal_year), as_dict=True)

	return result[0].name if result else None 	
	
def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	user_roles = frappe.get_roles(user)
	if "SSO" in user_roles or "Administrator" in user_roles:
		return         

	student = frappe.db.get_value(
		"Student",
		{"user": user},
		"name"
	)

	if student:
		return f"`tabHostel Maintenance Application`.applied_by = '{student}'"

	return "" 


@frappe.whitelist()
def get_company_focal_persons(company):
    """Get all focal persons assigned to a company"""
    if not company:
        return {}
    
    focal_persons = frappe.db.get_value(
        "Company",
        company,
        ["plumber", "electrician", "mason", "carpenter"],
        as_dict=True
    )
    
    return focal_persons or {}