// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Credit Record", {
	refresh(frm) {
        frm.set_query("credit_type",function(){
             return {

                "filters": {
					"company": frm.doc.company
				
				}

            };

        });

        frm.call("has_credit_clearance").then((r) => {
			if (!r.message.has_student_rec) {
				

				if (
					frm.doc.docstatus === 1 &&
					frappe.model.can_create("Credit Clearance Record")
				) {
				
					frm.add_custom_button(
						__("Credit Clearance Record"),
						function () {
							frm.events.make_credit_clearance(frm);
						},
						__("Create"),
					);
				}

				
			}
		});

        frm.set_query("student_code","student_details",function(){
            return {

                "filters": {
					"company": frm.doc.company
				
				}

            };

        })

	},

    make_credit_clearance: function (frm) {
		let method = "erpnext.student_services.doctype.credit_clearance_record.credit_clearance_record.get_credit_clearance";
		return frappe.call({
			method: method,
			args: {
				dt: frm.doc.doctype,
				dn: frm.doc.name,
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			},
		});
	},
});
