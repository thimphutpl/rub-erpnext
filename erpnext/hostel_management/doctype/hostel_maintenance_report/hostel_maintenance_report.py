# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.controllers.stock_controller import StockController
from frappe.utils import flt, cint, cstr, fmt_money, formatdate, nowtime, getdate
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)


class HostelMaintenanceReport(StockController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		college: DF.Link | None
		cost_center: DF.Link | None
		damage_type: DF.Literal["", "Vandalism", "Loss or Misuse of Property", "Damage to Shared Facilities"]
		description_of_maintenance: DF.SmallText | None
		expenses_borne_by: DF.Literal["", "Student", "College"]
		first_name: DF.Data | None
		hostel_room: DF.Link | None
		hostel_type: DF.Link | None
		items: DF.Table[Document]
		jv: DF.Link | None
		last_name: DF.Data | None
		maintenance_focal: DF.Link | None
		maintenance_required_on: DF.Date | None
		maintenance_type: DF.Literal["", "Repair", "Replacement"]
		phone_number: DF.Data | None
		report_on_maintenance: DF.SmallText | None
		student_code: DF.Link | None
		total_expenses_incurred: DF.Currency
	# end: auto-generated types
	pass

	def on_submit(self):
		# self.validate_dc()
		# self.validate_data()
		# self.check_on_dry_hire()
		# self.check_budget()

		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		if (self.expenses_borne_by == "College" or self.expenses_borne_by == ""):
			self.update_stock_ledger()
			self.make_gl_entries()
			self.repost_future_sle_and_gle()
		else:
			self.post_journal_entry()
			# self.make_gl_entries()
		# self.make_pol_entry()

	def on_cancel(self):
		if (self.expenses_borne_by == "College" or self.expenses_borne_by == ""):
			self.update_stock_ledger()
		else:
			self.post_journal_entry()	
		""" ++++++++++ Ver 2.0.190509 Begins ++++++++++ """
		# Ver 2.0.190509, Following method commented by SHIV on 2019/05/20 
		#self.update_general_ledger(1)

		# Ver 2.0.190509, Following method added by SHIV on 2019/05/20
		if self.is_opening != "Yes":
			self.make_gl_entries_on_cancel()
		self.repost_future_sle_and_gle()
		""" ++++++++++ Ver 2.0.190509 Ends ++++++++++++ """
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
			"Stock Ledger Entry",
			"Repost Item Valuation",
			"Serial and Batch Bundle",
		)
		docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if docstatus and docstatus != 2:
			frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")

		self.db_set("jv", None)

	# Ver 2.0.190509, Following method added by SHIV on 2019/05/14
	def update_stock_ledger(self):
				# Stock entry for direct_consumption is disabled due to MAP related issues
		if self.direct_consumption:
			return		
		if self.hiring_warehouse:
			wh = self.hiring_warehouse
		else:
			wh = self.equipment_warehouse

		sl_entries = []
		sl_entries.append(self.get_sl_entries(self, {
										"item_code": self.pol_type,
					"actual_qty": flt(self.qty), 
					"warehouse": wh, 
					"incoming_rate": round(flt(self.total_amount) / flt(self.qty) , 2)
				}))

		if self.docstatus == 2:
			sl_entries.reverse()

		self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')	

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		# veh_cat = frappe.db.get_value("Equipment", self.equipment, "equipment_category")
		# if veh_cat:
		# 	if veh_cat == "Pool Vehicle":
		# 		pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pool_vehicle_pol_expenses")
		# 	else:
		# 		pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_expense_account")
		# else:
		# 	frappe.throw("Can not determine machine category")

		#expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		# expense_bank_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "expenses_included_in_asset_valuation")
		expense_bank_account = frappe.db.get_value("Company", self.college, "default_bank_account")
		if not expense_bank_account:
			frappe.throw("No Default Payable Account set in Company")

		# maintenance_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "asset_received_but_not_billed")
		maintenance_account = frappe.db.get_value("Company", self.college, "default_bank_account")
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
					"reference_type": "Hostel Maintenance Report",
					"reference_name": self.name,
					"debit_in_account_currency": flt(self.total_expenses_incurred),
					"debit": flt(self.total_expenses_incurred),
				})

			je.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					# "party_type": "Supplier",
					# "party": self.name,
					"credit_in_account_currency": flt(self.total_expenses_incurred),
					"credit": flt(self.total_expenses_incurred),
				})

			je.insert()
			self.db_set("jv", je.name)
		else:
			frappe.throw("Define POL expense account in Maintenance Setting or Expense Bank in Branch")		
