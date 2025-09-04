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
    

    def validate(self):
        """
        Validate if the room change is possible based on capacity and operation type
        """
        
        if self.requested_room and not self.room:
            self.operation_type = "move"
            self.validate_room_capacity()
        elif self.room and not self.requested_room:
            self.operation_type = "swap"
            self.validate_room_swap()
        else:
            frappe.throw(_("Please specify either a requested room (for move) or a swap room (for swap)"))
        
    def validate_room_swap(self):
        """Validate if the room swap is possible"""
        if self.current_room == self.room:
            frappe.throw(_("Cannot swap with the same room. Please select a different room."))
        
        room = frappe.get_doc("Hostel Room", self.room)
        if not room.student_list or len(room.student_list) == 0:
            frappe.throw(_(f"Room {self.room} has no students to swap with"))
    
    def validate_room_capacity(self):
        """
        Check if requested room has capacity (less than 3 students)
        """
        
        requested_room_doc = frappe.get_doc("Hostel Room", self.requested_room)
        current_student_count = len(requested_room_doc.get("student_list", []))
        
        if current_student_count >= 3:
            frappe.throw(_("Requested room {0} is already at full capacity (3 students). Cannot proceed with room change.").format(self.requested_room))

    def on_submit(self):
        """When submitted, either move or swap student based on operation type"""
        if self.operation_type == "move":
            self.move_student()
        elif self.operation_type == "swap":
            self.swep_student()
        else:
            frappe.throw(_("Invalid operation type. Please specify either move or swap operation."))

    def move_student(self):
        try:
            
            current_room = frappe.get_doc("Hostel Room", self.current_room)
            current_room.set("student_list", [
                s for s in current_room.student_list
                if s.student_code != self.applied_by
            ])
            current_room.save()
            
            
            new_room = frappe.get_doc("Hostel Room", self.requested_room)
            new_room.append("student_list", {
                "student_code": self.applied_by,
                "first_name": self.first_name,
                "last_name": self.last_name
            })
            new_room.save()
            
            
            self.db_set("current_room", self.requested_room)

            frappe.msgprint(_(f"Student moved from {self.current_room} → {self.requested_room}"))

        except Exception as e:
            frappe.throw(_(f"Error while moving student: {str(e)}"))
    
    def swep_student(self):
        """Strictly swap students between two rooms (G-1 <-> H-1)"""
        try:
            
            current_room_doc = frappe.get_doc("Hostel Room", self.current_room)
            requested_room_doc = frappe.get_doc("Hostel Room", self.room)

            student_x = next((s for s in current_room_doc.student_list if s.student_code == self.applied_by), None)
            student_y = next((s for s in requested_room_doc.student_list if s.student_code == self.student_code), None)

            if not student_x:
                frappe.throw(_(f"Student {self.applied_by} not found in {self.current_room}"))
            if not student_y:
                frappe.throw(_(f"Student {self.student_code} not found in {self.room}"))

            
            current_room_doc.set("student_list", [
                s for s in current_room_doc.student_list if s.student_code != student_x.student_code
            ])
            requested_room_doc.set("student_list", [
                s for s in requested_room_doc.student_list if s.student_code != student_y.student_code
            ])

            requested_room_doc.append("student_list", {
                "student_code": student_x.student_code,
                "student_name": student_x.student_name,
                "year": student_x.year
            })
            current_room_doc.append("student_list", {
                "student_code": student_y.student_code,
                "student_name": student_y.student_name,
                "year": student_y.year
            })

            current_room_doc.save(ignore_permissions=True)
            requested_room_doc.save(ignore_permissions=True)

            frappe.msgprint(_(
                f"Swapped {student_x.student_name} (from {self.current_room}) "
                f"with {student_y.student_name} (from {self.room})"
            ))

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Hostel Room Swap Error")
            frappe.throw(_(f"Error while swapping students: {str(e)}"))


@frappe.whitelist()
def get_hostel_change_details(student_code):
    """Get student's current room and its occupancy info"""
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

    if result: 
        return result[0]
    else:  
        return {}

    
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

@frappe.whitelist()
def get_room_capacity(room_code):
    """Get capacity and occupancy for a given room"""
    try:
        room = frappe.get_doc("Hostel Room", room_code)
        occupied = len(room.get("student_list"))
        return {
            "room_code": room.name,
            "capacity": room.capacity,
            "current_occupancy": occupied,
            "available_slots": room.capacity - occupied,
            "can_accommodate": occupied < room.capacity
        }
    except frappe.DoesNotExistError:
        return {"error": f"Room {room_code} does not exist"}