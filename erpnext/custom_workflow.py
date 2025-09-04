# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

'''
------------------------------------------------------------------------------------------------------------------------------------------
Version		  Author		 Ticket#		   CreatedOn		  ModifiedOn		  Remarks
------------ --------------- --------------- ------------------ -------------------  -----------------------------------------------------
3.0			   SHIV							 28/01/2019						  Original Version
------------------------------------------------------------------------------------------------------------------------------------------																		  
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, cint, flt
# from erpnext.hr.doctype.approver_settings.approver_settings import get_final_approver
# from erpnext.hr.hr_custom_functions import get_officiating_employee
from frappe.utils.nestedset import get_ancestors_of

class CustomWorkflow:
	def __init__(self, doc):
		self.doc = doc
		if self.doc.doctype == 'Review':
			self.new_state = self.doc.rev_workflow_state
			self.old_state = self.doc.get_db_value("rev_workflow_state")
		elif self.doc.doctype == 'Performance Evaluation':
			self.new_state = self.doc.eval_workflow_state
			self.old_state = self.doc.get_db_value("eval_workflow_state")
		else:
			self.new_state = self.doc.workflow_state
			self.old_state = self.doc.get_db_value("workflow_state")

		self.field_map 		= get_field_map()
		self.doc_approver	= self.field_map[self.doc.doctype]
		self.field_list		= ["user_id","employee_name","designation","name"]
		if self.doc.doctype not in ("Material Request", "Student Leave Application" "Performance Evaluation", "Project Capitalization","Asset Issue Details", "Compile Budget", "BTL Sales Cancellation", "Bulk Leave Encashment"):
			self.employee		= frappe.db.get_value("Employee", self.doc.employee, self.field_list)
			self.reports_to		= frappe.db.get_value("Employee", frappe.db.get_value("Employee", self.doc.employee, "reports_to"), self.field_list)
			self.supervisors_supervisor = frappe.db.get_value("Employee", frappe.db.get_value("Employee", frappe.db.get_value("Employee", self.doc.employee, "reports_to"), "reports_to"), self.field_list)
			# self.hrm_approver	= frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hrm_approver"), self.field_list)
			# self.hrd_approver	= frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hrd_approver"), self.field_list)
			self.hr_approver	= frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hrd_approver"), self.field_list)
			if self.doc.doctype in ('Travel Authorization','Travel Claim'):
				# if self.doc.reference_type in ("Project","Task"):
				# 	self.project_manager = None
				# 	if self.doc.reference_type == "Project":
				# 		self.project_manager = frappe.db.get_value("Employee",frappe.db.get_value("Project Definition",frappe.db.get_value("Project",self.doc.reference_name,"project_definition"),"project_manager"),self.field_list)
				# 	elif self.doc.reference_type == "Task":
				# 		self.project_manager = frappe.db.get_value("Employee",frappe.db.get_value("Project Definition",frappe.db.get_value("Project",frappe.db.get_value("Task",self.doc.reference_name,"project"),"project_definition"),"project_manager"),self.field_list)
				# if self.doc.travel_type not in ("Training", "Meeting and Seminars"):
				if frappe.db.get_value("Employee",self.doc.employee,"region"):
					self.ta_approver = None
					if frappe.db.get_value("Employee",self.doc.employee,"region") == "Western Region":
						# frappe.msgprint(str(frappe.db.get_value("Employee",{"user_id":a.parent},"region"))+" "+frappe.db.get_value("Employee", self.doc.employee, "region"))
						self.ta_approver = frappe.db.sql("""select user from `tabWestern Region Administrators""",as_dict=1)
					elif frappe.db.get_value("Employee",self.doc.employee,"region") == "Eastern Region":
						# frappe.msgprint(str(frappe.db.get_value("Employee",{"user_id":a.parent},"region"))+" "+frappe.db.get_value("Employee", self.doc.employee, "region"))
						# self.ta_approver = frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings","ta_eastern"), self.field_list)
						self.ta_approver = frappe.db.sql("""select user from `tabEastern Region Administrators""",as_dict=1)
					elif frappe.db.get_value("Employee",self.doc.employee,"region") == "South Western Region":
						# frappe.msgprint(str(frappe.db.get_value("Employee",{"user_id":a.parent},"region"))+" "+frappe.db.get_value("Employee", self.doc.employee, "region"))
						# self.ta_approver = frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings","ta_central"), self.field_list)
						self.ta_approver = frappe.db.sql("""select user from `tabSouth Western Region Administrators""",as_dict=1)
					elif frappe.db.get_value("Employee",self.doc.employee,"region") == "Central Region":
						# frappe.msgprint(str(frappe.db.get_value("Employee",{"user_id":a.parent},"region"))+" "+frappe.db.get_value("Employee", self.doc.employee, "region"))
						# self.ta_approver = frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings","ta_southern"), self.field_list)
						self.ta_approver = frappe.db.sql("""select user from `tabCentral Region Administrators""",as_dict=1)
					if self.ta_approver == None:
						frappe.throw("No Travel Administrator role for region "+frappe.db.get_value("Employee", self.doc.employee, "region")+" in HR Settings")
				else:
					self.ta_approver = None
					# self.ta_approver = frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings","ta_chq"), self.field_list)
					self.ta_approver = frappe.db.sql("""select user from `tabCHQ Administrators""",as_dict=1)
					if self.ta_approver == None:
						frappe.throw("Travel Administrator not set for CHQ")

			self.ceo			= frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"designation": "Chief Executive Officer", "status": "Active"},"name"), self.field_list)
			self.gmcsd			= frappe.db.get_value("Employee", frappe.db.get_value("Department", {"department_name": "Corporate Support Services Division"},"approver"), self.field_list)
			self.dept_approver	= frappe.db.get_value("Employee", frappe.db.get_value("Department", str(frappe.db.get_value("Employee", self.doc.employee, "department")), "approver"), self.field_list)
			self.gm_approver	= frappe.db.get_value("Employee", frappe.db.get_value("Department",{"department_name":str(frappe.db.get_value("Employee", self.doc.employee, "division"))}, "approver"),self.field_list)
			if self.doc.doctype in ["Employee Separation Clearance","Leave Encashment","POL","Leave Application","Travel Authorization","Travel Claim"]:
				self.inventory_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department", "Inventory Section - BTL","approver"), self.field_list)
				self.tswf_manager = frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings","tswf_manager"),self.field_list)
				self.ccs_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department","Customer Care Section - BTL","approver"),self.field_list)
				self.billing_section_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department","Billing & CRM Section - BTL","approver"),self.field_list)
				self.power_section_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department","Power Section - BTL","approver"),self.field_list)
				self.adm_section_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department","Administration Section - BTL","approver"),self.field_list)
				self.internal_audit = frappe.db.get_value("Employee", frappe.db.get_value("Department","Internal Audit - BTL","approver"),self.field_list)
				self.gm_itd = frappe.db.get_value("Employee", frappe.db.get_value("Department","Internet & IT Division - BTL","approver"),self.field_list)
				self.gm_cs = frappe.db.get_value("Employee", frappe.db.get_value("Department","Customer Services Division - BTL","approver"),self.field_list)
				self.gm_cpsd = frappe.db.get_value("Employee", frappe.db.get_value("Department","Corporate Planning & Strategy Division - BTL","approver"),self.field_list)
				self.gm_fid = frappe.db.get_value("Employee", frappe.db.get_value("Department","Finance Division - BTL","approver"),self.field_list)
				self.gmo = frappe.db.get_value("Employee", frappe.db.get_value("Department","Operations Division - BTL","approver"),self.field_list)
				self.director_t = frappe.db.get_value("Employee", frappe.db.get_value("Department","Technical Department - BTL","approver"),self.field_list)
				self.director_b = frappe.db.get_value("Employee", frappe.db.get_value("Department","Business Department - BTL","approver"),self.field_list)

			if frappe.db.get_value("Employee",self.doc.employee,"region") not in (None,'Corporate Head Quarter'):
				self.regional_director = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",self.doc.employee,"region"))+" - BTL","approver"),self.field_list)
		if self.doc.doctype == "Student Leave Application":
			pass

		if self.doc.doctype == "Performance Evaluation":
			self.employee		= frappe.db.get_value("Employee", self.doc.employee, self.field_list)
			self.reports_to		= frappe.db.get_value("Employee", frappe.db.get_value("Employee", self.doc.employee, "reports_to"), self.field_list)
			self.supervisors_supervisor = frappe.db.get_value("Employee", frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"user_id": self.doc.approver}, "name"), "reports_to"), self.field_list)
		if self.doc.doctype == "BTL Sales Cancellation":
			if frappe.db.exists("Employee", {"user_id":self.doc.owner}):
				if frappe.db.get_value("Employee",{"user_id": self.doc.owner},"region") not in (None,'Corporate Head Quarter'):
					self.regional_director = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region"))+" - BTL","approver"),self.field_list)
			if frappe.db.exists("User Mapping", {"user": self.doc.owner}):
				profit_center = frappe.db.get_value("User Mapping", {"user": self.doc.owner}, "profit_center")
				if not profit_center:
					frappe.throw("No profit center mapped for user {}".format(self.doc.owner))
				ro = frappe.db.sql("""
					   select um.user,um.employee_name from `tabUser Mapping` um, `tabUser Mapping Profit Center` umpc where umpc.parent = um.name and um.user_role = 'Revenue Officer'
					   and '{}' = umpc.profit_center group by um.user
					   """.format(profit_center))
				# if len(ro) > 1:
				# 	frappe.throw("More than one RO for profit center {}: {}".format(profit_center, ", ".join(name[1] for name in ro)))
				if not ro:
					frappe.throw("No RO found for profit center {}".format(profit_center))
				else:
					self.revenue_officer = frappe.db.get_value("Employee", {"user_id": ro[0][0]}, self.field_list)
			else:
				frappe.throw("User Mapping not found for user {}".format(self.doc.owner))
			self.general_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department",{"department_name":str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division"))},"approver"),self.field_list)
			self.reports_to		= frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"user_id":self.doc.owner}, "reports_to"), self.field_list)
			self.gm_fid = frappe.db.get_value("Employee", frappe.db.get_value("Department","Finance Division - BTL","approver"),self.field_list)
			if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,'Corporate Head Quarter'):
				self.regional_director = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region"))+" - BTL","approver"),self.field_list)
		if self.doc.doctype in ("Material Request", "Bulk Leave Encashment"):
			self.employee = frappe.db.get_value("Employee", {"user_id":self.doc.owner}, self.field_list)
			# if frappe.db.get_value("Employee", {"user_id": self.doc.owner}, "region") in ["Western Region", "South Western Region", "Eastern Region", "Central Region"]:
			if frappe.db.get_value("Employee", {"user_id": self.doc.owner}, "section"):
				self.pc_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"section"))+" - BTL","approver"),self.field_list)
			else:
				self.pc_manager = None
			if self.doc.doctype == "Material Request":
				if self.doc.reference_type == "Project":
					if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,'Corporate Head Quarter'):
						self.project_approver = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region"))+" - BTL","approver"),self.field_list)
					else:
						self.project_approver = frappe.db.get_value("Employee", frappe.db.get_value("Department",frappe.db.get_value("Project",self.doc.reference_name,"division"),"approver"),self.field_list)
				elif self.doc.reference_type == "Task":
					if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,'Corporate Head Quarter'):
						self.project_approver = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region"))+" - BTL","approver"),self.field_list)
					else:
						self.project_approver = frappe.db.get_value("Employee", frappe.db.get_value("Department",frappe.db.get_value("Project",frappe.db.get_value("Task",self.doc.reference_name,"project"),"division"),"approver"),self.field_list)
			if self.doc.doctype == "Bulk Leave Encashment":
				self.hr_approver	= frappe.db.get_value("Employee", frappe.db.get_single_value("HR Settings", "hrd_approver"), self.field_list)
			self.reports_to	= frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"user_id":self.doc.owner}, "reports_to"), self.field_list)
			self.regional_director = frappe.db.get_value("Employee", frappe.db.get_value("Department",str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region"))+" - BTL","approver"),self.field_list)
			self.general_manager = frappe.db.get_value("Employee", frappe.db.get_value("Department",{"department_name":str(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division"))},"approver"),self.field_list)
			self.ceo = frappe.db.get_value("Employee", frappe.db.get_value("Employee", {"designation": "Chief Executive Officer", "status": "Active"},"name"), self.field_list)

		self.login_user		= frappe.db.get_value("Employee", {"user_id": frappe.session.user}, self.field_list)
		#self.final_approver= frappe.db.get_value("Employee", {"user_id": get_final_approver(doc.branch)}, self.field_list)
		self.final_approver	= []

		if not self.login_user and frappe.session.user != "Administrator":
			if "PERC Member" in frappe.get_roles(frappe.session.user):
				return
			frappe.throw("{0} is not added as the employee".format(frappe.session.user))

	def update_employment_status(self):
		emp_status = frappe.db.get_value("Leave Type", self.doc.leave_type, ["check_employment_status","employment_status"])
		if cint(emp_status[0]) and emp_status[1]:
			emp = frappe.get_doc("Employee", self.doc.employee)
			emp.employment_status = emp_status[1]
			emp.save(ignore_permissions=True)

	def notify_hr(self):
		receipients = []
		email_group = frappe.db.get_single_value("HR Settings","email_group")
		if not email_group:
			frappe.throw("HR Users Email Group not set in HR Settings.")
		hr_users = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if hr_users:
			receipients = [a['email'] for a in hr_users]
			# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			# args = parent_doc.as_dict()
			args = self.doc.as_dict()
			if self.doc.doctype == "Leave Application":
				template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
					return
			else:
				template = ""
			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)

			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})

	def set_approver(self, approver_type):
		if approver_type == "Supervisor":
			officiating = get_officiating_employee(self.reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.reports_to[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.reports_to[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.reports_to[2]
		elif approver_type == "Supervisors Supervisor":
			officiating = get_officiating_employee(self.supervisors_supervisor[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.supervisors_supervisor[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.supervisors_supervisor[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.supervisors_supervisor[2]
		elif approver_type == "Project Manager":
			if self.project_manager == None:
				frappe.throw("""No Project Manager set in Project Definition <a href="#Form/Project%20Definition/{0}">{0}</a>""".format(frappe.db.get_value("Project",self.doc.reference_name,"project_definition")))
			officiating = get_officiating_employee(self.project_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.project_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.project_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.project_manager[2]
		elif approver_type == "HR":
			officiating = get_officiating_employee(self.hr_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.hr_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.hr_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.hr_approver[2]
		elif approver_type == "TravelAdmin":
			officiating = get_officiating_employee(self.ta_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.ta_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.ta_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.ta_approver[2]
		# elif approver_type == "HRD":
		# 	officiating = get_officiating_employee(self.hrd_approver[3])
		# 	if officiating:
		# 		officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
		# 	vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.hrd_approver[0]
		# 	vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.hrd_approver[1]
		# 	vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.hrd_approver[2]
		elif approver_type == "Inventory Manager":
			officiating = get_officiating_employee(self.inventory_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.inventory_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.inventory_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.inventory_manager[2]
		elif approver_type == "Revenue Officer":
			officiating = get_officiating_employee(self.revenue_officer[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.revenue_officer[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.revenue_officer[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.revenue_officer[2]
		elif approver_type == "Manager Power":
			officiating = get_officiating_employee(self.power_section_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.power_section_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.power_section_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.power_section_manager[2]
		elif approver_type == "TSWF Manager":
			officiating = get_officiating_employee(self.tswf_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.tswf_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.tswf_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.tswf_manager[2]
		elif approver_type == "CCS Manager":
			officiating = get_officiating_employee(self.ccs_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.ccs_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.ccs_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.ccs_manager[2]
		elif approver_type == "Billing Manager":
			officiating = get_officiating_employee(self.billing_section_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.billing_section_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.billing_section_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.billing_section_manager[2]
		elif approver_type == "ADM":
			officiating = get_officiating_employee(self.adm_section_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.adm_section_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.adm_section_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.adm_section_manager[2]
		elif approver_type == "Internal Audit":
			officiating = get_officiating_employee(self.internal_audit[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.internal_audit[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.internal_audit[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.internal_audit[2]
		elif approver_type == "General Manager":
			officiating = get_officiating_employee(self.general_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.general_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.general_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.general_manager[2]
		elif approver_type == "GMITD":
			officiating = get_officiating_employee(self.gm_itd[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_itd[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_itd[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_itd[2]
		elif approver_type == "GMCS":
			officiating = get_officiating_employee(self.gm_cs[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_cs[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_cs[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_cs[2]
		elif approver_type == "GMCPSD":
			officiating = get_officiating_employee(self.gm_cpsd[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_cpsd[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_cpsd[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_cpsd[2]
		elif approver_type == "GMFID":
			officiating = get_officiating_employee(self.gm_fid[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_fid[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_fid[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_fid[2]
		elif approver_type == "GMO":
			officiating = get_officiating_employee(self.gmo[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gmo[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gmo[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gmo[2]
		elif approver_type == "DirectorT":
			officiating = get_officiating_employee(self.director_t[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.director_t[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.director_t[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.director_t[2]
		elif approver_type == "DirectorB":
			officiating = get_officiating_employee(self.director_b[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.director_b[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.director_b[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.director_b[2]
		elif approver_type == "Regional Director":
			officiating = get_officiating_employee(self.regional_director[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.regional_director[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.regional_director[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.regional_director[2]
		elif approver_type == "Department Head":
			officiating = get_officiating_employee(self.dept_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.dept_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.dept_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.dept_approver[2]
		elif approver_type == "GM":
			# frappe.msgprint(str(self.gm_approver))
			officiating = get_officiating_employee(self.gm_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gm_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gm_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gm_approver[2]
		elif approver_type == "GMCSD":
			officiating = get_officiating_employee(self.gmcsd[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.gmcsd[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.gmcsd[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.gmcsd[2]
		elif approver_type == "CEO":
			officiating = get_officiating_employee(self.ceo[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.ceo[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.ceo[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.ceo[2]
		elif approver_type == "Final Approver":
			officiating = get_officiating_employee(self.final_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.final_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.final_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.final_approver[2]
		elif approver_type == "GM":
			officiating = get_officiating_employee(self.reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.reports_to[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.reports_to[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.reports_to[2]
		elif approver_type == "Project Approver":
			officiating = get_officiating_employee(self.project_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.project_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.project_approver[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.project_approver[2]
		elif approver_type == "PC Manager":
			if not frappe.db.get_value("Employee", {"user_id": self.doc.owner}, "section"):
				frappe.throw("Section is empty for MR Applicant {} in Employee Master Data".format(frappe.db.get_value("Employee", {"user_id": self.doc.owner}, "name")))
			if not self.pc_manager:
				frappe.throw("Approver not set in Department Tree for Section {}".format(frappe.db.get_value("Employee",{"user_id":self.doc.owner},"section")+" - BTL"))
			officiating = get_officiating_employee(self.pc_manager[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else self.pc_manager[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else self.pc_manager[1]
			vars(self.doc)[self.doc_approver[2]] = officiating[2] if officiating else self.pc_manager[2]
		else:
			frappe.throw(_("Invalid approver type for Workflow"))


	def apply_workflow(self):
		if (self.doc.doctype not in self.field_map) or not frappe.db.exists("Workflow", {"document_type": self.doc.doctype, "is_active": 1}):
			return

		if self.doc.doctype == "Leave Application":
			self.leave_application()	
		elif self.doc.doctype == "Leave Encashment":
			self.leave_encashment()
		elif self.doc.doctype == "Salary Advance":
			self.salary_advance()
		elif self.doc.doctype == "Bulk Leave Encashment":
			self.bulk_leave_encashment()
		elif self.doc.doctype == "Travel Authorization":
			self.travel_authorization()
		elif self.doc.doctype == "Travel Claim":
			self.travel_claim()
		elif self.doc.doctype == "Overtime Application":
			self.overtime_application()
		elif self.doc.doctype == "Material Request":
			self.material_request()		
		elif self.doc.doctype == "Festival Advance":
			self.festival_advance()
		elif self.doc.doctype == "Employee Transfer":
			self.employee_transfer()
		elif self.doc.doctype == "Employee Benefits":
			self.employee_benefits()
		elif self.doc.doctype == "Training Nomination":
			self.training_nomination()
		elif self.doc.doctype == "Training Approval Request":
			self.training_approval_request()
		elif self.doc.doctype == "Ad hoc Training Request":
			self.adhoc_training_request()
		elif self.doc.doctype == "SWS Application":
			self.sws_application()
		elif self.doc.doctype == "Assign Shift":
			self.assign_shift()
		elif self.doc.doctype == "Target Set Up":
			self.target_setup_request()
		elif self.doc.doctype == "Review":
			self.review_request()
		elif self.doc.doctype == "Performance Evaluation":
			self.performance_evaluation_request()
		elif self.doc.doctype == "PMS Appeal":
			self.pms_appeal_request()
		elif self.doc.doctype == "Employee Separation":
			self.employee_separation()
		elif self.doc.doctype == "Employee Separation Clearance":
			self.employee_separation_clearance()
		elif self.doc.doctype == "POL":
			self.pol()
		elif self.doc.doctype in ("Asset Issue Details","Project Capitalization"):
			self.asset()
		elif self.doc.doctype == "Compile Budget":
			self.compile_budget()
		elif self.doc.doctype == "BTL Sales Cancellation":
			self.btl_sales_cancellation()
		else:
			frappe.throw(_("Workflow not defined for {}").format(self.doc.doctype))
	
	def compile_budget(self):
		if not self.old_state:
			return
		elif self.old_state.lower() == "Draft".lower() and self.new_state.lower() != "Draft".lower():
			if self.new_state.lower() == "Waiting RD Approval".lower() or self.new_state.lower() == "Waiting GM Approval".lower():
				if self.doc.budget_level == "Region":
					approver = frappe.db.get_value("Employee", frappe.db.sql("select approver from tabDepartment where name like '%{}%' and is_region=1".format(self.doc.region))[0][0], self.field_list)
				elif self.doc.budget_level == "Division":
					approver = frappe.db.get_value("Employee", frappe.db.get_value("Department", self.doc.division, "approver"), self.field_list)
				officiating = get_officiating_employee(approver[3])
				if officiating:
					officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
				vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else approver[0]
				vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else approver[1]
			else:
				pass
		elif self.old_state.lower() in ("Waiting RD Approval".lower(), "Rejected by GMO".lower()) and self.new_state.lower() == "Waiting GMO Approval".lower():
			if self.doc.approver == frappe.session.user or "Accounts Manager" in frappe.get_roles(frappe.session.user):
				pass
			else:
				frappe.throw("Only <b>{}</b> can Forward/Reject".format(self.doc.approver_name))
			self.doc.old_approver_id = self.doc.approver
			self.doc.old_approver = self.doc.approver_name
			self.doc.rejected_remarks = ""

			approver = frappe.db.get_value("Employee", frappe.db.get_value("Department", "Operations Division - BTL", "approver"), self.field_list)
			officiating = get_officiating_employee(approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else approver[1]
		elif self.old_state.lower() in ("Waiting GM Approval".lower(),"Waiting RD Approval".lower()) and self.new_state.lower() in ("Rejected by GM".lower(), "Rejected by RD".lower()):
			if self.doc.approver == frappe.session.user or "Accounts Manager" in frappe.get_roles(frappe.session.user):
				pass
			else:
				frappe.throw("Only <b>{}</b> can Forward/Reject".format(self.doc.approver_name))
		elif self.old_state.lower() == "Waiting GMO Approval".lower() and self.new_state.lower() == "Rejected by GMO".lower():
			self.doc.old_approver_id = ""
			self.doc.old_approver = ""
			approver = frappe.db.get_value("Employee", frappe.db.sql("select approver from tabDepartment where name like '%{}%' and is_region=1".format(self.doc.region))[0][0], self.field_list)
			officiating = get_officiating_employee(approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, self.field_list)
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else approver[1]
		elif self.new_state.lower() == "Waiting Finance Department Approval".lower():
			if self.doc.approver == frappe.session.user or "Accounts Manager" in frappe.get_roles(frappe.session.user):
				pass
			else:
				frappe.throw("Only <b>{}</b> can Forward/Reject".format(self.doc.approver_name))
		elif self.old_state.lower() in ("Rejected by GM".lower(), "Rejected by RD".lower(), "Rejected by Finance Department".lower(), "Rejected by Management".lower(), "Rejected by Board".lower()):
			self.doc.rejected_remarks = ""

	def btl_sales_cancellation(self):
		if not frappe.db.exists("Employee", {"user_id": self.doc.owner}):
			frappe.throw("The owner of this document i.e. {} is not registered as an Employee!".format(self.doc.owner))
		if not self.old_state:
			return
		if self.new_state.lower() == "Waiting Supervisor Approval".lower():
			if self.old_state.lower() != self.new_state.lower():
				if frappe.session.user != self.doc.owner:
					frappe.throw("Only the owner of the document can request for cancellation")
			self.set_approver("Supervisor")
		elif self.new_state.lower() == "Verified by Supervisor".lower():
			if frappe.session.user != self.doc.approver:
				frappe.throw("Only {} can verify this document".format(self.doc.approver))
			if frappe.db.exists("Employee", {"user_id": self.doc.owner}):
				region = frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region")
				if region not in (None,"Corporate Head Quarter") and self.doc.owner != self.regional_director[0]:
					self.set_approver("Regional Director")
				else:
					self.set_approver("General Manager")
		elif self.new_state.lower() == "Waiting GMF Approval".lower():
			if frappe.session.user != self.doc.approver:
				frappe.throw("Only {} can verify this document".format(self.doc.approver))
			self.set_approver("GMFID")
		elif self.new_state.lower() == "Verified".lower():
			if frappe.session.user != self.doc.approver:
				frappe.throw("Only {} can verify this document".format(self.doc.approver))
			self.set_approver("Revenue Officer")
		
	def training_nomination(self):		
		if not self.old_state:	 
			return
		elif self.old_state.lower() == "Draft".lower() and self.new_state.lower() != "Draft".lower():
			if self.doc.training_category == "Third Country" and self.doc.training_mode == "Regular":
				self.doc.workflow_state = "Waiting CEO Approval"
			elif self.doc.training_category == "India" and self.doc.training_mode == "Regular":
				self.doc.workflow_state = "Waiting Director, CA Approval" 
			# elif self.doc.training_category == "Third Country" or self.doc.training_category == "India" or self.doc.training_category == "In-Country" and self.doc.training_mode == "Online" and self.is_professional == 1:
			#	 self.doc.workflow_state = "Waiting Director, CA Approval" 
			elif self.doc.training_category == "Third Country" or self.doc.training_category == "India" or self.doc.is_professional_certificate == 1 and self.doc.training_mode == "Online":
				self.doc.workflow_state = "Waiting Director, CA Approval" 
			else:
				self.doc.workflow_state = "Waiting Chief, PCD Approval"

	def training_approval_request(self):		
		if not self.old_state:	 
			return
		elif self.old_state.lower() == "Draft".lower() and self.new_state.lower() != "Draft".lower():
			if self.doc.training_category == "Third Country" and self.doc.training_mode == "Regular":
				self.doc.workflow_state = "Waiting CEO Approval"
			elif self.doc.training_category == "India" and self.doc.training_mode == "Regular":
				self.doc.workflow_state = "Waiting Director, CA Approval"			
			elif self.doc.training_category == "Third Country" or self.doc.training_category == "India" or self.doc.is_professional == 1 and self.doc.training_mode == "Online":
				self.doc.workflow_state = "Waiting Director, CA Approval"  
					
			else:
				self.doc.workflow_state = "Waiting Chief, PCD Approval"

	def target_setup_request(self):
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.set_manual_approver == 1:
				return
			else:
				self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if ("HR User" in frappe.get_roles(frappe.session.user) or "HR Manager" in frappe.get_roles(frappe.session.user)) and self.doc.employee != frappe.db.get_value('Employee',{'user_id':frappe.session.user},'name') : 
				return
			if self.doc.user_id != frappe.session.user and self.doc.approver != frappe.session.user :
				frappe.throw("Only <b>{}</b> or <b>{}</b> can Apply or make changes to this Target".format(self.doc.employee_name, self.doc.approver_name))
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Approve/Reject this Target".format(self.doc.approver_name))

	def review_request(self):
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.set_manual_approver == 1:
				return
			else:
				self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if ("HR User" in frappe.get_roles(frappe.session.user) or "HR Manager" in frappe.get_roles(frappe.session.user)) and self.doc.employee != frappe.db.get_value('Employee',{'user_id':frappe.session.user},'name') : 
				return
			if self.doc.user_id != frappe.session.user and self.doc.approver != frappe.session.user :
				frappe.throw("Only <b>{}</b> or <b>{}</b> can Apply or make changes to this Target".format(self.doc.employee_name, self.doc.approver_name))
			
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only <b>{}</b> can Approve/Reject this Target".format(self.doc.approver_name))

	def performance_evaluation_request(self):
		if not self.new_state:
			frappe.throw('Due to slow network/some other issue this document faced issue to save. Please reload the page and save again.')
		if self.new_state.lower() in ("Draft".lower()):
			if (self.doc.owner != frappe.session.user and self.doc.approver != frappe.session.user):
				frappe.throw("Only {} or {} can Apply or make changes to this Request".format(self.doc.employee_name, self.doc.approver_name))	
			if self.doc.set_manual_approver == 1:
				return
			else:
				self.set_approver("Supervisor")

		elif self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			# to accomodate the approver changes made manually for PMS Calendar 2021
			if self.doc.set_manual_approver != 1:
				self.set_approver("Supervisor")
			elif self.doc.set_manual_approver == 1:
				if self.old_state.lower() == "Rejected".lower():
					self.doc.approver = self.doc.approver_in_first_level
					self.doc.approver_name = self.doc.approver_fl_name
					self.doc.approver_designation = self.doc.approver_fl_designation
				else:
					return
			if ("HR User" in frappe.get_roles(frappe.session.user) or "HR Manager" in frappe.get_roles(frappe.session.user)) and self.doc.employee != frappe.db.get_value('Employee',{'user_id':frappe.session.user},'name') : 
				return
			if (self.doc.owner != frappe.session.user and self.doc.approver != frappe.session.user):
				frappe.throw("Only {} or {} can Apply or make changes to this Request".format(self.doc.employee_name, self.doc.approver_name))
			
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward/Reject this Target".format(self.doc.approver_name))
			self.set_approver("Supervisors Supervisor")
			if "HR User" in frappe.get_roles(frappe.session.user) or "HR Manager" in frappe.get_roles(frappe.session.user): 
				return	
		elif self.new_state.lower() in ("Approved".lower(), "Waiting PERC".lower(), "Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Forward/Reject this Target".format(self.doc.approver_name))
		elif self.new_state.lower() in ("Approved By PERC".lower(), "Rejected By PERC".lower()):
			if "PERC Member" in frappe.get_roles(frappe.session.user):
				return
			else:
				frappe.throw("Only PERC Member can Approve/Reject this Target")

	def pms_appeal_request(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting PERC".lower(), "Waiting CEO Approval".lower()):
			if "PERC Member" in frappe.get_roles(frappe.session.user):
				return
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this PMS Appeal".format(self.doc.employee_name))
		elif self.new_state.lower() in ("Approved By PERC".lower(), "Rejected By PERC".lower()):
			if self.doc.owner == frappe.session.user:
				return
			if "PERC Member" in frappe.get_roles(frappe.session.user):
				return
			else:
				frappe.throw("Only {} PERC Member can Approve/Reject this PMS Appeal")
		elif self.new_state.lower() in ("Approved By CEO".lower(), "Rejected By CEO".lower()):
			if "CEO" in frappe.get_roles(frappe.session.user):
				return
			else:
				frappe.throw("Only CEO can Approve/Reject this PMS Appeal")

	def employee_separation(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting HR Approval".lower()):
			if self.new_state.lower() == "Waiting HR Approval".lower() and self.doc.owner != frappe.session.user:
				if "HR User" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only {} can Apply this Appeal".format(self.doc.employee_name))
			self.set_approver("HR")
		elif self.new_state.lower() in ("Submitted".lower()):
			if "HR User" not in frappe.get_roles(frappe.session.user):
				if self.doc.approver != frappe.session.user:
					frappe.throw("Only {} can edit/submit this documents".format(self.doc.approver))

	def employee_separation_clearance(self):
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only {} can Apply this Document".format(self.doc.employee_name))
			self.set_approver("Supervisor")
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting RD Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("Regional Director")
		elif self.new_state.lower() in ("Waiting Inventory Section Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("Inventory Manager")
		elif self.new_state.lower() in ("Waiting Secretary TSWF Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("TSWF Manager")
		elif self.new_state.lower() in ("Waiting Customer Care Service Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("CCS Manager")
		elif self.new_state.lower() in ("Waiting Billing Section Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("Billing Manager")
		elif self.new_state.lower() in ("Waiting Administration Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("ADM")
		elif self.new_state.lower() in ("Waiting Internal Audit Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("Internal Audit")
		elif self.new_state.lower() in ("Waiting IT Division Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("GMITD")
		elif self.new_state.lower() in ("Waiting Marketing Division Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("GMCS")
		elif self.new_state.lower() in ("Waiting CPSD Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("GMCPSD")
		elif self.new_state.lower() in ("Waiting FID Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("GMFID")
		elif self.new_state.lower() in ("Waiting Operations Division Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("GMO")
		elif self.new_state.lower() in ("Waiting CSD Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("GMCSD")
		elif self.new_state.lower() in ("Waiting Director, Technical Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("DirectorT")
		elif self.new_state.lower() in ("Waiting Director, Business Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("DirectorB")
		elif self.new_state.lower() in ("Waiting HR Approval".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit this document".format(self.doc.approver))
			self.set_approver("HR")
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit/approve this document".format(self.doc.approver))
		elif self.new_state.lower() in ("Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can reject/approve this document".format(self.doc.approver))

	def pol(self):
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.approver and self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can approve this document".format(self.doc.approver))
			if self.doc.region and self.doc.region != "Corporate Head Quarter":
				self.set_approver("Regional Director")
			else:
				if self.doc.equipment_category == "POWER EQUIPMENT":
					self.set_approver("Manager Power")
				else:
					if self.doc.branch == "Customer Services":
						self.set_approver("GMCS")
					else:
						self.set_approver("ADM")
		elif self.new_state.lower() in ("Approved".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can edit/approve this documents".format(self.doc.approver))
		elif self.new_state.lower() in ("Cancelled".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can cancel this documents".format(self.doc.approver))

	def asset(self):
		if self.new_state.lower() in ("Waiting Verification".lower()):
			if frappe.session.user != self.doc.owner:
				if self.doc.doctype == "Project Capitalization" and "Projects Manager" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only {} can forward this Asset for verification.".format(self.doc.owner))
				if self.doc.doctype == "Asset Issue Details" and "Stock User" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only {} can forward this Asset for verification.".format(self.doc.owner))
		if self.new_state.lower() in ("Verified".lower()):
			if "Accounts User" not in frappe.get_roles(frappe.session.user) and "Projects Manager" not in frappe.get_roles(frappe.session.user):
				if self.old_state.lower() != self.new_state.lower():
					frappe.throw("Only Accounts User can verify for this Asset.")
		if self.new_state.lower() in ("Submitted".lower()):
			if frappe.session.user != self.doc.owner:
				frappe.throw("Only {} can submit this Asset".format(self.doc.owner))
		if self.new_state.lower() in ("Rejected".lower()):
			if "Accounts User" not in frappe.get_roles(frappe.session.user):
				frappe.throw("Only Accounts User can reject this Asset.")
			
	
	def adhoc_training_request(self):		
		if not self.old_state:	 
			return
		elif self.old_state.lower() =="Waiting HR Approval".lower() and self.new_state.lower() != "Waiting HR Approval".lower():
			data = frappe.db.sql(""" 
								 SELECT i.training_category,i.training_mode
								 from `tabAd hoc Training Request` atr, `tabTraining Needs Assessment Item` i 
								 where atr.name=i.parent
								 and atr.name='{}' and atr.fiscal_year='{}'""".format(self.doc.name,self.doc.fiscal_year),as_dict=True)	  
			if data[0].training_category == "Third Country" and data[0].training_mode == "Regular":
				self.doc.workflow_state = "Waiting CEO Approval"
			elif data[0].training_category == "India" and data[0].training_mode == "Regular":
				self.doc.workflow_state = "Waiting Director, CA Approval"
			elif data[0].training_category == "Third Country" or data[0].training_category == "India" or data[0].is_professional_certificate == 1 and data[0].training_mode == "Online":
				self.doc.workflow_state = "Waiting Director, CA Approval"
			else:
				self.doc.workflow_state = "Waiting Chief, PCD Approval"

	def leave_application(self):
		''' Leave Application Workflow
			1. Casual Leave, Earned Leave & Paternity Leave: 
				* Employee -> Supervisor
			2. Medical Leave:
				* Employee -> Department Head (if the leave is within 5 days)
				* Employee -> CEO (more than 5 days)
			3. Bereavement & Maternity:
				* Employee -> Department Head
			4. Extraordinary Leave:
				* Employee -> CEO 
		'''
		if self.new_state.lower() in ("Draft".lower(),"Waiting Supervisor Approval".lower()):
			if "HR User" in frappe.get_roles(frappe.session.user):
				pass
			else:
				if frappe.session.user != frappe.db.get_value("Employee",self.doc.employee,"user_id"):
					frappe.throw("Only {} can apply.".format(self.doc.employee))
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if self.doc.leave_approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Leave Application".format(self.doc.leave_approver_name))
			region = frappe.db.get_value("Employee",self.doc.employee,"region")
			if region not in (None,"Corporate Head Quarter") and frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]:
				self.set_approver("Regional Director")
			else:
				# if frappe.db.get_value("Employee",self.doc.employee,""(frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
				self.set_approver("Supervisors Supervisor")
				# else:
				# 	self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting Director Approval".lower()):
			if self.doc.leave_approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Leave Application".format(self.doc.leave_approver_name))
			self.set_approver("Department Head")
		elif self.new_state.lower() in ("Waiting GM Approval".lower()):
			if self.doc.leave_approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Leave Application".format(self.doc.leave_approver_name))
			self.set_approver("GM")
		elif self.new_state.lower() in ("Waiting CEO Approval".lower()):
			if self.doc.leave_approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Leave Application".format(self.doc.leave_approver_name))
			self.set_approver("CEO")
			# if self.doc.leave_type in ("Casual Leave", "Earned Leave", "Paternity Leave"):
			# 	self.set_approver("Supervisor")
			# elif self.doc.leave_type in ("EOL"):
			# 	self.set_approver("HRM")
			# elif self.doc.leave_type in ("Medical Leave"):
			# 	if flt(self.doc.total_leave_days) <= 5:
			# 		self.set_approver("Department Head")
			# 		# when Department Head himself/herself applies, request should go to their reports_to
			# 		if self.doc.leave_approver == self.employee[0]:
			# 			self.set_approver("Supervisor")
			# 	else:
			# 		self.set_approver("CEO")
			# 		# when CEO himself/herself applies, request should go to their reports_to
			# 		if self.doc.leave_approver == self.employee[0]:
			# 			self.set_approver("Supervisor")
			# elif self.doc.leave_type in ("Bereavement Leave", "Maternity Leave"):
			# 	self.set_approver("Department Head")
			# 	# when Department Head himself/herself applies, request should go to their reports_to
			# 	if self.doc.leave_approver == self.employee[0]:
			# 		self.set_approver("Supervisor")
			# elif self.doc.leave_type in ("EOL", "Extraordinary Leave"):
			# 	self.set_approver("CEO")
			# 	# when CEO himself/herself applies, request should go to their reports_to
			# 	if self.doc.leave_approver == self.employee[0]:
			# 		self.set_approver("Supervisor")
			# else:
			# 	frappe.throw(_("Workflow not defined for leave type {}").format(self.doc.leave_type))
		elif self.new_state.lower() == "Approved".lower():
			if "HR Manager" not in frappe.get_roles(frappe.session.user):
				if self.doc.leave_approver != frappe.session.user:
					frappe.throw("Only {} can Approve this Leave Application".format(self.doc.leave_approver_name))
			self.doc.status= "Approved"
			self.update_employment_status()
		elif self.new_state.lower() == "Rejected".lower():
			if self.doc.leave_approver != frappe.session.user and "HR Manager" not in frappe.get_roles(frappe.session.user):
				frappe.throw("Only {} can Reject this Leave Application".format(self.doc.leave_approver_name))
			self.doc.status = "Rejected"
		else:
			frappe.throw(_("Invalid Workflow State {}").format(self.doc.workflow_state))

	def leave_encashment(self):
		''' Leave Encashment Workflow
			1. Employee -> HR
		'''
		# if self.new_state.lower() in ("Draft".lower(), "Waiting HR Approval".lower()):
		# 	self.set_approver("HRM")
		if self.new_state.lower() == "Waiting HR Approval".lower():
			# if self.doc.approver != frappe.session.user:
			# 	frappe.throw("Only {} can Approve this Leave Encashment".format(self.doc.approver_name))
			self.set_approver("HR")
		if self.new_state.lower() == "Waiting Director, Business Approval".lower():
			# if self.doc.approver != frappe.session.user:
			# 	frappe.throw("Only {} can Approve this Leave Encashment".format(self.doc.approver_name))
			self.set_approver("DirectorB")
		elif self.new_state.lower() == "Waiting Approval".lower():
			# if self.doc.approver != frappe.session.user:
			# 	frappe.throw("Only {} can Approve this Leave Encashment".format(self.doc.approver_name))
			self.set_approver("GMCSD")
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Encashment".format(self.doc.approver_name))
		elif self.new_state.lower() in ('Rejected'):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this Encashment".format(self.doc.approver_name))

	def bulk_leave_encashment(self):
		''' Leave Encashment Workflow
			1. HR -> HR Manager
		'''
		if self.new_state.lower() in ("Draft".lower(), "Waiting HR Approval".lower()):
			self.set_approver("HR")
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve the Bulk Leave Encashment".format(self.doc.approver_name))
		elif self.new_state.lower() in ('Rejected'):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject the Bulk Leave Encashment".format(self.doc.approver_name))

	def salary_advance(self):
		''' Salary Advance Workflow
			1. Employee -> GM -> CEO -> HR
		'''	
		if self.new_state.lower() in ("Waiting CEO Approval".lower()):
			if "Director" not in frappe.get_roles(frappe.session.user) and "General Manager" not in frappe.get_roles(frappe.session.user):
				if self.doc.advance_approver != frappe.session.user:
					frappe.throw(_("Only {} can Verify this request").format(self.doc.advance_approver_name))	
			self.set_approver("CEO")
			self.doc.db_set("status",self.new_state)
		elif self.new_state.lower() in ("Waiting HR Approval".lower()):
			# if self.doc.advance_approver != frappe.session.user:
			# 	frappe.throw(_("Only {} can Approve this request").format(self.doc.advance_approver_name))
			self.set_approver("HR")
			self.doc.db_set("status",self.new_state)
		elif self.new_state.lower() in ("Waiting GM Approval".lower()):
			# if self.doc.advance_approver != frappe.session.user:
			# 	frappe.throw(_("Only {} can Approve this request").format(self.doc.advance_approver_name))
			self.set_approver("GM")
			self.doc.db_set("status",self.new_state)
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw(_("Only {} can Approve this request").format(self.doc.advance_approver_name))	
			self.doc.db_set("status",self.new_state)	
		elif self.new_state.lower() == "Rejected":
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw(_("Only {} can Reject this request").format(self.doc.advance_approver_name))
			self.doc.db_set("status",self.new_state)		
		elif self.new_state.lower() == "Cancelled".lower():
			if frappe.session.user not in (self.doc.advance_approver,"Administrator"):
				if "HR Manager" not in frappe.get_roles(frappe.session.user):
					frappe.throw(_("Only {} can Cancel this document.").format(self.doc.advance_approver_name))
			self.doc.db_set("status",self.new_state)
	
	def travel_authorization(self):
		''' Travel Authorization Workflow
			1. Employee -> Supervisor
		'''
		# if self.new_state.lower() in ("Waiting HR Approval".lower()):
		# 	self.set_approver()
		if self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
			self.doc.document_status = "Draft"
		if self.new_state.lower() in ("Waiting Project Manager Approval".lower()):
			if self.doc.reference_type in ("Project","Task"):
				self.set_approver("Project Manager")
		elif self.new_state == "Waiting CEO Approval":
			self.set_approver("CEO")
		# elif self.new_state == "Waiting Supervisor Approval":
		# 	self.set_approver("Supervisor")
		elif self.new_state == "Verified by Supervisor":
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			region = frappe.db.get_value("Employee",self.doc.employee,"region")
			if region not in (None,"Corporate Head Quarter") and frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]:
				self.set_approver("Regional Director")
			else:
				if self.gm_approver != None:
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("Supervisors Supervisor")	
					else:
						self.set_approver("Supervisor")
				else:
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("Supervisors Supervisor")	
					else:
						self.set_approver("Supervisor")		
			# self.doc.document_status = "Verified by Supervisor"
		elif self.new_state == "Verified By Project Manager":
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			region = frappe.db.get_value("Employee",self.doc.employee,"region")
			if region not in (None,"Corporate Head Quarter") and frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]:
				self.set_approver("Regional Director")
			else:
				if frappe.db.get_value("Employee",self.doc.employee,"region") not in (None,'Corporate Head Quarter'):
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("Regional Director")
					else:
						if (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.regional_director[0]):
							self.set_approver("GMO")
						else:
							self.set_approver("GM")
				else:
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0] if self.gm_approver else "") and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("GM")
					else:
						if (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.director_t[0]) or (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.director_b[0]) or (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.ceo[0]):
							self.set_approver("Supervisor")
						else:
							self.set_approver("Department Head")
		elif self.new_state == "Rejected By Supervisor":
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			self.doc.document_status = "Rejected"
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.supervisor != frappe.session.user and frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]:
				frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			self.doc.document_status = "Approved"
		elif self.new_state.lower() == 'Rejected'.lower():
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Reject this request".format(self.doc.supervisor_name))
			self.doc.document_status = "Rejected"
		elif self.new_state.lower() == "Cancelled".lower():
			if self.doc.owner != "ceo@bt.bt":
				if "HR User" not in frappe.get_roles(frappe.session.user):
					frappe.throw(_("Only {} can Cancel this Travel Authorization").format(self.doc.supervisor_name))
			self.doc.document_status = "Cancelled"

	def travel_claim(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			# if self.doc.travel_type not in ("Training In-Country", "Training Out-Country", "Meeting and Seminars"):
			self.set_approver("Supervisor")
		if self.new_state.lower() in ("Waiting Project Manager Approval".lower()):
			if self.doc.reference_type in ("Project","Task"):
				self.set_approver("Project Manager")
		elif self.new_state == "Verified by Supervisor":
			if "HR User" not in frappe.get_roles(frappe.session.user):
				if self.doc.supervisor != frappe.session.user:
					frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			region = frappe.db.get_value("Employee",self.doc.employee,"region")
			if region not in (None,"Corporate Head Quarter") and frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]:
				self.set_approver("Regional Director")
			else:
				if self.gm_approver != None:				
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("Supervisors Supervisor")
					else:
						self.set_approver("Supervisor")
				else:
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("Supervisors Supervisor")
					else:
						self.set_approver("Supervisor")

		elif self.new_state == "Verified By Project Manager":
			if "HR User" not in frappe.get_roles(frappe.session.user):
				if self.doc.supervisor != frappe.session.user:
					frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			region = frappe.db.get_value("Employee",self.doc.employee,"region")
			if region not in (None,"Corporate Head Quarter") and frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]:
				self.set_approver("Regional Director")
			else:
				if frappe.db.get_value("Employee",self.doc.employee,"region") not in (None,'Corporate Head Quarter'):
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.regional_director[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("Regional Director")
					else:
						if (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.regional_director[0]):
							self.set_approver("GMO")
						else:
							self.set_approver("GM")
				else:
					if (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.gm_approver[0] if self.gm_approver else "") and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_t[0]) and (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.director_b[0]):
						self.set_approver("GM")
					else:
						if (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.director_t[0]) or (frappe.db.get_value("Employee",self.doc.employee,"user_id") == self.director_b[0]) or (frappe.db.get_value("Employee",self.doc.employee,"user_id") != self.ceo[0]):
							self.set_approver("Supervisor")
						else:
							self.set_approver("Department Head")
		elif self.new_state.lower() == "Waiting Approval".lower():
			if "HR User" not in frappe.get_roles(frappe.session.user):
				if self.doc.supervisor != frappe.session.user:
					frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			# self.set_approver("TravelAdmin")
			self.doc.supervisor_approval = 1
		elif self.new_state.lower() == "Waiting HR".lower():
			if self.doc.owner != "ceo@bt.bt":
				if "HR User" not in frappe.get_roles(frappe.session.user):
					if self.doc.supervisor != frappe.session.user:
						frappe.throw("Only {} can Approve this request".format(self.doc.supervisor_name))
			self.doc.supervisor_approval = 1
		elif self.new_state.lower() == "Claimed".lower():
			if self.old_state.lower() == "Waiting Approval".lower():
				submit_flag = 0
				if self.ta_approver:
					for a in self.ta_approver:
						if a.user == str(frappe.session.user):
							submit_flag = 1
				if submit_flag == 0:
					frappe.throw("Only {} can submit/edit this document".format(tuple(self.ta_approver)))
			self.doc.status = "Claimed"
			self.doc.hr_approval = 1
			self.doc.hr_approved_on = nowdate()
		elif self.new_state.lower() == "Approved".lower():
			if "Travel Administrator" in frappe.get_roles(frappe.session.user):
				submit_flag = 0
				if self.ta_approver:
					for a in self.ta_approver:
						if a.user == str(frappe.session.user):
							submit_flag = 1
				if submit_flag == 0:
					frappe.throw("Only {} can submit/edit this document".format(tuple(self.ta_approver)))
			else:
				if "HR User" not in frappe.get_roles(frappe.session.user):
					if self.doc.supervisor != frappe.session.user:
						frappe.throw("Only {} can Edit or Approve this request".format(self.doc.supervisor))
		elif self.new_state.lower() in ('Rejected By Supervisor'.lower()):
			if self.old_state.lower() == "Verified By Supervisor".lower():
				if self.doc.supervisor_manager != frappe.session.user:
					frappe.throw("Only {} can Reject this request".format(self.doc.supervisor))
			elif self.old_state.lower() == "Waiting Supervisor Approval".lower():
				if self.doc.supervisor != frappe.session.user:
					frappe.throw("Only {} can Reject this request".format(self.doc.supervisor))
			self.doc.status = "Rejected"
		elif self.new_state.lower() == "Rejected":
			if self.doc.supervisor != frappe.session.user:
				frappe.throw("Only {} can Reject this request".format(self.doc.supervisor))
		elif self.new_state.lower() == "Cancelled".lower():
			if self.doc.supervisor != frappe.session.user:
				if "HR User" not in frappe.get_roles(frappe.session.user):
					frappe.throw(_("Only {} can Cancel this request").format(self.doc.supervisor))

	def overtime_application(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() == "Waiting Approval".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.approver_name))
			self.set_approver("Supervisors Supervisor")
		elif self.new_state.lower() == "Waiting GM Approval".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.approver_name))
			self.set_approver("GM")
		elif self.new_state.lower() == "Waiting HR Approval".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve this request".format(self.doc.approver_name))
			self.set_approver("HR")
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.approver != frappe.session.user and "HR User" not in frappe.get_roles(frappe.session.user):
				frappe.throw("Only {} can Approve this request".format(self.doc.approver_name))
		elif self.new_state.lower() in ('Rejected'.lower(), 'Rejected By Supervisor'.lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Reject this request".format(self.doc.approver_name))
		elif self.new_state.lower() == "Cancelled".lower():
			if "HR User" not in frappe.get_roles(frappe.session.user):
				if self.doc.approver != frappe.session.user:
					frappe.throw("Only {} can Cancel this request".format(self.doc.approver_name))

	def material_request(self):
		''' Material Request Workflow
			1. Employee -> MR Manager
		'''
		if self.new_state.lower() in ("Draft".lower()):
			if self.doc.owner != frappe.session.user:
				frappe.throw("Only the document owner can Apply this material request")
		elif self.new_state.lower() in ("Waiting Approval".lower()):
			if frappe.session.user != self.doc.approver:
				if self.old_state != "Draft":
					frappe.throw("Only {} can make changes to this Material Request".format(self.doc.approver))
				elif self.old_state == "Draft" and frappe.session.user != self.doc.owner:
					frappe.throw("Only {} can make changes to this Material Request".format(self.doc.owner))
				if self.old_state.lower() == "Waiting Supervisor Approval".lower():
					self.doc.verifier = frappe.session.user
				if self.doc.reference_type:
					if self.doc.reference_type == "Project":
						project = frappe.get_doc("Project",self.doc.reference_name)
						if project.division not in (None,''):
							self.set_approver("Project Approver")
						else:
							frappe.throw("Division not set for Project {}".format(self.doc.reference_name))
					elif self.doc.reference_type == "Task":
						project = frappe.get_doc("Project",frappe.db.get_value("Task",self.doc.reference_name,"project"))
						if project.division not in (None,''):
							self.set_approver("Project Approver")
						else:
							frappe.throw("Division not set for Project {}".format(frappe.db.get_value("Task",self.doc.reference_name,"project")))
					else:
						if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,"Corporate Head Quarter"):
							self.set_approver("Regional Director")
						else:
							if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division") not in (None,""):
								self.set_approver("General Manager")
							else:
								self.set_approver("CEO")
				else:
					if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,"Corporate Head Quarter"):
						self.set_approver("Regional Director")
					else:
						if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division") not in (None,""):
							self.set_approver("General Manager")
						else:
							self.set_approver("CEO")
		elif self.new_state.lower() in ("Waiting Supervisor Approval".lower()):
			if frappe.session.user != self.doc.approver:
				if self.old_state == "Draft" and self.doc.owner != frappe.session.user:
					frappe.throw("Only {} can make changes to this Material Request".format(self.doc.owner))
			self.set_approver("Supervisor")
		elif self.new_state.lower() in ("Waiting RD Approval".lower()):
			if frappe.session.user != self.doc.approver:
				frappe.throw("Only {} can make changes to this Material Request".format(self.doc.approver))
			if self.old_state.lower() == "Waiting Supervisor Approval".lower():
				self.doc.verifier = frappe.session.user
			if self.doc.reference_type:
				if self.doc.reference_type == "Project":
					project = frappe.get_doc("Project",self.doc.reference_name)
					if project.division not in (None,''):
						self.set_approver("Project Approver")
					else:
						frappe.throw("Division not set for Project {}".format(self.doc.reference_name))
				elif self.doc.reference_type == "Task":
					project = frappe.get_doc("Project",frappe.db.get_value("Task",self.doc.reference_name,"project"))
					if project.division not in (None,''):
						self.set_approver("Project Approver")
					else:
						frappe.throw("Division not set for Project {}".format(frappe.db.get_value("Task",self.doc.reference_name,"project")))
				else:
					if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,"Corporate Head Quarter"):
						self.set_approver("Regional Director")
					else:
						if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division") not in (None,""):
							self.set_approver("General Manager")
						else:
							self.set_approver("CEO")
			else:
				if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"region") not in (None,"Corporate Head Quarter"):
					self.set_approver("Regional Director")
				else:
					if frappe.db.get_value("Employee",{"user_id":self.doc.owner},"division") not in (None,""):
						self.set_approver("General Manager")
					else:
						self.set_approver("CEO")
		elif self.new_state.lower() in ("Approved".lower(), "Rejected".lower()):
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can Approve or Reject this request".format(self.doc.approver_name))


		# needed so that non-employees like admin cannot create MR 
		# added by phuntsho on Feb 3 2021 (NHDCL)
		'''
		workflow_state	= self.doc.get("workflow_state").lower
		final_approver	= frappe.db.get_value("Employee", {"user_id": get_final_approver(self.doc.branch)}, ["user_id","employee_name","designation","name"])
		if not self.login_user: 
			frappe.throw("You do not have permission to create MR!")
		owner		= frappe.db.get_value("Employee", {"user_id": self.doc.owner}, ["user_id","employee_name","designation","name"])
		employee		  = frappe.db.get_value("Employee", owner[3], ["user_id","employee_name","designation","name"])
		reports_to		= frappe.db.get_value("Employee", frappe.db.get_value("Employee", owner[3], "reports_to"), ["user_id","employee_name","designation","name"])

		if workflow_state == "Waiting Supervisor Approval".lower():
			if self.doc.approver and self.doc.approver != frappe.session.user:
				frappe.throw(_("Only the approver <b>{0}</b> allowed to verify or approve this document").format(self.doc.approver), title="Invalid Operation")
			if "MR GM" in frappe.get_roles(frappe.session.user):
				# MR GM should be able to edit only if MR is submitted by Manager
				if (self.doc.owner != frappe.session.user) and "MR Manager" not in frappe.get_roles(self.doc.owner):
					frappe.throw("MR GM is not allowed to save the document during this workflow state.")
					
			officiating = get_officiating_employee(reports_to[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else reports_to[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else reports_to[1]

			
		elif workflow_state == "Verified By Supervisor".lower():
			officiating = get_officiating_employee(final_approver[3])
			if officiating:
				officiating = frappe.db.get_value("Employee", officiating[0].officiate, ["user_id","employee_name","designation","name"])
			vars(self.doc)[self.doc_approver[0]] = officiating[0] if officiating else final_approver[0]
			vars(self.doc)[self.doc_approver[1]] = officiating[1] if officiating else final_approver[1]
		elif workflow_state == "Approved":
			self.doc.docstatus = 1
		'''

	def festival_advance(self):
		''' Leave Encashment Workflow
			1. Employee -> Supervisor -> HR
		'''
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			self.set_approver("Supervisor")
		elif self.new_state.lower() == "Waiting HR Approval".lower():
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw("Only {} can Approve this Festival Advance".format(self.doc.advance_approver_name))
			self.set_approver("HRM")
		elif self.new_state.lower() == "Approved".lower():
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw("Only {} can Approve the Festival Claim".format(self.doc.advance_approver_name))
		elif self.new_state.lower() in ('Rejected', 'Rejected By Supervisor'):
			if self.doc.advance_approver != frappe.session.user:
				frappe.throw("Only {} can Reject the Festival Advance".format(self.doc.advance_approver_name))

	def employee_benefits(self):
		workflow_state	= self.doc.get("workflow_state").lower()
		if workflow_state == "Draft".lower():
			# if doc.purpose == "Separation":
			if not "HR Manager" in frappe.get_roles(frappe.session.user):
				frappe.throw("Only HR user with role HR Manager can create the employee benefit with purpose Separation")


		elif workflow_state == "Waiting Approval".lower():
			# if doc.purpose == "Separation":
			set_approver("HR")

			if not officiating and not "HR Manager" in frappe.get_roles(frappe.session.user):
				frappe.throw("Only HR user with role HR Manager can create the employee benefit with purpose Separation")

		elif workflow_state == "Approved".lower():
			if self.doc.docstatus == 0 and self.doc.workflow_state == "Approved":
				self.doc.workflow_state == "Waiting Approval"
			if not "Chief PCD" in frappe.get_roles(frappe.session.user):
				frappe.throw(_("Only Chief PCD can approve this application").format(title="Invalid Operation"))
			vars(self.doc)[self.doc_approver[0]] = self.login_user[0]
			vars(self.doc)[self.doc_approver[1]] = self.login_user[1]
	
		elif workflow_state == "Rejected".lower():
			if not "Chief PCD" in frappe.get_roles(frappe.session.user):
				if workflow_state != self.doc.get_db_value("workflow_state"):
					frappe.throw(_("Only Cheif PCD can reject this application").format(title="Invalid Operation"))
		else:
			pass

	def employee_transfer(self):
		if self.doc.workflow_state == "Draft":
			# if not self.description or self.description == "":
			# 		frappe.throw("Please write a reason for transfer")
			if self.doc.transfer_type != 'Personal Request':
				if "HR User" not in frappe.get_roles(frappe.session.user):
					frappe.throw("Only HR User can apply for Management Transfer or Mutual Swipe")
			# frappe.throw(frappe.db.get_value("Employee",self.employee,"user_id"))
			else:
				if "HR User" in frappe.get_roles(frappe.session.user):
					frappe.throw("HR User can apply for Management Transfer or Mutual Swipe only")
				if frappe.session.user != frappe.db.get_value("Employee",self.doc.employee,"user_id"):
					frappe.throw("Only the selected employee {0} can apply for employee transfer".format(self.doc.employee))
			supervisor_id = frappe.db.get_value("Employee", self.doc.employee, "reports_to")
			self.doc.supervisor_name = frappe.db.get_value("Employee", supervisor_id, "employee_name")
			self.doc.supervisor_email = frappe.db.get_value("Employee", supervisor_id, "company_email")
			self.doc.supervisor = frappe.db.get_value("User", frappe.db.get_value("Employee", supervisor_id, "user_id"), "name")

		if self.doc.workflow_state == "Rejected":
			if not self.doc.rejection_reason:
				frappe.throw("Please input a rejection reason")

	def sws_application(self):
		if self.new_state.lower() in ("Draft".lower(), "Waiting Supervisor Approval".lower()):
			if not self.doc.verified and self.doc.approval_status == "Approved":
				frappe.throw("Can approve claim only after verification by supervisors")
			self.set_approver("Supervisor")
			try:
				eid = frappe.db.get_value("Employee",self.doc.employee,"user_id")
			except:
				frappe.throw("User ID not set for Employee '{0}'".format(self.doc.employee))
			if frappe.session.user != eid :
				frappe.throw("Only Selected Employee can apply for SWS Application")

		if self.new_state.lower() == "Waiting Supervisor Approval".lower():
			if not self.doc.verified and self.doc.approval_status == "Approved":
				frappe.throw("Can approve claim only after verification by supervisors")
	
		if self.new_state.lower() == "Waiting SWS User Approval".lower():
			if not self.doc.verified and self.doc.approval_status == "Approved":
				frappe.throw("Can approve claim only after verification by supervisors")

		if self.new_state.lower() == "Cancelled".lower():
			if not self.doc.verified and self.doc.approval_status == "Approved":
				frappe.throw("Can approve claim only after verification by supervisors")

		if self.new_state.lower() == "Verified".lower():
			self.doc.verified = 1
   
		if self.new_state.lower() =="Rejected".lower():
			self.doc.verified = 0
			self.doc.approval_status = "Rejected"
   
		if self.new_state.lower() =="Approved".lower():
			self.doc.approval_status = "Approved"

	def assign_shift(self):
		if self.new_state.lower() in ("Draft".lower()):
			frappe.throw
			try:
				eid = frappe.db.get_value("Employee",self.doc.employee,"user_id")
			except:
				frappe.throw("User ID not set for Supervisor '{0}'".format(self.doc.employee))
			if frappe.session.user != eid:
				frappe.throw("Only {} can apply or edit this document.".format(self.doc.employee))

		elif self.new_state.lower() == "Waiting GM Approval".lower():
			if self.doc.approver:
				if self.doc.approver != frappe.session.user:
					frappe.throw("Only {} can approve or edit this document.".format(self.doc.approver))
			self.set_approver("GM")
	
		elif self.new_state.lower() == "Waiting RD Approval".lower():
			self.set_approver("Regional Director")

		elif self.new_state.lower() == "Waiting HR Approval".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can approve or edit this document.".format(self.doc.approver))
   
		elif self.new_state.lower() =="Rejected".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can reject this document.".format(self.doc.approver))
   
		elif self.new_state.lower() =="Approved".lower():
			if self.doc.approver != frappe.session.user:
				frappe.throw("Only {} can approve or edit this document.".format(self.doc.approver))

	def notify(self, args):
		args = frappe._dict(args)
		# args -> message, message_to, subject

		contact = args.message_to
		if not isinstance(contact, list):
			if not args.notify == "employee":
				contact = frappe.get_doc('User', contact).email or contact

		sender	  		= dict()
		sender['email']	 = frappe.get_doc('User', frappe.session.user).email
		sender['full_name'] = frappe.utils.get_fullname(sender['email'])

		try:
			frappe.sendmail(
				recipients = contact,
				sender = sender['email'],
				subject = args.subject,
				message = args.message,
			)
			frappe.msgprint(_("Email sent to {0}").format(contact))
		except frappe.OutgoingEmailError:
			pass

class NotifyCustomWorkflow:
	def __init__(self,doc):
		self.doc 			= doc
		self.old_state 		= self.doc.get_db_value("workflow_state")
		self.new_state 		= self.doc.workflow_state
		self.field_map 		= get_field_map()
		self.doc_approver	= self.field_map[self.doc.doctype]
		self.field_list		= ["user_id","employee_name","designation","name"]
		if self.doc.doctype not in ("Material Request","Asset Issue Details", "Project Capitalization", "BTL Sales Cancellation"):
			self.employee   = frappe.db.get_value("Employee", self.doc.employee, self.field_list)
		else:
			self.employee = frappe.db.get_value("Employee", {"user_id":self.doc.owner}, self.field_list)

	def notify_employee(self):
		if self.doc.doctype not in ("Material Request","Asset Issue Details", "Project Capitalization", "BTL Sales Cancellation"):
			employee = frappe.get_doc("Employee", self.doc.employee)
		else:
			employee = frappe.get_doc("Employee", frappe.db.get_value("Employee",{"user_id":self.doc.owner},"name"))
		if not employee.user_id:
			return

		# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
		# args = parent_doc.as_dict()
		args = self.doc.as_dict()

		if self.doc.doctype == "Leave Application":
			template = frappe.db.get_single_value('HR Settings', 'leave_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Leave Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Leave Encashment":
			template = frappe.db.get_single_value('HR Settings', 'encashment_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Encashment Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Salary Advance":
			template = frappe.db.get_single_value('HR Settings', 'advance_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Advance Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Travel Authorization":
			template = frappe.db.get_single_value('HR Settings', 'authorization_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Authorization Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Travel Claim":
			template = frappe.db.get_single_value('HR Settings', 'claim_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Claim Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Overtime Application":
			template = frappe.db.get_single_value('HR Settings', 'overtime_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Overtime Status Notification in HR Settings."))
				return

		elif self.doc.doctype == "Employee Benefits":
			template = frappe.db.get_single_value('HR Settings', 'benefits_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Employee Benefits Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Employee Separation":
			template = frappe.db.get_single_value('HR Settings', 'employee_separation_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Employee Separation Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Employee Separation Clearance":
			template = frappe.db.get_single_value('HR Settings', 'employee_separation_clearance_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Employee Separation Clearance Status Notification in HR Settings."))
				return

		elif self.doc.doctype == "SWS Application":
			template = frappe.db.get_single_value('HR Settings', 'sws_application_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for SWS Application Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "Training Request":
			template = frappe.db.get_single_value('HR Settings', 'training_request_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Training Request Status Notification in HR Settings."))
				return
		elif self.doc.doctype == "POL":
			template = frappe.db.get_single_value('Maintenance Settings', 'pol_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for POL Status Notification in Maintenance Settings."))
				return
		elif self.doc.doctype == "Material Request":
			template = frappe.db.get_single_value('Stock Settings', 'mr_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Material Request Status Notification in Stock Settings."))
				return

		elif self.doc.doctype == "Asset Issue Details":
			template = frappe.db.get_single_value('Asset Settings', 'asset_issue_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Issue Status Notification in Asset Settings."))
				return
		elif self.doc.doctype == "Project Capitalization":
			template = frappe.db.get_single_value('Asset Settings', 'asset_status_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Status Notification in Asset Settings."))
				return

		elif self.doc.doctype == "Training Nomination":
			# template needs to be taken care
			pass
		elif self.doc.doctype == "Ad hoc Training Request":
			# template needs to be taken care
			pass
		elif self.doc.doctype == "Training Approval Request":
			# template needs to be taken care
			pass

		elif self.doc.doctype == "Festival Advance":
			# template needs to be taken care
			pass
		else:
			template = ""

		if not template:
			frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
			return
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		if employee and "Driver" not in employee.designation and "Elementary Service Personnel" not in employee.designation and "Home Based Caretaker" not in employee.designation and employee.user_id not in ('dawa486@bt.bt','sonam.tobgye274@bt.bt'):
			self.notify({
				# for post in messages
				"message": message,
				"message_to": employee.user_id,
				# for email
				"subject": email_template.subject,
				"notify": "employee"
			})

	def notify_approver(self):
		if self.doc.get(self.doc_approver[0]):
			# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			# args = parent_doc.as_dict()
			args = self.doc.as_dict()

			if self.doc.doctype == "Leave Application":
				template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Leave Encashment":
				template = frappe.db.get_single_value('HR Settings', 'encashment_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Encashment Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Salary Advance":
				template = frappe.db.get_single_value('HR Settings', 'advance_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Advance Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Travel Authorization":
				template = frappe.db.get_single_value('HR Settings', 'authorization_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Authorization Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Travel Claim":
				template = frappe.db.get_single_value('HR Settings', 'claim_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Claim Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Overtime Application":
				template = frappe.db.get_single_value('HR Settings', 'overtime_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Overtime Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Benefits":
				template = frappe.db.get_single_value('HR Settings', 'benefits_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Benefits Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Separation":
				template = frappe.db.get_single_value('HR Settings', 'employee_separation_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Separation Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Separation Clearance":
				template = frappe.db.get_single_value('HR Settings', 'employee_separation_clearance_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Separation Clearance Notification in HR Settings."))
					return 
			elif self.doc.doctype == "SWS Application":
				template = frappe.db.get_single_value('HR Settings', 'sws_application_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for SWS Application Notification in HR Settings."))
					return
			elif self.doc.doctype == "Training Request":
				template = frappe.db.get_single_value('HR Settings', 'training_request_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Training Request Notification in HR Settings."))
					return
			elif self.doc.doctype == "POL":
				template = frappe.db.get_single_value('Maintenance Settings', 'pol_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for POL Approval Notification in Maintenance Settings."))
					return
			elif self.doc.doctype == "POL":
				template = frappe.db.get_single_value('Maintenance Settings', 'pol_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for POL Approval Notification in Maintenance Settings."))
					return
			elif self.doc.doctype == "Material Request":
				template = frappe.db.get_single_value('Stock Settings', 'mr_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Material Request Approval Notification in Stock Settings."))
					return

			elif self.doc.doctype == "Asset Issue Details":
				template = frappe.db.get_single_value('Asset Settings', 'asset_issue_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Asset Issue Approval Notification in Asset Settings."))
					return
	
			elif self.doc.doctype == "Project Capitalization":
				template = frappe.db.get_single_value('Asset Settings', 'asset_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Asset Approval Notification in Asset Settings."))
					return

			elif self.doc.doctype == "Training Nomination":
				# template needs to be taken care
				pass
			elif self.doc.doctype == "Ad hoc Training Request":
				# template needs to be taken care
				pass
			elif self.doc.doctype == "Training Approval Request":
				# template needs to be taken care
				pass
			elif self.doc.doctype == "Festival Advance":
				# template needs to be taken care
				pass
			else:
				template = ""

			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# emp = frappe.db.get_value("Employee",{"user_id":self.doc_approver[0]},"name")
			# employee = frappe.get_doc("Employee",emp)
			# if employee and "Driver" not in employee.designation and "Elementary Service Personnel" not in employee.designation and "Home Based Caretaker" not in employee.designation and employee.user_id not in ('dawa486@bt.bt','sonam.tobgye274@bt.bt'):
			self.notify({
				# for post in messages
				"message": message,
				"message_to": self.doc.get(self.doc_approver[0]),
				# for email
				"subject": email_template.subject
			})
			# else:
			# 	receipients = []
			# 	if self.new_state.lower() == "Waiting Approval":
			# 		if self.ta_approver != None:
			# 			for a in self.ta_approver:
			# 				receipients.append(a.user)
			# 		self.notify({
			# 			# for post in messages
			# 			"message": message,
			# 			"message_to": receipients,
			# 			# for email
			# 			"subject": email_template.subject
			# 		})
			# 	elif self.new_state.lower() == "Waiting HR Approval":
			# 		for a in frappe.db.sql("""select parent from `tabHas Role` where role = 'HR User' and parent like '%@%'"""):
			# 			receipients.append(a)
			# 		self.notify({
			# 			# for post in messages
			# 			"message": message,
			# 			"message_to": receipients,
			# 			# for email
			# 			"subject": email_template.subject
			# 		})

	def notify_hr_users(self):
		receipients = []
		email_group = frappe.db.get_single_value("HR Settings","email_group")
		if not email_group:
			frappe.throw("HR Users Email Group not set in HR Settings.")
		hr_users = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if hr_users:
			receipients = [a['email'] for a in hr_users]
			# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			# args = parent_doc.as_dict()
			args = self.doc.as_dict()

			if self.doc.doctype == "Leave Application":
				template = frappe.db.get_single_value('HR Settings', 'leave_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Leave Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Leave Encashment":
				template = frappe.db.get_single_value('HR Settings', 'encashment_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Encashment Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Salary Advance":
				template = frappe.db.get_single_value('HR Settings', 'advance_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Advance Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Travel Authorization":
				template = frappe.db.get_single_value('HR Settings', 'authorization_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Authorization Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Travel Claim":
				template = frappe.db.get_single_value('HR Settings', 'claim_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Claim Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Overtime Application":
				template = frappe.db.get_single_value('HR Settings', 'overtime_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Overtime Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Benefits":
				template = frappe.db.get_single_value('HR Settings', 'benefits_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Benefits Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Separation":
				template = frappe.db.get_single_value('HR Settings', 'employee_separation_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Separation Approval Notification in HR Settings."))
					return
			elif self.doc.doctype == "Employee Separation Clearance":
				template = frappe.db.get_single_value('HR Settings', 'employee_separation_clearance_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Employee Separation Clearance Notification in HR Settings."))
					return 
			elif self.doc.doctype == "SWS Application":
				template = frappe.db.get_single_value('HR Settings', 'sws_application_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for SWS Application Notification in HR Settings."))
					return
			elif self.doc.doctype == "Training Request":
				template = frappe.db.get_single_value('HR Settings', 'training_request_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Training Request Notification in HR Settings."))
					return
			elif self.doc.doctype == "Training Nomination":
				# template needs to be taken care
				pass
			elif self.doc.doctype == "Ad hoc Training Request":
				# template needs to be taken care
				pass
			elif self.doc.doctype == "Training Approval Request":
				# template needs to be taken care
				pass
			elif self.doc.doctype == "Festival Advance":
				# template needs to be taken care
				pass
			else:
				template = ""

			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# frappe.throw(self.doc.get(self.doc_approver[0]))
			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})

	def notify_finance_users(self):
		receipients = ["finance@bt.bt"]
		# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
		# args = parent_doc.as_dict()
		args = self.doc.as_dict()

		if self.doc.doctype in ("Project Capitalization"):
			template = frappe.db.get_single_value('Asset Settings', 'asset_approval_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Approval Notification in Asset Settings."))
				return
		elif self.doc.doctype in ("Asset Issue Details"):
			template = frappe.db.get_single_value('Asset Settings', 'asset_issue_approval_notification_template')
			if not template:
				frappe.msgprint(_("Please set default template for Asset Issue Approval Notification in Asset Settings."))
				return
		else:
			template = ""

		if not template:
			frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
			return
		email_template = frappe.get_doc("Email Template", template)
		message = frappe.render_template(email_template.response, args)
		# frappe.throw(self.doc.get(self.doc_approver[0]))
		self.notify({
			# for post in messages
			"message": message,
			"message_to": receipients,
			# for email
			"subject": email_template.subject
		})

	def notify_travel_administrators(self):
		receipients = []
		region = frappe.db.get_value("Employee",self.doc.employee,"region")
		if region == "Western Region":
			email_group = "Travel Adminstrator, Western Region"
		elif region == "South Western Region":
			email_group = "Travel Administrator, South Western Region"
		elif region == "Eastern Region":
			email_group = "Travel Administrator, Eastern Region"
		elif region == "Central Region":
			email_group = "Travel Administrator, Central Region"
		else:
			email_group = "Travel Administrator, CHQ"
		if self.doc.doctype == "Travel Claim":
			if self.doc.travel_type in ("Training","Meeting and Seminars","BT DAY","Pilgrimage"):
				email_group = "Travel Administrator, CHQ"
		ta = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if ta:
			receipients = [a['email'] for a in ta]
			# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			# args = parent_doc.as_dict()
			args = self.doc.as_dict()
			if self.doc.doctype == "Travel Claim":
				template = frappe.db.get_single_value('HR Settings', 'claim_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Claim Approval Notification in HR Settings."))
					return
			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# frappe.throw(self.doc.get(self.doc_approver[0]))
			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})

	def notify_ta_finance(self):
		receipients = []
		region = frappe.db.get_value("Employee",self.doc.employee,"region")
		email_group = "Travel Administrator, Finance"
		ta = frappe.get_list("Email Group Member", filters={"email_group":email_group}, fields=['email'])
		if ta:
			receipients = [a['email'] for a in ta]
			# parent_doc = frappe.get_doc(self.doc.doctype, self.doc.name)
			# args = parent_doc.as_dict()
			args = self.doc.as_dict()
			if self.doc.doctype == "Travel Claim":
				template = frappe.db.get_single_value('HR Settings', 'claim_approval_notification_template')
				if not template:
					frappe.msgprint(_("Please set default template for Claim Approval Notification in HR Settings."))
					return
			if not template:
				frappe.msgprint(_("Please set default template for {}.").format(self.doc.doctype))
				return
			email_template = frappe.get_doc("Email Template", template)
			message = frappe.render_template(email_template.response, args)
			# frappe.throw(self.doc.get(self.doc_approver[0]))
			self.notify({
				# for post in messages
				"message": message,
				"message_to": receipients,
				# for email
				"subject": email_template.subject
			})
					
	def notify(self, args):
		args = frappe._dict(args)
		# args -> message, message_to, subject
		contact = args.message_to
		if not isinstance(contact, list):
			if not args.notify == "employee":
				contact = frappe.get_doc('User', contact).email or contact

		sender	  		= dict()
		sender['email']	 = frappe.get_doc('User', frappe.session.user).email
		sender['full_name'] = frappe.utils.get_fullname(sender['email'])

		try:
			frappe.sendmail(
				recipients = contact,
				sender = sender['email'],
				subject = args.subject,
				message = args.message,
			)
			frappe.msgprint(_("Email sent to {0}").format(contact))
		except frappe.OutgoingEmailError:
			pass

	def send_notification(self):
		if (self.doc.doctype not in self.field_map) or not frappe.db.exists("Workflow", {"document_type": self.doc.doctype, "is_active": 1}):
			return
		if self.new_state == "Draft":
			return
		elif self.new_state in ("Approved", "Rejected", "Cancelled", "Claimed", "Submitted"):
			self.notify_employee()
			if self.doc.doctype in ("Travel Claim"):
				if self.new_state in ("Approved"):
					self.notify_travel_administrators()
				elif self.new_state == "Claimed":
					self.notify_ta_finance()
			elif self.doc.doctype == "Leave Application":
				self.notify_hr_users()
		elif self.new_state.startswith("Waiting") and self.old_state != self.new_state and self.doc.doctype not in ("Asset Issue Details","Project Capitalization"):
			if self.doc.doctype in ("Travel Authorization","Leave Application","Travel Claim"):
				if self.new_state.lower() == "Waiting HR Approval".lower() and self.doc.owner == "ceo@bt.bt":
					self.notify_hr_users()
				elif self.new_state.lower() == "Waiting HR".lower():
					self.notify_hr_users()
				else:
					self.notify_approver()
					# self.notify_hr_users()
			else:
				self.notify_approver()
		elif self.new_state.startswith("Waiting") and self.old_state != self.new_state and self.doc.doctype in ("Asset Issue Details","Project Capitalization"):
			self.notify_finance_users()
		elif self.new_state.startswith("Verified") and self.old_state != self.new_state:
			if self.doc.doctype not in ("Asset Issue Details","Project Capitalization"):
				self.notify_approver()
			else:
				self.notify_employee()
		else:
			frappe.msgprint(_("Email notifications not configured for workflow state {}").format(self.new_state))

def get_field_map():
	return {
		"Salary Advance": ["advance_approver","advance_approver_name","advance_approver_designation"],
		"Leave Encashment": ["approver","approver_name","approver_designation"],
		"Leave Application": ["leave_approver", "leave_approver_name", "leave_approver_designation"],
		"Travel Authorization": ["supervisor", "supervisor_name", "supervisor_designation"],
		"Travel Claim": ["supervisor", "supervisor_name", "supervisor_designation"],
		"Overtime Application": ["approver", "approver_name", "approver_designation"],
		"Material Request": ["approver","approver_name","approver_designation"],
		"Festival Advance": ["advance_approver","advance_approver_name", "advance_approver_designation"],
		"Employee Transfer": ["supervisor", "supervisor_name", "supervisor_designation"],
		"Employee Benefits": ["benefit_approver","benefit_approver_name","benefit_approver_designation"],
		"SWS Application": ["supervisor","supervisor_name","supervisor_designation"],
		"Training Nomination": [],
		"Ad hoc Training Request": [],
		"Training Approval Request": [],
		"Compile Budget": ["approver","approver_name"],
		"Assign Shift": ["approver","approver_name","approver_designation"],
		"Employee Separation": ["approver","approver_name","approver_designation"],
		"Employee Separation Clearance": ["approver","approver_name","approver_designation"],
		"Target Set Up": ["approver","approver_name","approver_designation"],
		"Review": ["approver","approver_name","approver_designation"],
		"Performance Evaluation": ["approver","approver_name","approver_designation"],
		"BTL Sales Cancellation": ["approver","approver_name","approver_designation"],
		"POL": ["approver","approver_name","approver_designation"],
		"Bulk Leave Encashment": ["approver","approver_name","approver_designation"],
		"PMS Appeal":[],
		"Asset Issue Details": [],
		"Project Capitalization": [],

	}

def validate_workflow_states(doc):
	wf = CustomWorkflow(doc)
	wf.apply_workflow()

def notify_workflow_states(doc):
	wf = NotifyCustomWorkflow(doc)
	wf.send_notification()

