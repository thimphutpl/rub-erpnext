// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplementary Budgets", {
	refresh(frm) {
        if (!frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today())
        }
	},
});
