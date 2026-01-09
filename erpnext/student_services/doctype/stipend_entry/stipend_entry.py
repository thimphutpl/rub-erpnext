# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.utils import (
	cint,
	get_link_to_form,
	get_last_day,
	getdate,
	flt,
	nowdate,
)
from frappe.model.document import Document


class StipendEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.stipend_entry_details.stipend_entry_details import StipendEntryDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		company: DF.Link
		end_date: DF.Date | None
		error_message: DF.SmallText | None
		failed: DF.Data | None
		fiscal_year: DF.Link
		month: DF.Literal["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		number_of_employees: DF.Data | None
		number_of_students: DF.Data | None
		payroll_frequency: DF.Literal["", "Monthly"]
		posting_date: DF.Date
		start_date: DF.Date | None
		status: DF.Literal["Draft", "Submitted", "Cancelled", "Queued", "Failed"]
		stipend_slip_created: DF.Check
		stipend_slip_submitted: DF.Check
		student_code: DF.Link | None
		students: DF.Table[StipendEntryDetails]
		successful: DF.Data | None
	# end: auto-generated types

	def onload(self):
		if not self.docstatus == 1 or self.stipend_slip_submitted:
			return

	def validate(self):
		self.validate_dates()
		self.set_status()

	def validate_dates(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw(_("Start date cannot be after end date"))

		if self.start_date:
			check_start_end_dates(self.start_date,self.fiscal_year, self.month)

		if self.end_date:
			check_start_end_dates(self.end_date,self.fiscal_year, self.month)
			

	def on_cancel(self):
		self.delete_linked_stipend_slips()
		self.db_set("stipend_slip_created", 0)
		self.db_set("stipend_slip_submitted", 0)
		self.set_status(update=True, status="Cancelled")
		self.db_set("error_message", "")

	def cancel(self):
		if len(self.get_linked_stipend_slips()) > 50:
			msg = _("Stipend Entry cancellation is queued. It may take a few minutes")
			msg += "<br>"
			msg += _(
				"In case of any error during this background process, the system will add a comment about the error on this Stipend Entry and revert to the Submitted status"
			)
			frappe.msgprint(
				msg,
				indicator="blue",
				title=_("Cancellation Queued"),
			)
			self.queue_action("cancel", timeout=3000)
		else:
			self._cancel()

	def delete_linked_stipend_slips(self):
		stipend_slips = self.get_linked_stipend_slips()

		for stipend_slip in stipend_slips:
			if stipend_slip.docstatus == 1:
				frappe.get_doc("Stipend Slip", stipend_slip.name).cancel()
			frappe.delete_doc("Stipend Slip", stipend_slip.name)

	def get_linked_stipend_slips(self):
		return frappe.get_all("Stipend Slip", {"stipend_entry": self.name}, ["name", "docstatus"])

	def before_submit(self):
		if not self.students:
			frappe.throw(_("Please add students before submitting"))

	def on_submit(self):
		self.set_status(update=True, status="Submitted")
		self.create_stipend_slips()

	def set_status(self, status=None, update=False):
		if not status:
			status = {0: "Draft", 1: "Submitted", 2: "Cancelled"}[self.docstatus or 0]

		if update:
			self.db_set("status", status)
		else:
			self.status = status

	@frappe.whitelist()
	def fill_student_details(self):
		
		filters = self.make_filters()
		students = get_student_list(filters=filters, as_dict=True, ignore_match_conditions=True)
		self.set("students", [])
		
		if not students:
			error_msg = _("No students found for the mentioned criteria:<br>Company: {0}").format(
				frappe.bold(self.company)
			)
			if self.fiscal_year:
				error_msg += "<br>" + _("Fiscal Year: {0}").format(frappe.bold(self.fiscal_year))
			if self.month:
				error_msg += "<br>" + _("Month: {0}").format(frappe.bold(self.month))
			frappe.throw(error_msg, title=_("No students found"))
		
		for student in students:
			self.append("students", {
				"student_code": student.name,
				"full_name": student.student_name,
				"programme": student.programme,
				"semester": student.semester,
				"year": student.year if hasattr(student, 'year') else None
			})
			
		self.number_of_students = len(students)
		self.save()
		return len(students)

	def make_filters(self):
		filters = frappe._dict(
			company=self.company,
			student_code=self.student_code,
			fiscal_year=self.fiscal_year,
			month=self.month,
		)
		return filters

	@frappe.whitelist()
	def create_stipend_slips(self):
		"""Creates stipend slip for selected students if not already created"""
		self.check_permission("write")
		students = [std.student_code for std in self.students]
		
		if students:
			args = frappe._dict({
				"company": self.company,
				"fiscal_year": self.fiscal_year,
				"month": self.month,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"stipend_entry": self.name,
			})
			
			if len(students) > 100:
				self.db_set("status", "Queued")
				frappe.enqueue(
					create_stipends_slips_for_students,
					timeout=3000,
					students=students,
					args=args,
					publish_progress=False,
				)
				frappe.msgprint(
					_("Stipend Slip creation is queued. It may take a few minutes"),
					alert=True,
					indicator="blue",
				)
			else:
				create_stipends_slips_for_students(students, args, publish_progress=False)
				self.reload()

	@frappe.whitelist()
	def has_bank_entries(self) -> dict[str, bool]:
		je = frappe.qb.DocType("Journal Entry")
		jea = frappe.qb.DocType("Journal Entry Account")

		bank_entries = (
			frappe.qb.from_(je)
			.inner_join(jea)
			.on(je.name == jea.parent)
			.select(je.name)
			.where(
				(je.voucher_type == "Bank Entry")
				& (jea.reference_name == self.name)
				& (jea.reference_type == "Stipend Entry")
			)
		).run(as_dict=True)

		return {
			"has_bank_entries": bool(bank_entries)
		}

	@frappe.whitelist()
	def submit_stipend_slips(self):
		self.check_permission("write")
		stipend_slips = self.get_st_slip_list(ss_status=0)

		if len(stipend_slips) > 300 :
			self.db_set("status", "Queued")
			frappe.enqueue(
				submit_stipend_slips_for_students,
				timeout=3000,
				stipend_entry=self,
				stipend_slips=stipend_slips,
				publish_progress=False,
			)
			frappe.msgprint(
				_("Stipend Slip submission is queued. It may take a few minutes"),
				alert=True,
				indicator="blue",
			)
		else:
			submit_stipend_slips_for_students(self, stipend_slips, publish_progress=False)

	@frappe.whitelist()
	def make_bank_entry(self):
		
		
		self.check_permission("write")

		
		
		
		stipend_slip_total = 0
		stipend_details = self.get_stipend_slip_details()
		
		posting        = frappe._dict()
		for stipend_detail in stipend_details:
			#frappe.msgprint(str(stipend_detail.gl_head))
			#frappe.msgprint(f"GL Head: {str(salary_detail.gl_head)}, Party: {str(salary_detail.party)}, Party Type: {str(salary_detail.party_type)}")
			stipend_slip_total += (-1 * flt(stipend_detail.amount,2) if stipend_detail.parentfield == "deductions" else flt(stipend_detail.amount,2))
			posting.setdefault("to_payables", []).append({
				"account"        : stipend_detail.gl_head,
				"credit_in_account_currency" if stipend_detail.parentfield == "deductions" else "debit_in_account_currency": flt(stipend_detail.amount),
				"against_account": "4-193 - Sundry Creditors - Domestic - GCIT",
				"cost_center"    : "Student Service Division - OVC",
				"party_check"    : 0,
				"account_type"   :  "student",
				"party_type"     :  "Student",
				"party"          :  "",
				"reference_type": self.doctype,
				"reference_name": self.name,
				"salary_component": stipend_detail.salary_component
			})

			

		# To Bank
		if posting.get("to_payables") and len(posting.get("to_payables")):
			# frappe.throw(str(salary_slip_total))
			posting.setdefault("to_bank", []).append({
				"account"       				: "4-193 - Sundry Creditors - Domestic - GCIT",
				"debit_in_account_currency"		: flt(stipend_slip_total),
				"cost_center"   				: "Student Service Division - OVC",
				"party_check"   				: 0,
				"reference_type"				: self.doctype,
				"reference_name"				: self.name,
				"salary_component"				: stipend_detail.salary_component
			})
			posting.setdefault("to_bank", []).append({
				"account"       				: "Bank - GCIT",
				"credit_in_account_currency"	: flt(stipend_slip_total),
				"cost_center"   				: "Student Service Division - OVC",
				"party_check"   				: 0,
				"reference_type"				: self.doctype,
				"reference_name"				: self.name,
				"salary_component"				: stipend_detail.salary_component
			})
			posting.setdefault("to_payables",[]).append({
				"account"       				: "4-193 - Sundry Creditors - Domestic - GCIT",
				"credit_in_account_currency" 	: flt(stipend_slip_total),
				"cost_center"  				 	: "Student Service Division - OVC",
				"party_check"   				: 0,
				"reference_type"				: self.doctype,
				"reference_name"				: self.name,
				"salary_component"				: "Net Pay"
			})
				
		if posting:
			jv_name, v_title = None, ""
			for i in posting:
				if i == "to_payables":
					v_title         = "To Payables"
					v_voucher_type  = "Journal Entry"
					v_naming_series = "Journal Voucher"
				else:
					v_title         = "To Bank" if i == "to_bank" else i
					v_voucher_type  = "Bank Entry"
					v_naming_series = "Bank Payment Voucher"

				if v_title:
					v_title = "STIPEND"+str(self.fiscal_year)+'- '+str(self.month)+" - "+str(v_title)
				else:
					v_title = "STIPEND"+str(self.fiscal_year)+'- '+str(self.month)

				#frappe.throw(str(self.doctype))

				doc = frappe.get_doc({
						"doctype"			: "Journal Entry",
						"voucher_type"		: v_voucher_type,
						"naming_series"		: v_naming_series,
						"title"				: v_title,
						"fiscal_year"		: self.fiscal_year,
						"remark"			: v_title,
						"posting_date"		: nowdate(),                     
						"company"			: self.company,
						"accounts"			: sorted(posting[i], key=lambda item: item['cost_center']),
						"branch"			: "Communication and Linkage Services - PCE",
						"reference_type"	: self.doctype,
						"reference_name"	: self.name,
					})
				doc.flags.ignore_permissions = 1 
				doc.insert()

				if i == "to_payables":
				
					doc.submit()
					jv_name = doc.name

			frappe.msgprint(_("Salary posting to accounts is successful."),title="Posting Successful")
		else:
			frappe.throw(_("No data found"),title="Posting failed")

	def get_stipend_slip_details(self):
		result = frappe.db.sql("""
			SELECT 
				sc.name as sc_name,
				sc.name as salary_component,
				sc.component_type as component_type,
				sd.parentfield,
				sca.account as gl_head,
				sum(ifnull(sd.amount,0)) as amount,
				'Payable' as account_type,
				'Student' as party_type,
				t1.student_code as party,
				sca.company as college
			FROM
				`tabStipend Slip` t1,
				`tabStipend Details` sd,
				`tabStipend Component` sc,
				`tabStipend Component Details` sca,
				`tabCompany` c
			WHERE 
				t1.fiscal_year = '{0}'
				AND t1.month='{1}'
				AND t1.stipend_entry='{2}'
				AND t1.docstatus = 1
				AND sd.parent = t1.name
				AND sc.name = sd.stipend_component
				AND sca.parent = sc.name
				AND c.name = t1.company
				AND sca.company = t1.company
				AND sd.amount > 0 
				AND exists(select 1
							from `tabStipend Entry Details` ped
							where ped.parent = t1.stipend_entry
							and ped.student_code = t1.student_code)
					
			GROUP BY 
				sc.component_type, 
				sca.account, 
				sca.company, 
				t1.student_code,
				sc.name,
				sd.parentfield;
		""".format(self.fiscal_year, self.month, self.name),as_dict=1)
		return result

	def get_st_slip_list(self, ss_status, as_dict=False):
		"""
		Returns list of salary slips based on selected criteria
		"""

		ss = frappe.qb.DocType("Stipend Slip")
		ss_list = (
			frappe.qb.from_(ss)
			.select(ss.name, ss.stipend_structure)
			.where(
				(ss.docstatus == ss_status)
				& (ss.fiscal_year == self.fiscal_year)
				& (ss.month == self.month)
				& (ss.stipend_entry == self.name)
				& ((ss.journal_entry.isnull()) | (ss.journal_entry == ""))
			)
		).run(as_dict=as_dict)

		return ss_list

@frappe.whitelist()
def get_start_end_dates(fiscal_year, month, company=None):
	"""Returns dict of start and end dates for given month and fiscal year"""
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	month_num = str(months.index(month) + 1).rjust(2, "0")
	
	start_date = f"{fiscal_year}-{month_num}-01"
	end_date = get_last_day(start_date)

	return frappe._dict({"start_date": start_date, "end_date": end_date})

@frappe.whitelist()
def check_start_end_dates(date_sr,fiscal_year, month, company=None):
	"""Returns dict of start and end dates for given month and fiscal year"""
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	month_num = str(months.index(month) + 1).rjust(2, "0")
	
	start_date = f"{fiscal_year}-{month_num}-01"
	end_date = get_last_day(start_date)

	start_date_obj = getdate(start_date)
	end_date_obj = getdate(end_date)
	date_sr_obj = getdate(date_sr)
	if start_date_obj <= date_sr_obj <= end_date_obj:
		return
	else:
		 frappe.throw(f"Date {date_sr} is out of range. Valid range: {start_date} to {end_date}")

	#return frappe._dict({"start_date": start_date, "end_date": end_date})

def get_student_list(filters, as_dict=True, ignore_match_conditions=False):
	"""Get filtered student list"""
	std_list = get_filtered_students(
		filters,
		as_dict=as_dict,
		ignore_match_conditions=ignore_match_conditions,
	)
	
	if as_dict:
		students_to_check = {std['name']: std for std in std_list}
	else:
		students_to_check = {std[0]: std for std in std_list}
	
	return remove_payrolled_students(students_to_check, filters.fiscal_year, filters.month)

def get_filtered_students(filters, as_dict=True, ignore_match_conditions=False):
	"""Get students with active stipend structure"""
	StipendStructure = frappe.qb.DocType("Stipend Structure")
	Student = frappe.qb.DocType("Student")
	
	query = (
		frappe.qb.from_(Student)
		.inner_join(StipendStructure)
		.on(Student.name == StipendStructure.student_code)
		.where(
			(Student.company == filters.company) 
			
		)
	)
	
	if filters.get('student_code'):
		query = query.where(Student.name == filters.student_code)
	
	query = query.select(
		Student.name,
		Student.student_name,
		Student.programme,
		Student.semester,
		Student.year
	).distinct()
	
	return query.run(as_dict=as_dict)

def remove_payrolled_students(std_list, fiscal_year, month):
	"""Remove students who already have stipend slips for given period"""
	StipendSlip = frappe.qb.DocType("Stipend Slip")
	
	student_with_payroll = (
		frappe.qb.from_(StipendSlip)
		.select(StipendSlip.student_code)
		.where(
			(StipendSlip.docstatus == 1) &
			(StipendSlip.fiscal_year == fiscal_year) &
			(StipendSlip.month == month)
		)
	).run(pluck=True)
	
	return [std_list[std] for std in std_list if std not in student_with_payroll]

def create_stipends_slips_for_students(students, args, publish_progress=True):
	"""Create stipend slips for students in background"""
	stipend_entry = frappe.get_cached_doc("Stipend Entry", args.stipend_entry)
	
	try:
		stipend_slips_exist_for = get_existing_stipend_slips(students, args)
		count = 0

		students = list(set(students) - set(stipend_slips_exist_for))
		
		for std in students:
			args.update({
				"doctype": "Stipend Slip", 
				"student_code": std
			})
			stipend_slip = frappe.get_doc(args)
			stipend_slip.insert()
			#stipend_slip.submit()

			count += 1
			if publish_progress:
				frappe.publish_progress(
					count * 100 / len(students),
					title=_("Creating Stipend Slips..."),
				)

		stipend_entry.db_set({
			"status": "Submitted", 
			"stipend_slip_created": 1, 
			"error_message": "",
			
		})

		if stipend_slips_exist_for:
			frappe.msgprint(
				_("Stipend Slips already exist for students {0}, and will not be processed by this stipend entry.").format(
					frappe.bold(", ".join(std for std in stipend_slips_exist_for))
				),
				title=_("Message"),
				indicator="orange",
			)

	except Exception as e:
		frappe.db.rollback()
		log_stipend_failure("creation", stipend_entry, e)
		raise

	finally:
		frappe.db.commit()
		frappe.publish_realtime("completed_stipend_slip_creation", user=frappe.session.user)

def get_existing_stipend_slips(students, args):
	"""Get list of students who already have stipend slips for this period"""
	StipendSlip = frappe.qb.DocType("Stipend Slip")

	return (
		frappe.qb.from_(StipendSlip)
		.select(StipendSlip.student_code)
		.distinct()
		.where(
			(StipendSlip.docstatus != 2) &
			(StipendSlip.company == args.company) &
			(StipendSlip.stipend_entry == args.stipend_entry) &
			(StipendSlip.student_code.isin(students))
		)
	).run(pluck=True)

def submit_stipend_slips_for_students(stipend_entry, stipend_slips, publish_progress=True):
	try:
		submitted = []
		unsubmitted = []
		frappe.flags.via_stipend_entry = True
		count = 0

		for entry in stipend_slips:
			stipend_slip = frappe.get_doc("Stipend Slip", entry[0])
			if flt(stipend_slip.net_pay )< 0:
				unsubmitted.append(entry[0])
			else:
				try:
					stipend_slip.submit()
					submitted.append(stipend_slip)
				except frappe.ValidationError:
					unsubmitted.append(entry[0])

			count += 1
			if publish_progress:
				frappe.publish_progress(
					count * 100 / len(stipend_slips), title=_("Submitting Stipend Slips...")
				)

		if submitted:
			# payroll_entry.make_accrual_jv_entry(submitted)
			stipend_entry.db_set({"stipend_slip_submitted": 1, "status": "Submitted", "error_message": ""})

		show_stipend_submission_status(submitted, unsubmitted, stipend_entry)

	except Exception as e:
		frappe.db.rollback()
		log_stipend_failure("submission", stipend_entry, e)

	finally:
		frappe.db.commit()  # nosemgrep
		frappe.publish_realtime("completed_sitpend_slip_submission", user=frappe.session.user)

	frappe.flags.via_payroll_entry = False

def log_stipend_failure(process, stipend_entry, error):
	"""Log errors during stipend processing"""
	error_log = frappe.log_error(
		title=_("Stipend Slip {0} failed for Stipend Entry {1}").format(process, stipend_entry.name)
	)
	
	message_log = frappe.message_log.pop() if frappe.message_log else str(error)

	try:
		if isinstance(message_log, str):
			error_message = json.loads(message_log).get("message")
		else:
			error_message = message_log.get("message")
	except Exception:
		error_message = message_log

	error_message += "\n" + _("Check Error Log {0} for more details.").format(
		get_link_to_form("Error Log", error_log.name)
	)

	stipend_entry.db_set({"error_message": error_message, "status": "Failed"})


def show_stipend_submission_status(submitted, unsubmitted, stipend_entry):
	if not submitted and not unsubmitted:
		frappe.msgprint(
			_(
				"No Stipend slip found to submit for the above selected criteria OR sTipend slip already submitted"
			)
		)
	elif submitted and not unsubmitted:
		frappe.msgprint(
			_("Stipend Slips submitted for period from {0} to {1}").format(
				stipend_entry.start_date, stipend_entry.end_date
			),
			title=_("Success"),
			indicator="green",
		)
	elif unsubmitted:
		frappe.msgprint(
			_("Could not submit some Stipend Slips: {}").format(
				", ".join(get_link_to_form("Stipend Slip", entry) for entry in unsubmitted)
			),
			title=_("Failure"),
			indicator="red",
		)