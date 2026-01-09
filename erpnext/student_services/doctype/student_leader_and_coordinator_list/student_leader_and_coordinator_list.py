# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentLeaderandCoordinatorList(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.student_leader_and_coordinator_items.student_leader_and_coordinator_items import StudentLeaderandCoordinatorItems
		from frappe.types import DF

		academic_term: DF.Link | None
		academic_year: DF.Link | None
		college_abbr: DF.Data | None
		company: DF.Link | None
		student_leader_and_coordinator_details: DF.Table[StudentLeaderandCoordinatorItems]
	# end: auto-generated types
	
	def validate(self):
		#frappe.throw("hi")
		self.add_role_for_student_leader()
		

	# def add_role_for_student_leader(self):
	# 	doc=frappe.get_doc('Student Leader and Coordinator List',self.name)
	# 	for row in doc.student_leader_and_coordinator_details:
	# 		user_email=frappe.get_value('Student',row.student_code,'user')
			
	# 		user_has_role = frappe.db.exists('Has Role', {
	# 			'parent': user_email,
	# 			'role': 'Purchase User'
	# 		})
	# 		if not user_has_role:
	# 			add_role=frappe.new_doc('Has Role')
	# 			add_role.parent=user_email
	# 			add_role.role='Purchase User'
	# 			add_role.parentfield='roles'
	# 			add_role.parenttype='User'
	# 			add_role.save()
	# 			frappe.db.commit()
 
	def add_role_for_student_leader(self):
		for row in self.student_leader_and_coordinator_details:
			user_email = frappe.get_value('Student', row.student_code, 'user')

			if user_email:
				user_has_role = frappe.db.exists('Has Role', {
					'parent': user_email,
					'role': 'Purchase User'
				})
				if not user_has_role:
					add_role = frappe.new_doc('Has Role')
					add_role.parent = user_email
					add_role.role = 'Purchase User'
					add_role.parentfield = 'roles'
					add_role.parenttype = 'User'
					add_role.insert(ignore_permissions=True)


		