# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.naming import make_autoname

class AnnualPerformanceAssessment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.budget.doctype.annual_performance_extra_item.annual_performance_extra_item import AnnualPerformanceExtraItem
		from erpnext.budget.doctype.apa_outcome_item.apa_outcome_item import APAOutcomeItem
		from erpnext.budget.doctype.apa_output_item.apa_output_item import APAOutputItem
		from frappe.types import DF

		amended_from: DF.Link | None
		college: DF.Link
		from_year: DF.Link
		outcome_calculation: DF.Percent
		outcome_items: DF.Table[APAOutcomeItem]
		outcome_rating: DF.Percent
		outcome_value: DF.Percent
		output_calculation: DF.Percent
		output_extra_items: DF.Table[AnnualPerformanceExtraItem]
		output_items: DF.Table[APAOutputItem]
		output_rating: DF.Percent
		output_value: DF.Percent
		overall_rating: DF.Percent
		performance: DF.Data | None
		to_year: DF.Link
	# end: auto-generated types

	def autoname(self):
		college_abbr = frappe.get_value("Company", self.college, "abbr")
		self.name = make_autoname(f"APA/{college_abbr}/{self.from_year}-{self.to_year}")

	def validate(self):
		self.check_college()
		self.fetch_percentage_calculation()
		if self.workflow_state == "Waiting Approval":
			self.calculate_output_rating()
			self.calculate_outcome_rating()
			self.calculate_overall_rating()

	def check_college(self):
		college = frappe.get_value("Annual Performance Assessment", {"college": self.college, "from_year": self.from_year, "to_year": self.to_year, "docstatus": 1}, "name")
		if college:
			frappe.throw("Annual Performance Assessment exist for college <b>{0}</b> from year <b>{1}</b> to <b>{2}</b>".format(self.college, self.from_year, self.to_year))

	def fetch_percentage_calculation(self):
		self.output_calculation = frappe.get_single_value("APA Settings", "output_2b_percentage")
		if not self.output_calculation:
			frappe.throw("Set Output Percent Calculation in APA Settings")

		self.outcome_calculation = frappe.get_single_value("APA Settings", "outcome_2a_percentage")
		if not self.outcome_calculation:
			frappe.throw("Set Outcome Percent Calculation in APA Settings")

	def calculate_output_rating(self):
		output_calc = 0
		output_total_val = 0
		for item in self.get("output_items"):
			output_calc += flt(item.weighted_score, 2)
			output_total_val += flt(item.weightage, 2)

		if self.get("output_extra_items"):
			for item in self.get("output_extra_items"):
				output_calc += flt(item.weighted_score, 2)
				output_total_val += flt(item.weightage, 2)

		self.output_rating = output_calc/output_total_val * 100

	def calculate_outcome_rating(self):
		outcome_calc = 0
		for item in self.get("outcome_items"):
			outcome_calc += flt(item.irt_rating, 2)

		self.outcome_rating = outcome_calc/flt(len(self.outcome_items), 2)

	def calculate_overall_rating(self):
		self.output_value = flt(self.output_rating, 2) * flt(self.output_calculation, 2)/100
		self.outcome_value = flt(self.outcome_rating, 2) * flt(self.outcome_calculation, 2)/100
		self.overall_rating = self.output_value + self.outcome_value
		category = frappe.db.sql("""
			SELECT
				category
			FROM `tabInterpolation Category`
			WHERE parent = 'APA Settings'
			AND min < %s AND max >= %s
		""", (self.overall_rating, self.overall_rating), pluck=True)
		
		self.performance = category[0]
		# if self.overall_rating > 100:
		# 	frappe.throw("Overall rating percentage cannot be more than 100")


