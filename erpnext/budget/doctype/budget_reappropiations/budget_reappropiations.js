// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Budget Reappropiations", {
	refresh(frm) {
        if (!frm.doc.appropriation_date) {
            frm.set_value("appropriation_date", frappe.datetime.get_today())
        }

	},
});
