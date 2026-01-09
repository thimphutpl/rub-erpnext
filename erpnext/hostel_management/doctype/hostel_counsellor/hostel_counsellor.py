# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HostelCounsellor(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.hostel_management.doctype.block_counsellor_details.block_counsellor_details import BlockCounsellorDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		company: DF.Link
		hostel_block: DF.Data
		hostel_type: DF.TableMultiSelect[BlockCounsellorDetails]
		table_lbtp: DF.Table[BlockCounsellorDetails]
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
def get_hostel_rooms_with_students(company=None, hostel_types=None):
    """
    Fetch all hostel rooms for a given company and multiple hostel types.
    Each room includes its capacity and list of students from the child table.
    """
    if not company or not hostel_types:
        return []

    if isinstance(hostel_types, str):
        hostel_types = [h.strip() for h in hostel_types.split(",") if h.strip()]

    results = []

    for h_type in hostel_types:
        rooms = frappe.get_all(
            "Hostel Room",
            filters={"company": company, "hostel_type": h_type},
            fields=["name", "room_number", "capacity", "hostel_type"],
            order_by="room_number asc"
        )

        for room in rooms:
            students = frappe.get_all(
                "Student List Item",
                filters={"parent": room.name, "parenttype": "Hostel Room"},
                fields=["student_code", "first_name", "last_name"]
            )

            results.append({
                "room_number": room.room_number,
                "hostel_capacity": room.capacity,
                "hostel_type": room.hostel_type,
                "students": students or []
            })

    return results
