import frappe
from datetime import datetime, date

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": "College", "fieldname":"college", "fieldtype":"Link", "options":"Company", "width":180},
        {"label": "Student Code", "fieldname":"student_code", "fieldtype":"Link", "options":"Student", "width":140},
        {"label": "Student Name", "fieldname":"student_name", "fieldtype":"Data", "width":180},
        {"label": "Hostel Block", "fieldname":"hostel_block", "fieldtype":"Data", "width":120},
        {"label": "Room Number", "fieldname":"room_number", "fieldtype":"Data", "width":120},
        {"label": "Hostel Attendance", "fieldname":"attendance", "fieldtype":"Data", "width":120},
        {"label": "Posting Date", "fieldname":"posting_date", "fieldtype":"Date", "width":120},
        {"label": "Leave Type", "fieldname":"leave_type", "fieldtype":"Data", "width":150},
        {"label": "From Date", "fieldname":"from_date", "fieldtype":"Date", "width":120},
        {"label": "To Date", "fieldname":"to_date", "fieldtype":"Date", "width":120},
        {"label": "Total Leave Days", "fieldname":"total_leave_days", "fieldtype":"Float", "width":140},
    ]

    filters_dict = {}
    conditions_ha = ["ha.docstatus = 1", "had.student_code IS NOT NULL", "had.student_code != ''"]

    if filters.get("student_code"):
        conditions_ha.append("had.student_code = %(student_code)s")
        filters_dict["student_code"] = filters.get("student_code")

    if filters.get("college"):
        conditions_ha.append("ha.company = %(college)s")
        filters_dict["college"] = filters.get("college")

    if filters.get("hostel_block"):
        conditions_ha.append("ha.hostel_block = %(hostel_block)s")
        filters_dict["hostel_block"] = filters.get("hostel_block")

    def build_conditions(conditions):
        return "WHERE " + " AND ".join(conditions) if conditions else ""

    where_ha = build_conditions(conditions_ha)

    hostel_attendance = frappe.db.sql(f"""
        SELECT
            had.student_code,
            had.student_name,
            ha.hostel_block,
            had.room_number,
            had.attendance,
            ha.posting_date,
            ha.company AS college
        FROM `tabHostel Attendance` ha
        JOIN `tabHostel Attendance Details` had ON had.parent = ha.name
        {where_ha}
    """, filters_dict, as_dict=True)

    leave_applications = frappe.db.sql("""
        SELECT
            student AS student_code,
            student_name,
            leave_type,
            from_date,
            to_date,
            total_leave_days,
            college
        FROM `tabStudent Leave Application`
        WHERE student IS NOT NULL AND student != ''
    """, as_dict=True)

    leave_lookup = {}
    for la in leave_applications:
        leave_lookup.setdefault(la['student_code'], []).append(la)

    data = []
    for ha in hostel_attendance:
        row = {
            "student_code": ha.get("student_code"),
            "student_name": ha.get("student_name"),
            "hostel_block": ha.get("hostel_block"),
            "room_number": ha.get("room_number"),
            "attendance": ha.get("attendance"),
            "posting_date": ha.get("posting_date"),
            "leave_type": None,
            "from_date": None,
            "to_date": None,
            "total_leave_days": None,
            "college": ha.get("college")
        }

        leaves = leave_lookup.get(ha['student_code'], [])
        for la in leaves:
            posting_date = ha.get("posting_date")
            from_date = la.get("from_date")
            to_date = la.get("to_date")

            if isinstance(posting_date, datetime):
                posting_date = posting_date.date()
            if isinstance(from_date, datetime):
                from_date = from_date.date()
            if isinstance(to_date, datetime):
                to_date = to_date.date()

            if from_date <= posting_date <= to_date:
                row.update({
                    "leave_type": la.get("leave_type"),
                    "from_date": la.get("from_date"),
                    "to_date": la.get("to_date"),
                    "total_leave_days": la.get("total_leave_days"),
                })
                break  

        data.append(row)

    return columns, data






