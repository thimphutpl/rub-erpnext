// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Output Indicator", {
	refresh(frm) {

	},
    get_planning_info: function(frm){
        if (frm.doc.fiscal_year){
            frappe.call({
                method:"erpnext.budget.doctype.output_indicator.output_indicator.fetch_budgetplan",
                args: {
                        fiscal_year: frm.doc.fiscal_year
                    },
                callback: function(r) {
                    if (r.message) {
                        // Clear existing rows first (optional)
                        console.log(r.message)
                        frm.clear_table("items");
    
                        // r.message should be an array of objects
                        r.message.forEach(function(row) {
                            let child = frm.add_child("items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project
    
                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.activity_link = row.activity_link
                            // child.competency = row.competency_item;
                            // child.description = row.description;
                        });
    
                        // Refresh the table to show the new data
                        frm.refresh_field("items");
                    }
                }
            })
        }
    }
});
