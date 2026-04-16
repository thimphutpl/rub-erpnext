import frappe
import json
from frappe import _

@frappe.whitelist()
def get_feedback_type():
    feedback_type = frappe.db.sql(""" 
        SELECT name 
        FROM `tabFeedback Type` 
        ORDER BY name
    """, as_dict=1)
    return feedback_type

@frappe.whitelist()
def get_feedback_data(feedback_type, student):
    
    
    academic_year=frappe.db.sql("""SELECT name  FROM `tabAcademic Year`  WHERE CURDATE() BETWEEN year_start_date AND year_end_date and Month(year_start_date) <> 01 limit 1 """,as_dict=1)
    for aca in academic_year:
        year=aca.name
    #frappe.throw(str(year))
    
    result = {
        'rating_questions': [],
        'oeq_questions': [],
        'existing_feedback': None,
        'has_questions': False
    }
    college=get_student_college(student)
    doc=frappe.get_doc("Company",college)
    if doc.enable==0:
        result['has_questions'] = False
        return result

    
    question_exists = frappe.db.sql("""
        SELECT name 
        FROM `tabFeedback Question` 
        WHERE feedback_type = %s
    """, feedback_type, as_dict=1)
    
    if not question_exists:
        result['has_questions'] = False
        return result
    
    result['has_questions'] = True
    
    rating_query = """
        SELECT mcq.question
        FROM `tabFeedback Question` fb 
        INNER JOIN `tabFeedback MCQ` mcq ON fb.name = mcq.parent 
        WHERE fb.feedback_type = %s and mcq.status='Enable'
    """
    result['rating_questions'] = frappe.db.sql(rating_query, feedback_type, as_dict=1)
    
    oeq_query = """
        SELECT oeq.question 
        FROM `tabFeedback Question` fb 
        INNER JOIN `tabFeedback OEQ` oeq ON fb.name = oeq.parent 
        WHERE fb.feedback_type = %s and oeq.status='Enable'
    """
    result['oeq_questions'] = frappe.db.sql(oeq_query, feedback_type, as_dict=1)
    
    existing = frappe.db.get_value(
        "Student Feedback", 
        {"feedback_type": feedback_type, "student": student,"academic_year":year},
        ["name", "creation"],
        as_dict=True
    )
    
    if existing and existing.get('name'):
        
        feedback_doc = frappe.get_doc("Student Feedback", existing['name'])
        
        rating_responses = []
        for row in feedback_doc.rating_responses:
            rating_responses.append({
                "question": row.question,
                "rating": row.rating
            })
        
        oeq_responses = []
        for row in feedback_doc.oeq_responses:
            oeq_responses.append({
                "question": row.question,
                "response_text": row.response_text
            })
        
        result['existing_feedback'] = {
            "name": feedback_doc.name,
            "creation": str(feedback_doc.creation),
            "rating_responses": rating_responses,
            "oeq_responses": oeq_responses
        }
    
    return result

@frappe.whitelist()
def submit_feedback_responses(feedback_type, rating_answers, oeq_answers, student):
    try:
        college=""
        #frappe.throw("hiii")
        academic_year=frappe.db.sql("""SELECT name  FROM `tabAcademic Year`  WHERE CURDATE() BETWEEN year_start_date AND year_end_date and Month(year_start_date) <> 01 limit 1 """,as_dict=1)
        college=get_student_college(student)
        
            
        for aca in academic_year:
            year=aca.name
        if isinstance(rating_answers, str):
            rating_answers = json.loads(rating_answers)
        if isinstance(oeq_answers, str):
            oeq_answers = json.loads(oeq_answers)
        
        existing = frappe.db.exists("Student Feedback", {
            "feedback_type": feedback_type,
            "student": student,
            "academic_year":year,
            "college":college


        })
        
        if existing:
            return {'success': False, 'error': 'You have already submitted feedback for this type.'}
        
        feedback = frappe.get_doc({
            'doctype': 'Student Feedback',
            'feedback_type': feedback_type,
            'student': student,
            "academic_year":year,
            "college":college,
            'date': frappe.utils.nowdate()
        })
        
        for answer in rating_answers:
            feedback.append('rating_responses', {
                'question': answer.get('question'),
                'rating': answer.get('rating')
            })
        
        for answer in oeq_answers:
            feedback.append('oeq_responses', {
                'question': answer.get('question'),
                'response_text': answer.get('answer')
            })
        
        feedback.insert()
        frappe.db.commit()
        
        return {'success': True, 'name': feedback.name}
        
    except Exception as e:
        frappe.db.rollback()
        return {'success': False, 'error': str(e)} 

@frappe.whitelist()  
def get_student_college(user):
    #frappe.throw(str(user))
    
   
    student=frappe.db.sql("""select company from `tabStudent` where user=%s """,user,as_dict=1)
    if not student:
        college='Royal University of Bhutan'
    for std in student:
        college=std.company

    return college