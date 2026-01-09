# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, cstr, flt, getdate, get_first_day, today, get_last_day
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe import _

class StipendStructure(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.student_services.doctype.stipend_details.stipend_details import StipendDetails
        from frappe.types import DF

        amended_from: DF.Link | None
        company: DF.Data | None
        deductions: DF.Table[StipendDetails]
        earnings: DF.Table[StipendDetails]
        eligible_for_mess_fees: DF.Check
        eligible_for_rent: DF.Check
        full_name: DF.Data | None
        net_amount: DF.Data | None
        programme: DF.Data | None
        semester: DF.Data | None
        student_code: DF.Link
        total_deductions: DF.Currency
        total_earnings: DF.Currency
        year: DF.Data | None
    # end: auto-generated types
    def autoname(self):
        if not self.student_code:
            frappe.throw(_("Student field cannot be empty for autoname generation."))
        self.name = make_autoname(f"{self.student_code}/.SPST/.#####")
    
    def validate(self):
        self.check_duplicate()
        self.calculate_totals()
        self.update_stipend_structure()
    
    def on_submit(self):
        # Validate that there's only one active stipend structure per student
        self.validate_active_structure()
    
    def on_cancel(self):
        pass
    
    def check_duplicate(self):
        """Check if active stipend structure already exists for this student"""
        if self.docstatus == 0:  # Only for draft documents
            student_exist = frappe.db.exists(
                "Stipend Structure", 
                {
                    "student_code": self.student_code, 
                    "docstatus": 1,
                    "is_active": "Yes"
                }
            )
            
            if student_exist:
                frappe.throw(_("Active Stipend Structure already exists for student {0}").format(self.student_code))
    
    def validate_active_structure(self):
        """Ensure only one active stipend structure per student"""
        existing_active = frappe.get_all(
            "Stipend Structure",
            filters={
                "student_code": self.student_code,
                "is_active": "Yes",
                "docstatus": 1,
                "name": ["!=", self.name]
            },
            limit=1
        )
        
        if existing_active:
            frappe.throw(_("Another active Stipend Structure already exists for student {0}").format(self.student_code))
    
    def calculate_totals(self):
        """Calculate total earnings, deductions and net amount"""
        total_earnings = sum(flt(earning.amount) for earning in self.earnings)
        total_deductions = sum(flt(deduction.amount) for deduction in self.deductions)
        net_amount = total_earnings - total_deductions
        
        self.total_earnings = total_earnings
        self.total_deductions = total_deductions
        self.net_amount = net_amount

    @frappe.whitelist()
    def update_stipend_structure(self, update_type="deductions", save=0):
        """Update either earnings or deductions while preserving the other"""
        if not self.company:
            frappe.throw(_("Company is mandatory to update stipend structure"))
        
        # Fetch stipend components for the company
        stipend_components = frappe.db.sql("""
            select sc.name, sc.component_type, sc.component, scd.amount as amt  
            from `tabStipend Component` sc 
            join `tabStipend Component Details` scd on scd.parent = sc.name
            where scd.company = %s 
        """, self.company, as_dict=True)
        #frappe.throw(str(self.company))
        if not stipend_components:
            frappe.throw(_("No stipend components configured for company: {0}").format(self.company))
        
        earnings_map = {}
        deductions_map = {}
        
        for sc in stipend_components:
            if sc.component_type == 'Earning':
                earnings_map[sc.component] = sc.amt
            elif sc.component_type == 'Deduction':
                deductions_map[sc.component] = sc.amt
        
        if update_type == "deductions":
            # Only update deductions - preserve earnings
            self.set('deductions', [])
            
            if self.eligible_for_rent and 'Rent' in deductions_map:
                self.append('deductions', {
                    'stipend_component': 'Rent',
                    'amount': deductions_map['Rent']
                })
            
            if self.eligible_for_mess_fees and 'Mess Fees' in deductions_map:
                self.append('deductions', {
                    'stipend_component': 'Mess Fees',
                    'amount': deductions_map['Mess Fees']
                })
        
        elif update_type == "earnings":
            # Only update earnings - preserve deductions
            self.set('earnings', [])
            
            if 'Stipend' in earnings_map:
                self.append('earnings', {
                    'stipend_component': 'Stipend',
                    'amount': earnings_map['Stipend']
                })
        
        # Recalculate totals after updates
        self.calculate_totals()
        if save == 1:
            self.save()

        
        frappe.msgprint(_("Stipend structure updated successfully for {0}").format(update_type))


@frappe.whitelist()
def make_stipend_slip(
    source_name,
    target_doc=None,
    student_code=None,
    posting_date=None,
    as_print=False,
    print_format=None,
    for_preview=0,
    ignore_permissions=False,
):
    """
    Create a Stipend Slip from Stipend Structure
    
    Args:
        source_name (str): Source Stipend Structure name
        target_doc (dict, optional): Existing target document
        student_code (str, optional): Student code for the slip
        posting_date (str, optional): Posting date for the slip
        as_print (bool, optional): Return as print format
        print_format (str, optional): Print format to use
        for_preview (int, optional): If creating for preview
        ignore_permissions (bool, optional): Ignore permissions check
    """
    
    def postprocess(source, target):
        """
        Post-process the mapped document
        """
        # Set student code if provided
        if student_code:
            target.student_code = student_code
        
        # Set posting date if provided
        if posting_date:
            target.posting_date = posting_date
        
        # Map additional fields from source to target
        target.stipend_structure = source.name
        target.gross_pay = source.total_earnings
        target.net_pay = source.net_amount
        
        # Copy earnings and deductions
        target.set('earnings', [])
        target.set('deductions', [])
        
        # Copy earnings from structure to slip
        for earning in source.earnings:
            target.append('earnings', {
                'stipend_component': earning.stipend_component,
                'amount': earning.amount,
                'component_type': getattr(earning, 'component_type', None),
                'description': getattr(earning, 'description', '')
            })
        
        # Copy deductions from structure to slip
        for deduction in source.deductions:
            target.append('deductions', {
                'stipend_component': deduction.stipend_component,
                'amount': deduction.amount,
                'component_type': getattr(deduction, 'component_type', None),
                'description': getattr(deduction, 'description', '')
            })
        
        # Process stipend structure calculations
        if hasattr(target, 'process_stipend_structure'):
            target.process_stipend_structure(for_preview=for_preview)
    
    try:
        # Get the mapped document
        doc = get_mapped_doc(
            "Stipend Structure",
            source_name,
            {
                "Stipend Structure": {
                    "doctype": "Stipend Slip",
                    "field_map": {
                        "total_earnings": "gross_pay",
                        "net_amount": "net_pay",
                        "company": "company"
                    },
                }
            },
            target_doc,
            postprocess,
            ignore_child_tables=True,  # We handle child tables manually in postprocess
            ignore_permissions=ignore_permissions,
        )
        
        # If as_print is requested, return print format
        if cint(as_print):
            doc.name = f"Preview for {student_code}" if student_code else "Preview"
            return frappe.get_print(
                doc.doctype, 
                doc.name, 
                doc=doc, 
                print_format=print_format
            )
        else:
            return doc
            
    except Exception as e:
        frappe.log_error(f"Error creating stipend slip: {str(e)}")
        frappe.throw(_("Failed to create stipend slip: {0}").format(str(e)))


@frappe.whitelist()
def get_student_stipend_structure(student_code):
    """
    Get active stipend structure for a student
    
    Args:
        student_code (str): Student code
        
    Returns:
        dict: Stipend structure details
    """
    if not student_code:
        return None
    
    structure = frappe.get_all(
        "Stipend Structure",
        filters={
            "student_code": student_code,
            
            "docstatus": 1
        },
        fields=["name", "total_earnings", "total_deductions", "net_amount"],
        limit=1
    )
    
    return structure[0] if structure else None


@frappe.whitelist()
def create_stipend_slip_from_structure(stipend_structure, student_code, posting_date=None):
    """
    Create and submit a stipend slip from stipend structure
    
    Args:
        stipend_structure (str): Stipend Structure name
        student_code (str): Student code
        posting_date (str, optional): Posting date
        
    Returns:
        str: Created Stipend Slip name
    """
    try:
        # Create stipend slip using the mapper
        stipend_slip = make_stipend_slip(
            source_name=stipend_structure,
            student_code=student_code,
            posting_date=posting_date or today(),
            ignore_permissions=True
        )
        
        # Save the stipend slip
        stipend_slip.insert()
        
        # Submit if required
        # stipend_slip.submit()
        
        frappe.db.commit()
        
        frappe.msgprint(_("Stipend Slip {0} created successfully").format(
            frappe.bold(stipend_slip.name)
        ))
        
        return stipend_slip.name
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error creating stipend slip from structure: {str(e)}")
        frappe.throw(_("Failed to create stipend slip: {0}").format(str(e)))