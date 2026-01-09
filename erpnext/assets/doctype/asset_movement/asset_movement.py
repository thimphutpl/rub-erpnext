# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form

from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity
from erpnext.accounts.utils import make_asset_transfer_gl


class AssetMovement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.assets.doctype.asset_movement_item.asset_movement_item import AssetMovementItem
		from frappe.types import DF

		amended_from: DF.Link | None
		asset_custodian_type: DF.Link | None
		assets: DF.Table[AssetMovementItem]
		attachment: DF.Attach | None
		company: DF.Link
		cost_center: DF.Link | None
		from_employee: DF.Link | None
		from_hostel: DF.Link | None
		from_roombuilding: DF.Link | None
		inter_company_transfer: DF.Check
		project: DF.Link | None
		purpose: DF.Literal["", "Transfer", "Receipt"]
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		to_company: DF.Link | None
		to_employee: DF.Link | None
		to_hostel: DF.Link | None
		to_roombuilding: DF.Link | None
		to_single: DF.Check
		transaction_date: DF.Datetime
		workflow_state: DF.Data | None
	# end: auto-generated types

	def validate(self):
		if self.asset_custodian_type == "Hostel Room":
			self.from_employee = None
			self.to_employee = None
		if self.purpose == 'Receipt':
			return
		self.validate_asset()
		self.validate_cost_center()
		self.validate_employee()

	def validate_asset(self):
		for d in self.assets:
			status, company = frappe.db.get_value("Asset", d.asset, ["status", "company"])
			if self.purpose == "Transfer" and status in ("Draft", "Scrapped", "Sold"):
				frappe.throw(_("{0} asset cannot be transferred").format(status))

			if self.inter_company_transfer == 0 and company != self.company:
				frappe.throw(_("Asset {0} does not belong to company {1}").format(d.asset, self.company))
			if d.to_custodian_type == "Employee" and not (d.from_employee and d.to_employee):
				if not d.source_cost_center and not d.from_employee and not d.to_employee:
					frappe.throw(_("Source Cost Center, From Employee, To Employee must be required"))

				""" update target details """
				d.target_cost_center = frappe.get_value("Employee", d.to_employee, "cost_center")
				d.to_employee_name = frappe.get_value("Employee", d.to_employee, "employee_name")
				if not d.target_cost_center:
					frappe.throw(_("Missing Cost Center value in Employee for {0}").format(d.to_employee))
			elif d.to_custodian_type == "Hostel Room" and not (d.from_employee and d.to_employee):
				if not d.source_cost_center and not d.from_employee and not d.to_employee:
					frappe.throw(_("Source Cost Center, From Hostel, To Hostel must be required"))

				""" update target details """
				d.target_cost_center = frappe.get_value("Hostel Room", d.to_employee, "cost_center")
				d.to_employee_name = frappe.get_value("Hostel Room", d.to_employee, "room_number")
				if not d.target_cost_center:
					frappe.throw(_("Missing Cost Center value in Hostel Room for {0}").format(d.to_employee))
			elif d.to_custodian_type == "Room" and not (d.from_employee and d.to_employee):
				if not d.source_cost_center and not d.from_employee and not d.to_employee:
					frappe.throw(_("Source Cost Center, From Room/Building, To Room/Building must be required"))

				""" update target details """
				d.target_cost_center = frappe.get_value("Room", d.to_employee, "cost_center")
				d.to_employee_name = frappe.get_value("Room", d.to_employee, "room_name")
				if not d.target_cost_center:
					frappe.throw(_("Missing Cost Center value in Room for {0}").format(d.to_employee))
	def validate_cost_center(self):
		for d in self.assets:
			if self.purpose in ["Transfer", "Issue"]:
				current_cost_center = frappe.db.get_value("Asset", d.asset, "cost_center")
				if d.source_cost_center:
					if current_cost_center != d.source_cost_center:
						frappe.throw(
							_("Asset {0} does not belongs to the cost center {1}").format(
								d.asset, d.source_cost_center
							)
						)
				else:
					d.source_cost_center = source_cost_center

			if self.purpose == "Issue":
				# if d.target_cost_center:
				# 	frappe.throw(
				# 		_(sxdcy
				# 			"Issuing cannot be done to a location. Please enter employee to issue the Asset {0} to"
				# 		).format(d.asset),
				# 		title=_("Incorrect Movement Purpose"),
				# 	)
				if not d.to_employee:
					frappe.throw(_("Employee is required while issuing Asset {0}").format(d.asset))

			if self.purpose == "Transfer":
				if not d.to_employee:
					frappe.throw(
						_(
							"Missing To Employee/Hostel/Room/Building at #Row:{0}"
						).format(d.idx),
						title=_("Missing Value"),
					)
				if not d.target_cost_center:
					frappe.throw(
						_("Target Cost Center is required while transferring Asset at #Row:{0}").format(d.idx)
					)
				# if d.source_location == d.target_location:
				# 	frappe.throw(_("Source and Target Location cannot be same"))

			if self.purpose == "Transfer":
				if not (d.to_employee or d.target_cost_center):
					frappe.throw(
						_("Target Cost Center or Employee/Hostel/Room/Building is required while transferring Asset {0}").format(d.asset)
					)

				# if d.to_employee and d.target_cost_center:
				# 	frappe.msgprint(
				# 		_("Asset {0} will be transferred to Cost Center {1} and Employee {2}").format(
				# 			d.asset, d.target_cost_center, d.to_employee
				# 		)
				# 	)
				# elif d.to_employee:
				# 	frappe.msgprint(
				# 		_("Asset {0} will be transferred to Employee {1} only").format(
				# 			d.asset, d.to_employee
				# 		)
				# 	)
				# elif d.target_cost_center:
				# 	frappe.msgprint(
				# 		_("Asset {0} will be transferred to Cost Center {1} only").format(
				# 			d.asset, d.target_cost_center
				# 		)
				# 	)

			# if self.purpose == "Receipt":
			# 	if not (d.source_location) and not (d.target_location or d.to_employee):
			# 		frappe.throw(
			# 			_("Target Location or To Employee is required while receiving Asset {0}").format(
			# 				d.asset
			# 			)
			# 		)
			# 	elif d.source_location:
			# 		if d.from_employee and not d.target_location:
			# 			frappe.throw(
			# 				_(
			# 					"Target Location is required while receiving Asset {0} from an employee"
			# 				).format(d.asset)
			# 			)
			# 		elif d.to_employee and d.target_location:
			# 			frappe.throw(
			# 				_(
			# 					"Asset {0} cannot be received at a location and given to an employee in a single movement"
			# 				).format(d.asset)
			# 			)

	def get_assets_for_employee(self):
		if self.from_employee:
			# Clear current assets in table
			self.assets = []

			# Fetch assets assigned to the selected employee
			assets = frappe.db.get_all(
				"Assets",
				filters={"custodian": self.from_employee, "company": self.company},
				fields=["name as asset", "cost_center as source_cost_center", "custodian_name as from_employee_name"]
			)

			# Add each asset to the assets table
			for asset in assets:
				self.append("assets", asset)
            
	def on_asset_fetch_button_click(self):
		# Call the function to fetch assets
		self.get_assets_for_employee()

	def validate_employee(self):
		for d in self.assets:
			if d.to_custodian_type == "Employee":
				if d.from_employee:
					current_custodian = frappe.db.get_value("Asset", d.asset, "custodian")

					if current_custodian != d.from_employee:
						frappe.throw(
							_("Asset {0} does not belongs to the custodian {1}").format(d.asset, d.from_employee)
						)
			elif d.asset_custodian_type == "Hostel Room":
				if d.from_employee:
					current_custodian = frappe.db.get_value("Asset", d.asset, "hostel")

					if current_custodian != d.from_employee:
						frappe.throw(
							_("Asset {0} does not belong to the Hostel Room {1}").format(d.asset, d.from_employee)
						)
			elif d.to_custodian_type == "Room":
				if d.from_employee:
					current_custodian = frappe.db.get_value("Asset", d.asset, "roombuilding")

					if current_custodian != d.from_employee:
						frappe.throw(
							_("Asset {0} does not belong to the Room/Building {1}").format(d.asset, d.from_employee)
						)

			if d.to_custodian_type == "Employee":
				if d.to_employee and frappe.db.get_value("Employee", d.to_employee, "company") != self.company:
					frappe.throw(
						_("Employee {0} does not belongs to the company {1}").format(d.to_employee, self.company)
					)
			elif d.to_custodian_type == "Hostel Room":
				if d.to_employee and frappe.db.get_value("Hostel Room", d.to_employee, "company") != self.company and self.inter_company_transfer == 0:
					frappe.throw(
						_("Hostel Room {0} does not belong to the company {1}").format(d.to_employee, self.company)
					)
			elif d.to_custodian_type == "Room":
				if d.to_employee and frappe.db.get_value("Room", d.to_employee, "company") != self.company and self.inter_company_transfer == 0:
					frappe.throw(
						_("Room {0} does not belongs to the company {1}").format(d.to_employee, self.company)
					)

	def before_submit(self):
		for d in self.assets:
			if d.asset_custodian_type == "Employee":
				d.from_employee = frappe.db.get_value("Asset", d.asset, "custodian")
			elif d.asset_custodian_type == "Hostel Room":
				d.from_employee = frappe.db.get_value("Asset", d.asset, "hostel")
			else:
				d.from_employee = frappe.db.get_value("Asset", d.asset, "roombuilding")
			d.from_cost_center = frappe.db.get_value("Asset", d.asset, "cost_center")
			if self.asset_custodian_type == "Employee" and self.from_employee != d.from_employee:
				frappe.throw("Asset data ("+str(d.asset)+") had changed since you created the document. Pull the assets again")
			if self.asset_custodian_type == "Hostel Room" and self.from_hostel != d.from_employee:
				frappe.throw("Asset data ("+str(d.asset)+") had changed since you created the document. Pull the assets again")
			if self.asset_custodian_type == "Room" and self.from_roombuilding != d.from_employee:
				frappe.throw("Asset data ("+str(d.asset)+") had changed since you created the document. Pull the assets again")
			if self.cost_center and self.cost_center != d.from_cost_center:
				frappe.throw("Asset data ("+str(d.asset)+") had changed since you created the document. Pull the assets again")

		for a in self.assets:
			doc_list = frappe.db.sql("select asm.name FROM `tabAsset Movement Item` asm_item, `tabAsset Movement` asm where asm_item.parent=asm.name and asm.docstatus = 1 and asm_item.asset = %s and asm.transaction_date >= %s", (a.asset, self.transaction_date), as_dict=1)
			for a in doc_list:
				frappe.throw("Cannot modify Asset <b>"+ str(a.asset) +"</b> since the asset has already been modified at through Asset Movement " + str(a.name))	

	
	def on_submit(self):
		self.set_latest_location_and_custodian_in_asset()

	def on_cancel(self):
		self.ignore_linked_doctypes = (
			"GL Entry",
			"Payment Ledger Entry",
		)
		self.set_latest_location_and_custodian_in_asset(1)

	def set_latest_location_and_custodian_in_asset(self, cancel=0):
		current_cost_center, current_employee, current_employee_name, current_hostel, current_roombuilding = "", "", "", "", ""
		cond = "1=1"

		for d in self.assets:
			args = {"asset": d.asset, "company": self.company}

			# latest entry corresponds to current document's location, employee when transaction date > previous dates
			# In case of cancellation it corresponds to previous latest document's location, employee
			latest_movement_entry = frappe.db.sql(
				f"""
				SELECT asm_item.target_cost_center, asm_item.to_employee, asm_item.to_employee_name, asm_item.asset_custodian_type
				FROM `tabAsset Movement Item` asm_item, `tabAsset Movement` asm
				WHERE
					asm_item.parent=asm.name and
					asm_item.asset=%(asset)s and
					asm.company=%(company)s and
					asm.docstatus=1 and {cond}
				ORDER BY
					asm.transaction_date desc limit 1
				""",
				args,
			)
			if latest_movement_entry:
				current_cost_center = latest_movement_entry[0][0]
				if latest_movement_entry[0][3] == "Employee":
					current_employee = latest_movement_entry[0][1]
				elif latest_movement_entry[0][3] == "Hostel Room":
					current_hostel = latest_movement_entry[0][1]
				elif latest_movement_entry[0][3] == "Room":
					current_roombuilding = latest_movement_entry[0][1]
				current_employee_name = latest_movement_entry[0][2]

			branch = frappe.get_value("Branch", {"cost_center": d.target_cost_center if not cancel else d.source_cost_center}, "name")
			from_custodian = self.from_roombuilding if self.asset_custodian_type == "Room" else (self.from_hostel if self.asset_custodian_type == "Hostel Room" else self.from_employee)
			frappe.db.set_value("Asset", d.asset, "branch", branch, update_modified=False)
			frappe.db.set_value("Asset", d.asset, "cost_center", d.target_cost_center if not cancel else d.source_cost_center, update_modified=False)
			frappe.db.set_value("Asset", d.asset, "is_hostel_asset", d.to_custodian_type if not cancel else d.asset_custodian_type, update_modified=False)
			frappe.db.set_value("Asset", d.asset, "company", self.to_company if not cancel else self.company, update_modified=False)
			if d.to_custodian_type == "Employee":
				frappe.db.set_value("Asset", d.asset, "custodian", current_employee, update_modified=False)
				frappe.db.set_value("Asset", d.asset, "custodian_name", current_employee_name, update_modified=False)
			elif d.to_custodian_type == "Hostel Room":
				frappe.db.set_value("Asset", d.asset, "hostel", d.to_employee if not cancel else d.from_employee, update_modified=False)
			elif d.to_custodian_type == "Room":
				frappe.db.set_value("Asset", d.asset, "roombuilding", d.to_employee if not cancel else d.from_employee, update_modified=False)

			equipment = frappe.db.get_value("Equipment", {"asset_code": d.asset}, "name")
			if equipment:
				equip = frappe.get_doc("Equipment", equipment)
				equip.branch = branch
				equip.save()
			""" Asset transfer gl """
			if d.source_cost_center != d.target_cost_center and self.purpose == "Transfer":
				self.posting_date = self.transaction_date
				make_asset_transfer_gl(self, d.asset, self.transaction_date, d.source_cost_center, d.target_cost_center, cancel)

			if current_cost_center and current_employee:
				add_asset_activity(
					d.asset,
					_("Asset received at Cost Center {0} and issued to Employee {1}").format(
						get_link_to_form("Cost Center", current_cost_center),
						get_link_to_form("Employee", current_employee),
					),
				)
			elif current_cost_center and current_hostel:
				add_asset_activity(
					d.asset,
					_("Asset transferred to Cost Center {0} and issued to Hostel Room {1}").format(
						get_link_to_form("Cost Center", current_cost_center),
						get_link_to_form("Hostel Room", current_hostel),
					),
				)
			elif current_cost_center and current_roombuilding:
				add_asset_activity(
					d.asset,
					_("Asset transferred to Cost Center {0} and issued to Room/Building {1}").format(
						get_link_to_form("Cost Center", current_cost_center),
						get_link_to_form("Room", current_roombuilding),
					),
				)
			elif current_cost_center:
				add_asset_activity(
					d.asset,
					_("Asset transferred to Cost Center {0}").format(
						get_link_to_form("Cost Center", current_cost_center)
					),
				)
			elif current_employee:
				add_asset_activity(
					d.asset,
					_("Asset issued to Employee {0}").format(get_link_to_form("Employee", current_employee)),
				)
			elif current_hostel:
				add_asset_activity(
					d.asset,
					_("Asset issued to Hostel Room {0}").format(get_link_to_form("Hostel Room", current_hostel)),
				)
			elif current_roombuilding:
				add_asset_activity(
					d.asset,
					_("Asset issued to Room/Building {0}").format(get_link_to_form("Room", current_roombuilding)),
				)

	@frappe.whitelist()
	def get_asset_list(self):
		custodian_count = 0
		to_custodian_type = "Employee" if self.to_employee else ("Hostel Room" if self.to_hostel else "Room")
		if not self.from_employee and self.asset_custodian_type == 'Employee' :
			frappe.throw("From Employee is required.")
		elif not self.from_hostel and self.asset_custodian_type == 'Hostel Room' :
			frappe.throw("From Hostel is required.")
		elif not self.from_roombuilding and self.asset_custodian_type == 'Room' :
			frappe.throw("From Room/Building is required.")
		else:
			if self.to_single:
				if self.to_employee:
					custodian_count += 1
				if self.to_hostel:
					custodian_count += 1
				if self.to_roombuilding:
					custodian_count += 1
				if custodian_count > 1:
					frappe.throw("Select only one To Custodian")
				if custodian_count == 0:
					frappe.throw("Select To Custodian")
				if self.from_employee == self.to_employee and self.to_employee:
					frappe.throw("Select Different Employee")
				if self.from_hostel == self.to_hostel and self.to_hostel:
					frappe.throw("Select Different Hostel")
				if self.from_roombuilding == self.to_roombuilding and self.to_roombuilding:
					frappe.throw("Select Different Room/Building")
			else:
				self.to_employee=''

			condition_statement=''
			if self.asset_custodian_type == 'Employee':
				condition_statement = f"custodian = '{self.from_employee}'"
			elif self.asset_custodian_type == 'Hostel Room':
				condition_statement = f"hostel = '{self.from_hostel}'"
			elif self.asset_custodian_type == 'Room':
				condition_statement = f"roombuilding = '{self.from_roombuilding}'"
			elif self.cost_center:
				condition_statement = f"cost_center = '{self.cost_center}'"
			
			asset_list = frappe.db.sql("""
				select name, custodian_name, custodian, cost_center, is_hostel_asset, hostel, roombuilding
				from `tabAsset` 
				where {cond} 
				and docstatus = 1 
				""".format(cond=condition_statement),as_dict = 1)
			if asset_list:
				self.set("assets",[])
				for x in asset_list:
					row = self.append("assets",{})
					if self.to_employee:
						to_custodian = self.to_employee if self.to_single else ''
						to_cost_center = frappe.db.get_value("Employee",self.to_employee,"cost_center")
					elif self.to_hostel:
						to_custodian = self.to_hostel if self.to_single else ''
						to_cost_center = frappe.db.get_value("Hostel Room",self.to_hostel,"cost_center")
					elif self.to_roombuilding:
						to_custodian = self.to_roombuilding if self.to_single else ''
						to_cost_center = frappe.db.get_value("Room",self.to_roombuilding,"cost_center")
					else:
						to_custodian = ''
						to_cost_center = ''
					data = {"asset":x.name, 
							"from_employee":str(x.custodian) if x.is_hostel_asset == "Employee" else (x.hostel if x.is_hostel_asset == "Hostel Room" else x.roombuilding),
							"to_employee":to_custodian,
							"from_employee_name":x.custodian_name if x.is_hostel_asset == "Employee" else (frappe.db.get_value("Hostel Room", x.hostel, "room_number") if x.is_hostel_asset == "Hostel Room" else frappe.db.get_value("Room", x.roombuilding, "room_name")), 
							"source_cost_center":x.cost_center,
							"target_cost_center": to_cost_center,
							"asset_custodian_type": x.is_hostel_asset,
							"to_custodian_type": to_custodian_type
							}
					row.update(data)
			else:
				frappe.msgprint(f"No Assets registered with given Custodian/Cost Center", title="Notification", indicator='green')

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabAsset Movement`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabPurchase Invoice`.branch)
	)""".format(user=user)				