@frappe.whitelist()
def fetch_output_and_outcome(from_year, to_year, college):
	if not from_year or not to_year or not college:
		frappe.throw("Select Fiscal Year and College")
	output = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.activity_link,
			atoi.sub_activity_no,
			atoi.unit,
			atoi.weightage,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.activities_no,
			atoi.sub_activity,
			atoi.target,
			atoi.justification
		FROM `tabAPA Mid Term Review` ats
		INNER JOIN `tabAPA Target Output Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Mid Term Review" AND ats.college = %s AND ats.docstatus = 1
		ORDER BY atoi.idx desc
	''',(from_year, to_year, college), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	output_extra = frappe.db.sql('''
		SELECT  
			atoi.output_no,
			atoi.project_no,
			atoi.unit,
			atoi.weightage,
			atoi.output,
			atoi.project,
			atoi.activities,
			atoi.sub_activity,
			atoi.activity_link,
			atoi.sub_activity_link,
			atoi.target,
			atoi.justification
		FROM `tabAPA Mid Term Review` ats
		INNER JOIN `tabAPA Output Extra Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Mid Term Review" AND ats.college = %s AND ats.docstatus = 1
		ORDER BY atoi.idx desc
	''',(from_year, to_year, college), as_dict=True)

	if not output:
		frappe.throw("No Output Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	outcome = frappe.db.sql('''
		SELECT  
			atoi.outcome,
			atoi.unit,
			atoi.weightage,
			atoi.target,
			atoi.justification
		FROM `tabAPA Mid Term Review` ats
		INNER JOIN `tabAPA Target Outcome Item` atoi ON ats.name = atoi.parent
		WHERE ats.from_year = %s AND ats.to_year = %s AND atoi.parenttype = "APA Mid Term Review" AND ats.college = %s AND ats.docstatus = 1
	''',(from_year, to_year, college), as_dict=True)

	if not outcome:
		frappe.throw("No Outcome Indicator found from year <b>{0}</b> to <b>{1}</b> for <b>{2}</b>".format(from_year, to_year, college))

	return {
		"output": output,
		"output_extra": output_extra,
		"outcome": outcome
	}

@frappe.whitelist()
def calculate_outcome_irt_rating(raw_rating, outcome, unit, from_year, to_year, college):
	outcome_category = None
	irt_rating = 0
	if unit in ["Percent", "Number", "Survey"]:
		outcome_category = frappe.db.sql('''
			SELECT 
				oi.is_not_range,
				oii.category,
				oii.max as apa_max,
				oii.min as apa_min,
				oii.unit as target,
				oii.category,
				oii.raw_rating as score
			FROM `tabOutcome Target Setup` oi
			INNER JOIN `tabOutcome Indicator Item` oii ON oi.name = oii.parent
			WHERE oi.outcome = %s AND oi.from_year = %s AND oi.to_year = %s AND disabled = 0
			AND oi.college = %s
			AND ((oi.is_not_range = 1 AND oii.unit = %s)
				OR
				(
					IFNULL(oi.is_not_range, 0) = 0
					AND oii.min <= %s
					AND oii.max >= %s
				)
			)
		''',(outcome, from_year, to_year, college, flt(raw_rating, 2), flt(raw_rating, 2), flt(raw_rating, 2)), as_dict=True)
	elif unit == "Status of Work":
		outcome_category = frappe.db.sql('''
			SELECT oii.category, oii.raw_rating as score
			FROM `tabOutcome Target Setup` oi
			INNER JOIN `tabOutcome Indicator Item` oii ON oi.name = oii.parent
			WHERE oi.outcome = %s AND oi.from_year = %s AND oi.to_year = %s AND disabled = 0
			AND oi.college = %s AND oii.unit = %s
		''',(outcome, from_year, to_year, college, raw_rating), as_dict=True)
	# if not outcome_category:
	# 	frappe.throw("Category not found in Outcome Target Setup")
	if outcome_category:
		interpolation_categories = frappe.db.sql("""
			SELECT
				pms_max,
				pms_min
			FROM `tabInterpolation Formula`
			WHERE parent = 'APA Settings'
			AND category = %s
		""", (outcome_category[0].category), as_dict=True)

		new_raw_rating = 0
		if unit in ["Percent", "Number", "Survey"]:
			if outcome_category[0].is_not_range == 1:
				new_raw_rating = outcome_category[0].score
			else:
				new_raw_rating = raw_rating
		elif unit == "Status of Work":
			new_raw_rating = outcome_category[0].score

		if unit == "Status of Work":
			irt_rating = new_raw_rating
		else:
			if outcome_category[0].is_not_range == 1:
				irt_rating = new_raw_rating
			else:
				irt_rating = ((flt(new_raw_rating, 2) - flt(outcome_category[0].apa_min, 2)) / (flt(outcome_category[0].apa_max, 2) - flt(outcome_category[0].apa_min, 2))) * (flt(interpolation_categories[0].pms_max, 2) - flt(interpolation_categories[0].pms_min, 2)) + flt(interpolation_categories[0].pms_min, 2)
	else:
		irt_rating = 0
	return {
		"irt_rating": irt_rating,
		"category": outcome_category[0].category
	}

@frappe.whitelist()
def calculate_output_irt_rating(raw_rating, activity_link, unit, weightage, college, from_year, to_year, sub_activity_no = None):
	output_category = None
	irt_rating = 0
	if sub_activity_no:
		# if unit == "Percent":
		# 	output_category = frappe.db.sql('''
		# 		SELECT  
		# 			oii.category
		# 		FROM `tabAPA Sub Activities` oi
		# 		INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
		# 		WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s
		# 		AND oi.college = %s AND oii.min < %s AND oii.max >= %s AND oi.disabled = 0
		# 	''',(sub_activity_no, from_year, to_year, college, raw_rating, raw_rating), as_dict=True)
		if unit in ["Percent", "Number", "Survey"]:
			output_category = frappe.db.sql('''
				SELECT  
					oi.is_not_range,
					oii.category,
					oii.max as apa_max,
					oii.min as apa_min,
					oii.unit as target,
					oii.category,
					oii.raw_rating as score
				FROM `tabAPA Sub Activities` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s
				AND oi.college = %s AND (
					(oi.is_not_range = 1 AND oii.unit = %s)
					OR
					(
						IFNULL(oi.is_not_range, 0) = 0
						AND oii.min <= %s
						AND oii.max >= %s
					)
				) AND oi.disabled = 0
			''',(sub_activity_no, from_year, to_year, college, flt(raw_rating, 2), flt(raw_rating, 2), flt(raw_rating, 2)), as_dict=True)
		elif unit == "Status of Work":
			output_category = frappe.db.sql('''
				SELECT  
					oii.category, oii.raw_rating as score
				FROM `tabAPA Sub Activities` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s
				AND oi.college = %s AND oii.unit = %s AND oi.disabled = 0
			''',(sub_activity_no, from_year, to_year, college, raw_rating), as_dict=True)
	else:
		# if unit == "Percent":
		# 	output_category = frappe.db.sql('''
		# 		SELECT  
		# 			oii.category
		# 		FROM `tabPlanning Activities Target Setup` oi
		# 		INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
		# 		WHERE oi.activities = %s AND oi.from_year = %s AND oi.to_year = %s
		# 		AND oi.college = %s AND oii.min < %s AND oii.max >= %s AND oi.disabled = 0
		# 	''',(activity_link, from_year, to_year, college, raw_rating, raw_rating), as_dict=True)
		if unit in ["Percent", "Number", "Survey"]:
			output_category = frappe.db.sql('''
				SELECT  
					oi.is_not_range,
					oii.category,
					oii.max as apa_max,
					oii.min as apa_min,
					oii.unit as target,
					oii.category,
					oii.raw_rating as score
				FROM `tabPlanning Activities Target Setup` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.activities = %s AND oi.from_year = %s AND oi.to_year = %s
				AND oi.college = %s AND (
					(oi.is_not_range = 1 AND oii.unit = %s)
					OR
					(
						IFNULL(oi.is_not_range, 0) = 0
						AND oii.min <= %s
						AND oii.max >= %s
					)
				) AND oi.disabled = 0
			''',(activity_link, from_year, to_year, college, flt(raw_rating, 2), flt(raw_rating, 2), flt(raw_rating, 2)), as_dict=True)
		elif unit == "Status of Work":
			output_category = frappe.db.sql('''
				SELECT  
					oii.category, oii.raw_rating as score
				FROM `tabPlanning Activities Target Setup` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.activities = %s AND oi.from_year = %s AND oi.to_year = %s
				AND oi.college = %s AND oii.unit = %s AND oi.disabled = 0
			''',(activity_link, from_year, to_year, college, raw_rating), as_dict=True)
	
	# if not output_category:
	# 	frappe.throw("Category not found in Planning Activities Target Setup or APA Sub Activities")
	# frappe.throw(str(output_category))
	if output_category:
		interpolation_categories = frappe.db.sql("""
			SELECT
				pms_max,
				pms_min
			FROM `tabInterpolation Formula`
			WHERE parent = 'APA Settings'
			AND category = %s
		""", (output_category[0].category), as_dict=True)

		new_raw_rating = 0
		if unit in ["Percent", "Number", "Survey"]:
			if output_category[0].is_not_range == 1:
				new_raw_rating = output_category[0].score
			else:
				new_raw_rating = raw_rating
		elif unit == "Status of Work":
			new_raw_rating = output_category[0].score

		if unit == "Status of Work":
			irt_rating = new_raw_rating
		else:
			if output_category[0].is_not_range == 1:
				irt_rating = new_raw_rating
			else:
				irt_rating = ((flt(new_raw_rating, 2) - flt(output_category[0].apa_min, 2)) / (flt(output_category[0].apa_max, 2) - flt(output_category[0].apa_min, 2))) * (flt(interpolation_categories[0].pms_max, 2) - flt(interpolation_categories[0].pms_min, 2)) + flt(interpolation_categories[0].pms_min, 2)
		
		weighted_score = flt(irt_rating, 2)/100*flt(weightage, 2)
	else:
		irt_rating = 0
		weighted_score = 0

	return {
		"irt_rating": irt_rating,
		"weighted_score": weighted_score,
		"category": output_category[0].category,
	}

