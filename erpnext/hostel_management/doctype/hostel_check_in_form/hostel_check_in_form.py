# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import getdate

class HostelCheckInForm(Document):
	def validate(self):
		self.validate_company_before_hostel_room()
		self.validate_posting_date_within_fiscal_year()
		self.validate_duplicate_check_in()

	def validate_company_before_hostel_room(self):
		"""Validate that hostel_room cannot be selected without company"""
		if self.hostel_room and not self.company:
			frappe.throw(_("Please select a College first before selecting Hostel Room"))

		if self.hostel_room and self.company:
			# Get the company from the selected Hostel Room
			room_company = frappe.db.get_value("Hostel Room", self.hostel_room, "company")
			
			if room_company and room_company != self.company:
				frappe.throw(_("Hostel Room {0} belongs to {1}, but you have selected {2}. Please select a Hostel Room from the correct College.").format(
					frappe.bold(self.hostel_room),
					frappe.bold(room_company),
					frappe.bold(self.company)
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
		if not self.hostel_room or not self.fiscal_year:
			return
		
		# Check if there's already a submitted check-in for this student and fiscal year
		existing_check_in = frappe.db.exists(
			"Hostel Check-In Form",
			{
				"hostel_room": self.hostel_room,
				"fiscal_year": self.fiscal_year,
				"name": ["!=", self.name],  # Exclude current document
				"docstatus": 1  # Only submitted documents
			}
		)
		
		if existing_check_in:
			frappe.throw(_("Student {0} already has a Hostel Check-In for fiscal year {1}. Multiple check-ins are not allowed for the same fiscal year.").format(
				frappe.bold(self.hostel_room),
				frappe.bold(self.fiscal_year)
			))
			
	def on_submit(self):
		pass			

@frappe.whitelist()
def get_students_from_room(hostel_room):
	if not hostel_room:
		frappe.throw("Please select a Hostel Room first")

	students = frappe.get_all(
		"Student List Item",
		filters={"parent": hostel_room, "parenttype": "Hostel Room"},
		fields=["student_code", "year", "first_name", "last_name"]
	)

	return students

@frappe.whitelist()
def get_assets_from_room(hostel_room):
	if not hostel_room:
		frappe.throw("Please select a Hostel Room first")

	assets = frappe.get_all(
		"Hostel Asset Item",
		filters={"parent": hostel_room, "parenttype": "Hostel Room"},
		fields=["asset_code", "asset_name"]
	)

	return assets

@frappe.whitelist()
def make_checkout_form(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Hostel Check-In Form", source_name, {
			"Hostel Check-In Form": {
				"doctype": "Hostel Check-Out Form",
				"field_map": {
					"name": "hostel_check_out_form",
					"posting_date": "posting_date",
					"company": "college",
					"hostel_room": "hostel_room",
					"hostel_type": "hostel_type",
					"fiscal_year": "fiscal_year",
					"name":"hostel_check_in_link",
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Check-In Students Items": {
				"doctype": "Check-Out Student Details",
				"postprocess": transfer_currency,
			},
			"Check-In Asset Items": {
				"doctype": "Check-Out Asset Items",
				"field_map": {
					"asset_code": "asset_code",
					"asset_name": "asset_name",
					"asset_condition": "asset_condition_check_in",
					"remarks": "remarks_check_in",
				},
				"postprocess": transfer_currency,
			},
		}, target_doc, adjust_last_date)
	return doc	

@frappe.whitelist()
def get_filtered_students(doctype, txt, searchfield, start, page_len, filters):
	"""
	Returns filtered students based on the hostel room's student list
	"""
	hostel_room = filters.get('hostel_room')
	
	if not hostel_room:
		return []
	
	# Get the student codes from the selected Hostel Room's child table
	student_codes = frappe.db.get_all('Student List Item', 
		filters={'parent': hostel_room, 'parenttype': 'Hostel Room'},
		pluck='student_code'
	)
	
	if not student_codes:
		frappe.msgprint(_('No students assigned to this hostel room'))
		return []
	
	# Build search condition for the student field
	search_condition = ""
	if txt:
		search_condition = f"AND (name LIKE '%{txt}%' OR student_name LIKE '%{txt}%')"
	
	# Query students matching the codes from the hostel room
	students = frappe.db.sql(f"""
		SELECT name, student_name 
		FROM `tabStudent` 
		WHERE name IN %(student_codes)s
		{search_condition}
		ORDER BY 
			CASE 
				WHEN name LIKE %(_txt)s THEN 0
				ELSE 1
			END,
			name
		LIMIT %(start)s, %(page_len)s
	""", {
		'student_codes': student_codes,
		'_txt': f'%{txt}%',
		'start': start,
		'page_len': page_len
	})
	
	return students

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
			SELECT 1 FROM `tabCheck-In Students Items` hai
			WHERE hai.parent = `tabHostel Check-In Form`.name
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