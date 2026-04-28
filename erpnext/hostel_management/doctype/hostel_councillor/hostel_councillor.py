# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document


class HostelCouncillor(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.block_counsellor_details.block_counsellor_details import BlockCounsellorDetails
		from erpnext.hostel_management.doctype.hostel_councilor_student.hostel_councilor_student import HostelCouncilorStudent
		from erpnext.hostel_management.doctype.hostel_room_item.hostel_room_item import HostelRoomItem
		from frappe.types import DF

		academic_year: DF.Link
		amended_from: DF.Link | None
		company: DF.Link
		from_hostel_room: DF.Link | None
		hostel_block: DF.Data
		hostel_councellor: DF.Link | None
		hostel_councilor: DF.Table[HostelCouncilorStudent]
		hostel_room: DF.TableMultiSelect[HostelRoomItem]
		hostel_type: DF.TableMultiSelect[BlockCounsellorDetails]
		table_lbtp: DF.Table[BlockCounsellorDetails]
		to_hostel_room: DF.Link | None
	# end: auto-generated types
	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.block_counsellor_details.block_counsellor_details import BlockCounsellorDetails
		from frappe.types import DF

		company: DF.Link
		hostel_block: DF.Data
		hostel_type: DF.Link
		table_lbtp: DF.Table[BlockCounsellorDetails]
	pass

@frappe.whitelist()
def get_hostel_rooms_with_students(company=None, hostel_types=None, hostel_rooms=None):
    """
    Fetch selected hostel rooms with students based on:
    - multiple hostel types
    - multiple hostel rooms
    """

    if not company or not hostel_types:
        return []

    # Convert string to list
    if isinstance(hostel_types, str):
        hostel_types = [h.strip() for h in hostel_types.split(",") if h.strip()]

    if isinstance(hostel_rooms, str):
        hostel_rooms = [r.strip() for r in hostel_rooms.split(",") if r.strip()]

    filters = {
        "company": company,
        "hostel_type": ["in", hostel_types]
    }

    # Apply room filter only if selected
    if hostel_rooms:
        filters["name"] = ["in", hostel_rooms]

    rooms = frappe.get_all(
        "Hostel Room",
        filters=filters,
        fields=["name", "room_number", "capacity", "hostel_type"],
        order_by="room_number asc"
    )

    results = []

    for room in rooms:
        students = frappe.get_all(
            "Student List Item",
            filters={
                "parent": room.name,
                "parenttype": "Hostel Room"
            },
            fields=["student_code", "first_name", "last_name"]
        )

        if students:
            results.append({
                "room_number": room.name,
                "hostel_capacity": room.capacity,
                "hostel_type": room.hostel_type,
                "students": students
            })

    return results
