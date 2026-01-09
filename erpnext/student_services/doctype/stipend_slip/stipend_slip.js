// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stipend Slip", {
	refresh(frm) {
        frm.set_query("student_code",function(){
			return{
				"filters":{
				"company":frm.doc.company
				}
			};
		})

	},
});
