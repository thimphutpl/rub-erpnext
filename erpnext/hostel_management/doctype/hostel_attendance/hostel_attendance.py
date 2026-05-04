# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class HostelAttendance(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.hostel_management.doctype.hostel_attendance_details.hostel_attendance_details import HostelAttendanceDetails
        from erpnext.hostel_management.doctype.hostel_councillor_item.hostel_councillor_item import HostelCouncillorItem
        from frappe.types import DF

        amended_from: DF.Link | None
        company: DF.Link
        councilor_name: DF.Data | None
        fiscal_year: DF.Link
        hostel_block: DF.Link
        hostel_councellor: DF.Link | None
        hostel_councillor: DF.Table[HostelCouncillorItem]
        last_name: DF.Data | None
        posting_date: DF.Date
        student_councilor: DF.Link
        table_tulk: DF.Table[HostelAttendanceDetails]
    # end: auto-generated types

    def validate(self):
        """Validate before saving"""
        self.validate_duplicate_attendance()
    
    def validate_duplicate_attendance(self):
        """Check if attendance already exists for this posting date and hostel block"""
        if not self.posting_date or not self.hostel_block:
            return
        
        # Check if there's already a submitted Hostel Attendance for this date and block
        existing_attendance = frappe.db.exists(
            "Hostel Attendance",
            {
                "posting_date": self.posting_date,
                "hostel_block": self.hostel_block,
                "docstatus": 1,  # Submitted/Submitted documents
                "name": ["!=", self.name]  # Exclude current document if editing
            }
        )
        
        if existing_attendance:
            frappe.throw(
                _("Hostel Attendance already exists for Block {0} on {1}. Please edit the existing attendance record.").format(
                    frappe.bold(self.hostel_block),
                    frappe.bold(frappe.utils.format_date(self.posting_date))
                )
            )
            
    def on_submit(self):
        """Auto-create HostelAttendanceEntry records for each student when submitting attendance"""
        self.create_hostel_attendance_entries()

    def create_hostel_attendance_entries(self):
        """Create individual HostelAttendanceEntry records for each student in the attendance table"""
        
        if not self.table_tulk:
            frappe.msgprint(_("No attendance records found to create entries."))
            return

        # Build full councilor name from first_name + last_name
        full_councilor_name = ""
        if self.councilor_name:
            full_councilor_name = self.councilor_name
            # If there's a last_name field, append it
            if hasattr(self, 'last_name') and self.last_name:
                full_councilor_name = f"{self.councilor_name} {self.last_name}"            
        
        created_count = 0
        skipped_count = 0
        
        for row in self.table_tulk:
            # Skip if no student code
            if not row.student_code:
                skipped_count += 1
                continue
            
            # Check if attendance entry already exists for this student on this date
            existing_entry = frappe.db.exists("Hostel Attendance Entry", {
                "student_code": row.student_code,
                "posting_date": self.posting_date,
                "attendance": row.attendance
            })
            
            if existing_entry:
                skipped_count += 1
                continue
            
            # Create new Hostel Attendance Entry
            try:
                attendance_entry = frappe.get_doc({
                    "doctype": "Hostel Attendance Entry",
                    "posting_date": self.posting_date,
                    "student_code": row.student_code,
                    "student_name": row.student_name,
                    "room_number": row.room_number,
                    "attendance": row.attendance,
                    "college": self.company,
                    "hostel_councilor": self.student_councilor,
                    "councilor_name": full_councilor_name,
                    "transaction_type": "Hostel Attendance",
			        "transaction_name": self.name,
                })
                
                attendance_entry.insert()
                attendance_entry.submit()
                created_count += 1
                
            except Exception as e:
                frappe.log_error(
                    title="Hostel Attendance Entry Creation Error",
                    message=f"Error creating attendance entry for student {row.student_code}: {str(e)}"
                )
                frappe.msgprint(_(f"Error creating attendance entry for student {row.student_code}: {str(e)}"), 
                              indicator='orange', alert=True)
        
        # Show summary message
        if created_count > 0:
            frappe.msgprint(_(f"Successfully created {created_count} Hostel Attendance Entry records."))
        if skipped_count > 0:
            frappe.msgprint(_(f"Skipped {skipped_count} records (no student code or already exists)."), 
                          indicator='orange', alert=True)


# @frappe.whitelist()
# def get_hostel_attendance(company, hostel_block):
#     if not company or not hostel_block:
#         return []

#     rooms = frappe.get_all(
#         "Hostel Councillor",
#         filters={"company": company, "hostel_block": hostel_block},
#         fields=["name"],
#     )

#     results = []

#     for r in rooms:
#         block_details = frappe.get_all(
#             "Block Counsellor Details",
#             filters={"parent": r.name, "parenttype": "Hostel Councillor"},
#             fields=["room_number", "student_code", "first_name", "last_name"],
#         )

#         for d in block_details:

#             # 🔥 Skip rows that have no data (prevents empty first row)
#             if not (d.room_number or d.student_code or d.first_name or d.last_name):
#                 continue

#             # Build full name
#             if d.first_name and d.last_name:
#                 full_name = f"{d.first_name} {d.last_name}"
#             elif d.first_name:
#                 full_name = d.first_name
#             elif d.last_name:
#                 full_name = d.last_name
#             else:
#                 full_name = ""

#             results.append({
#                 "room_number": d.room_number,
#                 "student_code": d.student_code,
#                 "student_name": full_name,
#             })

#     return results


@frappe.whitelist()
def get_hostel_attendance(company, hostel_block, posting_date):
    if not company or not hostel_block or not posting_date:
        return []

    rooms = frappe.get_all(
        "Hostel Councillor",
        filters={"company": company, "hostel_block": hostel_block},
        fields=["name"],
    )

    results = []

    for r in rooms:
        block_details = frappe.get_all(
            "Block Counsellor Details",
            filters={"parent": r.name, "parenttype": "Hostel Councillor"},
            fields=["room_number", "student_code", "first_name", "last_name"],
            order_by="room_number ASC"
        )

        for d in block_details:

            if not (d.room_number or d.student_code):
                continue

            # Full name
            full_name = " ".join(filter(None, [d.first_name, d.last_name]))

            #Fetch Student Attendance
            attendance = frappe.db.get_value(
                "Student Attendance",
                {
                    "student": d.student_code,
                    "date": posting_date
                },
                "status"
            )
            # if attendance and len(attendance) > 0:
            results.append({
                "room_number": d.room_number,
                "student_code": d.student_code,
                "student_name": full_name,
                "attendance": attendance if attendance else ""   # only set if exists
            })

    return results

