# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompanyCompact(Document):
	def validate(self):
		self.validate_duplicate()

	@frappe.whitelist()
	def get_department_details(self):
		if self.department:
			ft_count = frappe.db.get_value("Department", self.department, "financial_tables")
			nft_count = frappe.db.get_value("Department", self.department, "non_financial_tables")
			financial_tables = frappe.db.sql("""
				select label from `tabFinancial Tables` where parent = '{}'
			""".format(self.department), as_dict=True)
			financial_tables = [table.label for table in financial_tables]
			non_financial_tables = frappe.db.sql("""
				select label from `tabNon Financial Tables` where parent = '{}'
			""".format(self.department), as_dict=True)
			non_financial_tables = [table.label for table in non_financial_tables]
			return financial_tables, non_financial_tables, ft_count, nft_count
	
	def validate_duplicate(self):
		if self.type == "Company":
			existing_compact = frappe.get_all(
				"Company Compact",
				filters={"company": self.company, "fiscal_year": self.fiscal_year, "name": ["!=", self.name]},
				limit=1,
				fields=["name"],
			)
			if existing_compact:
				frappe.throw(
					_("A compact with the same company and compact already exists: {0} for fiscal year {1}").format(existing_compact[0].name, self.fiscal_year)
				)
		else:
			existing_compact = frappe.get_all(
				"Company Compact",
				filters={"department": self.department, "fiscal_year": self.fiscal_year, "name": ["!=", self.name]},
				limit=1,
				fields=["name"],
			)
			if existing_compact:
				frappe.throw(
					_("A compact with the same department and compact already exists: {0} for fiscal_year").format(existing_compact[0].name, self.fiscal_year)
				)
