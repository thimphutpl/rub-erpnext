import frappe
from frappe.model.document import Document


class ClubMembershipList(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.student_services.doctype.club_membership_list_detials.club_membership_list_detials import ClubMembershipListDetials
		from frappe.types import DF

		amended_from: DF.Link | None
		club_member: DF.Table[ClubMembershipListDetials]
		club_name: DF.Link | None
		college: DF.Link | None
	# end: auto-generated types
	
	def validate(self):
		"""Validate the document before saving"""
		self.validate_duplicate_members()
		self.validate_members_exist()
	
	def validate_duplicate_members(self):
		"""Check for duplicate student codes in club_member table"""
		student_codes = []
		duplicate_rows = []
		
		for idx, row in enumerate(self.get("club_member"), start=1):
			if row.student_code:
				if row.student_code in student_codes:
					duplicate_rows.append(f"Row {idx}: {row.student_name} ({row.student_code})")
				else:
					student_codes.append(row.student_code)
		
		if duplicate_rows:
			frappe.throw(
				f"Duplicate student entries found:<br><br>{'<br>'.join(duplicate_rows)}<br><br>Please remove duplicates before saving.",
				title="Duplicate Members"
			)
	
	def validate_members_exist(self):
		"""Validate that all members exist in the database and are active"""
		invalid_members = []
		
		for row in self.get("club_member"):
			if row.student_code:
				# Check if student exists and is active in the selected club
				student = frappe.db.sql("""
					SELECT st.student_name, ca.club_name 
					FROM `tabStudent` st 
					INNER JOIN `tabExtra Curricular Activities Details` ca 
						ON st.name = ca.parent
					WHERE st.name = %s 
						AND st.status = 'Active' 
						AND st.company = %s 
						AND ca.club_name = %s
				""", (row.student_code, self.college, self.club_name), as_dict=1)
				
				if not student:
					invalid_members.append(f"{row.student_name} ({row.student_code})")
		
		if invalid_members:
			frappe.throw(
				f"The following students are not active members of {self.club_name}:<br><br>{'<br>'.join(invalid_members)}",
				title="Invalid Members"
			)
	
	@frappe.whitelist()
	def get_member(self):
		"""Fetch and add active club members from the database"""
		try:
			# Validate required fields
			if not self.college:
				frappe.throw("Please select College/Company first")
			if not self.club_name:
				frappe.throw("Please select Club Name first")
			
			# Get existing student codes from the child table to check duplicates
			existing_students = set()
			for member in self.get("club_member"):
				if member.student_code:
					existing_students.add(member.student_code)
			
			# Fetch active members from database
			potential_members = frappe.db.sql("""
				SELECT 
					st.name as student_code,
					st.student_name,
					ca.club_name 
				FROM `tabStudent` st 
				INNER JOIN `tabExtra Curricular Activities Details` ca 
					ON st.name = ca.parent
				WHERE st.status = 'Active' and ca.status='Active'
					AND st.company = %s 
					AND ca.club_name = %s
				ORDER BY st.student_name
			""", (self.college, self.club_name), as_dict=1)
			
			if not potential_members:
				frappe.msgprint(
					f"No active members found for {self.club_name}",
					alert=True,
					indicator="yellow"
				)
				return
			
			# Counters for summary
			added_count = 0
			skipped_count = 0
			skipped_members = []
			
			# Add new members
			for member in potential_members:
				# Check if student already exists in the table
				if member.student_code in existing_students:
					skipped_count += 1
					skipped_members.append(f"{member.student_name} ({member.student_code})")
					continue
				
				# Add new member
				self.append("club_member", {
					"student_code": member.student_code,
					"student_name": member.student_name
				})
				
				# Add to existing_students set to prevent duplicates within same run
				existing_students.add(member.student_code)
				added_count += 1
				
				frappe.msgprint(
					f"Added: {member.student_name} ({member.student_code})",
					alert=True,
					indicator="green"
				)
			
			# Show summary message
			summary = f"Added {added_count} new member(s) to {self.club_name}."
			if skipped_count > 0:
				summary += f"<br><br>Skipped {skipped_count} existing member(s):<br>{'<br>'.join(skipped_members[:5])}"
				if skipped_count > 5:
					summary += f"<br>...and {skipped_count - 5} more."
			
			if added_count > 0 or skipped_count > 0:
				frappe.msgprint(
					summary,
					title="Member Import Summary",
					indicator="blue" if added_count > 0 else "orange"
				)
			
		except Exception as e:
			frappe.log_error(
				f"Error in get_member: {str(e)}\nCollege: {self.college}\nClub: {self.club_name}", 
				"Club Membership List Error"
			)
			frappe.throw(f"Failed to fetch club members. Error: {str(e)}")
	
	@frappe.whitelist()
	def clear_members(self):
		"""Clear all members from the table"""
		if self.get("club_member"):
			self.set("club_member", [])
			frappe.msgprint(
				"All members have been cleared from the list.",
				alert=True,
				indicator="red"
			)
	
	@frappe.whitelist()
	def get_member_count(self):
		"""Get count of active members for the selected club"""
		if not self.college or not self.club_name:
			return 0
		
		count = frappe.db.sql("""
			SELECT COUNT(*) as count
			FROM `tabStudent` st 
			INNER JOIN `tabExtra Curricular Activities Details` ca 
				ON st.name = ca.parent
			WHERE st.status = 'Active' 
				AND st.company = %s 
				AND ca.club_name = %s
		""", (self.college, self.club_name))[0][0]
		
		return count