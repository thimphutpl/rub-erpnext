// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Welfare Scheme Claim", {
	refresh(frm) {
        if (frm.doc.workflow_state === 'Waiting for Disbursement'||frm.doc.workflow_state === 'Approved') {
            frm.set_df_property('reference_number', 'hidden', 0); // Show the field
        } else {
            frm.set_df_property('reference_number', 'hidden', 1); // Hide the field
        }

	},
});
