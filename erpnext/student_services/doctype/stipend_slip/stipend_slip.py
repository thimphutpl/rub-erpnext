# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.query_builder import Order
# from frappe.model.naming import make_autoname
# from frappe import _, msgprint
# from frappe.model.mapper import get_mapped_doc
# from frappe.model.document import Document
# from frappe.utils import cint, cstr, flt, getdate, get_first_day, today, get_last_day


# class StipendSlip(Document):
# 	# begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.student_services.doctype.stipend_details.stipend_details import StipendDetails
# 		from frappe.types import DF

# 		amended_from: DF.Link | None
# 		college_bank_account: DF.Link | None
# 		company: DF.Link
# 		deductions: DF.Table[StipendDetails]
# 		earnings: DF.Table[StipendDetails]
# 		end_date: DF.Date | None
# 		fiscal_year: DF.Link
# 		gross_pay: DF.Data | None
# 		journal_entry: DF.Link | None
# 		month: DF.Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# 		net_pay: DF.Data | None
# 		start_date: DF.Date | None
# 		stipend_entry: DF.Link | None
# 		stipend_structure: DF.Link | None
# 		student_bank_account: DF.Data | None
# 		student_code: DF.Link
# 	# end: auto-generated types
	
# 	def autoname(self):
# 		self.series = f"Stp Slip/{self.student_code}/.#####"
# 		self.name = make_autoname(self.series)
	
# 	def validate(self):
# 		struct = self.check_stp_struct()
# 		#frappe.throw(str(self.end_date))
# 		if struct:
# 			self.set_stipend_structure_doc()
# 			#self.pull_stp_struct()
# 			self.process_stipend_structure()

# 	def set_stipend_structure_doc(self) -> None:
# 		if self.stipend_structure:
# 			self._stipend_structure_doc = frappe.get_cached_doc("Stipend Structure", self.stipend_structure)

# 	# def copy_structure_to_slip(self):
# 	# 	frappe.throw("zzzz")
# 	# 	if not hasattr(self, '_stipend_structure_doc') or not self._stipend_structure_doc:
# 	# 		return
			
# 	# 	# Copy earnings
# 	# 	self.set('earnings', [])
# 	# 	for earning in self._stipend_structure_doc.earnings:
# 	# 		self.append('earnings', {
# 	# 			'stipend_component': earning.stipend_component,
# 	# 			'amount': flt(earning.amount),
# 	# 			'component_type': getattr(earning, 'component_type', None),
# 	# 			'description': getattr(earning, 'description', '')
# 	# 		})
		
# 	# 	# Copy deductions
# 	# 	self.set('deductions', [])
# 	# 	for deduction in self._stipend_structure_doc.deductions:
# 	# 		self.append('deductions', {
# 	# 			'stipend_component': deduction.stipend_component,
# 	# 			'amount': flt(deduction.amount),
# 	# 			'component_type': getattr(deduction, 'component_type', None),
# 	# 			'description': getattr(deduction, 'description', '')
# 	# 		})
		
# 	# 	# Copy totals
# 	# 	self.gross_pay = flt(self._stipend_structure_doc.total_earnings)
# 	# 	self.net_pay = flt(self._stipend_structure_doc.net_amount)
	

# 	def process_stipend_structure(self, for_preview=0):
# 		"""Calculate stipend after structure details have been updated"""
# 		self.calculate_earning()
# 		self.calculate_deduction()
# 		self.calculate_net_pay()

# 	def calculate_earning(self):
# 		if self.stipend_structure:
# 			self.calculate_component_amounts("earnings")
# 			self.calculate_gross_pay()

# 	def calculate_deduction(self):
# 		if self.stipend_structure:
# 			self.calculate_component_amounts("deductions")

# 	def calculate_component_amounts(self, component_type):
# 		if not getattr(self, "_stipend_structure_doc", None):
# 			self.set_stipend_structure_doc()

# 		if self._stipend_structure_doc:
# 			self.add_structure_components(component_type)

# 	def add_structure_components(self, component_type):
# 		"""Add components from stipend structure to the slip"""
# 		# Clear existing components of this type
# 		self.set(component_type, [])
		
# 		if not self._stipend_structure_doc:
# 			return
			
# 		for struct_row in self._stipend_structure_doc.get(component_type, []):
# 			self.add_structure_component(struct_row, component_type)

# 	def add_structure_component(self, struct_row, component_type):
# 		"""Add a single component from structure to slip"""
# 		component_row = self.append(component_type, {})
# 		component_row.stipend_component = struct_row.stipend_component
# 		component_row.amount = struct_row.amount
# 		component_row.component_type = getattr(struct_row, 'component_type', None)
		
# 		if hasattr(struct_row, 'description'):
# 			component_row.description = struct_row.description

# 	def calculate_gross_pay(self):
# 		"""Calculate total gross pay from earnings"""
# 		gross_pay = 0
# 		for earning in self.earnings:
# 			gross_pay += flt(earning.amount)
# 		self.gross_pay = gross_pay

# 	def calculate_net_pay(self):
# 		"""Calculate net pay after deductions"""
# 		total_deductions = 0
# 		for deduction in self.deductions:
# 			total_deductions += flt(deduction.amount)
		
# 		self.net_pay = flt(self.gross_pay) - flt(total_deductions)

# 	def check_stp_struct(self):
# 		"""Find active stipend structure for the student"""
# 		ss = frappe.qb.DocType("Stipend Structure")

