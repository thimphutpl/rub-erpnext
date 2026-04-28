// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Counselling Request Form", {
	refresh(frm) {

        frm.set_query("student_id", function() {
			return {
				"filters": {
					"Company": frm.doc.college
				
				}
			};
		});


	},
});
