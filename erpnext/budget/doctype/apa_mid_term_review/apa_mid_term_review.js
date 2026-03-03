// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("APA Mid Term Review", {
	refresh(frm) {

	},
    fiscal_year: function(frm) {
        if(frm.doc.fiscal_year && frm.doc.college){
            frm.trigger("get_target_setup_details");
        }
    },
    college: function(frm) {
        if(frm.doc.fiscal_year && frm.doc.college){
            frm.trigger("get_target_setup_details");
        }
    },
    get_target_setup_details: function(frm){
        frappe.call({
            method:"erpnext.budget.doctype.apa_mid_term_review.apa_mid_term_review.get_target_setup_details",
            args: {
                    fiscal_year: frm.doc.fiscal_year,
                    college: frm.doc.college,
                },
                callback: function(r) {
                    if (r.message.output) {
                        console.log(r.message.output)
                        frm.clear_table("output_items");

                        r.message.output.forEach(function(row) {
                            let child = frm.add_child("output_items");
                            child.output = row.output
                            child.activities= row.activities
                            child.project = row.project

                            child.output_no = row.output_no
                            child.project_no = row.project_no
                            child.activity_link = row.activity_link
                            child.activities_no = row.activities_no
                            child.unit = row.unit
                            child.weightage = row.weightage
                            child.target = row.target
                            child.justification = row.justification
                        });
    
                        frm.refresh_field("output_items");
                    }
                    if (r.message.outcome) {
                        console.log(r.message.outcome)
                        frm.clear_table("outcome_items");
                        
                        r.message.outcome.forEach(function(row) {
                            let child = frm.add_child("outcome_items");
                            child.outcome = row.outcome
                            child.unit= row.unit
                            child.weightage = row.weightage
                            child.target = row.target
                            child.justification = row.justification
                        });
    
                        frm.refresh_field("outcome_items");
                    }
                }
        })
    }
});
