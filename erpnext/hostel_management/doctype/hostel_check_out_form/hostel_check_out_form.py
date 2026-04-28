# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class HostelCheckOutForm(Document):
	def validate(self):
		self.validate_assets_exist()
		self.validate_posting_date_within_fiscal_year()
		self.validate_duplicate_check_in()

	def validate_assets_exist(self):
		"""Validate that checked-in assets exist for this student"""
		if self.student and self.fiscal_year:
			assets = frappe.db.exists("Check-In Asset Items", {
				"student": self.student,
				"parenttype": "Hostel Check-In Form",
				"docstatus": 1
			})
			
			if not assets:
				frappe.throw(_("No checked-in assets found for student {0} in any check-in form").format(
					self.student
				))

	def validate_posting_date_within_fiscal_year(self):
		"""Validate that posting_date falls within the selected fiscal year"""
		if not self.posting_date or not self.fiscal_year:
			return
		
		# Convert posting_date string to date object
		posting_date_obj = getdate(self.posting_date)
		
		# Get fiscal year dates
		fiscal_year_doc = frappe.get_cached_doc("Fiscal Year", self.fiscal_year)
		year_start_date = fiscal_year_doc.year_start_date
		year_end_date = fiscal_year_doc.year_end_date
		
		# Check if posting_date is within fiscal year
		if posting_date_obj < year_start_date or posting_date_obj > year_end_date:
			frappe.throw(_("Posting Date {0} is not within Fiscal Year {1} ({2} to {3})").format(
				frappe.bold(frappe.utils.format_date(self.posting_date)),
				frappe.bold(self.fiscal_year),
				frappe.bold(frappe.utils.format_date(year_start_date)),
				frappe.bold(frappe.utils.format_date(year_end_date))
			)) 

	def validate_duplicate_check_in(self):
		"""Validate that student doesn't have multiple check-ins for the same fiscal year"""
		if not self.student or not self.fiscal_year:
			return
		
		# Check if there's already a submitted check-in for this student and fiscal year
		existing_check_in = frappe.db.exists(
			"Hostel Check-Out Form",
			{
				"student": self.student,
				"fiscal_year": self.fiscal_year,
				"name": ["!=", self.name],  # Exclude current document
				"docstatus": 1  # Only submitted documents
			}
		)
		
		if existing_check_in:
			frappe.throw(_("Student {0} already has a Hostel Check-Out for fiscal year {1}. Multiple check-outs are not allowed for the same fiscal year.").format(
				frappe.bold(self.student),
				frappe.bold(self.fiscal_year)
			))			             

@frappe.whitelist()
def get_student_assets_from_check_in(student, fiscal_year):
	"""
	Fetch assets from Check-In Asset Items child table for a specific student and fiscal year
	
	Args:
		student (str): Student ID
		fiscal_year (str): Fiscal Year name
	
	Returns:
		list: List of assets where student matches
	"""
	if not student or not fiscal_year:
		return []
	
	# Get all Hostel Check-In Forms for the fiscal year
	check_in_forms = frappe.db.get_all(
		"Hostel Check-In Form",
		filters={
			"fiscal_year": fiscal_year,
			"student": student,
			"docstatus": 1  # Only submitted check-ins
		},
		pluck="name"
	)
	
	if not check_in_forms:
		return [] 
	
	# Fetch all asset items where student matches from those check-in forms
	assets = frappe.get_all(
		"Check-In Asset Items",  # Your child table doctype name
		filters={
			"parent": ["in", check_in_forms],
			"parenttype": "Hostel Check-In Form",
			"student": student
		},
		fields=[
			"name",
			"asset_code",
			"asset_name",
			"remarks",
			"parent as check_in_form",
			"student",
			"asset_condition",
		],
		order_by="student desc"
	)
	
	# Optional: Mark if any asset is already checked out
	for asset in assets:
		# Check if this asset is already checked out
		is_checked_out = frappe.db.exists("Check-Out Asset Items", {
			"check_in_asset_item": asset.name,
			"parenttype": "Hostel Check-Out Form",
			"docstatus": 1
		})
		asset.is_checked_out = bool(is_checked_out)
	
	return assets

@frappe.whitelist()
def get_student_check_in_summary(student, fiscal_year):
	"""
	Get summary of student's check-in including check-in form details
	"""
	if not student or not fiscal_year:
		return None
	
	# Get all check-in forms for this student in the fiscal year
	check_ins = frappe.db.get_all(
		"Hostel Check-In Form",
		filters={
			"fiscal_year": fiscal_year,
			"docstatus": 1
		},
		fields=["name", "hostel_room", "check_in_date", "company", "hostel_type"]
	)
	
	result = []
	for check_in in check_ins:
		# Get assets for this check-in
		assets = frappe.get_all(
			"Check-In Asset Items",
			filters={
				"parent": check_in.name,
				"student": student
			},
			fields=["asset_code", "asset_name",]
		)
		
		check_in.asset_count = len(assets)
		result.append(check_in)
	
	return result

def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	# Get student linked to user
	student = frappe.db.get_value(
		"Student",
		{"user": user},
		"name"
	)

	if not student:
		return ""

	return f"""
		EXISTS (
			SELECT 1 FROM `tabCheck-Out Student Details` hai
			WHERE hai.parent = `tabHostel Check-Out Form`.name
			AND hai.student_code = '{student}'
		)
	""" 

@frappe.whitelist()
def validate_posting_date(posting_date, fiscal_year):
	"""
	Validate if posting_date falls within fiscal_year
	Returns dict with validation result and date ranges
	"""
	if not posting_date or not fiscal_year:
		return {
			"is_valid": False,
			"message": _("Posting Date and Fiscal Year are required")
		}
	
	try:
		# Get fiscal year dates
		fiscal_year_doc = frappe.get_cached_doc("Fiscal Year", fiscal_year)
		year_start_date = fiscal_year_doc.year_start_date
		year_end_date = fiscal_year_doc.year_end_date
		
		# Convert posting_date to date if it's string
		from frappe.utils import getdate
		posting_date_obj = getdate(posting_date)
		
		# Check if within range
		is_valid = year_start_date <= posting_date_obj <= year_end_date
		
		return {
			"is_valid": is_valid,
			"year_start_date": frappe.utils.format_date(year_start_date),
			"year_end_date": frappe.utils.format_date(year_end_date),
			"message": _("Posting Date should be between {0} and {1}").format(
				frappe.utils.format_date(year_start_date),
				frappe.utils.format_date(year_end_date)
			) if not is_valid else ""
		}
	
	except Exception as e:
		frappe.log_error(f"Error validating posting date: {str(e)}", "Hostel Check-In Validation")
		return {
			"is_valid": False,
			"message": _("Error validating date. Please check Fiscal Year configuration.")
		}    