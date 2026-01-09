// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hostel Budget", {
	// Trigger whenever form is refreshed or total changes
    refresh(frm) {
        calculate_balance(frm);
    },
    total_budget_collection(frm) {
        calculate_balance(frm);
    },
    onload(frm) {
        // Only set posting_date when creating a new document
        if (frm.is_new() && !frm.doc.posting_date) {
            frm.set_value("posting_date", frappe.datetime.get_today());
        }
    }
});

frappe.ui.form.on("Hostel Budget Item", {
    // Trigger when amount changes in child table
    amount(frm, cdt, cdn) {
        calculate_balance(frm);
    },
    // Trigger when rows are added or removed
    items_remove(frm) {
        calculate_balance(frm);
    },
});

function calculate_balance(frm) {
    let total_amount = 0;
    (frm.doc.expenses_amount || []).forEach(row => {
        total_amount += flt(row.amount);
    });

    let balance = flt(frm.doc.total_budget_collection) - total_amount;
    frm.set_value("balance_amount", balance);
}
