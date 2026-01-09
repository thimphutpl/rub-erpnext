# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class HostelAttendance(Document):
# 	# begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.hostel_management.doctype.hostel_attendance_details.hostel_attendance_details import HostelAttendanceDetails
# 		from frappe.types import DF

# 		amended_from: DF.Link | None
# 		company: DF.Link
# 		fiscal_year: DF.Link
# 		hostel_block: DF.Link
# 		posting_date: DF.Date
# 		table_tulk: DF.Table[HostelAttendanceDetails]
# 	# end: auto-generated types
# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.hostel_management.doctype.hostel_attendance_details.hostel_attendance_details import HostelAttendanceDetails
# 		from frappe.types import DF

# 		amended_from: DF.Link | None
# 		company: DF.Link
# 		hostel_block: DF.Link
# 		posting_date: DF.Date
# 		table_tulk: DF.Table[HostelAttendanceDetails]
# 	pass


# @frappe.whitelist()
# def get_hostel_attendance(company, hostel_block):
# 	if not company or not hostel_block:
# 		return []

# 	rooms = frappe.get_all(
# 		"Hostel Counsellor",
# 		filters={"company": company, "hostel_block": hostel_block},
# 		fields=["name"],
# 	)

# 	results = []

# 	for r in rooms:
# 		block_details = frappe.get_all(
# 			"Block Counsellor Details",
# 			filters={"parent": r.name, "parenttype": "Hostel Counsellor"},
# 			fields=[
# 				"room_number",
# 				"student_code",
# 				"first_name",
# 				"last_name",
# 			],
# 		)

# 		for d in block_details:
# 			full_name = ""
# 			if d.first_name and d.last_name:
# 				full_name = f"{d.first_name} {d.last_name}"
# 			elif d.first_name:
# 				full_name = d.first_name
# 			elif d.last_name:
# 				full_name = d.last_name

# 			results.append({
# 				"room_number": d.room_number,
# 				"student_code": d.student_code,
# 				"student_name": full_name,
# 			})

# 	return results



# Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HostelAttendance(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.hostel_management.doctype.hostel_attendance_details.hostel_attendance_details import HostelAttendanceDetails
        from frappe.types import DF

        amended_from: DF.Link | None
        company: DF.Link
        fiscal_year: DF.Link
        hostel_block: DF.Link
        posting_date: DF.Date
        table_tulk: DF.Table[HostelAttendanceDetails]
    # end: auto-generated types
    pass


@frappe.whitelist()
def get_hostel_attendance(company, hostel_block):
    if not company or not hostel_block:
        return []

    rooms = frappe.get_all(
        "Hostel Counsellor",
        filters={"company": company, "hostel_block": hostel_block},
        fields=["name"],
    )

    results = []

    for r in rooms:
        block_details = frappe.get_all(
            "Block Counsellor Details",
            filters={"parent": r.name, "parenttype": "Hostel Counsellor"},
            fields=["room_number", "student_code", "first_name", "last_name"],
        )

        for d in block_details:

            # 🔥 Skip rows that have no data (prevents empty first row)
            if not (d.room_number or d.student_code or d.first_name or d.last_name):
                continue

            # Build full name
            if d.first_name and d.last_name:
                full_name = f"{d.first_name} {d.last_name}"
            elif d.first_name:
                full_name = d.first_name
            elif d.last_name:
                full_name = d.last_name
            else:
                full_name = ""

            results.append({
                "room_number": d.room_number,
                "student_code": d.student_code,
                "student_name": full_name,
            })

    return results

