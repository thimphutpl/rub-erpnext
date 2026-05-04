import frappe
from frappe.model.document import Document
from frappe import _

class HostelAllocationBulkUpload(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.hostel_management.doctype.block_counsellor_details.block_counsellor_details import BlockCounsellorDetails
        from erpnext.hostel_management.doctype.hostel_allocation_item.hostel_allocation_item import HostelAllocationItem
        from frappe.types import DF

        amended_from: DF.Link | None
        company: DF.Link
        gender: DF.Literal["", "Male", "Female"]
        hostel_type: DF.TableMultiSelect[BlockCounsellorDetails]
        posting_date: DF.Date
        re_allocate_hostel_room: DF.Check
        table_caon: DF.Table[HostelAllocationItem]
        year: DF.Link
    # end: auto-generated types

    def before_save(self):
        self.validate_room_capacity()
        self.validate_student_allocations()
        self.validate_previous_year_active_students()
        self.validate_student_company()
        # self.validate_duplicate_student_in_room()

    def on_submit(self):
        self.update_hostel_room_students()
        self.create_hostel_allocation_entry()

    def on_cancel(self):
        """
        Remove only students added by this document
        from Hostel Room.student_list
        """

        for row in self.table_caon:
            if not row.hostel_room or not row.student_code:
                continue

            hostel_room = frappe.get_doc("Hostel Room", row.hostel_room)

            updated_list = []

            for student in hostel_room.student_list:
                if not (
                    student.student_code == row.student_code
                    and student.year == self.year
                ):
                    updated_list.append(student)

            hostel_room.set("student_list", [])

            for s in updated_list:
                hostel_room.append("student_list", {
                    "student_code": s.student_code,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "year": s.year,
                })

            hostel_room.save()

        frappe.msgprint(_("Students removed successfully after cancellation."))

    def create_hostel_allocation_entry(self):
        """Create individual HostelAttendanceEntry records for each student in the attendance table"""
        
        if not self.table_caon:
            frappe.msgprint(_("No attendance records found to create entries."))
            return

        # # Build full councilor name from first_name + last_name
        # full_councilor_name = ""
        # if self.councilor_name:
        #     full_councilor_name = self.councilor_name
        #     # If there's a last_name field, append it
        #     if hasattr(self, 'last_name') and self.last_name:
        #         full_councilor_name = f"{self.councilor_name} {self.last_name}"            
        
        created_count = 0
        skipped_count = 0
        
        for row in self.table_caon:
            # Skip if no student code
            if not row.student_code:
                skipped_count += 1
                continue
            
            # Check if attendance entry already exists for this student on this date
            existing_entry = frappe.db.exists("Hostel Allocation Entry", {
                "student": row.student_code,
                "posting_date": self.posting_date,
                "student_name": f"{row.first_name} {row.middle_name} {row.last_name}" if row.first_name and row.middle_name and row.last_name else row.first_name,
                "year": row.year,
                "transaction_type": "Hostel Allocation Bulk Upload",
                "transaction_name": self.name,
                "hostel_type": row.hostel_type,
                "hostel_room": row.hostel_room,
            })
            
            if existing_entry:
                skipped_count += 1
                continue
            
            # Create new Hostel Allocation Entry
            try:
                hostel_entry = frappe.get_doc({
                    "doctype": "Hostel Allocation Entry",
                    "student": row.student_code,
                    "posting_date": self.posting_date,
                    "student_name": f"{row.first_name} {row.middle_name} {row.last_name}" if row.first_name and row.middle_name and row.last_name else row.first_name,
                    "year": row.year,
                    "transaction_type": "Hostel Allocation Bulk Upload",
                    "transaction_name": self.name,
                    "current_hostel_type": row.hostel_type,
                    "current_hostel_room": row.hostel_room,
                    "catering_type": row.catering_type,
                    "scholarship_type": row.scholarship_type
                })
                
                hostel_entry.insert()
                # hostel_entry.submit()
                created_count += 1
                
            except Exception as e:
                frappe.log_error(
                    title="Hostel Hostel Entry Creation Error",
                    message=f"Error creating hostel entry for student {row.student_code}: {str(e)}"
                )
                frappe.msgprint(_(f"Error creating hostel entry for student {row.student_code}: {str(e)}"), 
                              indicator='orange', alert=True)
        
        # Show summary message
        if created_count > 0:
            frappe.msgprint(_(f"Successfully created {created_count} Hostel Entry records."))
        if skipped_count > 0:
            frappe.msgprint(_(f"Skipped {skipped_count} records (no student code or already exists)."), 
                          indicator='orange', alert=True)

    def validate_room_capacity(self):
        """Validate that no room exceeds capacity for the same academic year and status validation."""
        room_students = {}
        for row in self.table_caon:
            if row.hostel_room:
                room_students[row.hostel_room] = room_students.get(row.hostel_room, 0) + 1

        for room_code, new_count in room_students.items():
            existing_count = frappe.db.sql("""
                SELECT COUNT(*) as count
                FROM `tabHostel Allocation Item` hai
                JOIN `tabHostel Allocation Bulk Upload` habu 
                    ON hai.parent = habu.name
                WHERE habu.docstatus = 1 
                AND hai.hostel_room = %s
                AND habu.year = %s
            """, (room_code, self.year), as_dict=1)[0].count
            room_capacity = frappe.db.get_value("Hostel Room", room_code, "capacity")
            if not room_capacity:
                frappe.throw(_("Room {0} does not exist or capacity is not set.").format(room_code))

            if self.re_allocate_hostel_room:
                # Allow replacement, but ensure total does not exceed capacity
                total_students = new_count

                if total_students > room_capacity:
                    frappe.throw(_("Room {0} capacity is {1}. "
                                "Cannot reallocate more than capacity.")
                                .format(room_code, room_capacity))

            else:    
                total_students = existing_count + new_count
                if total_students > room_capacity:
                    frappe.throw(_("Room {0} will have {1} students after this allocation. "
                                "Maximum allowed is {2} for academic year {3}.").format(
                        room_code, total_students, room_capacity, self.year
                    ))
                if total_students == room_capacity:
                    frappe.msgprint(_("Room {0} has reached full capacity ({1}). No more allocations can be made.")
                                    .format(room_code, room_capacity))

    def validate_student_allocations(self):
        """Validate that a student is not assigned to multiple rooms in the SAME academic year."""
        student_rooms = {}
        duplicates = []

        for row in self.table_caon:
            if row.student_code:
                if row.student_code in student_rooms:
                    duplicates.append({
                        'student': row.student_code,
                        'first_room': student_rooms[row.student_code],
                        'second_room': row.hostel_room
                    })
                else:
                    student_rooms[row.student_code] = row.hostel_room

        existing_allocations = frappe.db.sql("""
            SELECT DISTINCT ha.student_code, ha.hostel_room
            FROM `tabHostel Allocation Bulk Upload` h
            JOIN `tabHostel Allocation Item` ha
                ON h.name = ha.parent
            WHERE h.docstatus = 1
            AND h.name != %s
            AND h.year = %s  
            AND ha.student_code IS NOT NULL
        """, (self.name, self.year), as_dict=1)

        existing_student_rooms = {alloc['student_code']: alloc['hostel_room'] for alloc in existing_allocations}

        for row in self.table_caon:
            if row.student_code and row.student_code in existing_student_rooms:
                duplicates.append({
                    'student': row.student_code,
                    'first_room': existing_student_rooms[row.student_code],
                    'second_room': row.hostel_room,
                    'existing': True
                })

        if duplicates and not self.re_allocate_hostel_room:
            msg = _("The following students are assigned to multiple rooms for academic year {0}: ").format(self.year)
            for d in duplicates:
                if d.get('existing'):
                    msg += _("Student {0} is already assigned to room {1} and cannot be assigned to room {2}. ").format(
                        d['student'], d['first_room'], d['second_room']
                    )
                else:
                    msg += _("Student {0} is assigned to both {1} and {2} in this allocation. ").format(
                        d['student'], d['first_room'], d['second_room']
                    )
            frappe.throw(msg)

    def validate_previous_year_active_students(self):
        """
        Prevent submission if all previous year students in the same room are Active.
        Allow replacing only Left students with new Active students.
        """
        for row in self.table_caon:
            if not row.hostel_room or row.status != "Active":
                continue

            prev_students = frappe.db.sql("""
                SELECT hai.student_code, hai.status, habu.year
                FROM `tabHostel Allocation Item` hai
                JOIN `tabHostel Allocation Bulk Upload` habu 
                    ON hai.parent = habu.name
                WHERE habu.docstatus = 1
                AND hai.hostel_room = %s
                AND habu.year < %s
            """, (row.hostel_room, self.year), as_dict=1)

            if not prev_students:
                continue

            all_active = all(s["status"] == "Active" for s in prev_students)
            if all_active and not self.re_allocate_hostel_room:
                frappe.throw(_("Room {0} has already reached its maximum capacity, or the student is still active.").format(row.hostel_room))

    def update_hostel_room_students(self):
        """
        Update student_list in Hostel Room:
        - If re_allocate_hostel_room = 1 → Replace existing students (within capacity)
        - Else → Keep previous Active students and append new ones (within capacity)
        """

        room_allocations = {}

        for row in self.table_caon:
            if row.hostel_room and row.student_code or row.cid_number:
                room_allocations.setdefault(row.hostel_room, []).append({
                    "student_code": row.student_code,
                    "cid_number": row.cid_number,
                    "first_name": row.first_name,
                    "last_name": row.last_name,
                    "year": self.year,
                    "status": row.status
                })

        for room_code, new_students in room_allocations.items():
            try:
                hostel_room = frappe.get_doc("Hostel Room", room_code)
                capacity = hostel_room.capacity or 0

                if self.re_allocate_hostel_room:
                    # 🔁 FULL REPLACEMENT MODE
                    if len(new_students) > capacity:
                        frappe.throw(
                            _("Room {0} capacity is {1}. Cannot allocate {2} students.")
                            .format(room_code, capacity, len(new_students))
                        )

                    hostel_room.set("student_list", [])

                    for ns in new_students:
                        hostel_room.append("student_list", ns)

                else:
                    # ➕ NORMAL MODE (keep previous active students)
                    existing_students = frappe.db.sql("""
                        SELECT hai.student_code, hai.cid_number, hai.first_name, hai.last_name, 
                            habu.year, hai.status
                        FROM `tabHostel Allocation Item` hai
                        JOIN `tabHostel Allocation Bulk Upload` habu 
                            ON hai.parent = habu.name
                        WHERE habu.docstatus = 1
                        AND hai.hostel_room = %s
                    """, (room_code,), as_dict=1)

                    final_students = []

                    # keep previous active students from older years
                    for s in existing_students:
                        if s["status"] == "Active" and s["year"] < self.year:
                            final_students.append(s)

                    final_students.extend(new_students)

                    if len(final_students) > capacity:
                        frappe.throw(
                            _("Room {0} will exceed capacity ({1}).")
                            .format(room_code, capacity)
                        )

                    hostel_room.set("student_list", [])
                    for fs in final_students:
                        hostel_room.append("student_list", fs)

                hostel_room.save()
                frappe.msgprint(
                    _("Room {0} successfully updated for academic year {1}")
                    .format(room_code, self.year)
                )

            except frappe.DoesNotExistError:
                frappe.throw(_("Hostel Room {0} does not exist.").format(room_code))
            except Exception as e:
                frappe.throw(_("Error updating room {0}: {1}").format(room_code, str(e)))

    def validate_duplicate_student_in_room(self):
        """
        Prevent same student_code from being assigned
        to the same hostel_room.
        """

        # Check duplicates inside current document
        seen = set()
        for row in self.table_caon:
            if row.student_code and row.hostel_room:
                key = (row.student_code, row.hostel_room)

                if key in seen:
                    frappe.throw(
                        _("Student {0} is duplicated in Room {1} in this allocation.")
                        .format(row.student_code, row.hostel_room)
                    )
                seen.add(key)

        #Check against already submitted documents
        for row in self.table_caon:
            if not row.student_code or not row.hostel_room:
                continue

            existing = frappe.db.sql("""
                SELECT name FROM `tabHostel Allocation Item`
                WHERE student_code = %s
                AND hostel_room = %s
                AND parent IN (
                    SELECT name FROM `tabHostel Allocation Bulk Upload`
                    WHERE docstatus = 1
                    AND name != %s
                    AND year = %s
                )
            """, (row.student_code, row.hostel_room, self.name, self.year))

            if existing and not self.re_allocate_hostel_room:
                frappe.throw(
                    _("Student {0} is already assigned to Room {1} "
                    "for academic year {2}.")
                    .format(row.student_code, row.hostel_room, self.year)
                )  

    def validate_student_company(self):
        """
        Ensure student belongs to the same company
        as the Hostel Allocation document.
        """

        for row in self.table_caon:
            if not row.student_code:
                continue

            student_company = frappe.db.get_value(
                "Student",
                row.student_code,
                "company"
            )

            if not student_company:
                frappe.throw(
                    _("Student {0} does not have a company assigned.")
                    .format(row.student_code)
                )

            if student_company != self.company:
                frappe.throw(
                    _("Student {0} belongs to Company {1}, "
                    "but this allocation is for Company {2}.")
                    .format(row.student_code, student_company, self.company)
                ) 

# def get_permission_query_conditions(user):
#     if not user:
#         user = frappe.session.user

#     student = frappe.db.get_value(
#         "Student",
#         {"user": user},
#         "gender"
#     )

#     if student:
#         return f"`tabHostel Allocation Bulk Upload`.gender = '{student}'"

#     return "" 

# def get_permission_query_conditions(user):
#     if not user:
#         user = frappe.session.user

#     # Get student linked to user
#     student = frappe.db.get_value(
#         "Student",
#         {"user": user},
#         "name",
#         "gender"
#     )

#     if not student:
#         return ""

#     return f"""
#         EXISTS (
#             SELECT 1 FROM `tabHostel Allocation Item` hai
#             WHERE hai.parent = `tabHostel Allocation Bulk Upload`.name
#             AND hai.student_code = '{student}'
#         )
#     """

@frappe.whitelist()
def get_students(year, gender, company):
    if not year:
        frappe.throw("Please select Year")

    filters = {
        "year": year,
        "status": "Active",
        "company": company
    }

    if gender:
        filters["gender"] = gender

    students = frappe.get_all(
        "Student",
        filters=filters,
        fields=["name", "first_name", "middle_name", "last_name", "gender", "cid", "catering_type", "scholarship_type", "status" ]
    )

    return students

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)
    if "SSO" in user_roles or "Administrator" in user_roles:
        return        

    student = frappe.db.get_value(
        "Student",
        {"user": user},
        ["name", "gender"],
        as_dict=True
    )

    if not student:
        return "1=0"   # No access

    return f"""
        `tabHostel Allocation Bulk Upload`.gender = '{student.gender}'
        AND EXISTS (
            SELECT 1 FROM `tabHostel Allocation Item` hai
            WHERE hai.parent = `tabHostel Allocation Bulk Upload`.name
            AND hai.student_code = '{student.name}'
        )
    """

