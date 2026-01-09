// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Statement", {
	refresh(frm) {
        frm.set_query("student_code",function(){
            return {

                "filters": {
					"company": frm.doc.company
				
				}

            };
        
        
        });
        frm.call("has_disciplinary_action").then((r) => {
			if (!r.message.has_travel_claim) {
				

				if (
					frm.doc.docstatus === 1 && frm.doc.disciplinary_issue_type=='Major Issue' &&
					frappe.model.can_create("Disciplinary Action")
				) {
				
					frm.add_custom_button(
						__("Disciplinary Action"),
						function () {
							frm.events.make_disciplinary_action(frm);
						},
						__("Create"),
					);
				}
            }});

        

	},


    make_disciplinary_action: function (frm) {
		//let method = "get_disciplinary_action";
		return frappe.call({
			method: "erpnext.student_services.doctype.student_statement.student_statement.get_disciplinary_action",
			args: {
				dt: frm.doc.doctype,
				dn: frm.doc.name,
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			},
		});
	}
});
