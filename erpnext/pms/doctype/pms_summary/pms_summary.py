# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _

class PMSSummary(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		date_of_joining: DF.Data | None
		department: DF.Link | None
		designation: DF.Link | None
		division: DF.Link | None
		employee: DF.Link
		employee_name: DF.Data | None
		final_score: DF.Float
		final_score_percent: DF.Percent
		form_i_score: DF.Float
		form_i_total_rating: DF.Float
		form_i_weightage: DF.Percent
		form_ii_score: DF.Float
		form_ii_total_rating: DF.Float
		form_ii_weightage: DF.Percent
		gender: DF.Data | None
		max_rating_limit: DF.Float
		overall_rating: DF.Link | None
		pms_calendar: DF.Link
		pms_group: DF.Link | None
		posting_date: DF.Date | None
		section: DF.Link | None
		star_obtained: DF.Rating
		unit: DF.Link | None
	# end: auto-generated types
	def validate(self):
		self.get_summary()
	
	def on_submit(self):
		self.create_employee_pms_record()
	
	def create_employee_pms_record(self):
		emp = frappe.get_doc("Employee",self.employee)
		row = emp.append("employee_pms",{})
		row.fiscal_year = self.pms_calendar
		row.final_score = self.final_score
		row.final_score_percent = self.final_score_percent
		row.overall_rating = self.overall_rating
		row.reference_type = 'PMS Summary'
		row.performance_evaluation = self.name
		emp.save(ignore_permissions=True)
		
	def on_cancel(self):
		self.remove_employee_pms_record()

	def remove_employee_pms_record(self):
		doc = frappe.db.get_value("Employee PMS Rating",{"performance_evaluation":self.name},"name")
		if doc:
			frappe.delete_doc("Employee PMS Rating",doc)
		else:
			frappe.msgprint("""No PMS record found in Employee Master Data of employee <a href= "#Form/Quotation/{0}">{0}</a>""".format(self.employee))

	def get_summary(self):
		count = frappe.db.sql('''
				SELECT count(name)
				FROM `tabPerformance Evaluation` 
				WHERE employee = '{}'
				AND pms_calendar ='{}'
				AND docstatus = 1 
				AND reason in (SELECT reason FROM `tabPerformance Evaluation` WHERE reason IN ('Change In Section/Division/Department','Transfer','Change in PMS Group'))
			'''.format(self.employee, self.pms_calendar))[0][0]
			
		if flt(count) != 2:
			frappe.throw('Looks like both your target is not Evaluated yet')
		max = frappe.get_doc('PMS Setting')
		self.max_rating_limit = max.max_rating_limit

		f_i_total_rating = 0
		f_ii_total_rating = 0
		f_i_avg_score = 0
		f_ii_avg_score = 0
		total = 0
		target_weightage , competency_weightage = frappe.db.get_value('PMS Group',self.pms_group,['weightage_for_target','weightage_for_competency'])

		for d in frappe.db.get_list('Performance Evaluation',
			filters={
				'docstatus': 1,
				'employee': self.employee,
				'pms_calendar': self.pms_calendar,
				'reference': ('!=','')
			},
			fields=['form_i_total_rating', 'form_ii_total_rating', 'form_i_score', 'form_ii_score','final_score', 'no_of_months_served']):

			f_i_total_rating += flt(d['form_i_total_rating']) * flt(d['no_of_months_served']) / 12
			f_ii_total_rating += flt(d['form_ii_total_rating']) * flt(d['no_of_months_served']) / 12
			f_i_avg_score += flt(d['form_i_score']) * flt(d['no_of_months_served']) / 12
			f_ii_avg_score += flt(d['form_ii_score']) * flt(d['no_of_months_served']) / 12
			total += flt(d['final_score'])
			
		self.form_i_total_rating = f_i_total_rating
		self.form_ii_total_rating = f_ii_total_rating
		self.form_i_score = f_i_avg_score
		self.form_ii_score = f_ii_avg_score
		self.form_i_weightage = target_weightage
		self.form_ii_weightage = competency_weightage
		self.final_score = total
		self.final_score_percent = flt(self.final_score)/ flt(self.max_rating_limit) * 100
		self.overall_rating = frappe.db.sql('''select name from `tabOverall Rating` where  upper_range_percent >= {0} and lower_range_percent <= {0}'''.format(self.final_score_percent))[0][0]
		self.star_obtained = frappe.db.get_value('Overall Rating',self.overall_rating,'weightage')
		# else:
		# 	frappe.throw(
		# 		title=_('Error'),
		# 		msg=_("You Need to have TWO PMS for Summary"))


def get_permission_query_conditions(user):
	# restrict user from accessing this doctype    
	if not user: user = frappe.session.user     
	user_roles = frappe.get_roles(user)

	if user == "Administrator":      
		return
	if "HR User" in user_roles or "HR Manager" in user_roles:       
		return

	return """(
		`tabPMS Summary`.owner = '{user}'
		or
		exists(select 1
				from `tabEmployee`
				where `tabEmployee`.name = `tabPMS Summary`.employee
				and `tabEmployee`.user_id = '{user}')
			)""".format(user=user)
