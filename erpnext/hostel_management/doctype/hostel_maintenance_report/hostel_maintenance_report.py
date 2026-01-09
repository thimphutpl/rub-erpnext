# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.stock_controller import StockController
from erpnext.controllers.buying_controller import BuyingController
from frappe.utils import flt, cint, cstr, fmt_money, formatdate, nowtime, getdate
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available


class HostelMaintenanceReport(BuyingController, StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.hostel_maintenance_report_item.hostel_maintenance_report_item import HostelMaintenanceReportItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		damage_type: DF.Literal["", "Vandalism", "Loss or Misuse of Property", "Damage to Shared Facilities"]
		description_of_maintenance: DF.SmallText | None
		expenses_borne_by: DF.Literal["", "Student", "College"]
		first_name: DF.Data | None
		full_name: DF.Data | None
		hostel_maintenance_application: DF.Data | None
		hostel_room: DF.Link | None
		hostel_type: DF.Link | None
		items: DF.Table[HostelMaintenanceReportItem]
		jv: DF.Link | None
		last_name: DF.Data | None
		maintenance_focal: DF.Link | None
		maintenance_required_on: DF.Date | None
		maintenance_type: DF.Literal["", "Repair", "Replacement"]
		phone_number: DF.Data | None
		posting_date: DF.Date
		posting_time: DF.Time | None
		report_on_maintenance: DF.SmallText | None
		student_code: DF.Link | None
		total_expenses_incurred: DF.Currency
	# end: auto-generated types

	def on_submit(self):
		# self.validate_dc()
		# self.validate_data()
		# self.check_on_dry_hire()
		# self.check_budget()
		# self.update_stock_ledger()
		self.link_maintenance_application_to_maintenance_report()

		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		if (self.expenses_borne_by == "College" or self.expenses_borne_by == ""):
			# return
			self.update_stock_ledger()
			self.make_gl_entries()
			self.repost_future_sle_and_gle()
		else:
			# return
			# self.post_journal_entry()
			self.make_gl_entries()

		if self.expenses_borne_by == "Student":
			make_payment_entry(self.name)
		else:
			make_stock_entry(self.name)	
	
	def link_maintenance_application_to_maintenance_report(self):
		# find the related Hostel Maintenance Application
		application = frappe.get_doc("Hostel Maintenance Application", self.hostel_maintenance_application)

		# update its hostel_maintenance_report field with this report's name
		application.hostel_maintenance_report = self.name
		application.save(ignore_permissions=True)	
		

	def on_cancel(self):
		# self.update_stock_ledger()
		if (self.expenses_borne_by == "College" or self.expenses_borne_by == ""):
			self.update_stock_ledger()
		else:
			self.get_gl_entries()
			# self.post_journal_entry()	
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# Ver 2.0.190509, Following method commented by SHIV on 2019/05/20 
		#self.update_general_ledger(1)

		# Ver 2.0.190509, Following method added by SHIV on 2019/05/20
		# if self.is_opening != "Yes":
		# 	self.make_gl_entries_on_cancel()
		# self.repost_future_sle_and_gle()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Hostel Maintenance Application",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)
		docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if docstatus and docstatus != 2:
			frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")

		self.db_set("jv", None)

	def validate(self):
		self.calculate_amount()
		# self.validate_accounts()	

	def calculate_amount(self):
		for item in self.items:
			amount =  (item.rate * item.qty)
			item.amount = amount
			self.total_expenses_incurred = item.amount		

	# Ver 2.0.190509, Following method added by SHIV on 2019/05/14
	def update_stock_ledger(self):
				# Stock entry for direct_consumption is disabled due to MAP related issues
		for d in self.items:		
			if d.expenses_type=="Asset":
				return		
			if d.expenses_type=="Stock Item":
				wh = d.warehouse
			else:
				wh = d.warehouse

			sl_entries = []
			sl_entries.append(self.get_sl_entries(self, {
						"item_code": d.item_code,
						"actual_qty": -1 * flt(d.qty), 
						"warehouse": wh, 
						"incoming_rate": 0,
					}))

			if self.docstatus == 2:
				sl_entries.reverse()

			self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')	

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		#expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		# expense_bank_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "expenses_included_in_asset_valuation")
		expense_bank_account = frappe.db.get_value("Company", self.college, "income_account")
		if not expense_bank_account:
			frappe.throw("No Default Payable Account set in Company")

		# maintenance_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "asset_received_but_not_billed")
		maintenance_account = frappe.db.get_value("Company", self.college, "receivable_account")
		if not maintenance_account:
			frappe.throw("No Default Payable Account set in Company")	

		if expense_bank_account and maintenance_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Hostel Maintenance (" + self.student_code + " for " + self.hostel_room + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Payment Voucher'
			je.remark = 'Payment against : ' + self.name
			je.posting_date = self.maintenance_required_on
			je.branch = self.branch
			je.company = self.college

			je.append("accounts", {
					"account": maintenance_account,
					"cost_center": self.cost_center,
					"party_type": self.expenses_borne_by,
					"party": self.student_code,
					"reference_type": "Hostel Maintenance Report",
					"reference_name": self.name,
					"debit_in_account_currency": flt(self.total_expenses_incurred),
					"debit": flt(self.total_expenses_incurred),
				})

			je.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					# "party_type": "Supplier",
					"party_type": self.expenses_borne_by,
					"party": self.student_code,
					"credit_in_account_currency": flt(self.total_expenses_incurred),
					"credit": flt(self.total_expenses_incurred),
				})

			je.insert()
			self.db_set("jv", je.name)
		else:
			frappe.throw("Define POL expense account in Maintenance Setting or Expense Bank in Branch")		


	# def get_gl_entries(self, warehouse_account):
	def get_gl_entries(self):
		gl_entries = []
		# creditor_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_advance_account")
		creditor_account = frappe.db.get_value("Company", self.company, "income_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")


		# expense_account = self.get_expense_account() receivable_account
	#    expense_account = frappe.db.get_value("Equipment Category", self.equipment_category, "pol_advance_account")
		expense_account = frappe.db.get_value("Company", self.company, "receivable_account")
		if not expense_account:
			frappe.throw("Set Default Payable Account in Company")

		# if self.hiring_cost_center:
		#     cost_center = self.hiring_cost_center
		# else:
		# cost_center = get_branch_cc(self.vehicle_branch)


		# ba = get_equipment_ba(self.vehicle)
		# default_ba = get_default_ba()


		gl_entries.append(
			prepare_gl(self, {"account": expense_account,
				"debit": flt(self.total_expenses_incurred),
				"debit_in_account_currency": flt(self.total_expenses_incurred),
				"cost_center": self.cost_center,
				"party_type": "Student",
				"party": self.student_code,
				# "business_activity": ba
				})
		)


		gl_entries.append(
			prepare_gl(self, {"account": creditor_account,
				"credit": flt(self.total_expenses_incurred),
				"credit_in_account_currency": flt(self.total_expenses_incurred),
				"cost_center": self.cost_center,
				"party_type": "Student",
				"party": self.student_code,
				"against_voucher": self.name,
				"against_voucher_type": self.doctype,
				# "business_activity": default_ba
				})
		)
		# frappe.throw(str(gl_entries))
		return gl_entries 

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Hostel Maintenance Report", source_name, {
			"Hostel Maintenance Report": {
				"doctype": "Payment Entry",
				"field_map": {
					"name": "payment_entry",
					"posting_date": "ta_date",
					"college":"company",
					"branch":"branch",
					# "total_expenses_incurred":"total_taxes_and_charges",
					"expenses_borne_by":"party_type",
					"student_code":"party",
					"full_name": "party_name",
					"total_expenses_incurred":"party_balance",
					"total_expenses_incurred": "paid_amount"
					# "total_expenses_incurred":"base_total_taxes_and_charges"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Hostel Asset Maintenance": {
				"doctype": "Hostel Maintenance Expenses Item",
				"postprocess": transfer_currency,
			},
			# "Hostel Maintenance Expenses Item": { 
			# 	"doctype": "Stock Entry Detail",
			# 	"postprocess": transfer_currency,
			# },
		}, target_doc, adjust_last_date)
	return doc

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def update_date(obj, target, source_parent):
		return

	def transfer_currency(obj, target, source_parent):
		return
		
	def adjust_last_date(source, target):
		return

	doc = get_mapped_doc("Hostel Maintenance Report", source_name, {
			"Hostel Maintenance Report": {
				"doctype": "Stock Entry",
				"field_map": {
					"name": "stock_entry",
					"posting_date": "ta_date",
					"college":"company",
					"branch":"branch",
					"total_expenses_incurred":"total_outgoing_value"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1]}
			},
			"Hostel Asset Maintenance": {
				"doctype": "Hostel Maintenance Expenses Item",
				"postprocess": transfer_currency,
			},
			"Hostel Maintenance Expenses Item": {
				"doctype": "Stock Entry Detail",
				"field_map": [
					["name", "hostel_maintenance_expenses_item"],
					["parent", "hostel_maintenance_report"],
				],
				"postprocess": transfer_currency,
			},
		}, target_doc, 
		adjust_last_date,
		# ignore_child_tables=True,
		# ignore_permissions=ignore_permissions,
		# cached=True,
		)
	return doc					

@frappe.whitelist()
def get_asset_rate(item_code):
	# Fetch Item Price for given Asset (Item)
	price = frappe.db.get_value("Item Price", {"item_code": item_code}, "price_list_rate")
	return price or 0

@frappe.whitelist()
def get_warehouse_by_cost_center(cost_center):
	warehouse = frappe.db.get_value("Cost Center", cost_center, "warehouse")
	# frappe.throw(str(warehouse))
	return warehouse	