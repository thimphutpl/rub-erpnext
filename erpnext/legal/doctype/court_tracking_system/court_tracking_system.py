# -*- coding: utf-8 -*-
# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class CourtTrackingSystem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.legal.doctype.court_status.court_status import CourtStatus
		from erpnext.legal.doctype.hearing_details.hearing_details import HearingDetails
		from frappe.types import DF

		account_type: DF.Literal["", "Active", "OBS", "APF", "BG Revoke"]
		amended_from: DF.Link | None
		borrower_filed_by: DF.Data | None
		branch: DF.Link
		case_status: DF.Table[CourtStatus]
		case_type: DF.Literal["", "Counter Litigation", "Criminal & ACC Cases", "Others"]
		cid_license_number: DF.Data | None
		collateral_description: DF.SmallText | None
		collateral_type: DF.Literal["", "Movable", "Immovable", "Extension of Charges", "Mortgage and Mortgagee"]
		court_case: DF.SmallText | None
		court_venue: DF.Literal["", "Bumthang", "Chukha", "Dagana", "Gasa", "Haa", "Lhuentse", "Mongar", "Paro", "Pemagatshel", "Punakha", "Samtse", "Sarpang", "Thimphu", "Trashigang", "Trashiyangtse", "Trongsa", "Tsirang", "Wangdue Phodrang", "Zhemgang", "Samdrup Jongkhar", "Phuentsholing", "Lhamoi Zingkha", "Nganglam", "Jomotshangkha", "Samdrup Choling", "Dorokha", "Tashi Choling", "Gelephu", "Lingzhi", "Sakteng", "Thrimshing", "Wamrong", "Pangbang", "Weringla", "Sombekha", "Supreme Court", "High Court", "Time Bound Bench", "Supreme Court", "Office of Gyalpoi Zimpoen"]
		current_status: DF.SmallText | None
		date: DF.Date
		exposure: DF.Data | None
		follow_up: DF.SmallText | None
		guarantor: DF.Data | None
		hearing_details: DF.Table[HearingDetails]
		investigation: DF.Literal["", "Police", "ACC", "Audit"]
		issue_details: DF.SmallText | None
		loan_account_no: DF.Data | None
		loan_category: DF.Link | None
		loan_outstanding: DF.Float
		loan_product: DF.Link | None
		loan_sub_category: DF.Link | None
		loan_tenure: DF.Date | None
		overdue_amount: DF.Float
		recovered_amount: DF.Float
		sanction_amount: DF.Float
		sanction_date: DF.Date | None
	# end: auto-generated types

	def on_submit(self):
		pass
		# self.notify_users()

	def autoname(self):
		type = ""
		if self.case_type == "NPL Recovery Cases":
			type = "CASE/RC/"
		elif self.case_type == "Counter Litigation":
			type = "CASE/CL/"
		elif self.case_type == "Criminal & ACC Cases":
			type = "CASE/CC/"
		self.name = make_autoname(str(type)+".YYYY./.#####")

	def notify_users(self):
		args = self.get_args()
		template = frappe.db.get_single_value('HR Settings', 'criminal_and_acc_cases')
		
		if self.case_type in ("Counter Litigation","NPL Recovery Cases"):
			template = frappe.db.get_single_value('HR Settings', 'npl_recovery_cases_and_counter_litigation_notification')
		
		if not template:
			frappe.msgprint(_("Please set default template for Court Tracking Templates in HR settings."))
			return

		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		#frappe.msgprint(str(message))
		recipients = self.owner
		subject = email_template.subject
		self.send_mail(recipients,message, subject)

	def send_mail(self, recipients, message, subject):
		attachments = self.get_attachment()
		try:
			frappe.sendmail(
					recipients=recipients,
					subject=_(subject),
					message= _(message),
					attachments=attachments,
				)
		except:
			pass
	def get_args(self):
		parent_doc = frappe.get_doc(self.doctype, self.name)
		args = parent_doc.as_dict()
		return args
	
	def get_attachment(self):
		"""check print settings are attach the pdf"""
		print_settings = frappe.get_doc("Print Settings", "Print Settings")
		return [
			{
				"print_format_attachment": 1,
				"doctype": self.doctype,
				"name": self.name,
				"print_format": "Court Tracking System",
				"print_letterhead": print_settings.with_letterhead,
				"lang": "en",
			}
		]
	
	def before_update_after_submit(self):
		frappe.msgprint(str(self))
		# send email on change of status
@frappe.whitelist()
def get_loan_product(doctype, txt, searchfield, start, page_len, filters):
	query = """
		SELECT 
			loan_product
		FROM 
			`tabLoan Products`
		WHERE parent_product = '{0}' and is_sub_group = '0'
	""".format(filters.get('parent_product'))
	return frappe.db.sql(query)

@frappe.whitelist()
def get_case_description_options(doctype, txt, searchfield, start, page_len, filters):
	case_status = filters.get("case_status")

	if not case_status:
		return []

	return frappe.db.sql("""
		SELECT name, name
		FROM `tabCase Description`
		WHERE name IN (
			SELECT parent
			FROM `tabCase Status Item`
			WHERE case_status = %s
		)
		AND name LIKE %s
		LIMIT %s OFFSET %s
	""", (case_status, f"%{txt}%", page_len, start))