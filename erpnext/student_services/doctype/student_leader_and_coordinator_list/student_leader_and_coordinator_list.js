// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.ui.form.on("Student Leader and Coordinator List", {
    refresh(frm) {

        frm.set_query("student_code","student_leader_and_coordinator_details",function(){
            return {

                "filters": {
					"company": frm.doc.company
				
				}

            };
        });
        frm.fields_dict["student_leader_and_coordinator_details"].grid.get_field("student_code").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    "company": frm.doc.company
                }
            };
        };
        frm.fields_dict["student_leader_and_coordinator_details"].grid.get_field("hostel_counsellor").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    "company": frm.doc.company
                }
            };
        };
    },
});
