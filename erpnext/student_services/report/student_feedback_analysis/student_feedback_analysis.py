# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """Main method to execute the report"""
    
    # Define columns
    columns = [
        {
            "fieldname": "feedback_type",
            "label": _("Feedback Type"),
            "fieldtype": "Link",
            "options": "Feedback Type",
            "width": 150
        },
        {
            "fieldname": "college",
            "label": _("College"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 200
        },
        {
            "fieldname": "question",
            "label": _("Question"),
            "fieldtype": "Data",
            "width": 400
        },
        {
            "fieldname": "student_count",
            "label": _("Number of Students"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "average_rating",
            "label": _("Average Rating"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 150
        },
        {
            "fieldname": "total_responses",
            "label": _("Total Responses"),
            "fieldtype": "Int",
            "width": 150
        }
    ]
    
    # Build conditions based on filters
    conditions = "1=1"
    
    if filters:
        if filters.get("feedback_type"):
            conditions += f" AND sf.feedback_type = '{filters.get('feedback_type')}'"
        
        if filters.get("college"):
            conditions += f" AND sf.college = '{filters.get('college')}'"
    
    # SQL query - Count unique students per question
    query = f"""
        SELECT 
            sf.feedback_type,
            sf.college,
            r.question,
            COUNT(DISTINCT sf.student) AS student_count,
            AVG(r.rating) AS average_rating,
            COUNT(r.rating) AS total_responses
        FROM 
            `tabStudent Feedback` sf
        INNER JOIN 
            `tabRating Responses` r ON sf.name = r.parent
        WHERE 
            {conditions}
        GROUP BY 
            sf.feedback_type,
            sf.college, 
            r.question
        ORDER BY 
            sf.feedback_type ASC,
            student_count DESC
    """
    
    data = frappe.db.sql(query, as_dict=1)
    
    # Prepare chart data for single chart
    chart = get_chart_data(data)
    
    # Return with chart
    return columns, data, None, chart

def get_chart_data(data):
    """Prepare chart data for visualization"""
    
    if not data:
        return None
    
    # Chart 1: Student Count by Question (Top 10)
    sorted_by_students = sorted(data, key=lambda x: x.get('student_count', 0), reverse=True)
    top_questions = sorted_by_students[:10]
    
    # Prepare labels and values for chart
    labels = []
    values = []
    
    for d in top_questions:
        # Truncate long question text
        question_text = d.get('question', '')
        if len(question_text) > 40:
            question_text = question_text[:37] + '...'
        labels.append(question_text)
        values.append(d.get('student_count', 0))
    
    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Number of Students"),
                    "values": values
                }
            ]
        },
        "type": "bar",
        "title": _("Top 10 Questions by Student Participation"),
        "height": 300,
        "colors": ["#4CAF50"]
    }
    
    return chart