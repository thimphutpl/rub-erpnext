// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Application", {
	refresh(frm) {
		frm.set_query("student_code", function(){
			return {
				filters: {
					"company": frm.doc.company,
				}
			}
		});
		frm.set_query("hostel_room", function(){
			return {
				filters: {
					"company": frm.doc.company,
				}
			}
		});
	},
    onload(frm){
        if (!frm.doc.posting_date) {
			frm.set_value('posting_date', frappe.datetime.now_date());
			// frm.set_value("posting_date", get_today());
		}
    }
});
