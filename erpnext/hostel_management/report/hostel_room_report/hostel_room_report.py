# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd.
# # For license information, please see license.txt

# import frappe


# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = [
#         {"label": "College", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
#         {"label": "Hostel Type", "fieldname": "hostel_type", "fieldtype": "Link", "options": "Hostel Type", "width": 140},
#         {"label": "Room Number", "fieldname": "name", "fieldtype": "Data", "width": 120},
#         {"label": "Capacity", "fieldname": "capacity", "fieldtype": "Int", "width": 100},
#         {"label": "Available", "fieldname": "available_left", "fieldtype": "Int", "width": 140},
#         {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Data", "width": 160},
#         {"label": "Room Description", "fieldname": "room_description", "fieldtype": "Text", "width": 200},
#         {"label": "Asset Code", "fieldname": "asset_code", "fieldtype": "Link", "options": "Asset", "width": 140},
#         {"label": "Number of Asset", "fieldname": "number_of_asset", "fieldtype": "Int", "width": 140},
#         {"label": "Student Code", "fieldname": "student_code", "fieldtype": "Link", "options": "Student", "width": 180},
#         {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data", "width": 140},
#         {"label": "Last Name", "fieldname": "last_name", "fieldtype": "Data", "width": 140},
#         {"label": "Year", "fieldname": "year", "fieldtype": "Data", "width": 80},
#     ]

#     conditions = []
#     if filters.get("company"):
#         conditions.append("hr.company = %(company)s")
#     if filters.get("hostel_type"):
#         conditions.append("hr.hostel_type = %(hostel_type)s")
#     if filters.get("name"):
#         conditions.append("hr.name= %(name)s")

#     if filters.get("asset_code"):
#         conditions.append("hai.asset_code = %(asset_code)s")
#     if filters.get("student_code"):
#         conditions.append("sli.student_code = %(student_code)s")

#     where_clause = ""
#     if conditions:
#         where_clause = "WHERE " + " AND ".join(conditions)

#     data = frappe.db.sql(
#         f"""
#         SELECT
#             hr.company,
#             hr.hostel_type,
#             hr.name,
#             hr.room_number,
#             hr.capacity,

#             (hr.capacity - IFNULL(sc.student_count, 0)) AS available_left,

#             hr.cost_center,
#             hr.room_description,
#             hai.asset_code,
#             hai.number_of_asset,
#             sli.student_code,
#             sli.first_name,
#             sli.last_name,
#             sli.year

#         FROM `tabHostel Room` hr
#         LEFT JOIN (
#             SELECT parent, COUNT(*) AS student_count
#             FROM `tabStudent List Item`
#             WHERE docstatus = 0
#             GROUP BY parent
#         ) sc ON sc.parent = hr.name

#         LEFT JOIN `tabHostel Asset Item` hai
#             ON hr.name = hai.parent
#             AND hai.docstatus = 0

#         LEFT JOIN `tabStudent List Item` sli
#             ON hr.name = sli.parent
#             AND sli.docstatus = 0

#         {where_clause}

#         ORDER BY
#             hr.company,
#             hr.room_number,
#             sli.student_code
#         """,
#         filters,
#         as_dict=True,
#     )

#     return columns, data


import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": "College", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
        {"label": "Hostel Type", "fieldname": "hostel_type", "fieldtype": "Link", "options": "Hostel Type", "width": 140},
        {"label": "Room Number", "fieldname": "name", "fieldtype": "Data", "width": 120},
        {"label": "Capacity", "fieldname": "capacity", "fieldtype": "Int", "width": 100},
        {"label": "Available", "fieldname": "available_left", "fieldtype": "Int", "width": 120},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Data", "width": 160},
        {"label": "Room Description", "fieldname": "room_description", "fieldtype": "Text", "width": 200},

        {"label": "Asset Codes", "fieldname": "asset_codes", "fieldtype": "Data", "width": 200},
        {"label": "Total Assets", "fieldname": "total_assets", "fieldtype": "Int", "width": 120},

        {"label": "Student Codes", "fieldname": "student_codes", "fieldtype": "Data", "width": 220},
        {"label": "Students", "fieldname": "student_names", "fieldtype": "Data", "width": 250},
        {"label": "Year", "fieldname": "years", "fieldtype": "Data", "width": 120},
    ]

    conditions = []
    if filters.get("company"):
        conditions.append("hr.company = %(company)s")
    if filters.get("hostel_type"):
        conditions.append("hr.hostel_type = %(hostel_type)s")
    if filters.get("name"):
        conditions.append("hr.name = %(name)s")
    if filters.get("asset_code"):
        conditions.append("hai.asset_code = %(asset_code)s")
    if filters.get("student_code"):
        conditions.append("sli.student_code = %(student_code)s")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            hr.company,
            hr.hostel_type,
            hr.name,
            hr.capacity,
            (hr.capacity - IFNULL(sc.student_count, 0)) AS available_left,
            hr.cost_center,
            hr.room_description,

            GROUP_CONCAT(DISTINCT hai.asset_code SEPARATOR ', ') AS asset_codes,
            SUM(DISTINCT hai.number_of_asset) AS total_assets,

            GROUP_CONCAT(DISTINCT sli.student_code SEPARATOR ', ') AS student_codes,
            GROUP_CONCAT(DISTINCT CONCAT(sli.first_name, ' ', sli.last_name) SEPARATOR ', ') AS student_names,
            GROUP_CONCAT(DISTINCT sli.year SEPARATOR ', ') AS years

        FROM `tabHostel Room` hr

        LEFT JOIN (
            SELECT parent, COUNT(*) AS student_count
            FROM `tabStudent List Item`
            WHERE docstatus = 0
            GROUP BY parent
        ) sc ON sc.parent = hr.name

        LEFT JOIN `tabHostel Asset Item` hai
            ON hr.name = hai.parent AND hai.docstatus = 0

        LEFT JOIN `tabStudent List Item` sli
            ON hr.name = sli.parent AND sli.docstatus = 0

        {where_clause}

        GROUP BY hr.name
        ORDER BY hr.company, hr.name
        """,
        filters,
        as_dict=True,
    )

    return columns, data
