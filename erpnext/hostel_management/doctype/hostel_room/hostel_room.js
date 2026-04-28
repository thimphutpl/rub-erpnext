// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Room", {
	refresh: function(frm) { 
	},
	setup: function(frm){
		frm.set_query("company", function(){
			return {
				filters: {
					"is_group": 0,
				}
			}
		})
		frm.set_query('cost_center', function(doc) {
			return {
				filters: {
					"company": doc.company
				}
			}
		}); 
		// frm.set_query('hostel_type', function(doc) {
		// 	return {
		// 		filters: {
		// 			"company": doc.company
		// 		}
		// 	}
		// }); 
		frm.set_query("hostel_type", function(){
            if (!frm.doc.company) {
                return {
                    filters: [
                        ["name", "=", ""]  // Return empty result
                    ]
                };
            }
			return {
				filters: {
					company: frm.doc.company
				}
			}
		});
		frm.set_query('student_list', function(doc) {
			return {
				filters: {
					"company": doc.company
				}
			}
		}); 
		frm.fields_dict["student_list"].grid.get_field("student_code").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
		frm.fields_dict["hostel_room_item"].grid.get_field("asset_code").get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        };
	}
});
