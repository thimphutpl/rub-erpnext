import frappe
from frappe.model.document import Document
from frappe import _

class HostelAllocationBulkUpload(Document):

    def before_submit(self):
        self.validate_room_capacity()
        self.validate_student_allocations()
        self.validate_previous_year_active_students()

    def on_submit(self):
        self.update_hostel_room_students()

    def validate_room_capacity(self):
        """Validate that no room exceeds capacity for the same academic year."""
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

            if existing_count + new_count > room_capacity:
                frappe.throw(_("Room {0} will have {1} students after this allocation. "
                               "Maximum allowed is {2} for academic year {3}.").format(
                    room_code, existing_count + new_count, room_capacity, self.year
                ))

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

        if duplicates:
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
            if all_active:
                frappe.throw(_("Room G-1 has already reached its maximum capacity, and the student is still active."))
                

    def update_hostel_room_students(self):
        """
        Update student_list in Hostel Room:
        - Keep Active students from previous years
        - Replace Left students with current year's Active students
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
                hostel_room.set("student_list", [])

                existing_students = frappe.db.sql("""
                    SELECT hai.student_code, hai.first_name, hai.last_name, habu.year, hai.status
                    FROM `tabHostel Allocation Item` hai
                    JOIN `tabHostel Allocation Bulk Upload` habu 
                        ON hai.parent = habu.name
                    WHERE habu.docstatus = 1
                    AND hai.hostel_room = %s
                """, (room_code,), as_dict=1)

                for s in existing_students:
                    if s["status"] == "Active" and s["year"] < self.year:
                        hostel_room.append("student_list", s)
                for ns in new_students:
                    hostel_room.append("student_list", ns)

                hostel_room.save()
                frappe.msgprint(_("Updated student list for room {0} for academic year {1}")
                                .format(room_code, self.year))

            except frappe.DoesNotExistError:
                frappe.msgprint(_("Hostel Room {0} does not exist.").format(room_code),
                                indicator="orange", alert=True)
            except Exception as e:
                frappe.msgprint(_("Error updating room {0}: {1}").format(room_code, str(e)),
                                indicator="red", alert=True)
