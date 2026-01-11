// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club", {
	refresh(frm) {
        frm.set_query("student_code","club_management",function(){
                    return {filters:{
                        "company":frm.doc.company

                    }  
                } ;        

        })
         frm.set_query("employee_id","club_management",function(){
                    return {filters:{
                        "company":frm.doc.company

                    }  
                } ;        

        })

	},
});
