# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    # Define columns for the report
    columns = [
        {
            "fieldname": "club_name",
            "label": _("Club Name"),
            "fieldtype": "Link",
            "options": "Club",
            "width": 200
        },
        {
            "fieldname": "minimum_year_required",
            "label": _("Minimum Years Required"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "college",
            "label": _("College"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "student_name",
            "label": _("Student Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "student_code",
            "label": _("Student Code"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "years_difference",
            "label": _("Years Since Posting"),
            "fieldtype": "Int",
            "width": 150
        }
    ]
    
    # Check if club filter is provided
    if not filters or not filters.get("club"):
        # Return empty data with a message
        frappe.msgprint(_("Please select a Club to view the report."))
        return columns, []
    
    # Build the SQL query
    query = """
        SELECT 
            c.name as club_name,
            c.minimum_year_required_for_certification as minimum_year_required,
            ca.college,
            CONCAT(ca.first_name, " ", ca.last_name) as student_name,
            ca.student_code,
            ca.posting_date,
            TIMESTAMPDIFF(YEAR, ca.posting_date, CURDATE()) AS years_difference
        FROM 
            `tabClub Membership Application` ca 
        INNER JOIN 
            `tabClub` c ON ca.applying_for_club = c.name 
        WHERE 
            c.name = %(club)s
            AND c.minimum_year_required_for_certification IS NOT NULL 
            AND ca.docstatus = 1 
            AND TIMESTAMPDIFF(YEAR, ca.posting_date, CURDATE()) > c.minimum_year_required_for_certification
    """
    
    # Apply additional filters if provided
    conditions = []
    values = {"club": filters.get("club")}
    
    # College filter
    if filters.get("college"):
        conditions.append("ca.college = %(college)s")
        values["college"] = filters.get("college")
    
    # From Date filter
    if filters.get("from_date"):
        conditions.append("ca.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    
    # To Date filter
    if filters.get("to_date"):
        conditions.append("ca.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    
    # Add conditions to query
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    # Add order by clause
    query += ' ORDER BY ca.posting_date DESC'
    
    # Execute the query
    data = frappe.db.sql(query, values, as_dict=1)
    
    # Optional: Show message if no data found
    if not data:
        frappe.msgprint(_("No eligible members found for the selected club."))
    
    return columns, data