@frappe.whitelist()
def calculate_extra_output_irt_rating(raw_rating, activity_link, unit, weightage, college, from_year, to_year, sub_activity_link = None):
	output_category = None
	irt_rating = 0
	if sub_activity_link:
		# if unit == "Percent":
		# 	output_category = frappe.db.sql('''
		# 		SELECT
		# 			oii.category
		# 		FROM `tabAdditional Sub Activities` oi
		# 		INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
		# 		WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s AND oi.disabled = 0
		# 		AND oi.college = %s AND oii.min < %s AND oii.max >= %s
		# 	''',(sub_activity_link, from_year, to_year, college, raw_rating, raw_rating), as_dict=True)
		if unit in ["Percent", "Number", "Survey"]:
			output_category = frappe.db.sql('''
				SELECT
					oi.is_not_range,
					oii.category,
					oii.max as apa_max,
					oii.min as apa_min,
					oii.unit as target,
					oii.raw_rating as score
				FROM `tabAdditional Sub Activities` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s AND oi.disabled = 0
				AND oi.college = %s AND (
					(oi.is_not_range = 1 AND oii.unit = %s)
					OR
					(
						IFNULL(oi.is_not_range, 0) = 0
						AND oii.min <= %s
						AND oii.max >= %s
					)
				)
			''',(sub_activity_link, from_year, to_year, college, flt(raw_rating, 2), flt(raw_rating, 2), flt(raw_rating, 2)), as_dict=True)
		elif unit == "Status of Work":
			output_category = frappe.db.sql('''
				SELECT  
					oii.category, oii.raw_rating as score
				FROM `tabAdditional Sub Activities` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s AND oi.disabled = 0
				AND oi.college = %s AND oii.unit = %s
			''',(sub_activity_link, from_year, to_year, college, raw_rating), as_dict=True)
	else:
		# if unit == "Percent":
		# 	output_category = frappe.db.sql('''
		# 		SELECT  
		# 			oii.category
		# 		FROM `tabAdditional Activities` oi
		# 		INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
		# 		WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s AND oi.disabled = 0
		# 		AND oi.college = %s AND oii.min < %s AND oii.max >= %s
		# 	''',(activity_link, from_year, to_year, college, raw_rating, raw_rating), as_dict=True)
		if unit in ["Percent", "Number"]:
			output_category = frappe.db.sql('''
				SELECT  
					oi.is_not_range,
					oii.category,
					oii.max as apa_max,
					oii.min as apa_min,
					oii.unit as target,
					oii.category,
					oii.raw_rating as score
				FROM `tabAdditional Activities` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s AND oi.disabled = 0
				AND oi.college = %s AND (
					(oi.is_not_range = 1 AND oii.unit = %s)
					OR
					(
						IFNULL(oi.is_not_range, 0) = 0
						AND oii.min <= %s
						AND oii.max >= %s
					)
				)
			''',(activity_link, from_year, to_year, college, flt(raw_rating, 2), flt(raw_rating, 2), flt(raw_rating, 2)), as_dict=True)
		elif unit == "Status of Work":
			output_category = frappe.db.sql('''
				SELECT  
					oii.category, oii.raw_rating as score
				FROM `tabAdditional Activities` oi
				INNER JOIN `tabOutput Category Item` oii ON oi.name = oii.parent
				WHERE oi.name = %s AND oi.from_year = %s AND oi.to_year = %s AND oi.disabled = 0
				AND oi.college = %s  AND oii.unit = %s
			''',(activity_link, from_year, to_year, college, raw_rating), as_dict=True)
	
	# if not output_category:
	# 	frappe.throw("Category not found in Planning Activities or APA Sub Activities")
	if output_category:
		interpolation_categories = frappe.db.sql("""
			SELECT
				pms_max,
				pms_min
			FROM `tabInterpolation Formula`
			WHERE parent = 'APA Settings'
			AND category = %s
		""", (output_category[0].category), as_dict=True)

		new_raw_rating = 0
		if unit in ["Percent", "Number", "Survey"]:
			if output_category[0].is_not_range == 1:
				new_raw_rating = output_category[0].score
			else:
				new_raw_rating = raw_rating

		# elif unit == "Number":
		# 	max_value = frappe.db.sql("""
		# 		SELECT MAX(`max`)
		# 		FROM `tabOutput Category Item`
		# 		WHERE parent = %s
		# 	""", sub_activity_no if sub_activity_no else activity_link, pluck=True)
		# 	new_raw_rating = flt(raw_rating, 2)/flt(max_value[0], 2)*100
		elif unit == "Status of Work":
			new_raw_rating = output_category[0].score

		if unit == "Status of Work":
			irt_rating = new_raw_rating
		else:
			if output_category[0].is_not_range == 1:
				irt_rating = new_raw_rating
			else:
				irt_rating = ((flt(new_raw_rating, 2) - flt(output_category[0].apa_min, 2)) / (flt(output_category[0].apa_max, 2) - flt(output_category[0].apa_min, 2))) * (flt(interpolation_categories[0].pms_max, 2) - flt(interpolation_categories[0].pms_min, 2)) + flt(interpolation_categories[0].pms_min, 2)
		
		weighted_score = flt(irt_rating, 2)/100*flt(weightage, 2)
	else:
		irt_rating = 0
		weighted_score = 0

	return {
		"irt_rating": irt_rating,
		"weighted_score": weighted_score,
		"category": output_category[0].category,
	}

@frappe.whitelist()
def get_category_for_irt_rating(irt_rating, unit):
	category = frappe.db.sql("""
		SELECT
			category
		FROM `tabInterpolation Category`
		WHERE parent = 'APA Settings'
		AND min <= %s AND max >= %s
	""", (irt_rating if unit != "Number" else flt(irt_rating), irt_rating if unit != "Number" else flt(irt_rating)), as_dict=True)
	
	# irt_rating = ((flt(raw_rating, 2) - flt(interpolation_categories[0].apa_min, 2)) / (flt(interpolation_categories[0].apa_max, 2) - flt(interpolation_categories[0].apa_min, 2))) * (flt(interpolation_categories[0].pms_max, 2) - flt(interpolation_categories[0].pms_min, 2)) + flt(interpolation_categories[0].pms_min, 2)
	return category[0].category