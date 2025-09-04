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
	}
});
