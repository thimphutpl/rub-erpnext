import frappe
from frappe.model.document import Document
from frappe import _

class HostelAllocationBulkUpload(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.model.document import Document
        from frappe.types import DF

        amended_from: DF.Link | None
        company: DF.Link
        posting_date: DF.Date
        re_allocate_hostel_room: DF.Check
        table_caon: DF.Table[Document]
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
        
    # def on_cancel(self):
    #     """Revert hostel room student allocations when this document is cancelled."""
    #     room_allocations = {}

    #     for row in self.table_caon:
    #         if row.hostel_room and row.student_code:
    #             room_allocations.setdefault(row.hostel_room, []).append(row.student_code)

    #     for room_code, students_to_remove in room_allocations.items():
    #         try:
    #             hostel_room = frappe.get_doc("Hostel Room", room_code)
    #             hostel_room.set("student_list", [])

    #             existing_students = frappe.db.sql("""
    #                 SELECT hai.student_code, hai.first_name, hai.last_name, hai.status, habu.year
    #                 FROM `tabHostel Allocation Item` hai
    #                 JOIN `tabHostel Allocation Bulk Upload` habu 
    #                     ON hai.parent = habu.name
    #                 WHERE habu.docstatus = 1
    #                 AND habu.name != %s
    #                 AND hai.hostel_room = %s
    #             """, (self.name, room_code), as_dict=1)

    #             for s in existing_students:
    #                 hostel_room.append("student_list", s)

    #             hostel_room.save()
    #             frappe.msgprint(_("Reverted student list for room {0} after cancellation of allocation {1}")
    #                             .format(room_code, self.name))

    #         except frappe.DoesNotExistError:
    #             frappe.msgprint(_("Hostel Room {0} does not exist.").format(room_code),
    #                             indicator="orange", alert=True)
    #         except Exception as e:
    #             frappe.msgprint(_("Error reverting room {0}: {1}").format(room_code, str(e)),
    #                             indicator="red", alert=True)

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

        

    # def validate_room_capacity(self):
    #     """Validate that no room exceeds capacity for the same academic year."""
    #     room_students = {}
    #     for row in self.table_caon:
    #         if row.hostel_room:
    #             room_students[row.hostel_room] = room_students.get(row.hostel_room, 0) + 1

    #     for room_code, new_count in room_students.items():
    #         existing_count = frappe.db.sql("""
    #             SELECT COUNT(*) as count
    #             FROM `tabHostel Allocation Item` hai
    #             JOIN `tabHostel Allocation Bulk Upload` habu 
    #                 ON hai.parent = habu.name
    #             WHERE habu.docstatus = 1 
    #             AND hai.hostel_room = %s
    #             AND habu.year = %s
    #         """, (room_code, self.year), as_dict=1)[0].count

    #         room_capacity = frappe.db.get_value("Hostel Room", room_code, "capacity")
    #         if not room_capacity:
    #             frappe.throw(_("Room {0} does not exist or capacity is not set.").format(room_code))

    #         if existing_count + new_count > room_capacity:
    #             frappe.throw(_("Room {0} will have {1} students after this allocation. "
    #                            "Maximum allowed is {2} for academic year {3}.").format(
    #                 room_code, existing_count + new_count, room_capacity, self.year
    #             ))

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
                frappe.throw(_("Room {0} has already reached its maximum capacity {1}, and the student is still active.").format(row.hostel_room, row.capacity))
                

    # def update_hostel_room_students(self):
    #     """
    #     Update student_list in Hostel Room:
    #     - Keep Active students from previous years
    #     - Replace Left students with current year's Active students
    #     """
    #     room_allocations = {}
    #     for row in self.table_caon:
    #         if row.hostel_room and row.student_code:
    #             room_allocations.setdefault(row.hostel_room, []).append({
    #                 "student_code": row.student_code,
    #                 "first_name": row.first_name,
    #                 "last_name": row.last_name,
    #                 "year": self.year,
    #                 "status": row.status
    #             })

    #     for room_code, new_students in room_allocations.items():
    #         try:
    #             hostel_room = frappe.get_doc("Hostel Room", room_code)
    #             hostel_room.set("student_list", [])

    #             existing_students = frappe.db.sql("""
    #                 SELECT hai.student_code, hai.first_name, hai.last_name, habu.year, hai.status
    #                 FROM `tabHostel Allocation Item` hai
    #                 JOIN `tabHostel Allocation Bulk Upload` habu 
    #                     ON hai.parent = habu.name
    #                 WHERE habu.docstatus = 1
    #                 AND hai.hostel_room = %s
    #             """, (room_code,), as_dict=1)

    #             if self.re_allocate_hostel_room:
    #                 # Clear all existing students
    #                 hostel_room.set("student_list", [])
    #             else:
    #                 for s in existing_students:
    #                     if s["status"] == "Active" and s["year"] < self.year:
    #                         hostel_room.append("student_list", s)
    #                 for ns in new_students:
    #                     hostel_room.append("student_list", ns)

    #                 hostel_room.save()
    #                 frappe.msgprint(_("Updated student list for room {0} for academic year {1}")
    #                                 .format(room_code, self.year))

    #         except frappe.DoesNotExistError:
    #             frappe.msgprint(_("Hostel Room {0} does not exist.").format(room_code),
    #                             indicator="orange", alert=True)
    #         except Exception as e:
    #             frappe.msgprint(_("Error updating room {0}: {1}").format(room_code, str(e)),
    #                             indicator="red", alert=True)

    def update_hostel_room_students(self):
        """
        Update student_list in Hostel Room:
        - If re_allocate_hostel_room = 1 → Replace existing students (within capacity)
        - Else → Keep previous Active students and append new ones (within capacity)
        """

        room_allocations = {}

        for row in self.table_caon:
            if row.hostel_room and row.student_code:
                room_allocations.setdefault(row.hostel_room, []).append({
                    "student_code": row.student_code,
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
                        SELECT hai.student_code, hai.first_name, hai.last_name, 
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