# 		query = (
# 			frappe.qb.from_(ss)
# 			.select(ss.name)
# 			.where(
# 				#(ss.docstatus == 1) &  # Only submitted structures
# 				(ss.student_code == self.student_code) 
				
# 			)
# 			.orderby(ss.creation, order=Order.desc)
# 			.limit(1)
# 		)

# 		st_name = query.run()
		
# 		if st_name:
# 			self.stipend_structure = st_name[0][0]
# 			return self.stipend_structure
# 		else:
# 			self.stipend_structure = None
# 			frappe.msgprint(
# 				_("No active Stipend Structure found for student {0}").format(
# 					self.student_code
# 				),
# 				title=_("Stipend Structure Missing"),
# 			)
# 			return None
# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Order
from frappe.model.naming import make_autoname
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, getdate, get_first_day, today, get_last_day, date_diff


class StipendSlip(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.student_services.doctype.stipend_details.stipend_details import StipendDetails
        from frappe.types import DF

        amended_from: DF.Link | None
        college_bank_account: DF.Link | None
        company: DF.Link
        deductions: DF.Table[StipendDetails]
        earnings: DF.Table[StipendDetails]
        end_date: DF.Date | None
        fiscal_year: DF.Link
        gross_pay: DF.Data | None
        journal_entry: DF.Link | None
        month: DF.Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        net_pay: DF.Data | None
        start_date: DF.Date | None
        stipend_entry: DF.Link | None
        stipend_structure: DF.Link | None
        student_bank_account: DF.Data | None
        student_code: DF.Link
    # end: auto-generated types
    
    def autoname(self):
        self.series = f"Stp Slip/{self.student_code}/.#####"
        self.name = make_autoname(self.series)
    
    def validate(self):
        struct = self.check_stp_struct()
        if struct:
            self.set_stipend_structure_doc()
            self.process_stipend_structure()

    def set_stipend_structure_doc(self) -> None:
        if self.stipend_structure:
            self._stipend_structure_doc = frappe.get_cached_doc("Stipend Structure", self.stipend_structure)
    
    def process_stipend_structure(self, for_preview=0):
        """Calculate stipend after structure details have been updated"""
        self.calculate_earning()
        self.calculate_deduction()
        self.calculate_net_pay()

    def calculate_earning(self):
        if self.stipend_structure:
            self.calculate_component_amounts("earnings")
            self.calculate_gross_pay()

    def calculate_deduction(self):
        if self.stipend_structure:
            self.calculate_component_amounts("deductions")

    def calculate_component_amounts(self, component_type):
        if not getattr(self, "_stipend_structure_doc", None):
            self.set_stipend_structure_doc()

        if self._stipend_structure_doc:
            self.add_structure_components(component_type)

    def add_structure_components(self, component_type):
        """Add components from stipend structure to the slip"""
        # Clear existing components of this type
        self.set(component_type, [])
        
        if not self._stipend_structure_doc:
            return
            
        for struct_row in self._stipend_structure_doc.get(component_type, []):
            self.add_structure_component(struct_row, component_type)

    def add_structure_component(self, struct_row, component_type):
        """Add a single component from structure to slip WITH PROPORTIONAL CALCULATION"""
        component_row = self.append(component_type, {})
        component_row.stipend_component = struct_row.stipend_component
        
        # CALCULATE PROPORTIONAL AMOUNT BASED ON DAYS
        amount = self.calculate_proportional_amount(struct_row.amount)
        component_row.amount = amount
        
        component_row.component_type = getattr(struct_row, 'component_type', None)
        
        if hasattr(struct_row, 'description'):
            component_row.description = struct_row.description

    def calculate_proportional_amount(self, monthly_amount):
        """Calculate amount proportional to number of days"""
        # Get total days from start_date and end_date
        total_days = self.get_total_days()
        
        # If no dates or 30 days, use full amount
        if total_days >= 28:  # 28+ days considered full month
            return flt(monthly_amount)
        
        # Calculate proportional amount
        # Monthly amount / 30 days * actual days
        daily_rate = flt(monthly_amount) / 30
        proportional_amount = flt(daily_rate * total_days)
        
        return proportional_amount

    def get_total_days(self):
        """Calculate days between start_date and end_date"""
        if self.start_date and self.end_date:
            # Add 1 to include both start and end date
            return date_diff(self.end_date, self.start_date) + 1
        return 30  # Default to 30 if no dates

    def calculate_gross_pay(self):
        """Calculate total gross pay from earnings"""
        gross_pay = 0
        for earning in self.earnings:
            gross_pay += flt(earning.amount)
        self.gross_pay = flt(gross_pay,2)

    def calculate_net_pay(self):
        """Calculate net pay after deductions"""
        total_deductions = 0
        for deduction in self.deductions:
            total_deductions += flt(deduction.amount)
        
        self.net_pay = flt(self.gross_pay) - flt(total_deductions,2)

    def check_stp_struct(self):
        """Find active stipend structure for the student"""
        ss = frappe.qb.DocType("Stipend Structure")

        query = (
            frappe.qb.from_(ss)
            .select(ss.name)
            .where(
                (ss.student_code == self.student_code) 
            )
            .orderby(ss.creation, order=Order.desc)
            .limit(1)
        )

        st_name = query.run()
        
        if st_name:
            self.stipend_structure = st_name[0][0]
            return self.stipend_structure
        else:
            self.stipend_structure = None
            frappe.msgprint(
                _("No active Stipend Structure found for student {0}").format(
                    self.student_code
                ),
                title=_("Stipend Structure Missing"),
            )
            return None