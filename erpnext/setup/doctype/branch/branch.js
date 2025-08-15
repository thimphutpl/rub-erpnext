// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch", {
	onload: function (frm) {
		frm.set_query("expense_bank_account", function() {
            return {
                filters: {
                    "company": frm.doc.company,
                    "is_group": 0,
                    "account_type": "Bank"
                }
            };
        });
        frm.set_query("branch", function() {
            return {
                filters:{
                    "company": frm.doc.cost_center,
                    "is_group":0,
                    account_type: "branch"
                }
            }
        })
	},

	refresh: function (frm) {
		
	},
});