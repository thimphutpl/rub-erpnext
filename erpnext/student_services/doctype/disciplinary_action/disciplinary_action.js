// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Disciplinary Action", {
	refresh(frm) {
        frm.call("has_appeal_action").then((r) => {
			if (!r.message.has_appeal_action) {
				

				if (
					frm.doc.docstatus === 1 &&
					frappe.model.can_create("Appeal")
				) {
				
					frm.add_custom_button(
						__("Appeal"),
						function () {
							frm.events.make_appeal(frm);
						},
						__("Create"),
					);
				}
            }
        
        }
        
        );
	},
	 make_appeal: function (frm) {
		//let method = "get_disciplinary_action";
		return frappe.call({
			method: "erpnext.student_services.doctype.disciplinary_action.disciplinary_action.get_appeal",
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
