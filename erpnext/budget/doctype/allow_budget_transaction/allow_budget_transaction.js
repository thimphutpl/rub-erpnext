// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Allow Budget Transaction", {
	refresh(frm) {
        frm.set_query("college", function () {
            return {
                filters: {
                    is_group: 0,
                },
            };
        });
	},
    setup(frm) {
        frm.set_query("college", function () {
            return {
                filters: {
                    is_group: 0,
                },
            };
        });
    },
    transaction_type(frm) {
        if(frm.doc.transaction_type){
            frm.set_query("transaction_no", function () {
                return {
                    filters: {
                        docstatus: 0,
                    },
                };
            });
        }
    }
});
