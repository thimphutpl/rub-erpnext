# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class HostelChangeApplication(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        applied_by: DF.Link
        comments_approver: DF.SmallText | None
        company: DF.Link
        current_room: DF.Link | None
        first_name: DF.Data | None
        hostel_type: DF.Data | None
        hostel_type_req: DF.Data | None
        last_name: DF.Data | None
        operation_type: DF.Literal["", "Room Transfer", "Room Swap", "Day Scholar"]
        original_hostel_type: DF.Data | None
        original_room: DF.Link | None
        original_rooms: DF.Link | None
        reason_for_change_for_student: DF.SmallText | None
        requested_room: DF.Link | None
        room: DF.Link | None
        student_code: DF.Link | None
        type: DF.Data | None
    # end: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        applied_by: DF.Link
        comments_approver: DF.SmallText | None
        company: DF.Link | None
        current_room: DF.Link | None
        first_name: DF.Data | None
        hostel_type: DF.Data | None
        hostel_type_req: DF.Data | None
        last_name: DF.Data | None
        qrc: DF.Check
        reason_for_change_for_student: DF.SmallText | None
        requested_room: DF.Link | None
        room: DF.Link | None
        student_code: DF.Link | None
        type: DF.Data | None
        operation_type: DF.Data | None 
        original_room: DF.Link | None  
        original_rooms: DF.Link | None  

    def validate(self):
        """Validate the room change based on frontend operation_type"""
        if not self.operation_type:
            frappe.throw(_("Operation Type is required (Room Transfer or Room Swap)."))

        if self.operation_type == "Room Transfer":
            if not self.requested_room:
                frappe.throw(_("Requested Room is required for Room Transfer."))
            self.validate_room_capacity()

        elif self.operation_type == "Room Swap":
            if not self.room:
                frappe.throw(_("Room to swap with is required for Room Swap."))
            self.validate_room_swap()
        
        elif self.operation_type == "Day Scholar":
            self.on_update_after_submit()

        else:
            frappe.throw(_("Invalid operation type. Must be Room Transfer or Room Swap."))

    def validate_room_swap(self):
        """Validate if the room swap is possible"""
        if self.current_room == self.room:
            frappe.throw(_("Cannot swap with the same room. Please select a different room."))

        room_doc = frappe.get_doc("Hostel Room", self.room)
        if not room_doc.student_list or len(room_doc.student_list) == 0:
            frappe.throw(_(f"Room {self.room} has no students to swap with"))

    def validate_room_capacity(self):
        """Check if requested room has not exceeded its defined capacity"""
        if self.operation_type == "Room Transfer" and self.current_room == self.requested_room:
            frappe.throw(
                _("You cannot transfer to the same room ({0}). Please select a different room.").format(self.requested_room)
            )
        requested_room_doc = frappe.get_doc("Hostel Room", self.requested_room)
        room_capacity = requested_room_doc.capacity
        current_student_count = len(requested_room_doc.get("student_list", []))
        if current_student_count >= room_capacity:
            frappe.throw(
                _("Requested room {0} has reached its full capacity ({1} students). Cannot proceed with room change.").format(
                    self.requested_room, room_capacity
                )
            )


    def on_submit(self):
        """Submit the room change based on frontend operation_type"""
        self.db_set("original_room", self.current_room)

        if self.operation_type == "Room Transfer":
            self.move_student()
        elif self.operation_type == "Room Swap":
            self.swap_student()
        elif self.operation_type == "Day Scholar":
            self.on_update_after_submit()
        else:
            frappe.throw(_("Invalid operation type. Must be Room Transfer or Room Swap."))
            
    def on_update_after_submit(self):
        if self.operation_type == "Day Scholar":
            self.remove_student_from_room()

    def remove_student_from_room(self):
        if not self.current_room:
            return

        room = frappe.get_doc("Hostel Room", self.current_room)
        for row in room.student_list:
            if row.student_code == self.applied_by:
                room.remove(row)
                break

        room.save()
        frappe.db.commit()
  

    def on_cancel(self):
        """Revert the room change when cancelled"""
        try:
            if not self.operation_type:
                frappe.throw(_("No operation type found for cancel. Cannot revert."))

            if self.operation_type == "Room Transfer":
                self.revert_move_student()
            elif self.operation_type == "Room Swap":
                self.revert_swap_student()
            elif self.operation_type == "Day Scholar":
                self.revert_dayscholar_student()
            else:
                frappe.throw(_("Invalid operation type for cancel."))
            self.operation_type = None
            self.db_set("operation_type", None)

        except Exception as e:
            frappe.throw(_(f"Error while cancelling room change: {str(e)}"))

    def move_student(self):
        """Move student to requested room"""
        current_room_doc = frappe.get_doc("Hostel Room", self.current_room)
        new_room_doc = frappe.get_doc("Hostel Room", self.requested_room)
        current_room_doc.set("student_list", [
            s for s in current_room_doc.student_list if s.student_code != self.applied_by
        ])
        current_room_doc.save(ignore_permissions=True)

        new_room_doc.append("student_list", {
            "student_code": self.applied_by,
            "first_name": self.first_name,
            "last_name": self.last_name
        })
        new_room_doc.save(ignore_permissions=True)
        self.db_set("current_room", self.requested_room)
        self.db_set("hostel_type", new_room_doc.hostel_type)
        frappe.msgprint(_(f"Student moved from {self.original_room} → {self.requested_room}"))

    def swap_student(self):
        """Swap students between two rooms, including updating fields in the Swap DocType"""
        current_room_doc = frappe.get_doc("Hostel Room", self.current_room)
        requested_room_doc = frappe.get_doc("Hostel Room", self.room)

        student_x = next((s for s in current_room_doc.student_list if s.student_code == self.applied_by), None)
        student_y = next((s for s in requested_room_doc.student_list if s.student_code == self.student_code), None)

        if not student_x or not student_y:
            frappe.throw(_("Students not found for swap"))

        self.db_set("original_room", self.current_room)
        self.db_set("original_rooms", self.room)
        current_room_doc.set("student_list", [
            s for s in current_room_doc.student_list if s.student_code != student_x.student_code
        ])
        requested_room_doc.set("student_list", [
            s for s in requested_room_doc.student_list if s.student_code != student_y.student_code
        ])

        requested_room_doc.append("student_list", {
            "student_code": student_x.student_code,
            "first_name": student_x.first_name,
            "last_name": student_x.last_name
        })
        current_room_doc.append("student_list", {
            "student_code": student_y.student_code,
            "first_name": student_y.first_name,
            "last_name": student_y.last_name
        })
        current_room_doc.save(ignore_permissions=True)
        requested_room_doc.save(ignore_permissions=True)
        self.db_set("current_room", self.room)
        self.db_set("hostel_type", requested_room_doc.hostel_type)
        self.db_set("room", self.original_room)
        self.db_set("type", current_room_doc.hostel_type)

        frappe.msgprint(_(
            f"Swapped {student_x.first_name} {student_x.last_name} (from {self.original_room}) "
            f"with {student_y.first_name} {student_y.last_name} (from {self.original_rooms})"
        ))

    
    

    def revert_move_student(self):
        """Revert the move operation (put student back to old room)"""
        old_room_doc = frappe.get_doc("Hostel Room", self.original_room)
        new_room_doc = frappe.get_doc("Hostel Room", self.current_room)
        new_room_doc.set("student_list", [
            s for s in new_room_doc.student_list if s.student_code != self.applied_by
        ])
        new_room_doc.save(ignore_permissions=True)
        old_room_doc.append("student_list", {
            "student_code": self.applied_by,
            "first_name": self.first_name,
            "last_name": self.last_name
        })
        old_room_doc.save(ignore_permissions=True)

        self.db_set("current_room", self.original_room)
        frappe.msgprint(_(f"Reverted move: Student {self.applied_by} restored to {self.original_room}"))

    def revert_swap_student(self):
        """Revert the swap operation (restore both students to original rooms and hostel types)"""
        
        if not self.original_room or not self.original_rooms:
            frappe.throw(_("Original rooms not stored. Cannot revert swap."))
        current_room_doc = frappe.get_doc("Hostel Room", self.current_room)
        requested_room_doc = frappe.get_doc("Hostel Room", self.room)
        student_x = next((s for s in current_room_doc.student_list if s.student_code == self.applied_by), None)
        student_y = next((s for s in requested_room_doc.student_list if s.student_code == self.student_code), None)

        if not student_x or not student_y:
            frappe.throw(_("Students not found to revert swap"))
        current_room_doc.set("student_list", [
            s for s in current_room_doc.student_list if s.student_code != student_x.student_code
        ])
        requested_room_doc.set("student_list", [
            s for s in requested_room_doc.student_list if s.student_code != student_y.student_code
        ])
        requested_room_doc.append("student_list", {
            "student_code": student_x.student_code,
            "first_name": student_x.first_name,
            "last_name": student_x.last_name
        })
        current_room_doc.append("student_list", {
            "student_code": student_y.student_code,
            "first_name": student_y.first_name,
            "last_name": student_y.last_name
        })
        current_room_doc.save(ignore_permissions=True)
        requested_room_doc.save(ignore_permissions=True)
        self.db_set("current_room", self.original_room)
        self.db_set("hostel_type", current_room_doc.hostel_type)
        self.db_set("room", self.original_rooms)
        self.db_set("type", requested_room_doc.hostel_type)

        frappe.msgprint(_(
            f"Reverted swap: {student_x.first_name} {student_x.last_name} back to {self.original_room}, "
            f"{student_y.first_name} {student_y.last_name} back to {self.original_rooms}"
        ))
    def revert_dayscholar_student(self):
        """Revert the Day Scholar operation (restore student back to original room)"""
        try:
            if not self.original_room:
                frappe.throw(_("Original room not found. Cannot revert Day Scholar operation."))
            old_room_doc = frappe.get_doc("Hostel Room", self.original_room)
            old_room_doc.append("student_list", {
                "student_code": self.applied_by,
                "first_name": self.first_name,
                "last_name": self.last_name
            })
            old_room_doc.save(ignore_permissions=True)
            self.db_set("current_room", self.original_room)

            frappe.msgprint(_(f"Reverted Day Scholar Student: Student {self.applied_by} restored to {self.original_room}"))

        except Exception as e:
            frappe.throw(_(f"Error while reverting Day Scholar operation: {str(e)}"))





