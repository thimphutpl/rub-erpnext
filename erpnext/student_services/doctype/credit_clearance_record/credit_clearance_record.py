import frappe
from frappe.model.document import Document
from frappe.utils import (
    add_days,
    ceil,
    cint,
    cstr,
    date_diff,
    floor,
    flt,
    formatdate,
    get_first_day,
    get_last_day,
    get_link_to_form,
    getdate,
    money_in_words,
    rounded,
    nowdate,
    now_datetime
)
from frappe import _

class CreditClearanceRecord(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.student_services.doctype.credit_clearance_details.credit_clearance_details import CreditClearanceDetails
        from frappe.types import DF

        amended_from: DF.Link | None
        college: DF.Link
        credit_type: DF.Link
        posting_date: DF.Date
        student_details: DF.Table[CreditClearanceDetails]
        student_record_ref: DF.Link
    # end: auto-generated types

    def validate(self):
        """Validate the document before saving"""
        try:
            self.validate_required_fields()
            self.validate_duplicates()
            self.validate_amounts()
        except Exception as e:
            frappe.log_error(
                title="Credit Clearance Validation Error",
                message=f"Error in validate method: {str(e)}\n{frappe.get_traceback()}"
            )
            frappe.throw(_("Validation failed: {0}").format(str(e)))

    def on_submit(self):
        """Actions to perform on submit"""
        try:
            self.check_all_paid()
            self.update_student_credit_status()
        except Exception as e:
            frappe.log_error(
                title="Credit Clearance Submit Error",
                message=f"Error in on_submit method: {str(e)}\n{frappe.get_traceback()}"
            )
            frappe.throw(_("Failed to submit: {0}").format(str(e)))

    def on_cancel(self):
        """Actions to perform on cancel"""
        try:
            self.revert_student_credit_status()
        except Exception as e:
            frappe.log_error(
                title="Credit Clearance Cancel Error",
                message=f"Error in on_cancel method: {str(e)}\n{frappe.get_traceback()}"
            )
            frappe.throw(_("Failed to cancel: {0}").format(str(e)))

    def validate_required_fields(self):
        """Validate that required fields are filled"""
        try:
            if not self.college:
                frappe.throw(_("College is required."))
            
            if not self.credit_type:
                frappe.throw(_("Credit Type is required."))
            
            if not self.posting_date:
                self.posting_date = nowdate()

            if not self.student_details:
                frappe.throw(_("At least one student must be added to the clearance record."))
        except Exception as e:
            frappe.log_error(
                title="Required Fields Validation Error",
                message=f"Error in validate_required_fields: {str(e)}\n{frappe.get_traceback()}"
            )
            raise

    def validate_duplicates(self):
        """Check for duplicate student entries within the table"""
        try:
            seen = set()
            duplicate_students = []
            
            for row in self.student_details:
                if not row.student_code:
                    continue
                    
                if row.student_code in seen:
                    duplicate_students.append(row.student_code)
                else:
                    seen.add(row.student_code)
            
            if duplicate_students:
                duplicate_list = ", ".join(duplicate_students)
                frappe.throw(
                    _("Duplicate student entries found for: {0}. Please remove duplicates before saving.").format(duplicate_list),
                    title=_("Duplicate Students")
                )
        except Exception as e:
            frappe.log_error(
                title="Duplicate Validation Error",
                message=f"Error in validate_duplicates: {str(e)}\n{frappe.get_traceback()}"
            )
            raise

    def validate_amounts(self):
        """Validate that amounts are positive"""
        try:
            for row in self.student_details:
                if flt(row.amount) < 0:
                    frappe.throw(
                        _("Amount for student {0} - {1} cannot be negative.").format(row.student_code, row.full_name),
                        title=_("Invalid Amount")
                    )
        except Exception as e:
            frappe.log_error(
                title="Amount Validation Error",
                message=f"Error in validate_amounts: {str(e)}\n{frappe.get_traceback()}"
            )
            raise

    def check_all_paid(self):
        """Check if all students have paid status"""
        try:
            unpaid_students = []
            
            for child in self.student_details:
                if child.status != 'Paid':
                    unpaid_students.append(f"{child.student_code} - {child.full_name}")
            
            if unpaid_students:
                student_list = "\n".join(unpaid_students)
                frappe.throw(
                    _("All students must have 'Paid' status before submission.\nThe following students are not paid:\n{0}").format(student_list),
                    title=_("Payment Required")
                )
        except Exception as e:
            frappe.log_error(
                title="Payment Check Error",
                message=f"Error in check_all_paid: {str(e)}\n{frappe.get_traceback()}"
            )
            raise

    def update_student_credit_status(self):
        """Update student credit status after clearance"""
        try:
            updated_count = 0
            error_count = 0
            
            for child in self.student_details:
                try:
                    # Check if there's a student credit document to update
                    student_credit = frappe.db.exists("Student Credit", {
                        "student_code": child.student_code,
                        "credit_type": self.credit_type,
                        "docstatus": 1
                    })
                    
                    if student_credit:
                        # Update existing student credit record
                        credit_doc = frappe.get_doc("Student Credit", student_credit)
                        credit_doc.db_set("clearance_status", "Cleared")
                        credit_doc.db_set("clearance_date", self.posting_date)
                        credit_doc.db_set("clearance_reference", self.name)
                        
                        updated_count += 1
                        
                except Exception as e:
                    error_count += 1
                    frappe.log_error(
                        title="Student Credit Update Error",
                        message=f"Failed to update student {child.student_code}: {str(e)}\n{frappe.get_traceback()}"
                    )
            
            if updated_count > 0:
                frappe.msgprint(
                    _("Successfully updated credit status for {0} student(s).").format(updated_count),
                    alert=True,
                    indicator="green"
                )
            
            if error_count > 0:
                frappe.msgprint(
                    _("Failed to update {0} student(s). Check error logs for details.").format(error_count),
                    alert=True,
                    indicator="red"
                )
                
        except Exception as e:
            frappe.log_error(
                title="Credit Status Update Error",
                message=f"Error in update_student_credit_status: {str(e)}\n{frappe.get_traceback()}"
            )
            raise

    def revert_student_credit_status(self):
        """Revert student credit status on cancellation"""
        try:
            reverted_count = 0
            error_count = 0
            
            for child in self.student_details:
                try:
                    student_credit = frappe.db.exists("Student Credit", {
                        "student_code": child.student_code,
                        "credit_type": self.credit_type,
                        "clearance_reference": self.name,
                        "docstatus": 1
                    })
                    
                    if student_credit:
                        credit_doc = frappe.get_doc("Student Credit", student_credit)
                        credit_doc.db_set("clearance_status", "Pending")
                        credit_doc.db_set("clearance_date", None)
                        credit_doc.db_set("clearance_reference", None)
                        
                        reverted_count += 1
                        
                except Exception as e:
                    error_count += 1
                    frappe.log_error(
                        title="Student Credit Revert Error",
                        message=f"Failed to revert student {child.student_code}: {str(e)}\n{frappe.get_traceback()}"
                    )
            
            if reverted_count > 0:
                frappe.msgprint(
                    _("Successfully reverted credit status for {0} student(s).").format(reverted_count),
                    alert=True,
                    indicator="orange"
                )
            
            if error_count > 0:
                frappe.msgprint(
                    _("Failed to revert {0} student(s). Check error logs for details.").format(error_count),
                    alert=True,
                    indicator="red"
                )
                
        except Exception as e:
            frappe.log_error(
                title="Credit Status Revert Error",
                message=f"Error in revert_student_credit_status: {str(e)}\n{frappe.get_traceback()}"
            )
            raise

    @frappe.whitelist()
    def get_students(self):
        """Fetch students from reference document with validation"""
        try:
            # Validate required fields
            if not self.student_record_ref:
                frappe.throw(_("Please select a Student Record Reference first."))
            
            if not self.credit_type:
                frappe.throw(_("Please select a Credit Type first."))
            
            # Check if reference document exists and is submitted
            if not frappe.db.exists("Student Credit Record", self.student_record_ref):
                frappe.throw(_("Student Record Reference {0} does not exist.").format(self.student_record_ref))
            
            ref_doc = frappe.get_doc("Student Credit Record", self.student_record_ref)
            if ref_doc.docstatus != 1:
                frappe.throw(_("Student Record Reference must be submitted before fetching students."))
            
            # Get existing student codes to check for duplicates
            existing_students = {d.student_code for d in self.student_details if d.student_code}
            
            # Fetch students from the reference document
            students = frappe.db.sql("""
                SELECT 
                    student_code, 
                    full_name, 
                    programme, 
                    semester,
                    year,
                    amount 
                FROM `tabStudent Credit Details` 
                WHERE parent = %s
                ORDER BY student_code
            """, self.student_record_ref, as_dict=1)
            
            if not students:
                frappe.msgprint(
                    _("No students found in the selected reference document."),
                    alert=True,
                    indicator="yellow"
                )
                return
            
            added_count = 0
            skipped_count = 0
            skipped_students = []
            
            for std in students:
                # Skip if no student code
                if not std.student_code:
                    continue
                
                # Check if student code exists in current table
                if std.student_code in existing_students:
                    skipped_count += 1
                    skipped_students.append(f"{std.student_code} - {std.full_name} (_('already in table'))")
                    continue
                
                # Check if student already has a credit clearance record for this credit type
                clearance_check = self.check_existing_clearance(std.student_code)
                if clearance_check["exists"]:
                    skipped_count += 1
                    skipped_students.append(
                        f"{std.student_code} - {std.full_name} "
                        f"(_('already cleared in')) {clearance_check['reference']}"
                    )
                    continue
                
                # Add the student
                self.append("student_details", {
                    "student_code": std.student_code,
                    "full_name": std.full_name,
                    "programme": std.programme,
                    "semester": std.semester,
                    "year": std.year,
                    "amount": std.amount,
                    "status": "Unpaid"  # Default status
                })
                
                # Add to existing set to prevent duplicates within same append operation
                existing_students.add(std.student_code)
                added_count += 1
            
            # Show summary message
            if added_count > 0:
                frappe.msgprint(
                    _("✅ Successfully added {0} student(s).").format(added_count),
                    alert=True,
                    indicator="green"
                )
            
            if skipped_count > 0:
                message = _("⚠️ Skipped {0} student(s):\n").format(skipped_count)
                message += "\n".join(skipped_students[:5])  # Show first 5
                if len(skipped_students) > 5:
                    message += _("\n... and {0} more").format(len(skipped_students) - 5)
                
                frappe.msgprint(
                    message,
                    title=_("Skipped Students"),
                    indicator="orange",
                    wide=True
                )
                
        except Exception as e:
            frappe.log_error(
                title="Get Students Error",
                message=f"Error in get_students: {str(e)}\n{frappe.get_traceback()}"
            )
            frappe.throw(_("Failed to fetch students: {0}").format(str(e)))

    def check_existing_clearance(self, student_code):
        """Check if student already has a credit clearance record for this credit type"""
        try:
            result = {
                "exists": False,
                "reference": None,
                "status": None,
                "date": None
            }
            
            # Check in submitted documents
            existing = frappe.db.sql("""
                SELECT 
                    ccr.name,
                    ccr.docstatus,
                    ccr.posting_date
                FROM `tabCredit Clearance Record` ccr
                INNER JOIN `tabCredit Clearance Details` ccd 
                    ON ccd.parent = ccr.name
                WHERE 
                    ccr.credit_type = %s
                    AND ccr.docstatus = 1
                    AND ccd.student_code = %s
                    AND ccr.name != %s
                ORDER BY ccr.posting_date DESC
                LIMIT 1
            """, (self.credit_type, student_code, self.name or "None"), as_dict=1)
            
            if existing:
                result["exists"] = True
                result["reference"] = existing[0].name
                result["status"] = "submitted"
                result["date"] = existing[0].posting_date
                return result
            
            # Check in draft documents (excluding current)
            existing_draft = frappe.db.sql("""
                SELECT 
                    ccr.name,
                    ccr.docstatus
                FROM `tabCredit Clearance Record` ccr
                INNER JOIN `tabCredit Clearance Details` ccd 
                    ON ccd.parent = ccr.name
                WHERE 
                    ccr.credit_type = %s
                    AND ccr.docstatus = 0
                    AND ccd.student_code = %s
                    AND ccr.name != %s
                LIMIT 1
            """, (self.credit_type, student_code, self.name or "None"), as_dict=1)
            
            if existing_draft:
                result["exists"] = True
                result["reference"] = existing_draft[0].name
                result["status"] = "draft"
            
            return result
            
        except Exception as e:
            frappe.log_error(
                title="Clearance Check Error",
                message=f"Error in check_existing_clearance for student {student_code}: {str(e)}\n{frappe.get_traceback()}"
            )
            return {"exists": False, "error": str(e)}  # Return safe default on error

    @frappe.whitelist()
    def clear_students(self):
        """Clear all student details"""
        try:
            if self.student_details:
                self.student_details = []
                frappe.msgprint(
                    _("✅ All student details cleared."),
                    alert=True,
                    indicator="blue"
                )
            else:
                frappe.msgprint(
                    _("No student details to clear."),
                    alert=True,
                    indicator="yellow"
                )
        except Exception as e:
            frappe.log_error(
                title="Clear Students Error",
                message=f"Error in clear_students: {str(e)}\n{frappe.get_traceback()}"
            )
            frappe.throw(_("Failed to clear students: {0}").format(str(e)))

    @frappe.whitelist()
    def get_student_summary(self):
        """Get summary of student details"""
        try:
            total_students = len(self.student_details)
            total_amount = sum(flt(d.amount) for d in self.student_details)
            paid_count = sum(1 for d in self.student_details if d.status == 'Paid')
            unpaid_count = total_students - paid_count
            
            return {
                "total_students": total_students,
                "total_amount": total_amount,
                "paid_count": paid_count,
                "unpaid_count": unpaid_count,
                "paid_amount": sum(flt(d.amount) for d in self.student_details if d.status == 'Paid'),
                "unpaid_amount": sum(flt(d.amount) for d in self.student_details if d.status == 'Unpaid')
            }
        except Exception as e:
            frappe.log_error(
                title="Student Summary Error",
                message=f"Error in get_student_summary: {str(e)}\n{frappe.get_traceback()}"
            )
            return {
                "error": str(e),
                "total_students": 0,
                "total_amount": 0,
                "paid_count": 0,
                "unpaid_count": 0,
                "paid_amount": 0,
                "unpaid_amount": 0
            }


@frappe.whitelist()
def get_credit_clearance(dt, dn):
    """Create a new Credit Clearance Record from a Student Credit Record"""
    try:
        # Validate input
        if not dt or not dn:
            frappe.throw(_("Document type and name are required."))
        
        # Get the source document
        doc = frappe.get_doc(dt, dn)
        
        # Validate source document
        if doc.doctype != "Student Credit Record":
            frappe.throw(_("Source document must be a Student Credit Record."))
        
        if doc.docstatus != 1:
            frappe.throw(_("Cannot create clearance from an unsubmitted Student Credit Record."))
        
        # Check if clearance already exists
        existing_clearance = frappe.db.exists("Credit Clearance Record", {
            "student_record_ref": dn,
            "docstatus": ["!=", 2]  # Not cancelled
        })
        
        if existing_clearance:
            frappe.throw(
                _("A clearance record already exists for this reference: {0}").format(
                    get_link_to_form('Credit Clearance Record', existing_clearance)
                )
            )
        
        # Create new clearance record
        cc = frappe.new_doc("Credit Clearance Record")
        cc.posting_date = nowdate()
        cc.college = doc.company
        cc.credit_type = doc.credit_type
        cc.student_record_ref = doc.name
        
        # Copy student details
        student_count = 0
        for d in doc.get("student_details"):
            item = d.as_dict()
            
            # Check if student already has clearance
            clearance_check = check_student_clearance_status(
                item["student_code"], 
                doc.credit_type
            )
            
            if clearance_check.get("has_clearance"):
                frappe.msgprint(
                    _("Student {0} - {1} already has clearance in {2}. Skipped.").format(
                        item['student_code'], item['full_name'], clearance_check['reference']
                    ),
                    alert=True,
                    indicator="orange"
                )
                continue
            
            cc.append("student_details", {
                "student_code": item["student_code"],
                "full_name": item["full_name"],
                "programme": item["programme"],
                "semester": item["semester"],
                "year": item["year"],
                "amount": item["amount"],
                "status": "Unpaid"
            })
            student_count += 1
        
        if student_count == 0:
            frappe.msgprint(
                _("No new students to add. All students already have clearance records."),
                alert=True,
                indicator="yellow"
            )
        
        return cc.as_dict()
        
    except Exception as e:
        frappe.log_error(
            title="Get Credit Clearance Error",
            message=f"Error in get_credit_clearance for {dt}-{dn}: {str(e)}\n{frappe.get_traceback()}"
        )
        frappe.throw(_("Failed to create credit clearance: {0}").format(str(e)))


@frappe.whitelist()
def check_student_clearance_status(student_code, credit_type):
    """Check if a student already has clearance for a credit type"""
    try:
        result = {
            "has_clearance": False,
            "reference": None,
            "status": None,
            "date": None
        }
        
        if not student_code or not credit_type:
            return result
        
        # Check in submitted documents
        existing = frappe.db.sql("""
            SELECT 
                ccr.name,
                ccr.posting_date
            FROM `tabCredit Clearance Record` ccr
            INNER JOIN `tabCredit Clearance Details` ccd 
                ON ccd.parent = ccr.name
            WHERE 
                ccr.credit_type = %s
                AND ccr.docstatus = 1
                AND ccd.student_code = %s
            ORDER BY ccr.posting_date DESC
            LIMIT 1
        """, (credit_type, student_code), as_dict=1)
        
        if existing:
            result["has_clearance"] = True
            result["reference"] = existing[0].name
            result["status"] = "Cleared"
            result["date"] = existing[0].posting_date
        
        return result
        
    except Exception as e:
        frappe.log_error(
            title="Check Clearance Status Error",
            message=f"Error checking clearance for student {student_code}: {str(e)}\n{frappe.get_traceback()}"
        )
        return {"has_clearance": False, "error": str(e)}


@frappe.whitelist()
def get_pending_clearance_students(credit_type=None, college=None):
    """Get students pending clearance for a credit type"""
    try:
        conditions = []
        values = []
        
        if credit_type:
            conditions.append("ccr.credit_type = %s")
            values.append(credit_type)
        
        if college:
            conditions.append("ccr.college = %s")
            values.append(college)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Get students with pending clearance
        pending_students = frappe.db.sql("""
            SELECT 
                ccd.student_code,
                ccd.full_name,
                ccd.programme,
                ccd.semester,
                ccd.year,
                ccd.amount,
                ccr.name as clearance_ref,
                ccr.posting_date
            FROM `tabCredit Clearance Details` ccd
            INNER JOIN `tabCredit Clearance Record` ccr 
                ON ccr.name = ccd.parent
            WHERE 
                ccr.docstatus = 0  /* Draft documents */
                AND {where_clause}
            ORDER BY ccr.posting_date DESC, ccd.student_code
        """.format(where_clause=where_clause), values, as_dict=1)
        
        return pending_students
        
    except Exception as e:
        frappe.log_error(
            title="Get Pending Clearance Error",
            message=f"Error getting pending clearance students: {str(e)}\n{frappe.get_traceback()}"
        )
        return []  # Return empty list on error