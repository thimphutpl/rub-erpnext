# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.doctype.journal_entry.journal_entry import get_tds_account
from erpnext.accounts.utils import get_account_currency, get_balance_on, get_outstanding_invoices,check_clearance_date
from frappe.model.mapper import get_mapped_doc

class TDSRemittance(AccountsController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.tds_remittance_item.tds_remittance_item import TDSRemittanceItem
		from frappe.types import DF

		amended_from: DF.Link | None
		based_on_region: DF.Check
		branch: DF.Link
		cheque_date: DF.Date | None
		cheque_lot: DF.Link | None
		cheque_no: DF.Data | None
		clearance_date: DF.Date | None
		company: DF.Link
		cost_center: DF.Link | None
		credit_account: DF.Link
		default_region_cost_center: DF.Link | None
		from_date: DF.Date
		items: DF.Table[TDSRemittanceItem]
		mode_of_payment: DF.Link
		pay_to_recd_from: DF.Data | None
		posting_date: DF.Date
		purpose: DF.Literal["", "Other Invoice"]
		reference_date: DF.Data | None
		reference_number: DF.Data | None
		region: DF.Data | None
		remarks: DF.SmallText | None
		tax_withholding_category: DF.Link
		to_date: DF.Date
		total_amount: DF.Currency
		total_tds: DF.Currency
		use_cheque_lot: DF.Check
	# end: auto-generated types
	
	def validate(self):
		self.calculate_total()

	def on_submit(self):
		self.make_gl_entries()

	def on_cancel(self):
		check_clearance_date(self.doctype, self.name)
		self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry", "Payment Ledger Entry")
		self.make_gl_entries()
	def get_condition(self):
		if self.branch:
			return ' AND t.branch ="{}" '.format(self.branch)
		return ''
	@frappe.whitelist()
	def get_details(self):
		total_tds_amount = total_bill_amount = 0

		if self.purpose != 'Other Invoice':
			return total_tds_amount, total_bill_amount
		cond = self.get_condition()

		entries = get_tds_invoices(self.tax_withholding_category,self.company, self.from_date, self.to_date, \
			self.name, filter_existing=True, cond= cond, cost_center=self.cost_center)
		
		if not entries:
			frappe.msgprint(_("No Records Found"))

		self.set('items', [])
		for d in entries:
			d.bill_amount 		= flt(d.bill_amount,2)
			d.tds_amount 		= flt(d.tds_amount,2)
			total_tds_amount 	+= flt(d.tds_amount)
			total_bill_amount 	+= flt(d.bill_amount)
			row 				= self.append('items', {})
			row.update(d)
		return total_tds_amount, total_bill_amount

	def calculate_total(self):
		self.total_tds = self.total_amount = 0
		for d in self.items:
			self.total_tds 		+= flt(d.tds_amount)
			self.total_amount 	+= flt(d.bill_amount)

	def make_gl_entries(self):
		gl_entries   = []
		tds_account  = get_tds_account(self.tax_withholding_category,self.company)

		if flt(self.total_tds) > 0:
			for item in self.items:
				gl_entries.append(
					self.get_gl_dict({
						"account": str(item.tax_account),
						"debit": item.tds_amount,
						"debit_in_account_currency": item.tds_amount,
						"voucher_type": self.doctype,
						"voucher_no": self.name,
						"cost_center": item.cost_center,
						"against_voucher_type":	item.invoice_type,
						"against_voucher": item.invoice_no
					},
					account_currency= "BTN"))
			
			gl_entries.append(
				self.get_gl_dict({
					"account": str(self.credit_account),
					"credit": self.total_tds,
					"credit_in_account_currency": self.total_tds,
					"voucher_type": self.doctype,					
					"voucher_no": self.name,
					"cost_center": self.cost_center,
					"against_voucher_type":	self.doctype,
					"against_voucher": self.name,
				},
				account_currency="BTN"))
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
		else:
			frappe.throw("Total TDS Amount is Zero.")


def get_tds_invoices(tax_withholding_category,company, from_date, to_date, name, filter_existing = False, cond='', party_type = None, cost_center = None):
	
	accounts_cond = accounts_cond_ti = accounts_cond_eme = existing_cond = party_cond = cost_center_cond=je_cost_center_cond="" 

	entries = pi_entries = pe_entries = je_entries = []

	if cost_center:
		cost_center_cond =  "and t.cost_center = '{cost_center}'".format(cost_center=cost_center)
		je_cost_center_cond="and t1.cost_center = '{cost_center}'".format(cost_center=cost_center)

	if not tax_withholding_category:
		frappe.msgprint(_("<b>Tax Withholding Category</b> is mandatory"))
		return entries
	
		

	def _get_existing_cond():
		return """ and not exists (select 1 from `tabTDS Remittance Item` i
			inner join `tabTDS Remittance` r
			on i.parent = r.name
			where r.name != "{name}"
			and i.invoice_no = t.name
			and r.docstatus != 2)
			and not exists(select 1
				from `tabTDS Receipt Entry`	re
				where re.invoice_no = t.name)""".format(name=name,cost_center=cost_center)

	accounts = [i.account for i in frappe.db.get_all("Tax Withholding Account", \
		{"parent": tax_withholding_category,"company":company}, "account")]
	# frappe.throw(str(accounts))
	if not len(accounts):
		return entries
	elif len(accounts) == 1:
		accounts_cond = 'and t1.account_head = "{}"'.format(accounts[0])
		accounts_cond_ti = 'and t1.account = "{}"'.format(accounts[0])
		accounts_cond_eme = 'and t.tds_account = "{}"'.format(accounts[0])
	else:
		accounts_cond = 'and t1.account_head in ({})'.format('"' + '","'.join(accounts) + '"')
		accounts_cond_ti = 'and t1.account in ({})'.format('"' + '","'.join(accounts) + '"')
		accounts_cond_eme = 'and t.tds_account in ({})'.format('"' + '","'.join(accounts) + '"')

	if filter_existing:
		existing_cond = _get_existing_cond()
	
	# Purchase Invoice
	if not party_type or party_type == "Supplier":
		tax = 0
		if tax_withholding_category == 'TDS - 2%':
			tax = 2
		if tax_withholding_category == 'TDS - 3%':
			tax = 3
		if tax_withholding_category == 'TDS - 5%':
			tax = 5
		if tax_withholding_category == 'TDS - 10%':
			tax = 10
		
		pi_entries = frappe.db.sql("""select t.posting_date, 'Purchase Invoice' as invoice_type, t.name as invoice_no,  
				'Supplier' as party_type, t.supplier as party, (select supplier_tpn_no from `tabSupplier` where name = t.supplier) as tpn, 
				t.cost_center,
				t1.total as bill_amount, 
				(case when t1.base_tax_amount_after_discount_amount > 0 then t1.base_tax_amount_after_discount_amount else t1.tax_amount end) tds_amount,
				t1.account_head as tax_account, tre.tds_remittance, tre.tds_receipt_update,t.bill_no, t.bill_date,
				(case when tre.tds_receipt_update is not null then 'Paid' else 'Unpaid' end) remittance_status
			from `tabPurchase Invoice` t 
				inner join `tabPurchase Taxes and Charges` t1 on t.name = t1.parent
				left join `tabSupplier` s on s.name = t.supplier
				left join `tabTDS Receipt Entry` tre on tre.invoice_no = t.name 
			where t.posting_date between '{from_date}' and '{to_date}'
			{accounts_cond}
			and t.docstatus = 1
			and t1.rate = {rate}
			{cost_center_cond}
			{existing_cond}
			{cond}""".format(accounts_cond = accounts_cond, cond = cond, cost_center_cond=cost_center_cond,existing_cond = existing_cond,\
				from_date=from_date, to_date=to_date, cost_center=cost_center,rate=tax), as_dict=True)

	# Payment Entry
	if party_type:
		party_cond = "and t.party_type = '{}'".format(party_type)
	pe_entries = frappe.db.sql("""select t.posting_date, t.name as invoice_no, 'Payment Entry' as invoice_type,
			t.party_type, t.party, 
			(case when t.party_type = 'Customer' then c.tax_id when t.party_type = 'Supplier' then s.supplier_tpn_no else null end) as tpn, 
			t.cost_center,
			case when t1.base_total > 0 then (t1.base_tax_amount + t1.base_total) else (t1.tax_amount + t1.total) end as bill_amount, 
			case when t1.base_tax_amount > 0 then t1.base_tax_amount else t1.tax_amount end as tds_amount,
			t1.account_head as tax_account, tre.tds_remittance, tre.tds_receipt_update,
			(case when tre.tds_receipt_update is not null then 'Paid' else 'Unpaid' end) remittance_status
		from `tabPayment Entry` as t
			inner join `tabAdvance Taxes and Charges` t1 on t.name = t1.parent
			left join `tabCustomer` c on t.party_type = 'Customer' and c.name = t.party
			left join `tabSupplier` s on t.party_type = 'Supplier' and s.name = t.party
			left join `tabTDS Receipt Entry` tre on tre.invoice_no = t.name 
		where t.posting_date between '{from_date}' and '{to_date}'
		{accounts_cond}
		and t.docstatus = 1
		and t.tax_withholding_category = "{tax_withholding_category}"
		{cost_center_cond}
		{existing_cond}
		{party_cond}
		{cond}""".format(accounts_cond = accounts_cond, cost_center_cond=cost_center_cond,cond = cond, existing_cond = existing_cond,\
			party_cond = party_cond, from_date=from_date, to_date=to_date,tax_withholding_category=tax_withholding_category), as_dict=True)
	
	# Journal Entry
	if len(accounts) == 1:
		accounts_cond = """and (t1.account = "{0}" or 
			(t1.tax_account = "{0}" and ifnull(t1.apply_tds,0) = 1))""".format(accounts[0])
	else:
		accounts_cond = """and (t1.account in ({0}) or 
			t1.tax_account in ({0}) and ifnull(t1.apply_tds,0) = 1))""".format('"' + '","'.join(accounts) + '"')
	
	if party_type:
		party_cond = "and t1.party_type = '{}'".format(party_type)
	# frappe.throw(str(accounts_cond))

	je_entries = frappe.db.sql("""select t.posting_date, t.name as invoice_no, 'Journal Entry' as invoice_type,
		t1.party_type, t1.party, 
		(case when t1.party_type = 'Customer' then c.tax_id 
			when t1.party_type = 'Supplier' then s.supplier_tpn_no else null end) as tpn, 
		t1.cost_center,
		(case when t1.tax_amount > 0 and t1.debit > 0 and ifnull(t1.apply_tds) = 1 
				then t1.taxable_amount 
			else 0 end) as bill_amount, 
		(case when t1.tax_amount > 0 and t1.debit > 0 and ifnull(t1.apply_tds) = 1 
				then t1.tax_amount
			when t1.tax_amount = 0 and t1.credit > 0 then t1.credit
			else 0 end) as tds_amount,
		(case when t1.tax_amount > 0 and t1.debit > 0 and ifnull(t1.apply_tds) = 1 
				then t1.tax_account
			else t1.account end) as tax_account, tre.tds_remittance, tre.tds_receipt_update, t.bill_no, t.bill_date,
		(case when tre.tds_receipt_update is not null then 'Paid' else 'Unpaid' end) remittance_status
		from `tabJournal Entry` as t
			inner join `tabJournal Entry Account` t1 on t.name = t1.parent
			left join `tabCustomer` c on t1.party_type = 'Customer' and c.name = t1.party
			left join `tabSupplier` s on t1.party_type = 'Supplier' and s.name = t1.party
			left join `tabTDS Receipt Entry` tre on tre.invoice_no = t.name 
		where t.posting_date between '{from_date}' and '{to_date}'
		{accounts_cond}
		and t.docstatus = 1 and t.apply_tds = 1 and t.tax_withholding_category = "{tax_withholding_category}"
		{je_cost_center_cond}
		{existing_cond}
		{party_cond}
		{cond}""".format(accounts_cond = accounts_cond, je_cost_center_cond=je_cost_center_cond,cond = cond, existing_cond = existing_cond,\
			party_cond = party_cond, from_date=from_date, to_date=to_date, cost_center=cost_center,tax_withholding_category=tax_withholding_category), as_dict=True)

	for i in je_entries:
		# frappe.throw(str(i))
		party = frappe.db.get_value("GL Entry",{'voucher_no':i['invoice_no'],'account':i['tax_account']},'against')
		party_type = frappe.db.get_value("GL Entry",{'voucher_no':i['invoice_no'],'party':party},'party_type')

		i['party'] = party
		i['party_type']= party_type
		
	# Transporter Invoice
	# ti_entries = frappe.db.sql("""select t.posting_date, t.name as invoice_no, 'Transporter Invoice' as invoice_type,
	# 			'Supplier' as party_type, t.supplier as party, 
	# 			(select supplier_tpn_no from `tabSupplier` where name = t.supplier) as tpn, 
	# 			t.cost_center,
	# 			t.gross_amount as bill_amount, 
	# 			t.tds_amount,
	# 			t1.account as tax_account, tre.tds_remittance, tre.tds_receipt_update,
	# 			(case when tre.tds_receipt_update is not null then 'Paid' else 'Unpaid' end) remittance_status
	# 			from `tabTransporter Invoice` t 
	# 				inner join `tabTransporter Invoice Deduction` t1 on t1.parent = t.name
	# 				left join `tabTDS Receipt Entry` tre on tre.invoice_no = t.name 
	# 			where t.posting_date between '{from_date}' and '{to_date}'
	# 			and t.tds_amount > 0
	# 			{accounts_cond}
	# 			and t.docstatus = 1
	# 			{existing_cond}
	# 			{cond}
	# 			""".format(accounts_cond = accounts_cond_ti, cond = cond, existing_cond = existing_cond,\
	# 					party_cond = party_cond, from_date=from_date, to_date=to_date), as_dict=True)
	# EME Invoice
	# eme_entries = frappe.db.sql("""select t.posting_date, t.name as invoice_no, 'EME Invoice' as invoice_type,
	# 			'Supplier' as party_type, t.supplier as party, 
	# 			(select supplier_tpn_no from `tabSupplier` where name = t.supplier) as tpn, 
	# 			t.cost_center, t.bill_no, t.bill_date,
	# 			t.grand_total as bill_amount, 
	# 			t.tds_amount,
	# 			t.tds_account as tax_account, tre.tds_remittance, tre.tds_receipt_update,
	# 			(case when tre.tds_receipt_update is not null then 'Paid' else 'Unpaid' end) remittance_status
	# 			from `tabEME Invoice` t 
	# 				left join `tabTDS Receipt Entry` tre on tre.invoice_no = t.name 
	# 			where t.posting_date between '{from_date}' and '{to_date}'
	# 			and t.tds_amount > 0
	# 			{accounts_cond}
	# 			and t.docstatus = 1
	# 			{existing_cond}
	# 			{cond}
	# 			""".format(accounts_cond = accounts_cond_eme, cond = cond, existing_cond = existing_cond,\
	# 					party_cond = party_cond, from_date=from_date, to_date=to_date), as_dict=True)
	# repair and service invoice 
	# r_and_s_entries = frappe.db.sql("""select t.posting_date, t.name as invoice_no, 
	# 			'Repair And Service Invoice' as invoice_type,t.party_type, t.party, 
	# 			(CASE WHEN t.party_type = 'Supplier' THEN (select supplier_tpn_no from `tabSupplier` where name = t.party) ELSE '' END)tpn, t.cost_center, t.bill_no, t.bill_date,
	# 			t.grand_total as bill_amount, 
	# 			t.tds_amount,
	# 			t.tds_account as tax_account, tre.tds_remittance, tre.tds_receipt_update,
	# 			(case when tre.tds_receipt_update is not null then 'Paid' else 'Unpaid' end) remittance_status
	# 			from `tabRepair And Service Invoice` t 
	# 				left join `tabTDS Receipt Entry` tre on tre.invoice_no = t.name 
	# 			where t.posting_date between '{from_date}' and '{to_date}'
	# 			and t.tds_amount > 0
	# 			and t.party_type = 'Supplier'
	# 			{accounts_cond}
	# 			and t.docstatus = 1
	# 			and t.cost_center = '{cost_center}'
	# 			{existing_cond}
	# 			{cond}
	# 			""".format(accounts_cond = accounts_cond_eme, cond = cond, existing_cond = existing_cond,\
	# 					party_cond = party_cond, from_date=from_date, to_date=to_date, cost_center=cost_center), as_dict=True)
	entries = pi_entries + pe_entries + je_entries
	entries = sorted(entries, key=lambda d: (d['posting_date'], d['invoice_no']))
	return entries

@frappe.whitelist()
def create_tds_receipt_update(source_name, target_doc=None):
	doclist = get_mapped_doc("TDS Remittance", source_name, {
		"TDS Remittance": {
			"doctype": "TDS Receipt Update",
			"field_map":{
				"total_amount":"total_bill_amount",
				"total_tds":"total_tax_amount"
			}
		},
		"TDS Remittance Item":{
			"doctype":"TDS Remittance Item"
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def get_tds_receipt_update(tds_remittance):
	res = frappe.db.sql("""select parent as tds_receipt_update
			from `tabTDS Remittance Item`
			where parenttype = 'TDS Receipt Update'
			and tds_remittance = "{tds_remittance}"
			and docstatus != 2
			limit 1
		""".format(tds_remittance=tds_remittance), as_dict=True)
	return res[0] if res else None

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles or "Accounts User" in user_roles: 
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabTDS Remittance`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabTDS Remittance`.branch)
	)""".format(user=user)
