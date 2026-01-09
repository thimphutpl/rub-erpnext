// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Allocation Bulk Upload", {
    onload: function(frm) {
        frm.set_query("company", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		});   
        frm.fields_dict["table_caon"].grid.get_field("hostel_room").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };


        frm.fields_dict["table_caon"].grid.get_field("student_code").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company,
                    year: frm.doc.year

                }
            };
        };
    },    
});