@frappe.whitelist()
def get_hostel_change_details(student_code):
    """Get student's current room and occupancy info"""
    result = frappe.db.sql("""
        SELECT 
            si.student_code,
            si.first_name,
            si.last_name,
            si.parent AS current_room,
            hr.hostel_type,
            hr.capacity,
            (SELECT COUNT(*) 
             FROM `tabStudent List Item`
             WHERE parent = si.parent) AS current_occupancy
        FROM `tabStudent List Item` si
        LEFT JOIN `tabHostel Room` hr ON si.parent = hr.name
        WHERE si.student_code = %s
        LIMIT 1
    """, (student_code,), as_dict=True)

    return result[0] if result else {}


@frappe.whitelist()
def get_change_request_room(student_code):
    """Get student's current room, occupancy info, and hostel type"""
    res = frappe.db.sql("""
        SELECT 
            si.student_code,
            si.parent AS room,
            hr.hostel_type AS type, 
            (SELECT COUNT(*) 
             FROM `tabStudent List Item`
             WHERE parent = si.parent) AS occupancy
        FROM `tabStudent List Item` si
        JOIN `tabHostel Room` hr ON si.parent = hr.name
        WHERE si.student_code = %s
        LIMIT 1
    """, (student_code,), as_dict=True)

    return res[0] if res else {}
