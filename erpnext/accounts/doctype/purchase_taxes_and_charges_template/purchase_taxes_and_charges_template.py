# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.model.document import Document

from erpnext.accounts.doctype.sales_taxes_and_charges_template.sales_taxes_and_charges_template import (
	valdiate_taxes_and_charges_template,
)


class PurchaseTaxesandChargesTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.purchase_taxes_and_charges.purchase_taxes_and_charges import PurchaseTaxesandCharges
		from frappe.types import DF

		company: DF.Link
		disabled: DF.Check
		is_default: DF.Check
		tax_category: DF.Link | None
		taxes: DF.Table[PurchaseTaxesandCharges]
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		valdiate_taxes_and_charges_template(self)

	def autoname(self):
		if self.company and self.title:
			abbr = frappe.get_cached_value("Company", self.company, "abbr")
			self.name = f"{self.title} - {abbr}"
	def after_insert(self):
		"""
		After creating a Purchase Taxes and Charges Template:
		- Copy it to all child companies.
		- Map parent accounts to child company accounts using company abbreviation.
		- Skip tax rows if the account does not exist in child company.
		"""

		# Fetch all child companies of this parent company
		child_companies = frappe.get_all(
			"Company",
			filters={"parent_company": self.company},
			pluck="name"
		)

		if not child_companies:
			return

		for child in child_companies:

			# Skip if template already exists for this child
			if frappe.db.exists(
				"Purchase Taxes and Charges Template",
				{"company": child, "title": self.title}
			):
				continue

			# Get child company abbreviation
			child_abbr = frappe.get_cached_value("Company", child, "abbr")

			# Create new template for child company
			new_template = frappe.new_doc("Purchase Taxes and Charges Template")
			new_template.title = self.title
			new_template.company = child
			new_template.disabled = self.disabled
			new_template.is_default = self.is_default
			new_template.tax_category = self.tax_category

			# Copy each tax row, map to child company account
			for tax in self.taxes:
				# Base account: e.g., "4-151 - 10% TDS"
				base_name_parts = tax.account_head.split(" - ")[:2]
				base_account_name = tax.account_head.rsplit(" - ", 1)[0]

				# base_account_name = " - ".join(base_name_parts)

				# Child account: "4-151 - 10% TDS - OVC"
				child_account_name = f"{base_account_name} - {child_abbr}"

				# Lookup exact account in child company
				# frappe.throw(str(child_account_name))
				child_account = frappe.db.get_value(
					"Account",
					{"company": child, "name": child_account_name},
					"name"
				)
				# frappe.throw(frappe.as_json(child_account))

				if not child_account:
					frappe.msgprint(
						f"Skipping tax row: Account {child_account_name} does not exist in company {child}"
					)
					continue  # Skip this tax row if account missing

				new_template.append("taxes", {
					"charge_type": tax.charge_type,
					"account_head": child_account,  # exact Account.name
					"description": tax.description,
					"rate": tax.rate,
					"included_in_print_rate": tax.included_in_print_rate
				})

			# Save the new template if it has any tax rows
			if new_template.taxes:
				new_template.insert(ignore_permissions=True)

		frappe.db.commit()
		frappe.msgprint(f"Purchase Taxes and Charges Template '{self.title}' copied to child companies.")