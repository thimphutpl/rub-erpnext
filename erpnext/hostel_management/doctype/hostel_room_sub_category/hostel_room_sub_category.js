// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Room Sub Category", {
	refresh(frm) {

	},

    setup: function(frm){
        frm.set_query('hostel_room', function(doc) {
            return {
                filters: {
                    "company": doc.company
                }
            }
        }); 
    }
});