@frappe.whitelist()
def auto_allocate_rooms(company, year, hostel_types, students):
    import json

    if isinstance(hostel_types, str):
        hostel_types = [h.strip() for h in hostel_types.split(",") if h.strip()]

    if isinstance(students, str):
        students = json.loads(students)

    if not company or not hostel_types or not students:
        return []

    # -------------------------
    # 1. Get Rooms
    # -------------------------
    rooms = frappe.get_all(
        "Hostel Room",
        filters={
            "company": company,
            "hostel_type": ["in", hostel_types]
        },
        fields=["name", "capacity", "hostel_type"],
        order_by="name asc"
    )

    # -------------------------
    # 2. Build Room Availability
    # -------------------------
    room_slots = []

    for room in rooms:
        occupied = frappe.db.count(
            "Student List Item",
            {
                "parent": room.name,
                "parenttype": "Hostel Room"
            }
        )

        available = (room.capacity or 0) - occupied

        if available > 0:
            room_slots.append({
                "room": room.name,
                "hostel_type": room.hostel_type,
                "available": available
            })

    # -------------------------
    # 3. Allocate Students
    # -------------------------
    allocations = []
    student_index = 0

    for slot in room_slots:
        for i in range(slot["available"]):
            if student_index >= len(students):
                break

            student = students[student_index]

            allocations.append({
                "student_code": student.get("student_code"),
                "hostel_room": slot["room"],
                "hostel_type": slot["hostel_type"]
            })

            student_index += 1

        if student_index >= len(students):
            break

    return allocations
