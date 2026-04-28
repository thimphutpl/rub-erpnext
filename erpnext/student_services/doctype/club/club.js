// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club", {
	refresh(frm) {
       
         frm.set_query("employee_student","club_management",function(){
                    return {filters:{
                        "company":frm.doc.company

                    }  
                } ;        

        })

	},
   
});

frappe.ui.form.on("Club Management Details", {  // Use your child doctype name

     refresh: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.role === "Club Advisor") {
            frappe.model.set_value(cdt, cdn, "type", "Employee");
        }
        else if (row.role === "Club Coordinator") {
            frappe.model.set_value(cdt, cdn, "type", "Student");
        }
        else if (row.role) {
            // Optional: Clear type for other roles
            frappe.model.set_value(cdt, cdn, "type", "");
        }
    },
    employee_student: function(frm, cdt, cdn) {
         let row = frappe.get_doc(cdt, cdn);
         //alert(row.employee_student)
        frm.call({
                    method: "erpnext.student_services.doctype.club.club.get_full_name",  
                    //doc: frm.doc,           
                    args: {                 
                        std_emp_id: row.employee_student,
                        type : row.type,
                        doc : frm.doc.name

                        
                    },
                    callback: function(response) {
                        if (response.message) {

                             if (response.message.exists) {
                                frappe.msgprint({
                                    title: __('Membership Exists'),
                                    indicator: 'red',
                                    message: __('This member already has an active membership in this club')
                                });
                            } else {

                                if (row.type == 'Employee') {
                                    // For Employee, response.message is string (full_name)
                                    
                                    frappe.model.set_value(cdt, cdn, "full_name", response.message.full_name);
                                    frappe.model.set_value(cdt, cdn, "designation", response.message.designation);
                                } 
                                else if (row.type == 'Student') {
                                    // For Student, response.message is object
                                    let data = response.message;
                                    frappe.model.set_value(cdt, cdn, "full_name", data.full_name);
                                    frappe.model.set_value(cdt, cdn, "program", data.programme);
                                    frappe.model.set_value(cdt, cdn, "year", data.year);
                                    frappe.model.set_value(cdt, cdn, "semester", data.semester);
                                }
                                
                                frm.refresh_field("club_management");
                            }
                    }
                    },
                    freeze: true,           
                    freeze_message: "Processing..." 
                });
    },

    role: function(frm,cdt,cdn){
         let row = frappe.get_doc(cdt, cdn);
         //alert("hii2")
         if (row.role==="Club Advisor"){
            
             frappe.model.set_value(cdt, cdn, "type", "Employee");

         }
         else if(row.role==="Club Coordinator"){
            frappe.model.set_value(cdt, cdn, "type", "Student");

         }
         else{

             frappe.model.set_value(cdt, cdn, "type", "");

         }
    }
});
